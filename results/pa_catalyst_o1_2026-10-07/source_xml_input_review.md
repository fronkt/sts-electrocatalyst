# Source review: QE 7.5 XML `<input>` as written, for the corrected one-boundary re-test (2026-10-04)

Scope. This review is the spec's `source_review` pin for `launch_spec.json` (schema `pa-catalyst-retest-v1`). It covers only what the
trial of 2026-10-03 did not: how QE 7.5 writes the `<input>` element that `pa_qe_adapter_v2.py` compares with the arm's own deck.
The stop-observer, optimizer-file, cleanup and EXIT-file review of `results/pa_catalyst_trial_2026-10-03/source_boundary_review.md`
(SHA-256 `7efb6e27d9859eff629df0cc6dfcd90ef9e17b74819e9500ee398b5e432addac`) is unchanged and remains in force: no controller,
supervisor, stop, copy or deadline logic differs between `pa_catalyst_trial.py` and `pa_catalyst_retest.py` except the registered
identity (schema, date, parent directory, dependency names) and a zero-SU PREFLIGHT replay of the real control call.

Source. Official QE `qe-7.5` files cached under `results/pa_catalyst_trial_2026-10-03/qe_source/`; every file's URL, byte length and SHA-256 is
recorded in that phase's `qe_source*retrieval.json` receipts, and `tests/test_pa_qe_adapter_v2_real.py` re-verifies each cached file against
its receipt before quoting it. Line numbers below are those of the cached files.

## 1. DFT+U is written as `<dftU new_format="true">`; there is no `<lda_plus_u>` element

* `Modules/qexsd_init.f90:510`: `CALL qes_init (obj, "dftU", .true., lda_plus_u_kind, ...)`. The third positional argument of `qes_init_dftU` is
  `new_format`, so every QE 7.5 DFT+U block carries `new_format="true"`.
* `Modules/qes_init_module.f90` `qes_init_dftU`: the argument list is `new_format, lda_plus_u_kind, Hubbard_Occ, Hubbard_U, Hubbard_Um, Hubbard_J0,
  Hubbard_alpha, Hubbard_beta, Hubbard_J, starting_ns, Hubbard_V, Hubbard_ns, Hub_m_order, U_projection_type, Hubbard_back, Hubbard_alpha_back,
  Hubbard_ns_nc`. It has no `lda_plus_u` argument.
* `Modules/qexsd_copy.f90:403`: `lda_plus_u = dft_obj%dftU_ispresent`. QE's own reader derives the flag from the presence of the block.
* `PW/src/pw_init_qexsd_input.f90:305-401` builds the block only `IF (ip_lda_plus_u)`, from `lda_plus_u_kind` (:395), the U values converted
  eV to Hartree (`ev_to_Ha = 1/e2/RYTOEV`, :143, :343) and `U_projection_type = ip_hubbard_projectors` (:396).

Real files agree: all 21 real QE 7.5 XML files with a DFT+U block (the control call and 19 `calculation='scf'` files, plus one more in
`runs/hea/ieee_init_2026-09-11`) contain exactly one `dftU` with attribute `new_format="true"` and children `lda_plus_u_kind`, `Hubbard_U`,
`U_projection_type`; none contains `lda_plus_u`. The `<output>` element repeats a `dftU` block of its own; only `<input>` is compared.

Adapter rule (v2): exactly one `dftU`; `new_format == "true"`; children limited to the three above (any other child, including an invented
`lda_plus_u`, `Hubbard_J0`, `Hubbard_Um`, `Hubbard_V`, `Hubbard_back`, fails closed); `lda_plus_u_kind == 0`; `U_projection_type == atomic`;
`Hubbard_U` species, shell and eV value (Hartree x 2 x Ry/eV) equal to the deck's `HUBBARD (atomic)` card within 1e-10 eV.

## 2. Deck strings that QE rewrites before they reach `<input>`

`pa_qe_adapter_v2.QE75_XML_CANONICAL` is the map used by every deck-string comparison; a compared key without a rule raises.

