# Lessons (corrections log)

## 2026-07-01 — Archive superseded planning docs explicitly, don't rely on git history
**What happened:** during the thermal pivot I rewrote `tasks/todo.md` in place,
counting on git history to preserve the old content. The user wanted the old plan
kept as a visible backup doc.
**Rule:** when a pivot/supersession replaces or rewrites a planning/status doc,
first copy the outgoing version to an explicit dated archive file (e.g.
`<name>-archive-YYYY-MM-DD-<reason>.md`) with a provenance header, and link it
from the replacement. Git history is provenance, not a browsable backup.

## 2026-07-31 — `pkill -f <pattern>` matches the shell that runs it
**What happened:** to clear leftover preflight processes I ran `pkill -f pw.x` over SSH.
`-f` matches the whole command line, and the command line of the bash process *executing
that very command* contains the string `pw.x` — so it killed its own session. That bash
was the container's foreground process, so the Vast.ai instance exited. By the time it
could be restarted the interruptible slot had been taken by another tenant, and the box
(with its finished QE install) was lost.
**Rule:** never `pkill -f` with a pattern that appears in the killing command line. Use
`pkill -x <exact-process-name>` (matches the name, not the cmdline), or resolve the PID
first (`ps -eo pid,cmd --no-headers | awk '/patt[e]rn/{print $1}'`) and `kill` that literal
PID. The bracket trick (`patt[e]rn`) exists for exactly this reason.

## 2026-07-31 — Vast.ai `cpu_cores_effective` is an advertisement; measure it
**What happened:** a box advertising 128 `cpu_cores_effective` delivered ~20–25 real cores;
a dual-socket EPYC 7742 advertising 256 delivered ~47. QE was launched at 96 ranks on the
first one and crawled at ~4 min per SCF iteration — the docs/23 s8 thrash, one level up.
**Rule:** rent, then **benchmark before uploading anything**, and size ranks to the measured
number. A 60-second parallel-scaling probe costs about $0.01 and is the difference between
a 3-hour run and a 20-hour one. Expect SMT to add ~nothing for DFT: on the EPYC 7742,
64 workers gave 47 effective cores and 128 workers gave 50.
**Corollary — write the benchmark correctly.** My first version used a 0.16 s work unit and
a cold `mp.Pool`, so process-spawn dominated and it reported ~28 cores where the true figure
was ~47. Use a work unit of several seconds, and warm the pool before timing. I nearly
discarded a usable box on a measurement artifact.

## 2026-07-31 — `apt install quantum-espresso-data-sssp` fails before Ubuntu 24.04
**What happened:** the SSSP pseudopotential package is its own source package and only
exists from noble/trixie onwards; on a 22.04 box `apt-get install` finds nothing and the
setup script reported all five required UPFs missing.
**Rule:** it is `arch:all` (pure data), so pull the .deb straight from
`pool/universe/q/quantum-espresso-data-sssp/` and `dpkg -x` it — release-independent.
Note the pool path uses the *source package* name, not `quantum-espresso`.
**Bonus check worth repeating:** pw.x prints an MD5 for every pseudopotential it reads.
The O/H/Cr/Ni MD5s from this .deb match the 2026-06 campaign's archived outputs exactly,
which is a free, airtight proof that new runs sit on the archive's footing.

## 2026-07-31 — `--bind-to core --map-by numa` silently cripples MPI inside a container
**What happened:** on a 2-socket EPYC 7742 Vast box I "improved" the proven mpirun line to
`--bind-to core --map-by numa`. PRTE logged one line — *"tried to bind a process but failed …
performance may be degraded"* — and continued. The ranks then migrated across sockets and sat
blocked in collectives: the host showed **87.5% idle** while pw.x crawled at ~105 s per SCF
iteration, against a cgroup quota of 245 CPUs we were nowhere near using. Reverting to
`--bind-to none` took host utilisation from 12.4% to 44.2% (~32 → ~113 cores of useful work)
with zero binding warnings.
**Rule:** inside a Vast/Docker container hwloc usually cannot see the true topology, so
explicit binding fails and leaves ranks unpinned *and* mis-mapped. Use `--bind-to none` (what
docs/23 s8 shipped at 99% core efficiency) unless you have verified binding actually took.
**Diagnostic that finds this fast:** if `top` shows the host mostly IDLE while your ranks are
"running", they are blocked, not throttled — check the bind warning and the cgroup quota
before assuming you were sold fewer cores than advertised. Idle host + slow job = communication
problem; busy host + slow job = oversubscription.

## 2026-07-31 — killing a job cleanly is how I found the *third* `JOB DONE` false success
**What happened:** `Ni_slab/s0_O` stalled — SCF descended cleanly for 80 iterations
(432 → 2.1e-4 Ry, a tidy ~0.85×/iteration decay) then went dead flat for 4 against
`conv_thr = 1e-6`, still on ionic step 1 of ~20 at ~150 s/iteration. Rather than
`pkill` (which once killed the container — see the lesson above), I stopped it with QE's
own mechanism: `touch <outdir>/<prefix>.EXIT`. pw.x exited gracefully in 20 s … and
**printed `JOB DONE.`**. The queue logged `rc=0 JOB_DONE=1 SCF_FAIL=0` — passing the first
two clauses of my own pre-registered acceptance criterion on a job I had just killed.
Worse, `qe_qc.py` called the file **TRUSTWORTHY**, because its `n_ionic == 0` clause (there
to admit genuine `calculation='scf'` gas references) fired on a relax that died inside its
first ionic step with a **null energy**.
**Rule:** `JOB DONE` means "pw.x reached its exit routine", nothing more. Three distinct
ways to get it with no result: SCF failure, `nstep` exhaustion, and a user `.EXIT` stop.
The only safe gate is "did this run produce an energy I can defend" — so **make "has an
energy" a hard precondition for any TRUSTWORTHY verdict**, and never accept a job on log
strings alone.
**Generalisation:** when a QC tool and the thing it checks are written by the same person
in the same session, the tool inherits the blind spots. Deliberately feeding it a file I
*knew* was worthless is what exposed the hole — do that on purpose, not by accident.
`tests/test_qe_qc.py` now pins all three modes.

