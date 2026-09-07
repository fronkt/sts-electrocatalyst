"""HEA fixed-geometry SCF arms: deck writer round-trip, k-mesh rule, geometry integrity, the
submitter greps on the NOT LICENSED manifests, cost-model calibration and survey, the pilot
reuse of panel decks, and the readout on synthetic pw.x fragments (including realistic
non-convergence, kill sidecars, the sign-scoring rule, the desorbed-OOH bookkeeping and the
Loewdin spin check)."""
import hashlib
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "dft"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import hea_deck as hd  # noqa: E402
import hea_cost_model as cm  # noqa: E402
import hea_geometry as hg  # noqa: E402
import hea_panel_readout as hp  # noqa: E402

BANK = os.path.join(ROOT, "results", "cr_site_chains_2026-09-06")
PANEL = os.path.join(BANK, "dft_branch_panel.json")
MANIFESTS = [os.path.join(ROOT, "runs", "hea", "m_branch_panel.txt"),
             os.path.join(ROOT, "runs", "hea", "m_pilot_retained.txt")]

WEIRD_CELL = [[5.855999434240528, 0.0, 3.585765481475687e-16],
              [2.0120443058924784e-15, 12.511759014755889, 7.66124281456192e-16],
              [0.0, 0.0, 25.023518029511784]]


def test_bank_and_manifests_are_tracked_and_present():
    """The source records are tracked (git ls-files lists 43 files under the bank, the panel
    JSON, verification.json, both replay and both result JSONs and the extxyz exports among
    them), so a fresh checkout must carry them: absence is a failure, not a skip."""
    for p in (PANEL, os.path.join(BANK, "verification.json"), os.path.join(BANK, "equiatomic_ooh_replay.json"),
              os.path.join(BANK, "leader_ooh_replay.json"), os.path.join(BANK, "equiatomic_result.json"),
              os.path.join(BANK, "leader_result.json"), *MANIFESTS):
        assert os.path.exists(p), p


def _synthetic():
    symbols = ["Ni", "Cr", "Cu", "O", "O", "H"]
    positions = [[7.545166147096794e-16, 4.691909630533458, 9.383819261066916],
                 [1.7605387676559188e-15, 10.947789137911403, 9.383819261066916],
                 [0.1, 0.2, 0.30000000000000004],
                 [-0.11067278661244617, 4.522886059217383, 20.170834189759912],
                 [1e-05, 2.0, 3.0],
                 [1.3602639407291246, 4.72985995569906, 21.32519720039578]]
    return symbols, positions, WEIRD_CELL, [0, 1, 3]


# --------------------------------------------------------------------------- deck writer
def test_deck_round_trips_exactly_and_orders_species():
    symbols, positions, cell, fixed = _synthetic()
    text = hd.render_deck("t__atomic", symbols, positions, cell, fixed, "atomic")
    p = hd.parse_deck(text)
    assert p["positions"] == positions and p["cell"] == cell and p["symbols"] == symbols
    assert p["fixed"] == fixed
    assert p["species"] == ["Cr", "Cu", "Ni", "O", "H"]
    assert p["U"] == {"Cr": 3.7, "Ni": 6.2}          # no U line for Cu
    assert p["mag"] == {1: 0.6, 2: 0.2, 3: 0.3, 4: 0.0, 5: 0.0}
    assert "HUBBARD (atomic)" in text and "\r" not in text
    assert "  electron_maxstep = 300" in text and "  max_seconds = 165000" in text
    assert "  calculation = 'scf'" in text and "  nspin = 2" in text
    ortho = hd.render_deck("t__ortho", symbols, positions, cell, fixed, "ortho")
    assert "HUBBARD (ortho-atomic)" in ortho
    assert sum(1 for a, b in zip(text.split("\n"), ortho.split("\n")) if a != b) == 2  # prefix + card


def test_deck_writer_refuses_unknown_species_and_bad_projector():
    symbols, positions, cell, fixed = _synthetic()
    with pytest.raises(SystemExit):
        hd.render_deck("x", ["Ru"] + symbols[1:], positions, cell, fixed, "atomic")
    with pytest.raises(SystemExit):
        hd.render_deck("x", symbols, positions, cell, fixed, "orthoatomic")


def test_write_lf_refuses_cr_and_differing_overwrite(tmp_path):
    p = tmp_path / "a.in"
    hd.write_lf(p, "x\n")
    hd.write_lf(p, "x\n")  # identical is fine
    with pytest.raises(SystemExit):
        hd.write_lf(p, "y\n")
    with pytest.raises(SystemExit):
        hd.write_lf(tmp_path / "b.in", "x\r\n")


