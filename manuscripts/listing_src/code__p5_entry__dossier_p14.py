#!/usr/bin/env python3
"""p14 dossier: the frozen P.3/P.4 chains (re-pointed to the p14 release gate, which recomputes the classical
acceptance from the frozen P13_* certificates) + the P.5 ENTRY chain.  Every link is resolved mechanically
(function in file via AST, certificate key = expected value, test present in tests/test_p14.py) by the frozen
p13 resolver (code/classical/dossier.py, imported, not edited).  Writes certificates/P14_dossier.json and
manuscript/body/P14-dossier-table.tex, and the P.5 entry summary manuscript/body/P14-entry-summary.tex (values
  +>  read
from the certificates of the build).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "code" / "classical"))
import dossier as D  # noqa: E402   (frozen p13 resolver)
import p14_conventions as PC  # noqa: E402
import certio  # noqa: E402

D.T = "tests/test_p14.py"
R, ALL_TRUE, NONEMPTY = D.R, D.ALL_TRUE, D.NONEMPTY
RS = "RELEASE_STATUS.json"
F_RL14 = "code/p5_entry/release_p14.py"
QO, PD = "certificates/P14_quantum_object.json", "certificates/P14_prescription_D11_matching.json"
CT, AM = "certificates/P14_counterterm_domain.json", "certificates/P14_amplitude_rules.json"
F_QO, F_PD, F_CT = "code/p5_entry/quantum_object.py", "code/p5_entry/prescription_d11.py", "code/p5_entry/coun
  +> terterm_domain.py"
F_AM, F_FZ, F_FY = "code/p5_entry/amplitude_rules.py", "code/p5_entry/freeze_p13.py", "code/p5_entry/feynman.p
  +> y"
F_SH = "code/p5_entry/shadow.py"
DR, F_DR = "certificates/P14_dred_rules.json", "code/p5_entry/dred.py"
F_HR = "code/p5_entry/hessian_route.py"


def classical_chains():
    """p13 chains, unchanged claims/evidence; RELEASE_STATUS keys moved under /classical; the release function
  +>  is the
    p14 fork of the p13 acceptance (release_p14.classical_block)."""
    out = []
    for m, name, rows in D.CHAINS:
        nr = []
        for r in rows:
            r = json.loads(json.dumps(r))
            if r["file"] == D.F_RL:
                r["file"], r["functions"] = F_RL14, ["classical_block"]
            for c in r["checks"]:
                if c["source"] == D.RS and not c["key"].startswith("/classical/"):
                    c["key"] = "/classical" + c["key"]
            nr.append(r)
        out.append((m, name + " [frozen P.3/P.4 input]", nr))
    return out


P5_CHAIN = ("P.5_entry", "quantum object -> prescription/D11 matching -> counterterm domain -> amplitude rules
  +>  -> gate", [
    R("P5E.1", "quantum object in transformed variables: S_Psi parts, eps = -1, b retained (elimination makes 
  +> S quadratic "
               "in cbar*'), Gamma_1 independent of cbar*', b*'; pullback != quantum theorem", F_QO,
      ["main", "patterns", "b_elimination"],
      [(QO, "/quantum_action_defined", True), (QO, "/Q1_transformed_variables/eps_derived", -1),
       (QO, "/Q2_fields_antifields_b/b_decision", "RETAINED and integrated"),
       (QO, "/Q2_fields_antifields_b/Gamma1_independent_of", ["bs", "cbs"]),
       (QO, "/Q5_kappa_loop_bookkeeping/ok", True),
       (QO, "/Q6_pullback_vs_theorem/quantum_gauge_change_theorem_asserted", False)],
      ["test_quantum_object"]),
    R("P5E.2", "ONE prescription: operational DRED (rules R1-R6), MS-bar, Feynman i0; scaleless rules defined 
  +> but not "
               "applied; quantum_prescription_defined requires the verified DRED rules", F_PD,
      ["main"], [(PD, "/quantum_prescription_defined", True), (PD, "/prescription/id", "P14_DRED_MSbar_Feynman
  +> I0"),
                 (PD, "/prescription_checks", ALL_TRUE),
                 (PD, "/prescription_checks/operational_DRED_rules_verified", True), (PD, "/D12_status", "Miss
  +> ing")],
      ["test_prescription_and_D11_matching"]),
    R("P5E.2b", "operational DRED: g4 = ghat + gtilde (tr d, 4-d), l and p in QdS, l_r = l.e_(r) lifting, ghat
  +> -projected "
                "Gram/PV reduction, contractions before Laurent with d symbolic; evanescent parts retained; pr
  +> emature "
                "d=4, tr ghat=4 and expand-before-contract are rejected", F_DR,
      ["reduce_tensor", "eta_trace_Gt", "toy_four_d_part", "toy_evanescent_trace", "known_reductions", "lift_e
  +> xported",
       "main"],
      [(DR, "/dred_rules_verified", True), (DR, "/mutations_all_rejected", True),
       (DR, "/mutations/premature_d4/rejected", True), (DR, "/mutations/trace_ghat_eq_4/rejected", True),
       (DR, "/mutations/contract_after_laurent/rejected", True),
       (DR, "/toy_checks/T1_four_d_part/finite", "a/8 + b/4"), (DR, "/toy_checks/T2_evanescent_trace/finite", 
  +> "-a/2"),
       (DR, "/known_reductions/pass", True), (DR, "/evanescent_parts_present_in_exports", True),
       (DR, "/loop_evaluations_performed", False)],
      ["test_dred_rules_certificate", "test_dred_premature_d4_changes_finite_part_and_is_caught",
       "test_dred_evanescent_trace_is_d_minus_4_times_pole", "test_dred_trace_ghat_eq_4_rejected",
       "test_dred_known_reductions_and_contraction_engine"]),
    R("P5E.3", "D11 matching DEFINED (M1 exact integrand identity vs XVI-O V_tensor, 100 pairs; M3 CONDITIONAL
  +>  on M2: "
               "sd(u^R) 4, kernel sd <= 8, contact derivative order <= 4, contact space orders 0/2/4 = 2/4/5, 
  +> degree 4 "
               "imposed by normalization condition N4; no c delta; r = -i pi^2 XVI-O side only); NOT verified"
  +> , F_PD,
      ["M1_identity", "M3_local_space", "M3_contact_analysis"],
      [(PD, "/D11_matching_defined", True), (PD, "/D11_matching_verified", False),
       (PD, "/matching/M1_integrand_identity/mismatches", []),
       (PD, "/matching/M1_integrand_identity/component_pairs_checked", 100),
       (PD, "/matching/M1_integrand_identity/bound_to_export", True),
       (PD, "/matching/M3_local_difference/labels/scalar_extension_scaling_degree", 4),
       (PD, "/matching/M3_local_difference/labels/kernel_scaling_degree_bound", 8),
       (PD, "/matching/M3_local_difference/labels/local_contact_derivative_order_bound", 4),
       (PD, "/matching/M3_local_difference/lower_degree_contacts_excluded_by_N4/order_2_mu2", 4),
       (PD, "/matching/M3_local_difference/dimension", 5),
       (PD, "/matching/M3_local_difference/transverse_subspace_dimension", 2),
       (PD, "/matching/M4_finite_adjustments/u_R_c_delta_added_by_P", False),
       (PD, "/matching/M5_residue/r", "-i * pi**2")],
      ["test_prescription_and_D11_matching"]),
    R("P5E.4", "counterterm domain: kappa^1 empty, kappa^2 basis 11 (hh 5, cbar c 2, K'c 3, phi phi 1) generat
  +> ed "
               "mechanically; eight candidate directions modulo the computed exact equivalences, before imposi
  +> ng the "
               "identity constraints (no cohomological classification: D cap ker sigma_0 not computed); constr
  +> aint "
               "list, not an admission", F_CT,
      ["structures", "admissible_pairs", "rank", "main"],
      [(CT, "/counterterm_domain_defined", True), (CT, "/kappa1/basis_size", 0), (CT, "/kappa2/basis_size", 11
  +> ),
       (CT, "/equivalences/quotient_dimension", 8), (CT, "/equivalences/D_cap_ker_sigma0_computed", False),
       (CT, "/equivalences/S0_density_check/ok", True), (CT, "/XIV_J_opened", False), (CT, "/XV_B_opened", Fal
  +> se)],
      ["test_counterterm_domain"]),
    R("P5E.5", "amplitude rules: vertices (incl. ghost-graviton derivative terms, K' vertex), propagators, ord
  +> ering, "
               "multiplicities, symmetry factors, signs; symbolic integrands; W1-W6 controls (W5 regenerates o
  +> nly "
               "D14a-c, D11, D13; W6 regenerates D01, D02, D03, D12)", F_AM,
      ["build_integrands", "verify", "W2", "W3", "W4", "W5"],
      [(AM, "/amplitude_rules_verified", True), (AM, "/controls/W1_wick_berezin_shadow/pass", True),
       (AM, "/controls/W4_ward_bose/pass", True), (AM, "/integrands_only", True),
       (AM, "/loop_evaluations_performed", False), (AM, "/graphs/D12/D12_status", "Missing")],
      ["test_amplitude_rules_and_mutations"]),
    R("P5E.5b", "independent Hessian/Tr-log regeneration of D01, D02, D03, D12 from the field-dependent Hessia
  +> n of "
                "S_Psi (own (h,b) inverse; not the Feynman-rule assembler) == exported integrands", F_HR,
      ["ell_table", "graviton_inverse", "ghost_inverse", "reference", "W6", "compare_exports"],
      [(AM, "/controls/W6_hessian_route/pass", True), (AM, "/W6_exports/all_agree", True),
       (AM, "/W6_exports/D01/n_mismatches", 0), (AM, "/W6_exports/D03/n_mismatches", 0)],
      ["test_hessian_route_regenerates_D01_D02_D03_D12"]),
    R("P5E.6", "mutations rejected: tadpole factor, ghost-loop sign, off-diagonal multiplicity, source/ghost o
  +> rder, "
               "ghost transport term", F_AM, ["apply_mutations", "main"],
      [(AM, "/mutations_all_rejected", True), (AM, "/mutations/omit_ghost_transport_term/rejected", True),
       (AM, "/mutations/reversed_source_ghost_order/rejected", True)],
      ["test_amplitude_rules_and_mutations"]),
    R("P5E.7", "Berezin/Wick shadow fixes symmetry factors and Grassmann signs independently", F_SH,
      ["expect", "gamma1", "run_shadows"], [(AM, "/controls/W1_wick_berezin_shadow/pass", True)],
      ["test_amplitude_rules_and_mutations"]),
    R("P5E.8", "P.3/P.4 freeze bound to the p13 tree (independent rebuild passed; same-box caveat); frozen cod
  +> e and "
               "values unchanged", F_FZ, ["freeze", "F1_independent", "F2_frozen_code", "F3_frozen_values"],
      [(RS, "/P3_P4_frozen_as_P5_inputs", True),
       (RS, "/p13_independent_rebuild/bound_to_source_tree_sha256", PC.P13_SOURCE_TREE_SHA256),
       (RS, "/p13_independent_rebuild/caveat", "CONTAINS:SAME box"),
       (RS, "/freeze/F2/changed_or_missing", []), (RS, "/freeze/F3/differences", [])],
      ["test_freeze_binding"]),
    R("P5E.9", "P.5 entry gate: earned iff all five contract flags hold; loop/restoration flags NOT earned", F
  +> _RL14,
      ["_main", "p5_entry_flags", "milestones_p14"],
      [(RS, "/P5_entry_flags", ALL_TRUE), (RS, "/P5_entry_earned", True), (RS, "/hard_stops_hold", True),
       (RS, "/hard_stops/quantum_inputs_evaluated", "not_earned"),
       (RS, "/hard_stops/projected_identity_verified", "not_earned"),
       (RS, "/hard_stops/bulk_symmetry_restored", False), (RS, "/D11_matching_verified", False),
       (RS, "/D12_status", "Missing"), (RS, "/hard_stops/O1_closure", "NOT_CLOSED")],
      ["test_p5_entry_gate_and_hard_stops"]),
    R("P5E.10", "publication gate (p14) re-invoked before pdf/zip/manifest stages", "tools/build.py",
      ["publication_gate", "pdf_readback"], [], ["test_resumed_stage_build_blocked"]),
])


def build():
    cache = {}
    rs = json.loads((ROOT / RS).read_text())
    chains = [{"milestone": m, "chain": name, "rows": [D.resolve_row(r, cache) for r in rows]}
              for m, name, rows in classical_chains() + [P5_CHAIN]]
    sl = D.slots(cache)
    resolved = all(r["resolved"] for ch in chains for r in ch["rows"]) and all(s["resolved"] for s in sl)
    return {
        "landmark": "XVI-P", "revision": PC.REVISION, "document": "P.5 entry dossier (with the frozen P.3/P.4 
  +> chains)",
        "status_of_this_document": ("package evidence for XVI-P (unregistered; XVI-O conv:package): an archive
  +> , a listing "
                                    "and a manifest are not a series certificate. Does not update XVI-O "
                                    "(prop:kappa2-master stays Partial there; symmetry_restored false; O.1 NOT
  +> _CLOSED)."),
        "milestone_definitions": rs.get("milestones", {}).get("definitions"), "milestone_status": rs.get("mile
  +> stones", {}),
        "chains": chains, "quantum_input_slots": sl, "hard_stops": rs.get("hard_stops", {}),
        "reproducibility": {k: rs.get(k) for k in ("author_rebuild_passed", "independent_rebuild_passed")},
        "p13_independent_rebuild": rs.get("p13_independent_rebuild"),
        "P3_P4_frozen_as_P5_inputs": rs.get("P3_P4_frozen_as_P5_inputs"),
        "all_links_resolved": resolved,
        "n_rows": sum(len(ch["rows"]) for ch in chains), "n_slots": len(sl),
    }


def table(d):
    t = D.table(d).replace("P14\\_", "")
    p13 = d.get("p13_independent_rebuild") or {}
    extra = (r"; p13 \texttt{independent\_rebuild\_passed} = " + D.tex(json.dumps(p13.get("independent_rebuild
  +> _passed")))
             + r" (bound to the p13 source tree \texttt{" + D.tex(PC.P13_SOURCE_TREE_SHA256[:16]) + r"...}; ca
  +> veat: "
             + D.tex(PC.INDEPENDENT_CAVEAT) + ")")
    t2, n = re.subn(r"(\\texttt\{P3\\_P4\\_frozen\\_as\\_P5\\_inputs\} = [^.]*)\.\}", lambda m_: m_.group(1) +
  +>  extra + ".}", t)
    assert n == 1
    return t2.replace("(package evidence, read from RELEASE\\_STATUS at build time):}",
                      "(package evidence, read from RELEASE\\_STATUS at build time; p14 flags bound to the p14
  +>  tree):}")


def summary_tex():
    """P.5 entry summary tables, every value read from the certificates of this build."""
    cj = lambda n: json.loads((ROOT / "certificates" / n).read_text())  # noqa: E731
    qo, pd, ct, am = cj("P14_quantum_object.json"), cj("P14_prescription_D11_matching.json"), \
        cj("P14_counterterm_domain.json"), cj("P14_amplitude_rules.json")
    dr = cj("P14_dred_rules.json")
    rs = json.loads((ROOT / RS).read_text())
    t = D.tex
    L = [r"\begin{center}\small", r"\begin{tabular}{@{}p{5.2cm}p{10.3cm}@{}}", r"\toprule contract item & valu
  +> e (from the certificates of this build)\\ \midrule"]
    q2 = qo["Q2_fields_antifields_b"]
    m1 = pd["matching"]["M1_integrand_identity"]
    m3 = pd["matching"]["M3_local_difference"]
    eq = ct["equivalences"]
    rows = [
        ("integrated fields", ", ".join(q2["integrated"])),
        ("external antifields", ", ".join(f"{k}: {v}" for k, v in q2["external_antifields"].items())),
        ("b", f"{q2['b_decision']}; det M_bb = {q2['b_justification']['elimination']['b_hessian_det']}; elimin
  +> ating b gives "
              f"{q2['b_justification']['elimination']['cbar_star_quadratic_terms']} terms quadratic in cbar*';
  +>  Gamma_1 "
              f"independent of {', '.join(q2['Gamma1_independent_of'])}"),
        ("antifield shift", f"eps = {qo['Q1_transformed_variables']['eps_derived']} (derived)"),
        ("prescription", pd["prescription"]["id"] + ": " + pd["prescription"]["subtraction"]),
        ("i0", pd["prescription"]["i0"]),
        ("DRED rules", f"verified = {json.dumps(dr['dred_rules_verified'])}; T1 finite {dr['toy_checks']['T1_f
  +> our_d_part']['finite']} "
                       f"(premature d=4 would give {dr['mutations']['premature_d4'].get('finite_part_if_not_ca
  +> ught')}); "
                       f"T2 finite {dr['toy_checks']['T2_evanescent_trace']['finite']} ((d-4) x pole); mutatio
  +> ns: "
                       + ", ".join(f"{k} {'rejected' if v['rejected'] else 'NOT rejected'}" for k, v in dr["mu
  +> tations"].items())),
        ("D11 matching", f"defined = {json.dumps(pd['D11_matching_defined'])}, verified = "
                         f"{json.dumps(pd['D11_matching_verified'])}; M1: {m1['component_pairs_checked']} comp
  +> onent pairs, "
                         f"{len(m1['mismatches'])} mismatches; M3 (conditional on M2): kernel sd <= "
                         f"{m3['labels']['kernel_scaling_degree_bound']}, contact order <= "
                         f"{m3['labels']['local_contact_derivative_order_bound']}; contact space "
                         + ", ".join(f"{k} {v['dimension']}" for k, v in m3['bounded_contact_space'].items())
                         + f"; under N4 {m3['dimension']} (transverse {m3['transverse_subspace_dimension']}); 
  +> M2 "
                         f"{pd['matching']['M2_nonlocal_agreement_on_U']['status']}"),
        ("counterterm domain", f"kappa^1: {ct['kappa1']['basis_size']}; kappa^2: {ct['kappa2']['basis_size']} 
  +> ("
                               + ", ".join(f"{k} {v}" for k, v in ct['kappa2']['basis_size_by_sector'].items()
  +> )
                               + f"); sigma_0-equivalent: {eq['domain_cap_image']} ("
                               + ", ".join(f"{k} {v}" for k, v in eq['sector_cap_image'].items())
                               + f"); {eq['quotient_dimension']} candidate directions modulo the computed exac
  +> t "
                               "equivalences, before the identity constraints (D cap ker sigma_0 not computed)
  +> "),
        ("amplitude controls", ", ".join(f"{k}: {'pass' if v['pass'] else 'FAIL'}" for k, v in am["controls"].
  +> items())
         + "; W5 regenerates D14a-c, D11, D13; W6 (Hessian route) regenerates D01, D02, D03, D12 == exports: "
         + json.dumps(am["W6_exports"]["all_agree"])),
        ("mutations (must be rejected)", ", ".join(f"{k}: {'rejected' if v['rejected'] else 'NOT rejected'}"
                                                  for k, v in am["mutations"].items())),
        ("P.5 entry flags", ", ".join(f"{k} = {json.dumps(v)}" for k, v in rs["P5_entry_flags"].items())),
        ("P3_P4_frozen_as_P5_inputs", f"{json.dumps(rs['P3_P4_frozen_as_P5_inputs'])} ({rs['p13_independent_re
  +> build']['caveat']})"),
        ("P.5 entry", rs["milestones"]["status"]["P.5_entry"]),
    ]
    for k, v in rows:
        L.append(t(k) + " & " + t(v) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{center}", "",
          r"\begin{center}\small", r"\begin{tabular}{@{}lllrrrl@{}}",
          r"\toprule graph & prefactor & denominators & comps & monomials & deg & status \\ \midrule"]
    for g, r in am["graphs"].items():
        L.append(" & ".join([t(g), r"\texttt{" + t(r["prefactor"]) + "}", t(", ".join(r["denominators"])),
                             str(r["numerator_components"]), str(r["numerator_monomials"]), str(r["numerator_d
  +> egree"]),
                             t(r["status"].split(" (")[0].split(":")[0])]) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
    return "\n".join(L) + "\n"


def main():
    d = build()
    certio.write(ROOT / "certificates" / "P14_dossier.json", d)
    (ROOT / "manuscript" / "body").mkdir(parents=True, exist_ok=True)
    (ROOT / "manuscript" / "body" / "P14-dossier-table.tex").write_text(table(d))
    (ROOT / "manuscript" / "body" / "P14-entry-summary.tex").write_text(summary_tex())
    bad = [r["id"] for ch in d["chains"] for r in ch["rows"] if not r["resolved"]] + \
          [s["slot"] for s in d["quantum_input_slots"] if not s["resolved"]]
    print(json.dumps({"all_links_resolved": d["all_links_resolved"], "rows": d["n_rows"], "slots": d["n_slots"
  +> ],
                      "unresolved": bad}))
    return 0 if d["all_links_resolved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
