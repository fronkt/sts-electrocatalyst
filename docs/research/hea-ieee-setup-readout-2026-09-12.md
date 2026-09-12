# HEA setup-only diagnostic readout — 2026-09-12

Diagnostic 20586171_1 completed at 01:46:18 UTC on September 12 with scheduler exit 0:0. Its 90-second allocation on 128 CPUs cost 3.200 core-hours against the 21.333 core-hour ceiling. The independently reconstructed outcome is **SETUP_ONLY_CLEAN**, with no IEEE flags in stdout, launcher stderr, or any of the 128 rank stderr files. It remains **DIAGNOSTIC_ONLY**; no earlier rejected endpoint is reclassified.

The retrieval receipt covers 138 files, each checked against its remote SHA-256 and byte count. The 128 rank files and launcher stderr are present and empty. Reassembling the raw streams reproduces the exact 20,081-byte combined output and the stored rank audit. The frozen input and runtime input agree byte for byte and differ from the original smearing deck only in nstep=0 and max_seconds=480. The batch log agrees with the diagnostic JSON and terminal accounting.

The positive branch evidence consists of a single QE 7.5 invocation, config-init output and JOB DONE, plus XML exit status 255, nstep=0, max_seconds=480, 128 ranks and eight k-point pools. No SCF iterations, computed endpoint energy, band structure or forces are present. QE reports 0.95 seconds of program wall time; scheduler allocation time also includes preparation and verification. Empty timing headings that name later stages are not evidence that those stages ran.

A fresh read-only evaluation on Anvil rehashed the accepted source, live pseudopotentials and retained clone and reproduced the original diagnostic JSON exactly. The retained clone contains 27 files totaling 15,813,962,059 bytes. All non-XML clone members match the source inventory; the XML records the expected setup-only branch. Six live pseudopotentials match their stored SHA-256 and sizes, and all seven printed species/path/MD5 entries agree, including the two oxygen species. The large clone remains on Anvil under the existing retention policy; the setup XML is also local.

The diagnostic did not reproduce the invalid flag in this early setup/shutdown execution. It does not demonstrate that checkpoint density or wavefunctions were read. In [QE 7.5 run_pwscf](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/run_pwscf.f90#L148-L159), the nstep=0 branch returns before init_run and the electronic loop. Consequently, checkpoint initialization, electronic iterations, force evaluation, and path-dependent shutdown remain candidate locations for the earlier invalid operation. A single clean execution also cannot exclude run-to-run variability. The original smearing failures remain rejected.

This completes the bounded setup diagnostic. Any further exception-localization experiment should distinguish the remaining execution stages while retaining full rank capture and the original scientific acceptance rule. This readout alone does not justify a larger candidate relaxation campaign; that decision still depends on the complete census and rank-resolution analysis. No additional Anvil job was submitted during this recovery.

## Evidence

Terminal accounting and queue are in [status_2026-09-12.json](../../results/hea_ieee_init_2026-09-11/status_2026-09-12.json). The [readout directory](../../results/hea_ieee_init_2026-09-11/readout_2026-09-12/) contains transfers.json, local_reconstruction.json, remote_revalidation.json, the scheduler log and independent_review.json. Raw streams and XML are under runs/hea/ieee_init_2026-09-11/.

The combined output SHA-256 is d8c105e179c74edff0c5bafbf2ab71981d2e812dd2365d4f1d34ddd720b98b18. The runtime deck SHA-256 is 5383a3a00ab75457aab9a27f22e7d9d376669399fb642b1a94bb9573d1705aff. The setup XML SHA-256 is e38a10e5751b79513ad442d54baf35c3b0ade0dd7e03053f4cb4dfaf77c08dd4. Byte hashes are exact, without line-ending normalization.