def test_kmesh_rule_matches_qe_slab_and_nk_choice():
    import qe_slab
    for cell, want in ((WEIRD_CELL, (4, 2, 1)),
                       ([[5.9455, 0, 0], [0, 12.601349947525463, 0], [0, 0, 25.20269989505093]], (4, 2, 1)),
                       ([[5.832, 0, 0], [0, 6.25223816, 0], [0, 0, 25.00895264]], (4, 4, 1)),
                       ([[2.916, 0, 0], [0, 6.25223816, 0], [0, 0, 25.00895264]], (9, 4, 1))):
        assert hd.kgrid_from_cell(cell) == want == tuple(qe_slab.kgrid_from_cell(cell))
    assert hd.kpoint_count((4, 2, 1)) == 8
    assert [hd.choose_nk(n) for n in (8, 10, 16, 15, 3, 1)] == [8, 8, 16, 8, 2, 1]


def test_preflight_upf_table_parses():
    pre = hd.preflight_upfs()
    for sp in hd.ELEMENTS.values():
        assert sp["pseudo"] in pre
    assert pre["Cu.paw.z_11.ld1.psl.v1.0.0-low.upf"] == "619f40885d92a09a85a8b37550532d0c"


# --------------------------------------------------------------------------- geometry integrity
def _toy_slab():
    """4 metals + 4 O in a 10 x 10 x 30 A box; adsorbate atoms appended."""
    cell = [[10.0, 0, 0], [0, 10.0, 0], [0, 0, 30.0]]
    sym = ["Cr", "Ni", "Fe", "Co", "O", "O", "O", "O"]
    pos = [[0, 0, 10.0], [5, 0, 10.0], [0, 5, 10.0], [5, 5, 10.0],
           [2.5, 0, 10.0], [7.5, 0, 10.0], [2.5, 5, 10.0], [7.5, 5, 10.0]]
    return sym, pos, cell


def test_geometry_classes_and_mic():
    sym, pos, cell = _toy_slab()
    assert hg.mic_distance([0, 0, 0], [9.5, 0, 0], cell) == pytest.approx(0.5)
    # intact *OOH on Cr0
    r = hg.analyse(sym + ["O", "O", "H"], pos + [[0, 0, 12.0], [0.9, 0, 13.0], [1.4, 0, 13.8]], cell, n_slab=8)
    assert r["screen_category"] == "NORMAL" and r["free_species"] is None
    assert r["atoms"][8]["nearest_metal"] == "Cr0" and r["atoms"][8]["nearest_metal_A"] == pytest.approx(2.0)
    # HO2 radical 4 A above the surface
    r = hg.analyse(sym + ["O", "O", "H"], pos + [[0, 0, 14.5], [1.3, 0, 14.5], [1.6, 0, 15.4]], cell, n_slab=8)
    assert r["screen_category"] == "DESORPTION" and r["expected_free_species_moment_muB"] == 1.0
    # O2 in the cell + H on slab O4
    r = hg.analyse(sym + ["O", "O", "H"], pos + [[5, 2.5, 13.5], [5, 3.7, 13.5], [2.5, 0, 10.97]], cell, n_slab=8)
    assert r["screen_category"].startswith("DESORPTION") and "DISSOCIATION" in r["screen_category"]
    assert r["expected_free_species_moment_muB"] == 2.0 and r["H_nearest_slab_O_index"] == 4
    # *O2 + H_b bridge state: O2 bound to Ni1, H on slab O
    r = hg.analyse(sym + ["O", "O", "H"], pos + [[5, 0, 11.9], [5, 1.2, 12.0], [2.5, 0, 10.97]], cell, n_slab=8)
    assert r["screen_category"] == "DISSOCIATION / H TRANSFER" and r["free_species"] is None
    # OH and O records, clean slab
    assert hg.analyse(sym + ["O", "H"], pos + [[0, 0, 11.9], [0, 0, 12.87]], cell, n_slab=8)["screen_category"] == "NORMAL"
    assert hg.analyse(sym + ["O"], pos + [[0, 0, 11.6]], cell, n_slab=8)["screen_category"] == "NORMAL"
    assert hg.analyse(sym, pos, cell, n_slab=8)["anomaly_class"] == "CLEAN SLAB"


