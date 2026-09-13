#!/usr/bin/env python3
"""Verify authorized AI core authorship and explicit disclosure, not disjointness.

The historical check_disjoint.py assertion remains unchanged. This check proves
only that the recorded authorization is intact and every existing core Python
file is explicitly named in the declared provenance record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
POLICY = ".github/ci/core-authorship.json"
CORE_FILES = ("census.py", "classify.py", "direction.py", "cli.py")
TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\\*+-]*")


def confined_file(root, value):
    if not isinstance(value, str) or not value:
        raise ValueError("policy must name a nonempty repository-relative file")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("policy file paths must stay within the repository")
    resolved = (root / relative).resolve()
    resolved.relative_to(root)
    if not resolved.is_file():
        raise ValueError("required file missing: %s" % value)
    return resolved


def check(root=ROOT, policy=POLICY):
    root = Path(root).resolve()
    result = {"assertion": "authorized AI core authorship is explicitly disclosed",
              "status": "FAIL", "policy": str(policy), "core_paths": [],
              "undisclosed": []}
    try:
        config = json.loads(confined_file(root, str(policy)).read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("authorship policy is not an object")
        if config.get("schema") != "silentgate-authorship-v1":
            raise ValueError("unrecognized authorship policy schema")
        if config.get("mode") != "ai-assisted-authorized":
            raise ValueError("AI-assisted authorship is not authorized by this policy")
        authorization = confined_file(root, config.get("authorization"))
        digest = hashlib.sha256(authorization.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if digest != config.get("authorization_sha256"):
            raise ValueError("authorization document SHA256 mismatch")
        if not authorization.read_text(encoding="utf-8").strip():
            raise ValueError("authorization document is empty")
        provenance = confined_file(root, config.get("provenance"))
        text = provenance.read_text(encoding="utf-8")
        tokens = {token.replace("\\", "/").rstrip(".")
                  for token in TOKEN_RE.findall(text)}
        core = root / "silentgate"
        required = [core / name for name in CORE_FILES]
        readers = list((core / "readers").rglob("*.py")) if (core / "readers").is_dir() else []
        if not readers or any(not path.is_file() or path.stat().st_size == 0 for path in required):
            raise ValueError("core incomplete: four modules and Python readers are required")
        paths = sorted({path.relative_to(root).as_posix() for path in list(core.glob("*.py")) + readers})
        result["core_paths"] = paths
        result["undisclosed"] = [path for path in paths if path not in tokens]
        if result["undisclosed"]:
            raise ValueError("core files not explicitly disclosed: " + ", ".join(result["undisclosed"]))
        result.update(status="PASS", mode=config["mode"],
                      authorization=config["authorization"], authorization_sha256=digest,
                      provenance=config["provenance"],
                      detail="Authorized AI-assisted core; %d core Python files explicitly disclosed. "
                             "The historical disjointness assertion is not satisfied by this check." % len(paths))
    except (OSError, ValueError, TypeError) as exc:
        result["reason"] = str(exc)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--policy", default=POLICY)
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    result = check(args.root, args.policy)
    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("CORE AUTHORSHIP: %s -- %s" % (result["status"], result.get("detail", result.get("reason"))))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
