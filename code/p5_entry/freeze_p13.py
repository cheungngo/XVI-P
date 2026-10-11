#!/usr/bin/env python3
"""XVI-P p14: the P.3/P.4 freeze (P3_P4_frozen_as_P5_inputs), bound to the p13 SOURCE TREE, not to the p14 tree.

P3_P4_frozen_as_P5_inputs := F1 AND F2 AND F3
  F1 independent_rebuild_passed (p13): the archived reviewer report archival/p13/reproducibility/
     independent_rebuild_report_p13.json has the pinned sha256, pass = true, no mismatches, and is bound to the p13
     source tree 2b1baf33... and source-only zip 2f85a566... (the live reproducibility/independent_rebuild_report.json,
     when present, must be byte-identical to the archived copy; it is never written by this package).
  F2 frozen code: every file of archival/p13/frozen_p13_inputs.json (classical P.3/P.4 code, inherited XVI-O code and
     notes, pins, inherited data; 54 files) is byte-identical in the current tree; the list itself has its pinned sha
     and, where the archived p13 zip is present, equals the zip (zip sha256 pinned).
  F3 frozen values: the classical reference values recomputed now (export hashes, the 7 classical P13_* certificate
     content hashes ignoring timings, the 2 classical ledgers, residual records, inherited pins) equal
     archival/p13/reference_values_p13.json (pinned sha).
The p13 flag cannot be inherited by p14 changes: it is bound to the p13 tree sha, and F2/F3 fail as soon as a frozen
file or a frozen value changes.  p14's own author/independent rebuild flags are separate (release_p14.py).
"""
from __future__ import annotations
import hashlib
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "code" / "classical"))
sys.path.insert(0, str(ROOT / "tools"))
import p14_conventions as PC  # noqa: E402
import certio  # noqa: E402
import inherited  # noqa: E402
import source_manifest as SM  # noqa: E402

CLASSICAL_CERTS = ("P13_boundary_identity", "P13_quartic_verified", "P13_brst_derivation", "P13_source_action",
                   "P13_gauge_fixing_map", "P13_ch_source_audit", "P13_master_kappa2")