| key | rule | source (cached file:line) | quoted text |
|---|---|---|---|
| `diagonalization` | `david` -> `davidson`, otherwise verbatim | `PW/src/pw_init_qexsd_input.f90:477-481` | `IF (TRIM(ip_diagonalization) == 'david') THEN` / `diagonalization = 'davidson'` / `ELSE` / `diagonalization = ip_diagonalization` |
| `disk_io` | `default` -> `low`, otherwise verbatim | `Modules/qexsd_input.f90:85-89` | `IF ( TRIM(disk_io) .EQ. 'default' ) THEN` / `disk_io_value="low"` |
| `verbosity` | `default` -> `low`, otherwise verbatim | `Modules/qexsd_input.f90:80-84` | `IF ( TRIM( verbosity ) .EQ. 'default' ) THEN` / `verbosity_value = "low"` |
| `functional` (`input_dft`) | upper case when set; absent -> functional of the pseudopotentials (`PBE` here) | `PW/src/pw_init_qexsd_input.f90:203-211` | `dft_name(i:i) = capital(dft_name(i:i))` |
| smearing | alias table `gaussian`, `mp`, `mv`, `fd` (`cold` and `m-v` -> `mv`) | `PW/src/set_occupations.f90:135-157` | `CASE ( 'marzari-vanderbilt', 'cold', 'm-v', 'mv', 'Marzari-Vanderbilt', 'M-V', 'MV')` / `schema_smearing = 'mv'` |
| `mixing_mode` | verbatim, case-sensitive | `PW/src/input.f90:1163-1164` | `SELECT CASE( trim( mixing_mode ) )` / `CASE( 'plain' )` |
| `ion_dynamics` | verbatim (`&IONS` is read for `scf` too, so the deck value is written for every arm) | `Modules/read_namelists.f90` main routine; `Modules/input_parameters.f90:1099-1103` | `READ( unit_loc, ions, ...)` unless `nscf`/`bands` |
| `occupations` | verbatim | `PW/src/pw_init_qexsd_input.f90:449` | `ip_occupations` |
| `calculation`, `restart_mode`, `prefix` | verbatim | `Modules/qexsd_input.f90:92-93` | `calculation=TRIM(calculation)`, `restart_mode=TRIM(restart_mode)`, `prefix=TRIM(prefix)` |
| `U_projection_type` | verbatim (`atomic`, `ortho-atomic` seen in real files) | `PW/src/pw_init_qexsd_input.f90:396` | `U_PROJECTION_TYPE=ip_hubbard_projectors` |

`max_seconds` is written as `nint(max_seconds)` (`Modules/qexsd_input.f90:79`), an integer equal to the deck's `7080`. `nstep` is the internal value
(`NSTEP = cf_nstep`, `PW/src/pw_init_qexsd_input.f90:170`), which QE sets to 1 for `calculation='scf'` (all 19 real scf files show `nstep` 1 against
a deck value of 200) and is therefore neither compared nor part of the cross-arm identity.

Every one of these maps is exercised on real files. `diagonalization='david'`, `disk_io='default'`, `verbosity='default'` and `input_dft='pbe'`
are QE's own defaults made explicit, so the real control XML is the XML QE writes for those decks too; the corrected adapter accepts them and the
frozen adapter (with only the `lda_plus_u` requirement removed) refuses three of the four (`audit_table.md`, section 3).

## 3. What the fresh and restart arms change in `<input>`

`Modules/read_namelists.f90` `fixval` sets, per `calculation`, only `ion_dynamics` for `relax` (to `bfgs`, before `&IONS` is read, so the deck's own
`ion_dynamics = 'bfgs'` wins) and `startingwfc` / `startingpot` (not written to the XML). Real evidence: the `<input>` of the real relax control and a
real scf file differ only in `calculation`, `max_seconds`, `nstep`, `outdir`, `prefix`, `pseudo_dir` (declared operational exclusions of the cross-arm
identity) and in fields set by the two different decks; and the four real H2 arms (clean stop, continuous, resumed with `restart_mode='restart'`,
from-scratch negative control) share one XML identity. No real relax and scf pair from the same deck exists locally, so the fresh-versus-control
identity on the catalyst deck is inferred from this, not observed.

## 4. Not claimed

* The registered `HUBBARD (atomic)` projector is the only one accepted for the trial. The `ortho-atomic` decks of the 19 real scf files are read in tests
  only, by widening `HUBBARD_PROJECTORS` inside the test.
* A real restart (`restart_mode='restart'`) log from a 72-atom 128-rank run does not exist; the resumed arm's log parsing is checked on the real
  one-process H2 restart only.
* The carry-over hypothesis, the warm-versus-fresh decision and the reseed branch were not reached by job 21034683 and are not tested by any of the
  above.