def test_panel_decks_carry_the_stated_anomaly_classes():
    want = {"equiatomic_pull2.10": "NORMAL", "equiatomic_builder": "DESORPTION", "leader_builder": "DESORPTION",
            "leader_pull2.10": "DESORPTION + DISSOCIATION / H TRANSFER", "leader_pull1.70": "DESORPTION + DISSOCIATION / H TRANSFER"}
    for label, cat in want.items():
        r = hp.deck_integrity(os.path.join(ROOT, "runs", "hea", "branch_panel", f"{label}__atomic.in"))
        assert r["screen_category"] == cat, label
    r = hp.deck_integrity(os.path.join(ROOT, "runs", "hea", "branch_panel", "leader_pull2.10__atomic.in"))
    assert r["O_O_A"] == pytest.approx(1.2299356375432444, abs=1e-6)     # dft_branch_panel.json O-O of record
    assert r["H_nearest_slab_O_index"] == 56 and r["expected_free_species_moment_muB"] == 2.0


# --------------------------------------------------------------------------- built decks + manifests
def test_panel_decks_reproduce_the_retained_geometry_exactly():
    panel = json.load(open(PANEL, encoding="utf-8"))
    for pair in panel["pairs"]:
        for st in pair["states"]:
            doc = json.load(open(os.path.join(BANK, st["source_json"]), encoding="utf-8"))
            g = hd.json_pointer(doc, st["geometry_pointer"])
            for proj in ("atomic", "ortho"):
                path = os.path.join(ROOT, "runs", "hea", "branch_panel", f"{pair['arm']}_{st['start']}__{proj}.in")
                assert os.path.exists(path)
                text = open(path, "rb").read()
                assert b"\r" not in text
                p = hd.parse_deck(text.decode("utf-8"))
                assert p["positions"] == g["positions_A"] and p["cell"] == g["cell_A"]
                assert p["symbols"] == g["symbols"] and p["fixed"] == sorted(g["fixed_atom_indices"])
                assert p["mesh"] == (4, 2, 1)


def test_manifests_trip_the_submitter_refusals_and_carry_true_md5s():
    import re
    for m in MANIFESTS:
        text = open(m, "rb").read().decode("utf-8")
        assert "\r" not in text
        assert re.search("not licensed", text, re.I)                        # anvil/47_submit_a0.sh:57
        assert f"# SUBMIT WITH EXCLUDE={hd.EXCLUDE}" in text.split("\n")     # :62-80
        assert sum(1 for ln in text.split("\n") if re.match(r"^# *N(P|CONC)=", ln)) == 1
        assert sum(1 for ln in text.split("\n") if re.match(r"^# NP=[0-9]+ NCONC=[0-9]+$", ln)) == 1
        assert "# NP=128 NCONC=1" in text.split("\n")   # 47_submit_a0.sh:100 preflights the driver with NCONC 1
        info = hd.check_manifest_text(text)
        assert info["not_licensed"] and info["np_directive"]
        rows = [ln.split() for ln in text.split("\n") if ln.strip() and not ln.startswith("#")]
        for d, job, suf, nk in rows:
            deck = os.path.join(ROOT, "runs", d, job + suf)
            assert os.path.exists(deck), deck
            assert 128 % int(nk) == 0
            assert hashlib.md5(open(deck, "rb").read()).hexdigest() in text
        assert len(rows) in (10, 12)


def test_pilot_reuses_the_panel_ooh_decks_instead_of_duplicating_them():
    text = open(MANIFESTS[1], "rb").read().decode("utf-8")
    reused = [ln for ln in text.split("\n") if ln.startswith("#   ") and "-> hea/branch_panel/" in ln]
    assert len(reused) == 4
    for ln in reused:
        target = ln.split("-> ")[1].split()[0]          # hea/branch_panel/<label>__<proj>.in
        md5 = [t for t in ln.split() if len(t) == 32 and all(c in "0123456789abcdef" for c in t)][0]
        assert hashlib.md5(open(os.path.join(ROOT, "runs", target), "rb").read()).hexdigest() == md5
    for chain in ("Fe25Co25Ni25Cr25__s2_site0", "Ni31Cr29Cu5Mn35__s0_site0"):
        for proj in ("atomic", "ortho"):
            assert not os.path.exists(os.path.join(ROOT, "runs", "hea", "pilot_retained", chain, f"OOH__{proj}.in"))
    assert "OOH__atomic .in" not in text and "OOH__ortho .in" not in text


def test_builders_verify_in_check_mode_without_writing():
    import build_hea_panel
    import build_hea_pilot
    before = {p: os.path.getmtime(p) for p in MANIFESTS if os.path.exists(p)}
    assert build_hea_panel.main(["--check"]) == 0
    assert build_hea_pilot.main(["--retained", "--check"]) == 0
    assert {p: os.path.getmtime(p) for p in before} == before


