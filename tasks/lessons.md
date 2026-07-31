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
