#!/usr/bin/env python3
"""XVI-P p21 release gate: small release from p20 (no scope expansion), from the p20 independent-rebuild findings.

Runs AFTER the p14r .. p20 gates (release_p20.py -> certificates/P20_release.json, the p20 LAYER record) and requires:
  contract identity : as in p19/p20 (no contract revision);
  lower layers      : RE-CHECKED live, not read from layer records: p18 layer (files byte-identical, P18
                      quantum_inputs_evaluated == 'earned'), graph inventory, p19 layer (release_p20.p19_layer), K1
                      correction content (release_p20.k1_check), retraction check;
  p20 layer         : p20_conventions.py byte-identical; d11_pin.py and release_p20.py differ from the p20 zip ONLY as
                      the disclosed p21 revisions; P20_release accepted with D11_ratio_pin_verified and
                      D11_absolute_pin_verified earned;
  absolute D11 pin  : P20_D11_pin.json absolute pin PASS (derived from 1/2 Tr ln under the declared conventions, no
                      external convention choice), top-level *_pin_status == nested status, x2 / sign flip / drop D11
                      detected (release_p20.d11_pin_check, live);
  disclosure        : every file modified vs the p20 zip is a disclosed revision (code, tests, manuscript) or a
                      documentation / build file listed in DISCLOSED_OTHER; the p20 edit of P19_defect.tex is listed;
  p20 independent   : archived report pinned (e8f358f9...), PASS, bound to tree 2c0aa153... / zip ca32ce01...
                      (same-box caveat) -> independent_rebuild_passed_p20; the p21 independent flag is pending;
  hard stops        : QC.HARD_STOPS_P21 (bulk_symmetry_restored false regardless; O.1 NOT_CLOSED).
Publication fails closed.  On reject: no P21_release.json and NO RELEASE_STATUS.json is left behind.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p21_conventions as QC  # noqa: E402
import p20_conventions as Q20  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)
import release_p19 as R19  # noqa: E402   (helpers only)
import release_p20 as R20  # noqa: E402   (helpers only)

ARCH_P20 = "archival/p20"
ARCH_P20_INDEP = f"{ARCH_P20}/reproducibility/independent_rebuild_report_p20.json"
STATUS_FILES = ("RELEASE_STATUS.json", "certificates/RELEASE_STATUS.json")
# documentation / build / archive files that every release updates (not package logic)
DISCLOSED_OTHER_PREFIXES = ("README.md", "REBUILD_INSTRUCTIONS.md", "tools/", "archival/", "manuscript/",
                            "reproducibility/", "build/")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def lower_layers():
    id_ok, ident = R19.contract_identity()
    l18_ok, l18 = R19.p18_layer()[:2]
    inv_ok, _ = R19.inventory_recheck()
    l19_ok, l19, _r19 = R20.p19_layer()
    k1_ok, k1, _ = R20.k1_check()
    rt_ok, rt = R20.retraction_check()
    ok = bool(id_ok and l18_ok and inv_ok and l19_ok and k1_ok and rt_ok)
    return ok, {"contract_identity": id_ok, "p18_layer": l18_ok,
                "P18_quantum_inputs_evaluated": l18.get("P18_quantum_inputs_evaluated"), "inventory": inv_ok,
                "p19_layer": l19_ok, "k1_correction": k1_ok, "retraction": rt_ok, "retraction_hits": rt.get("hits"),
                "contract_detail": ident, "rechecked_live": True}


def p20_layer():
    conv_ok = sha(ROOT / "code/p5_calc/p20_conventions.py") == QC.P20_CONVENTIONS_SHA256
    revs = {k: {"sha256": sha(ROOT / k), "differs_from_p20": sha(ROOT / k) != h,
                "disclosed": k in QC.DISCLOSED_P20_LAYER_REVISIONS_P21} for k, h in QC.P20_RELEASED_SHA256.items()}
    r = jl("certificates/P20_release.json")
    ok = bool(conv_ok and all(v["disclosed"] for v in revs.values())
              and r.get("revision") == Q20.REVISION and r.get("publication") == "accepted"
              and r.get("release_claim_accepted") is True and r.get("D11_ratio_pin_verified") == "earned"
              and r.get("D11_absolute_pin_verified") == "earned" and r.get("hard_stops_hold") is True
              and r.get("bulk_symmetry_restored") is False)
    return ok, {"p20_conventions_byte_identical": conv_ok, "disclosed_p21_revisions": revs,
                "P20_release_accepted": r.get("publication") == "accepted",
                "P20_D11_absolute_pin_verified": r.get("D11_absolute_pin_verified")}, r


def p20_independent():
    f = ROOT / ARCH_P20_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P20_INDEP, "present": False, "pins_ok": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P20_INDEPENDENT_REPORT
    rec = {"report": ARCH_P20_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P20_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"), "bound_to_source_zip_sha256": rep.get("zip_sha256"),
           "tree_matches_p20": rep.get("source_tree_sha256") == QC.P20_SOURCE_TREE_SHA256,
           "zip_matches_p20": rep.get("zip_sha256") == QC.P20_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])),
           "findings": [x.get("id") for x in rep.get("findings", []) if isinstance(x, dict)],
           "caveat": rep.get("same_box_caveat") or "same box (disclosed)",
           "live_report_identical_to_archived": (live.read_bytes() == f.read_bytes()) if live.is_file()
           else "live report not in this tree",
           "NOT_inherited_by_p21": "bound to the p20 tree/zip; the p21 tree has its own (pending) independent flag"}
    rec["archived_p20_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P20_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p20_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p20"] and rec["zip_matches_p20"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def change_log():
    f = ROOT / QC.P20_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P20_ARCHIVED_RECORDS[QC.P20_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT) if r != SM.REFERENCE_FILE}
    added = sorted((set(new) - set(old)) | {SM.REFERENCE_FILE})
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])
    contract = [x for x in added + removed + modified if x.startswith("code/p5_entry/")
                and not __import__("contract_registry").registered_contract_change(x, ROOT)]   # p22 registry
    disclosed = (set(QC.DISCLOSED_P20_LAYER_REVISIONS_P21) | set(QC.DISCLOSED_TEST_REVISIONS_P21)
                 | set(QC.DISCLOSED_MANUSCRIPT_REVISIONS)
                 | set(__import__("contract_registry").P22_REVISED_FILES)
                 | set(__import__("contract_registry").P23_REVISED_FILES))   # p22 disclosed revisions (pinned by the p22 gate)
    undisclosed = [x for x in modified + removed if x not in disclosed and not x.startswith(DISCLOSED_OTHER_PREFIXES)]
    return {"base": f"{QC.P20_SOURCE_LIST} (pinned; files of the p20 zip sha256 {QC.P20_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok, "added": added, "removed": removed, "modified": modified,
            "contract_files_changed": contract, "undisclosed_package_changes": undisclosed,
            "counts": {"added": len(added), "removed": len(removed), "modified": len(modified)}}


def manuscript_disclosure():
    rec = {}
    for k, v in QC.DISCLOSED_MANUSCRIPT_REVISIONS.items():
        cur = sha(ROOT / k) if (ROOT / k).is_file() else None
        rec[k] = {"current_equals_disclosed_p20": cur == v["p20_sha256"], "differs_from_p19": cur != v["p19_sha256"],
                  "revised_in": v["revised_in"]}
    return all(x["current_equals_disclosed_p20"] for x in rec.values()), rec


def _main():
    low_ok, low = lower_layers()
    l20_ok, l20, r20 = p20_layer()
    pin_ok, pin, pc = R20.d11_pin_check()
    p20i_ok, p20i = p20_independent()
    md_ok, md = manuscript_disclosure()
    hard = dict(QC.HARD_STOPS_P21)
    hard_ok = bool(all(r20.get("hard_stops", {}).get(k) == v for k, v in hard.items())
                   and r20.get("bulk_symmetry_restored") is False)
    cl = change_log()
    execution_pass = bool(low_ok and l20_ok and pin_ok and hard_ok and md_ok and cl["base_pinned_ok"]
                          and not cl["contract_files_changed"] and not cl["undisclosed_package_changes"]
                          and p20i.get("pins_ok") is True)
    publish = execution_pass
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    earned = {k: ("earned" if (publish and r20.get(k) == "earned") else "not_earned") for k in QC.EARNABLE_P21}
    ms = json.loads(json.dumps(r20.get("milestones", {})))
    cert = dict(r20)
    for k in ("change_log_vs_p19", "disclosed_test_revisions_p20", "disclosed_p19_layer_revisions_p20",
              "p19_layer", "erratum_p19", "K1_correction", "retraction_check", "D11_pin", "open_pins",
              "open_pins_closed_in_p21", "p19_independent_rebuild", "independent_rebuild_passed_p19"):
        cert[f"p20_layer_{k}"] = cert.pop(k, None)
    # reviewer (p20): the P19 gate's change log is recomputed on the CURRENT tree; name it so
    if "p19_layer_change_log_vs_p18" in cert:
        cert["p19_gate_change_log_vs_p18_recomputed_on_current_tree"] = cert.pop("p19_layer_change_log_vs_p18")
    cert.update({
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DATE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": "p21 small release (absolute D11 pin derived; gate, scan, disclosure fixes)",
        "execution_pass": execution_pass,
        "claim_status": (("p21 small release from p20 (no scope expansion). D11 absolute pin: the sign and magnitude "
                          "of the D11 UV pole are derived from 1/2 Tr ln of the minimal scalar loop under the "
                          "package's declared conventions and equal the heat-kernel a_2 = C^2/120 + R^2/72 exactly "
                          "(Gamma^(2)|_pole = kappa^2/(16 pi^2 eps) [p^4 P2/240 + p^4 P0s/24]); external inputs are "
                          "mathematics only (a_2 coefficients, heat-kernel pole formula), no external convention "
                          "choice. Projected (ch-only) results as in p20; bulk symmetry NOT restored/claimed; "
                          "O.1 NOT_CLOSED.") if publish else "p21: not accepted"),
        "absolute_pin": {"check": pin, "absolute_pin": pc.get("absolute_pin"),
                         "absolute_pin_status": pc.get("absolute_pin_status"), "mutations": pc.get("mutations")},
        "lower_layers": low, "p20_layer": l20, "manuscript_disclosure": md, "change_log_vs_p20": cl,
        "open_pins": list(QC.OPEN_PINS_P21),
        "release_claim_accepted": publish,
        "release_claim_accepted_definition": ("lower layers re-checked live (contract, p18 incl. q earned, inventory, "
                                              "p19 layer, K1, retraction) AND p20 layer accepted (disclosed p21 "
                                              "revisions of d11_pin.py and release_p20.py only) AND the absolute D11 "
                                              "pin AND every package change disclosed AND the pinned p20 independent "
                                              "record AND the p21 hard stops"),
        "publication": "accepted" if publish else "REJECTED",
        **earned,
        "disclosed_p20_layer_revisions_p21": QC.DISCLOSED_P20_LAYER_REVISIONS_P21,
        "disclosed_test_revisions_p21": QC.DISCLOSED_TEST_REVISIONS_P21,
        "disclosed_manuscript_revisions": QC.DISCLOSED_MANUSCRIPT_REVISIONS,
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": ms,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p20": p20i_ok, "p20_independent_rebuild": p20i,
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p21) source "
                               "tree only (independent: pending until a reviewer report for this tree exists); "
                               f"independent_rebuild_passed_p20 refers to the p20 tree {QC.P20_SOURCE_TREE_SHA256} / zip "
                               f"{QC.P20_SOURCE_ZIP_SHA256} (same-box caveat) and is not inherited by p21"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_source.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p20_archive": ARCH_P20,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "symmetry_restored": False, "bulk_symmetry_restored": False,
        "O1_closure": "NOT_CLOSED", "insertion_status": "Frozen_negative_obstruction_preserved",
        "XV_B_opened": False, "XIV_J_opened": False, "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
            ("P20_release.json", "P20_D11_pin.json") if (ROOT / "certificates" / n).is_file()},
    })
    if publish:
        ms.setdefault("status", {})["P.5_identity"] = str(ms.get("status", {}).get("P.5_identity", "")) + \
            " [p21: D11 absolute pin derived and verified]"
    cdir = ROOT / "certificates"
    if publish:
        txt = certio.dumps(cert)
        for st in STATUS_FILES:
            (ROOT / st).write_text(txt)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release.json").write_text(txt)
        certio.write(ROOT / "ledgers" / f"{QC.CERT_PREFIX}_milestones.json", {
            "landmark": "XVI-P", "revision": QC.REVISION, "ledger": "milestones (authoritative definitions + status)",
            **ms, "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
            "independent_rebuild_passed_p20": p20i_ok, "hard_stops": hard,
            "flags": {**earned, "quantum_inputs_evaluated": cert.get("quantum_inputs_evaluated"),
                      "bulk_symmetry_restored": False}})
    else:
        _reject({"lower_layers_ok": low_ok, "lower_layers": low, "p20_layer_ok": l20_ok, "p20_layer": l20,
                 "absolute_pin_ok": pin_ok, "absolute_pin": pin, "manuscript_disclosure_ok": md_ok,
                 "p20_independent_pins_ok": p20i.get("pins_ok"), "hard_stops_hold": hard_ok,
                 "change_log_base_ok": cl["base_pinned_ok"], "contract_files_changed": cl["contract_files_changed"],
                 "undisclosed_package_changes": cl["undisclosed_package_changes"]})
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publication"],
                      "lower_layers": low_ok, "p20_layer": l20_ok, "absolute_pin": pin_ok, "manuscript": md_ok,
                      "hard_ok": hard_ok, **earned, "author": author_ok, "independent_p21": indep_ok,
                      "independent_p20": p20i_ok, "undisclosed": cl["undisclosed_package_changes"],
                      "change_log_counts": cl["counts"]}, indent=1))
    return 0 if publish else 1


def _reject(detail):
    cdir = ROOT / "certificates"
    (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
    for st in STATUS_FILES:                      # a reject must not leave a stale RELEASE_STATUS.json
        (ROOT / st).unlink(missing_ok=True)
    (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(json.dumps(
        {"landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED", **detail}, indent=1, default=str) + "\n")


def main():
    try:
        return _main()
    except Exception as exc:  # noqa: BLE001   fail closed
        _reject({"error": f"{type(exc).__name__}: {exc}"})
        print(f"release_p21 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
