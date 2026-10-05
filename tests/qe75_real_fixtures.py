"""Shared access to the real QE 7.5 output fixtures (tests/fixtures/qe75_real)."""
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/qe75_real"
CATALYST = {"nprocs": 128, "nthreads": 1, "ntasks": 1, "nbgrp": 1, "npool": 8, "ndiag": 16}
SERIAL = {key: 1 for key in CATALYST}
LOGGED_CONTROL_UPF_DIR = "/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03/trial_results/common_pseudo/"
LOGGED_TINY_DIR = "/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/tiny_results/candidate-stop/"
TINY_UPF_SHA256 = "27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962"


def manifest():
    return json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))


def materialize(destination):
    """Decompress every fixture into destination, proving each equals its recorded original."""
    destination = Path(destination)
    for row in manifest():
        raw = gzip.decompress((FIXTURES / row["fixture"]).read_bytes())
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise AssertionError("fixture differs from its recorded original: " + row["fixture"])
        target = destination / row["fixture"][:-3]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return destination


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def xml_vocabulary(paths):
    """Every element tag and (tag, attribute) pair that occurs in the given real XML files."""
    tags, attributes = set(), set()
    for path in paths:
        for node in ET.parse(str(path)).getroot().iter():
            tags.add(tag(node))
            attributes.update((tag(node), key.rsplit("}", 1)[-1]) for key in node.attrib)
    return tags, attributes


def real_xml_paths(root):
    root = Path(root)
    return sorted(root.rglob("data-file-schema.xml")) + sorted((root / "pproj6").glob("*.xml"))


def pinned_control_upfs(root):
    """{filename: sha256} of the five UPFs the control call consumed, and the log-path map."""
    directory = Path(root) / "control/common_pseudo"
    pins = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(directory.iterdir())}
    return pins, {LOGGED_CONTROL_UPF_DIR + name: str(directory / name) for name in pins}


def control_call(root, module):
    """Positional and keyword arguments that read the real control call through module.read_qe_arm."""
    directory = Path(root) / "control"
    expected = module.parse_deck(directory / "input.in")
    expected["upf_pins"], expected["upf_read_path_map"] = pinned_control_upfs(root)
    receipt = json.loads((directory / "process_receipt.json").read_text(encoding="utf-8"))
    args = (directory / "input.in", directory / "stdout.log", directory / "stderr.log",
            directory / "data-file-schema.xml", receipt)
    kwargs = dict(expected_settings=expected, expected_parallel=CATALYST,
                  expected_exit="clean_stop", expected_evaluations=3)
    return args, kwargs
