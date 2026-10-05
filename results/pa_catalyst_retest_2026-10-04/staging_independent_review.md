# Independent staging and Anvil preflight review

Decision: GO_SUBMISSION_PREFLIGHT_READINESS_ONLY

Scope: the recorded staging/preflight of exact commit c5b33c28bb09324d7decf5c2bb5f6100a877a366. This is technical readiness to request submission approval. No scientific trial result or user submission authorization is granted. The recorded staging approval expressly sets submission_approved=false. This reviewer inspected local files and receipts and computed hashes only, without any process, test, Anvil contact, QE invocation or submission.

## Exact snapshot and reviewed pins

remote_stage.json SHA-256 0177ca384b0c80adb87f057c92336522bd50422f7fb6d3dcce01adb73d6461a2 records returncode=0 and successful=true. The published commit, remote publication head, detached Anvil checkout, Anvil HEAD, materialization commit and outer staging receipt all agree on c5b33c28bb09324d7decf5c2bb5f6100a877a366. All 206 unique staged path/size/SHA-256 records exactly equal the published 203 blob pins plus the three additional registered input pins. I independently read all 206 locally materialized files and confirmed the same published sizes and hashes: zero mismatches.

The immutable materialization receipt uses git-cat-file-batch-exact-blobs and retains the exact c5b33c2 package while the live task log advances. Its source checks each committed blob against publication pins before invoking the unchanged reviewed staging program. The prior Git-archive newline refusal is retained in staging_materialization_refusal.json; its document blob agrees with publication, archive CRLF conversion explains the mismatch, and the refusal records no Anvil contact. No reviewed source was rewritten to work around the refusal.

All 26 final code pins agree across offline_release_lf.json, independent_launch_review_final_pins.json, publication, remote stage and current local files. Final receipt SHA-256 dbeabe311d10e758567d9177db5d93d93ae9be0e53f6fd6097b3d04b047c2e12 and the final memo/sidecar hashes remain exactly bound by publication_final.json. staging_independent_review.json retains the exact inspected receipt hashes and full stage-pin-array digest.

## Remote preflight and live inputs

The staged controller returned PREFLIGHT_PASS with returncode=0 under /apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3. Remote bash -n also passed. All 17 source/runtime/UPF/seed/dependency pins recorded by controller preflight match the reviewed spec: source deck and source review; pw.x and mpirun; four code/wrapper dependencies; five UPFs; and the four historical initialization files, including their registered seed sizes. The historical initialization is correctly reported as not a full continuity checkpoint.

The real-control replay is true with three evaluated states, global SCF cycles [1,2,3], saved optimizer counters [3,3,0], staged adapter path and XML settings identity 3bd17094ff7919c4d831d8725d6297eac21858be16143dae686883c27ea232f0. Both controller and outer-stage replay summaries agree exactly with all registered expected values. The compressed replay fixtures are among the 206 verified pins. This is a replay of retained output; no new QE calculation occurred.

## Resource observations and remaining gate

The successful remote balance query recorded che260157 CPU balance 36,775.4 SU, exceeding the required 2,048-SU ceiling. The invoking user queue was empty; wholenode was UP with MaxCPUsPerNode=128. Quota recorded home 0.2%, scratch 0.0%, project storage 44.3% (2.2/5.0TB), project files 8.0% (83.4K/1.0M). All ten recorded staging commands completed with returncode=0. The staging program verifies no trial_results or replay scratch remains. Staging submitted zero jobs and invoked no QE, with zero SU of scheduler compute.

No blocking finding in the recorded evidence. Balance, queue and allocation remain time-dependent and are rechecked by the reviewed held-submission/release gates after explicit submission approval. The permitted next trial remains one job, estimated 275–543 SU, hard ceiling 2,048 SU / 16 hours, with no automatic retry and production_accepted=false.
