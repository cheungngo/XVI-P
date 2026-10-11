#!/usr/bin/env python3
"""XVI-P p16 release gate: P.5 calculation, second step -- E2 evanescent analysis (priority 1) and Batch C (D01, D03),
on the p14r contract with the disclosed p15 (F1) and p16 (F3) dred.py revisions.

Runs AFTER the p14r contract gate (release_p14.py -> certificates/P14_release.json) and the p15 layer gate
(release_p15.py -> certificates/P15_release.json) and requires both to be accepted.  Recomputes:
  contract identity : p14r contract files byte-identical to p14r EXCEPT code/p5_entry/dred.py (disclosed p15 F1 + p16
                      F3); NO new contract file (the E2 decoupling is proven, no evanescent counterterm added);
                      dred.py F3 hardening active (replace / lambdify / match refused outside substitute_d);
  p15 layer        : every p15 calculation file byte-identical to the p15 zip (QC.P15_CALC_SHA256); P15_release
                      accepted (Batch A, D13);
  E2               : P16_E2_evanescent.json -- decoupling proof controls all true, mutations rejected;
  batchC_evaluated : P16_batchC.json -- D01, D03 (covariant route, two loop routes, regeneration, hh basis, mutations);
  hard stops       : QC.HARD_STOPS_P16 (D11 NOT evaluated; quantum_inputs_evaluated not_earned; ...).
Rebuild flags (package evidence): author/independent for the CURRENT (p16) tree; independent_rebuild_passed_p15 from
the archived p15 independent report, bound to the p15 tree 79f53752... / zip 54325c1f... (same-box caveat).
Change log (F5): every source file added/modified/removed relative to the p15 source-only zip, contract and
non-contract, is listed in the status (change_log_vs_p15).
"""
from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p16_conventions as QC  # noqa: E402
import p15_conventions as Q15  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)

ARCH_P15 = "archival/p15"
ARCH_P15_INDEP = f"{ARCH_P15}/reproducibility/independent_rebuild_report_p15.json"
E2_MUTATIONS = ("M1_gauge_fixed_operator_qq2P", "M2_E1_in_place_of_E2", "M3_wrong_index_slot")
C_MUTATIONS = ("wrong_ghost_loop_sign_D03", "wrong_symmetry_factor_D01", "premature_d4", "drop_evanescent_gt",
               "wrong_external_index_position", "wrong_offdiagonal_weight", "component_route_linear_realization")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def contract_identity():
    cur = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    changed = sorted(k for k, h in Q15.P14R_CONTRACT_SHA256.items() if cur.get(k) != h)
    added = sorted(set(cur) - set(Q15.P14R_CONTRACT_SHA256))
    dred_changed_vs_p15 = cur.get("code/p5_entry/dred.py") != QC.P15_DRED_SHA256
    f3 = f3_hardening()
    ok = bool(changed == sorted(QC.P14R_CONTRACT_FILES_CHANGED_IN_P16) and added == sorted(QC.NEW_CONTRACT_FILES_P16)
              and dred_changed_vs_p15 and f3["all_refused"] and f3["authorised_path_works"])
    return ok, {"p14r_contract_files": len(Q15.P14R_CONTRACT_SHA256), "changed_vs_p14r": changed, "added": added,
                "dred_changed_vs_p15": dred_changed_vs_p15, "disclosed_revisions_p16": QC.DISCLOSED_CONTRACT_REVISIONS_P16,
                "disclosed_corrections_p15": Q15.DISCLOSED_CONTRACT_CORRECTIONS, "F3_probe": f3,
                "evanescent_counterterm_added": False,
                "why_no_evanescent_counterterm": "E2 decoupling from the ch-projected slot proven (P16_E2_evanescent.json)"}


