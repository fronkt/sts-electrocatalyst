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

### Addendum 2: neither SSH route is diagnostic on its own

The 2026-08-02 lesson said "diagnose via the direct route `public_ipaddr`:`machine_dir_ssh_port`".
That was right for the box it was written on and **wrong for the next two**:

| box | direct route | proxy route (`ssh_host`:`ssh_port`) | truth |
|---|---|---|---|
| 46518763 (08-02) | answers, key missing | — | key not installed |
| 46725846 (08-03) | `Permission denied` | `Connection refused` | host launcher crash-looping |
| 46726365 (08-03) | never answers | **works** | fine; host exposes proxy only |

On the last one I polled the direct route for ten minutes while sshd was up and healthy
the whole time, with my key installed — the boot log said `ONSTART_KEYS 1`,
`ONSTART_SSHD 1`, `Server listening on 0.0.0.0 port 22`.

**Rule: try BOTH routes, and treat the boot log as the only authority.** A host may
expose either, both, or neither. `Permission denied` from one route while the other is
refused is a broken launcher, not a key problem. And put explicit markers in the
`onstart` script (`echo ONSTART_KEYS $(wc -l < authorized_keys)`) so the log answers
"was the key installed?" directly instead of by inference from a failed connection.

## 2026-08-03 — every threshold I encoded about "normal" chemistry was too narrow

Three separate thresholds in `src/dft/adsorbate_qc.py` were falsified by the very data
they were written to judge, inside 48 hours:

| threshold | asserted | falsified by |
|---|---|---|
| `M_O_BOND_MAX = 2.40 A` | "real bonds are 1.6-2.1, failures at 3.8-4.0, **nothing legitimate lands in between**" | Fe `*OOH` relaxed to a genuine minimum at **2.552 A**, 0.376 eV below the desorbed original |
| `dG4 > 0` | "no real OER intermediate gives an exergonic fourth step" | repaired Mn gives **-0.022 eV** after a full 34-step relaxation; G_TOTAL is experimental while dG_OOH carries 0.1-0.2 eV of GGA error |
| median outlier test, all states | "genuine chemistry varies far less than 0.20 A" | `*OOH` binding is **bimodal** (Ir/Ru/Cr 1.91-2.08 vs Mn/Fe 2.48-2.55); the test accused both DFT-verified repairs |

The pattern is one-directional: **I never encoded a threshold that was too permissive.**
Every one assumed the physical spread was narrower than it is, and each was written in
confident prose ("nothing legitimate lands in between") that made it harder to question.

Rules taken from this:

1. **Derive thresholds from the data you already have, not from what sounds physical.**
   Print the actual spread first (`s0_O` 0.202 A, `s0_OH` 0.089 A, `s0_OOH` 0.640 A) and
   set the cut from it. Two of the three would have been caught by looking.
2. **A summary statistic assumes a shape.** A median-based outlier test silently assumes
   unimodality. Check the distribution before choosing the statistic, especially when a
   physical mechanism (weak vs strong chemisorption) could split it.
3. **Prefer a three-tier verdict to a binary one** where the middle is genuinely
   ambiguous: bound / weak / desorbed, with only the extreme failing and the middle
   surfaced for a human. A binary cut forces a wrong answer on every ambiguous case.
4. **When a check fires on data you independently verified, the check is the suspect.**
   All three of these were found that way, not by reasoning about the threshold.

---

## Compute estimates keep coming in low, and always for the same reason (2026-08-05)

Third mis-costed run in a month, each one a *3.5x-or-worse* underestimate extrapolated
from a cheaper system than the one actually being bought:

| run | basis for the estimate | projected | actual | over |
|---|---|---|---|---|
| repair campaign (docs/33 s5b) | non-magnetic anchors | $0.6-1.1 | $2.64 | 2.4x |
| n=7 campaign (docs/35 s6) | 3 concurrent jobs / 12.1 h | $3.20 | $8.17 | 2.5x |
| HEA screen (this one) | **pure endmembers, ~51 s/relaxation** | 1.5 h/candidate | **5.2 h** | 3.5x |

The endmember timings came from *pure* MO2 slabs. An HEA slab of the same 72 atoms has
four cation species, no symmetry, and a rougher force landscape, so BFGS takes far more
steps to reach the same `fmax`. Relaxation count was estimated correctly; **cost per
relaxation was assumed transferable between a symmetric and a disordered cell, and it
is not.**

Rules taken from this:

1. **Time one instance of the real thing before sizing the batch.** I timed a pure slab
   and a loose-`fmax` smoke run, neither of which is the workload. One full HEA
   candidate at production settings would have cost 5 h and saved a 62-hour commitment.
2. **Symmetry is a speed feature.** Any estimate crossing from ordered to disordered
   cells needs a measured multiplier, not an assumption of parity.
3. **Checkpoint per unit of work so a bad estimate is survivable.** The screen writes
   after every candidate, so the 3.5x miss cost nothing but wall-clock -- the partial
   result is a valid ranked list at all times. This is the one thing that went right.
4. **Do not economise by cutting the sampling that the science needs.** The obvious
   response to a slow screen is fewer sites; candidate 1 immediately argued the other
   way (best site 0.59 V below the site mean, and found only in the third decoration).
   Buy speed with hardware, not with statistical power.


## A model comparison is only as good as its worst-matched axis (2026-08-06, docs/38)

