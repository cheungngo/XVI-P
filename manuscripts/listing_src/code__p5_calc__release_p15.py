#!/usr/bin/env python3
"""XVI-P p15 release gate: FIRST P.5 CALCULATION (Batch A: D02, D12, D14a-c; Batch B: D13) on the p14r contrac
  +> t.

Runs AFTER the p14r contract gate (code/p5_entry/release_p14.py, which writes certificates/P14_release.json) a
  +> nd
requires it to be accepted.  Recomputes (never trusts a stored Boolean alone):
  contract layer : P14_release.json accepted (classical claim, P3/P4 freeze, five P.5-entry flags, contract ha
  +> rd stops);
  contract identity : every p14r contract file byte-identical to its p14r sha256 EXCEPT the disclosed correcti
  +> on
                   (QC.DISCLOSED_CONTRACT_CORRECTIONS: code/p5_entry/dred.py, finding F1), whose regression to
  +> ys pass;
  library        : P15_integral_library.json (A0, B0, tensor reduction in ghat, S0) certified;
  batchA_evaluated : P15_batchA.json (status per graph, two routes, gate checks, D12 separate from the one-poi
  +> nt slot);
  D13_evaluated  : P15_D13.json (two routes exact in d, exact fit, ghost equation, c.K' / c.cb maps, 5 mutatio
  +> ns);
  hard stops     : QC.HARD_STOPS_P15 (quantum_inputs_evaluated etc. NOT earned; O.1 NOT_CLOSED; insertion froz
  +> en ...).
Rebuild flags (package evidence, not part of release_claim_accepted): author/independent for the CURRENT (p15)
  +>  tree;
independent_rebuild_passed_p14r from the archived p14r report, bound to the p14r tree/zip (same-box caveat).
Publication: P15_release.json (+ RELEASE_STATUS.json, ledgers/P15_milestones.json) only if accepted; otherwise
P15_release_rejected.json and exit 1.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p15_conventions as QC  # noqa: E402
import p14_conventions as PC  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)

ARCH_P14R = "archival/p14r"
ARCH_P14R_INDEP = f"{ARCH_P14R}/reproducibility/independent_rebuild_report_p14r.json"
D13_MUTATIONS = ("wrong_ghost_loop_sign", "premature_d4", "drop_evanescent_Gt", "wrong_symmetry_factor",
                 "wrong_K_c_ordering")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def contract_layer():
    r = jl("certificates/P14_release.json")
    ok = bool(r.get("revision") == PC.REVISION == QC.CONTRACT_REVISION and r.get("publication") == "accepted"
              and r.get("release_claim_accepted") is True and r.get("P5_entry_earned") is True
              and r.get("P3_P4_frozen_as_P5_inputs") is True and r.get("hard_stops_hold") is True
              and all(r.get("P5_entry_flags", {}).values()) and len(r.get("P5_entry_flags", {})) == 5
              and (ROOT / "certificates" / "P14_closure_release.json").is_file())
    return ok, r


def contract_identity():
    cur = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    changed = sorted(k for k, h in QC.P14R_CONTRACT_SHA256.items() if cur.get(k) != h)
    added = sorted(set(cur) - set(QC.P14R_CONTRACT_SHA256))
    disclosed = sorted(QC.DISCLOSED_CONTRACT_CORRECTIONS)
    dr = jl("certificates/P14_dred_rules.json")
    corr = dr.get("p15_contract_correction", {})
    toys = corr.get("regression_toys", {})
    toys_ok = bool(toys.get("pass") is True and toys.get("eta_trace_correct", {}).get("raised") is False
                   and toys.get("eta_trace_premature_d4", {}).get("raised") is True
                   and toys.get("A0_mixing", {}).get("mixed_refused") is True
                   and toys.get("B0_mixing", {}).get("mixed_refused") is True)
    dred_ok = bool(dr.get("dred_rules_verified") is True and dr.get("mutations_all_rejected") is True
                   and dr.get("mutations", {}).get("trace_ghat_eq_4", {}).get("structurally_refused") is True
                   and corr.get("released_p14r_values_affected") is False)
    ok = bool(changed == disclosed and not added and toys_ok and dred_ok)
    return ok, {"p14r_contract_files": len(QC.P14R_CONTRACT_SHA256), "changed": changed, "added": added,
                "disclosed_corrections": QC.DISCLOSED_CONTRACT_CORRECTIONS,
                "byte_identical_except_disclosed": changed == disclosed and not added,
                "regression_toys_pass": toys_ok, "dred_certificate_ok": dred_ok,
                "regression_toys": toys, "test_revisions_disclosed": QC.DISCLOSED_TEST_REVISIONS,
                "P3_P4_code": "frozen p13 classical code byte-identical (freeze F2, checked by the p14r contra
  +> ct gate)"}


def p14r_independent():
    f = ROOT / ARCH_P14R_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P14R_INDEP, "present": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P14R_INDEPENDENT_REPORT
    rec = {"report": ARCH_P14R_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P14R_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"),
           "bound_to_source_zip_sha256": rep.get("zip_sha256"),
           "tree_matches_p14r": rep.get("source_tree_sha256") == QC.P14R_SOURCE_TREE_SHA256,
           "zip_matches_p14r": rep.get("zip_sha256") == QC.P14R_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])), "findings": [x.get("id") for x in rep.get("findings",
  +>  [])],
           "caveat": rep.get("same_box_caveat"),
           "live_report_identical_to_archived": (live.is_file() and live.read_bytes() == f.read_bytes())
           if live.is_file() else "live report not in this tree",
           "NOT_inherited_by_p15": "bound to the p14r tree/zip; the p15 tree has its own (pending) independent
  +>  flag"}
    rec["archived_p14r_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                            for p, h in QC.P14R_ARCHIVED_RECORDS.items()}
    ok = bool(rec["report_sha256_pinned"] and all(rec["archived_p14r_records_pinned"].values()) and rep.get("p
  +> ass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p14r"] and rec["zip_matches_p14r"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def library():
    c = jl(f"certificates/{QC.CERT_PREFIX}_integral_library.json")
    return bool(c.get("library_certified") is True and c.get("revision") == QC.REVISION), c


def batch_a():
    c = jl(f"certificates/{QC.CERT_PREFIX}_batchA.json")
    if not c:
        return False, {}, c
    g = c.get("graphs", {})
    per = {k: {"status": g.get(k, {}).get("status"), "UV_pole": g.get(k, {}).get("UV_subtraction"),
               "finite_part": g.get(k, {}).get("finite_part"),
               "routes_agree": g.get(k, {}).get("verification_controls", {}).get(
                   "route1_dred_lift_equals_route2_symmetric_integration")} for k in QC.BATCH_A}
    ok = bool(c.get("revision") == QC.REVISION and set(g) == set(QC.BATCH_A)
              and all(v["status"] in QC.STATUS_VALUES and v["status"] != "unevaluated" for v in per.values())
              and all(v["routes_agree"] is True for v in per.values())
              and all(c.get("gate_checks", {}).values()) and c.get("gate_checks", {}).get("D12_separate_from_o
  +> ne_point_slot")
              and c.get("batchA_evaluated", {}).get("execution") is True
              and all(g[k].get("value_imported_from_XVI_O") is False for k in g))
    return ok, per, c


def d13():
    c = jl(f"certificates/{QC.CERT_PREFIX}_D13.json")
    if not c:
        return False, c
    muts = c.get("mutations", {})
    ok = bool(c.get("revision") == QC.REVISION and c.get("status") in QC.STATUS_VALUES
              and all(v is True for v in c.get("controls", {}).values()) and len(c.get("controls", {})) >= 10
              and sorted(muts) == sorted(D13_MUTATIONS)
              and all(v.get("rejected") is True and v.get("changes_result") is True for v in muts.values())
              and c.get("D13_evaluated", {}).get("execution") is True)
    return ok, c


def milestones(contract, a_ok, b_ok):
    st = dict(contract.get("milestones", {}).get("status", {}))
    st["P.5_calculation"] = ("opened (p15: Batch A D02/D12/D14a-c and Batch B D13 evaluated under the p14r "
                             "prescription; Batch C D01/D03 and the D11 matching M2 NOT evaluated)"
                             if a_ok and b_ok else "open (p15 evaluation not accepted)")
    st["P.5_identity"] = "open"
    return {"definitions": contract.get("milestones", {}).get("definitions"),
            "order": contract.get("milestones", {}).get("order"), "status": st,
            "P5_entry_earned": contract.get("P5_entry_earned"),
            "P3_P4_frozen_as_P5_inputs": contract.get("P3_P4_frozen_as_P5_inputs"),
            "P4_is_NOT": "coupled one-loop restoration (quantum_inputs_evaluated / projected_identity_verified
  +>  not earned)"}


def results_table(per, dc):
    rows = []
    for k in QC.BATCH_A:
        rows.append(f"{k} & {per[k]['status'].replace('_', chr(92) + '_')} & 0 & 0 \\\\")
    r = dc.get("result", {})
    pole = ", ".join(f"{k}: {r[k]['UV_pole']}" for k in ("T1", "T2", "T3", "E1", "E2") if k in r)
    loc = ", ".join(f"{k}: {r[k]['local_polynomial']}" for k in ("T1", "T2", "T3", "E1", "E2") if k in r)
    rows.append(f"D13 & {dc.get('status', '?')} (4D: renormalized) & {pole} & local {loc} \\\\")
    return ("% generated by code/p5_calc/release_p15.py -- do not edit\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{1.1cm}p{4.2cm}p{4.3cm}p{4.3cm}}\\hline\n"
            "graph & status & UV pole (units $\\kappa^2 N_\\epsilon/\\epsilon$) & finite part \\\\\\hline\n"
            + "\n".join(rows) + "\n\\hline\\end{tabular}\\end{center}\n")


def _main():
    c_ok, contract = contract_layer()
    id_ok, ident = contract_identity()
    lib_ok, lib = library()
    a_ok, per, ac = batch_a()
    b_ok, dc = d13()
    p14r_ok, p14r_rec = p14r_independent()
    flags = {
        "library_certified": lib_ok,
        "batchA_evaluated": {"execution": a_ok, "claim": ac.get("batchA_evaluated", {}).get("claim") if a_ok e
  +> lse
                             "not established", "scope": ac.get("batchA_evaluated", {}).get("scope")},
        "D13_evaluated": {"execution": b_ok, "claim": dc.get("D13_evaluated", {}).get("claim") if b_ok else
                          "not established", "scope": dc.get("D13_evaluated", {}).get("scope")},
    }
    d12 = ac.get("D12_slot", {})
    D12_status = d12.get("status") if (a_ok and d12.get("derivation")) else "Missing"
    hard = dict(QC.HARD_STOPS_P15)
    certs_claim = [jl(f"certificates/{QC.CERT_PREFIX}_{n}.json") for n in ("integral_library", "batchA", "D13"
  +> )]
    hard_ok = bool(all(hard[k] == v for k, v in QC.HARD_STOPS_P15.items())
                   and not any(c.get("quantum_inputs_evaluated") not in (None, "not_earned") for c in certs_cl
  +> aim)
                   and set(per) == set(QC.BATCH_A) and not set(QC.NOT_EVALUATED_P15) & set(per))
    execution_pass = bool(c_ok and id_ok and lib_ok and a_ok and b_ok and hard_ok)
    release_claim_accepted = execution_pass
    publish = release_claim_accepted
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    m = milestones(contract, a_ok, b_ok)
    graphs = {k: {**per[k], "kappa_order": ac["graphs"][k]["kappa_order"], "slot": ac["graphs"][k]["slot"]}
              for k in QC.BATCH_A} if a_ok else {}
    if b_ok:
        graphs["D13"] = {"status": dc["status"], "sector_status": dc["sector_status"],
                         "UV_pole": {k: v["UV_pole"] for k, v in dc["result"].items()},
                         "MSbar_finite": {k: v["MSbar_finite"] for k, v in dc["result"].items()},
                         "UV_pole_in_p14r_cK_basis": dc["UV_pole_in_p14r_cK_basis"]["coordinates"],
                         "evanescent_pole_nonzero": dc["evanescent_pole_nonzero"]}
    for k in QC.NOT_EVALUATED_P15:
        graphs[k] = {"status": "unevaluated"}
    cert = {
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DA
  +> TE,
        "deliverable": "P.5 calculation, first batch (Batch A: D02, D12, D14a-c; Batch B: D13)",
        "execution_pass": execution_pass,
        "claim_status": ("P.5_calculation: Batch A and D13 evaluated under the p14r prescription; P.5_entry: e
  +> arned "
                         "(p14r contract); classical_readiness (frozen P.4): earned") if execution_pass else
                        "P.5_calculation: not accepted",
        "scope": ("first P.5 calculation: the Batch A graphs (D02, D12, D14a-c) and the Batch B graph D13 eval
  +> uated "
                  "under the frozen p14r prescription (DRED R1-R6, Feynman +i0, MS-bar) with the explicit scal
  +> eless "
                  "rule S0; D01, D03, D11 NOT evaluated; no slot of the identity is complete; NOT quantum inpu
  +> ts, NOT "
                  "the projected defect/identity, NOT bulk restoration, NOT the insertion"),
        "release_claim_accepted": release_claim_accepted,
        "release_claim_accepted_definition": ("p14r contract accepted (P14_release.json) AND contract byte-ide
  +> ntity "
                                              "except the disclosed dred.py correction (regression toys pass) 
  +> AND "
                                              "library certified AND batchA_evaluated AND D13_evaluated AND p1
  +> 5 hard "
                                              "stops"),
        "publication": "accepted" if publish else "REJECTED",
        "flags": flags, "batchA_evaluated": a_ok, "D13_evaluated": b_ok, "library_certified": lib_ok,
        "graphs": graphs, "D12_status": D12_status,
        "D12_status_derivation": d12.get("derivation") if D12_status != "Missing" else None,
        "D12_previous_status": "Missing (p14r)",
        "one_point_slot_kappa1": ac.get("one_point_slot_kappa1"),
        "D13_summary": {k: dc.get(k) for k in ("status", "sector_status", "convention", "UV_pole_in_p14r_cK_ba
  +> sis",
                                                "local_polynomial_in_p14r_cK_basis", "MSbar_counterterm",
                                                "evanescent_pole_nonzero", "evanescent_counterterm_declared_in
  +> _p14r",
                                                "local_ambiguity", "renormalization_conditions", "controls")},
        "contract_identity": ident, "contract_correction_disclosed": True,
        "contract_layer": {"certificate": "certificates/P14_release.json", "accepted": c_ok,
                           "revision": contract.get("revision"),
                           "P5_entry_earned": contract.get("P5_entry_earned"),
                           "P5_entry_flags": contract.get("P5_entry_flags"),
                           "P3_P4_frozen_as_P5_inputs": contract.get("P3_P4_frozen_as_P5_inputs"),
                           "contract_hard_stops": contract.get("hard_stops"),
                           "note": ("the contract-layer statements (e.g. D12_status Missing, P5_calculation_op
  +> ened "
                                    "false) describe the p14r CONTRACT and are superseded for p15 by this stat
  +> us; the "
                                    "contract record's rebuild flags refer to the current tree through the p14
  +> r "
                                    "report paths and are superseded by the p15 flags below")},
        "P5_entry_earned": contract.get("P5_entry_earned"), "P5_entry_flags": contract.get("P5_entry_flags"),
        "P3_P4_frozen_as_P5_inputs": contract.get("P3_P4_frozen_as_P5_inputs"),
        "classical": contract.get("classical"),
        "D11_matching_verified": False,
        "hard_stops": hard, "hard_stops_hold": hard_ok,
        "milestones": m,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p14r": p14r_ok,
        "independent_rebuild_passed_p13": contract.get("independent_rebuild_passed_p13"),
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p15
  +> ) source "
                               "tree only; independent_rebuild_passed_p14r refers to the p14r tree "
                               f"{QC.P14R_SOURCE_TREE_SHA256} / zip {QC.P14R_SOURCE_ZIP_SHA256} (same-box cave
  +> at) and "
                               "is not inherited by p15; independent_rebuild_passed_p13 carries the P.3/P.4 fr
  +> eeze"),
        "p14r_independent_rebuild": p14r_rec,
        "p13_independent_rebuild": contract.get("p13_independent_rebuild"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_s
  +> ource.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p14r_archive": ARCH_P14R,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "XVI_M_sha256": contract.get("XVI_M_sha256"), "XVI_M_pin_ok": contract.get(
  +> "XVI_M_pin_ok"),
        "symmetry_restored": False, "bulk_symmetry_restored": False, "O1_closure": "NOT_CLOSED",
        "insertion_status": "Frozen_negative_obstruction_preserved", "XV_B_opened": False, "XIV_J_opened": Fal
  +> se,
        "Route_B_discharged": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
                   ("P14_release.json", "P14_dred_rules.json", f"{QC.CERT_PREFIX}_integral_library.json",
                    f"{QC.CERT_PREFIX}_batchA.json", f"{QC.CERT_PREFIX}_D13.json") if (ROOT / "certificates" /
  +>  n).is_file()},
    }
    cdir = ROOT / "certificates"
    txt = certio.dumps(cert)
    if publish:
        (ROOT / "RELEASE_STATUS.json").write_text(txt)
        (cdir / "RELEASE_STATUS.json").write_text(txt)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release.json").write_text(txt)
        certio.write(ROOT / "ledgers" / f"{QC.CERT_PREFIX}_milestones.json", {
            "landmark": "XVI-P", "revision": QC.REVISION, "ledger": "milestones (authoritative definitions + s
  +> tatus)",
            **m, "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
            "independent_rebuild_passed_p14r": p14r_ok, "hard_stops": hard,
            "flags": {"batchA_evaluated": a_ok, "D13_evaluated": b_ok, "library_certified": lib_ok}})
        (ROOT / "manuscript" / "body").mkdir(parents=True, exist_ok=True)
        (ROOT / "manuscript" / "body" / "P15-results-table.tex").write_text(results_table(per, dc))
    else:
        (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(certio.dumps({
            "landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED",
            "contract_layer_accepted": c_ok, "contract_identity_ok": id_ok, "contract_identity": ident,
            "library_certified": lib_ok, "batchA_evaluated": a_ok, "D13_evaluated": b_ok, "hard_stops_hold": h
  +> ard_ok}))
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publicat
  +> ion"],
                      "contract_layer": c_ok, "contract_identity": id_ok, "changed_contract_files": ident["cha
  +> nged"],
                      "library": lib_ok, "batchA_evaluated": a_ok, "D13_evaluated": b_ok, "D12_status": D12_st
  +> atus,
                      "hard_ok": hard_ok, "author": author_ok, "independent_p15": indep_ok,
                      "independent_p14r": p14r_ok}, indent=1))
    return 0 if publish else 1


def main():
    try:
        return _main()
    except Exception as exc:  # noqa: BLE001   fail closed
        cdir = ROOT / "certificates"
        (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(json.dumps(
            {"landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED",
             "error": f"{type(exc).__name__}: {exc}"}, indent=1) + "\n")
        print(f"release_p15 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