CLASSICAL_LEDGERS = ("P13_ch_dependency_rows", "P13_graph_inventory")
P13_RUN_SPECIFIC = ("reproducibility", "author_rebuild_passed", "independent_rebuild_passed")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def F1_independent(root=ROOT):
    root = Path(root)
    arch = root / PC.P13_INDEPENDENT_REPORT
    rec = {"report": PC.P13_INDEPENDENT_REPORT, "present": arch.is_file()}
    if not arch.is_file():
        return False, rec
    rec["sha256_ok"] = sha(arch) == PC.P13_INDEPENDENT_REPORT_SHA256
    rep = json.loads(arch.read_text())
    rec.update({"report_pass": rep.get("pass"), "report_independent_rebuild_passed": rep.get("independent_rebuild_passed"),
                "mismatches": len(rep.get("mismatches", [])),
                "independent_comparisons": len(rep.get("independent_comparisons", [])),
                "compared_with_reference": (rep.get("checks", {}).get("2_entrypoint_rebuild_from_source", {})
                                            .get("comparison_with_in_zip_reference")),
                "bound_source_tree_sha256": rep.get("source_tree_sha256"),
                "bound_zip_sha256": rep.get("zip_sha256") or rep.get("source_zip_sha256"),
                "bound_to_p13_tree": rep.get("source_tree_sha256") == PC.P13_SOURCE_TREE_SHA256,
                "bound_to_p13_zip": (rep.get("zip_sha256") or rep.get("source_zip_sha256")) == PC.P13_SOURCE_ZIP_SHA256,
                "environment": rep.get("environment"), "caveat": PC.INDEPENDENT_CAVEAT})
    live = root / PC.P13_INDEPENDENT_REPORT_LIVE
    rec["live_report_present"] = live.is_file()
    rec["live_report_identical_to_archived"] = (sha(live) == sha(arch)) if live.is_file() else None
    ok = bool(rec["sha256_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and not rep.get("mismatches") and rec["bound_to_p13_tree"] and rec["bound_to_p13_zip"]
              and rec["live_report_identical_to_archived"] is not False)
    return ok, rec


def F2_frozen_code(root=ROOT):
    root = Path(root)
    lst = root / PC.P13_FROZEN_LIST
    rec = {"list": PC.P13_FROZEN_LIST, "present": lst.is_file()}
    if not lst.is_file():
        return False, rec
    rec["list_sha256_ok"] = sha(lst) == PC.P13_FROZEN_LIST_SHA256
    L = json.loads(lst.read_text())
    zp = root / PC.P13_SOURCE_ZIP_ARCHIVED
    if zp.is_file():
        rec["archived_zip_sha256_ok"] = sha(zp) == PC.P13_SOURCE_ZIP_SHA256
        with zipfile.ZipFile(zp) as z:
            names = {n.split("/", 1)[1]: n for n in z.namelist()}
            rec["list_equals_archived_zip"] = all(
                f["path"] in names and hashlib.sha256(z.read(names[f["path"]])).hexdigest() == f["sha256"]
                for f in L["files"])
    else:
        rec["archived_zip_sha256_ok"] = None          # not in a source-only copy (zips are never source)
        rec["list_equals_archived_zip"] = None
    changed = [f["path"] for f in L["files"] if not (root / f["path"]).is_file() or sha(root / f["path"]) != f["sha256"]]
    rec.update({"files": len(L["files"]), "changed_or_missing": changed})
    ok = bool(rec["list_sha256_ok"] and not changed and rec["archived_zip_sha256_ok"] is not False
              and rec["list_equals_archived_zip"] is not False and L.get("p13_source_zip_sha256") == PC.P13_SOURCE_ZIP_SHA256)
    return ok, rec


def classical_values(root=ROOT):
    """the classical subset of tools/rebuild_from_source.reference_values (p13 definitions, verbatim key layout)"""
    root = Path(root)
    q = json.loads((root / "certificates" / "P13_quartic_verified.json").read_text())
    m = json.loads((root / "certificates" / "P13_master_kappa2.json").read_text())
    rec = lambda r: {k: r[k] for k in ("W_terms", "Q_terms", "Q_identically_zero", "s0_piece_alone_Q_terms")}  # noqa: E731
    return {
        "inherited_pins": {**{k: v["sha256"] for k, v in inherited.PINS.items()},
                           **{k: v["sha256"] for k, v in SM.inherited_data(root).items()},
                           "XVI-O_o70_source_tree": json.loads((root / SM.XVIO_TREE).read_text())["sha256"]},
        "exports": {**{f"ell{k}": {"file_sha256": SM.sha(root / "exports" / f"ell{k}_generating_polynomial.srepr"),
                                   "polynomial_sha256": q[f"ell{k}_sha256"],
                                   "terms": q["terms_reproducibility"][str(k)]} for k in (2, 3, 4)},
                    "V4_grav.json": SM.sha(root / "exports" / "V4_grav.json"),
                    "ell4_conventions.json": SM.sha(root / "exports" / "ell4_conventions.json")},
        "certificate_content_sha256_ignoring_timings": {
            **{c: certio.file_content_sha(root / "certificates" / f"{c}.json", P13_RUN_SPECIFIC) for c in CLASSICAL_CERTS},
            **{f"ledgers/{l_}": certio.file_content_sha(root / "ledgers" / f"{l_}.json", P13_RUN_SPECIFIC)
               for l_ in CLASSICAL_LEDGERS}},
        "residual_records": {
            "quartic_C7": {o: rec(q["controls"]["C7_noether_exact"][o]) for o in certio.ORDERS},
            "master_grav_af0": {o: rec(m["details"]["grav_af0_deterministic"][o]) for o in certio.ORDERS},
            "master_table": m["table_by_kappa_and_antifield_number"],
            "required_master_residuals": m["required_master_residuals"]},
    }


def _flat(d, p=""):
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            out.update(_flat(v, f"{p}/{k}"))
        return out
    return {p: d}


def F3_frozen_values(root=ROOT):
    root = Path(root)
    ref_f = root / PC.P13_REFERENCE_FILE
    rec = {"reference": PC.P13_REFERENCE_FILE, "present": ref_f.is_file()}
    if not ref_f.is_file():
        return False, rec
    rec["reference_sha256_ok"] = sha(ref_f) == PC.P13_REFERENCE_VALUES_SHA256
    refv = json.loads(ref_f.read_text())["values"]
    cur = classical_values(root)
    ref_sub = {k: (refv[k] if k != "certificate_content_sha256_ignoring_timings" else
                   {c: refv[k][c] for c in cur[k]}) for k in cur}
    a, b = _flat(ref_sub), _flat(cur)
    diffs = [k for k in sorted(set(a) | set(b)) if a.get(k, "<absent>") != b.get(k, "<absent>")]
    rec.update({"compared": len(set(a) | set(b)), "equal": len(set(a) | set(b)) - len(diffs), "differences": diffs[:30]})
    return bool(rec["reference_sha256_ok"] and not diffs), rec


def freeze(root=ROOT):
    f1, r1 = F1_independent(root)
    f2, r2 = F2_frozen_code(root)
    f3, r3 = F3_frozen_values(root)
    return {"P3_P4_frozen_as_P5_inputs": bool(f1 and f2 and f3),
            "definition": "F1 independent_rebuild_passed(p13 tree) AND F2 frozen code byte-identical AND F3 frozen values equal",
            "independent_rebuild_passed_p13": f1, "frozen_code_unchanged": f2, "frozen_values_unchanged": f3,
            "bound_to": {"p13_source_tree_sha256": PC.P13_SOURCE_TREE_SHA256, "p13_source_zip_sha256": PC.P13_SOURCE_ZIP_SHA256},
            "caveat": PC.INDEPENDENT_CAVEAT,
            "F1": r1, "F2": r2, "F3": r3}


if __name__ == "__main__":
    out = freeze()
    print(json.dumps({k: out[k] for k in ("P3_P4_frozen_as_P5_inputs", "independent_rebuild_passed_p13",
                                          "frozen_code_unchanged", "frozen_values_unchanged")}, indent=1))
    print(json.dumps(out["F3"], indent=0)[:600])
