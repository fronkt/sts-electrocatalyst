# Blocking findings — 1B-hpx

Verbatim from the 2026-08-09 adversarial review (6 verifiers, 31 blocking,
all six verdicts FIX_FIRST). Numbering is global across all three lanes.

## [9] src/dft/queue_hp.sh:45
**lens:** Computational-catalysis referee: does this deck measure what it claims to measur

**Problem.** Every hp.x rung of an arm shares one prefix and one outdir (all 8 atomic-arm lines use prefix='tio2_atomic', outdir='./tmp_tio2_atomic'; all 4 crslab_sym lines share theirs), and queue_hp.sh defaults NCONC=2 with no per-(dir,prefix) lock on the hp stage -- the mkdir lock at lines 55-81 guards only the SCF. I ran hp.x and listed its scratch: it writes <outdir>/HP/<prefix>.dvwfc1..12, .dwfc1..12, .hubnoS1..12 and .wfc1..N, named from prefix + MPI rank only, with no run identifier. Two concurrent rungs at the same NP open byte-identical paths.

**Why it ruins the result.** The manifests place same-prefix jobs adjacently (m_hp_tio2.txt lines 1-8, 9-16; m_hp_costmodel.txt lines 1-4, 5-6), so NCONC=2 -- the script's own default -- guarantees two hp.x jobs write the same Sternheimer buffers. The failure mode is not a crash, it is a corrupted chi and therefore a U that looks fine and is wrong. That is the exact class of number nobody can interpret after the fact, and the gate it feeds is a GO/NO-GO.

**Proposed fix.** Either (a) hard-force serialisation: wrap the hp.x invocation in the same mkdir test-and-set keyed on "$dir/.hp_${prefix}.lock", or (b) give each rung its own outdir by copying <prefix>.save (3.2 MB charge density + xml here; cheap), or at minimum (c) refuse to run when two manifest lines share a (dir, prefix) and NCONC>1, and state NCONC=1 in both manifest headers.

---

## [10] runs/hp_costmodel/cost_model.json:1
**lens:** Computational-catalysis referee: does this deck measure what it claims to measur

