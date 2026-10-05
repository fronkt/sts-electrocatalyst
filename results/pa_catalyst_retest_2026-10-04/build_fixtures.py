"""Copy real QE 7.5 outputs into tests/fixtures/qe75_real as deterministic gzip files.

Originals are only read, never moved or changed.  manifest.json records, for every
fixture, the repo-relative original, its byte length and SHA-256 (of the uncompressed
bytes), so a test can prove the fixture decompresses to exactly the original.
Refuses to overwrite an existing fixture directory.
"""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "tests/fixtures/qe75_real"
MIRROR = ROOT / "results/pa_catalyst_trial_readout_2026-10-04/mirror/trial_results"
PPROJ6 = ROOT / "runs/a0/pproj6"
FRESH = ROOT / "results/lowtail_low_state_restart_2026-09-22/checked2/outputs/Cu8Cr23Mn35Co34__s20_site2/segments"
TINY = ROOT / "results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw/tiny_results"

README = """Real QE 7.5 output fixtures for tests/test_pa_qe_adapter_v2_real.py.

Every file is a deterministic gzip (mtime 0) copy of an original that is left in place;
manifest.json holds the original path, byte length and SHA-256 of the uncompressed bytes.

control/      the control call of Slurm job 21034683 (72-atom Hubbard relax, 128 MPI, clean stop
              after three SCF evaluations): deck, stdout, stderr, process receipt, XML, .bfgs,
              and the five pinned UPFs it consumed.
pproj6/       19 real calculation='scf' Hubbard (ortho-atomic) XML files with their decks and
              logs (runs/a0/pproj6; untracked in the repository because of the **/dens/ ignore).
fresh_logs/   two real 72-atom 128-rank calculation='scf' logs from the September checked run
              (one converged, one stalled at SCF iteration 127), stdout and stderr merged.
tiny_h2/      four arms of the real one-process H2 restart probe (QE 7.5, serial): the clean-stop
              candidate, the continuous run, the resumed run (restart_mode='restart') and the
              from-scratch negative control; tracked originals under results/s2_2026-09-25/.
"""


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def put(manifest, group, name, source):
    raw = Path(source).read_bytes()
    target = DEST / group / (name + ".gz")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=handle, mtime=0, compresslevel=9) as stream:
            stream.write(raw)
    manifest.append({"fixture": target.relative_to(DEST).as_posix(),
                     "source": Path(source).resolve().relative_to(ROOT).as_posix(),
                     "bytes": len(raw), "sha256": digest(raw)})


def main():
    if DEST.exists():
        raise SystemExit("fixture directory exists; refusing to overwrite")
    DEST.mkdir(parents=True)
    manifest = []
    control = MIRROR / "control"
    for name in ("input.in", "stdout.log", "stderr.log", "process_receipt.json"):
        put(manifest, "control", name, control / name)
    put(manifest, "control", "data-file-schema.xml", control / "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml")
    put(manifest, "control", "slab_c5low__pa_boundary.bfgs", control / "outdir/slab_c5low__pa_boundary.bfgs")
    for upf in sorted((MIRROR / "common_pseudo").iterdir()):
        put(manifest, "control/common_pseudo", upf.name, upf)
    for xml in sorted(PPROJ6.rglob("data-file-schema.xml")):
        element, case = xml.parts[-4], xml.parent.name[:-5]
        base = PPROJ6 / element
        stem = element + "__" + case
        put(manifest, "pproj6", stem + ".xml", xml)
        put(manifest, "pproj6", stem + ".in", base / (case + ".in"))
        put(manifest, "pproj6", stem + ".out", base / (case + ".out"))
    for name in ("slab_c5low__checked.fresh3.out", "slab_c5low__checked.fresh10.out"):
        put(manifest, "fresh_logs", name, FRESH / name)
    for arm in ("candidate-stop", "continuous", "resumed", "negative-fresh"):
        directory = TINY / arm
        for name in ("input.in", "stdout.log", "stderr.log", "receipt.json"):
            put(manifest, "tiny_h2/" + arm, name, directory / name)
        put(manifest, "tiny_h2/" + arm, "data-file-schema.xml", directory / "scratch/h2_probe.save/data-file-schema.xml")
    put(manifest, "tiny_h2/candidate-stop", "h2_probe.bfgs", TINY / "candidate-stop/scratch/h2_probe.bfgs")
    put(manifest, "tiny_h2/candidate-stop", "H.pbe-rrkjus_psl.1.0.0.UPF", TINY / "candidate-stop/H.pbe-rrkjus_psl.1.0.0.UPF")
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8", newline="\n")
    (DEST / "README.txt").write_text(README, encoding="utf-8", newline="\n")
    # Binary and verbatim: keep git from rewriting any byte on any platform.
    (DEST / ".gitattributes").write_text("* -text\n", encoding="utf-8", newline="\n")
    total = sum((DEST / row["fixture"]).stat().st_size for row in manifest)
    print(json.dumps({"fixtures": len(manifest), "compressed_bytes": total}))


if __name__ == "__main__":
    main()
