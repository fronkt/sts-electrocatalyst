"""P-BUILDER atomate gate: evaluation helpers and the recorded result (no network)."""
import copy
import io
import json
import tarfile

from s2.p_builder import atomate_gate as g
from s2.p_builder.registered import PRESTATE_DIR

REC = json.loads((PRESTATE_DIR / "atomate_gate.json").read_text(encoding="utf-8"))

ONE_LINE = '''class MPSurfaceSet(MVLSlabSet):
    @property
    def incar(self):
        # Should give better forces for optimization
        incar_config = {"EDIFFG": -0.05, "ENAUG": 4000, "IBRION": 1,
                        "POTIM": 1.0, "LDAU": ldau, "EDIFF": 1e-5, "ISYM": 0}
        incar.update(incar_config)


def other():
    pass
'''

MULTI_LINE = '''class MPSurfaceSet(MVLSlabSet):
    def incar(self):
        # Should give better forces for optimization
        incar_config = {
            "EDIFFG": -0.05,
            "EDIFF": 1e-5,
            "ISYM": 0,
        }
'''

NOT_GOVERNED = '''class MPSurfaceSet(MVLSlabSet):
    def incar(self):
        # Should give better forces for optimization
        incar_config = {"EDIFFG": -0.05}

        other = {"ISYM": 0}
'''

OLD_SETS = '''MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


class VaspInputSet(six.with_metaclass(abc.ABCMeta, MSONable)):
    pass


class DictSet(VaspInputSet):
    def incar(self):
        return 1


class MPRelaxSet(DictSet):
    CONFIG = loadfn(os.path.join(MODULE_DIR, "MPRelaxSet.yaml"))


class MPNonSCFSet(MPRelaxSet):
    x = {"ISYM": 0}


class MVLSlabSet(MPRelaxSet):
    def incar(self):
        return 2
'''

NEW_SETS = '''def _load_yaml_config(fname):
    config = loadfn(os.path.join(MODULE_DIR, "%s.yaml" % fname))
    config["INCAR"].update(loadfn(os.path.join(MODULE_DIR,
                                               "VASPIncarBase.yaml")))
    return config


class DictSet(VaspInputSet):
    pass


class MPRelaxSet(DictSet):
    CONFIG = _load_yaml_config("MPRelaxSet")


class MVLSlabSet(MPRelaxSet):
    pass
'''


def test_isym_under_comment_forms():
    r = g.isym_under_comment(ONE_LINE, "MPSurfaceSet")
    assert r["ok"] and r["comment_line"]["line"] == 4 and r["isym_line"]["line"] == 6
    assert r["class_span"] == (1, 9)
    m = g.isym_under_comment(MULTI_LINE, "MPSurfaceSet")
    assert m["ok"] and m["isym_line"]["line"] == 7
    assert not g.isym_under_comment(NOT_GOVERNED, "MPSurfaceSet")["ok"]
    assert not g.isym_under_comment(ONE_LINE, "MPSurfaceInputSet")["ok"]


def test_class_base_and_counts():
    assert g.class_base(ONE_LINE, "MPSurfaceSet") == "MVLSlabSet"
    assert g.count_isym(ONE_LINE) == 1 and g.count_isym("ISYMX = 1") == 0


def test_chain_and_yaml_discovery_both_loader_styles():
    assert g.class_chain(OLD_SETS, "MVLSlabSet") == ["MVLSlabSet", "MPRelaxSet", "DictSet", "VaspInputSet"]
    assert g.chain_yaml_names(OLD_SETS) == ["MPRelaxSet"]
    assert g.chain_yaml_names(NEW_SETS) == ["MPRelaxSet", "VASPIncarBase"]
    ok = g.mvlslabset_chain_isym(OLD_SETS, {"MPRelaxSet": "INCAR:\n  EDIFF: 1e-5\n"})
    assert ok["ok"] and ok["isym_lines_per_class"]["MVLSlabSet"] == 0  # MPNonSCFSet's ISYM is outside the chain
    bad_yaml = g.mvlslabset_chain_isym(OLD_SETS, {"MPRelaxSet": "INCAR:\n  ISYM: 0\n"})
    missing = g.mvlslabset_chain_isym(NEW_SETS, {"MPRelaxSet": "INCAR: {}\n"})
    parent = g.mvlslabset_chain_isym(OLD_SETS, {"MPRelaxSet": "PARENT: Base\n", "Base": "ISYM: 2\n"})
    assert not bad_yaml["ok"] and not missing["ok"] and not parent["ok"]


