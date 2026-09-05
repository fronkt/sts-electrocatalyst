# Pseudopotential provenance — the Ru second-family control (RU-PP)

Record of where the second Ru pseudopotential came from, what it is, and where it is
staged. The file itself is not in the repository (no pseudopotential is); this record
plus the two-ended md5 is what A8.5's "byte-identical (md5 verified on both ends)"
rule (docs/43:1608-1610) asks for. It has **no row** in
`anvil/pseudo_md5_preflight_2026-08-23.md`; adding a dated row there is part of
licensing, not of building.

## The file

| field | value |
|---|---|
| filename | `ru_pbe_v1.2.uspp.F.UPF` |
| family | GBRV v1.2 — the same family and version line as `Ir_pbe_v1.2.uspp.F.UPF` (Ir), and the same family as `cr_pbe_v1.5`, `mn_pbe_v1.5`, `ti_pbe_v1.4` (docs/45:35) |
| source URL | `https://www.physics.rutgers.edu/gbrv/ru_pbe_v1.2.uspp.F.UPF` (per-element link on `https://www.physics.rutgers.edu/gbrv/`) |
| downloaded | 2026-09-05, `curl -fsSL`, from this Windows checkout |
| size | 680598 bytes |
| md5 (local) | `7158a806dd851261a58e6920c40ebe78` |
| line endings | LF only (0 CR bytes); `file` reports ASCII text |
| library citation (from the GBRV page) | K.F. Garrity, J.W. Bennett, K.M. Rabe, D. Vanderbilt, Comput. Mater. Sci. 81, 446 (2014), 10.1016/j.commatsci.2013.08.053 |

Header facts, read from the file's `PP_INFO` / `PP_HEADER` blocks:

| field | value |
|---|---|
| generator | Vanderbilt code version 7 3 6, author kfg, generation date 3 2 2014 |
| type | `US` ultrasoft, scalar-relativistic, nonlinear core correction `T` |
| functional | `SLA PW PBE PBE` (PBE) |
| Z valence | 16.0 |
| pseudo-wavefunctions | 4S (occ 2), 4P (6), 4D (6), 5S (1), 5P (0) — 5 wavefunctions, 6 projectors |
| local potential cutoff radius | 1.40 |
| suggested cutoffs in header | `0.00000 0.00000` (none recorded in the file) |

## Against the pseudopotential it replaces

| | `Ru_ONCV_PBE-1.0.oncvpsp.upf` (banked) | `ru_pbe_v1.2.uspp.F.UPF` (control) |
|---|---|---|
| type | `NC`, scalar-relativistic (ONCVPSP 3.3.1, D. R. Hamann) | `US` |
| md5 | `be037bb81c227cfb9b1461a9f099f4bd` (`anvil/pseudo_md5_preflight_2026-08-23.md`; printed by every `runs/a0/main/Ru/*.out`) | `7158a806dd851261a58e6920c40ebe78` |
| valence electrons per Ru | 16 (slab `.out`: "number of electrons = 168.00" for 6 Ru + 12 O, `runs/a0/main/Ru/slab__u000.out`) | 16 (`Z valence 16.00000000000`) |
| projector manifolds seen by projwfc | s, p, s, d — four (`runs/a0/pproj6/Ru/*.pdos_atm#1(Ru)_wfc#1(s)` … `_wfc#4(d)`) | 4S, 4P, 4D, 5S, 5P — five |
| `HUBBARD` `U Ru-4d` manifold present | yes | yes (4D pseudo-wavefunction, occ 6) |

Consequences carried into docs/89: the electron count and the U manifold are unchanged,
so the decks need no `nbnd` or HUBBARD edit; the Löwdin projector basis is NOT the same
(four vs five manifolds), so Löwdin populations are not comparable across the pair and
are diagnostic only.

## Staging on Anvil

| step | result |
|---|---|
| target | `/anvil/projects/x-che260157/pseudo/ru_pbe_v1.2.uspp.F.UPF` (the `$PSEUDO_DIR` that `anvil/47_submit_a0.sh` exports) |
| copied | 2026-09-05 by `scp` from this checkout |
| md5 on Anvil | `7158a806dd851261a58e6920c40ebe78` — matches local |
| size on Anvil | 680598 bytes |
| `$PROJECT/pseudo` count | 13 files after staging (12 before: the twelve rows of the 2026-08-23 preflight table) |
| deck directory | `/anvil/projects/x-che260157/sts/runs/a0/ru_pp/Ru/` created, empty |

Before staging, `find $PROJECT -iname '*ru*.upf'` and `find $PROJECT -iname '*ru_pbe*'`
returned only `Ru_ONCV_PBE-1.0.oncvpsp.upf` (in `pseudo/`, `pseudo_src/`, and the
retained `dens/*.save` directories under `runs/a0/main/Ru`, `runs/a0/pproj6/Ru`,
`runs/a0/spin/Ru`); no GBRV Ru file existed on Anvil, in this checkout, or elsewhere
under `C:\Users\frank`.

Nothing was submitted. No job reads this file until a dated registration line exists
and the `NOT LICENSED` notice is lifted from `runs/a0/m_ru_pp.txt`.
