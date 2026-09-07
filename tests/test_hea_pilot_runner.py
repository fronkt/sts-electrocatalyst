"""Pilot shell failures with fake MPI/QE; never submit or run DFT.

Windows uses Git Bash only (or HEA_TEST_BASH), never the WSL shim. All mock
executables and scientific artifacts live in pytest's temporary directory.
"""
from pathlib import Path
import os
import shutil
import subprocess
import textwrap
import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "anvil/53_hea_pilot.slurm"
DIRECTORY = "hea/controls_2026-09-07"
JOB = "hc__leader_builder__atomic__baseline"
OTHER_JOB = "hc__leader_pull2.10__atomic__baseline"


def _bash():
    explicit = os.environ.get("HEA_TEST_BASH")
    if explicit:
        if not Path(explicit).is_file(): pytest.fail("HEA_TEST_BASH does not name a file")
        return explicit
    if os.name == "nt":
        choices = [Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe",
                   Path(os.environ.get("LOCALAPPDATA", "C:/Users/Default/AppData/Local")) / "Programs/Git/bin/bash.exe"]
        executable = next((str(p) for p in choices if p.is_file()), None)
    else:
        executable = shutil.which("bash")
    if executable is None: pytest.skip("bash unavailable; set HEA_TEST_BASH to Git Bash on Windows")
    return executable


def _shell_path(path):
    value = Path(path).resolve().as_posix()
    if os.name == "nt":
        if len(value) < 3 or value[1:3] != ":/": raise ValueError("tests require a local Windows drive")
        return "/" + value[0].lower() + value[2:]
    return value


