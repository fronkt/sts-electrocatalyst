# `.github/ci` — the S1 control machinery

Three scripts and three data files implementing the A9.2 controls and the A9.1
disjointness assertion. See `docs/57-s1-ci-handoff-2026-08-27.md` for the full
hand-off; this is the map.

| file | what it is |
|---|---|
| `check_disjoint.py` | the :1840 assertion: AI-use log file list INTERSECT core path list = {} |
| `run_controls.py`   | the A9.2 status face — every gate, one commit-stamped surface |
| `run_oc20.py`       | the A9.2.1 OC20 control; both registered transports, neither defaulted |
| `core_paths.txt`    | the five-entry core path list, transcribed from :1840 |
| `populations.txt`   | the 9 nosym-absent + 11 nosym-present production runs, from :1864 |
| `silentgate-invocation.toml` | **blank by design** — the entrant declares how CI calls the CLI |

## The boundary these files sit on

`silentgate/readers/*`, `census.py`, `classify.py`, `direction.py` and `cli.py`
are core: "written and committed only by the entrant" (docs/43:1840). AI may
write "tests and fixtures, the CI workflow, and review comments".

So **nothing here parses a pw.x output.** These scripts move bytes, check hashes,
read the AI-use log, invoke the entrant's CLI and compare its JSON against
thresholds transcribed from docs/43. A helper that parsed a force block would be
a reader, and writing one under any name — helper, checker, shim — would be
authoring core.

The same rule is why `silentgate-invocation.toml` is empty. Hard-coding a command
line and a JSON shape would design the CLI's interface, and `cli.py` is core. The
entrant declares the interface; these scripts supply the mechanism.

## Expect red until the core exists

A9.2 is a gate, not a caveat (:1848). A gate whose instrument has not been
written is not green, and `run_controls.py` says which of the two it is — core
absent, or a control that regressed — so a red run is never ambiguous.