def test_setup_py_spec_and_sdist_member_extraction():
    line = "        install_requires=['FireWorks>=1.4.0', 'pymatgen>=4.7.1',"
    assert g.setup_py_pymatgen_spec(line) == [dict(line=1, text=line, spec=">=4.7.1")]
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, data in [("pymatgen-1.0/pymatgen/io/vasp/sets.py", b"top"),
                           ("pymatgen-1.0/test_files/pymatgen/io/vasp/sets.py", b"nested")]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    got = g._sdist_members(buf.getvalue(), "pymatgen-1.0.tar.gz", {"sets": "pymatgen/io/vasp/sets.py"})
    assert got == {"sets": "top"}


def test_git_blob_sha1_matches_git():
    assert g.git_blob_sha1(b"hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_vasp_default_parser():
    page = ('<script>x</script><p>ISYM = -1 | 0 | 1 | 2 | 3</p><p>Default: <b>ISYM</b> = 1 if VASP runs with '
            'USPPs</p><p>= 3 if LHFCALC =.TRUE.</p><p>= 2 else</p><p>Description: ...</p>'
            '"wgCurRevisionId":26986,')
    d = g.vasp_isym_default(page)
    assert d["default_else"] == 2 and d["revision_id"] == 26986


def test_recorded_gate_re_evaluates_identically():
    assert json.loads(json.dumps(g.evaluate(REC["sources"], REC["checked_utc"]))) == REC["checks"]
    assert REC["checks"]["GATE"]["passed"] is True
    src = REC["sources"]
    assert src["commit_isym"]["sha"].startswith("a7d5f316") and src["commit_2017"]["sha"].startswith("d2742a3b")
    assert src["adsorption_py_at_isym_commit"]["blob_sha_match"] and src["adsorption_py_at_2017_commit"]["blob_sha_match"]


def test_scope_checks_recorded():
    ch = REC["checks"]
    h = ch["7_isym0_every_default_branch_version_since_a7d5f316"]
    assert h["ok"] and h["detail"]["n_versions"] == 11 and h["detail"]["oldest"].startswith("a7d5f316")
    assert all(v["ok"] for v in h["detail"]["versions"]) and h["detail"]["head_blob_equals_newest_listed"]
    r = ch["4b_MVLSlabSet_chain_no_ISYM_every_admitted_release_before_a7d5f316"]
    assert r["ok"] and r["detail"]["specifier"] == ">=4.7.1" and r["detail"]["setup_py_line"][0]["line"] == 23
    assert r["detail"]["n_releases"] == r["detail"]["n_sdist_sha256_match"] == r["detail"]["n_no_isym"] == 43
    st = ch["DATED_STATEMENT"]
    assert st["since_wording_supported"] and st["all_admitted_releases_checked"]
    assert "every version" in st["text"][0] and "43 pymatgen releases" in st["text"][1]


def test_dated_statement_narrows_when_a_scope_check_fails():
    src = copy.deepcopy(REC["sources"])
    src["default_branch_history_since_isym_commit"]["listed_newest_first"][3]["isym_under_comment_ok"] = False
    src["pymatgen_releases_admitted_before_isym_commit"]["releases"][5]["ok"] = False
    ch = g.evaluate(src, REC["checked_utc"])
    assert ch["GATE"]["passed"] is True
    st = ch["DATED_STATEMENT"]
    assert not st["since_wording_supported"] and not st["all_admitted_releases_checked"]
    assert "versions in between were not established" in st["text"][0]
    assert "other releases admitted by setup.py were not established" in st["text"][1]