def _write(path, text, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8", newline="\n")
    if executable: path.chmod(0o755)


@pytest.fixture
def pilot(tmp_path):
    executable = _bash()
    runs, prefix = tmp_path / "runs", tmp_path / "qe"
    directory = runs / DIRECTORY
    directory.mkdir(parents=True)
    pseudo = tmp_path / "pseudo"
    pseudo.mkdir()
    manifest = tmp_path / "pilot.txt"
    rows = f"{DIRECTORY} {JOB} .in 8\n{DIRECTORY} {OTHER_JOB} .in 8\n"
    manifest.write_text(rows, encoding="utf-8", newline="\n")
    Path(str(manifest) + ".lines").write_text(rows, encoding="utf-8", newline="\n")
    for job in (JOB, OTHER_JOB):
        _write(directory / (job + ".in"), f"""
            &CONTROL
              calculation = 'scf'
              prefix = '{job}'
              outdir = './unused'
              pseudo_dir = './unused-pseudo'
              max_seconds = 13200
              tprnfor = .true.
            /
            &SYSTEM
              nat=1
              ntyp=1
            /
            ATOMIC_SPECIES
              H 1.008 H.UPF
            ATOMIC_POSITIONS angstrom
              H 0 0 0
            K_POINTS gamma
        """)
    _write(prefix / "bin/mpirun", r"""
        #!/bin/bash
        set -eu
        printf '%s\n' "$*" >> "$MOCK_MPI_LOG"
        while [ "$#" -gt 0 ]; do
          case "$1" in
            --oversubscribe) shift ;;
            -np|-n) shift 2 ;;
            pw.x|projwfc.x) exec "$@" ;;
            *) echo "Unexpected mock MPI argument: $1" >&2; exit 97 ;;
          esac
        done
        exit 98
    """, executable=True)
    _write(prefix / "bin/pw.x", r"""
        #!/bin/bash
        set -eu
        inp=''
        while [ "$#" -gt 0 ]; do
          case "$1" in
            -in) inp=$2; shift 2 ;;
            -nk) shift 2 ;;
            *) exit 96 ;;
          esac
        done
        [ -f "$inp" ] || exit 95
        prefix=$(sed -n "s/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        scratch=$(sed -n "s/^[[:space:]]*outdir[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        [ -n "$prefix" ] && [ -n "$scratch" ] || exit 94
        mkdir -p "$scratch/$prefix.save"
        printf '%s\n' 'mock metadata' > "$scratch/$prefix.save/data-file-schema.xml"
        printf '%s\n' 'mock density' > "$scratch/$prefix.save/charge-density.dat"
        printf '%s\n' 'irreplaceable mock wavefunction' > "$scratch/$prefix.save/wfc1.dat"
        printf '%s\n' "$scratch/$prefix.save/wfc1.dat" > "$MOCK_WFC_RECORD"
        if [ "$MOCK_SCF_MODE" != missing_energy ]; then echo '! total energy = -2.0 Ry'; fi
        case "$MOCK_SCF_MODE" in
          nonconverged) echo 'convergence NOT achieved'; echo 'JOB DONE.'; exit 0 ;;
          userstop) echo 'Program stopped by user request'; echo 'JOB DONE.'; exit 0 ;;
          no_convergence) echo 'JOB DONE.'; exit 0 ;;
        esac
        echo 'convergence has been achieved in 3 iterations'
        echo 'JOB DONE.'
        [ "$MOCK_SCF_MODE" != bad_rc ] || exit 11
    """, executable=True)
    _write(prefix / "bin/projwfc.x", r"""
        #!/bin/bash
        set -eu
        wfc=$(cat "$MOCK_WFC_RECORD")
        [ -f "$wfc" ] || { echo 'wavefunction already lost'; exit 93; }
        printf '%s\n' 'projection saw intact wavefunction' > "$MOCK_PROJECTION_RECORD"
        if [ "$MOCK_PROJ_MODE" != no_lowdin ]; then echo 'Lowdin Charges:'; fi
        case "$MOCK_PROJ_MODE" in
          error_marker) echo 'Error in routine mock_projection'; echo 'JOB DONE.'; exit 0 ;;
          no_done) exit 0 ;;
        esac
        echo 'JOB DONE.'
        [ "$MOCK_PROJ_MODE" != bad_rc ] || exit 12
    """, executable=True)
    env = os.environ.copy()
    env.update(MANIFEST=_shell_path(manifest), RUNS=_shell_path(runs), QE_PREFIX=_shell_path(prefix),
               PSEUDO_DIR=_shell_path(pseudo), NP="128", SLURM_ARRAY_TASK_ID="1", SLURM_JOB_ID="123456",
               SLURM_CPUS_ON_NODE="128", MOCK_MPI_LOG=_shell_path(tmp_path / "mpi.log"),
               MOCK_WFC_RECORD=_shell_path(tmp_path / "wavefunction.txt"),
               MOCK_PROJECTION_RECORD=_shell_path(tmp_path / "projection.txt"),
               MOCK_SCF_MODE="success", MOCK_PROJ_MODE="success")
    return dict(root=tmp_path, directory=directory, prefix=prefix, manifest=manifest, env=env,
                executable=executable, scratch=directory / ("tmp_" + JOB), save=directory / "dens" / (JOB + ".save"))


def run_pilot(pilot, **env):
    return subprocess.run([pilot["executable"], _shell_path(RUNNER)], cwd=pilot["root"],
                          env=dict(pilot["env"], **env), text=True, capture_output=True, timeout=20,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def assert_launches(pilot, programs):
    log = pilot["root"] / "mpi.log"
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    assert len(lines) == len(programs), lines
    for line, program in zip(lines, programs): assert f"-np 128 {program} -nk 8 -in " in line


def assert_scratch_preserved(pilot):
    saved = pilot["scratch"] / (JOB + ".save")
    assert (saved / "wfc1.dat").read_text().strip() == "irreplaceable mock wavefunction"
    assert (saved / "data-file-schema.xml").read_text().strip() == "mock metadata"
    assert (saved / "charge-density.dat").read_text().strip() == "mock density"
    assert not pilot["save"].exists()


@pytest.mark.parametrize("mode", ["bad_rc", "nonconverged", "userstop", "no_convergence", "missing_energy"])
def test_scf_failure_stops_projection_and_preserves_wavefunctions(pilot, mode):
    result = run_pilot(pilot, MOCK_SCF_MODE=mode)
    assert result.returncode != 0, result.stdout + result.stderr
    assert_launches(pilot, ["pw.x"])
    assert_scratch_preserved(pilot)
    assert not (pilot["root"] / "projection.txt").exists()
    assert not (pilot["directory"] / (JOB + ".projwfc.out")).exists()


@pytest.mark.parametrize("mode", ["bad_rc", "no_lowdin", "error_marker", "no_done"])
def test_projection_failure_keeps_scratch_for_repair(pilot, mode):
    result = run_pilot(pilot, MOCK_PROJ_MODE=mode)
    assert result.returncode != 0, result.stdout + result.stderr
    assert_launches(pilot, ["pw.x", "projwfc.x"])
    assert_scratch_preserved(pilot)
    assert (pilot["directory"] / (JOB + ".out")).is_file()
    assert (pilot["directory"] / (JOB + ".projwfc.out")).is_file()


def test_success_projects_before_wavefunction_cleanup_and_retains_density(pilot):
    result = run_pilot(pilot)
    assert result.returncode == 0, result.stdout + result.stderr
    assert_launches(pilot, ["pw.x", "projwfc.x"])
    assert (pilot["root"] / "projection.txt").read_text().strip() == "projection saw intact wavefunction"
    assert not pilot["scratch"].exists()
    assert (pilot["save"] / "data-file-schema.xml").read_text().strip() == "mock metadata"
    assert (pilot["save"] / "charge-density.dat").read_text().strip() == "mock density"
    assert not list(pilot["save"].glob("wfc*"))
    assert "Lowdin Charges" in (pilot["directory"] / (JOB + ".projwfc.out")).read_text()


@pytest.mark.parametrize("suffix", [".out", ".projwfc.out", ".run.in", ".projwfc.in"])
def test_preexisting_output_or_runtime_input_is_refused_without_touching_it(pilot, suffix):
    artifact = pilot["directory"] / (JOB + suffix)
    artifact.write_bytes(b"retained incomplete artifact, no success marker\n")
    result = run_pilot(pilot)
    assert result.returncode != 0
    assert artifact.read_bytes() == b"retained incomplete artifact, no success marker\n"
    assert_launches(pilot, [])
    assert not pilot["scratch"].exists()


@pytest.mark.parametrize("kind", ["scratch", "save"])
def test_existing_scratch_or_retained_density_is_never_erased(pilot, kind):
    existing = pilot[kind]
    existing.mkdir(parents=True)
    sentinel = existing / "keep-this.bin"
    sentinel.write_bytes(b"must survive")
    result = run_pilot(pilot)
    assert result.returncode != 0
    assert sentinel.read_bytes() == b"must survive"
    assert_launches(pilot, [])
    assert not (pilot["directory"] / (JOB + ".out")).exists()


@pytest.mark.parametrize("np_value", ["0", "-8", "abc", "127", "8.0"])
def test_invalid_np_refused_before_work(pilot, np_value):
    result = run_pilot(pilot, NP=np_value)
    assert result.returncode != 0
    assert_launches(pilot, [])
    assert not pilot["scratch"].exists()


@pytest.mark.parametrize("nk_value", ["0", "-8", "abc", "7", "8.0"])
def test_invalid_or_unlicensed_nk_refused_before_work(pilot, nk_value):
    Path(str(pilot["manifest"]) + ".lines").write_text(f"{DIRECTORY} {JOB} .in {nk_value}\n{DIRECTORY} {OTHER_JOB} .in 8\n", encoding="utf-8", newline="\n")
    result = run_pilot(pilot)
    assert result.returncode != 0
    assert_launches(pilot, [])
    assert not pilot["scratch"].exists()


def test_density_copy_failure_preserves_repairable_scratch(pilot):
    _write(pilot["prefix"] / "bin/cp", "#!/bin/bash\nexit 19", executable=True)
    result = run_pilot(pilot)
    assert result.returncode != 0, result.stdout + result.stderr
    assert_launches(pilot, ["pw.x", "projwfc.x"])
    assert_scratch_preserved(pilot)


def test_pilot_has_four_hour_scheduler_cap():
    lines = RUNNER.read_text(encoding="utf-8").splitlines()
    times = [line.split()[-1] for line in lines if line.startswith("#SBATCH -t ")]
    assert times in (["04:00:00"], ["4:00:00"])
