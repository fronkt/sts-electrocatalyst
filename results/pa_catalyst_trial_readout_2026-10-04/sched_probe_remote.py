"""Read-only Slurm/accounting probe for job 21034683, piped to the remote Python on stdin.

Runs only query commands (sacct, scontrol show, squeue, jobsu, mybalance, which); creates nothing on Anvil.
"""
import json
import subprocess

JOB = "21034683"
COMMANDS = [
    ("sacct_header", ["sacct", "-P", "-j", JOB, "--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,ReqMem,AllocTRES,CPUTimeRAW,MaxRSS,Start,End"]),
    ("sacct_nheader_watcher_format", ["sacct", "-n", "-P", "-j", JOB, "--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,ReqMem,AllocTRES,CPUTimeRAW"]),
    ("scontrol_show_job", ["scontrol", "show", "job", JOB, "-o"]),
    ("squeue", ["squeue", "-h", "-j", JOB, "-o", "%i|%T|%M|%C|%R"]),
    ("which_jobsu", ["bash", "-lc", "command -v jobsu; command -v mybalance"]),
    ("jobsu_help", ["bash", "-lc", "jobsu -h 2>&1 | head -30"]),
    ("jobsu_j", ["bash", "-lc", "jobsu -j " + JOB + " 2>&1"]),
    ("mybalance", ["bash", "-lc", "mybalance 2>&1"]),
]
out = {"job_id": JOB, "readonly": True, "commands": {}}
for name, args in COMMANDS:
    try:
        p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=40)
        out["commands"][name] = {"args": args, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        out["commands"][name] = {"args": args, "error": repr(exc)}
print(json.dumps(out))