def f3_hardening():
    import dred
    import sympy as sp
    d = dred.d
    e = (d - 4) / (d - 1) + d ** 2
    probes = {"expr.replace(d, 4)": lambda: e.replace(d, 4), "sympy.lambdify(d, expr)": lambda: sp.lambdify(d, e),
              "expr.match(d)": lambda: e.match(d), "expr.subs(d, 4)": lambda: e.subs(d, 4),
              "expr.xreplace({d: 4})": lambda: e.xreplace({d: 4}), "expr.evalf(subs={d: 4})": lambda: e.evalf(subs={d: 4})}
    res = {}
    for k, f in probes.items():
        try:
            f()
            res[k] = "NOT refused"
        except dred.PrematureD4Substitution:
            res[k] = "refused"
    auth = dred.substitute_d(e, 4, "release_p16.f3_hardening: authorised-path probe") == 16
    return {"probes": res, "all_refused": all(v == "refused" for v in res.values()), "authorised_path_works": auth}


def p15_layer():
    cur = {k: sha(ROOT / k) if (ROOT / k).is_file() else None for k in QC.P15_CALC_SHA256}
    ident = all(cur[k] == h for k, h in QC.P15_CALC_SHA256.items())
    r = jl("certificates/P15_release.json")
    ok = bool(ident and r.get("publication") == "accepted" and r.get("release_claim_accepted") is True
              and r.get("batchA_evaluated") is True and r.get("D13_evaluated") is True
              and r.get("library_certified") is True and r.get("hard_stops_hold") is True)
    return ok, {"p15_calc_files_byte_identical": ident, "P15_release_accepted": r.get("publication") == "accepted",
                "batchA_evaluated": r.get("batchA_evaluated"), "D13_evaluated": r.get("D13_evaluated"),
                "D12_status": r.get("D12_status")}, r


def p15_independent():
    f = ROOT / ARCH_P15_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P15_INDEP, "present": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P15_INDEPENDENT_REPORT
    rec = {"report": ARCH_P15_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P15_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"),
           "bound_to_source_zip_sha256": rep.get("zip_sha256"),
           "tree_matches_p15": rep.get("source_tree_sha256") == QC.P15_SOURCE_TREE_SHA256,
           "zip_matches_p15": rep.get("zip_sha256") == QC.P15_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])), "findings": [x.get("id") for x in rep.get("findings", [])],
           "caveat": rep.get("same_box_caveat"),
           "live_report_identical_to_archived": (live.read_bytes() == f.read_bytes()) if live.is_file()
           else "live report not in this tree",
           "NOT_inherited_by_p16": "bound to the p15 tree/zip; the p16 tree has its own (pending) independent flag"}
    rec["archived_p15_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P15_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p15_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p15"] and rec["zip_matches_p15"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def e2():
    c = jl(f"certificates/{QC.CERT_PREFIX}_E2_evanescent.json")
    muts = c.get("mutations", {})
    ok = bool(c.get("revision") == QC.REVISION and c.get("E2_decoupling_proven") is True
              and all(v is True for v in c.get("controls", {}).values()) and len(c.get("controls", {})) >= 9
              and sorted(muts) == sorted(E2_MUTATIONS)
              and all(v.get("accepted_as_rejection") is True for v in muts.values()))
    return ok, c


def batch_c():
    c = jl(f"certificates/{QC.CERT_PREFIX}_batchC.json")
    g = c.get("graphs", {})
    muts = c.get("mutations", {})
    ok = bool(c.get("revision") == QC.REVISION and set(g) == set(QC.BATCH_C)
              and all(v.get("evaluated") is True and v.get("status") in QC.STATUS_VALUES
                      and v.get("status") != "unevaluated" for v in g.values())
              and all(all(x is True for x in v.get("controls", {}).values()) for v in g.values())
              and all(v is True for v in c.get("controls", {}).values())
              and sorted(muts) == sorted(C_MUTATIONS)
              and all(v.get("accepted_as_rejection") is True for v in muts.values())
              and c.get("batchC_evaluated", {}).get("execution") is True)
    return ok, c


def change_log():
    """F5: every source file added / modified / removed relative to the released p15 source-only zip.  The base is the
    pinned per-file list archival/p15/p15_source_files.json (so the log is identical in a source-only tree)."""
    f = ROOT / QC.P15_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P15_ARCHIVED_RECORDS[QC.P15_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT) if r != SM.REFERENCE_FILE}   # reference: written after the build
    contract = set(Q15.P14R_CONTRACT_SHA256) | {p.relative_to(ROOT).as_posix() for p in (ROOT / "code" / "p5_entry").glob("*.py")}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])
    changed = sorted(added + removed + modified)
    return {"base": f"{QC.P15_SOURCE_LIST} (pinned; files of the p15 zip sha256 {QC.P15_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok, "excluded": f"{SM.REFERENCE_FILE} (new in p16; written after the author build)", "added": added, "removed": removed, "modified": modified,
            "contract_files_changed": [x for x in changed if x in contract],
            "non_contract_files_changed": [x for x in changed if x not in contract],
            "counts": {"added": len(added), "removed": len(removed), "modified": len(modified)}}


