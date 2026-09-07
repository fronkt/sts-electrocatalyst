"""Create every manifest of the 2026-09-06 site-integrity census (docs/91) and hash them.

Each box manifest is produced by the existing CLI, ``screen_diagnostic.py prepare``, run as a
subprocess with the exact fractions taken from the tracked LF source rows; the endmember
manifest is produced by site_census_endmember_manifest.py. Existing manifests are never
overwritten (write_json_new opens with mode 'x'); rerunning after a partial build fills in
the missing ones only. MANIFESTS.sha256 lists the LF sha256 of every manifest in queue order;
it is written once, left alone when it already matches, and refused (unless --rehash) when
it differs from the manifests on disk.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from scripts import site_census_plan as plan  # noqa: E402

PREPARE = ROOT / "src/scripts/screen_diagnostic.py"
ENDMEMBER = ROOT / "src/scripts/site_census_endmember_manifest.py"


def sha256_lf(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def prepare_cli(python, formula, tag, seeds, out):
    cmd = [python, str(PREPARE), "prepare", "--source", str(plan.BOX_SOURCE),
           "--formula", formula, "--model-file", str(plan.model_path(tag)),
           "--seeds", ",".join(str(s) for s in seeds), "--n-sites", "4",
           "--steps", "300", "--fmax", "0.05", "--mode", "diagnostic", "--out", str(out)]
    return cmd


def build(python, only=None, dry_run=False):
    plan.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    commands = []
    for stem in plan.expected_stems():
        if only and stem not in only:
            continue
        out = plan.manifest_path(stem)
        info = plan.parse_stem(stem)
        if info["arm"] == "ENDMEMBER-2x2":
            cmd = [python, str(ENDMEMBER), "--source", str(plan.VALIDATE_SOURCE),
                   "--model-file", str(plan.model_path("mpa0")), "--out", str(out)]
        elif info["arm"] == "CENSUS-3":
            lo, hi = info["block"]
            cmd = prepare_cli(python, info["formula"], "mpa0", range(lo, hi + 1), out)
        else:
            cmd = prepare_cli(python, info["formula"], info["tag"], (0, 1, 2), out)
        commands.append((stem, out, cmd))
    made, skipped = [], []
    for stem, out, cmd in commands:
        if out.exists():
            skipped.append(stem)
            continue
        if dry_run:
            print(" ".join(cmd))
            continue
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"{stem}: prepare failed\n{proc.stdout}\n{proc.stderr}")
        made.append(stem)
        print(stem, proc.stdout.strip())
    return made, skipped


def write_hashes(rehash=False):
    """Write MANIFESTS.sha256 once. An existing list that already matches the manifests is
    left untouched; one that differs is refused unless `rehash` is given, so the hash list
    of the blind boundary cannot be rewritten by an ordinary rerun."""
    stems = plan.queue_order([p.stem for p in plan.MANIFEST_DIR.glob("*.json")])
    lines = [f"{sha256_lf(plan.manifest_path(s))}  manifests/{s}.json" for s in stems]
    text = "\n".join(lines) + "\n"
    if plan.MANIFEST_HASHES.exists():
        existing = plan.MANIFEST_HASHES.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
        if existing == text:
            return lines, "unchanged"
        if not rehash:
            raise FileExistsError(f"{plan.MANIFEST_HASHES} differs from the manifests on disk; "
                                  "pass --rehash to rewrite it deliberately")
    plan.MANIFEST_HASHES.write_text(text, encoding="utf-8", newline="\n")
    return lines, "written"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--only", action="append", help="build only these manifest stems")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-hashes", action="store_true")
    parser.add_argument("--rehash", action="store_true",
                        help="rewrite MANIFESTS.sha256 even when it differs from the manifests")
    args = parser.parse_args(argv)
    made, skipped = build(args.python, only=args.only, dry_run=args.dry_run)
    print(f"made {len(made)}, already present {len(skipped)}")
    if not args.dry_run and not args.no_hashes:
        lines, action = write_hashes(rehash=args.rehash)
        print(f"{len(lines)} hashes {action} -> {plan.MANIFEST_HASHES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
