#!/usr/bin/env bash
# Local wait-pull-terminate loop for the film-DFT pilot (start with run_in_background right
# after aws_launch.sh). Every 10 min: copy queue.log for monitoring; when RUN_DONE or
# RUN_STALLED appears, pull out.tgz, verify md5, touch PULLED, terminate the instance,
# delete the security group and key pair. Exits 2 if the instance stopped before a pull.
set -u
export MSYS_NO_PATHCONV=1
P=83sciences-research
R=us-east-1
BASE=/d/sts-electrocatalyst/film_pilot
# shellcheck disable=SC1090
source "$BASE/aws_state.txt"
SSHO=(-o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$BASE/known_hosts" -o ConnectTimeout=20)
aws() { command aws --profile "$P" --region "$R" "$@"; }
OUT=$BASE/out
mkdir -p "$OUT"

while true; do
  st=$(aws ec2 describe-instances --instance-ids "$IID" --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null || echo unknown)
  if [ "$st" = stopped ] || [ "$st" = terminated ]; then
    echo "instance $IID is $st before a pull $(date -u +%FT%TZ)"; exit 2
  fi
  ssh "${SSHO[@]}" ubuntu@"$IP" 'cat ~/film/queue.log 2>/dev/null' > "$BASE/queue.log.tmp" 2>/dev/null && mv "$BASE/queue.log.tmp" "$BASE/queue.log"
  flag=$(ssh "${SSHO[@]}" ubuntu@"$IP" 'cd ~/film; ls RUN_DONE RUN_STALLED 2>/dev/null' 2>/dev/null || true)
  if [ -n "$flag" ]; then
    echo "flag: $flag $(date -u +%FT%TZ)"
    for attempt in 1 2 3; do
      scp "${SSHO[@]}" ubuntu@"$IP":film/out.tgz ubuntu@"$IP":film/out.tgz.md5 "$OUT/" && \
        (cd "$OUT" && md5sum -c out.tgz.md5) && break
      sleep 30
    done
    if (cd "$OUT" && md5sum -c out.tgz.md5 >/dev/null 2>&1); then
      (cd "$OUT" && tar xzf out.tgz)
      ssh "${SSHO[@]}" ubuntu@"$IP" 'touch ~/film/PULLED'
      sleep 5
      # The box stops itself once PULLED exists. Terminating needs a live SSO token, which may
      # have expired on a multi-day run; if so, the stopped instance only bills its disk until
      # Frank logs in again and it is terminated by hand.
      if aws ec2 terminate-instances --instance-ids "$IID" >/dev/null && \
         aws ec2 wait instance-terminated --instance-ids "$IID"; then
        aws ec2 delete-security-group --group-id "$SG" && aws ec2 delete-key-pair --key-name "$KEY"
        echo "PULLED_AND_TERMINATED $flag $(date -u +%FT%TZ)" | tee -a "$BASE/aws_state.txt"
        exit 0
      fi
      echo "PULLED_NOT_TERMINATED (SSO expired?) $flag $(date -u +%FT%TZ)" | tee -a "$BASE/aws_state.txt"
      exit 4
    fi
    echo "pull failed md5 check; instance left running for a manual pull"; exit 3
  fi
  sleep 600
done
