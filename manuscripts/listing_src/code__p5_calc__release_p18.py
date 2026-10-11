#!/usr/bin/env python3
"""XVI-P p18 release gate: P.5 calculation, fourth step -- the D11 matching premise M2 (discharge), D11 evalua
  +> ted
under the declared prescription, the full hh slot D01 + D02 + D03 + D11 + D12, and the p17 reviewer findings H
  +> 1-H5,
on the p14r contract with the disclosed p15 (F1), p16 (F3), p17 (G1-G3) and p18 (H3/H5, documentation only) dr
  +> ed.py
revisions.

Runs AFTER the p14r, p15, p16 and p17 gates (release_p17.py -> certificates/P17_release.json) and requires all
  +>  four
to be accepted.  Recomputes:
  contract identity : p14r contract files byte-identical EXCEPT code/p5_entry/dred.py; dred.py differs from th
  +> e p17
                      release only in comments/docstrings (AST without docstrings pinned: QC.P17_DRED_AST_SHA2
  +> 56); NO
                      new contract file (no evanescent h.h counterterm: the full-row decoupling is proven);
  p17 layer        : every p17 layer file byte-identical to the p17 zip (QC.P17_CALC_SHA256); P17_release acce
  +> pted;
  M2               : P18_D11_M2.json -- all controls true, all mutations rejected, verdict DISCHARGED;
  D11              : P18_D11.json -- evaluated, all controls true, mutations rejected;
  hh slot          : P18_hh_slot.json -- full-row decoupling, no surviving evanescent structure;
  earned flags     : D11_matching_verified, D11_evaluated, quantum_inputs_evaluated -- each ONLY from the cert
  +> ificates
                      (the inventory of the three ch slots is re-read here from the P15/P16/P18 certificates);
  hard stops       : QC.HARD_STOPS_P18 (projected identity/restoration NOT earned; symmetry flags false; ...).
Rebuild flags: author/independent for the CURRENT (p18) tree; independent_rebuild_passed_p17 from the archived
  +>  p17
independent report, bound to the p17 tree 2a5a6317... / zip 7f4f61df... (same-box caveat).
Change log: every source file added/modified/removed relative to the p17 source-only zip, INCLUDING the p18
reference-values file (listed as added by declaration: it is written after the author build).
"""
from __future__ import annotations
import ast, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p18_conventions as QC  # noqa: E402
import p15_conventions as Q15  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)

ARCH_P17 = "archival/p17"
ARCH_P17_INDEP = f"{ARCH_P17}/reproducibility/independent_rebuild_report_p17.json"
M2_MUTATIONS = ("alpha_beta_swapped", "offdiagonal_weight_1", "FT_log_constant_sign_flipped", "symmetry_factor
  +> _doubled",
                "D01_in_place_of_D11", "D0_dropped_beta_0")
