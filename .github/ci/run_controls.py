#!/usr/bin/env python3
"""The A9.2 status face: run the registered controls and print their status.

Registered requirements this implements:

  :1868  "Both controls live in CI and re-run on every commit; the amendment
          records their status at the moment each audit number is generated."
  :1868  "Every census table, figure and CSV written by silentgate carries the
          commit hash and the control status at that commit on its face."
  :1868  "Control results are recorded with the status vocabulary
          MEASURED / BOUNDED / TRANSFERRED / NOT MEASURED."
  :1840  the disjointness assertion's status is printed "next to the controls".
  :1868  "a commit on which the OC20 job did not execute is not green."
  :1834  the tag-free adsorbate rule "must reproduce the tag counts 20/20 on the
          production runs, and that agreement is printed by CI."

WHAT THIS FILE IS NOT
---------------------
It is not a reader. It never opens a pw.x output. It invokes the entrant's
`silentgate` through the command declared in silentgate-invocation.toml, reads
back JSON, and compares it against thresholds transcribed from docs/43. Every
parse of a force block, header or deck happens inside the core, where the
registered authorship rule puts it (:1840).

While silentgate-invocation.toml is blank -- which it is until the entrant
writes the core -- every control reports NOT MEASURED and the build is not
green. That is the registered state of a gate whose instrument does not exist,
not a defect in this script.

AUTHORSHIP: written by AI as "the CI workflow" under the A9.1 :1840 permitted
list.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

MEASURED = "MEASURED"
NOT_MEASURED = "NOT MEASURED"

# Adsorbate counts implied by this repo's legacy filename tags. Used ONLY for the
# :1834 agreement print -- the registered identification rule is tag-free and
# lives in the core; the tag is "used only as a consistency check".
TAG_COUNTS = (("s0_OOH", 3), ("s0_OH", 2), ("s0_O", 1))


def load_toml(path):
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        try:
            import tomli as tomllib  # type: ignore
        except ModuleNotFoundError:
            raise SystemExit(
                "FATAL: need Python 3.11+ (tomllib) or the `tomli` package to read %s"
                % path
            )
    with open(path, "rb") as fh:
        return tomllib.load(fh)


# The registered population sizes, docs/43:1864. Asserted, not assumed: without
# this, deleting the 11 nosym_present lines from populations.txt would make the
# face print "force-only LOCKED 0/11" as MEASURED/PASS with zero runs scored --
# a green gate over an empty set, which is the fail-open A9.2 exists to prevent.
REGISTERED_SIZES = {"nosym_absent": 9, "nosym_present": 11}


def load_populations(path):
    sets = {"nosym_absent": [], "nosym_present": []}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 2 or parts[0] not in sets:
                raise SystemExit("FATAL: bad populations line: %r" % line)
            sets[parts[0]].append(parts[1])
    for key, want in REGISTERED_SIZES.items():
        got = len(sets[key])
        if got != want:
            raise SystemExit(
                "FATAL: %s lists %d runs, not the registered %d (docs/43:1864). "
                "The positive control is enumerated BY FILE; a short population "
                "would be scored as a passing gate over fewer runs." % (key, got, want)
            )
    dupes = [p for p in set(sets["nosym_absent"]) & set(sets["nosym_present"])]
    if dupes:
        raise SystemExit("FATAL: %r appear in both halves of the partition" % dupes)
    return sets


def tag_count(path):
    base = os.path.basename(path)
    for tag, n in TAG_COUNTS:
        if base.startswith(tag):
            return n
    return None


def json_pointer(obj, pointer):
    """RFC-6901-lite. Empty pointer -> the object itself. Returns (found, value)."""
    if pointer in ("", None):
        return False, None
    if pointer == "/":
        return True, obj
    cur = obj
    for raw in pointer.lstrip("/").split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            if key not in cur:
                return False, None
            cur = cur[key]
        elif isinstance(cur, list):
            try:
                cur = cur[int(key)]
            except (ValueError, IndexError):
                return False, None
        else:
            return False, None
    return True, cur


class Gate:
    def __init__(self, key, title, registered_at):
        self.key = key
        self.title = title
        self.registered_at = registered_at
        self.status = NOT_MEASURED
        self.verdict = None  # True / False / None
        self.detail = ""
        self._measured = False

    def measure(self, ok, detail):
        self.status = MEASURED
        self.verdict = bool(ok)
        self.detail = detail
        self._measured = True

    def unmeasured(self, detail):
        self.status = NOT_MEASURED
        self.verdict = None
        self.detail = detail
        self._measured = False

    @property
    def green(self):
        # Keyed on the measurement, not on the display label: the core-presence
        # row prints PRESENT / ABSENT rather than borrowing the :1868 control
        # vocabulary, and must still be able to go green.
        return self._measured and self.verdict is True

    def as_dict(self):
        return {
            "key": self.key,
            "title": self.title,
            "registered_at": self.registered_at,
            "status": self.status,
            "verdict": self.verdict,
            "detail": self.detail,
        }


def run_command(template, subs):
    """Split the TEMPLATE, then substitute into the resulting argv.

    Substituting first and splitting after would push the substituted value
    through shlex, which in POSIX mode eats backslashes -- so a Windows temp path
    like C:\\Users\\...\\tmp.txt arrives at the tool mangled and unopenable. The
    template's own quoting is the author's to get right; the values are never
    parsed. (Quote paths, or write them with forward slashes.)
    """
    argv = []
    for tok in shlex.split(template):
        for k, v in subs.items():
            tok = tok.replace("{%s}" % k, v)
        argv.append(tok)
    proc = subprocess.run(argv, capture_output=True, text=True, cwd=ROOT)
    return proc, " ".join(argv)


def collect_reports(runs, schema, pops):
    """The registered quantities CI must PRINT but does not gate on.

    :1834 requires the UNIDENTIFIED count ("reported, not silently dropped",
    "with the count printed on the figure face") and the if_pos-excluded count
    ("their number reported"). :1836 requires the header form "logged per file".
    Declaring these in [schema] and never reading them would make filling them in
    a no-op, so they are collected and printed under the gates.
    """
    watched = set(pops["nosym_absent"]) | set(pops["nosym_present"])
    rows = [r for r in runs if norm_path(r.get("path")) in watched]
    rep = {}
    if schema.get("unidentified"):
        unid = [norm_path(r.get("path")) for r in rows if r.get("unidentified") is True]
        rep["UNIDENTIFIED adsorbate rows (:1834)"] = (
            "%d of %d%s" % (len(unid), len(rows),
                            (" -- " + ", ".join(unid[:3])) if unid else "")
        )
    if schema.get("n_if_pos_excluded"):
        vals = [r.get("n_if_pos_excluded") for r in rows]
        ints = [v for v in vals if isinstance(v, int)]
        rep["atoms excluded for if_pos = 0 (:1834)"] = (
            "%d across %d runs%s" % (sum(ints), len(ints),
                                     "" if len(ints) == len(vals)
                                     else " (%d rows reported none)" % (len(vals) - len(ints)))
        )
    if schema.get("header_form"):
        forms = {}
        for r in rows:
            f = r.get("header_form")
            if isinstance(f, str) and f:
                forms[f] = forms.get(f, 0) + 1
        rep["header forms encountered (:1836)"] = (
            ", ".join("%s x%d" % (k, v) for k, v in sorted(forms.items())) or "none reported"
        )
    return rep


def extract_runs(payload, schema):
    """Map the core's JSON onto the registered quantity names. Returns (runs, missing)."""
    missing = [k for k in ("runs_array", "path") if not schema.get(k)]
    if missing:
        return None, missing
    found, arr = json_pointer(payload, schema["runs_array"])
    if not found or not isinstance(arr, list):
        return None, ["runs_array (pointer %r resolved to nothing)" % schema["runs_array"]]
    out = []
    for item in arr:
        rec = {}
        for name, pointer in schema.items():
            if name == "runs_array" or not pointer:
                continue
            ok, val = json_pointer(item, pointer)
            rec[name] = val if ok else None
        out.append(rec)
    return out, []


