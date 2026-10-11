#!/usr/bin/env python3
"""XVI-P p17 release gate: P.5 calculation, third step -- the D01/D03 evanescent poles vs the ch-projected slo
  +> t
(priority 1) and the p16 reviewer findings G1-G6, on the p14r contract with the disclosed p15 (F1), p16 (F3) a
  +> nd
p17 (G1-G3) dred.py revisions.

Runs AFTER the p14r contract gate (release_p14.py), the p15 layer gate (release_p15.py) and the p16 layer gate
(release_p16.py -> certificates/P16_release.json) and requires all three to be accepted.  Recomputes:
  contract identity : p14r contract files byte-identical to p14r EXCEPT code/p5_entry/dred.py; dred.py differs
  +>  from
                      the p16 release (disclosed p17 revision: parse_d / assert_opaque_d); NO new contract fil
  +> e (no
                      evanescent h.h counterterm: the decoupling is proven); F3 guard and G2 loader active (pr
  +> obes);
  p16 layer        : every p16 layer file byte-identical to the p16 zip (QC.P16_CALC_SHA256); P16_release acce
  +> pted;
  hh slot          : P17_hh_slot.json -- decoupling proof controls all true, mutations M1-M4 rejected, no surv
  +> iving
                      evanescent structure in the slot;
  hard stops       : QC.HARD_STOPS_P17 (D11 NOT evaluated; quantum_inputs_evaluated not_earned; ...).
Rebuild flags (package evidence): author/independent for the CURRENT (p17) tree; independent_rebuild_passed_p1
  +> 6 from
the archived p16 independent report, bound to the p16 tree 90b4a665... / zip 56d5887d... (same-box caveat).
Change log (G4): every source file added/modified/removed relative to the p16 source-only zip, INCLUDING the p
  +> 17
reference-values file (listed as added by declaration: it is written after the author build).
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p17_conventions as QC  # noqa: E402
import p15_conventions as Q15  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)

ARCH_P16 = "archival/p16"
ARCH_P16_INDEP = f"{ARCH_P16}/reproducibility/independent_rebuild_report_p16.json"
HH_MUTATIONS = ("M1_wrong_relative_sign_D03", "M2_D03_times_2_symmetry_factor", "M3_D03_evanescent_dropped_nai
  +> ve_4D",
                "M4_trace_operator_in_place_of_s_h")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def f3_hardening():
    """F3 runtime guard (unchanged) and the p17 G2 loader."""
    import dred
    import sympy as sp
    d = dred.d
    e = (d - 4) / (d - 1) + d ** 2
    probes = {"expr.replace(d, 4)": lambda: e.replace(d, 4), "sympy.lambdify(d, expr)": lambda: sp.lambdify(d,
  +>  e),
              "expr.match(d)": lambda: e.match(d), "expr.subs(d, 4)": lambda: e.subs(d, 4),
              "expr.xreplace({d: 4})": lambda: e.xreplace({d: 4}),
              "dred.parse_d(str(expr)).subs(d, 4)": lambda: dred.parse_d(str(e)).subs(d, 4)}
    res = {}
    for k, f in probes.items():
        try:
            f()
            res[k] = "NOT refused"
        except dred.PrematureD4Substitution:
            res[k] = "refused"
    plain = sp.sympify(str(e))                                  # the G2 hazard: a plain Symbol('d')
    try:
        dred.assert_opaque_d(plain)
        plain_caught = False
    except dred.PlainDimensionSymbol:
        plain_caught = True
    rt = dred.parse_d(str(e))
    try:
        dred.parse_d("d + 1", {"d": sp.Symbol("d")})
        rebind_refused = False
    except dred.PlainDimensionSymbol:
        rebind_refused = True
    g2 = {"parse_d_round_trip_equals_original": sp.cancel(rt - e) == 0, "parse_d_restores_opaque_d": rt.has(d)
  +> ,
          "plain_sympify_detected_by_assert_opaque_d": plain_caught, "extra_locals_rebinding_d_refused": rebin
  +> d_refused}
    auth = dred.substitute_d(e, 4, "release_p17.f3_hardening: authorised-path probe") == 16
    return {"probes": res, "all_refused": all(v == "refused" for v in res.values()), "G2": g2,
            "G2_ok": all(g2.values()), "authorised_path_works": auth}


def contract_identity():
    cur = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    changed = sorted(k for k, h in Q15.P14R_CONTRACT_SHA256.items() if cur.get(k) != h)
    added = sorted(set(cur) - set(Q15.P14R_CONTRACT_SHA256))
    dred_changed_vs_p16 = cur.get("code/p5_entry/dred.py") != QC.P16_DRED_SHA256
    g = f3_hardening()
    ok = bool(changed == sorted(QC.P14R_CONTRACT_FILES_CHANGED_IN_P17) and added == sorted(QC.NEW_CONTRACT_FIL
  +> ES_P17)
              and dred_changed_vs_p16 and g["all_refused"] and g["G2_ok"] and g["authorised_path_works"])
    return ok, {"p14r_contract_files": len(Q15.P14R_CONTRACT_SHA256), "changed_vs_p14r": changed, "added": add
  +> ed,
                "dred_changed_vs_p16": dred_changed_vs_p16,
                "disclosed_revisions_p17": QC.DISCLOSED_CONTRACT_REVISIONS_P17, "guard_probes": g,
                "evanescent_hh_counterterm_added": False,
                "why_no_evanescent_hh_counterterm": ("D01/D03 evanescent poles decouple from the ch-projected 
  +> slot as "
                                                     "the sum D01 + D03 (proof, certificates/P17_hh_slot.json)
  +> ")}


def p16_layer():
    cur = {k: sha(ROOT / k) if (ROOT / k).is_file() else None for k in QC.P16_CALC_SHA256}
    ident = all(cur[k] == h for k, h in QC.P16_CALC_SHA256.items())
    r = jl("certificates/P16_release.json")
    ok = bool(ident and r.get("publication") == "accepted" and r.get("release_claim_accepted") is True
              and r.get("batchC_evaluated") is True and r.get("E2_decoupling_proven") is True
              and r.get("hard_stops_hold") is True)
    return ok, {"p16_layer_files_byte_identical": ident, "P16_release_accepted": r.get("publication") == "acce
  +> pted",
                "batchC_evaluated": r.get("batchC_evaluated"), "E2_status": r.get("E2_status")}, r


def p16_independent():
    f = ROOT / ARCH_P16_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P16_INDEP, "present": False, "pins_ok": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P16_INDEPENDENT_REPORT
    rec = {"report": ARCH_P16_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P16_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"),
           "bound_to_source_zip_sha256": rep.get("zip_sha256"),
           "tree_matches_p16": rep.get("source_tree_sha256") == QC.P16_SOURCE_TREE_SHA256,
           "zip_matches_p16": rep.get("zip_sha256") == QC.P16_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])), "findings": [x.get("id") for x in rep.get("findings",
  +>  [])],
           "caveat": rep.get("same_box_caveat"),
           "live_report_identical_to_archived": (live.read_bytes() == f.read_bytes()) if live.is_file()
           else "live report not in this tree",
           "NOT_inherited_by_p17": "bound to the p16 tree/zip; the p17 tree has its own (pending) independent 
  +> flag"}
    rec["archived_p16_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P16_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p16_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p16"] and rec["zip_matches_p16"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def hh_slot():
    c = jl(f"certificates/{QC.CERT_PREFIX}_hh_slot.json")
    muts = c.get("mutations", {})
    ok = bool(c.get("revision") == QC.REVISION and c.get("decoupling_proven") is True
              and c.get("status") == "decoupled_from_ch_slot_proven_as_sum"
              and c.get("surviving_evanescent_structures_in_slot") == []
              and all(v is True for v in c.get("controls", {}).values()) and len(c.get("controls", {})) >= 16
              and sorted(muts) == sorted(HH_MUTATIONS)
              and all(v.get("accepted_as_rejection") is True for v in muts.values()))
    return ok, c


def change_log():
    """G4: every source file added / modified / removed relative to the released p16 source-only zip, base the
  +>  pinned
    per-file list archival/p16/p16_source_files.json.  The p17 reference-values file is written AFTER the auth
  +> or
    build; it is listed as ADDED by declaration (deterministic: identical before and after it exists)."""
    f = ROOT / QC.P16_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P16_ARCHIVED_RECORDS[QC.P16_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT) if r != SM.REFERENCE_FILE}
    contract = set(Q15.P14R_CONTRACT_SHA256) | {p.relative_to(ROOT).as_posix() for p in (ROOT / "code" / "p5_e
  +> ntry").glob("*.py")}
    added = sorted((set(new) - set(old)) | {SM.REFERENCE_FILE})
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])
    changed = sorted(added + removed + modified)
    return {"base": f"{QC.P16_SOURCE_LIST} (pinned; files of the p16 zip sha256 {QC.P16_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok,
            "reference_file": f"{SM.REFERENCE_FILE} listed as added by declaration (written after the author b
  +> uild)",
            "added": added, "removed": removed, "modified": modified,
            "contract_files_changed": [x for x in changed if x in contract],
            "non_contract_files_changed": [x for x in changed if x not in contract],
            "counts": {"added": len(added), "removed": len(removed), "modified": len(modified)}}


def milestones(p16r, h_ok):
    st = dict(p16r.get("milestones", {}).get("status", {}))
    st["P.5_calculation"] = ("in progress (p15: Batch A D02/D12/D14a-c and Batch B D13; p16: E2 decoupled from
  +>  the ch "
                             "slot (proof), Batch C D01/D03 evaluated; p17: D01/D03 evanescent poles decoupled
  +>  from "
                             "the ch slot as the sum D01 + D03 (proof); D11 matching M2 NOT evaluated)"
                             if h_ok else "open (p17 hh-slot analysis not accepted)")
    st["P.5_identity"] = "open"
    return {"definitions": p16r.get("milestones", {}).get("definitions"), "order": p16r.get("milestones", {}).
  +> get("order"),
            "status": st, "P5_entry_earned": p16r.get("P5_entry_earned"),
            "P3_P4_frozen_as_P5_inputs": p16r.get("P3_P4_frozen_as_P5_inputs"),
            "P4_is_NOT": "coupled one-loop restoration (quantum_inputs_evaluated / projected_identity_verified
  +>  not earned)"}


def tex(x):
    """plain text-mode rendering (no math mode): ** -> ^, TeX specials escaped, typewriter font."""
    t = str(x).replace("**", "^").replace("\\", "/").replace("_", "\\_").replace("^", "\\^{}").replace("&", "\
  +> \&")
    return "\\texttt{" + t + "}"


def results_table(hc):
    ps = hc["per_structure"]
    labs = sorted(set(ps["D01"]) | set(ps["D03"]))
    yn = {True: "yes", False: "no", None: "--"}
    rows = [f"{tex(l)} & {yn[ps['D01'].get(l, ps['D03'].get(l, {})).get('evanescent')]} & "
            f"{yn[ps['D01'][l]['reaches_slot']] if l in ps['D01'] else '--'} & "
            f"{yn[ps['D03'][l]['reaches_slot']] if l in ps['D03'] else '--'} \\\\" for l in labs]
    fd = hc["four_D_poles"]
    crow = [f"{g} & " + " & ".join(tex(x) for x in fd["graphs"][g]["coordinates_p14r_basis"])
            + f" & {yn[fd['graphs'][g]['transverse']]} \\\\" for g in ("D01", "D03", "D01+D03")]
    kern = "; ".join("(" + ", ".join(v) + ")" for v in fd["transverse_basis_in_p14r_coordinates"])
    return ("% generated by code/p5_calc/release_p17.py -- do not edit\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{4.2cm}p{1.6cm}p{2.2cm}p{2.2cm}}\\hline\n"
            "structure of $G^{(mn)(rs)}$ & evanescent & D01 reaches slot & D03 reaches slot \\\\\\hline\n"
            + "\n".join(rows) + "\n\\hline\\end{tabular}\\end{center}\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{1.3cm}p{1.5cm}p{1.5cm}p{1.5cm}p{1.5cm}p{1.5cm}p{1.3
  +> cm}}\\hline\n"
            "4D pole & $z_1$ & $z_2$ & $z_3$ & $z_4$ & $z_5$ & transverse \\\\\\hline\n"
            + "\n".join(crow) + "\n\\hline\\end{tabular}\\end{center}\n"
            f"\\noindent Verdict: {tex(hc['verdict'])}. Surviving evanescent structures in the slot: none. "
            f"Transverse kernel (p14r coordinates): {tex(kern)}. D11: NOT evaluated.\n")


def _main():
    id_ok, ident = contract_identity()
    l16_ok, l16, p16r = p16_layer()
    h_ok, hc = hh_slot()
    p16i_ok, p16i = p16_independent()
    p14r = jl("certificates/P14_release.json")
    p15r = jl("certificates/P15_release.json")
    hard = dict(QC.HARD_STOPS_P17)
    graphs = dict(p16r.get("graphs", {}))
    for g in QC.HH_SLOT_GRAPHS:
        if g in graphs and h_ok:
            graphs[g] = dict(graphs[g], ch_slot=("decoupled as the sum D01 + D03 (evanescent and 4D parts; "
                                                 "certificates/P17_hh_slot.json); NOT graph by graph"))
    graphs["D11"] = {"status": "unevaluated", "reason": "M2 undischarged (D11 matching not verified)",
                     "ch_slot": "open (same row (S0,Gamma1^[2]) s2 K:K.c)"}
    hard_ok = bool(all(hard[k] == v for k, v in QC.HARD_STOPS_P17.items())
                   and graphs.get("D11", {}).get("status") == "unevaluated"
                   and hc.get("quantum_inputs_evaluated") in (None, "not_earned")
                   and p14r.get("hard_stops_hold") is True and p15r.get("hard_stops_hold") is True
                   and p16r.get("hard_stops_hold") is True)
    cl = change_log()
    execution_pass = bool(id_ok and l16_ok and h_ok and hard_ok and cl["base_pinned_ok"] and p16i.get("pins_ok
  +> ") is True)
    publish = execution_pass
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    m = milestones(p16r, h_ok)
    hh_status = hc.get("status") if h_ok else "open"
    flags = dict(p16r.get("flags", {}))
    flags["hh_evanescent_decoupled_from_ch_slot"] = {
        "execution": h_ok, "claim": hc.get("verdict") if h_ok else "not established",
        "scope": ("the ch-projected one-loop kappa^2 identity, row (S0,Gamma1^[2]) s2 K:K.c, contributions of 
  +> D01 + D03 "
                  "(D02 = D12 = 0); the summed evanescent poles remain (transverse) UV poles of the hh Green f
  +> unction "
                  "outside this projection; D11 (same row) NOT evaluated")}
    cert = {
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DA
  +> TE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": "P.5 calculation, third step (D01/D03 evanescent poles vs the ch-projected slot; G1-G6)
  +> ",
        "execution_pass": execution_pass,
        "claim_status": ("P.5_calculation: Batch A, D13 (p15), Batch C D01, D03 (p16) evaluated under the decl
  +> ared "
                         "prescription; E2 (p16) and the D01/D03 evanescent poles (p17, as the sum) decoupled 
  +> from the "
                         "ch-projected slot (proofs); P.5_entry: earned (p14r contract); classical_readiness (
  +> frozen "
                         "P.4): earned") if execution_pass else "P.5_calculation: not accepted",
        "scope": ("P.5 calculation: Batch A (D02, D12, D14a-c), Batch B (D13) and Batch C (D01, D03) evaluated
  +>  under "
                  "the frozen prescription (DRED R1-R6, Feynman +i0, MS-bar, S0; d opaque); D01 + D03 contribu
  +> te zero "
                  "to the ch-projected slot (exact in d); D11 NOT evaluated (M2 undischarged), so the hh slot 
  +> is "
                  "incomplete and no slot of the identity is complete; NOT quantum inputs, NOT the projected "
                  "defect/identity, NOT bulk restoration, NOT the insertion"),
        "release_claim_accepted": execution_pass,
        "release_claim_accepted_definition": ("p14r contract accepted AND p15 and p16 layers accepted and byte
  +> -identical "
                                              "AND contract identity (only dred.py changed vs p14r; changed vs
  +>  p16 by "
                                              "the disclosed G2 loader; guard probes; no new contract file) AN
  +> D the "
                                              "hh-slot decoupling proof AND p17 hard stops"),
        "publication": "accepted" if publish else "REJECTED",
        "flags": flags, "batchA_evaluated": p16r.get("batchA_evaluated"), "D13_evaluated": p16r.get("D13_evalu
  +> ated"),
        "batchC_evaluated": p16r.get("batchC_evaluated"), "library_certified": p16r.get("library_certified"),
        "E2_status": p16r.get("E2_status"), "E2_decoupling_proven": p16r.get("E2_decoupling_proven"),
        "hh_evanescent_status": hh_status, "hh_evanescent_decoupling_proven": h_ok,
        "evanescent_hh_counterterm_added": False,
        "D01_evaluated": p16r.get("D01_evaluated"), "D03_evaluated": p16r.get("D03_evaluated"), "D11_evaluated
  +> ": False,
        "graphs": graphs, "D12_status": p16r.get("D12_status"), "D12_status_derivation": p16r.get("D12_status_
  +> derivation"),
        "hh_slot_summary": {k: hc.get(k) for k in ("verdict", "status", "row", "operator_s_h", "proof",
                                                   "surviving_evanescent_structures_in_slot", "consequence",
                                                   "four_D_poles", "evanescent_poles_D01_plus_D03_in_hh_green_
  +> function",
                                                   "phase_convention_G6", "controls")},
        "phase_convention_G6": QC.PHASE_CONVENTION_G6,
        "contract_identity": ident, "contract_revision_disclosed": True,
        "disclosed_test_revisions_p17": QC.DISCLOSED_TEST_REVISIONS_P17,
        "p16_layer": l16, "change_log_vs_p16": cl,
        "P5_entry_earned": p16r.get("P5_entry_earned"), "P5_entry_flags": p16r.get("P5_entry_flags"),
        "P3_P4_frozen_as_P5_inputs": p16r.get("P3_P4_frozen_as_P5_inputs"), "classical": p16r.get("classical")
  +> ,
        "D11_matching_verified": False, "quantum_inputs_evaluated": "not_earned",
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": m,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p16": p16i_ok,
        "independent_rebuild_passed_p15": p16r.get("independent_rebuild_passed_p15"),
        "independent_rebuild_passed_p14r": p16r.get("independent_rebuild_passed_p14r"),
        "independent_rebuild_passed_p13": p16r.get("independent_rebuild_passed_p13"),
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p17
  +> ) source "
                               "tree only (independent: pending until a reviewer report for this tree exists);
  +>  "
                               f"independent_rebuild_passed_p16 refers to the p16 tree {QC.P16_SOURCE_TREE_SHA
  +> 256} / zip "
                               f"{QC.P16_SOURCE_ZIP_SHA256} (same-box caveat) and is not inherited by p17; "
                               "_p15 / _p14r / _p13 as recorded by the p16 layer"),
        "p16_independent_rebuild": p16i,
        "p15_independent_rebuild": p16r.get("p15_independent_rebuild"),
        "p14r_independent_rebuild": p16r.get("p14r_independent_rebuild"),
        "p13_independent_rebuild": p16r.get("p13_independent_rebuild"),
        "one_point_slot_kappa1": p16r.get("one_point_slot_kappa1"), "D13_summary": p16r.get("D13_summary"),
        "E2_summary": p16r.get("E2_summary"), "batchC_summary": p16r.get("batchC_summary"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_s
  +> ource.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p16_archive": ARCH_P16,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "XVI_M_sha256": p16r.get("XVI_M_sha256"), "XVI_M_pin_ok": p16r.get("XVI_M_p
  +> in_ok"),
        "symmetry_restored": False, "bulk_symmetry_restored": False, "O1_closure": "NOT_CLOSED",
        "insertion_status": "Frozen_negative_obstruction_preserved", "XV_B_opened": False, "XIV_J_opened": Fal
  +> se,
        "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
            ("P14_release.json", "P15_release.json", "P16_release.json", f"{QC.CERT_PREFIX}_hh_slot.json")
            if (ROOT / "certificates" / n).is_file()},
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
            "independent_rebuild_passed_p16": p16i_ok, "hard_stops": hard,
            "flags": {"batchA_evaluated": p16r.get("batchA_evaluated"), "D13_evaluated": p16r.get("D13_evaluat
  +> ed"),
                      "batchC_evaluated": p16r.get("batchC_evaluated"),
                      "E2_decoupling_proven": p16r.get("E2_decoupling_proven"),
                      "hh_evanescent_decoupling_proven": h_ok}})
        (ROOT / "manuscript" / "body").mkdir(parents=True, exist_ok=True)
        (ROOT / "manuscript" / "body" / "P17-results-table.tex").write_text(results_table(hc))
    else:
        (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(certio.dumps({
            "landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED", "contract_identity_ok": i
  +> d_ok,
            "contract_identity": ident, "p16_layer_ok": l16_ok, "p16_layer": l16, "hh_slot_ok": h_ok,
            "p16_independent_pins_ok": p16i.get("pins_ok"), "hard_stops_hold": hard_ok,
            "change_log_base_ok": cl["base_pinned_ok"]}))
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publicat
  +> ion"],
                      "contract_identity": id_ok, "changed_vs_p14r": ident["changed_vs_p14r"], "added": ident[
  +> "added"],
                      "p16_layer": l16_ok, "hh_slot": h_ok, "hard_ok": hard_ok,
                      "author": author_ok, "independent_p17": indep_ok, "independent_p16": p16i_ok,
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
        print(f"release_p17 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