**Problem.** The whole cost model is anchored on nq=2x2x2, which is the one mesh in which every q point satisfies q = -q + G. hp.x therefore gets the maximum possible symmetry reduction at every measured point. I measured the actual k-counts of hp.x's internal NSCF on the shipped TiO2 ground state: 65 k at Gamma, 130 k at q=b3/2 (the builder's basis), 208 k at q=b3/3 (nq 3x3x3, q#2), and 576 k at q=(1/4,-1/2,0.388) (nq 4x4x4, q#14) -- the full unreduced 6x6x8 grid doubled for k and k+q. Cost per (atom,q) tracks that count (measured 12.5 s/LR-iteration at 208 k vs the builder's 8.0 s at 130 k, ratio 1.56 vs a k ratio of 1.60), but the model applies a flat 0.308 core-h to all 102 (atom,q).

**Why it ruins the result.** Block 1B exists to produce 'an exact cost model before spending anything' (plan, Week 1). Using the k-count as the cost proxy, the shipped TiO2 batch is ~90 core-h, not 32 -- roughly 2.5-3x low, and the q444 rung (20 of the 51 (atom,q) per arm) is low by ~4.4x on its own. The same flat per-(atom,q) is then carried into the 2C projection (0.92 core-h at nq 3x3x3) and into every slab row, so the one number 1B is supposed to deliver repeats the 2.4x/2.5x/3.5x pattern the builder quoted from tasks/lessons.md two paragraphs earlier. The batch still fits the ~1 box-day allowance at ~4 box-hours, so this does not stop the launch -- it invalidates the deliverable.

**Proposed fix.** Re-cost per (atom,q) as a function of the measured NSCF k-count, not as a constant: hp.x prints 'number of k points=' for every q, so scale 0.308 core-h by n_k(q)/97.5. Note explicitly in cost_model.json that nq=2x2x2 is the cheapest possible mesh because all 6 of its q are time-reversal-invariant momenta, and that Gamma and zone-boundary q are not representative of a general q.

---

## [11] runs/hp_costmodel/crslab_sym__hp_1atomq.in:8
**lens:** Computational-catalysis referee: does this deck measure what it claims to measur

**Problem.** The slab timing deck -- the single measurement the builder correctly identifies as the thing block 3Y must not be committed without -- runs start_q=1, last_q=1, and q#1 of the 3x2x1 mesh is Gamma. Gamma is the cheapest point by construction: no k+q doubling and the full point group survives. The same deck for the nosym arm has the same defect.

**Why it ruins the result.** The builder ran BOTH q#1 and q#2 on TiO2 and wrote 'costing the model off q#1 alone would have understated it', then shipped Gamma-only for the slab. On TiO2 the Gamma-to-general-q k-count ratio I measured is 65 -> 576, i.e. up to 8.9x. The 3Y decision (191 to 4121 core-h per metal, the difference between 'affordable' and '30 days on 12 boxes') would be anchored on the one q that cannot show the cost.

**Proposed fix.** Add crslab_sym__hp_1atomq_q2.in and crslab_nosym__hp_1atomq_q2.in with start_q=2, last_q=2 (q#2 of the 3x2x1 mesh is a general in-plane q), add both to m_hp_costmodel.txt, and cost 3Y off the non-Gamma point. Costs one extra linear-response solve on a ground state that has to be computed anyway.

---

## [12] docs/43-prereg-week1-factorial.md:252
**lens:** Computational-catalysis referee: does this deck measure what it claims to measur

**Problem.** docs/43 section 4 (P15) ALREADY registers this gate, at 13:49 today, before the builder ran. It registers external window U(Ti-3d, atomic) in [3.0, 7.0] eV and four internal checks that ALL must pass: q-mesh dU < 0.2 eV, |chi_ij - chi_ji|/max|chi_ij| <= 0.05, perturbation-amplitude independence, symmetry-equivalent atoms within 0.05 eV. The builder's Part 2 text widens the external window to [2.0, 8.0] eV, deletes the amplitude criterion, tightens the chi-symmetry tolerance 50x to 1e-3, and is headed 'Registered 2026-08-09, before any hp.x production run' with no reference to the existing registration.

**Why it ruins the result.** Pasted into docs/43 as written, the document will contain two mutually inconsistent registrations of the same gate, one of which has a wider acceptance window. For an STS entry whose stated #1 and #2 disqualification risks are citation and disclosure integrity, a silently widened pre-registered acceptance window is the single most damaging artifact a judge can find. It also makes the verdict uninterpretable: a U of 2.4 eV passes one registration and fails the other.

**Proposed fix.** Publish it as a dated AMENDMENT to P15, not a fresh registration: state the old window and the new one side by side with the reason, keep [3.0, 7.0] unless there is a physics reason to widen (there is none given -- 'catch a broken calculation' is satisfied by the narrower window too), and record the amplitude-independence deletion as a withdrawal with its justification (hp.x is DFPT; no amplitude keyword exists in the binary's input-variable list -- that part is correct and worth stating).

---

## [13] src/dft/build_hp_validation.py:345
**lens:** Computational-catalysis referee: does this deck measure what it claims to measur

**Problem.** Criterion I2b ('MATRIX SYMMETRY, PASS iff |chi_ij - chi_ji| <= 1e-3 * max|chi|', declared a HARD GATE whose failure triggers NO-GO) is very likely an identity. hp.x symmetrises the response occupation matrices and reconstructs the unperturbed rows of chi rather than computing them. Evidence from the shipped binary: compiled-in source paths HP/src/hp_symdnsq.f90 and HP/src/hp_rotate_dnsq.f90; runtime strings 'RESPONSE OCCUPATION MATRICES (SYMMETRIZED):', 'Missing chi element for: na= nb= dist=', 'Reconstruction problem: some chi were not found', 'Found a new Hubbard_V element from the symmetry analysis!'.

**Why it ruins the result.** This is exactly the trap the builder correctly diagnosed for I2 at find_atpert=1 ('hp.x RECONSTRUCTS the other by symmetry, which makes this an identity, not a test') and then walked into one criterion later. If chi is symmetrised before printing, a pass measures nothing. If it is not, 1e-3 * max|chi| sits only one to two orders of magnitude above conv_thr_chi = 1e-5, so ordinary incomplete convergence can trip it -- and a trip triggers NO-GO on the entire S2 contribution. A gate that cannot fail, or that fails on noise, is worse than no gate.

**Proposed fix.** Before registering it as a hard gate, verify on one completed run whether hp.x prints chi pre- or post-symmetrisation (iverbosity=2 output, compare the printed matrix against its own transpose). If post-symmetrisation, demote I2b to a reported diagnostic and rely on I2 (find_atpert=4, two independently perturbed Ti) as the real reproducibility test. If pre-symmetrisation, keep the registered 0.05 relative tolerance from docs/43 P15, not 1e-3.

---

## [14] runs/hp_tio2/m_hp_tio2.txt:5
**lens:** Computational-catalysis referee: does this deck measure what it claims to measur

**Problem.** Criterion I5 ('n_pert(find_atpert=1) == n_pert(find_atpert=3) == 1 on bulk TiO2') has no deck. grep over every shipped .in in runs/hp_tio2 and runs/hp_costmodel returns find_atpert = 1 (10 decks) and find_atpert = 4 (2 decks). No find_atpert=3 input exists anywhere in the batch.

**Why it ruins the result.** A pre-registered gate that the shipped manifest cannot evaluate. The batch will be scored against a criterion for which no output was produced, which either silently drops the gate or invites a post-hoc extra run -- both of which defeat the point of registering it.

**Proposed fix.** Add hp_npert3__atomic.in / hp_npert3__ortho.in (identical to hp_npert__*.in with find_atpert = 3) and two manifest lines. These are the ~3 s counting decks; the cost is zero.

---

## [15] runs/hp_tio2/scf__atomic.in:18
**lens:** Computational-catalysis referee: does this deck measure what it claims to measur

**Problem.** Nothing in block 1B exercises the code path the campaign actually needs. The validation target is nspin = 1, occupations = 'fixed', a d0 closed-shell insulator, 6-atom bulk, empty Hubbard manifold. Production (2C, 3Y) is nspin = 2, occupations = 'smearing' mv/0.01, metallic, magnetic, partially-filled 3d. That is six co-varying differences, and the builder's own headline finding is that these are not the same branch of hp.x -- it hard-stops on a gapped system presented with smearing. The only magnetic evidence offered is an FeO2 run whose underlying SCF hit 'convergence NOT achieved after 200 iterations', so it proves a code path reached the solver and nothing about whether the response converges.

**Why it ruins the result.** The gate cannot fail for the reason that actually threatens S2 (risk R2: 'hp.x never converges here'). A GO on TiO2 licenses block 2C -- seven magnetic, metallic bulk rutiles, ~110-330 core-h -- on a branch that has never produced a converged U in this campaign. docs/43 already firewalls the SLAB ('a successful bulk validation does not license a slab U'), but it does not firewall magnetic BULK, which is precisely what 2C is.

**Proposed fix.** Add one bulk rutile CrO2 arm to the 1B batch: gen_rutile already has the entry (a=4.421, c=2.916, u=0.3023, mag=0.6), nspin=2, occupations='smearing' mv/0.01, HUBBARD (atomic) U Cr-3d 1.d-8, k 6x6x8, nq 2x2x2, find_atpert=1. That is 6 (atom,q); at the measured 0.308 core-h scaled ~2x for nspin=2 it is ~4 core-h, roughly 10 minutes of the box. Require it to print a finite U with zero 'Convergence has not been reached' lines before GO. Without it, restrict the declared consequence of GO to 'hp.x validates on a closed-shell bulk insulator' and gate 2C separately.

---

## [16] src/dft/build_hp_validation.py:306
**lens:** QE/hp.x run mechanics: will these decks execute, and will the output files carry

**Problem.** Every hp.x rung for a given projector shares one prefix and one outdir, and hp.x names its results by prefix ALONE. MEASURED on the box: the computed U appears NOWHERE in hp.x stdout (`grep -ac '4.1543' hp_q111.out` = 0; `grep -ac 'Hubbard U parameters' hp_q222.out` = 0). U, chi0, chi, chi^-1 and the Hubbard matrix exist only in `<cwd>/<prefix>.Hubbard_parameters.dat` and `<outdir>/HP/<prefix>.chi.dat` + `.chi.pert_N.dat`. I ran nq=1x1x1 (U = 4.1543 eV), then nq=2x2x2 in the same outdir: the .dat was overwritten in place with 4.1786 and chi.dat grew 208 -> 1440 bytes. The manifest has 4 U-producing atomic rungs (q222, q333, q444, q333_allatoms) + 4 ortho rungs, all writing the same three filenames per projector.

**Why it ruins the result.** 8 U determinations are computed and 2 survive, with no record of which q-mesh produced the survivor. Criterion I1 (|U(4x4x4) - U(3x3x3)| <= 0.10 eV), I2 (two-site reproducibility) and I2b (chi_ij vs chi_ji) are all scored off numbers that no longer exist when the batch ends. The .out files retain only the INPUT U (`U(Ti-3d) = 0.0000`, i.e. the 1.d-8 seed) — a reader of the archive would see a batch that ran clean and produced nothing. ~60-80 core-h burned for one uninterpretable number per projector.

**Proposed fix.** In queue_hp.sh run_one, immediately after the hp.x call and before the next job: `for f in *.Hubbard_parameters.dat; do [ -e "$f" ] && mv "$f" "${hp}.Hubbard_parameters.dat"; done` and `cp -a <outdir>/HP/*.chi*.dat` into `${hp}.chi.dat` / `${hp}.chi.pert_*.dat`. Key every artifact on $hp (the deck basename, which already encodes the q-mesh), not on $prefix. Also correct the docstring at build_hp_validation.py:140-146 — iverbosity=2 does not put chi0/chi in the output file, it puts them in the .dat.

---

## [17] src/dft/queue_hp.sh:104
**lens:** QE/hp.x run mechanics: will these decks execute, and will the output files carry

**Problem.** `hasu=$(grep -ac 'Hubbard U parameters:' "${hp}.out")`. That exact string exists — but only inside `<prefix>.Hubbard_parameters.dat`, never in hp.x stdout. MEASURED: 0 on a run that produced U = 4.1543 eV. The `udat` fallback on line 106 (`ls -1 *.Hubbard_parameters.dat | wc -l`) is a directory-wide count, so once ANY job in runs/hp_tio2 has written a .dat, every later job — including the ~3 s determine_*_only jobs that compute nothing — reports UDAT=1.

**Why it ruins the result.** The script's own header declares HAS_U 'the only defensible gate' after four paragraphs about JOB DONE being worthless. It is dead: HAS_U=0 on all 22 jobs whether they succeeded or failed, and UDAT=1 on all of them after the first. A fully-successful batch and a fully-failed batch emit byte-identical log signatures, so the campaign's oldest lesson is re-committed in the file written to prevent it.

**Proposed fix.** Gate on the artifact, not on stdout: `hasu=$([ -s "${hp}.Hubbard_parameters.dat" ] && grep -ac 'Hubbard U parameters:' "${hp}.Hubbard_parameters.dat" || echo 0)` after the per-job rename above. `NOTCONV`/`SMOOTHSTOP`/`GAPSTOP` were verified against the binary's format strings and are correct; `NQ` (`\( +[0-9]+ q-points \)`) matches real output `(  6 q-points )`; `NPERT` is fine — hp.x prints `Atom which will be perturbed:` (no count) when n_pert=1, so the `${npert:-1}` default is right, and the plural form `List of  6 atoms which will be perturbed` matches the regex with awk $3 = 6.

---

## [18] src/dft/queue_hp.sh:45
**lens:** QE/hp.x run mechanics: will these decks execute, and will the output files carry

**Problem.** `NCONC=${3:-2}` plus a manifest whose first 8 lines all name scf__atomic / prefix tio2_atomic / outdir ./tmp_tio2_atomic. hp.x writes per-rank buffers into the shared outdir: I observed `tio2_atomic.wfc1..8` in outdir root and `HP/tio2_atomic.mixd1..8`, `HP/tio2_atomic.hubnoS1..8`, `HP/*.dns.pert_1.q_1.dat`, `HP/*.chi.pert_1.dat` — all named by prefix and rank index only. MEASURED: two hp.x runs launched simultaneously against the same prefix+outdir, run A finished JOB DONE, run B died with 12 error lines and `Exit code: 2`.

**Why it ruins the result.** With the shipped defaults, jobs 1+2, 3+4, 5+6, 7+8 of the TiO2 manifest run concurrently in one outdir. Best case one of each pair crashes and the queue logs rc!=0; worst case both survive having read each other's half-written .wfcN/.mixdN buffers and emit a plausible U that is arithmetic on two different perturbations. Combined with the artifact-overwrite finding above, the surviving .dat is whichever racer wrote last. (Sequential reuse of one outdir is SAFE — I verified q222 after q111 recomputed all 6 q from scratch and did not reuse the stale dns.pert_1.q_1.dat.)

**Proposed fix.** Serialise on the (dir, prefix) pair, not globally: hold the existing `.scf_<scf>.lock` directory for the whole hp.x call instead of releasing it after the SCF, or simply document and enforce NCONC=1. Concurrency across DIFFERENT prefixes (atomic vs ortho, sym vs nosym) is safe and is where the parallelism should come from.

---

## [19] runs/hp_costmodel/m_hp_costmodel.txt:7
**lens:** QE/hp.x run mechanics: will these decks execute, and will the output files carry

**Problem.** The header says 'nk=6 => NP must be 6, 12 or 18 (18 fits 23.04 usable cores)' but names no NCONC, and queue_hp.sh defaults to 2. NP=18 x NCONC=2 = 36 MPI ranks against a 2304000/100000 cgroup quota (23.04 cores); even the bare default NP=12 x NCONC=2 = 24 ranks is over. Worse, with NCONC=2 the queue reaches line 4 (`crslab_sym__hp_1atomq`) and line 5 (which triggers the ~1 h nosym production SCF) at the same time.

**Why it ruins the result.** `crslab_sym__hp_1atomq` is, by the builder's own argument, THE measurement that decides whether block 3Y is affordable — and it would be timed while a second job competes for a throttled cgroup. A wall-clock taken under contention plus OpenMPI spin-wait oversubscription is not a cost basis; it is the mechanism behind the 2.4x/2.5x/3.5x mis-costings in lessons.md 2026-08-05. Roughly 65-200 core-h of slab compute spent to produce a number that cannot be extrapolated.

**Proposed fix.** Run the timing decks alone: `bash queue_hp.sh m_hp_costmodel.txt 18 1`. Add to both manifest headers a hard line 'NP x NCONC must be <= 23 (cgroup 23.04 cores); the *_hp_1atomq lines REQUIRE NCONC=1'. For TiO2, NP=20 NCONC=1 keeps NP an exact multiple of nk=4 and stays inside the quota.

---

## [20] runs/hp_tio2/m_hp_tio2.txt:5
**lens:** QE/hp.x run mechanics: will these decks execute, and will the output files carry

**Problem.** `/workspace/sts/runs` on box 47025043 currently contains exactly one entry: `probe`. There is no `hp_tio2`, no `hp_costmodel`, and no `Cr_slab`. queue_hp.sh:86 does `cd "$dir" || { echo "NODIR $d"; return 2; }`.

**Why it ruins the result.** Launching as-is writes 22 `NODIR` lines and then `QUEUE_HP_ALL_DONE` to /workspace/queue_hp.log. The terminal line of the log is the success banner on a queue that did nothing — the same shape of false-clean signal as JOB DONE.

**Proposed fix.** rsync runs/hp_tio2/ and runs/hp_costmodel/ to /workspace/sts/runs/ before launch and verify `ls /workspace/sts/runs`. Add a pre-flight to queue_hp.sh: read the manifest once, `[ -d "$RUNS/$d" ] && [ -f "$RUNS/$d/$hp.in" ] && [ -f "$RUNS/$d/$scf.in" ]` for every line, and exit non-zero before launching anything if any check fails.

---