def norm_path(p):
    return (p or "").replace("\\", "/").lstrip("./")


def main():
    ap = argparse.ArgumentParser(description="A9.2 control status face")
    ap.add_argument("--invocation", default=os.path.join(HERE, "silentgate-invocation.toml"))
    ap.add_argument("--populations", default=os.path.join(HERE, "populations.txt"))
    ap.add_argument("--csv", default=os.path.join(ROOT, "docs", "figs", "symops_audit.csv"))
    ap.add_argument("--disjoint-json", default=None)
    ap.add_argument("--oc20-json", default=None,
                    help="status artifact written by the OC20 job; absent => NOT MEASURED")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--summary", default=os.environ.get("GITHUB_STEP_SUMMARY"))
    args = ap.parse_args()

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT
    ).stdout.strip() or "UNKNOWN"

    cfg = load_toml(args.invocation)
    cli = cfg.get("cli", {})
    schema = cfg.get("schema", {})
    pops = load_populations(args.populations)

    gates = [
        Gate("core_present", "silentgate core present", "docs/43:1840"),
        Gate("disjointness", "AI-use log INTERSECT core paths = {}", "docs/43:1840"),
        Gate("positive_9_9", "positive control: 9/9 LOCKED, nosym-absent", "docs/43:1864"),
        Gate("negative_qe_0_11", "QE negative control: 0/11 LOCKED, force-only", "docs/43:1858"),
        Gate("partition_20_20", "20-for-20 partition by the deck's nosym line", "docs/43:1864"),
        Gate("two_witness_n_n", "header-vs-force agreement, n/n classifiable rows", "docs/43:1864"),
        Gate("tag_agreement_20_20", "tag-free adsorbate rule reproduces tag counts 20/20", "docs/43:1834"),
        Gate("negative_oc20", "OC20 negative control: exactly 0.00 % of 500", "docs/43:1856"),
    ]
    G = {g.key: g for g in gates}

    # The five named core paths of :1840. An empty silentgate/ directory is not
    # a core, so this checks the modules themselves.
    reports = {}

    core_dir = os.path.join(ROOT, "silentgate")
    missing_core = [
        rel for rel in ("readers", "census.py", "classify.py", "direction.py", "cli.py")
        if not os.path.exists(os.path.join(core_dir, rel))
    ]
    if not missing_core:
        G["core_present"].measure(True, "all five named core paths present")
        G["core_present"].status = "PRESENT"
    else:
        G["core_present"].measure(
            False,
            "missing: %s. The core is entrant-written and entrant-committed "
            "(docs/43:1840), so this row is red until he commits it. Not a CI defect."
            % ", ".join("silentgate/" + m for m in missing_core),
        )
        G["core_present"].status = "ABSENT"

    # ---- disjointness -----------------------------------------------------
    dj = None
    if args.disjoint_json and os.path.exists(args.disjoint_json):
        try:
            with open(args.disjoint_json, "r", encoding="utf-8") as fh:
                dj = json.load(fh)
            if not isinstance(dj, dict):
                raise ValueError("not a JSON object")
        except (OSError, ValueError) as exc:
            # Never crash before the face is printed: the one moment this matters
            # is when the disjointness check itself misbehaved, and a traceback
            # instead of a status face would lose every other gate's result too.
            dj = None
            G["disjointness"].unmeasured(
                "check_disjoint.py result artifact is unreadable (%s)" % exc)
    if dj is not None:
        if dj.get("status") == "PASS":
            G["disjointness"].measure(
                True, "%d path token(s) in %s, none a core path"
                % (dj.get("n_paths_in_log", 0), dj.get("log_path"))
            )
        else:
            G["disjointness"].measure(
                False, dj.get("reason")
                or "%d core path(s) present in the log" % len(dj.get("violations", []))
            )
    else:
        G["disjointness"].unmeasured("check_disjoint.py produced no result artifact")

    # ---- OC20 (its own job; absence is NOT MEASURED, i.e. not green) ------
    if args.oc20_json and os.path.exists(args.oc20_json):
        with open(args.oc20_json, "r", encoding="utf-8") as fh:
            oc = json.load(fh)
        if oc.get("status") == MEASURED:
            rate = oc.get("locked_rate_percent")
            n = oc.get("n_relaxations")
            G["negative_oc20"].measure(
                rate == 0.0 and n == 500,
                "%s%% LOCKED over %s relaxations (registered: exactly 0.00 %% of 500)"
                % (rate, n),
            )
            if oc.get("per_step_exact_zero_count") is not None:
                reports["OC20 per-step exact-zero count (:1856)"] = str(
                    oc["per_step_exact_zero_count"])
        else:
            G["negative_oc20"].unmeasured(oc.get("detail", "OC20 job reported NOT MEASURED"))
    else:
        G["negative_oc20"].unmeasured(
            "the OC20 job did not execute or produced no artifact -- "
            "'a commit on which the OC20 job did not execute is not green' (:1868)"
        )

    # ---- the in-house controls -------------------------------------------
    census_cmd = (cli.get("census_cmd") or "").strip()
    if not census_cmd:
        why = ("silentgate-invocation.toml declares no census_cmd; the CLI is core "
               "(:1840) so CI does not invent its interface")
        for k in ("positive_9_9", "negative_qe_0_11", "partition_20_20",
                  "two_witness_n_n", "tag_agreement_20_20"):
            G[k].unmeasured(why)
    else:
        all_paths = pops["nosym_absent"] + pops["nosym_present"]
        # every classifiable adsorbate row of the CSV at the commit CI runs against
        csv_rows = []
        if os.path.exists(args.csv):
            with open(args.csv, "r", encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    try:
                        n_ads = int(row.get("n_adsorbate") or 0)
                    except ValueError:
                        n_ads = 0
                    if n_ads > 0 and (row.get("max_fy_adsorbate") or "").strip():
                        csv_rows.append(row)
        csv_paths = ["runs/" + norm_path(r["path"]) for r in csv_rows]
        want = list(dict.fromkeys(all_paths + csv_paths))

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as tf:
            tf.write("\n".join(want) + "\n")
            paths_file = tf.name
        try:
            proc, shown = run_command(census_cmd, {"paths_file": paths_file})
        finally:
            os.unlink(paths_file)

        if proc.returncode != 0:
            why = "census_cmd failed (rc=%d): %s" % (proc.returncode, (proc.stderr or "").strip()[:400])
            for k in ("positive_9_9", "negative_qe_0_11", "partition_20_20",
                      "two_witness_n_n", "tag_agreement_20_20"):
                G[k].unmeasured(why)
        else:
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError as exc:
                why = "census_cmd stdout is not JSON (%s); command was: %s" % (exc, shown)
                for k in ("positive_9_9", "negative_qe_0_11", "partition_20_20",
                          "two_witness_n_n", "tag_agreement_20_20"):
                    G[k].unmeasured(why)
            else:
                runs, missing = extract_runs(payload, schema)
                if runs is not None:
                    reports.update(collect_reports(runs, schema, pops))
                if missing:
                    why = ("silentgate-invocation.toml [schema] leaves these unmapped: %s"
                           % ", ".join(missing))
                    for k in ("positive_9_9", "negative_qe_0_11", "partition_20_20",
                              "two_witness_n_n", "tag_agreement_20_20"):
                        G[k].unmeasured(why)
                else:
                    by_path = {norm_path(r.get("path")): r for r in runs}
                    evaluate(G, schema, by_path, pops, csv_rows)

    # ---- the face ---------------------------------------------------------
    lines = []
    lines.append("silentgate S1 control face")
    lines.append("  commit: %s" % commit)
    lines.append("")
    width = max(len(g.title) for g in gates)
    for g in gates:
        mark = "PASS" if g.green else ("FAIL" if g.verdict is False else "----")
        lines.append("  %-*s  %-12s %-4s  %s" % (width, g.title, g.status, mark, g.registered_at))
        if g.detail:
            for chunk in wrap(g.detail, 84):
                lines.append("      %s" % chunk)
    if reports:
        lines.append("")
        lines.append("  REPORTED ALONGSIDE (registered to be printed, not gated on):")
        for k in sorted(reports):
            lines.append("    %-42s %s" % (k, reports[k]))
    lines.append("")
    green = all(g.green for g in gates)
    lines.append("RESULT: %s" % ("GREEN" if green else "NOT GREEN"))
    if not green:
        lines.append("")
        lines.append("  A9.2 is registered as a GATE: 'P-CTRL therefore voids rather than")
        lines.append("  caveats. Any drift voids the corresponding numbers rather than")
        lines.append("  caveating them.' (docs/43:1848) Numbers produced after the last")
        lines.append("  green commit are VOID until this face is green (:1868).")
    text = "\n".join(lines)
    print(text)

    if args.summary:
        try:
            with open(args.summary, "a", encoding="utf-8") as fh:
                fh.write("```text\n" + text + "\n```\n")
        except OSError:
            pass

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as fh:
            json.dump(
                {"commit": commit, "green": green, "reports": reports,
                 "gates": [g.as_dict() for g in gates]},
                fh, indent=1,
            )

    return 0 if green else 1


def wrap(s, n):
    words, line, out = s.split(), "", []
    for w in words:
        if line and len(line) + 1 + len(w) > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    return out


def evaluate(G, schema, by_path, pops, csv_rows):
    """Score the five in-house gates from the core's own output."""
    absent, present = pops["nosym_absent"], pops["nosym_present"]

    def need(name):
        return bool(schema.get(name))

    def nonbool(field, paths):
        """Rows whose verdict field is not a real boolean.

        A null is NOT MEASURED, never "not locked". Without this the 0/11 gate
        would report PASS on a census that answered nothing -- the exact shape of
        fail-open A9.2 exists to prevent (:1848, "voids rather than caveats").
        """
        return [p for p in paths if not isinstance(by_path[p].get(field), bool)]

    missing_rows = [p for p in absent + present if p not in by_path]
    if missing_rows:
        why = "census output has no row for: %s" % ", ".join(missing_rows[:5])
        for k in ("positive_9_9", "negative_qe_0_11", "partition_20_20", "tag_agreement_20_20"):
            G[k].unmeasured(why)
    else:
        # 9/9, scored two-witness AND force-only (:1864)
        if not (need("locked_two_witness") and need("locked_force_only")):
            G["positive_9_9"].unmeasured(
                "[schema] locked_two_witness / locked_force_only unmapped")
        else:
            blank = sorted(set(nonbool("locked_two_witness", absent))
                           | set(nonbool("locked_force_only", absent)))
            if blank:
                G["positive_9_9"].unmeasured(
                    "%d of 9 rows returned no boolean verdict, e.g. %s -- a null is "
                    "NOT MEASURED, not a verdict" % (len(blank), ", ".join(blank[:3])))
            else:
                tw = [p for p in absent if by_path[p]["locked_two_witness"] is True]
                fo = [p for p in absent if by_path[p]["locked_force_only"] is True]
                n = len(absent)
                G["positive_9_9"].measure(
                    len(tw) == n and len(fo) == n,
                    "two-witness %d/%d, force-only %d/%d" % (len(tw), n, len(fo), n),
                )

        # 0/11, FORCE-ONLY with the header witness ignored (:1858)
        if not need("locked_force_only"):
            G["negative_qe_0_11"].unmeasured("[schema] locked_force_only unmapped")
        else:
            blank = nonbool("locked_force_only", present)
            if blank:
                G["negative_qe_0_11"].unmeasured(
                    "%d of 11 rows returned no boolean verdict, e.g. %s -- reporting "
                    "0/11 from nulls would be the fail-open A9.2 exists to prevent"
                    % (len(blank), ", ".join(blank[:3])))
            else:
                hits = [p for p in present if by_path[p]["locked_force_only"] is True]
                G["negative_qe_0_11"].measure(
                    len(hits) == 0,
                    "force-only LOCKED %d/%d%s"
                    % (len(hits), len(present),
                       (" -- " + ", ".join(hits)) if hits else ""),
                )

        # the 20-for-20 partition by the DECK's nosym line (:1864)
        if not need("nosym_in_deck"):
            G["partition_20_20"].unmeasured("[schema] nosym_in_deck unmapped")
        else:
            blank = nonbool("nosym_in_deck", absent + present)
            if blank:
                G["partition_20_20"].unmeasured(
                    "%d of 20 rows returned no boolean for nosym_in_deck, e.g. %s"
                    % (len(blank), ", ".join(blank[:3])))
            else:
                bad = [p for p in absent if by_path[p]["nosym_in_deck"] is not False]
                bad += [p for p in present if by_path[p]["nosym_in_deck"] is not True]
                n = len(absent) + len(present)
                G["partition_20_20"].measure(
                    not bad,
                    "%d/%d partition%s"
                    % (n - len(bad), n,
                       (" -- misplaced: " + ", ".join(bad[:5])) if bad else ""),
                )

        # the tag-count agreement CI is registered to print (:1834)
        if need("n_adsorbate"):
            disagree = []
            for p in absent + present:
                want = tag_count(p)
                got = by_path[p].get("n_adsorbate")
                if want is None or got != want:
                    disagree.append("%s (tag %s, rule %s)" % (p, want, got))
            n = len(absent) + len(present)
            G["tag_agreement_20_20"].measure(
                not disagree,
                "%d/%d agree%s" % (n - len(disagree), n,
                                   (" -- " + "; ".join(disagree[:5])) if disagree else ""),
            )
        else:
            G["tag_agreement_20_20"].unmeasured("[schema] n_adsorbate unmapped")

    # header-vs-force agreement on every classifiable adsorbate row (:1864)
    if not (need("locked_two_witness") and need("locked_force_only")):
        G["two_witness_n_n"].unmeasured(
            "[schema] locked_two_witness / locked_force_only unmapped")
    elif not csv_rows:
        G["two_witness_n_n"].unmeasured(
            "docs/figs/symops_audit.csv has no classifiable adsorbate row at this commit")
    else:
        n = len(csv_rows)
        agree = 0
        absent_rows, blank_rows = [], []
        for row in csv_rows:
            p = "runs/" + norm_path(row["path"])
            rec = by_path.get(p)
            if rec is None:
                absent_rows.append(p)
                continue
            tw, fo = rec.get("locked_two_witness"), rec.get("locked_force_only")
            if not (isinstance(tw, bool) and isinstance(fo, bool)):
                blank_rows.append(p)
                continue
            if tw == fo:
                agree += 1
        if absent_rows:
            G["two_witness_n_n"].unmeasured(
                "census output missing %d of %d classifiable rows, e.g. %s"
                % (len(absent_rows), n, ", ".join(absent_rows[:3])))
        elif blank_rows:
            G["two_witness_n_n"].unmeasured(
                "%d of %d classifiable rows returned no boolean verdict, e.g. %s"
                % (len(blank_rows), n, ", ".join(blank_rows[:3])))
        else:
            G["two_witness_n_n"].measure(agree == n, "%d/%d agree" % (agree, n))


if __name__ == "__main__":
    sys.exit(main())