def test_pilot_builder_refuses_out_root_outside_runs_before_writing(tmp_path):
    import build_hea_pilot
    out = tmp_path / "pilot"
    with pytest.raises(SystemExit):
        build_hea_pilot.main(["--census", os.path.join(BANK, "leader_result.json"), "--formula", "Ni31Cr29Cu5Mn35",
                              "--seed", "0", "--site", "0", "--out-root", str(out), "--manifest", str(tmp_path / "m.txt")])
    assert not out.exists() and not (tmp_path / "m.txt").exists()


def test_manifest_planning_figures_equal_the_cost_model_arm_totals():
    tot = cm.arm_totals()
    for m, arm in zip(MANIFESTS, ("panel", "pilot")):
        text = open(m, encoding="utf-8").read()
        assert f"{tot[arm]['plan']:.1f} core-h for the" in text
        assert f"ceiling {tot[arm]['ceiling']:.1f} core-h" in text
    assert tot["panel"]["n"] == 10 and tot["pilot"]["n"] == 12
    assert sum(1 for r in tot["pilot"]["rows"] if r["reuse"]) == 4


# --------------------------------------------------------------------------- cost model
def test_nbnd_rule_reproduces_the_banked_pairs():
    for nelec, nbnd in ((312, 187), (325, 196), (318, 191), (319, 192), (163, 98), (162, 97),
                        (181, 109), (168, 101), (348, 209)):
        assert cm.nbnd_rule(nelec) == nbnd


def test_cost_model_calibration_residuals():
    rows = {r["name"]: r for r in cm.calibration()}
    ref = rows[cm.REF]
    assert abs(ref["t_iter_A"] / ref["t_iter_obs"] - 1) < 1e-12
    one = rows["s0_OH__u715_atomic (1x1, atomic)"]
    assert abs(one["t_iter_B"] / one["t_iter_obs"] - 1) < 0.05        # model B fits the 1x1 point
    assert abs(one["ram_pred"] / one["ram_obs"] - 1) < 0.02
    esc = rows["s0_OOH__2x1v_escape__u715 (atomic)"]
    assert 1.0 < esc["t_iter_A"] / esc["t_iter_obs"] < 1.5              # envelope over-predicts, bounded


def test_cost_model_constants_of_record():
    assert cm.ORTHO_WALL_RATIO == pytest.approx((7 * 60 + 53.78) / (6 * 60 + 29.41))   # :2530 / :2515
    ratios = {st: to / ta for st, (ta, to, _, _) in cm.ONE_BY_ONE_PAIRS.items()}
    assert ratios["OOH"] == pytest.approx(0.953, abs=1e-3) and ratios["OH"] == pytest.approx(1.609, abs=1e-3)
    assert min(ratios.values()) == ratios["OOH"] and max(ratios.values()) == ratios["OH"]
    assert cm.PLANNING_ITERS == 42 and cm.CEILING_FACTOR == 3.0 and cm.NODE_GB == 237.0


