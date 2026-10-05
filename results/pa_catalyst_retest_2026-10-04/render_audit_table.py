"""Render audit_real_outputs.json as audit_table.md (refuses to overwrite)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "audit_real_outputs.json").read_text(encoding="utf-8"))
target = HERE / "audit_table.md"
if target.exists():
    raise SystemExit("audit_table.md exists; refusing to overwrite")

out = []
add = out.append
add("# Real-output audit: what the adapter and controller require against real QE 7.5 output\n")
add("Zero SU: every row is computed from files already on this machine by `audit_real_outputs.py`; nothing ran on Anvil.")
add("Corpora: CONTROL = the control call of job 21034683 (72 atoms, Hubbard U, 128 MPI, relax stopped after 3 evaluations);")
add("SCF19 = 19 real `calculation='scf'` Hubbard XML files with deck and log (`runs/a0/pproj6`); FRESH21 / SEG21 = 21 real September")
add("72-atom 128-rank fresh-SCF / one-step from-scratch relax logs; TINY = the four retained one-process H2 restart arms.\n")

add("## 1. XML elements required by `read_qe_arm` (corrected adapter), per arm path\n")
add("`found once / lookups` counts every `_one(parent, tag)` call made while the corrected adapter accepted the real files. "
    "Clean-stop path = CONTROL (control, candidate, resumed, negative and reseed arms all end as clean stops); "
    "fresh path = SCF19 (`calculation='scf'`, `expected_exit='normal_scf'`).\n")
clean = {(r["parent"], r["tag"]): r for r in data["xml_lookups_clean_stop_path"]}
fresh = {(r["parent"], r["tag"]): r for r in data["xml_lookups_fresh_path"]}
add("| parent | required child | clean-stop path (1 real XML) | fresh path (19 real XML) | result |")
add("|---|---|---|---|---|")
for key in sorted(set(clean) | set(fresh)):
    a, b = clean.get(key), fresh.get(key)
    cell_a = "not used" if a is None else "%d / %d" % (a["found_once"], a["calls"])
    cell_b = "not used" if b is None else "%d / %d" % (b["found_once"], b["calls"])
    ok = all(r is None or r["missing_or_repeated"] == 0 for r in (a, b))
    add("| %s | %s | %s | %s | %s |" % (key[0], key[1], cell_a, cell_b, "PASS" if ok else "MISMATCH"))
add("\nElements used only on one path: `step` records and `output` proposal (clean stop); `output/convergence_info`, "
    "`output/total_energy`, `output/forces` (fresh path).\n")

add("## 2. XML attributes the adapter reads\n")
add("| element | attribute | present in real QE 7.5 XML |")
add("|---|---|---|")
for row in data["xml_attributes_read"]:
    add("| %s | %s | %s |" % (row["tag"], row["attribute"], "yes" if row["in_real_qe75_xml"] else "NO"))
add("\nElement the frozen synthetic fixture invented and the frozen adapter required: `lda_plus_u`; present in any real QE 7.5 "
    "XML: **%s** (%d real XML files scanned).\n" % ("yes" if data["tags_the_frozen_fixture_invented"]["lda_plus_u"] else "no",
                                                    data["real_xml_files_in_vocabulary"]))

add("## 3. Deck strings that QE rewrites before they reach the XML (canonicalization map)\n")
add("Source = cached official QE 7.5 source (retrieval receipts pin every file).\n")
add("| key | rule | QE 7.5 source | cited text |")
add("|---|---|---|---|")
for row in data["canonical_map"]:
    rule = row["kind"] if "map" not in row else "map " + json.dumps(row["map"])
    cited = " / ".join(x.strip() for x in row.get("cited_text", [])) if row.get("cited_text") else "(no line span)"
    add("| %s | %s | %s | `%s` |" % (row["deck_or_xml_key"], rule, row["source"], cited.replace("|", "/")[:160]))
add("\nEffect on real files (frozen adapter with only the dry-run's one-line `lda_plus_u` patch, versus the corrected adapter), "
    "real control XML, deck with one extra explicit assignment:\n")
add("| deck assignment | expectation | frozen + dry-run patch | corrected adapter |")
add("|---|---|---|---|")
for row in data["latent_literal_compare_hazards"]:
    add("| `%s` | %s | %s | %s |" % (row["deck_assignment"], row["expectation"], row["frozen_with_dryrun_patch"], row["v2"]))

add("\n## 4. Log literals and regular expressions (match counts per file: min-max over the corpus)\n")
corpora = []
for row in data["log_table"]:
    if row["corpus"] not in corpora:
        corpora.append(row["corpus"])
add("| item | role | " + " | ".join(c.split(" (")[0] + " (%d)" % next(r["files"] for r in data["log_table"] if r["corpus"] == c) for c in corpora) + " |")
add("|---|---|" + "---|" * len(corpora))
items = []
for row in data["log_table"]:
    if row["item"] not in items:
        items.append(row["item"])
for item in items:
    cells, role = [], ""
    for corpus in corpora:
        row = next(r for r in data["log_table"] if r["item"] == item and r["corpus"] == corpus)
        role = row["role"]
        low, high = row["match_counts_min_max"]
        cells.append(str(low) if low == high else "%d-%d" % (low, high))
    add("| %s | %s | %s |" % (item, role, " | ".join(cells)))
add("\nReading: 0 where a literal is not expected (no ionic cycle in a fixed-geometry scf; no `K-points division` / ELPA line in a "
    "serial run; no stop line in a normal run) is correct; `0-1` in the stalled-or-converged corpora is the per-file spread.\n")

add("## 5. Failure regular expressions on real logs (files that hit)\n")
add("| corpus | files | adapter FAILURE | controller FAILURE | controller TIME_FAILURE | controller HEA4 iteration >= 127 |")
add("|---|---|---|---|---|---|")
for row in data["failure_regex_table"]:
    add("| %s | %d | %d | %d | %d | %d |" % (row["corpus"], row["files"], row["adapter_FAILURE_hits"], row["controller_FAILURE_hits"],
                                              row["controller_TIME_FAILURE_hits"], row["controller_HEA4_iteration_127_hits"]))
add("\nTIME_FAILURE hits in SEG21 are the phrase `The maximum number of steps has been reached` that QE prints when `nstep=1` is "
    "exhausted; the registered arms use `nstep=30` with an EXIT stop, and the real control never printed it. "
    "HEA4 hits in FRESH21 are the 6 of 21 real fresh SCFs that stalled at iteration 127 (they are the HOLD path of the trial).\n")

add("## 6. Cross-arm XML identity on real files\n")
evidence = data["xml_identity_evidence"]
add("- TINY arms (clean stop, continuous, resumed with `restart_mode='restart'`, from-scratch negative): XML identity equal across all four: **%s**." % evidence["tiny_h2_all_equal"])
add("- Real relax (catalyst control) versus real scf (Mn slab) `<input>` fields whose values differ: `%s`." % ", ".join(evidence["relax_control_vs_scf_Mn_slab_differing_input_fields"]))
add("  Of these, `calculation`, `max_seconds`, `nstep`, `outdir`, `prefix`, `pseudo_dir` are the declared operational exclusions of the cross-arm identity; "
    "the rest (`Hubbard_U`, `U_projection_type`, `max_nstep`, `free_positions`, `monkhorst_pack`) are set by the two different decks. "
    "Fields present on one side only: %s." % (", ".join(evidence["relax_control_vs_scf_Mn_slab_fields_on_one_side_only"]) or "none"))
add("- No real relax/scf pair from the same deck exists locally, so fresh-versus-control identity on the catalyst deck itself is inferred from the above plus the QE source "
    "(`read_namelists.f90` fixval changes only ion_dynamics for `relax`, which the deck sets explicitly; `&IONS` is read for `scf` as well), not observed.\n")

add("## 7. Outcome of the corrected adapter on every real pair\n")
control = data["control_clean_stop"]
add("- CONTROL clean-stop path through `read_qe_arm`: **%s** (%d evaluations, SCF counters %s, optimizer counters %s, exit status %s, first threshold %s Ry, runtime %s)." % (
    control["result"], control["evaluations"], control["scf_counts"], control["optimizer_counts"], control["xml_exit_status"],
    control["first_conv_thr_Ry"], "%d MPI / %d pools / %s %s" % (control["runtime_parallel"]["nprocs"], control["runtime_parallel"]["npool"],
                                                              control["runtime_parallel"]["diagonalization_algorithm"], control["runtime_parallel"]["elpa_subgroup"])))
scf = data["scf_pairs"]
add("- SCF19 fresh path through `read_qe_arm(expected_exit='normal_scf')`: **%d of %d accepted** (%d with real UPF reads; the runtime-header check is stubbed because those runs used 128 ranks / 4 pools / serial diagonalization, not the registered layout)." % (
    sum(o["result"] == "ACCEPTED" for o in scf), len(scf), sum(o["real_upf_reads"] for o in scf)))
add("- Frozen adapter (byte-identical copy of the pin `25546421...`) on the same real files: control `_check_xml_input` -> **%s**; scf decks -> %s." % (
    data["frozen_adapter_on_same_files"]["control_xml_input"], data["frozen_adapter_on_same_files"]["scf_decks_refused_by_frozen_parse_deck"]))
target.write_text("\n".join(out) + "\n", encoding="utf-8")
print(len(out), "lines")
