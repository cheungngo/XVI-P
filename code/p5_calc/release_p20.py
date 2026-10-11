#!/usr/bin/env python3
"""XVI-P p20 release gate: CORRECTION release of p19 (no scope expansion), from the p19 independent-rebuild findings.

Runs AFTER the p14r .. p19 gates (release_p19.py -> certificates/P19_release.json, the p19 LAYER record) and requires:
  contract identity : as in p19 (p14r contract + dred.py byte-identical to p18; no new contract file);
  p18 layer         : byte-identical (pinned sha256);
  p19 layer         : p19_conventions.py byte-identical; defect.py and release_p19.py differ from the p19 zip ONLY as
                      the disclosed p20 revisions (QC.DISCLOSED_P19_LAYER_REVISIONS_P20); P19_release accepted with
                      quantum_inputs_evaluated and projected_defect_computed earned;
  K1 correction     : P19_defect.json (p20 content): orientation ratio -1, Sigma in route-G (c,cb) coordinates
                      (+3/8, -1/4), derived factor +1, full sigma_0 closure of the complete MS-bar S_ct, tree controls,
                      every p20 control true, full-closure detector catches drop D13 and flip K.c;
  retraction        : the retracted p19 K1 / J1 phrases appear nowhere in README.md, the P19 note, P19_defect.json or
                      P19_release.json (they may appear only quoted inside the erratum);
  D11 pin           : P20_D11_pin.json ratio pin PASS (derived); absolute pin PASS (derived in p21 from 1/2 Tr ln
                      under the declared conventions; p20 had it OPEN); the top-level *_pin_status keys (typeset in
                      the PDF) must equal the nested statuses; drop D11 / x2 / sign flip detected;
  p19 independent   : archived report pinned (1b01f1d8...), PASS, bound to tree fcf90354... / zip da924275...
                      (same-box caveat) -> independent_rebuild_passed_p19; the p20 independent flag is pending;
  hard stops        : QC.HARD_STOPS_P20 (bulk_symmetry_restored false regardless; O.1 NOT_CLOSED).
p21 DISCLOSED REVISION (p20 independent-rebuild findings): (i) absolute pin PASS required, top-level / nested status
consistency checked; (ii) run standalone, the gate no longer trusts the P19 layer record alone: it re-runs the p18
layer check (P18 quantum_inputs_evaluated == 'earned', p18 files byte-identical) and the graph inventory recheck.
Publication fails closed (I1 style).  On reject: no P20_release.json and NO RELEASE_STATUS.json is left behind.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p20_conventions as QC  # noqa: E402
import p19_conventions as Q19  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)
import release_p19 as R19  # noqa: E402   (helpers only; main() not run)

ARCH_P19 = "archival/p19"
ARCH_P19_INDEP = f"{ARCH_P19}/reproducibility/independent_rebuild_report_p19.json"
# p19 texts retracted by the p20 erratum (K1 orientation error; J1 wording)
RETRACTED_PHRASES = (
    "full c.b / ghost-sector closure FAILS",
    "full c.b / ghost-sector closure of the MS-bar counterterm FAILS",
    "for which full closure fails",
    "with +1 full closure fails",
    "full closure \\emph{fails}",
    "This is unresolved",
    "This is not resolved in p19",
    "needs relative factor -1; the derived ghost-equation relation gives +1; not resolved",
    "factor +1 (K1) full c.b closure FAILS",
    "full c.b closure NOT established (K1)",
    "the physical field",
)
RETRACTION_SCOPE = ("README.md", "manuscript/notes/P19_defect.tex", "certificates/P19_defect.json",
                    "certificates/P19_release.json", "manuscript/body/P19-results-table.tex")
STATUS_FILES = ("RELEASE_STATUS.json", "certificates/RELEASE_STATUS.json")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def p19_layer():
    conv_ok = sha(ROOT / "code/p5_calc/p19_conventions.py") == QC.P19_CONVENTIONS_SHA256
    revs = {k: {"sha256": sha(ROOT / k), "differs_from_p19": sha(ROOT / k) != h,
                "disclosed": k in QC.DISCLOSED_P19_LAYER_REVISIONS_P20} for k, h in QC.P19_RELEASED_SHA256.items()}
    r = jl("certificates/P19_release.json")
    l18_ok, l18 = R19.p18_layer()[:2]           # p21: recheck the lower layers (do not trust the P19 record alone)
    inv_ok, _inv = R19.inventory_recheck()
    ok = bool(conv_ok and all(v["disclosed"] for v in revs.values()) and l18_ok and inv_ok
              and r.get("revision") == Q19.REVISION and r.get("publication") == "accepted"
              and r.get("release_claim_accepted") is True and r.get("quantum_inputs_evaluated") == "earned"
              and r.get("projected_defect_computed") == "earned" and r.get("hard_stops_hold") is True
              and r.get("bulk_symmetry_restored") is False)
    return ok, {"p19_conventions_byte_identical": conv_ok, "disclosed_p20_revisions": revs,
                "P19_release_accepted": r.get("publication") == "accepted",
                "lower_layers_rechecked_p21": {"p18_layer_ok": l18_ok,
                                               "P18_quantum_inputs_evaluated": l18.get("P18_quantum_inputs_evaluated"),
                                               "inventory_recheck_ok": inv_ok}}, r


def k1_check():
    c = jl("certificates/P19_defect.json")
    k1 = c.get("counterterm_solve", {}).get("K1_ghost_closure_convention", {})
    det = c.get("full_closure_mutation_detector", {}).get("cases", {})
    ctrl = c.get("p20_controls", {})
    chk = {
        "content_revision_p20": str(c.get("corrected_in_revision", "")).startswith("p20"),
        "orientation_ratio_minus_one": k1.get("orientation_ratio_routeG_over_cbc") == ["-1", "-1"],
        "Sigma_pole_routeG_c_cb": k1.get("Sigma_pole_routeG_c_cb_coordinates") == ["3/8", "-1/4"],
        "derived_factor_plus_one": str(k1.get("relative_factor_derived")) == "1",
        "derived_relation_reproduces_P15": k1.get("derived_equals_P15") is True,
        "full_closure_complete_S_ct": k1.get("full_closure_complete_S_ct", {}).get("closed") is True,
        "without_ccb_not_closed": k1.get("full_closure_S_ct_without_ccb (p19 package S_ct)", {}).get("closed") is False,
        "tree_controls_ok": k1.get("tree_controls", {}).get("ok") is True,
        "p20_controls_all_true": bool(ctrl) and all(v is True for v in ctrl.values()),
        "detector_drop_D13": det.get("drop_graph_D13 (c.K data = 0, Sigma held fixed)", {}).get("detected") is True,
        "detector_flip_Kc": det.get("flip_sign_Kc (c.K data -> -c.K, Sigma held fixed)", {}).get("detected") is True,
        "detector_drop_D11_recorded_blind": det.get("drop_graph_D11", {}).get("detected") is False,
        "route_consistency_control_holds": c.get("route_consistency_control_p19_criterion", {}).get("holds") is True,
        "quotient_incl_Sigma_zero": all(x == "0" for v in (c.get("quotient_coordinates_including_Sigma") or {"x": ["?"]})
                                        .values() for x in v),
        "quotient_Sigma_alone_c_cb_plus_3_8_minus_1_4": (c.get("quotient_coordinates_Sigma_alone_routeG") or {})
        .get("pole", [None] * 5)[3:] == ["3/8", "-1/4"],
        "J1_wording": "compatible real structure" in str(c.get("findings", {}).get("J1_p14r_counterterm_domain_field")),
        "restoration_definition_p20": "COMPLETE" in str(c.get("flag_definitions", {})
                                                        .get("projected_restoration_verified", "")),
        "bulk_false": c.get("bulk_symmetry_restored") is False}
    return all(chk.values()), chk, c


def retraction_check():
    hits = {}
    for rel in RETRACTION_SCOPE:
        f = ROOT / rel
        if not f.is_file():
            hits[rel] = ["missing file"]
            continue
        t = f.read_text()
        found = [ph for ph in RETRACTED_PHRASES if ph in t]
        if found:
            hits[rel] = found
    return not hits, {"phrases": list(RETRACTED_PHRASES), "scope": list(RETRACTION_SCOPE), "hits": hits}


def d11_pin_check():
    c = jl(f"certificates/{QC.CERT_PREFIX}_D11_pin.json")
    m = c.get("mutations", {})
    chk = {"ratio_pin_PASS": c.get("ratio_pin", {}).get("status") == "PASS",
           "ratio_10": c.get("spin_decomposition", {}).get("ratio_c0_over_c2") == "10",
           "transverse": c.get("spin_decomposition", {}).get("transverse") is True,
           "C2_quadratic_form_half_P2": c.get("curvature_quadratic_forms_derived", {}).get("C2") == {"P2": "1/2", "P0s": "0"},
           "GaussBonnet_zero": c.get("curvature_quadratic_forms_derived", {}).get("E_GaussBonnet") == {"P2": "0", "P0s": "0"},
           "absolute_pin_PASS": c.get("absolute_pin", {}).get("status") == "PASS",
           "absolute_pin_flag": c.get("D11_absolute_pin_verified") is True,
           "top_level_absolute_status_consistent": c.get("absolute_pin_status") == c.get("absolute_pin", {}).get("status"),
           "top_level_ratio_status_consistent": c.get("ratio_pin_status") == c.get("ratio_pin", {}).get("status"),
           "absolute_ratios_one": (c.get("absolute_pin", {}).get("derivation_p21", {})
                                   .get("ratio_package_over_prediction") == {"spin2": "1", "spin0s": "1"}),
           "no_external_convention_choice": str(c.get("absolute_pin", {}).get("derivation_p21", {})
                                                .get("convention_choices_external", "")).startswith("none"),
           "drop_D11_detected": m.get("drop_graph_D11", {}).get("detected_by_ratio_pin") is True,
           "x2_detected_by_absolute": m.get("D11_normalisation_x2", {}).get("detected_by_absolute_pin") is True,
           "sign_flip_detected_by_absolute": m.get("D11_sign_flip", {}).get("detected_by_absolute_pin") is True,
           "corrected_in_p21": str(c.get("corrected_in_revision", "")).startswith("p21"),
           "literature_source_stated": bool(c.get("literature_a2_minimal_scalar", {}).get("source")),
           "revision": c.get("revision") == QC.REVISION}
    return all(chk.values()), chk, c


def p19_independent():
    f = ROOT / ARCH_P19_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P19_INDEP, "present": False, "pins_ok": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P19_INDEPENDENT_REPORT
    rec = {"report": ARCH_P19_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P19_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"), "bound_to_source_zip_sha256": rep.get("zip_sha256"),
           "tree_matches_p19": rep.get("source_tree_sha256") == QC.P19_SOURCE_TREE_SHA256,
           "zip_matches_p19": rep.get("zip_sha256") == QC.P19_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])), "findings": [x.get("id") for x in rep.get("findings", [])
                                                                      if isinstance(x, dict)],
           "caveat": rep.get("same_box_caveat") or "same box (disclosed)",
           "live_report_identical_to_archived": (live.read_bytes() == f.read_bytes()) if live.is_file()
           else "live report not in this tree",
           "NOT_inherited_by_p20": "bound to the p19 tree/zip; the p20 tree has its own (pending) independent flag"}
    rec["archived_p19_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P19_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p19_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p19"] and rec["zip_matches_p19"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def change_log():
    f = ROOT / QC.P19_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P19_ARCHIVED_RECORDS[QC.P19_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT) if r != SM.REFERENCE_FILE}
    added = sorted((set(new) - set(old)) | {SM.REFERENCE_FILE})
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])
    contract = [x for x in added + removed + modified if x.startswith("code/p5_entry/")
                and not __import__("contract_registry").registered_contract_change(x, ROOT)]   # p22 registry
    return {"base": f"{QC.P19_SOURCE_LIST} (pinned; files of the p19 zip sha256 {QC.P19_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok, "added": added, "removed": removed, "modified": modified,
            "contract_files_changed": contract, "counts": {"added": len(added), "removed": len(removed),
                                                           "modified": len(modified)}}


def _main():
    id_ok, ident = R19.contract_identity()
    import contract_registry as CR          # p22 disclosed revision: registered p22 revision of release_p18.py
    l18_ok = all((ROOT / k).is_file() and CR.layer_file_ok(k, sha(ROOT / k), h) for k, h in QC.P18_CALC_SHA256.items())
    l19_ok, l19, r19 = p19_layer()
    k1_ok, k1, dc = k1_check()
    rt_ok, rt = retraction_check()
    pin_ok, pin, pc = d11_pin_check()
    p19i_ok, p19i = p19_independent()
    hard = dict(QC.HARD_STOPS_P20)
    hard_ok = bool(all(r19.get("hard_stops", {}).get(k) == v for k, v in hard.items())
                   and dc.get("bulk_symmetry_restored") is False)
    cl = change_log()
    execution_pass = bool(id_ok and l18_ok and l19_ok and k1_ok and rt_ok and pin_ok and hard_ok
                          and cl["base_pinned_ok"] and not cl["contract_files_changed"] and p19i.get("pins_ok") is True)
    publish = execution_pass
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    earned = {k: ("earned" if (publish and r19.get(k) == "earned") else "not_earned") for k in Q19.EARNABLE_P19}
    earned["D11_ratio_pin_verified"] = "earned" if (publish and pc.get("D11_ratio_pin_verified") is True) else "not_earned"
    earned["D11_absolute_pin_verified"] = ("earned" if (publish and pc.get("D11_absolute_pin_verified") is True)
                                           else "not_earned")
    ms = json.loads(json.dumps(r19.get("milestones", {})))
    if publish:
        ms.setdefault("status", {})["P.5_identity"] = (
            "projected defect computed (zero exactly in d, all parts, all seven assignments; each row vanishes "
            "separately); projected identity verified; projected restoration verified (p20 definition: full sigma_0 "
            "closure of the complete one-loop kappa^2 MS-bar counterterm incl. c.cb, h.c/c.b/c.cbs); K1 corrected in "
            "p20 (orientation erratum); D11 ratio pin verified; D11 absolute pin verified (p21); bulk symmetry NOT restored/claimed; "
            "O.1 NOT_CLOSED")
    cert = dict(r19)
    for k in ("change_log_vs_p18", "disclosed_test_revisions_p19"):
        cert[f"p19_layer_{k}"] = cert.pop(k, None)
    cert.update({
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DATE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": "p20 CORRECTION of p19 (K1 orientation; restoration redefined; blind-spot pins; J1 wording; scan)",
        "execution_pass": execution_pass,
        "claim_status": (("p20 CORRECTION release (no scope expansion). " + str(r19.get("claim_status", "")) +
                          " D11: ratio pin verified (spin-0 : spin-2 = 10 : 1, derived from P18_D11 and equal to the "
                          "minimal-scalar a_2 prediction, literature source stated); absolute pin (sign and magnitude) derived in p21 from "
                          "1/2 Tr ln under the declared conventions and equal to the heat-kernel a_2 (p20: OPEN).")
                         if publish else "p20: not accepted"),
        "erratum_p19": {
            "K1": ("p19 stated that full sigma_0 closure of the MS-bar counterterm fails with the derived ghost-equation "
                   "factor +1 and needs -1 (unresolved). RETRACTED: Grassmann-orientation bookkeeping error -- the P15 "
                   "Sigma coordinates are (cb,c)-oriented, the route-G c.cb slots (c,cb), V[c.cb#k] = -V[(cb,c)#k]. "
                   "Corrected: Sigma = (+3/8, -1/4) in (c,cb) coordinates, derived +1, full closure in h.c, c.b, c.cbs."),
            "restoration": ("p19's projected_restoration_verified (P_ch sigma_0(S_ct) = 0, x = 0) followed from the "
                            "identity + locality; REDEFINED in p20 as full sigma_0 closure of the complete MS-bar S_ct "
                            "(incl. c.cb), kept as a labelled route-consistency control"),
            "J1": ("'over Q(i), the physical field' replaced by: the Q(i) counts are the real dimensions under a "
                   "compatible real structure"),
            "found_by": "p19 independent rebuild (report sha256 " + QC.P19_INDEPENDENT_REPORT_SHA256 + ")"},
        "K1_correction": k1, "retraction_check": rt, "D11_pin": {"check": pin, "ratio_pin": pc.get("ratio_pin"),
                                                                 "absolute_pin": pc.get("absolute_pin"),
                                                                 "spin_decomposition": pc.get("spin_decomposition"),
                                                                 "mutations": pc.get("mutations")},
        "open_pins": [x for x in QC.OPEN_PINS_P20
                      if not (x.startswith("D11_absolute") and pc.get("D11_absolute_pin_verified") is True)],
        "open_pins_closed_in_p21": [x for x in QC.OPEN_PINS_P20
                                    if x.startswith("D11_absolute") and pc.get("D11_absolute_pin_verified") is True],
        "release_claim_accepted": publish,
        "release_claim_accepted_definition": ("p19 layer accepted (with the disclosed p20 revisions of defect.py and "
                                              "release_p19.py only) AND p18 layer + contract byte-identical AND the K1 "
                                              "correction content AND the retraction check AND the D11 ratio pin AND "
                                              "the pinned p19 independent record AND the p20 hard stops"),
        "publication": "accepted" if publish else "REJECTED",
        **earned,
        "p19_layer": l19, "p18_layer_byte_identical": l18_ok, "contract_identity": ident,
        "change_log_vs_p19": cl,
        "disclosed_p19_layer_revisions_p20": QC.DISCLOSED_P19_LAYER_REVISIONS_P20,
        "disclosed_test_revisions_p20": QC.DISCLOSED_TEST_REVISIONS_P20,
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": ms,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p19": p19i_ok, "p19_independent_rebuild": p19i,
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p20) source "
                               "tree only (independent: pending until a reviewer report for this tree exists); "
                               f"independent_rebuild_passed_p19 refers to the p19 tree {QC.P19_SOURCE_TREE_SHA256} / zip "
                               f"{QC.P19_SOURCE_ZIP_SHA256} (same-box caveat) and is not inherited by p20"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_source.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p19_archive": ARCH_P19,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "symmetry_restored": False, "bulk_symmetry_restored": False,
        "O1_closure": "NOT_CLOSED", "insertion_status": "Frozen_negative_obstruction_preserved",
        "XV_B_opened": False, "XIV_J_opened": False, "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
            ("P19_release.json", "P19_defect.json", f"{QC.CERT_PREFIX}_D11_pin.json")
            if (ROOT / "certificates" / n).is_file()},
    })
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
            "independent_rebuild_passed_p19": p19i_ok, "hard_stops": hard,
            "flags": {**earned, "quantum_inputs_evaluated": cert.get("quantum_inputs_evaluated"),
                      "bulk_symmetry_restored": False}})
    else:
        _reject({"contract_identity_ok": id_ok, "p18_layer_ok": l18_ok, "p19_layer_ok": l19_ok, "k1_ok": k1_ok,
                 "k1": k1, "retraction_ok": rt_ok, "retraction": rt, "d11_pin_ok": pin_ok, "d11_pin": pin,
                 "p19_independent_pins_ok": p19i.get("pins_ok"), "hard_stops_hold": hard_ok,
                 "change_log_base_ok": cl["base_pinned_ok"], "contract_files_changed": cl["contract_files_changed"]})
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publication"],
                      "contract": id_ok, "p18_layer": l18_ok, "p19_layer": l19_ok, "k1": k1_ok, "retraction": rt_ok,
                      "retraction_hits": rt["hits"], "d11_pin": pin_ok, "hard_ok": hard_ok, **earned,
                      "author": author_ok, "independent_p20": indep_ok, "independent_p19": p19i_ok,
                      "change_log_counts": cl["counts"]}, indent=1))
    return 0 if publish else 1


def _reject(detail):
    cdir = ROOT / "certificates"
    (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
    for st in STATUS_FILES:                      # p19 reviewer: a reject must not leave a stale RELEASE_STATUS.json
        (ROOT / st).unlink(missing_ok=True)
    (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(json.dumps(
        {"landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED", **detail}, indent=1, default=str) + "\n")


def main():
    try:
        return _main()
    except Exception as exc:  # noqa: BLE001   fail closed
        _reject({"error": f"{type(exc).__name__}: {exc}"})
        print(f"release_p20 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