def milestones(p15r, c_ok, e_ok):
    st = dict(p15r.get("milestones", {}).get("status", {}))
    st["P.5_calculation"] = ("in progress (p15: Batch A D02/D12/D14a-c and Batch B D13; p16: E2 decoupled from the ch "
                             "slot (proof), Batch C D01/D03 evaluated; D11 matching M2 NOT evaluated)"
                             if c_ok and e_ok else "open (p16 evaluation not accepted)")
    st["P.5_identity"] = "open"
    return {"definitions": p15r.get("milestones", {}).get("definitions"), "order": p15r.get("milestones", {}).get("order"),
            "status": st, "P5_entry_earned": p15r.get("P5_entry_earned"),
            "P3_P4_frozen_as_P5_inputs": p15r.get("P3_P4_frozen_as_P5_inputs"),
            "P4_is_NOT": "coupled one-loop restoration (quantum_inputs_evaluated / projected_identity_verified not earned)"}


def tex(x):
    """plain text-mode rendering (no math mode): ** -> ^, * kept, TeX specials escaped, typewriter font."""
    t = str(x).replace("**", "^").replace("\\", "/").replace("_", "\\_").replace("^", "\\^{}").replace("&", "\\&")
    return "\\texttt{" + t + "}"


def results_table(bc, ec):
    rows = []
    for g in QC.BATCH_C:
        for lab, v in bc["graphs"][g]["result"].items():
            rows.append(f"{g} & {tex(lab)} & {tex(v['A_exact_d_times_MB'])} & {tex(v['UV_pole'])} & "
                        f"{tex(v['MSbar_finite'])} \\\\")
    st = " ".join(f"{g}: {bc['graphs'][g]['status']}." for g in QC.BATCH_C)
    return ("% generated by code/p5_calc/release_p16.py -- do not edit\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{0.7cm}p{2.9cm}p{3.7cm}p{1.4cm}p{3.3cm}}\\hline\n"
            "graph & structure & $A(d)$ (coefficient of MB) & UV pole & MS-bar finite \\\\\\hline\n"
            + "\n".join(rows) + "\n\\hline\\end{tabular}\\end{center}\n"
            f"\\noindent Status: {st} E2 (D13): {ec.get('outcome')}.\n")


