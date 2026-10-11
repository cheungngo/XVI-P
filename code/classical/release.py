#!/usr/bin/env python3
"""XVI-P p13 acceptance / release gate (assembled from the P13 certificates only).

p12 additions: residual-record invariant (Q_identically_zero == all(Q_terms == 0)) re-checked on EVERY certificate;
per-order acceptance Q_terms == [0,0,0,0] and Q_identically_zero at kappa0..kappa2 recomputed from the quartic AND
master records (never trusted from a stored Boolean); cross-certificate agreement (same export hashes + transformation
parameters => identical residual records).  Any failure => release_claim_accepted = false => publication rejected.

execution_pass         : the pipeline ran and every hard stop holds (package consistency).
claim_status           : the classical-readiness claim (five-flag conjunction), separate from execution.
scope                  : what the claim is about.
release_claim_accepted : execution_pass AND classical_readiness AND every acceptance prerequisite is
                         deterministic and true AND hash consistency (export file == quartic cert == master inputs).
p13 additions: milestone definitions/status (conventions.MILESTONES; P.4 = classical readiness, NOT coupled one-loop
restoration), the milestone ledger ledgers/P13_milestones.json, and the reproducibility flags
  author_rebuild_passed       : reproducibility/author_rebuild_report.json passed AND was produced from exactly the
                                current source tree (source_tree_sha256 equal) -- otherwise false;
  independent_rebuild_passed  : "pending" until reproducibility/independent_rebuild_report.json exists (written by a
                                separate clean environment); then the same binding rule.
These are package evidence (XVI-O conv:package), not mathematical certificates, and do not enter
release_claim_accepted.  Certificate input hashes are content hashes with wall-clock timings removed.

Publication rule (p11): the final closure artifacts (certificates/P13_release.json, certificates/P13_closure_release.json)
are written ONLY if release_claim_accepted and classical_readiness are both true.  Otherwise any stale closure artifact is
deleted, certificates/P13_release_rejected.json is written, RELEASE_STATUS.json records the rejection, and the exit is 1.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
import conventions as C  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402

import inherited  # noqa: E402


def j(name):
    return json.loads((ROOT / "certificates" / name).read_text())


def rebuild_flag(report_rel, pending_if_absent):
    f = ROOT / report_rel
    cur = SM.tree_sha(ROOT)
    if not f.exists():
        return ("pending" if pending_if_absent else False), {"report": report_rel, "present": False,
                                                              "current_source_tree_sha256": cur}
    try:
        rep = json.loads(f.read_text())
    except Exception as exc:  # noqa: BLE001
        return False, {"report": report_rel, "present": True, "error": str(exc)}
    same = rep.get("source_tree_sha256") == cur
    ok = rep.get("pass") is True and same
    return ok, {"report": report_rel, "present": True, "report_pass": rep.get("pass"),
                "report_source_tree_sha256": rep.get("source_tree_sha256"), "current_source_tree_sha256": cur,
                "bound_to_current_source": same,
                # the report's source_zip_sha256 is NOT copied here: the zip is a manifest-listed file and its hash must
                # not appear inside the PDFs (this record is typeset); build.py checks it against dist/ at the manifest gate
                "report_records_source_zip_sha256": "source_zip_sha256" in rep,
                "inherited_mode": rep.get("inherited_mode"), "environment": rep.get("environment")}


def milestones(ch, gi_names_tbd, conj, accepted, independent):
    p3 = bool(ch["ch_projection_defined"] and ch["ch_dependency_inventory_complete"] and ch["enumeration_lemma"]["holds"]
              and ch["checks"]["regenerated_rows_match_published"] and gi_names_tbd == [])
    p4 = bool(conj and accepted)
    st = {"P.3": "complete (declared ch target)" if p3 else "incomplete",
          "P.4": "earned (classical readiness)" if p4 else "not_earned",
          "P.5_entry": "next (not started; p13 does no P.5 work)",
          "P.5_calculation": "open", "P.5_identity": "open"}
    return {"definitions": C.MILESTONES, "order": list(C.MILESTONE_ORDER), "status": st,
            "P3_complete": p3, "P4_classical_readiness_earned": p4,
            "P4_is_NOT": "coupled one-loop restoration (quantum_inputs_evaluated / projected_identity_verified not earned)",
            "P3_P4_frozen_as_P5_inputs": independent is True,
            "frozen_rule": "P.3/P.4 become frozen P.5 inputs only after independent_rebuild_passed is true",
            "history": C.MILESTONE_HISTORY,
            "XVI_O_unaffected": "XVI-P is unregistered package evidence; XVI-O prop:kappa2-master stays Partial"}


def _main():
    try:
        pin = inherited.sha(inherited.resolve("XVI-M.tex"))
    except inherited.PinError:
        pin = "unavailable"
    pin_ok = pin == C.XVI_M_PIN
    q, br, sa = j("P13_quartic_verified.json"), j("P13_brst_derivation.json"), j("P13_source_action.json")
    gf, ms, ch = j("P13_gauge_fixing_map.json"), j("P13_master_kappa2.json"), j("P13_ch_source_audit.json")
    bi = j("P13_boundary_identity.json")
    flags = {
        "quartic_generator_verified": bool(q["quartic_generator_verified"]),
        "ch_projection_defined": bool(ch["ch_projection_defined"]),
        "ch_dependency_inventory_complete": bool(ch["ch_dependency_inventory_complete"]),
        "gauge_fixing_map_constructed": bool(gf["gauge_fixing_map_constructed"]),
        "required_classical_BV_components_verified": bool(ms["required_classical_BV_components_verified"]),
    }
    residuals = list(ms["required_master_residuals"])
    # ---- hash consistency: export files == quartic certificate == master inputs ----
    import sympy as sp
    file_sha = {}
    for k in (2, 3, 4):
        txt = (ROOT / "exports" / f"ell{k}_generating_polynomial.srepr").read_text().strip()
        file_sha[k] = hashlib.sha256(str(sp.sympify(txt)).encode()).hexdigest()
    hashes = {f"ell{k}": {"export_file": file_sha[k], "quartic_cert": q.get(f"ell{k}_sha256"),
                          "master_input": ms["identification_with_exports"]["ell2_ell3_ell4"][str(k)]["sha256"]
                          if str(k) in ms["identification_with_exports"]["ell2_ell3_ell4"]
                          else ms["identification_with_exports"]["ell2_ell3_ell4"][k]["sha256"]} for k in (2, 3, 4)}
    hash_consistent = all(len({v["export_file"], v["quartic_cert"], v["master_input"]}) == 1 for v in hashes.values())
    # ---- deterministic acceptance prerequisites ----
    gdet = ms["details"]["grav_af0_deterministic"]
    hess = gf["propagators"]["graviton"]
    det_prereq = {
        "C1_inverse_10comp": q["acceptance_controls_deterministic"]["C1"],
        "C2_det_tracelog_10comp": q["acceptance_controls_deterministic"]["C2"],
        "C3_boundary_identity_generic_and_conformal": bool(bi["C3_proved"]) and q["acceptance_controls_deterministic"]["C3"],
        "C4_export_equals_independent_evaluator": q["acceptance_controls_deterministic"]["C4"],
        "C5_cubic_regression_Euler": q["acceptance_controls_deterministic"]["C5"],
        "C6_quadratic_regression_Euler": q["acceptance_controls_deterministic"]["C6"],
        "C7_grav_noether_k0_k1_k2_on_exports": q["acceptance_controls_deterministic"]["C7"],
        "quartic_mutations_all_rejected": bool(q["mutations_all_rejected"]),
        "master_grav_noether_deterministic_k0_k1_k2": all(gdet[f"kappa{n}"]["Q_identically_zero"] for n in (0, 1, 2)),
        "master_engine_parts_exact": not [r for r in residuals],
        "graviton_hessian_generic_symbolic_k": bool(hess.get("schur_equals_k2P")) and bool(hess.get("propagator_hh_equals_inv_k2P"))
                                               and "generic" in str(hess.get("momentum", "")),
        "canonicity_all_23_antifield_components": bool(gf["canonicity"]["pass"]) and gf["canonicity"]["pairs_tested"] == 299,
        "ch_enumeration_lemma_mechanical": bool(ch["enumeration_lemma"]["holds"]),
    }
    # ---- p12: residual-record invariants, per-order acceptance, cross-certificate agreement ----
    allc = {"quartic": q, "brst": br, "source": sa, "gauge": gf, "master": ms, "ch": ch, "boundary": bi}
    inv_bad = {k: certio.invariant_violations(v) for k, v in allc.items()}
    inv_bad = {k: v for k, v in inv_bad.items() if v}
    q_c7 = q["controls"]["C7_noether_exact"]
    acc_q = certio.accepted_orders(q_c7)
    acc_m = certio.accepted_orders(gdet)
    cross = certio.cross_check(q_c7, q["controls"].get("C7_parameters"), gdet, ms["details"].get("grav_af0_parameters"))
    stored_vs_recomputed = (q["acceptance_controls_deterministic"]["C7"] == all(acc_q.values()))
    det_prereq.update({
        "residual_record_invariants_all_certificates": not inv_bad,
        "quartic_C7_Q_terms_zero_and_flag_true_all_orders": all(acc_q.values()),
        "master_grav_Q_terms_zero_and_flag_true_all_orders": all(acc_m.values()),
        "cross_certificate_quartic_vs_master_agree": cross["agree"],
        "stored_C7_flag_equals_recomputation": stored_vs_recomputed,
    })
    det_prereq["C7_grav_noether_k0_k1_k2_on_exports"] = det_prereq["C7_grav_noether_k0_k1_k2_on_exports"] and all(acc_q.values())
    det_prereq["master_grav_noether_deterministic_k0_k1_k2"] = det_prereq["master_grav_noether_deterministic_k0_k1_k2"] and all(acc_m.values())
    deterministic_ok = all(det_prereq.values())
    failed_prereq = [k for k, v in det_prereq.items() if not v] + ([] if hash_consistent else ["hash_consistency"])
    flags["quartic_generator_verified"] = (flags["quartic_generator_verified"] and hash_consistent and bool(bi["C3_proved"])
                                           and all(acc_q.values()) and "quartic" not in inv_bad)
    flags["required_classical_BV_components_verified"] = (flags["required_classical_BV_components_verified"]
                                                          and hash_consistent and not residuals and all(acc_m.values())
                                                          and cross["agree"] and "master" not in inv_bad)
    conj = all(flags.values())
    hard = dict(C.HARD_STOPS)
    hard_ok = (hard["quantum_inputs_evaluated"] == "not_earned" and hard["projected_identity_verified"] == "not_earned"
               and hard["D02_quantum_evaluated"] is False and hard["D12_quantum_evaluated"] is False
               and hard["D12_status"] == "Missing" and hard["symmetry_restored"] is False
               and hard["O1_closure"] == "NOT_CLOSED" and hard["XV_B_opened"] is False
               and hard["Route_B_discharged"] is False and hard["loop_evaluations_performed"] is False
               and hard["u_R_c_delta_added"] is False
               and q["D02_quantum_evaluated"] is False)
    execution_pass = bool(pin_ok and hard_ok and all(x["execution_pass"] for x in (q, br, sa, gf, ms, ch)))
    statuses = {k: ("earned" if v else "Partial") for k, v in flags.items()}
    release_claim_accepted = bool(execution_pass and conj and deterministic_ok and hash_consistent)
    statuses.update({
        "classical_readiness_for_ch_identity": "earned" if conj else "not_earned",
        "quantum_inputs_evaluated": "not_earned",
        "projected_identity_verified": "not_earned",
        "propagators_match_transformed_Hessians": bool(gf["propagators_match_transformed_Hessians"]),
        "source_identity_relation_defined": bool(gf["source_identity_relation_defined"]),
        "source_identity_relation": ("defined classical pullback/interface (related, not identical): "
                                     "Gamma_Psi(Phi,Phi*') := Gamma(Phi, Phi*' - dPsi/dPhi); not a quantum theorem"),
        "D02_vertex_available": bool(q["D02_vertex_available"]),
        "D02_quantum_evaluated": False, "D12_quantum_evaluated": False, "D12_status": "Missing",
    })
    author_ok, author_rec = rebuild_flag("reproducibility/author_rebuild_report.json", pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag("reproducibility/independent_rebuild_report.json", pending_if_absent=True)
    gi = json.loads((ROOT / "ledgers" / "P13_graph_inventory.json").read_text())
    ms_block = milestones(ch, gi.get("names_TBD"), conj, release_claim_accepted, indep_ok)
    surviving = [{"row": r["id"], "Gamma1_pattern": r["Gamma1_pattern"], "graphs": r["graphs"],
                  "value": "not evaluated in this release (D11 inherited from O5, not re-evaluated)"}
                 for r in ch["surviving_rows"]]
    cert = {
        "landmark": "XVI-P", "revision": C.REVISION, "date": C.DATE, "deliverable": "evidence_and_closure",
        "execution_pass": execution_pass,
        "claim_status": "classical_readiness_for_ch_identity: " + ("earned" if conj else "not_earned"),
        "scope": ("classical readiness for the fixed one-loop kappa^2 ch identity on the S_inv baseline (declared "
                  "conventions, affine metric, a=1/2, linear de Donder Psi, massless scalar); classical only; "
                  "NOT quantum inputs, NOT the projected identity, NOT the prepared S_D, NOT the insertion"),
        "execution_pass_means": "pipeline executed in dependency order; every hard stop holds; pin verified. "
                                "Does NOT mean any classical or quantum claim.",
        "release_claim_accepted": release_claim_accepted,
        "release_claim_accepted_definition": ("execution_pass AND classical_readiness_for_ch_identity AND all "
                                              "deterministic acceptance prerequisites AND hash consistency"),
        "deterministic_prerequisites": det_prereq, "failed_prerequisites": failed_prereq,
        "hash_consistency": {"consistent": hash_consistent, "ell": hashes},
        "residual_records": {"invariant_violations": inv_bad,
                             "quartic_C7_per_order": {o: {"residual_counts": q_c7[o]["Q_terms"], "zero_flag": q_c7[o]["Q_identically_zero"],
                                                          "accepted": acc_q[o]} for o in certio.ORDERS},
                             "master_grav_per_order": {o: {"residual_counts": gdet[o]["Q_terms"], "zero_flag": gdet[o]["Q_identically_zero"],
                                                           "accepted": acc_m[o]} for o in certio.ORDERS},
                             "cross_certificate": cross},
        "sampled_checks_role": "regression controls only (never acceptance): numeric evaluator samples, plane-wave "
                               "cubic/Noether samples",
        "flags": flags, "classical_readiness_for_ch_identity": conj,
        "classical_readiness_conjunction_definition": " AND ".join(flags),
        "statuses": statuses,
        "required_master_residuals": residuals,
        "closed_blocker": {"id": "complete_af_ghost_O_kappa2_on_D_h",
                           "closed": not residuals and flags["required_classical_BV_components_verified"],
                           "by": "P13_master_kappa2.json (transformed and invariant variables, by antifield number; "
                                 "grav af0 deterministic)"},
        "boundary_identity": {"statement": C.BOUNDARY_IDENTITY, "C3_proved": bi["C3_proved"],
                              "orientation_correction": bi.get("orientation_correction"),
                              "integrated_action_unaffected": bi.get("integrated_action_unaffected")},
        "s2_per_sector": br["s2_per_sector"], "s2_reason": br["s2_reason"],
        "master_table": ms["table_by_kappa_and_antifield_number"],
        "mixed_cancellations": ms["mixed_cancellations"],
        "derived_signs": {"sigma_A": sa["sigma"], "antifield_shift_eps": gf["derived_eps"],
                          "S_Psi": "S + s Psi (mod d)", "odd_Psi_left_equals_right": gf["left_equals_right_for_odd_Psi"]},
        "ch_surviving_rows_unevaluated": surviving,
        "graph_inventory": "ledgers/P13_graph_inventory.json",
        "source_identity_interface": ("Gamma_Psi(Phi,Phi*') := Gamma(Phi, Phi*' - dPsi/dPhi): defined classical "
                                      "pullback/interface, NOT an independently established quantum gauge-change theorem"),
        "remaining_blockers_outside_classical_scope": [
            {"id": "Gamma1_one_loop_coefficients (D01,D02,D03,D11,D12,D13,D14a-c)",
             "status": "not evaluated in this release (D11: inherited O5 kernel under prescription, not re-evaluated)",
             "blocks": "quantum_inputs_evaluated"},
            {"id": "D12_quantum_evaluation", "status": "Missing", "blocks": "quantum_inputs_evaluated"},
            {"id": "D02_quantum_tadpole_evaluation", "status": "not_performed (vertex available)",
             "blocks": "quantum_inputs_evaluated"},
        ],
        "hard_stops": hard, "hard_stops_hold": hard_ok,
        "milestones": ms_block,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_source.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False,
        "symmetry_restored": False, "O1_closure": "NOT_CLOSED",
        "insertion_status": "Frozen_negative_obstruction_preserved", "XV_B_opened": False, "Route_B_discharged": False,
        "P5_opened": False,
        "obstruction": "XVI-N thm:massless-obstruction respected: no completion of the prepared/inserted functional is "
                       "claimed; the closure is the S_inv classical master equation only. No c delta added to u^R_mu "
                       "(XVI-J prop:extension).",
        "not_premises": C.NOT_PREMISES,
        "baseline": C.BASELINE, "ghost_normalization_a": "1/2",
        "XVI_M_sha256": pin, "XVI_M_pin_ok": pin_ok,
        "XVI_A_to_O_edited": False, "XVI_O_o70_sync": "read-only",
        "inputs_content_sha256_ignoring_timings": {n: certio.file_content_sha(ROOT / "certificates" / n) for n in
                   ("P13_quartic_verified.json", "P13_boundary_identity.json", "P13_brst_derivation.json",
                    "P13_source_action.json", "P13_gauge_fixing_map.json", "P13_master_kappa2.json",
                    "P13_ch_source_audit.json")},
    }
    cdir = ROOT / "certificates"
    closure = [cdir / "P13_release.json", cdir / "P13_closure_release.json"]
    publish = release_claim_accepted and conj
    cert["publication"] = "accepted" if publish else "REJECTED"
    txt = certio.dumps(cert)
    (ROOT / "RELEASE_STATUS.json").write_text(txt)
    (cdir / "RELEASE_STATUS.json").write_text(txt)
    certio.write(ROOT / "ledgers" / "P13_milestones.json", {
        "landmark": "XVI-P", "revision": C.REVISION, "ledger": "milestones (authoritative definitions + status)",
        **ms_block, "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "hard_stops": hard, "dossier": "certificates/P13_dossier.json"})
    if publish:
        (cdir / "P13_release_rejected.json").unlink(missing_ok=True)
        closure[0].write_text(txt)
        closure[1].write_text(certio.dumps({
            "landmark": "XVI-P", "revision": C.REVISION, "closed_blocker": cert["closed_blocker"],
            "release_claim_accepted": True, "classical_readiness_for_ch_identity": True, "flags": flags,
            "scope": cert["scope"], "quantum_inputs_evaluated": "not_earned", "symmetry_restored": False,
            "O1_closure": "NOT_CLOSED", "release_certificate": "certificates/P13_release.json",
            "hashes_of_release_files": "external manifest only (RELEASE_MANIFEST_EXTERNAL.txt)"}))
    else:
        for f in closure:
            f.unlink(missing_ok=True)
        (cdir / "P13_release_rejected.json").write_text(certio.dumps({
            "landmark": "XVI-P", "revision": C.REVISION, "publication": "REJECTED",
            "release_claim_accepted": release_claim_accepted, "classical_readiness_for_ch_identity": conj,
            "execution_pass": execution_pass, "flags": flags, "failed_prerequisites": failed_prereq,
            "required_master_residuals": residuals, "hash_consistency": hash_consistent}))
    print(json.dumps({"execution_pass": execution_pass, "flags": flags, "conj": conj, "residuals": residuals,
                      "release_claim_accepted": release_claim_accepted, "failed_prerequisites": failed_prereq,
                      "publication": cert["publication"], "pin_ok": pin_ok}, indent=1))
    return 0 if publish else 1


def reject_on_error(exc):
    """Fail closed: an unreadable/inconsistent certificate set is a rejection, never a crash that leaves artifacts."""
    cdir = ROOT / "certificates"
    for f in (cdir / "P13_release.json", cdir / "P13_closure_release.json"):
        f.unlink(missing_ok=True)
    rec = {"landmark": "XVI-P", "revision": C.REVISION, "publication": "REJECTED", "release_claim_accepted": False,
           "classical_readiness_for_ch_identity": False, "error": f"{type(exc).__name__}: {exc}",
           "failed_prerequisites": ["release_evaluation_error"]}
    txt = certio.dumps(rec)
    (cdir / "P13_release_rejected.json").write_text(txt)
    (ROOT / "RELEASE_STATUS.json").write_text(txt)
    (cdir / "RELEASE_STATUS.json").write_text(txt)
    print(json.dumps({"publication": "REJECTED", "error": rec["error"]}))
    return 1


def main():
    try:
        return _main()
    except Exception as exc:  # noqa: BLE001
        return reject_on_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())
