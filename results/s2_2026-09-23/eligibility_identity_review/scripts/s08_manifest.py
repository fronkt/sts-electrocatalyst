"""Write manifest.json: sha256 and size of every file in this review directory."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
files = []
for p in sorted(ROOT.rglob("*")):
    if p.is_file() and p.name != "manifest.json" and "__pycache__" not in p.parts:
        files.append({"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size})
(ROOT / "manifest.json").write_text(json.dumps({"files": files}, indent=0), encoding="utf-8")
print(len(files), sum(f["bytes"] for f in files))
