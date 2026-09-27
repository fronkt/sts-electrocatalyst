"""Runs retrieval and screening end to end as one detached, windowless process.

  pythonw run_pipeline.py [--no-retrieve]

Steps, in order, each a child process with no console window; stdout/stderr of every step go to
pipeline.log with UTC timestamps.  A failing step is logged and the chain continues (every step is
resumable and skips finished work, so a rerun of this script picks up where it stopped):
  1. retrieve_browser.py              (browser routes; Purdue gate and Sci-Hub rules unchanged)
  2. ft_screen.py extract, prepare --pass 1/2
  3. api_screen.py --pass 1, --pass 2
  4. ft_screen.py collect --pass 1/2, third_read.py collect, reconcile.py, third_read.py prepare
  5. api_screen.py --third, third_read.py collect, reconcile.py
The run's PID and status go to pipeline_status.json (pipeline_screen_status.json and
pipeline_screen.log for --no-retrieve) so any session can check on it.
"""
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
# A screening-only run (--no-retrieve) can go alongside a retrieval run, so it keeps its own files.
TAG = "_v3" if "--v3" in sys.argv else "_v4" if "--v4" in sys.argv else "_screen" if "--no-retrieve" in sys.argv else ""
LOG = HERE / ("pipeline%s.log" % TAG)
STATUS = HERE / ("pipeline%s_status.json" % TAG)
PY = str(pathlib.Path(sys.executable).with_name("python.exe"))
NO_WINDOW = 0x08000000

STEPS = [
    ["retrieve_browser.py"],
    ["ft_screen.py", "extract"], ["ft_screen.py", "prepare", "--pass", "1"], ["ft_screen.py", "prepare", "--pass", "2"],
    ["api_screen.py", "--pass", "1"], ["api_screen.py", "--pass", "2"],
    ["ft_screen.py", "collect", "--pass", "1"], ["ft_screen.py", "collect", "--pass", "2"],
    ["third_read.py", "collect"], ["reconcile.py"], ["third_read.py", "prepare"],
    ["api_screen.py", "--third"], ["third_read.py", "collect"], ["reconcile.py"],
]

# --v4: the re-read of records the 2026-09-27 rulings can change (v4_read.py), logged to pipeline_v4.log.
V4_STEPS = [["v4_read.py", "prepare"], ["api_screen.py", "--v4"], ["v4_read.py", "collect"]]
# --v3: the v3 sensitivity reads for records screened only under v4 (v3_read.py), logged to pipeline_v3.log.
V3_STEPS = [["v3_read.py", "prepare"], ["api_screen.py", "--v3"], ["v3_read.py", "collect"]]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def status(**kw):
    STATUS.write_text(json.dumps(dict(pid=os.getpid(), updated=now(), **kw), indent=1), encoding="utf-8")


def main():
    steps = V3_STEPS if "--v3" in sys.argv else V4_STEPS if "--v4" in sys.argv else STEPS[1:] if "--no-retrieve" in sys.argv else STEPS
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    with open(LOG, "a", encoding="utf-8", newline="\n") as log:
        log.write("\n== pipeline start %s pid %d\n" % (now(), os.getpid()))
        for i, step in enumerate(steps, 1):
            name = " ".join(step)
            status(state="running", step=i, of=len(steps), command=name)
            log.write("== [%d/%d] %s  %s\n" % (i, len(steps), now(), name))
            log.flush()
            p = subprocess.run([PY] + step, cwd=HERE, env=env, stdout=log, stderr=subprocess.STDOUT,
                               stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)
            log.write("== [%d/%d] exit %d  %s\n" % (i, len(steps), p.returncode, now()))
            log.flush()
        log.write("== pipeline done %s\n" % now())
    status(state="done")


if __name__ == "__main__":
    main()