def _main():
    id_ok, ident = contract_identity()
    l15_ok, l15, p15r = p15_layer()
    e_ok, ec = e2()
    c_ok, bc = batch_c()
    p15i_ok, p15i = p15_independent()
    p14r = jl("certificates/P14_release.json")
    hard = dict(QC.HARD_STOPS_P16)
    graphs = dict(p15r.get("graphs", {}))
    for g in QC.BATCH_C:
        if c_ok:
            gg = bc["graphs"][g]
            graphs[g] = {"status": gg["status"], "sector_status": gg["sector_status"],
                         "UV_pole": {k: v["UV_pole"] for k, v in gg["result"].items()},
                         "MSbar_finite": {k: v["MSbar_finite"] for k, v in gg["result"].items()},
                         "UV_pole_in_p14r_hh_basis": gg["UV_pole_in_p14r_hh_basis"],
                         "evanescent_pole_nonzero": gg["evanescent_pole_nonzero"]}
        else:
            graphs[g] = {"status": "unevaluated"}
    graphs["D11"] = {"status": "unevaluated", "reason": "M2 undischarged (D11 matching not verified)"}
    if "D13" in graphs and e_ok:
        graphs["D13"]["E2_ch_slot"] = ec.get("E2_status")
    hard_ok = bool(all(hard[k] == v for k, v in QC.HARD_STOPS_P16.items())
                   and graphs.get("D11", {}).get("status") == "unevaluated"
                   and not any(c.get("quantum_inputs_evaluated") not in (None, "not_earned") for c in (ec, bc))
                   and p14r.get("hard_stops_hold") is True and p15r.get("hard_stops_hold") is True)
    cl = change_log()
    # integrity (fail closed): the archived p15 records are pinned inputs; a tampered archive rejects publication
    # (the VALUE of independent_rebuild_passed_p15 is package evidence, reported as a flag)
    execution_pass = bool(id_ok and l15_ok and e_ok and c_ok and hard_ok and cl["base_pinned_ok"]
                          and p15i.get("pins_ok") is True)
    publish = execution_pass
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    m = milestones(p15r, c_ok, e_ok)
    flags = {"library_certified": p15r.get("library_certified"),
             "batchA_evaluated": p15r.get("flags", {}).get("batchA_evaluated"),
             "D13_evaluated": p15r.get("flags", {}).get("D13_evaluated"),
             "batchC_evaluated": {"execution": c_ok, "claim": bc.get("batchC_evaluated", {}).get("claim") if c_ok
                                  else "not established", "scope": bc.get("batchC_evaluated", {}).get("scope")},
             "E2_decoupled_from_ch_slot": {"execution": e_ok, "claim": ec.get("outcome") if e_ok else "not established",
                                           "scope": ("the ch-projected one-loop kappa^2 identity (row (S0,Gamma1^[2]) "
                                                     "s1 h:h^2); the E2 pole remains a UV pole of the epsilon-scalar "
                                                     "K'.c Green function outside this projection")}}
    cert = {
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DATE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": "P.5 calculation, second step (E2 evanescent analysis; Batch C: D01, D03)",
        "execution_pass": execution_pass,
        "claim_status": ("P.5_calculation: Batch A, D13 (p15) and Batch C D01, D03 (p16) evaluated under the declared "
                         "prescription; E2 pole decoupled from the ch-projected slot (proof); P.5_entry: earned "
                         "(p14r contract); classical_readiness (frozen P.4): earned") if execution_pass else
                        "P.5_calculation: not accepted",
        "scope": ("P.5 calculation: Batch A (D02, D12, D14a-c), Batch B (D13) and Batch C (D01, D03) evaluated under "
                  "the frozen prescription (DRED R1-R6, Feynman +i0, MS-bar, S0; d opaque); D11 NOT evaluated (M2 "
                  "undischarged), so the hh slot is incomplete and no slot of the identity is complete; NOT quantum "
                  "inputs, NOT the projected defect/identity, NOT bulk restoration, NOT the insertion"),
        "release_claim_accepted": execution_pass,
        "release_claim_accepted_definition": ("p14r contract accepted AND p15 layer accepted and byte-identical AND "
                                              "contract identity (only dred.py changed vs p14r; F3 hardening active; "
                                              "no new contract file) AND E2 decoupling proof AND batchC_evaluated AND "
                                              "p16 hard stops"),
        "publication": "accepted" if publish else "REJECTED",
        "flags": flags, "batchA_evaluated": p15r.get("batchA_evaluated"), "D13_evaluated": p15r.get("D13_evaluated"),
        "batchC_evaluated": c_ok, "library_certified": p15r.get("library_certified"),
        "E2_status": ec.get("E2_status") if e_ok else "open", "E2_decoupling_proven": e_ok,
        "D01_evaluated": c_ok, "D03_evaluated": c_ok, "D11_evaluated": False,
        "graphs": graphs, "D12_status": p15r.get("D12_status"), "D12_status_derivation": p15r.get("D12_status_derivation"),
        "one_point_slot_kappa1": p15r.get("one_point_slot_kappa1"),
        "D13_summary": p15r.get("D13_summary"),
        "E2_summary": {k: ec.get(k) for k in ("outcome", "E2_status", "proof", "consequence", "D13_graph_status",
                                              "D13_slot_contribution", "controls")},
        "batchC_summary": {"finding_C1_component_route": bc.get("finding_C1_component_route"),
                           "D01_plus_D03_4D_pole_in_p14r_hh_basis": bc.get("D01_plus_D03_4D_pole_in_p14r_hh_basis"),
                           "controls": bc.get("controls"), "D11": bc.get("D11")},
        "contract_identity": ident, "contract_revision_disclosed": True,
        "p15_layer": l15, "change_log_vs_p15": cl,
        "P5_entry_earned": p15r.get("P5_entry_earned"), "P5_entry_flags": p15r.get("P5_entry_flags"),
        "P3_P4_frozen_as_P5_inputs": p15r.get("P3_P4_frozen_as_P5_inputs"), "classical": p15r.get("classical"),
        "D11_matching_verified": False, "quantum_inputs_evaluated": "not_earned",
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": m,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p15": p15i_ok,
        "independent_rebuild_passed_p14r": p15r.get("independent_rebuild_passed_p14r"),
        "independent_rebuild_passed_p13": p15r.get("independent_rebuild_passed_p13"),
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p16) source "
                               "tree only (independent: pending until a reviewer report for this tree exists); "
                               f"independent_rebuild_passed_p15 refers to the p15 tree {QC.P15_SOURCE_TREE_SHA256} / zip "
                               f"{QC.P15_SOURCE_ZIP_SHA256} (same-box caveat) and is not inherited by p16; "
                               "independent_rebuild_passed_p14r / _p13 as recorded by the p15 layer"),
        "p15_independent_rebuild": p15i,
        "p14r_independent_rebuild": p15r.get("p14r_independent_rebuild"),
        "p13_independent_rebuild": p15r.get("p13_independent_rebuild"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_source.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p15_archive": ARCH_P15,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "XVI_M_sha256": p15r.get("XVI_M_sha256"), "XVI_M_pin_ok": p15r.get("XVI_M_pin_ok"),
        "symmetry_restored": False, "bulk_symmetry_restored": False, "O1_closure": "NOT_CLOSED",
        "insertion_status": "Frozen_negative_obstruction_preserved", "XV_B_opened": False, "XIV_J_opened": False,
        "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
            ("P14_release.json", "P14_dred_rules.json", "P15_release.json", f"{QC.CERT_PREFIX}_E2_evanescent.json",
             f"{QC.CERT_PREFIX}_batchC.json") if (ROOT / "certificates" / n).is_file()},
    }
    cdir = ROOT / "certificates"
    txt = certio.dumps(cert)
    if publish:
        (ROOT / "RELEASE_STATUS.json").write_text(txt)
        (cdir / "RELEASE_STATUS.json").write_text(txt)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release.json").write_text(txt)
        certio.write(ROOT / "ledgers" / f"{QC.CERT_PREFIX}_milestones.json", {
            "landmark": "XVI-P", "revision": QC.REVISION, "ledger": "milestones (authoritative definitions + status)",
            **m, "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
            "independent_rebuild_passed_p15": p15i_ok, "hard_stops": hard,
            "flags": {"batchA_evaluated": p15r.get("batchA_evaluated"), "D13_evaluated": p15r.get("D13_evaluated"),
                      "batchC_evaluated": c_ok, "E2_decoupling_proven": e_ok}})
        (ROOT / "manuscript" / "body").mkdir(parents=True, exist_ok=True)
        (ROOT / "manuscript" / "body" / "P16-results-table.tex").write_text(results_table(bc, ec))
    else:
        (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(certio.dumps({
            "landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED", "contract_identity_ok": id_ok,
            "contract_identity": ident, "p15_layer_ok": l15_ok, "p15_layer": l15, "E2_ok": e_ok,
            "batchC_evaluated": c_ok, "hard_stops_hold": hard_ok}))
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publication"],
                      "contract_identity": id_ok, "changed_vs_p14r": ident["changed_vs_p14r"], "added": ident["added"],
                      "p15_layer": l15_ok, "E2": e_ok, "batchC_evaluated": c_ok, "hard_ok": hard_ok,
                      "author": author_ok, "independent_p16": indep_ok, "independent_p15": p15i_ok,
                      "change_log_counts": cl["counts"]}, indent=1))
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
        print(f"release_p16 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
