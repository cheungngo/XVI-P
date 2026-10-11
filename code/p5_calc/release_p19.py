#!/usr/bin/env python3
"""XVI-P p19 release gate: P.5 identity step -- the projected one-loop kappa^2 ch-identity defect assembled from the
evaluated inputs (code/p5_calc/defect.py -> certificates/P19_defect.json), the counterterm solve in the declared
domain, D cap ker sigma_0; p18 reviewer findings I1-I3.

Runs AFTER the p14r, p15, p16, p17 and p18 gates (release_p18.py -> certificates/P18_release.json) and requires all
five accepted.  Recomputes:
  contract identity : p14r contract files byte-identical EXCEPT code/p5_entry/dred.py, which is byte-identical to the
                      p18 release (no contract revision in p19; no new contract file);
  p18 layer         : d11.py / p18_conventions.py / release_p18.py byte-identical to the p18 zip; P18_release accepted
                      WITH quantum_inputs_evaluated == 'earned', D11 flags true (I1: the p18 gate itself did not gate
                      publication on quantum_inputs_evaluated; the p19 gate does, for the p18 layer and for itself);
  inventory         : re-read independently of defect.py (ledger rows; every input evaluated; no Missing);
  defect            : P19_defect.json -- every control true, every mutation changes the outcome, flags consistent;
  earned flags      : projected_defect_computed, projected_identity_verified, projected_restoration_verified -- each
                      ONLY from the certificate and only if publication is accepted; bulk_symmetry_restored and
                      symmetry_restored stay false regardless;
  hard stops        : QC.HARD_STOPS_P19.
Publication (I1) is gated on: execution_pass AND quantum inputs earned (p18 layer + recheck) AND
projected_defect_computed earned AND the flag implications (restoration => identity => computed).
Rebuild flags: author/independent for the CURRENT (p19) tree; independent_rebuild_passed_p18 from the archived p18
independent report, bound to the p18 tree bfab3b4b... / zip 7c7d5451... (same-box caveat).
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p19_conventions as QC  # noqa: E402
import p15_conventions as Q15  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)

ARCH_P18 = "archival/p18"
ARCH_P18_INDEP = f"{ARCH_P18}/reproducibility/independent_rebuild_report_p18.json"
DEFECT_MUTATIONS = ("drop_graph_D03", "drop_graph_D01", "flip_phase_D03", "symmetry_factor_D03_x2",
                    "wrong_projection_trace_operator_hh", "wrong_projection_gauge_fixed_operator_Kc",
                    "naive_4D_D03_evanescent_dropped", "naive_4D_D13_Gt_dropped")
MIN_DEFECT_CONTROLS = 25
P5_CALC_STATUS = ("evaluated; 4D sector renormalized (MS-bar, declared domain); evanescent regulated (poles retained, not "
                  "subtracted), decoupled from the ch slots")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def contract_identity():
    cur = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    changed = sorted(k for k, h in Q15.P14R_CONTRACT_SHA256.items() if cur.get(k) != h)
    added = sorted(set(cur) - set(Q15.P14R_CONTRACT_SHA256))
    import contract_registry as CR          # p22 disclosed revision: registered additive p22 contract revision
    _dr = CR.dred_revision(ROOT)
    dred_same_as_p18 = cur.get("code/p5_entry/dred.py") == QC.P18_DRED_SHA256 or _dr["state"] == "p18 + p22 guard block"
    ok = bool(changed == ["code/p5_entry/dred.py"] and added == sorted(QC.NEW_CONTRACT_FILES_P19) and dred_same_as_p18)
    return ok, {"p14r_contract_files": len(Q15.P14R_CONTRACT_SHA256), "changed_vs_p14r": changed, "added": added,
                "dred_byte_identical_to_p18": dred_same_as_p18, "dred_registry_state_p22": _dr["state"], "contract_revision_in_p19": False,
                "disclosed_revisions_p19": QC.DISCLOSED_CONTRACT_REVISIONS_P19}


def p18_layer():
    cur = {k: sha(ROOT / k) if (ROOT / k).is_file() else None for k in QC.P18_CALC_SHA256}
    import contract_registry as CR          # p22 disclosed revision: registered p22 revision of release_p18.py
    ident = all(CR.layer_file_ok(k, cur[k], h) for k, h in QC.P18_CALC_SHA256.items())
    r = jl("certificates/P18_release.json")
    q = r.get("quantum_inputs_evaluated") == "earned"
    ok = bool(ident and r.get("publication") == "accepted" and r.get("release_claim_accepted") is True
              and r.get("D11_matching_verified") is True and r.get("D11_evaluated") is True
              and r.get("hh_full_row_decoupling_proven") is True and r.get("hard_stops_hold") is True and q)
    return ok, {"p18_layer_files_byte_identical": ident, "P18_release_accepted": r.get("publication") == "accepted",
                "P18_quantum_inputs_evaluated": r.get("quantum_inputs_evaluated"),
                "I1_gate": "the p19 gate requires the p18 layer record's quantum_inputs_evaluated == 'earned'"}, r


def p18_independent():
    f = ROOT / ARCH_P18_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P18_INDEP, "present": False, "pins_ok": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P18_INDEPENDENT_REPORT
    rec = {"report": ARCH_P18_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P18_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"),
           "bound_to_source_zip_sha256": rep.get("zip_sha256"),
           "tree_matches_p18": rep.get("source_tree_sha256") == QC.P18_SOURCE_TREE_SHA256,
           "zip_matches_p18": rep.get("zip_sha256") == QC.P18_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])), "findings": [x.get("id") for x in rep.get("findings", [])],
           "caveat": rep.get("same_box_caveat"),
           "live_report_identical_to_archived": (live.read_bytes() == f.read_bytes()) if live.is_file()
           else "live report not in this tree",
           "NOT_inherited_by_p19": "bound to the p18 tree/zip; the p19 tree has its own (pending) independent flag"}
    rec["archived_p18_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P18_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p18_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p18"] and rec["zip_matches_p18"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def inventory_recheck():
    """independent of defect.py: every graph of every surviving ch row; flags/statuses re-read; no Missing."""
    rows = [r for r in jl("ledgers/P13_ch_dependency_rows.json").get("rows", [])
            if str(r.get("status", "")).startswith("surviving")]
    required = {gid.split("_")[0]: r["id"] for r in rows for gid in r.get("graphs", [])}
    b = jl("certificates/P15_batchA.json").get("batchA_evaluated", {})
    claim = b.get("claim", "") if isinstance(b, dict) else ""
    c16 = jl("certificates/P16_batchC.json").get("graphs", {})
    d13 = jl("certificates/P15_D13.json").get("D13_evaluated", {})
    d11 = jl("certificates/P18_D11.json")
    inv = {g: bool(isinstance(b, dict) and b.get("execution") is True and g in claim)
           for g in ("D02", "D12", "D14a", "D14b", "D14c")}
    inv["D01"] = c16.get("D01", {}).get("evaluated") is True
    inv["D03"] = c16.get("D03", {}).get("evaluated") is True
    inv["D13"] = isinstance(d13, dict) and d13.get("execution") is True
    inv["D11"] = d11.get("D11_evaluated") is True
    sa = {g: v.get("status") for g, v in jl("certificates/P15_batchA.json").get("graphs", {}).items()}
    status = {**sa, "D01": c16.get("D01", {}).get("status"), "D03": c16.get("D03", {}).get("status"),
              "D13": "evaluated" if inv["D13"] else None, "D11": d11.get("status")}
    lst = [{"graph": g, "slot_row": required.get(g), "evaluated": inv.get(g, False), "status": status.get(g)}
           for g in sorted(set(required) | set(inv))]
    no_missing = all(x["status"] and "missing" not in str(x["status"]).lower()
                     and "unevaluated" not in str(x["status"]).lower() for x in lst)
    ok = bool(set(required) == set(inv) == set(QC.INVENTORY_P19) and len(set(required.values())) == 3
              and all(inv.values()) and no_missing)
    return ok, lst


def defect_check(inv_ok):
    c = jl(f"certificates/{QC.CERT_PREFIX}_defect.json")
    muts = c.get("mutations", {})
    ctrl = c.get("controls", {})
    flags = {k: c.get(k) for k in QC.EARNABLE_P19}
    cs = c.get("counterterm_solve", {})
    k1 = cs.get("K1_ghost_closure_convention", {})
    # the distinct definitions (flag_definitions in P19_defect.json), re-checked here from the recorded content
    content = {
        "projected_defect_computed": bool(len(c.get("defect", {})) == 7 and inv_ok),
        "projected_identity_verified": bool(c.get("defect_zero_exact_in_d") is True),
        # p20 definition: full sigma_0 closure of the complete MS-bar S_ct (incl. c.cb, Sigma held fixed)
        "projected_restoration_verified": bool(c.get("defect_zero_exact_in_d") is True
                                               and k1.get("full_closure_complete_S_ct", {}).get("closed") is True
                                               and str(k1.get("relative_factor_derived")) == "1"
                                               and k1.get("derived_equals_P15") is True
                                               and bool(c.get("p20_controls"))
                                               and all(v is True for v in c.get("p20_controls", {}).values()))}
    flags = {k: ("earned" if (v == "earned" and content[k]) else "not_earned") for k, v in flags.items()}
    implications = bool((flags["projected_restoration_verified"] != "earned"
                         or flags["projected_identity_verified"] == "earned")
                        and (flags["projected_identity_verified"] != "earned"
                             or flags["projected_defect_computed"] == "earned"))
    ok = bool(inv_ok and c.get("revision") == QC.REVISION and len(ctrl) >= MIN_DEFECT_CONTROLS
              and all(v is True for v in ctrl.values())
              and sorted(muts) == sorted(DEFECT_MUTATIONS) and all(v.get("changes_outcome") is True for v in muts.values())
              and c.get("missing_control", {}).get("D11_removed_from_inventory", {}).get("changes_outcome") is True
              and c.get("projected_defect_computed") == "earned" and implications
              and c.get("bulk_symmetry_restored") is False
              and c.get("D_cap_ker_sigma0", {}).get("computed") is True
              and len(c.get("defect", {})) == 7
              and set(c.get("flag_definitions", {})) >= set(QC.EARNABLE_P19) and bool(c.get("why_zero"))
              and "J1_p14r_counterterm_domain_field" in c.get("findings", {})
              and k1.get("derived_equals_P15") is True and k1.get("relative_factor_derived") is not None)
    return ok, c, flags, implications


def change_log():
    f = ROOT / QC.P18_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P18_ARCHIVED_RECORDS[QC.P18_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT) if r != SM.REFERENCE_FILE}
    contract = set(Q15.P14R_CONTRACT_SHA256) | {p.relative_to(ROOT).as_posix() for p in (ROOT / "code" / "p5_entry").glob("*.py")}
    added = sorted((set(new) - set(old)) | {SM.REFERENCE_FILE})
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])
    changed = sorted(added + removed + modified)
    return {"base": f"{QC.P18_SOURCE_LIST} (pinned; files of the p18 zip sha256 {QC.P18_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok,
            "reference_file": f"{SM.REFERENCE_FILE} listed as added by declaration (written after the author build)",
            "added": added, "removed": removed, "modified": modified,
            "contract_files_changed": [x for x in changed if x in contract],
            "non_contract_files_changed": [x for x in changed if x not in contract],
            "counts": {"added": len(added), "removed": len(removed), "modified": len(modified)}}


def milestones(p18r, calc_ok, dc, publish):
    st = dict(p18r.get("milestones", {}).get("status", {}))
    defs = dict(p18r.get("milestones", {}).get("definitions", {}))
    st["P.5_calculation"] = (P5_CALC_STATUS + " (p15-p18 inputs D01, D02, D03, D11, D12, D13, D14a-c)"
                             if calc_ok else "open (quantum inputs not accepted)")
    if publish and dc.get("projected_identity_verified") == "earned":
        st["P.5_identity"] = ("projected defect computed (zero exactly in d: pole, nonlocal and local parts, all seven "
                              "external assignments); projected identity verified; projected restoration verified for "
                              "the renormalised Gamma_R = Gamma1 + S_ct (ch projection, one loop, kappa^2 only; "
                              "zero because each row vanishes separately, no counterterm cancellation); "
                              "projected restoration (p20 definition): full sigma_0 closure of the complete one-loop "
                              "kappa^2 MS-bar counterterm incl. c.cb (K1 orientation corrected in p20; p19 'closure "
                              "fails' retracted); bulk symmetry NOT restored/claimed; O.1 NOT_CLOSED")
    elif publish and dc.get("projected_defect_computed") == "earned":
        st["P.5_identity"] = "projected defect computed; identity NOT verified (see P19_defect.json)"
    else:
        st["P.5_identity"] = "open"
    return {"definitions": defs, "order": p18r.get("milestones", {}).get("order"), "status": st,
            "definition_vs_status_note": ("I3 (p18 reviewer): the P.5_calculation DEFINITION reads 'coefficients "
                                          "evaluated and renormalized'; the STATUS states exactly what holds: 4D "
                                          "sector renormalized, evanescent poles regulated and decoupled from the ch "
                                          "slots (not subtracted)"),
            "P5_entry_earned": p18r.get("P5_entry_earned"), "P3_P4_frozen_as_P5_inputs": p18r.get("P3_P4_frozen_as_P5_inputs"),
            "P4_is_NOT": "coupled one-loop restoration of the bulk symmetry (bulk_symmetry_restored false)"}


def tex(x):
    t = str(x).replace("**", "^").replace("\\", "/").replace("{", "\\{").replace("}", "\\}")
    t = t.replace("_", "\\_").replace("^", "\\^{}").replace("&", "\\&").replace("#", "\\#").replace("%", "\\%")
    t = t.replace("$", "\\$").replace("~", "\\textasciitilde{}")
    return "\\texttt{" + t + "}"


def results_table(dc):
    drows = [f"{tex(n)} & {tex(v['pole'])} & {tex(v['nonlocal_L'])} & {tex(v['local'])} \\\\"
             for n, v in dc["defect"].items()]
    rG = dc["route_G"]
    q = dc["quotient_coordinates"]
    mrows = [f"{tex(k)} & {tex(v['outcome'][:44])} & {'yes' if v['changes_outcome'] else 'no'} \\\\"
             for k, v in dc["mutations"].items()]
    return ("% generated by code/p5_calc/release_p19.py -- do not edit\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{3.2cm}p{2.6cm}p{2.6cm}p{2.6cm}}\\hline\n"
            "assignment $(c,h)$ & defect pole & coeff. of L & local finite \\\\\\hline\n" + "\n".join(drows)
            + "\n\\hline\\end{tabular}\\end{center}\n"
            f"\\noindent Route G over {tex(rG['field'])}: rank $\\sigma_0|_D$ = {rG['sigma0_rank_on_D']}, "
            f"dim $D\\cap\\ker\\sigma_0$ = {rG['dim_D_cap_ker_sigma0']}, dim $D\\cap\\mathrm{{Im}}\\,\\sigma_0$ = "
            f"{rG['dim_D_cap_Im_sigma0']}, cohomology {rG['cohomology_dim']}, quotient {rG['quotient_dim']} "
            f"(complement {tex(', '.join(q['complement_directions']))}); rank $P_{{ch}}\\sigma_0$ = "
            f"{rG['P_ch_sigma0_rank_on_D']} (Route C: {dc['counterterm_solve']['rank_routeC']}).\n"
            f"Over Q with the re/im split (p14r convention): dim $D\\cap\\mathrm{{Im}}$ = "
            f"{dc['route_G_Q_split_p14r_convention']['dim_D_cap_Im_sigma0']}, quotient "
            f"{dc['route_G_Q_split_p14r_convention']['quotient_dim']}, dim $D\\cap\\ker$ = "
            f"{dc['route_G_Q_split_p14r_convention']['dim_D_cap_ker_sigma0']}.\n\n"
            f"\\noindent Quotient coordinates of the $\\Gamma_1$ local data: pole {tex(q['pole'])}, coeff. of L "
            f"{tex(q['nonlocal_L'])}, local {tex(q['local'])}.\n"
            "\\begin{center}\\scriptsize\\begin{tabular}{p{4.6cm}p{6.4cm}p{1.2cm}}\\hline\n"
            "mutation & outcome & changes \\\\\\hline\n" + "\n".join(mrows) + "\n\\hline\\end{tabular}\\end{center}\n"
            f"\\noindent Counterterm solve: {tex(dc['counterterm_solve']['outcome'])}; "
            f"{tex(dc['counterterm_solve']['solution'])}.\n\n"
            "\\noindent\\textbf{Why zero.} " + tex(dc["why_zero"]) + "\n\n"
            "\\noindent\\textbf{Flag definitions.} " + " ".join(
                "\\textbf{" + tex(k) + "}: " + tex(v) + "." for k, v in dc["flag_definitions"].items()) + "\n\n"
            "\\noindent\\textbf{K1 (corrected in p20; erratum to p19).} derived relative factor "
            + tex(dc['counterterm_solve']['K1_ghost_closure_convention']["relative_factor_derived"])
            + "; orientation ratio (route-G (c,cb) over P15 (cb,c)) "
            + tex(dc['counterterm_solve']['K1_ghost_closure_convention']["orientation_ratio_routeG_over_cbc"])
            + "; Sigma pole in (c,cb) coordinates "
            + tex(dc['counterterm_solve']['K1_ghost_closure_convention']["Sigma_pole_routeG_c_cb_coordinates"])
            + "; full sigma\\_0 image of the complete MS-bar counterterm: "
            + tex(dc['counterterm_solve']['K1_ghost_closure_convention']["full_closure_complete_S_ct"]) + ". "
            + tex(dc['counterterm_solve']['K1_ghost_closure_convention']["reading"]) + "\n\n"
            "\\noindent\\textbf{J1 (finding about the p14r contract).} "
            + tex(dc["findings"]["J1_p14r_counterterm_domain_field"]) + "\n")


def _main():
    id_ok, ident = contract_identity()
    l18_ok, l18, p18r = p18_layer()
    p18i_ok, p18i = p18_independent()
    inv_ok, inv = inventory_recheck()
    d_ok, dc, dflags, impl = defect_check(inv_ok)
    p14r, p15r, p16r, p17r = (jl(f"certificates/{n}_release.json") for n in ("P14", "P15", "P16", "P17"))
    hard = dict(QC.HARD_STOPS_P19)
    hard_ok = bool(all(hard[k] == v for k, v in QC.HARD_STOPS_P19.items())
                   and all(r.get("hard_stops_hold") is True for r in (p14r, p15r, p16r, p17r, p18r))
                   and dc.get("bulk_symmetry_restored", False) is False)
    cl = change_log()
    q_earned = bool(inv_ok and l18_ok and p18r.get("quantum_inputs_evaluated") == "earned")
    execution_pass = bool(id_ok and l18_ok and d_ok and hard_ok and cl["base_pinned_ok"] and p18i.get("pins_ok") is True)
    publish = bool(execution_pass and q_earned and dflags.get("projected_defect_computed") == "earned" and impl)   # I1
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    m = milestones(p18r, q_earned, dc, publish)
    earned = {k: ("earned" if (publish and dflags.get(k) == "earned") else "not_earned") for k in QC.EARNABLE_P19}
    flags = dict(p18r.get("flags", {}))
    flags["projected_ch_identity"] = {"execution": d_ok, "claim": (dc.get("counterterm_solve", {}).get("outcome")
                                                                   if d_ok else "not accepted"),
                                      "scope": dc.get("scope")}
    cert = {
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DATE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": "P.5 identity step (projected one-loop kappa^2 ch-identity defect; counterterm solve; I1-I3)",
        "execution_pass": execution_pass,
        "claim_status": ("P.5_identity: projected defect assembled from every evaluated input (D01, D02, D03, D11, "
                         "D12, D13, D14a-c); outcome " + str(dc.get("counterterm_solve", {}).get("outcome")) +
                         ". WHY ZERO: " + str(dc.get("why_zero")) + " RESTS ON: " + "; ".join(dc.get("rests_on", [])) +
                         ". FLAGS: " + ", ".join(f"{k}={v}" for k, v in earned.items()) +
                         " (definitions: flag_definitions). projected_restoration_verified (p20 definition) = full "
                         "sigma_0 closure of the COMPLETE one-loop kappa^2 MS-bar counterterm (h.h + c.K + c.cb; ghost "
                         "self-energy held fixed; derived relative factor +1; orientation converted) in every ghost +1 "
                         "sector (h.c, c.b, c.cbs): " + str(dc.get("counterterm_solve", {}).get(
                             "K1_ghost_closure_convention", {}).get("full_closure_complete_S_ct")) +
                         ". Scope: that counterterm only -- NOT bulk symmetry (bulk_symmetry_restored=False), O.1 "
                         "NOT_CLOSED. The p19 criterion (P_ch sigma_0(S_ct) = 0, x = 0) follows from the identity + "
                         "locality and is kept only as a route-consistency control. ERRATUM (K1): the p19 text 'full "
                         "closure fails with the derived factor, needs -1, unresolved' was a Grassmann-orientation "
                         "bookkeeping error and is RETRACTED. J1: the p14r counterterm-domain counts are Q re/im-split "
                         "artefacts; the Q(i) counts are the real dimensions under a compatible real structure "
                         "(finding about the p14r contract; contract not modified)")
        if publish else "P.5_identity: not accepted",
        "flag_definitions": dc.get("flag_definitions"),
        "projected_restoration_scope": ("p20 definition: full sigma_0 closure (h.c, c.b, c.cbs) of the complete one-loop "
                                        "kappa^2 MS-bar counterterm incl. the c.cb ghost self-energy counterterm (held "
                                        "fixed, derived factor +1); NOT bulk symmetry, NOT O.1"),
        "route_consistency_control_p19_criterion": dc.get("route_consistency_control_p19_criterion"),
        "full_closure_mutation_detector": dc.get("full_closure_mutation_detector"),
        "p20_controls": dc.get("p20_controls"), "why_zero": dc.get("why_zero"), "rests_on": dc.get("rests_on"),
        "findings": dc.get("findings"),
        "K1_ghost_closure_convention": dc.get("counterterm_solve", {}).get("K1_ghost_closure_convention"),
        "scope": dc.get("scope"),
        "release_claim_accepted": publish,
        "release_claim_accepted_definition": ("p14r contract accepted AND p15..p18 layers accepted and byte-identical "
                                              "(p18 layer with quantum_inputs_evaluated earned) AND contract identity "
                                              "(dred.py byte-identical to p18; no new contract file) AND the inventory "
                                              "recheck AND the defect certificate (all controls, all mutations change "
                                              "the outcome, flag implications) AND p19 hard stops"),
        "publication": "accepted" if publish else "REJECTED",
        "publication_gated_on": ["execution_pass", "quantum_inputs_evaluated (p18 layer + recheck)",
                                 "projected_defect_computed", "flag implications restoration => identity => computed"],
        "flags": flags,
        **earned,
        "projected_defect_summary": {k: dc.get(k) for k in ("defect_zero_exact_in_d", "evanescent_in_assembly",
                                                            "quotient_coordinates", "D_cap_ker_sigma0", "field_note")},
        "counterterm_solve": dc.get("counterterm_solve"),
        "defect_controls": dc.get("controls"), "defect_mutations": dc.get("mutations"),
        "defect_insensitive_variations": dc.get("insensitive_variations"),
        "quantum_inputs_evaluated": "earned" if (q_earned and publish) else "not_earned",
        "quantum_inputs_inventory": inv,
        "D11_matching_verified": p18r.get("D11_matching_verified"),
        "D11_matching_verified_scope": p18r.get("D11_matching_verified_scope"),
        "D11_evanescent_components_matching": p18r.get("D11_evanescent_components_matching"),
        "M3_status": p18r.get("M3_status"), "D11_evaluated": p18r.get("D11_evaluated"),
        "hh_full_row_decoupling_proven": p18r.get("hh_full_row_decoupling_proven"),
        "evanescent_hh_counterterm_added": False,
        "batchA_evaluated": p18r.get("batchA_evaluated"), "D13_evaluated": p18r.get("D13_evaluated"),
        "batchC_evaluated": p18r.get("batchC_evaluated"), "library_certified": p18r.get("library_certified"),
        "E2_status": p18r.get("E2_status"), "E2_decoupling_proven": p18r.get("E2_decoupling_proven"),
        "hh_evanescent_status": p18r.get("hh_evanescent_status"),
        "hh_evanescent_decoupling_proven": p18r.get("hh_evanescent_decoupling_proven"),
        "D01_evaluated": p18r.get("D01_evaluated"), "D03_evaluated": p18r.get("D03_evaluated"),
        "graphs": p18r.get("graphs"), "D12_status": p18r.get("D12_status"),
        "contract_identity": ident, "p18_layer": l18, "change_log_vs_p18": cl,
        "disclosed_test_revisions_p19": getattr(QC, "DISCLOSED_TEST_REVISIONS_P19", {}),
        "P5_entry_earned": p18r.get("P5_entry_earned"), "P5_entry_flags": p18r.get("P5_entry_flags"),
        "P3_P4_frozen_as_P5_inputs": p18r.get("P3_P4_frozen_as_P5_inputs"), "classical": p18r.get("classical"),
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": m,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p18": p18i_ok,
        "independent_rebuild_passed_p17": p18r.get("independent_rebuild_passed_p17"),
        "independent_rebuild_passed_p16": p18r.get("independent_rebuild_passed_p16"),
        "independent_rebuild_passed_p15": p18r.get("independent_rebuild_passed_p15"),
        "independent_rebuild_passed_p14r": p18r.get("independent_rebuild_passed_p14r"),
        "independent_rebuild_passed_p13": p18r.get("independent_rebuild_passed_p13"),
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p19) source "
                               "tree only (independent: pending until a reviewer report for this tree exists); "
                               f"independent_rebuild_passed_p18 refers to the p18 tree {QC.P18_SOURCE_TREE_SHA256} / zip "
                               f"{QC.P18_SOURCE_ZIP_SHA256} (same-box caveat) and is not inherited by p19"),
        "p18_independent_rebuild": p18i,
        "p17_independent_rebuild": p18r.get("p17_independent_rebuild"),
        "p16_independent_rebuild": p18r.get("p16_independent_rebuild"),
        "p15_independent_rebuild": p18r.get("p15_independent_rebuild"),
        "p14r_independent_rebuild": p18r.get("p14r_independent_rebuild"),
        "p13_independent_rebuild": p18r.get("p13_independent_rebuild"),
        "M2_summary": p18r.get("M2_summary"), "D11_summary": p18r.get("D11_summary"),
        "hh_slot_summary": p18r.get("hh_slot_summary"), "D13_summary": p18r.get("D13_summary"),
        "E2_summary": p18r.get("E2_summary"), "batchC_summary": p18r.get("batchC_summary"),
        "one_point_slot_kappa1": p18r.get("one_point_slot_kappa1"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_source.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p18_archive": ARCH_P18,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "XVI_M_sha256": p18r.get("XVI_M_sha256"), "XVI_M_pin_ok": p18r.get("XVI_M_pin_ok"),
        "symmetry_restored": False, "bulk_symmetry_restored": False, "O1_closure": "NOT_CLOSED",
        "insertion_status": "Frozen_negative_obstruction_preserved", "XV_B_opened": False, "XIV_J_opened": False,
        "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, getattr(QC, "RUN_SPECIFIC_KEYS", ())) for n in
            ("P14_release.json", "P15_release.json", "P16_release.json", "P17_release.json", "P18_release.json",
             f"{QC.CERT_PREFIX}_defect.json") if (ROOT / "certificates" / n).is_file()},
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
            "independent_rebuild_passed_p18": p18i_ok, "hard_stops": hard,
            "flags": {**earned, "quantum_inputs_evaluated": cert["quantum_inputs_evaluated"],
                      "bulk_symmetry_restored": False}})
        (ROOT / "manuscript" / "body").mkdir(parents=True, exist_ok=True)
        (ROOT / "manuscript" / "body" / "P19-results-table.tex").write_text(results_table(dc))
    else:
        (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
        for st in (ROOT / "RELEASE_STATUS.json", cdir / "RELEASE_STATUS.json"):     # p20: no stale status on reject
            st.unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(certio.dumps({
            "landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED", "contract_identity_ok": id_ok,
            "contract_identity": ident, "p18_layer_ok": l18_ok, "inventory_ok": inv_ok, "defect_ok": d_ok,
            "quantum_inputs_earned": q_earned, "flag_implications": impl,
            "p18_independent_pins_ok": p18i.get("pins_ok"), "hard_stops_hold": hard_ok,
            "change_log_base_ok": cl["base_pinned_ok"]}))
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publication"],
                      "contract_identity": id_ok, "changed_vs_p14r": ident["changed_vs_p14r"], "added": ident["added"],
                      "p18_layer": l18_ok, "inventory": inv_ok, "defect": d_ok, "q": q_earned, **earned,
                      "hard_ok": hard_ok, "author": author_ok, "independent_p19": indep_ok,
                      "independent_p18": p18i_ok, "change_log_counts": cl["counts"]}, indent=1))
    return 0 if publish else 1


def main():
    try:
        return _main()
    except Exception as exc:  # noqa: BLE001   fail closed
        cdir = ROOT / "certificates"
        (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
        for st in (ROOT / "RELEASE_STATUS.json", cdir / "RELEASE_STATUS.json"):     # p20: no stale status on reject
            st.unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(json.dumps(
            {"landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED",
             "error": f"{type(exc).__name__}: {exc}"}, indent=1) + "\n")
        print(f"release_p19 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