## 2026-07-31 — a flat `estimated scf accuracy` is a decision point, not a wait
**What happened:** the temptation was to let the stalled Ni job run, since `electron_maxstep`
was 500 and it had "only" used 85. At ~150 s/iteration that was 17 more hours and ~$10 to
arrive at `convergence NOT achieved … stopping` — and it was still ionic step 1 of ~20, so
even a *healthy* SCF put the job at 8–16 h. It was also stealing 12 ranks from the anchors,
which are the actual deliverable.
**Rule:** when SCF accuracy plateaus, compute three numbers before deciding — decades still
to go, seconds per iteration, and *how many ionic steps remain*. The third usually dominates
and is the one that gets forgotten. A job that cannot finish in budget even if it unsticks
should be killed the moment you know that, not when it fails.

## 2026-08-01 — Vast's "SSH key associated" is bookkeeping, not installation
**What happened:** two boxes in a row refused me. The proxy route reported
`Connection refused`, which reads exactly like a host still provisioning, so I
destroyed the first one as a bad host. It was not. The **direct** route
(`public_ipaddr` : `machine_dir_ssh_port`, both in the instance JSON) reported the
real error — `Permission denied (publickey)`. The container was listening the whole
time. `ssh -v` then showed my client offering the correct key, the account record
matched my local `id_ed25519.pub` byte-for-byte, and the attach API answered
*"SSH key already associated with instance."* All true, and the key was still not in
the container's `authorized_keys`: `vastai/base-image:cuda-12.4.1-auto` never acts on
the association.
**Rule:** never diagnose a Vast box from the proxy alone — it masks auth failures as
connection refusals. Check the direct route before concluding anything about a host.
**Fix that always works, regardless of image:** pass an `onstart` that installs the key
itself, and a sentinel you can verify:
```
mkdir -p /root/.ssh && echo '<pubkey>' >> /root/.ssh/authorized_keys &&
chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys &&
echo KEY_INSTALLED > /root/.key_ok
```
SSH answered 40 s after `actual_status` went `running`. Cost of diagnosing it the slow
way: ~$0.12 across two destroyed boxes.
**Also:** poll `actual_status == "running"`, not `cur_state`. `cur_state` flips to
`running` when the *contract* is active — billing starts there, but the container may
still be pulling its image.

## 2026-08-03 — a Vast box can be broken in a way the status field never shows

`actual_status: running`, `status_msg: "success, running ..."`, SSH port open and
answering — and the instance was still unusable. Instance 46725846 (machine 129402) had
its own launcher in a crash loop:

```
/.launch: line 48: ssh: command not found      <- once per second, forever
```

Symptoms that looked like the familiar key problem but were not:
- direct route `public_ipaddr:machine_dir_ssh_port` → `Permission denied (publickey)`
- proxy route `ssh_host:ssh_port` → `Connection refused` (the reverse tunnel never opened)
- `POST /instances/<id>/ssh/` → `"SSH key already associated with instance."`

**Rule: when SSH fails on a fresh box, pull the boot log BEFORE re-trying, re-keying, or
waiting.** One call settles in seconds what guessing costs minutes of billed time:

```
PUT /api/v0/instances/request_logs/<id>/   {"tail":"120"}   -> {"result_url": ...}
# then GET result_url (S3, takes ~5-20 s to populate)
```

`Permission denied (publickey)` means the container's sshd is up and the key is missing.
`Connection refused` on the proxy route means the launcher never registered the tunnel —
that one is a broken host, and no amount of key installation fixes it. Destroy and move
to a **different machine_id**, not merely a different offer on the same machine.

Cost of finding this the slow way: $0.044. Cost of not checking the log first: however
long you spend re-attaching keys to a box that cannot run sshd.

### Addendum, same day: `intended_status: stopped` on a freshly created instance

The replacement box (46726365) then sat at `actual_status: loading` for ten minutes.
The log call returned `Error response from daemon: No such container: C.46726365` — the
container had never been created at all. The reason was in the instance record:

```
actual_status    loading      <- the field we poll
cur_state        stopped
intended_status  stopped      <- Vast never asked the host to start it
```

`PUT /api/v0/asks/<id>/` returned `{"success": true, "new_contract": ...}` and still left
the contract in a stopped state. Fixed with an explicit
`PUT /api/v0/instances/<id>/ {"state": "running"}`.

**So `actual_status` alone is not enough either** — it read `loading` the whole time,
which is indistinguishable from a slow image pull. Check `intended_status` on any box
that has not become reachable within a few minutes; if it says `stopped`, no amount of
waiting will help. Combined rule for a new box: poll `actual_status`, and if it has not
gone `running` in ~3 min, look at `intended_status` and the boot log before anything else.
