#!/usr/bin/env bash
# Launch the film-DFT pilot on the 83 Sciences AWS account (Git Bash on Frank's PC).
# Needs a live SSO session:  aws sso login --profile 83sciences-research
# Writes the instance/SG/key ids to $STATE; aws_pull_wait.sh reads it, pulls, terminates, cleans up.
set -euo pipefail
export MSYS_NO_PATHCONV=1
P=83sciences-research
R=us-east-1
VPC=vpc-077d401cf1d70dd26
TYPE=${TYPE:-c7a.48xlarge}
CAP_MIN=${CAP_MIN:-2880}            # hard cap: the box shuts itself down after 48 h
REPO=/c/Users/frank/sts-electrocatalyst
RUNDIR=$REPO/runs/film_pilot_2026-11-14
BASE=/d/sts-electrocatalyst/film_pilot
STATE=$BASE/aws_state.txt
STAMP=film-pilot-$(date +%Y%m%d-%H%M%S)
SSHO=(-o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$BASE/known_hosts" -o ConnectTimeout=20)
aws() { command aws --profile "$P" --region "$R" "$@"; }
mkdir -p "$BASE/stage/inputs" "$BASE/stage/pseudo"

# 1. stage the payload: inputs, pseudos, box scripts (LF line endings)
cp "$RUNDIR"/*.in "$RUNDIR/manifest.json" "$BASE/stage/inputs/"
cp "$BASE"/pseudo/*.UPF "$BASE"/pseudo/*.upf "$BASE/stage/pseudo/" 2>/dev/null || true
cp "$REPO"/src/dft/film_box/box_*.sh "$BASE/stage/"
sed -i 's/\r$//' "$BASE"/stage/*.sh "$BASE"/stage/inputs/*
grep -q "/home/ubuntu/film/pseudo" "$BASE"/stage/inputs/NiOOH__slab.in || { echo "inputs not built for /home/ubuntu/film/pseudo"; exit 1; }
tar czf "$BASE/payload.tgz" -C "$BASE/stage" .
echo "payload $(du -k "$BASE/payload.tgz" | cut -f1) KB"

# 2. AMI, key pair, security group
AMI=$(aws ssm get-parameter --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
      --query Parameter.Value --output text)
aws ec2 import-key-pair --key-name "$STAMP" --public-key-material fileb://C:/Users/frank/.ssh/id_ed25519.pub >/dev/null
SG=$(aws ec2 create-security-group --group-name "$STAMP" --description "film pilot ssh" --vpc-id "$VPC" \
     --query GroupId --output text)
MYIP=$(curl -s https://checkip.amazonaws.com | tr -d '\r\n')
aws ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port 22 --cidr "$MYIP/32" >/dev/null
printf '#!/bin/bash\nshutdown -h +%s\n' "$CAP_MIN" > "$BASE/userdata.sh"
UD=$(cygpath -m "$BASE/userdata.sh")
{ echo "STAMP=$STAMP"; echo "SG=$SG"; echo "KEY=$STAMP"; echo "AMI=$AMI"; echo "TYPE=$TYPE"; } > "$STATE"

# 3. run-instances, trying each default subnet until one has capacity
IID=""
for SUB in $(aws ec2 describe-subnets --filters Name=vpc-id,Values="$VPC" Name=default-for-az,Values=true \
             --query 'Subnets[].SubnetId' --output text); do
  if IID=$(aws ec2 run-instances --image-id "$AMI" --instance-type "$TYPE" --key-name "$STAMP" \
        --security-group-ids "$SG" --subnet-id "$SUB" \
        --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":150,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
        --instance-initiated-shutdown-behavior stop --user-data "file://$UD" \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$STAMP},{Key=Owner,Value=frank},{Key=Purpose,Value=sts-film-dft-pilot}]" \
        --query 'Instances[0].InstanceId' --output text 2>"$BASE/run_err.txt"); then
    break
  fi
  echo "subnet $SUB: $(tail -1 "$BASE/run_err.txt")"; IID=""
done
[ -n "$IID" ] || { echo "no subnet had capacity for $TYPE"; exit 1; }
echo "IID=$IID" >> "$STATE"
aws ec2 wait instance-running --instance-ids "$IID"
IP=$(aws ec2 describe-instances --instance-ids "$IID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "IP=$IP" >> "$STATE"
echo "launched $IID $TYPE at $IP; cap ${CAP_MIN} min"

# 4. wait for ssh (bounded), upload, start detached
for i in $(seq 1 30); do ssh "${SSHO[@]}" ubuntu@"$IP" true 2>/dev/null && break; sleep 10; done
ssh "${SSHO[@]}" ubuntu@"$IP" 'mkdir -p ~/film && cat > ~/film/payload.tgz' < "$BASE/payload.tgz"
ssh "${SSHO[@]}" ubuntu@"$IP" 'cd ~/film; tar xzf payload.tgz; md5sum payload.tgz' | tee "$BASE/payload_remote.md5"
md5sum "$BASE/payload.tgz"
ssh "${SSHO[@]}" ubuntu@"$IP" 'cd ~/film; setsid nohup bash box_start.sh > start.log 2>&1 < /dev/null & exit 0'
sleep 20
ssh "${SSHO[@]}" ubuntu@"$IP" 'cat ~/film/start.log; pgrep -af box_start | head -2'
echo "LAUNCHED $(date -u +%FT%TZ)" >> "$STATE"
