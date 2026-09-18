# Xu molecular references: deferred at the pseudopotential gate

Recorded 2026-09-18. The two approved H2/H2O jobs have **not been prepared or submitted**. Allocated cost is zero; the approved ceiling remains 64 core-hours (two jobs, at most 16 ranks and two hours each).

The Xu deposit identifies the required bytes unambiguously:

| Element | Required UPF | Required MD5 | Matching output headers |
| --- | --- | --- | ---: |
| O | `o_pbe_v1.01.uspp.F.UPF` | `2bcb18d16ea4b960afae9ec6d52f22d2` | 810 |
| H | `h_pbe_v1.uspp.F.UPF` | `3408e3ff4ec8b0a4e358431e7e038a48` | 780 |

See [the deposited-header identity evidence](../xu_pseudo_header_identity.json). The missing item is the original matching UPF content, not the identity requirement.

The [official GBRV distribution](https://www.physics.rutgers.edu/gbrv/) now links H v1.4 and O v1.2. Its [historical H generation directory](https://www.physics.rutgers.edu/gbrv/001-H/h_pbe_v1/) and [historical O generation directory](https://www.physics.rutgers.edu/gbrv/008-O/o_pbe_v1.01/) contain generation inputs. The official `Work_GBRV_v1.5.tar.gz` archive has 2,441 members and no UPF members. Original root UPF URLs returned HTML “Page Not Found” bodies despite HTTP 200. These bodies are saved with `.html` extensions as failure evidence; they are not pseudopotentials.

QE mirror attempts returned 404. Bounded Internet Archive CDX requests timed out. Two inspected public repository trees did not supply the historical files. These checks do not establish universal unavailability. [readiness.json](readiness.json) records the inspected URLs, responses, exact required identities, and evidence-file hashes; [retrieval/](retrieval/) preserves the primary-site pages, generation archive, and false-success bodies.

Under the [September 18 operating record](../../../docs/research/s2-operating-decisions-2026-09-18.md), this molecular-reference half is **DEFERRED**. Gas-independent Xu spans can proceed. No Xu floor margin may be presented as reference-complete, and no absolute Xu-metal overpotential is authorized.

To resume, obtain both original byte streams from an archived primary distribution or a retained original copy, require the MD5 matches above, and additionally pin SHA256, UPF metadata and acquisition provenance. Then prepare the approved two-deck manifest and supervised bounded launch. Substituting current GBRV/SSSP potentials or regenerating an unverified historical equivalent does not clear this gate. No compute or automatic retry was started during retrieval.
