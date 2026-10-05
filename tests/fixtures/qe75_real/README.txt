Real QE 7.5 output fixtures for tests/test_pa_qe_adapter_v2_real.py.

Every file is a deterministic gzip (mtime 0) copy of an original that is left in place;
manifest.json holds the original path, byte length and SHA-256 of the uncompressed bytes.

control/      the control call of Slurm job 21034683 (72-atom Hubbard relax, 128 MPI, clean stop
              after three SCF evaluations): deck, stdout, stderr, process receipt, XML, .bfgs,
              and the five pinned UPFs it consumed.
pproj6/       19 real calculation='scf' Hubbard (ortho-atomic) XML files with their decks and
              logs (runs/a0/pproj6; untracked in the repository because of the **/dens/ ignore).
fresh_logs/   two real 72-atom 128-rank calculation='scf' logs from the September checked run
              (one converged, one stalled at SCF iteration 127), stdout and stderr merged.
tiny_h2/      four arms of the real one-process H2 restart probe (QE 7.5, serial): the clean-stop
              candidate, the continuous run, the resumed run (restart_mode='restart') and the
              from-scratch negative control; tracked originals under results/s2_2026-09-25/.
