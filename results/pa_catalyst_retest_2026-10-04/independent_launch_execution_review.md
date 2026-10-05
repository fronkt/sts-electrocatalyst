# Independent one-trial launch execution review

Decision: PASS_ONE_AUTHORIZED_TRIAL_LAUNCH_ONLY

I independently inspected the immutable local approval, intent, submission, checked-held-validation, release, first-observation and launch-summary receipts. The recorded separate approval covers one held submission, validation, release of that same job once and read-only follow-through. This reviewer performed only file reads and hashes, without processes, tests, SSH, Anvil contact, job mutation or QE.

## Exact reviewed launch

All 26 reviewed code pins still match current disk bytes. Submission approval, both remote HEAD checks and launch summary bind implementation commit c5b33c28bb09324d7decf5c2bb5f6100a877a366 and spec SHA-256 4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435. The approval retains one job attempt, 275–543-SU estimate, 2,048-SU/57,600-second ceiling and automatic_retry=false. Its staging receipt pin matches the independently reviewed staging receipt.

The submission receipt records exactly one `sbatch --hold --parsable --no-requeue` with the pinned spec environment, returning job 21075231. The queue was empty immediately before it. Three independent held-shape observations agree on that same job: PENDING/JobHeldUser, priority 0, NumNodes=1-1 (one-node request range), 128 CPUs/tasks, one CPU per task, ReqTRES cpu=128,mem=200G,node=1,billing=128, 16:00:00, che260157/wholenode, Dependency=(null), Requeue=0 and Restarts=0, exact wrapper and checkout. Both local submission and release intents are retained. The hash-bound reviewed scripts exclusively claim local and remote intent files before their one mutating call; the release receipt confirms its remote intent was claimed.

Submission and release each executed a fresh pinned-controller PREFLIGHT under remote Python3.9.5 and received PREFLIGHT_PASS. All 17 live input pins and real-control replay evidence exactly match the staged preflight. CPU balance was 36,775.4 SU in both checks. Before release, the queue contained only 21075231/JobHeldUser/128. The release receipt records exactly one successful `scontrol release 21075231`, with no sbatch or replacement job; its post-release observation is PENDING/Reason=None with the same requested shape and no dependency/requeue. Every recorded launch command and receipt returned 0.

## Status and scientific limits

The immutable first observation at 2026-10-05T02:40:14.753245+00:00 is PENDING, Reason=None, AllocTRES=(null), sacct allocated CPUs=0 and CPUTimeRAW=0, with no trial arms yet. It does not prove a running allocation or a scientific trial result. The launch summary correctly reports PENDING_TRIAL_OUTCOME and production_accepted=false, and leaves actual allocation proof, terminal accounting/actual SU, immutable raw mirror and scientific readout pending. Its seven immutable receipt hashes match the inspected files. Mutable watch status is excluded from lasting evidence pins.

No blocking finding in the authorized launch sequence. The approved single diagnostic trial is released and remains subject to the reviewed running-allocation checks, one-job 2,048-SU/16-hour cap and no automatic retries. Scientific interpretation awaits the terminal trial evidence.

## Immutable receipt pins

| Receipt | SHA-256 |
|---|---|
| submission_approval.json | 099482608caae6a344adced5b456ab96518172b9f4215678fcfc0e2b25c724d4 |
| submission_intent.json | dcb92aec42bb665e90971a802268beb6dfed64adec823a54b74d88f0c75fd25a |
| submission.json | 6065b0226d69c45601d3fcddb8a7bcadc4a03263668211e32f22ea045c109207 |
| held_validation_checked.json | 5215777e619ee5d47af0970799079cea2235453319859e6d7c562a75feb24a0c |
| release_intent.json | 5ddfa5290b8fb037c43ed757e0b0442996f671399461062ffe4f0aa5358895b1 |
| release.json | 24c59113b16c0de5ae8b673d98bbf63ac5e8466514798ff206bb47e6f203bc5c |
| launch_first_observation.json | 14373d257a014f0e4b5acb628f86fb28a7eb76691d3cea240617f5afa4bebc68 |
| launch_summary.json | b462954411707fad57d44538e83bbd58d6aa34663ec941f1c76b6532cde9b606 |

## Launch receipt publication helper

I also inspected bank_launch_receipts.py, SHA-256 451448208d0a82f6cf798005abb86c967520f92beb6a3b2b0b3804315aaf9925, without executing it. Its 22 explicit paths contain launch receipts, the immutable first observation, review artifacts, launch helper, task log and desktop job/log/status evidence. Mutable watch observations/status/log are excluded. The helper requires the exact PASS_ONE_AUTHORIZED_TRIAL_LAUNCH_ONLY decision, checks all eight audit-bound immutable receipt pins, the launch receipt pins and all 26 reviewed code pins, requires the expected branch/base HEAD and empty prior index, restricts tracked changes to the task log, verifies the staged path set and staged bytes, checks whitespace, then commits/pushes and checks the remote head. The final clean tracked/index checks preserve the reviewed code. It has no scheduler or QE call. No blocking finding in this file-only publication review.