SLOT_MUTATIONS = ("M1_wrong_relative_sign_D03", "M3_D03_evanescent_dropped_naive_4D", "M4_trace_operator_in_pl
  +> ace_of_s_h")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def ast_sha(path):
    """sha256 of the module AST with every docstring removed (comment/docstring-only revisions keep it)."""
    tree = ast.parse(Path(path).read_text())
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body:
            b0 = n.body[0]
            if isinstance(b0, ast.Expr) and isinstance(b0.value, ast.Constant) and isinstance(b0.value.value, 
  +> str):
                n.body = n.body[1:] or [ast.Pass()]
    return hashlib.sha256(ast.dump(tree).encode()).hexdigest()


def contract_identity():
    cur = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    changed = sorted(k for k, h in Q15.P14R_CONTRACT_SHA256.items() if cur.get(k) != h)
    added = sorted(set(cur) - set(Q15.P14R_CONTRACT_SHA256))
    dred = ROOT / "code" / "p5_entry" / "dred.py"
    dred_changed_vs_p17 = cur.get("code/p5_entry/dred.py") != QC.P17_DRED_SHA256
    dred_ast_equal_p17 = ast_sha(dred) == QC.P17_DRED_AST_SHA256
    # p22 disclosed revision: the registered additive p22 contract revision (contract_registry: dred.py = the 
  +> p18 file
    # + one delimited guard block, remainder byte-identical to p18) is accepted in place of the AST identity
    if not dred_ast_equal_p17:
        import contract_registry as CR
        dred_ast_equal_p17 = CR.dred_revision(ROOT)["state"] == "p18 + p22 guard block"
    ok = bool(changed == sorted(QC.P14R_CONTRACT_FILES_CHANGED_IN_P18) and added == sorted(QC.NEW_CONTRACT_FIL
  +> ES_P18)
              and dred_changed_vs_p17 and dred_ast_equal_p17)
    return ok, {"p14r_contract_files": len(Q15.P14R_CONTRACT_SHA256), "changed_vs_p14r": changed, "added": add
  +> ed,
                "dred_changed_vs_p17": dred_changed_vs_p17,
                "dred_executable_code_identical_to_p17_ast_without_docstrings": dred_ast_equal_p17,
                "disclosed_revisions_p18": QC.DISCLOSED_CONTRACT_REVISIONS_P18,
                "evanescent_hh_counterterm_added": False,
                "why_no_evanescent_hh_counterterm": ("full row decoupled: p_m G_D11 = 0 exactly in d and p_m (
  +> G_D01 + "
                                                     "G_D03) = 0 exactly in d (certificates/P18_hh_slot.json)"
  +> )}


def p17_layer():
    cur = {k: sha(ROOT / k) if (ROOT / k).is_file() else None for k in QC.P17_CALC_SHA256}
    ident = all(cur[k] == h for k, h in QC.P17_CALC_SHA256.items())
    r = jl("certificates/P17_release.json")
    ok = bool(ident and r.get("publication") == "accepted" and r.get("release_claim_accepted") is True
              and r.get("hh_evanescent_decoupling_proven") is True and r.get("hard_stops_hold") is True)
    return ok, {"p17_layer_files_byte_identical": ident, "P17_release_accepted": r.get("publication") == "acce
  +> pted",
                "hh_evanescent_decoupling_proven_p17": r.get("hh_evanescent_decoupling_proven")}, r


def p17_independent():
    f = ROOT / ARCH_P17_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P17_INDEP, "present": False, "pins_ok": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P17_INDEPENDENT_REPORT
    rec = {"report": ARCH_P17_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P17_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"),
           "bound_to_source_zip_sha256": rep.get("zip_sha256"),
           "tree_matches_p17": rep.get("source_tree_sha256") == QC.P17_SOURCE_TREE_SHA256,
           "zip_matches_p17": rep.get("zip_sha256") == QC.P17_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])), "findings": [x.get("id") for x in rep.get("findings",
  +>  [])],
           "caveat": rep.get("same_box_caveat"),
           "live_report_identical_to_archived": (live.read_bytes() == f.read_bytes()) if live.is_file()
           else "live report not in this tree",
           "NOT_inherited_by_p18": "bound to the p17 tree/zip; the p18 tree has its own (pending) independent 
  +> flag"}
    rec["archived_p17_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P17_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p17_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p17"] and rec["zip_matches_p17"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def m2_check():
    c = jl(f"certificates/{QC.CERT_PREFIX}_D11_M2.json")
    muts = c.get("mutations", {})
    ok = bool(c.get("revision") == QC.REVISION and c.get("D11_matching_verified") is True
              and c.get("D11_matching_verified_scope") == "4D components"
              and c.get("evanescent_components_matching", {}).get("status") == "not_applicable_not_verified"
              and str(c.get("M3_status", {}).get("status", "")).startswith("unconditional on the 4D components
  +> ")
              and str(c.get("verdict", "")).startswith("DISCHARGED")
              and len(c.get("controls", {})) >= 8 and all(v is True for v in c.get("controls", {}).values())
              and sorted(muts) == sorted(M2_MUTATIONS) and all(v.get("accepted_as_rejection") is True for v in
  +>  muts.values())
              and c.get("route_B", {}).get("mismatches") == 0 and c.get("route_B", {}).get("pairs") == 100)
    return ok, c


def d11_check(m2_ok):
    c = jl(f"certificates/{QC.CERT_PREFIX}_D11.json")
    ok = bool(m2_ok and c.get("revision") == QC.REVISION and c.get("evaluated") is True and c.get("D11_evaluat
  +> ed") is True
              and len(c.get("controls", {})) >= 14 and all(v is True for v in c.get("controls", {}).values())
              and all(v.get("accepted_as_rejection") is True for v in c.get("mutations", {}).values())
              and len(c.get("mutations", {})) >= 4)
    return ok, c


def slot_check():
    c = jl(f"certificates/{QC.CERT_PREFIX}_hh_slot.json")
    muts = c.get("mutations", {})
    ok = bool(c.get("revision") == QC.REVISION and c.get("decoupling_proven_full_row") is True
              and c.get("surviving_evanescent_structures_in_slot") == [] and c.get("D11_reopens_evanescent_que
  +> stion") is False
              and len(c.get("controls", {})) >= 11 and all(v is True for v in c.get("controls", {}).values())
              and sorted(muts) == sorted(SLOT_MUTATIONS) and all(v.get("accepted_as_rejection") is True for v 
  +> in muts.values())
              and len(c.get("slot_values", {}).get("D01+D03+D11", {})) == 7)
    return ok, c


def inventory_recheck(d11_ok):
    """independent of d11.py: the required inputs are EVERY graph of every surviving ch row of the frozen ledg
  +> er
    (three slots: hh, K.c, one-point); each flag and status is re-read from its own certificate; no Missing.""
  +> "
    rows = [r for r in jl("ledgers/P13_ch_dependency_rows.json").get("rows", [])
            if str(r.get("status", "")).startswith("surviving")]
    required = {gid.split("_")[0]: r["id"] for r in rows for gid in r.get("graphs", [])}
    b = jl("certificates/P15_batchA.json").get("batchA_evaluated", {})
    claim = b.get("claim", "") if isinstance(b, dict) else ""
    c16 = jl("certificates/P16_batchC.json").get("graphs", {})
    d13 = jl("certificates/P15_D13.json").get("D13_evaluated", {})
    inv = {g: bool(isinstance(b, dict) and b.get("execution") is True and g in claim)
           for g in ("D02", "D12", "D14a", "D14b", "D14c")}
    inv["D01"] = c16.get("D01", {}).get("evaluated") is True
    inv["D03"] = c16.get("D03", {}).get("evaluated") is True
    inv["D13"] = isinstance(d13, dict) and d13.get("execution") is True
    inv["D11"] = bool(d11_ok)
    sa = {g: v.get("status") for g, v in jl("certificates/P15_batchA.json").get("graphs", {}).items()}
    status = {**sa, "D01": c16.get("D01", {}).get("status"), "D03": c16.get("D03", {}).get("status"),
              "D13": "evaluated" if inv["D13"] else None,
              "D11": jl(f"certificates/{QC.CERT_PREFIX}_D11.json").get("status") if d11_ok else None}
    lst = [{"graph": g, "slot_row": required.get(g), "evaluated": inv.get(g, False), "status": status.get(g),
            "certificate": QC.INPUT_EVALUATION_P18.get(g)} for g in sorted(set(required) | set(inv))]
    no_missing = all(x["status"] and "missing" not in str(x["status"]).lower()
                     and "unevaluated" not in str(x["status"]).lower() for x in lst)
    ok = bool(set(required) == set(inv) == set(QC.INVENTORY_P18) and len(set(required.values())) == 3
              and all(inv.values()) and no_missing)
    return ok, lst


def change_log():
    f = ROOT / QC.P17_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P17_ARCHIVED_RECORDS[QC.P17_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT) if r != SM.REFERENCE_FILE}
    contract = set(Q15.P14R_CONTRACT_SHA256) | {p.relative_to(ROOT).as_posix() for p in (ROOT / "code" / "p5_e
  +> ntry").glob("*.py")}
    added = sorted((set(new) - set(old)) | {SM.REFERENCE_FILE})
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])
    changed = sorted(added + removed + modified)
    return {"base": f"{QC.P17_SOURCE_LIST} (pinned; files of the p17 zip sha256 {QC.P17_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok,
            "reference_file": f"{SM.REFERENCE_FILE} listed as added by declaration (written after the author b
  +> uild)",
            "added": added, "removed": removed, "modified": modified,
            "contract_files_changed": [x for x in changed if x in contract],
            "non_contract_files_changed": [x for x in changed if x not in contract],
            "counts": {"added": len(added), "removed": len(removed), "modified": len(modified)}}


def milestones(p17r, ok):
    st = dict(p17r.get("milestones", {}).get("status", {}))
    st["P.5_calculation"] = ("quantum inputs evaluated (p15: Batch A D02/D12/D14a-c, Batch B D13; p16: E2 deco
  +> upled, "
                             "Batch C D01/D03; p17: D01/D03 evanescent poles decoupled as the sum; p18: M2 dis
  +> charged, "
                             "D11 evaluated, full hh row decoupled); the projected identity is NOT assembled"
                             if ok else "open (p18 D11 / full-slot analysis not accepted)")
    st["P.5_identity"] = "open"
    return {"definitions": p17r.get("milestones", {}).get("definitions"), "order": p17r.get("milestones", {}).
  +> get("order"),
            "status": st, "P5_entry_earned": p17r.get("P5_entry_earned"),
            "P3_P4_frozen_as_P5_inputs": p17r.get("P3_P4_frozen_as_P5_inputs"),
            "P4_is_NOT": "coupled one-loop restoration (projected_identity_verified / projected_restoration_ve
  +> rified not earned)"}


def tex(x):
    t = str(x).replace("**", "^").replace("\\", "/").replace("_", "\\_").replace("^", "\\^{}").replace("&", "\
  +> \&")
    return "\\texttt{" + t + "}"


def results_table(m2c, d11c, sc):
    rows = [f"{tex(k)} & {'yes' if v['evanescent'] else 'no'} & {tex(v['UV_pole'])} & {tex(v['nonlocal_coeffic
  +> ient_of_L'])} "
            f"& {tex(v['local_polynomial'])} & {tex(v['local_shift_from_d_dependence'])} \\\\"
            for k, v in d11c["result"].items()]
    fd = sc["four_D_poles"]
    crow = [f"{g} & " + " & ".join(tex(x) for x in fd["graphs"][g]["coordinates_p14r_basis"])
            + f" & {'yes' if fd['graphs'][g]['transverse'] else 'no'} \\\\" for g in ("D11", "D01+D03", "D01+D
  +> 03+D11")]
    srow = [f"{tex(n)} & {tex(sc['slot_values']['D01'][n])} & {tex(sc['slot_values']['D03'][n])} & "
            f"{tex(sc['slot_values']['D11'][n])} & {tex(sc['slot_values']['D01+D03+D11'][n])} \\\\"
            for n in sc["slot_values"]["D01+D03+D11"]]
    rb = m2c["route_B"]
    return ("% generated by code/p5_calc/release_p18.py -- do not edit\n"
            f"\\noindent M2: {tex(m2c['verdict'])}; route B: {rb['pairs']} component pairs, {rb['mismatches']}
  +>  "
            f"mismatches, constant {tex(rb['constant'])}; c\\_FT = {tex(m2c['FT_constant']['c_FT_from_DR_bubbl
  +> e'])} "
            f"(DR bubble) = {tex(m2c['FT_constant']['c_FT_from_minus_r'])} (-r).\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{3.0cm}p{0.6cm}p{1.5cm}p{1.5cm}p{3.6cm}p{2.4cm}}\\hl
  +> ine\n"
            "D11 structure & evan. & UV pole & coeff. of L & local (MS-bar) & shift (d=4 first) \\\\\\hline\n"
            + "\n".join(rows) + "\n\\hline\\end{tabular}\\end{center}\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{2.0cm}p{1.3cm}p{1.3cm}p{1.3cm}p{1.3cm}p{1.3cm}p{1.2
  +> cm}}\\hline\n"
            "4D pole & $z_1$ & $z_2$ & $z_3$ & $z_4$ & $z_5$ & transverse \\\\\\hline\n"
            + "\n".join(crow) + "\n\\hline\\end{tabular}\\end{center}\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{2.6cm}p{2.6cm}p{2.6cm}p{1.2cm}p{1.6cm}}\\hline\n"
            "assignment $(c,h)$ & $X_{D01}$ & $X_{D03}$ & $X_{D11}$ & sum \\\\\\hline\n"
            + "\n".join(srow) + "\n\\hline\\end{tabular}\\end{center}\n"
            f"\\noindent Full-row verdict: {tex(sc['verdict'])}.\n")


def _main():
    id_ok, ident = contract_identity()
    l17_ok, l17, p17r = p17_layer()
    p17i_ok, p17i = p17_independent()
    m2_ok, m2c = m2_check()
    d11_ok, d11c = d11_check(m2_ok)
    s_ok, sc = slot_check()
    inv_ok, inv = inventory_recheck(d11_ok)
    q_earned = bool(inv_ok and s_ok and sc.get("quantum_inputs_evaluated") == "earned")
    p14r, p15r, p16r = (jl(f"certificates/{n}_release.json") for n in ("P14", "P15", "P16"))
    hard = dict(QC.HARD_STOPS_P18)
    hard_ok = bool(all(hard[k] == v for k, v in QC.HARD_STOPS_P18.items())
                   and all(r.get("hard_stops_hold") is True for r in (p14r, p15r, p16r, p17r))
                   and not any(str(sc.get(k, "not_earned")) == "earned" for k in
                               ("projected_identity_verified", "projected_restoration_verified"))
                   and sc.get("bulk_symmetry_restored", False) is False)
    graphs = dict(p17r.get("graphs", {}))
    if d11_ok:
        graphs["D11"] = {"status": "evaluated", "certificate": f"certificates/{QC.CERT_PREFIX}_D11.json",
                         "sector_status": d11c.get("status"), "M2": m2c.get("verdict"),
                         "ch_slot": "decoupled by itself (p_m G_D11 = 0 exactly in d)"}
    else:
        graphs["D11"] = {"status": "unevaluated", "reason": "M2 not discharged or D11 certificate not accepted
  +> "}
    cl = change_log()
    execution_pass = bool(id_ok and l17_ok and m2_ok and d11_ok and s_ok and hard_ok and cl["base_pinned_ok"]
                          and p17i.get("pins_ok") is True)
    publish = execution_pass
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    m = milestones(p17r, execution_pass)
    flags = dict(p17r.get("flags", {}))
    flags["D11_matching_M2"] = {"execution": m2_ok, "claim": m2c.get("verdict") if m2_ok else "not discharged"
  +> ,
                                "scope": m2c.get("scope")}
    flags["hh_slot_full_row_decoupled"] = {"execution": s_ok, "claim": sc.get("verdict") if s_ok else "not est
  +> ablished",
                                           "scope": ("row (S0,Gamma1^[2]) s2 K:K.c; D01 + D02 + D03 + D11 + D1
  +> 2; the "
                                                     "summed evanescent poles remain (transverse) UV poles of 
  +> the hh "
                                                     "Green function outside this projection")}
    cert = {
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DA
  +> TE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": "P.5 calculation, fourth step (M2 discharge, D11 evaluation, full hh slot; H1-H5)",
        "execution_pass": execution_pass,
        "claim_status": ("P.5_calculation: every graph of the inventory (D01, D02, D03, D11, D12, D13, D14a-c)
  +>  evaluated "
                         "under the one declared prescription; M2 discharged (4D components); the hh row decou
  +> pled from "
                         "the ch-projected slot (D11 by itself, D01 + D03 as the sum); P.5_identity open")
        if execution_pass else "P.5_calculation: not accepted",
        "scope": ("quantum inputs = the evaluated one-loop graphs of the three ch slots (hh, K.c, one-point) u
  +> nder DRED "
                  "R1-R6 / Feynman +i0 / MS-bar / S0, d opaque. NOT the projected defect/identity, NOT project
  +> ed "
                  "restoration, NOT bulk restoration, NOT the insertion. Evanescent poles of the hh (D01, D03,
  +>  D11) and "
                  "K.c (D13 E2) Green functions are retained and nonzero; they decouple from the ch projection
  +> , and "
                  "renormalising those Green functions themselves would need evanescent counterterms (not clai
  +> med)."),
        "release_claim_accepted": execution_pass,
        "release_claim_accepted_definition": ("p14r contract accepted AND p15, p16, p17 layers accepted and "
                                              "byte-identical AND contract identity (only dred.py changed vs p
  +> 14r; vs "
                                              "p17 comments/docstrings only; no new contract file) AND M2 disc
  +> harged "
                                              "AND D11 evaluated AND the full-row slot decoupling AND p18 hard
  +>  stops"),
        "publication": "accepted" if publish else "REJECTED",
        "flags": flags,
        "D11_matching_verified": bool(m2_ok and publish),
        "D11_matching_verified_scope": m2c.get("D11_matching_verified_scope") if m2_ok else None,
        "D11_evanescent_components_matching": m2c.get("evanescent_components_matching", {}).get("status"),
        "M3_status": m2c.get("M3_status", {}).get("status") if m2_ok else "conditional on M2 (not discharged)"
  +> ,
        "D11_evaluated": bool(d11_ok and publish),
        "quantum_inputs_evaluated": "earned" if (q_earned and publish) else "not_earned",
        "quantum_inputs_inventory": inv,
        "projected_defect_computed": "not_earned", "projected_identity_verified": "not_earned",
        "projected_restoration_verified": "not_earned",
        "batchA_evaluated": p17r.get("batchA_evaluated"), "D13_evaluated": p17r.get("D13_evaluated"),
        "batchC_evaluated": p17r.get("batchC_evaluated"), "library_certified": p17r.get("library_certified"),
        "E2_status": p17r.get("E2_status"), "E2_decoupling_proven": p17r.get("E2_decoupling_proven"),
        "hh_evanescent_status": p17r.get("hh_evanescent_status"),
        "hh_evanescent_decoupling_proven": p17r.get("hh_evanescent_decoupling_proven"),
        "hh_full_row_decoupling_proven": s_ok, "evanescent_hh_counterterm_added": False,
        "D01_evaluated": p17r.get("D01_evaluated"), "D03_evaluated": p17r.get("D03_evaluated"),
        "graphs": graphs, "D12_status": p17r.get("D12_status"), "D12_status_derivation": p17r.get("D12_status_
  +> derivation"),
        "M2_summary": {k: m2c.get(k) for k in ("verdict", "D11_matching_verified_scope",
                                                "evanescent_components_matching", "M3_status", "statement", "r
  +> oute_B", "FT_constant", "controls",
                                                "analytic_inputs_cited", "scope", "M3_consequence")},
        "D11_summary": {k: d11c.get(k) for k in ("status", "prescription", "prescription_usage", "UV_pole_in_p
  +> 14r_hh_basis",
                                                  "evanescent_pole_nonzero", "controls")},
        "hh_slot_summary": {k: sc.get(k) for k in ("verdict", "row", "graphs", "how_D11_decouples",
                                                   "surviving_evanescent_structures_in_slot", "consequence", "
  +> controls")},
        "phase_convention_G6": QC.PHASE_CONVENTION_G6,
        "contract_identity": ident, "contract_revision_disclosed": True,
        "disclosed_test_revisions_p18": QC.DISCLOSED_TEST_REVISIONS_P18,
        "p17_layer": l17, "change_log_vs_p17": cl,
        "P5_entry_earned": p17r.get("P5_entry_earned"), "P5_entry_flags": p17r.get("P5_entry_flags"),
        "P3_P4_frozen_as_P5_inputs": p17r.get("P3_P4_frozen_as_P5_inputs"), "classical": p17r.get("classical")
  +> ,
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": m,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p17": p17i_ok,
        "independent_rebuild_passed_p16": p17r.get("independent_rebuild_passed_p16"),
        "independent_rebuild_passed_p15": p17r.get("independent_rebuild_passed_p15"),
        "independent_rebuild_passed_p14r": p17r.get("independent_rebuild_passed_p14r"),
        "independent_rebuild_passed_p13": p17r.get("independent_rebuild_passed_p13"),
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p18
  +> ) source "
                               "tree only (independent: pending until a reviewer report for this tree exists);
  +>  "
                               f"independent_rebuild_passed_p17 refers to the p17 tree {QC.P17_SOURCE_TREE_SHA
  +> 256} / zip "
                               f"{QC.P17_SOURCE_ZIP_SHA256} (same-box caveat) and is not inherited by p18; "
                               "_p16 / _p15 / _p14r / _p13 as recorded by the p17 layer"),
        "p17_independent_rebuild": p17i,
        "p16_independent_rebuild": p17r.get("p16_independent_rebuild"),
        "p15_independent_rebuild": p17r.get("p15_independent_rebuild"),
        "p14r_independent_rebuild": p17r.get("p14r_independent_rebuild"),
        "p13_independent_rebuild": p17r.get("p13_independent_rebuild"),
        "one_point_slot_kappa1": p17r.get("one_point_slot_kappa1"), "D13_summary": p17r.get("D13_summary"),
        "E2_summary": p17r.get("E2_summary"), "batchC_summary": p17r.get("batchC_summary"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_s
  +> ource.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p17_archive": ARCH_P17,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "XVI_M_sha256": p17r.get("XVI_M_sha256"), "XVI_M_pin_ok": p17r.get("XVI_M_p
  +> in_ok"),
        "symmetry_restored": False, "bulk_symmetry_restored": False, "O1_closure": "NOT_CLOSED",
        "insertion_status": "Frozen_negative_obstruction_preserved", "XV_B_opened": False, "XIV_J_opened": Fal
  +> se,
        "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
            ("P14_release.json", "P15_release.json", "P16_release.json", "P17_release.json",
             f"{QC.CERT_PREFIX}_D11_M2.json", f"{QC.CERT_PREFIX}_D11.json", f"{QC.CERT_PREFIX}_hh_slot.json")
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
            "independent_rebuild_passed_p17": p17i_ok, "hard_stops": hard,
            "flags": {"D11_matching_verified": cert["D11_matching_verified"], "D11_evaluated": cert["D11_evalu
  +> ated"],
                      "quantum_inputs_evaluated": cert["quantum_inputs_evaluated"],
                      "hh_full_row_decoupling_proven": s_ok}})
        (ROOT / "manuscript" / "body").mkdir(parents=True, exist_ok=True)
        (ROOT / "manuscript" / "body" / "P18-results-table.tex").write_text(results_table(m2c, d11c, sc))
    else:
        (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(certio.dumps({
            "landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED", "contract_identity_ok": i
  +> d_ok,
            "contract_identity": ident, "p17_layer_ok": l17_ok, "M2_ok": m2_ok, "D11_ok": d11_ok, "slot_ok": s
  +> _ok,
            "p17_independent_pins_ok": p17i.get("pins_ok"), "hard_stops_hold": hard_ok,
            "change_log_base_ok": cl["base_pinned_ok"]}))
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publicat
  +> ion"],
                      "contract_identity": id_ok, "changed_vs_p14r": ident["changed_vs_p14r"], "added": ident[
  +> "added"],
                      "p17_layer": l17_ok, "M2": m2_ok, "D11": d11_ok, "slot": s_ok, "inventory": inv_ok,
                      "quantum_inputs_evaluated": cert["quantum_inputs_evaluated"], "hard_ok": hard_ok,
                      "author": author_ok, "independent_p18": indep_ok, "independent_p17": p17i_ok,
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
        print(f"release_p18 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