def test_iteration_survey_reads_first_scf_and_nonconvergence(tmp_path):
    def out(name, nat, first, notconv=False, mag=True):
        lines = ["     Program PWSCF v.7.5", f"     number of atoms/cell      =  {nat}",
                 "     mixing beta               =       0.3000", "     local-TF  mixing"]
        if mag:
            lines.append("     total magnetization       =     2.00 Bohr mag/cell")
        if first:
            lines.append(f"     convergence has been achieved in  {first} iterations")
            lines.append("     convergence has been achieved in   5 iterations")   # a later ionic step, ignored
        if notconv:
            lines.append("     convergence NOT achieved after 300 iterations: stopping")
        (tmp_path / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    out("a.out", 36, 20)
    out("b.out", 36, 60)
    out("c.out", 36, None, notconv=True)
    out("d.out", 3, 99)          # a molecule: excluded by nat
    out("e.out", 36, 99, mag=False)   # nspin = 1: excluded
    (tmp_path / "hea").mkdir()
    out("hea/f.out", 36, 999)     # excluded directory
    sv = cm.iteration_survey(tmp_path)
    assert sv["n_files"] == 3 and sv["n_converged_first"] == 2 and sv["n_not_achieved"] == 1
    assert sv["local_tf_beta03"]["max"] == 60 and sv["all"]["min"] == 20


def test_cost_model_hea_cell_is_core_bound_at_planning():
    counts = {"Cr": 6, "Ni": 6, "Fe": 6, "Co": 6, "O": 50, "H": 1}
    cell = [[5.9455, 0, 0], [0, 12.601349947525463, 0], [0, 0, 25.20269989505093]]
    r = cm.per_scf(counts, cell, 8, 8)
    assert r["descriptors"]["nelec"] == 691 and r["descriptors"]["nbnd"] == 415
    assert r["billing"]["core_bound"] and r["billing"]["fits_node"]
    assert r["atomic"]["ceiling_coreh"] == pytest.approx(3 * r["atomic"]["plan_coreh"])
    assert r["ortho"]["plan_coreh"] == pytest.approx(r["atomic"]["plan_coreh"] * cm.ORTHO_WALL_RATIO)
    assert r["ceiling_iters"] == 126


# --------------------------------------------------------------------------- readout
def _fake_out(path, energy_ry, iters=25, done=True, notconv=False, wall="1h 2m 3.50s", cores=128, totmag=24.0,
              max_seconds=False):
    """A pw.x fragment. On non-convergence pw.x prints NO '!' line (runs/s3/Co/ref__2x1v.replay.out:
    0 lines match '^!', 'convergence NOT achieved after 500 iterations' at :8023, one JOB DONE)."""
    lines = [
        "     Parallel version (MPI & OpenMP), running on     %d processor cores" % cores,
        "     iteration #  1     ecut=    80.00 Ry     beta= 0.30",
        "     total magnetization       =    %.2f Bohr mag/cell" % totmag,
        "     absolute magnetization    =    30.00 Bohr mag/cell",
    ]
    if notconv:
        lines.append("     convergence NOT achieved after %d iterations: stopping" % iters)
    elif max_seconds:
        lines.append("     Maximum CPU time exceeded")
    else:
        lines.append("     convergence has been achieved in  %d iterations" % iters)
        lines.append("!    total energy              =   %.8f Ry" % energy_ry)
    lines.append("     PWSCF        :   8m34.51s CPU   %s WALL" % wall)
    if done:
        lines.append("   JOB DONE.")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def _fake_lowdin(path, polarizations):
    """<job>.lowdin.txt in the banked shape (Atom # N: ... polarization = x)."""
    lines = ["# Lowdin section of x.projwfc.out (full projwfc output retained on Anvil beside the deck)", "Lowdin Charges: ", ""]
    for i, p in enumerate(polarizations, 1):
        lines.append(f"     Atom #{i:4d}: total charge =   6.0000, s =  1.9000, p =  4.1000, d =  0.0000, ")
        lines.append(f"                 polarization = {p:8.4f}, s =  0.0000, p = {p:8.4f}, d =  0.0000, ")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def test_registered_bands_are_parsed_from_their_sources():
    b = hp.registered()
    assert b["band_dG_eV"] == 0.25
    assert b["band_eta_V"] == 0.164                          # docs/33:65, the same MACE-MPA-0 row
    assert b["band_eta_secondary_V"] == 0.12955764753597102  # r4_validate.json mae_eta


def test_readout_refuses_a_moved_band(tmp_path):
    bad = tmp_path / "33.md"
    bad.write_text("nothing here", encoding="utf-8")
    with pytest.raises(hp.Fatal):
        hp.registered(docs33=bad)


def test_parse_out_terminal_states(tmp_path):
    _fake_out(tmp_path / "a.out", -6000.12345678, iters=41, wall="2h 3m 4.25s")
    o = hp.parse_out(tmp_path / "a.out")
    assert o["status"] == "CONVERGED" and o["E_Ry"] == -6000.12345678 and o["iterations"] == 41 and o["job_done"] == 1
    assert o["wall_s"] == 2 * 3600 + 3 * 60 + 4.25 and o["cores"] == 128 and o["totmag"] == 24.0
    assert o["E_eV"] == pytest.approx(-6000.12345678 * hp.RY_EV)
    _fake_out(tmp_path / "b.out", -1.0, iters=300, notconv=True)          # realistic: no '!' line
    o = hp.parse_out(tmp_path / "b.out")
    assert o["status"] == "NOT CONVERGED" and o["not_achieved"] == 1 and o["iterations"] == 300 and o["E_Ry"] is None
    _fake_out(tmp_path / "c.out", -1.0, max_seconds=True)
    assert hp.parse_out(tmp_path / "c.out")["status"] == "NOT CONVERGED"
    _fake_out(tmp_path / "leader_pull2.10__ortho.out", -1.0, iters=3, done=False)   # running: no energy yet
    assert hp.parse_out(tmp_path / "leader_pull2.10__ortho.out")["status"] == "PENDING"
    (tmp_path / "leader_pull2.10__ortho.KILLED").write_text("kill rule (a)\n")      # dotted job name
    assert hp.parse_out(tmp_path / "leader_pull2.10__ortho.out")["status"] == "KILLED"
    assert hp.parse_out(tmp_path / "missing.out")["status"] == "PENDING"
    (tmp_path / "gone.KILLED").write_text("")
    assert hp.parse_out(tmp_path / "gone.out")["status"] == "KILLED"


def test_panel_pending_while_outputs_absent(tmp_path):
    panel = json.load(open(PANEL, encoding="utf-8"))
    r = hp.score_panel(panel, tmp_path, 0.25, deck_dir=os.path.join(ROOT, "runs", "hea", "branch_panel"))
    assert len(r["pending"]) == 10
    assert all(p["projectors"][x]["verdict"] == "PENDING" for p in r["pairs"] for x in ("atomic", "ortho"))
    assert r["integrity"]["leader_pull2.10"]["free_species"] == "O2(g) triplet"


def test_panel_scores_band_sign_rule_nonconvergence_and_spin(tmp_path):
    panel = json.load(open(PANEL, encoding="utf-8"))
    deck_dir = os.path.join(ROOT, "runs", "hea", "branch_panel")
    ev = hp.RY_EV
    base = -6000.0
    # pair 1 (equiatomic): MACE dE = +0.031 eV, inside the band -> sign UNSCORED.
    # atomic: DFT dE = +0.10 eV (within); ortho: DFT dE = -0.10 eV (within, sign differs but unscored).
    _fake_out(tmp_path / "equiatomic_pull2.10__atomic.out", base)
    _fake_out(tmp_path / "equiatomic_builder__atomic.out", base + 0.10 / ev)
    _fake_out(tmp_path / "equiatomic_pull2.10__ortho.out", base)
    _fake_out(tmp_path / "equiatomic_builder__ortho.out", base - 0.10 / ev)
    # pair 2 (leader): MACE dE = -2.28 eV, sign SCORED. atomic: DFT -2.20 (agrees, within);
    # ortho: leader_pull2.10 NOT CONVERGED (realistic fragment, no '!' line).
    _fake_out(tmp_path / "leader_builder__atomic.out", base)
    _fake_out(tmp_path / "leader_pull2.10__atomic.out", base - 2.20 / ev)
    _fake_out(tmp_path / "leader_builder__ortho.out", base)
    _fake_out(tmp_path / "leader_pull2.10__ortho.out", base - 2.5 / ev, notconv=True)
    # optional: pull1.70 - pull2.10 = +0.90 eV atomic (MACE +0.726, diff +0.174 within, sign agrees);
    # ortho leg of pull1.70 KILLED by the kill rule.
    _fake_out(tmp_path / "leader_pull1.70__atomic.out", base - 2.20 / ev + 0.90 / ev)
    (tmp_path / "leader_pull1.70__ortho.KILLED").write_text("kill rule (b)\n")
    # Loewdin tables: leader_pull2.10 atomic carries an O2 triplet on atoms 72-74 (2.0);
    # equiatomic_builder atomic carries 0.1 on the HO2 (expected 1) -> UNRESOLVED; no table for leader_builder.
    _fake_lowdin(tmp_path / "leader_pull2.10__atomic.lowdin.txt", [0.0] * 72 + [1.0, 1.0, 0.0])
    _fake_lowdin(tmp_path / "equiatomic_builder__atomic.lowdin.txt", [0.0] * 72 + [0.05, 0.05, 0.0])
    r = hp.score_panel(panel, tmp_path, 0.25, deck_dir=deck_dir)
    assert r["pending"] == []
    p1, p2 = r["pairs"]
    assert p1["sign_scored"] is False and p2["sign_scored"] is True
    assert p1["projectors"]["atomic"]["verdict"] == "WITHIN (sign UNSCORED: |dE_MACE| <= band)"
    assert p1["projectors"]["ortho"]["verdict"] == "WITHIN (sign UNSCORED: |dE_MACE| <= band)"
    assert p1["projectors"]["ortho"]["sign_agrees"] is False
    assert p1["projector_agreement"]["sign_agrees"] is False
    assert p2["projectors"]["atomic"]["dE_DFT_eV"] == pytest.approx(-2.20, abs=1e-6)
    assert p2["projectors"]["atomic"]["verdict"] == "SIGN AGREES / WITHIN"
    assert p2["projectors"]["ortho"]["verdict"].startswith("NOT CONVERGED")
    assert p2["projectors"]["ortho"]["legs"]["leader_pull2.10"] == "NOT CONVERGED"
    assert "sign_agrees" not in p2["projector_agreement"]
    opt = r["optional"]
    assert opt["projectors"]["atomic"]["verdict"] == "SIGN AGREES / WITHIN"
    assert opt["projectors"]["ortho"]["verdict"].startswith("NOT CONVERGED")
    assert opt["projectors"]["ortho"]["legs"]["leader_pull1.70"] == "KILLED"
    # spin checks
    legs = r["legs"]
    assert legs["leader_pull2.10__atomic"]["spin"]["verdict"] == "free-species moment reproduced"
    assert legs["leader_pull2.10__atomic"]["spin"]["moment_muB"] == pytest.approx(2.0)
    assert legs["equiatomic_builder__atomic"]["spin"]["verdict"] == "SPIN-STATE UNRESOLVED"
    assert legs["leader_builder__atomic"]["spin"]["verdict"] == "SPIN-STATE UNRESOLVED (no Loewdin table)"
    assert legs["equiatomic_pull2.10__atomic"]["spin"] == {"applies": False}


def _chain(formula, dG, eta, pls, desorbed, ooh_class, reuse=None):
    integ = {"OH": {"screen_category": "NORMAL", "anomaly_class": "*OH adsorbed, intact", "atoms": {}},
             "O": {"screen_category": "NORMAL", "anomaly_class": "*O adsorbed", "atoms": {}},
             "OOH": {"screen_category": ooh_class[0], "anomaly_class": ooh_class[1], "atoms": {}},
             "slab": {"screen_category": "n/a", "anomaly_class": "CLEAN SLAB", "atoms": {}}}
    return dict(formula=formula, seed=0, site=0, energies={}, dG=dG, eta=eta, pls=pls, desorbed=desorbed,
                integrity=integ, reuse=reuse or {})


def test_pilot_eta_rank_order_reuse_and_desorbed_bookkeeping(tmp_path):
    ev = hp.RY_EV
    gas = {"H2O": {"E_eV": -44.04119711 * ev}, "H2": {"E_eV": -2.33323818 * ev}}
    from hea_oer.referencing import ZPE_TS_CORRECTION, delta_G, reference_energy
    chains = [
        _chain("A", {"OH": 1.6, "O": 3.28, "OOH": 4.66}, 0.45, 2, [], ("NORMAL", "*OOH adsorbed, intact")),
        _chain("B", {"OH": 2.2, "O": 3.59, "OOH": 2.74}, 0.98, 1, [], ("NORMAL", "*OOH adsorbed, intact"),
               reuse={"OOH": "branch_panel/B_pull2.10"}),
    ]
    Es = -6000.0 * ev
    for c, tgt in zip(chains, ({"OH": 1.65, "O": 3.30, "OOH": 4.70}, {"OH": 2.10, "O": 3.60, "OOH": 2.80})):
        tag = f"{c['formula']}__s0_site0"
        for proj in ("atomic", "ortho"):
            _fake_out(tmp_path / "pilot" / tag / f"slab__{proj}.out", Es / ev)
            for sp in ("OH", "O", "OOH"):
                E_ad = tgt[sp] - ZPE_TS_CORRECTION[sp] + Es + reference_energy(sp, gas["H2O"]["E_eV"], gas["H2"]["E_eV"])
                assert delta_G(Es, E_ad, sp, gas["H2O"]["E_eV"], gas["H2"]["E_eV"]) == pytest.approx(tgt[sp])
                if c["reuse"].get(sp):
                    _fake_out(tmp_path / "panel" / f"B_pull2.10__{proj}.out", E_ad / ev)   # read from the panel dir
                else:
                    _fake_out(tmp_path / "pilot" / tag / f"{sp}__{proj}.out", E_ad / ev)
    r = hp.score_pilot(chains, tmp_path / "pilot", 0.164, 0.25, gas, band_eta_secondary=0.12955764753597102,
                       panel_dir=tmp_path / "panel")
    assert r["pending"] == []
    a, b = r["chains"]
    assert a["projectors"]["atomic"]["eta_DFT_V"] == pytest.approx(max(1.65, 3.30 - 1.65, 4.70 - 3.30, 4.92 - 4.70) - 1.23, abs=1e-6)
    assert a["projectors"]["atomic"]["band"] == "WITHIN" and a["projectors"]["atomic"]["band_secondary"] == "WITHIN"
    assert b["projectors"]["atomic"]["band"] == "WITHIN"
    assert "B__s0_site0/OOH__atomic (reused branch_panel/B_pull2.10__atomic)" in r["legs"]
    assert r["rank_order"]["atomic"]["identical"] is True and r["rank_order"]["atomic"]["kendall_tau"] == 1.0
    # remove one output -> pending, no rank order
    os.remove(tmp_path / "panel" / "B_pull2.10__ortho.out")
    r2 = hp.score_pilot(chains, tmp_path / "pilot", 0.164, 0.25, gas, panel_dir=tmp_path / "panel")
    assert r2["pending"] == ["B__s0_site0/OOH__ortho"]
    assert "identical" not in r2["rank_order"]["ortho"] and r2["rank_order"]["atomic"]["identical"]
    # desorbed OOH on chain B: AEM eta undefined, bridge lower bound printed, chain unscored, rank order not scored
    _fake_out(tmp_path / "panel" / "B_pull2.10__ortho.out", (2.80 - 0.40 + Es + reference_energy("OOH", gas["H2O"]["E_eV"], gas["H2"]["E_eV"])) / ev)
    chains[1]["desorbed"] = ["OOH"]
    chains[1]["integrity"]["OOH"] = {"screen_category": "DESORPTION + DISSOCIATION / H TRANSFER",
                                     "anomaly_class": "O2(g) in cell + H on slab O (H transferred)", "atoms": {}}
    r3 = hp.score_pilot(chains, tmp_path / "pilot", 0.164, 0.25, gas, panel_dir=tmp_path / "panel")
    pb = r3["chains"][1]["projectors"]["atomic"]
    assert pb["eta_scored"] is False and "eta_DFT_V" not in pb
    assert pb["verdict"].startswith("NOT AN *OOH STATE (O2(g) in cell + H on slab O (H transferred)): AEM eta UNDEFINED")
    assert pb["bridge"]["dE3_no_correction"] == pytest.approx(2.80 - 0.40, abs=1e-6)     # no 0.40 eV *OOH correction
    assert pb["bridge"]["eta_lower_bound_V"] == pytest.approx(max(2.10, 3.60 - 2.10, 2.40 - 3.60) - 1.23, abs=1e-6)
    assert pb["bridge"]["step_4"].startswith("UNMEASURED")
    assert pb["steps"]["OOH"]["verdict"].startswith("NOT AN *OOH STATE")
    assert r3["chains"][1]["MACE"]["eta_label"].startswith("AEM bookkeeping on a non-*OOH state")
    assert "NOT SCORED (1 scored chain(s)" in r3["rank_order"]["atomic"]["verdict"]


def test_main_exits_3_while_no_output_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(hp, "PANEL_DIR", tmp_path / "panel")
    monkeypatch.setattr(hp, "PILOT_DIR", tmp_path / "pilot")
    out = tmp_path / "readout.json"
    assert hp.main(["--json", str(out)]) == 3
    assert not out.exists()


def test_main_writes_json_once_every_leg_is_terminal(tmp_path, monkeypatch):
    """Every leg NOT CONVERGED (no '!' line anywhere): terminal, so the JSON is written with
    NOT CONVERGED rows and no number, instead of a PENDING deadlock."""
    panel_dir = tmp_path / "panel"
    pilot_dir = tmp_path / "pilot"
    for label in ("equiatomic_pull2.10", "equiatomic_builder", "leader_builder", "leader_pull2.10", "leader_pull1.70"):
        for proj in ("atomic", "ortho"):
            _fake_out(panel_dir / f"{label}__{proj}.out", -1.0, iters=300, notconv=True)
    for chain in ("Fe25Co25Ni25Cr25__s2_site0", "Ni31Cr29Cu5Mn35__s0_site0"):
        for st in ("slab", "OH", "O"):
            for proj in ("atomic", "ortho"):
                _fake_out(pilot_dir / chain / f"{st}__{proj}.out", -1.0, iters=300, notconv=True)
    monkeypatch.setattr(hp, "PANEL_DIR", panel_dir)
    monkeypatch.setattr(hp, "PILOT_DIR", pilot_dir)
    out = tmp_path / "readout.json"
    assert hp.main(["--json", str(out)]) == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["panel"]["pending"] == [] and doc["pilot"]["pending"] == []
    assert all(v["verdict"] == "NOT CONVERGED (no number)" for p in doc["panel"]["pairs"] for v in p["projectors"].values())
    assert all(v["verdict"] == "NOT CONVERGED (no number)" for c in doc["pilot"]["chains"] for v in c["projectors"].values())