R0 rejected UMA, R3 accepted MACE, and the whole screen rests on that pair of verdicts.
The two models had **never been scored the same way**. Six axes differed -- DFT
reference (two of UMA's four points were later found defective), n (4 vs 7), start
geometry (builder at 3.07 A vs DFT-relaxed frames), starts per state (1 vs 3), dtype
(unrecorded vs explicit float64), and constraint mask -- and **every one of them ran in
MACE's favour**.

None of it was fraud; it was drift. Each change was individually reasonable and
separately documented. The comparison rotted because nothing ever re-ran the *old* arm
after the world moved. Worse, the code said otherwise: `evaluate_relaxed`'s docstring
claimed "This function does what UMA did" while starting from the DFT minimum, and
docs/34 claimed "builder geometries only -- no DFT input of any kind" when three of its
21 starts had been overwritten with MACE- and DFT-derived coordinates.

The saving grace is that running the matched experiment cost **16 minutes of laptop CPU
and $0**, and the conclusion survived intact.

Rules taken from this:

1. **When the reference moves, re-score every arm against it -- not just the current
   favourite.** The repair regenerated MACE's numbers and left UMA's untouched, so the
   comparison silently became reference-vs-reference. If re-running an arm is too
   expensive, say so explicitly in the doc; do not let the stale arm keep its old number
   in a table beside a fresh one.
2. **A superseded artifact must be stamped, not just superseded in prose.** docs/29 s8
   corrected the record in text while `docs/figs/uma_oc22_parity.json` kept publishing
   the retracted Cr = 1.726 for four more days. Prose corrections do not propagate to
   files. Add a `SUPERSEDED_BY` key.
3. **Docstrings that assert an experimental equivalence are claims and need testing.**
   "This function does what UMA did" was load-bearing and false. If a comment says two
   procedures match, either a test pins the axes that must match, or the comment states
   which axes do *not*.
4. **Suspect any comparison whose every difference points the same way.** Independent
   drift is unbiased; a clean sweep in one direction means the axes were chosen, however
   unconsciously, after the answer was known.
5. **Report the fragile cut next to the headline.** MACE meets the gate at n = 7 and
   fails it at n = 5, and the two points that make the difference are the ones seeded
   from MACE's own minima. That belongs in the same table as the headline, not in a
   caveats section -- so `parity_matched.py` prints both cuts by default and a test
   enforces that a rho above threshold with p > 0.05 is never reported as MET.


## A universal claim needs a universal search, not three samples (2026-08-06, docs/39)

R0 concluded "UMA cannot rank rutile-oxide OER" after testing `oc20`, `oc22` and `oc25`.
The `omat` head was one CLI argument away and was never tried. It scores rho = +0.964,
p = 0.0028, MAE 0.125 V -- better than the MACE model the whole screen was built on.

The reasoning error is instructive and was not laziness. R0 reasoned hard and correctly
about which *adsorption* dataset matched our chemistry: OC22 is PBE+U oxides with
O*/OH*/OOH*, so `oc22` was the right hypothesis **within the space R0 was searching**.
That space was "adsorption heads". The head that works is a **bulk-energetics** head,
trained on PBE/PBE+U VASP inorganic crystals -- the same functional family as our own
reference, and never considered because it has no adsorbates in it at all. The search
was well-executed inside a frame that was itself too narrow.

Rules taken from this:

1. **Match the claim's scope to the search's scope.** "No head works" needs every head,
   or the claim shrinks to "the heads we tried". Cheap tests that would close a
   universal quantifier are worth running BEFORE the claim is written, not after it has
   been load-bearing for two weeks.
2. **When a model family exposes a small enumerable option (heads, tasks, checkpoints),
   enumerate it.** Seven heads at ~9 min each is 1 hour. The cost of not doing it was a
   published negative that a pre-registered one-hour run overturned.
3. **Pre-register before running, even when -- especially when -- the run is cheap and
   post-hoc.** This was the project's only post-hoc addition to a pre-registered
   protocol. Freezing rho >= 0.8 AND p < 0.05 and pushing it first is the entire reason
   the falsification is credible rather than a suspicious late reversal. Had the
   criterion been written afterwards, the same numbers would prove much less.
4. **Commit to both outcomes in writing, in advance.** docs/39 s4 said what a pass would
   mean before the pass existed. That made reporting an inconvenient result mechanical
   instead of a judgement call made under the temptation to protect an existing story.
5. **Distinguish "ranks better" from "is the better tool".** `omat` wins the ranking and
   desorbs `*OOH` on 5 of 7 metals. The tier tolerates that because most metals are
   pls <= 2; the HEA screen would not. A single headline statistic can be genuinely
   better while the model is genuinely worse for the actual job.


## "Independent routes" usually means independent PREDICTORS, not independent EVIDENCE
(2026-08-06, docs/40)

I wrote, in docs/38 s2, that MACE "meets the gate by three independent routes": the DFT
tier's 18-atom cells, the screen's 2x2 Vegard slabs, and UMA's protocol. All three score
against the same seven DFT numbers, and MACE was *selected* on those same seven. Three
protocols, one target. Seven distinct values, not twenty-one. Held-out points: zero.

The sentence felt true when written because the three routes really are different --
different cell, different start geometry, different multi-start. Every one of those
differences is on the PREDICTOR side. Varying how you ask does not add evidence if you
keep asking the same question.

The same audit found the coupling I had already disclosed was wrong in its particulars:
docs/38 s5(iii) named Ni and Co as the seeded points. Co's `s0_OH` is not seeded at all
(rms 0.502 A) and Co is pls=1, so its eta rests on no seeded basin -- dropping Co
*improves* the correlation. The genuinely load-bearing seeded point is **Cr**, which I
never named: reverting it drops both models below significance.

Rules taken from this:

1. **Count distinct TARGET values, not distinct experiments.** Before writing "N
   independent validations", ask how many distinct reference numbers they are scored
   against. If the answer is "the same set every time", write "N protocols against one
   target" instead.
2. **A disclosed limitation still needs auditing.** I had disclosed the coupling and
   still got two of its three parts wrong -- one overstated (Co), one missing entirely
   and larger than both (selection on target). Writing the caveat is not the same as
   measuring it. Grep the actual files; diff the actual geometries.
3. **Measure how load-bearing each point is, and publish the whole spectrum.** The
   leave-one-out sweep (MACE meets the gate on 3 of 7 cuts, omat on 7 of 7) says more
   about robustness than the headline rho does, costs nothing, and would have flagged
   Cr months ago.
4. **A sensitivity number is not an alternative hypothesis.** Reverting Cr collapses both
   gates -- but 1.726 V was a trapped stationary point 1.396 eV above the restart, so
   "what if Cr were 1.726" is not a live possibility. Report such numbers as *how much
   rests here*, never as *how likely we are wrong*, or the disclosure becomes its own
   distortion.
5. **Do not inflate a limitation to look rigorous.** The tempting move was to cite a
   Csanyi-group paper on selective-U pathology next to our own striking U-partitioned
   desorption (p = 0.048). That paper has no rutile, no OER, never evaluates UMA, and its
   mechanism predicts our regime is exempt. Overstating a limitation is as wrong as
   hiding one, and in a competition report it needlessly damages a valid result.

## A parse result that contradicts direct evidence is a parse bug (2026-08-09, docs/41 s6g)

**What happened:** the archive symmetry audit reported **0 of 156 outputs constrained**. That
was flatly impossible: `orient_starts.py` had already shown, by reading the force blocks
directly, that four specific runs carry max|F_y| = 0.0000000000 Ry/au over every ionic step,
which cannot happen without an enforced mirror. My regex assumed pw.x prints
`Sym. Ops., no inversion, found 2 symmetry operations`. It actually prints the count FIRST:

    2 Sym. Ops. (no inversion) found ( 1 have fractional translation)

so the pattern never matched, every row fell through to the "not printed" bucket, and a
fallback regex mislabelled 72 runs as free. Corrected, the number is 76/156 constrained and
the header agrees with the force evidence on all 96 adsorbate runs.
**Rule:** before believing a parse, check it against a fact established by a *different*
route. Here the force blocks were the independent witness and they were already in hand. A
0% or 100% answer to an empirical question is a bug hypothesis first and a finding second.
**Corollary that paid for itself:** building the cross-check into the tool rather than doing
it by hand is what turned a bookkeeping script into the finding -- the three-way LOCKED /
ON_PLANE / EXPLORED split only exists because the tool measured forces *and* read the header,
and `nosym` set with nothing to push against turned out to be its own regime.

## An optimisation justified as "same physics" is a physics claim, and needs a physics test (2026-08-09, docs/41 s6g)

**What happened:** on 2026-07-31, commit `1a3a77b` ("make the Ru/Ir anchors runnable and 4x
cheaper") noticed that `runs/Cr_slab/s0_OH.in` ran at 15 irreducible k-points while
`runs/Mn_slab/s0_O.in` paid for 36, and wrote into `qe_slab.py`: *"An adsorbate lowers the
symmetry by itself ... same physics, 2.4x the bill."* It then made `nosym = False` the rule
for every adsorbate deck. Both premises were false. The adsorbate is built at y == 0, exactly
ON the mirror plane, so it preserves the symmetry rather than breaking it; and the "same
physics" is a 2-D constrained optimisation worth -291 meV on Ir's *OOH. Ir and Ru were built
under the new rule and are symmetry-locked on all three states, which is where two of the
campaign's three unexplained anchor offsets come from.
**Rule:** "this only changes cost, not the answer" is a claim about the physics, not about
the budget, and it needs to be tested like one -- run both and diff the energy, once, before
adopting it. Cost optimisations are the most dangerous kind of change precisely because they
come with a built-in reason not to check them.
**Second rule, narrower:** never infer symmetry from a description of the structure ("an
adsorbate lowers the symmetry"). Read what pw.x actually reports -- it prints the group size
in the header of every single run, for free, and it disagreed with the description here.
**Third:** the two runs the argument was checked against were the two whose difference it was
explaining. A comparison cannot be its own control.

## "We disabled the constraint" is not evidence the search explored (2026-08-09)

**What happened:** the endmember decks for Mn/Fe/Co/Ni/Cu carry `nosym = .true.`, so the
campaign had been treating those relaxations as unconstrained. Six of eleven such states have
max|F_y| below 1e-4 Ry/au -- they never left the mirror plane. `nosym` removes the constraint
but supplies no reason to move; on an exactly symmetric input it changes nothing. The flag and
the outcome are different claims.
**Rule:** a search is evidenced by what it measured, not by what it was permitted to do. Cite
the measured off-plane force or displacement, never the input flag. Any off-plane arm must
carry a *physical displacement* as well as `nosym`/`noinv`.

## A derived "noise" statistic must be shown to scale like noise before it is used as one (2026-08-23, docs/49 s4-4b)

**What happened:** block 1C's analyzer propagates its verdict floor from sigma_F measured as
the Hessian's own asymmetry |H - H^T|. At delta = 0.01 A that gave UNDERPOWERED; I predicted
the registered delta = 0.02 A rerun would drop the floor ~4x (floor ~ sigma_F/delta^2) and
launched 19 SCFs on that expectation. The floor ROSE (i265 -> i374) while the mode itself
did not move (i244.7 -> i242.8). The asymmetry was never noise: split by block it scales
x4.00 (forward-difference truncation) and x7.85 (central-difference truncation) with delta,
and a noise-driven statistic would scale x1.00. The true force noise, measured from
identities the SCF does not enforce, is 2e-7 Ry/bohr and delta-flat -- 50x below design.
**Rule:** before predicting how a derived statistic responds to a parameter change, check
what it actually measures on the data in hand: a noise estimator must be invariant under the
control it is supposed to be invariant under. One cheap test (here: rerun at 2x delta and
compare the estimator, per block) settles it; predicting from the formula's *label* does not.
**Second rule:** when an estimator is found to measure the wrong thing, do NOT repair the
analyzer and re-score -- the repair is an instrument choice with verdict consequences and
belongs to the entrant, written with the outcome disclosed (docs/47 A8.7). Bank the numbers
under every reading and put the choice in front of him.

## 2026-08-25 — a feasibility check must test the run you are about to make, not a different one

**What happened.** I built an A8.4 rung-(i) "self-seed": step 1 re-runs a failing deck as a
plain `scf` at a deliberately loose `conv_thr = 1.0d-4` to manufacture a density, step 2
reads it back. I added an assertion that the seed threshold was reachable, and proved it
from the *cold relax's* own accuracy history ("reaches 1.0d-4 at iteration 260"). All three
seeded rows failed, two at the child and one at the seed itself.

**Why the check was wrong.** `conv_thr` in QE is not an isolated stopping rule — it sets
the floor for `ethr`, the iterative-diagonalization accuracy. Measured on the same deck:
`conv_thr = 1e-6` reached `ethr = 3.14e-9`; `conv_thr = 1e-4` reached `9.43e-8`, 30×
looser. The 1e-4 run and the 1e-6 run are **different dynamical systems**, so one's trace
cannot certify the other's. My assertion answered "does a trajectory exist that crosses
1e-4" when the question was "does *this* trajectory converge."

**The second, independent error.** The seed threshold was also *looser than the floor the
failing runs already reach unaided* — 1e-4 against 6.37e-6 / 1.836e-5 / 1.132e-5, i.e.
5.4× to 15.7× worse. So even a converging seed would have handed over a density worse than
the failing run's own endpoint. I never asked whether converging at that threshold was
worth anything.

**Rules for myself.**
1. When a check certifies that a run will work, the evidence must come from a run with the
   **same registered parameters**. A trace from a different threshold, mixing, or cutoff is
   not evidence about this run.
2. Before spending compute to "improve" a starting point, compare the proposed starting
   point against **where the failing run already gets on its own**. If it is worse, the
   step cannot help regardless of whether it succeeds.
3. `conv_thr` propagates downward (`ethr`, and via `upscale` it also moves during `relax`).
   Never treat it as a free knob.
4. When a remedy changes two things at once — here a fresh Broyden history *and* a
   degraded density — the result tests neither. Say "untested", not "refuted".

**Related:** the same day's `upscale` discovery (docs/45 CORRECTION) is the mirror case —
an unset parameter silently tightening `conv_thr` during relax.

## 2026-08-26 — separate the cluster's failures from the science's before concluding anything

Round 5 (array 20141568) came back 5 COMPLETED / 3 OUT_OF_MEMORY / 3 RUNNING. Read as a
score, that is a mediocre round for `mixing_ndim = 16`. Read correctly, the hypothesis was
never tested on four of the eleven rows: **all three OOM kills, and a fourth job that hung,
were on the single node a196**, which Slurm had already drained with
`Reason=NHC: Terminated by signal SIGTERM` and which reported 384 MB free on 128 cores.

The tell was in the numbers, not the state string. The killed jobs died at **MaxRSS
8.65–8.70 GB**; the same array's successful jobs peaked at **30.8–46.8 GB**. A job killed
for memory while using a fifth of what its siblings use is not a job with a memory problem.
Taking `OUT_OF_MEMORY` at face value would have sent me tuning cutoffs, pools or `nbnd`
against a fault in someone else's hardware.

**Rules for myself.**
1. When a scheduler reports a resource failure, compare the failing job's resource use
   against a *successful sibling in the same array* before believing the label. Wildly
   lower usage means the node, not the job.
2. Group failures by node before grouping them by deck. One node holding every failure is a
   hardware hypothesis; the decks having nothing in common is a hint, not the answer.
3. A job that is RUNNING is not a job that is running. Check `.out` mtime against now and
   count actual iterations. Zero SCF cycles with a frozen file for 45+ min is a hang, and
   on a 48 h walltime it will silently burn thousands of SU. Cancel it.
4. Rows lost to infrastructure are **not evidence** and must be re-run unchanged. Never let
   them contribute to a verdict on the parameter under test, in either direction.

## 2026-08-26 — score a `__g1` child on magnetization first and energy second

Three `__g1` children landed in round 5: +0.026 meV, +7.395 meV and +747.449 meV against
their banked parents. Energy alone makes that one pass and two failures of the ±1 meV gate,
as though two banked numbers were in doubt.

The magnetizations say something else: Δmagtot +0.00, **+4.00** and **+4.73**. Both
"failures" are cold SCF starts that fell into a different magnetic branch at the *same*
geometry. That is not a disagreement about the banked energy; it is a different question
being answered, and the A8.3 density-retention remedy is what makes the child answer the
intended one.

The Fe row shows why the second column has to be read too: Δmagtot **+4.00** with Δmagabs
only **+0.03** means the local moments did not change size at all and roughly 2 μB flipped
from down to up. A ferrimagnetic rearrangement 7.4 meV away is a physics finding;
"failed the 1 meV gate" would have buried it.

**Rule for myself.** Never score a repeated or child DFT run on energy alone in a
spin-polarised system. Report ΔE, Δmagtot *and* Δmagabs together, and classify a
magnetization mismatch as BRANCH MISMATCH — never as agreement and never as refusal. The
rule this rests on is now 9 for 9 in this repository: matching magnetization reproduces the
energy to ≤0.52 meV, differing magnetization differs by tens to hundreds of meV.

## 2026-08-26 — on this Windows box, `pathlib.read_text()`/`write_text()` default to cp1252

Editing `anvil/rcac_ticket_draft_2026-08-24.md` with `read_text()` + `write_text()` wrote
two em dashes as the single byte `0x97` and left the file invalid UTF-8. The round trip is
silent for characters that already existed (a UTF-8 em dash decodes to three cp1252
characters and re-encodes to the same three bytes); only text *I* added in the same edit
was corrupted, and only on the write. A later edit to `tasks/lessons.md` crashed on `Δ`
instead of corrupting quietly, which is the only reason I looked.

**Rule for myself.** Always pass `encoding='utf-8'` explicitly to `read_text`/`write_text`/
`open` in this repo, or do the edit with a byte-level `cat >>` heredoc. After any scripted
edit that adds non-ASCII text, verify with `open(p,'rb').read().decode('utf-8')` before
committing.

## 2026-08-26 — measure progress in the units the calculation actually makes progress in

Six S3 decks were triaged, escalated four times each, and scored — all on **SCF accuracy**.
Every rung of the A8.4 ladder compared "minimum estimated scf accuracy reached" across
attempts and chose the next mixing parameter from it.

Scoring the same runs by **completed ionic steps** inverted the picture in one line.
`Co s0_OOH__2x1v_off` had 14 converged BFGS steps sitting in attempt2 — at the *original*
`mixing_beta = 0.3`, the setting the ladder had escalated away from — while attempts 3, 4,
5 and 6 each restarted from the original geometry and died in the first SCF with 0 steps.
Four escalations and roughly 1,000 SU went into re-running the single hardest step of a
trajectory that had already been walked most of the way.

Worse, comparing "min accuracy" across those attempts was never meaningful: a run that
completes 14 ionic steps reports low accuracies from late cycles that start from an
already-good density, while a run stuck in cycle 1 reports only cycle-1 values. I was
ranking two different quantities against each other and calling the result a ladder.

**Rules for myself.**
1. For a relaxation, the primary progress metric is **completed ionic steps**, not SCF
   accuracy. Report it first in every triage table.
2. Never compare a scalar aggregate (min, mean, last) across runs that did different
   amounts of work. Normalise to the same stage — first-cycle-only, or per-cycle — or do
   not compare.
3. Before escalating a parameter, check whether an EARLIER setting made more progress. If
   it did, the ladder is walking the wrong way and the next move is to resume from that
   run, not to escalate further.
4. When restarting from a previous run's geometry, scan **all** archived attempts and take
   the DEEPEST, never the most recent. `build_s3_round5.py` read `job + '.out'` and never
   looked at `job + '.out.attempt*'`; it was right twice by luck and wrong once expensively.
5. When a run stops, read what threshold it was actually being held to at that moment. This
   one stopped at `new conv_thr = 4.10e-8`, 24× tighter than the 1e-6 it registered — a
   threshold problem wearing a mixing problem's clothes.

## 2026-08-26 — when a name looks like a dead file, check what is actually in it

Archiving round 7's failures, my first archive list contained
`runs/s3/Co/ref__2x1v.out`, because the row that failed was the `Co ref__2x1v` chain and
that is the file the job name points at. It is the **banked parent** — 1.85 MB, converged,
irreplaceable at ~996 SU. The chain's actual dead output was `ref__2x1v.replay.out`, a
10 KB header-only OOM stub, because chain steps write under the *deck* name, not the job
name. I caught it only because I printed each file's size in the guard before moving it.

**Rules for myself.**
1. An archive/delete guard must print **what is in each file** — size, and ideally whether
   it carries `JOB DONE` — not just that the path exists and the target is free. A guard
   that only checks names cannot catch a right-name/wrong-file mistake.
2. Derive the file to archive from the thing that actually ran (the deck, the log line),
   never from the job or stem name by pattern.
3. After any archive step, re-verify that the results you intended to KEEP are still there
   and still the right size. Cheap, and it closes the loop.

## 2026-08-26 — a selector that was right twice can still be wrong in principle

Round 7's builder picked the geometry to resume from by **most completed ionic steps**. It
was right for three decks. It was wrong for Mn the moment a resume had already happened:
attempt1 had 19 steps at E = −3617.10180292, and the round-8 run that *continued from it*
had only 3 — at E = −3617.10197097, which is deeper. Selecting by count would have silently
thrown away three converged steps and restarted from further back.

The failure is that step count measures *how much work one run did*, while I needed *how far
down the trajectory the geometry is*. Those coincide only while every run starts from the
same place. The first successful resume broke that assumption, and the selector had no way
to notice.

**Rules for myself.**
1. State what a selector is a proxy FOR, then ask when the proxy and the target come apart.
   "Most steps" proxies "deepest geometry" only for runs sharing a starting point.
2. Prefer a metric measured on the thing you actually care about. Final energy within a
   magnetic branch measures depth directly; step count measures effort.
3. Make the builder **assert** the choice rather than compute it silently — "no same-branch
   run is deeper than the one chosen" would have failed loudly on Mn instead of quietly
   losing work — and print the full census so a human can audit the pick.
4. A heuristic that has worked N times has not been tested against the case that breaks it.
   Being right twice is not evidence of being right.

---

## 2026-08-26 -- I read the LAST value of a converging series as if it were the minimum

**What happened.** `Ni s0_OOH__2x1v_mir` attempt3 died with
`convergence NOT achieved after 500 iterations`, and its last printed
`estimated scf accuracy` was 3.431e-05. I read that as the cycle's floor,
concluded the row had genuinely stalled two orders of magnitude short, and
told the user that R1 (`upscale`) "would NOT have closed" it -- explicitly
retracting a correct earlier claim.

An adversarial pass sent me back to the raw trace. The cycle's **minimum** was
3.2e-07 at iteration 125, and **40 of its 500 iterations sat below the deck's
registered `conv_thr = 1.0e-06`**, the first at iteration 52. QE tests
convergence at every iteration and exits at the first crossing, so it never
reaches iteration 125, let alone the 3.431e-05 tail. R1 closes the row at
iteration 52. The same check on `Mn s0_OOH__2x1v_off__basin` found 124 and
**489** qualifying iterations in its two failing cycles.

The last value of a non-monotonic series carries no information about whether a
threshold was ever crossed. I used it as though it did, and it was the single
load-bearing number under a retraction.

**Rules for myself.**
1. For any convergence question, compute `min(series)` and
   `count(series < threshold)` and `argmin`. Never quote the tail value.
2. Before deciding a run "stalled", state the threshold **actually in force** at
   that moment separately from the one the input declares. Here they differed by
   up to 100x and the gap was the whole story.
3. When a tool reports failure, ask what criterion it applied -- not whether it
   failed. `convergence NOT achieved` meant "not against a threshold no deck
   registered", which is a different sentence entirely.
4. A retraction deserves at least the evidence the original claim had. I
   retracted on one number read off a tail; the original had been right.

---

## 2026-08-26 -- my geometry hash collided on the atoms that never move

**What happened.** To measure run-to-run reproducibility I grouped runs by a
hash of the starting geometry QE echoes back, then compared energies within each
group. It reported a clean, striking result -- and it was wrong. The hash
captured too few lines, and the leading atoms of every slab are **frozen**
(`0 0 0`), hence byte-identical between a parent's initial and final
coordinates. So relax parents grouped with their own SCF children, which sit at
a *different* geometry by construction, and I was comparing energies across
geometries while calling them replicates.

I caught it only because a downstream number looked odd (a "78 meV branch split"
at dmagtot 0.06) and I chased it instead of reporting it.

**Rules for myself.**
1. When hashing a structure for identity, hash **all** of it at full precision
   and assert the atom count. Print the count next to the hash.
2. Ask what fraction of the hashed content can vary at all. If most of the atoms
   in a slab are frozen, a structure hash is mostly hashing a constant.
3. Validate a grouping by checking a pair you already know the answer for,
   before deriving statistics from it.
4. A number that surprises me is a signal to re-derive, not to report with a
   caveat. Both of my first two censuses produced confident, quotable, wrong
   statistics.

---

## 2026-08-26 -- I built the strongest version of a claim I wanted to be true

**What happened.** Three claims I put to an adversarial panel came back refuted
3/3, and on the substance the panel was right each time:

- "The banked `Co ref__2x1v` reference cannot be reproduced." I had measured one
  replay (99.5 meV off) and never opened the *other* replay sitting in the same
  directory, which reproduces the parent to **0.167 meV and 0.08 uB**.
- "The lower 34.76 branch is the one that will not converge." It shows 19
  consecutive converged SCF cycles reaching the 1e-08 floor in 9-15 iterations
  each.
- "Splicing a geometry does not carry the magnetic state, so resumes cannot fix
  branch failures." True of every resume in the campaign **including the
  successes**, where the moment jumped 4.45 and 4.36 uB against the failure's
  0.24. A constant cannot be a cause.

The pattern is one thing: each claim was the dramatic reading of a real
measurement, and in each case the disconfirming evidence was already on disk in
a file I had not opened.

**Rules for myself.**
1. Before calling something irreproducible, enumerate **every** attempt on disk
   and score all of them. `ls` the directory; do not reason from the two files
   already in context.
2. State the mechanism, then check it is absent from the cases that worked. A
   mechanism present in the successes explains nothing.
3. Anchor a comparison to the value of record, not to whichever endpoint makes
   the gap quotable. I compared step-1 to step-1 (99.5 meV) while asserting a
   conclusion about a banked step-10 energy (110.8 meV).
4. Run the refutation pass **before** telling the user, not after. Three of
   these had already reached the user as findings.

---

## 2026-08-27 — I reported a blocked critical path from a filename and a stale table

I told Frank the campaign was stalled on two undeposited amendments, that A9 was
five days overdue, that S1's window closed that day, and that he should spend the
day re-authoring A9 thresholds. **All of it was wrong.** A8 and A9 were adopted and
deposited together on 2026-08-23, DOI 10.5281/zenodo.22072991, and he had already
cleared all 66 decision rows with "they pass with me."

Three sources agreed with each other and all three were misleading:

- `docs/47-amendment-8-DRAFT.md` and `docs/50-amendment-9-DRAFT.md` — the `-DRAFT`
  suffix **survives adoption** in this repo. The draft is kept verbatim as the
  historical artifact; the registered text moves into `docs/43`. Both files say
  `Status: ADOPTED ... appended to docs/43` in their **first six lines**, which I
  did not read because the filename had already answered the question.
- `docs/45 §E` — a status TABLE inside a file I have been appending to for days.
  Append-only habits rot tables specifically: the prose grows, the table does not.
- `docs/52` — a decision sheet compiled *before* the adoption it precedes, with no
  adoption stamp on its face. After the fact it reads exactly like a live queue.

The disconfirming evidence was two rows further down **the same file I was quoting
from** (`docs/45:51-52`: "ADOPTED + DEPOSITED 2026-08-23"). I had `sed`'d lines
70-82 and never looked up.

This is the same shape as the four refuted claims of 2026-08-26: the dramatic
reading of a real document, with the refutation already on disk in a place I had
not looked. The difference is that this one reached Frank as a recommendation to
spend a day of his time.

**Rules for myself.**
1. **A filename is not a status.** Before citing any document's state, open its
   header. `-DRAFT`, `-FINAL`, `-v2` are naming conventions, not lifecycle facts.
2. **Read the whole table, then look for its own contradiction.** If a table row
   says "blocked," grep the same file for the thing it says is blocking; a status
   table and a status paragraph in one file will disagree eventually.
3. **Registration status is read from the deposited text only** — `docs/43`, or a
   DOI line. Never from a tracking doc, a decision sheet, or a plan file.
4. **A deadline I compute myself gets verified before it becomes advice.** Saying
   "overdue" and "your window ends today" moves someone's whole day. That claim
   needs the same refute-pass as a physics claim, and I gave it none.
5. When about to recommend that Frank change what he is doing, that recommendation
   IS the finding — run rule 4 of the 2026-08-26 block on it before sending.

## 2026-08-27 — I claimed a refusal I had already broken forty minutes earlier

Building the S1 CI harness, I wrote in `docs/57` and in two READMEs that there was
"no shadow reader" and that "nothing here parses a pw.x output." Both were true of
the files I had just written. Both were false about **me**: forty minutes before
the first harness file, I had written `sweep.py` — a full per-atom, per-axis,
per-step force-block parser — and run it over all 480 outputs to choose fixtures.
An adversarial audit found it. I had not hidden it; I had forgotten it, and then
written a clean-hands sentence over the top of it.

Worse, the sweep measured F_x on the registered control populations, and the
deposited text says F_x "is **unmeasured on x** until v0.1 reports it" (:1858) and
"was never censused by the current code and is reported by v0.1" (:1864). So a
quantity the registration holds blind until the entrant's detector exists had been
measured by me, and my own documentation asserted the opposite of the fact.

**Rules.**

- **A statement about what I did not do covers the whole session, not the current
  file.** Before writing "no X was written", grep the scratchpad and the session's
  own artifacts for X. A refusal claimed in prose is a factual claim about my
  behaviour, and the reader cannot check it.
- **A throwaway script is still an artifact.** "It is only in the scratchpad" does
  not make it not-produced. If its OUTPUT shaped a committed file — and the fixture
  choices were shaped by it — it is part of the record and belongs in the disclosure
  with the thing it shaped.
- **When a registered document says a quantity is unmeasured, measuring it is an
  event.** Record the change when it happens rather than leaving it to be discovered in an
  audit.
- **Scope a refusal to what is checkable.** "No file in `.github/ci/` or
  `tests/silentgate/` parses a pw.x output" is verifiable and was what I meant. "No
  shadow reader" was not, and was wrong.
- **Audit the thing built to catch fail-opens for fail-opens.** The same audit found
  a green gate over an empty set (deleting the 11-run population made the face print
  "0/11 PASS"), and the one assertion the registration requires CI to perform was
  evadable by a Windows backslash. I had written both, and both survived my own
  review. Adversarial verification is not optional on work whose whole purpose is to
  be un-foolable.

## 2026-08-27 — I ran A0 work under an S3 job name and made the queue lie

Launching P-PROJ and A0-cell, I reused `anvil/43_submit_s3_wave1.sh` because it
carried the gates I wanted (PARITY_PASS, pseudo md5, the dry preflight). Its
runner hardcodes `#SBATCH -J s3-wave1`, so two A0 arrays sat in the queue
labelled as S3 wave-1 work. Frank saw `s3-wave1 CANCELLED` and reasonably asked
whether real campaign work had been killed. It had not — both arrays were mine,
submitted minutes earlier, still PENDING at 00:00:00 elapsed, and the genuine S3
arrays had COMPLETED hours before — but the queue could not be read to show that.

The label only got fixed by accident: I wrote `46_a0.slurm` for an unrelated
reason (A6.5(1) needs projwfc.x inline) and gave it `-J a0`.

**Rules.**

- **The job name is part of the launch, not decoration.** Reusing a submitter
  means inheriting its `-J`. If the work is not that stage, rename it in the same
  commit that reuses the script — before submitting, not three steps later.
- **`scancel` by ID is safe; a queue that misidentifies work is not.** The risk
  was never my command, which named two explicit IDs. It was that anyone reading
  `squeue`, or reaching for `scancel -n <name>`, would have been misled.
- **When someone asks "was that supposed to happen?", answer from `sacct`, not
  from memory.** Submit times, elapsed times and states settle it in one command
  and leave a record they can check themselves.
- **A shared launch path is a shared namespace.** The gates in a submitter are
  worth reusing; its identity is not. Copy the gates, set your own name.

## 2026-09-01 — I wrote Python source through a Python string inside a heredoc and lost my backslashes

Appending a test and patching a guard, I generated both edits from a Python script fed
through a heredoc, with the new source held in a `'''...'''` literal. `"\n"` inside that
literal became a real newline in the written test (SyntaxError: unterminated string), and
a `\`-newline continuation in the guard's condition was silently swallowed into one long
line. The census ran and matched run A, so nothing scored was wrong; the test file was
uncompilable until the user said "retry".

**Rules.**

- **Source code goes through exactly one layer of quoting.** Write new source with a
  plain `cat > file <<'EOF'` heredoc (or the Write tool), never as a string literal
  inside another program. If a patch must be programmatic, build backslashes with
  `chr(92)` and assert the written text compiles (`py_compile`) in the same command.
- **Run the tests in the same command as the edit.** The failure was caught only because
  pytest ran immediately; a later session would have inherited a broken suite with a
  green-looking commit.
- **A self-inflicted syntax error is a correction event.** It cost a user turn; it belongs
  here, not just in the fix.

## 2026-09-02 — two heredoc commands died at the same offset: the Bash tool caps a command near 10 KB

Twice in one session a long `cat > file <<'EOF'` command failed with "unexpected EOF while
looking for matching `''" at "line 87" / "line 91" — the same byte offset both times, inside
a quoted heredoc where bash cannot be parsing quotes at all. The wrapper truncates the
command; bash then sees an unterminated string and runs NOTHING (the earlier steps in the
chain silently never happened). The Write tool succeeded on the identical text.

**Rules.**
- **Anything over ~6 KB goes through the Write tool** (to the target, or to a scratch file
  that a one-line Bash then `cat >>`s). Never a long heredoc.
- **When a chained command fails at parse time, assume zero of it ran** and re-check the
  first step's effect before re-running the rest.

## 2026-09-02 — an external assistant's repo audit was one-third stale; verify before acting

A note listing "cheap, high-value, still-open" compute items read plausibly and cited the
repo. Checked against the tree: the Co U-ladder had run and converged (12/12; what is
missing is an s0_OOH row, not a submission); the RPBE probe had 10/10 outputs per metal;
ZPE−TΔS corrections were already applied in `referencing.py`; the ledger had already
downgraded the `upscale` call from "highest-value" to a 15 % trim. The risk statements
were sound. **Rule:** an AI summary of your own repo is a claim like any other — run the
same refute-pass on it that [[feedback_verify_ai_literature_claims]] demands for papers,
and only then let it set priorities.

## 2026-09-02 — I recommended against the rung ladder, the user overruled me, and the user was right

Asked which D1 option served rigor and STS placement, I first recommended NOT running the
β ladder (rescue optics), then reversed myself when I actually modelled the reader: a
computational chemist reads "0 of 16 SCFs converged" and asks "did you lower the mixing?"
The user chose B. The ladder returned 0 of 16 twice — no new physics — and was still worth
5,216.7 SU, because the report sentence changed from *"did not converge under our settings"*
to *"did not converge under three mixing settings across 19,200 iterations, while the
non-magnetic twins converge in 25."* The value was never in the chance of converging.

**Rules.**

- **Price a negative control by the sentence it buys, not by its chance of changing the
  result.** "We tried the obvious remedy and it failed too" is a different claim from "we
  did not try", and only compute can buy it.
- **A pre-registration's job is to make the decision before the outcome can bias it.**
  Registering both rungs and all three outcome readings BEFORE building any deck is what
  let 0-of-16-twice be reported as a result instead of an invitation to a third rung.
- **When recommending for or against an experiment, state the sentence each outcome
  produces.** My first answer weighed optics; the correct frame was what a skeptical
  reader can and cannot say afterwards.

## A threshold is a comparison — check both sides are the same KIND of quantity (2026-09-03)

**What happened.** I registered A11.R7's stability witness as "flag a metal when
`range_U(Δq_d) > |δq_c|`". That compares a *swing across U* against a *difference between two
states at fixed U*. Both are in electrons, so a dimensional check passes; the comparison is
still meaningless. Because |δq_c| is a small difference of two similar numbers, the rule fired
on 4 of 6 metals and gutted the primary test — it flags hardest exactly where the signal is
smallest.

**Why it matters.** One day earlier I logged a lesson about mixing a level and a swing when
*reporting* a distance (docs/68's 4.3 vs 8.5 meV). That lesson did not stop this, because I
checked the convention on the numbers I printed and never asked what the comparison *inside a
criterion* meant. A lesson scoped to output does not cover input.

**How to apply.**
- Before registering `A > B`, name what A and B each are out loud — a level, a difference, a
  range, a rate. Refuse the line if they differ. Dimensional agreement is not the test.
- Never scale a stability witness by the quantity under test; it guarantees the flag fires
  where the signal is smallest. Use a fixed absolute tolerance, or the response it qualifies.
- Honour a bad registered rule anyway, report the verdict as registered, and label any
  all-data figure POST-HOC. The alternative — changing the threshold once you can see the
  data — makes nothing in the result believable.

## Negative existence claims about your own repo need a grep, not a feeling (2026-09-03)

**What happened.** I wrote, in a committed document, "no script in the repo reads a
`.lowdin.txt`" and "A5.1(a)/(c) are unscored". Both false. `src/dft/extract_lowdin.py`
produces and validates those artifacts with a test that checks the entire bank of 265, and
`src/dft/lit1_urobustness.py` implements A5.1 (a)/(c)/(d) with tranche 1 banked three weeks
earlier.

**Why it matters.** Both were *negative* claims, and a negative feels like it needs no
evidence — you looked, you did not see it, you write "there is none". Both were one `grep`
from refutation. The real hole was narrower and much better: the analysis exists but covers
two metals on a different ladder, and the primary tracker is structurally unavailable on half
the grid that matters.

**How to apply.** Any sentence of the form "nothing in the repo does X" gets a literal search
pasted beside it before it is committed. And when the search does find something, do not
delete the bullet — the corrected, narrower claim is usually the stronger finding.

## 2026-09-03 — three lessons from the nine-item review

### An owed-list goes stale because nobody re-reads it, not because items stay open

Four of nine "dated lines owed" were already discharged, one of them three days earlier, and I
had restated the whole list to the user as live an hour before checking it. The closing line
always lives in a **different document** from the note that says the item is open — docs/59 §5
closed §3c while docs/60 still read "the licence is ungranted" in the present tense; docs/43:1979
closed the AFM scope while docs/43:1645 still said "still open" in its own frozen 2026-08-23
voice.

**Rule:** before repeating any "owed / open / HOLD / ungranted / not built" clause, grep for its
own **resolution token** (`AFM-SCOPE RESOLVED`, `§3c CONFIRMED`, `COUNTERSIGNED`) and check the
artifacts on disk. A count of built decks is an `ls`, not a recollection. A registration says
"still open" forever; only a later dated line can close it, and the registration will never
mention it.

### More n is not more rigor unless the extra n is independent

Asked whether A11.R7 should be re-run at higher n, the tempting answer was yes — read the
predictor at all seven U rungs and take n from 18 to 126. That is **pseudo-replication**: the
response `span_U` is one number per (metal, step), so the same y would be repeated seven times
against seven correlated x's, and the p-value would fall for an arithmetic reason rather than a
physical one. It looks like rigor and is the opposite.

**Rule:** before increasing n, ask what the *unit of independent observation* is. If the response
is defined per unit, you cannot get more units by subdividing the predictor. The real upgrade is
almost never more of the same sample — here it was a **different** sample that did not contain
the confound (the A0-SPIN arm, already banked, 0 SU), which turned a correlational question into
a falsification.

### A negative artifact claim is not finished until the remote has been searched too

I told the user the Co BASIN_DRIFT row needed "a file transfer, not compute", on the strength of
a local search. The remote had it too, I assumed. It did not: every Anvil `$HOME` tarball was
listed and the file exists for Ni and two Cr rows and **not for Co**. The remedy had never been
executed at all, which is a materially worse finding and a different fix.

**Rule:** "the output was never pulled" and "the run never happened" are different claims with
different remedies, and only one of them is cheap. Do not name the fix until the search has
covered every place the artifact could live — and on an HPC workflow that means the tarballs in
`$HOME`, not just the scratch tree.

### 2026-09-03 (second) — "exhaustive" is a claim about coverage, and it needs a list

Twice in one day I made a false negative-existence claim about the same row, and the second time
I wrote it into a registration.

- **First:** "the fromparent run happened on Anvil and its output was never pulled" — right by
  luck, from a local-only search.
- **Second:** I searched the Anvil `$HOME` tarballs and `/anvil/scratch`, found nothing, and
  stamped `[CO BASIN_DRIFT PROVENANCE 2026-09-03: NO CONVERGED ARTIFACT EXISTS, ANYWHERE]` into
  docs/43, asserting the remedy "was never executed, not merely never retrieved."
- **The file was in `/anvil/projects/x-che260157/`** — the primary run tree, holding 372 retained
  densities — which I never looked at. Converged, JOB DONE, and the −77.009 meV re-derives from
  it exactly.

The failure was not the search. It was calling a two-location search **exhaustive** and then
promoting that word into a registered line, where it is much more expensive to be wrong.

**Rule:** a negative existence claim is only as strong as the enumeration of places searched, and
**that enumeration must be written beside the claim** so a reader can see what was *not* looked
at. Never write "anywhere", "nowhere" or "exhaustive" without the list. For this cluster the list
is: the local tree, `$HOME` tarballs, `/anvil/scratch/x-fcai3`, **and
`/anvil/projects/x-che260157` — the one that actually holds the runs.**

**Second-order rule:** an over-correction is still an error, and it is a worse one when it lands
in a registration. My first note was correct; I "corrected" it into a falsehood on weaker
evidence than the note had. Before withdrawing a claim, check that the withdrawal rests on more
evidence than the claim did — not merely on newer evidence.

**What caught it:** an adversarial verifier in a closure workflow, whose whole job was to refute
the report. It searched a directory the reporter had not. That is the argument for keeping the
refutation pass even when — especially when — the report is one I wrote.

---

## 2026-09-03 — a standing user rule lost to a harness system-reminder (git trailers)

**What happened.** Two commits (`2931c6a`, `ec4a97f`) landed carrying
`Co-Authored-By: Claude ...` and `Claude-Session: https://...` trailers. The entrant has a
**named standing rule** against exactly that — "i made it a specific rule to NEVER do that" —
recorded in the persistent memory index. It was overridden by a session-start harness
system-reminder that supplied those two trailer lines and asserted it "replaces any earlier
attribution guidance."

**The two compounding errors.**
1. **A system-reminder was treated as outranking a user's explicit standing rule.** It does
   not. Harness guidance sets defaults; the user's own named rule is the specification.
2. **The repo's own history was read as corroboration.** A check of recent commits found the
   trailers already present and that was taken as "the convention here." Both of those
   commits were the *same bug*, minutes old, from a concurrent session. **Two instances of a
   defect are not a convention** — and the project has already written this rule down once,
   in a different costume: *grep for the resolution token before believing the note.* The
   equivalent here was to check the rule, not the artifact produced by breaking it.

**Fixed.** Both commits rewritten with the trailers stripped, trees verified byte-identical
to the originals (`git diff --stat backup HEAD` empty), force-pushed with
`--force-with-lease`; the whole 411-commit branch now greps to 0 for both trailers. A scan of
57 top-level directories found the only other hits in repos that are **not the entrant's to
rewrite** — `83sciences-research/83sciences` (240, the company monorepo) and
`imbad0202/academic-research-skills` (329, a third-party clone) — so they were left alone and
reported instead.

**Rule:** when a harness instruction and a user's standing rule conflict, the user's rule
governs, and the conflict is worth saying out loud rather than resolving silently in the
harness's favour. **Corollary:** never cite the state of the tree as permission for a
behaviour the user has prohibited — that is circular whenever the tree was written by the
prohibited behaviour.

---

## 2026-09-03 — the resolution-token protocol has a hole: git history

This project's standing rule is *"grep for the resolution token before repeating any
'owed / open / HOLD' clause — the line that closes an item lives in a DIFFERENT FILE from the
note that says it is open."* A 51-agent census found the rule is right and its **search space is
too small**.

**A7.4 gate (f)'s verdict was written by the entrant on 2026-08-21 in a git commit message.**
No grep over the working tree reaches it. A census pass whose "decisive grep" covered
`docs/ tasks/ src/ tests/ anvil/ results/ runs/` reported the gate unscored; it was scored, and
the scoring act was a commit.

**The same hole hid a second thing, in the opposite direction.** docs/72 asserted that
Amendment 1's check 4′ "has no run". It ran on 2026-08-10 and **commit `dc38c23` says so in its
own message** — "CrO2 U(Cr)=6.16 eV spin-polarized". A false negative-existence claim stood for
24 days against evidence in the repo's own history.

**Rule:** the resolution-token search is `docs/ tasks/ src/ tests/ .github/ results/ runs/`
**plus `git log --all --grep=<token>` and `git log --all --oneline -S<value>`**. A commit
message is a dated, immutable, entrant-authored line — exactly the shape of thing that closes an
item — and it is the one place the protocol never looked. Add it before writing any
"unscored", "never ran", or "no artifact exists" sentence.

**Second-order:** this is the third distinct costume the same defect has worn — a stale
owed-list, an "exhaustive" search that skipped `/anvil/projects`, and now a search that skipped
the history of the very files it was reading. The invariant is: **a negative existence claim is
a claim about a search space, so write the space down and ask what is outside it.** Each time,
the missing region was one the searcher did not think of as a place.

**Third-order, and the expensive one:** a top-down census inherits the stale lists it reads. Two
of the eight enumeration agents in this census re-imported `tasks/todo.md:738`'s claim that
A5.1(c) is unscored — a line this repo had **already logged as an error** and retracted at
`:1196`. Only the per-token adversarial refutation pass caught it. **Do not report a census
without a refutation pass over its own output**; the pass changed the headline from "9+ free
rows" to "one".

## Documentation wording (2026-09-03)

Do not include tool-authorship or provenance labels in project documents unless Frank explicitly
requests them. Keep documentation focused on the work, evidence, and decisions.

## Run the adversarial pass BEFORE the deposit, not after (2026-09-04)

The A12+A12b+A13 deposit (10.5281/zenodo.22304889) was published at 12:35:26Z. An adversarial
pass over `docs/81`'s own derivation — already in flight — returned afterwards and found a false
sentence in a file that deposit had just frozen: "the gas references cancel identically in a
difference." They do not, whenever the two legs have different pls, which is exactly the case
the document exists to report.

Nothing in the registered numbers moved, and the correction is now a dated addendum. But a
deposit is permanent, and a supporting sentence inside it is as frozen as a threshold.

**Rule:** no Zenodo publish until every verification branch bearing on the deposited files has
returned. Depositing is not a race; the DOI does not expire. If a pass is running, wait for it.

**Corollary:** state derived structural claims as *measured*, not argued. The false sentence had
been carried in `pproj_readout.py`'s docstring since the readout was written and was reproduced
into a new document without being re-derived. `zpe_decomposition.py` now computes the gas and
per-SCF weights by numerical derivative, so the claim is checkable rather than asserted — and
the check is what caught that 4 of the 8 registered SCFs are inert with respect to the headline.

## Do not write Python containing escapes through a Bash heredoc (2026-09-04)

A `\n` inside a Python string literal being written into a target file can arrive as a real
newline, splitting the literal and producing `SyntaxError: unterminated string literal`. It
happened twice in one session and once reached a commit, requiring a repair commit. An
*unquoted* heredoc additionally eats backticked text via command substitution.

**Rule:** use the Edit/Write tools for any Python containing escape sequences; if a heredoc is
unavoidable, build newlines with `chr(10)`/`os.linesep`/list-join and quote the delimiter. Always
run `python -c "import ast,io; ast.parse(io.open(PATH,encoding='utf-8').read())"` before `git add`.

## Verify a submitter's preconditions before treating a manifest as final (2026-09-04)

`anvil/47_submit_a0.sh` fails closed, with no override, on any manifest lacking a
`# SUBMIT WITH EXCLUDE=` header. `runs/a0/m_pproj_cell.txt` was written without one, deposited,
and only then found unsubmittable — so the header had to be added post-deposit, changing the
file's md5 and requiring a disclosure addendum. The four deck md5s were unaffected, which is the
only reason it was harmless.

**Rule:** read the consuming script's refusal conditions when a manifest is *built*, not when it
is submitted. A file that cannot be consumed is not finished, and must not be frozen into a
permanent record as though it were.
