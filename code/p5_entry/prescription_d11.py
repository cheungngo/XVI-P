#!/usr/bin/env python3
"""XVI-P p14r Deliverable 2: ONE quantum prescription and the D11 matching note against XVI-O's frozen D11.

Prescription (P side): dimensional reduction (DRED) made OPERATIONAL in code/p5_entry/dred.py (rules R1-R6 of
certificates/P14_dred_rules.json: g4 = ghat + gtilde, tr ghat = d, tr gtilde = 4-d; l and p in QdS; exported l_r lifted as
l.e_(r); Gram/PV reduction with ghat projections; all contractions before the Laurent expansion with d symbolic;
evanescent remainders retained), MS-bar at scale mu, Feynman i0 on every propagator denominator.
quantum_prescription_defined requires dred_rules_verified.
The rules for scaleless integrals are PART of the definition, but they are NOT applied in p14: no tadpole (D02, D12,
D14a-c) is assigned a value, and D12 stays Missing.

D11 matching (defined, NOT verified):
  M0 baseline S_inv (not S_D): no switch/insertion fields; a1 = (1/2) tau eta - h equals XVI-O's vertex.
  M1 EXACT integrand identity (computed here): -i * [P's exported D11 integrand] == XVI-O's
       (i kappa^2/4) V V (C~C~ + C~C~) with C~_ab(k) = k_a k_b D~_F(k), D~_F = i/(k^2+i0), V = XVI-O's own V_tensor
       (imported from code/matter_loop/d11_tensor.py), mapped to P's independent lower components by the eta-raising map
       with orbit multiplicity; all 100 component pairs, as rational functions of (l, p) with the i0-denominators.
  M2 nonlocal agreement on U = R^4 \\ {0}: DEFINED only (needs the evaluated DR amplitude; p15).
  M3 (CONDITIONAL on M2) local difference L_match := FT[P^DR] - Pi_tr^R.  Scalar extension u^R_mu: scaling degree 4;
       kernel K u^R_mu: scaling degree at most eight; degree of divergence at most four; hence the local ambiguity has
       derivative order at most four (sd(d^alpha delta) = 4 + |alpha|).  IF M2 holds, L_match is supported at {0} and lies
       in the bounded contact space (orders 0, 2, 4; enumerated).  Exactly degree four is an EXPLICIT normalization
       condition N4 (mu^4 and mu^2 p^2 contacts excluded by N4, not by 'no other scale'); under N4 the space is the
       degree-4 hh span (computed: 5; transverse subspace computed: 2).
  M4 finite adjustments: P-side counterterms in the hh sector of P14_counterterm_domain; u^R_mu untouched (no c delta).
  M5 residue r = -i pi^2 is an XVI-O-side statement valid only after constructive holomorphy
       (lem:analytic_FP_u_mu_R_o70); P's 1/eps pole is P-side; no pole <-> residue identification is asserted.
  M6 provenance: XVI-O o70 files byte-pinned (tools/source_manifest.check_xvio_provenance).
  M7 the XVI-O kernel Ward identity is NOT functional ST4b; projected != bulk.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "code" / "classical"))
sys.path.insert(0, str(ROOT / "code" / "matter_loop"))
sys.path.insert(0, str(ROOT / "tools"))
import feynman as F  # noqa: E402
import amplitude_rules as A  # noqa: E402
import counterterm_domain as CT  # noqa: E402
import p14_conventions as PC  # noqa: E402
import certio  # noqa: E402
import d11_tensor as O  # noqa: E402   (XVI-O frozen code; imported, not edited)

I = sp.I
ETA = sp.diag(1, -1, -1, -1)

PRESCRIPTION = {
    "id": "P14_DRED_MSbar_FeynmanI0",
    "regularization": "dimensional reduction (DRED), operational rules R1-R6 (certificates/P14_dred_rules.json, "
                      "code/p5_entry/dred.py): quasi-4D metric g4 = ghat + gtilde, tr g4 = 4, tr ghat = d, "
                      "tr gtilde = 4 - d; loop momentum l and external momenta p in the d-dimensional space QdS "
                      "(p.gtilde = 0); field/vertex/polarisation indices quasi-4D; int d^d l/(2 pi)^d with mu^{2 eps}",
    "lifting": "exported numerators are polynomials in lower components l_r, p_r at fixed external indices; l_r := "
               "l.e_(r) (e_(r) the eta-orthonormal basis of Q4S), p_r = p.e_(r); vertex tensors lifted with eta -> g4",
    "subtraction": "MS-bar: subtract the pole in the combination 1/eps - gamma_E + log 4 pi; scale mu",
    "i0": "Feynman: every propagator denominator q^2 + i0 (eta = +,-,-,-); Wick rotation l0 = i l4 implied",
    "tensor_reduction": "Gram/Passarino-Veltman projection on symmetric ghat/p tensors with symbolic d; free quasi-4D "
                        "indices are projected with ghat_rs = eta_rs - Gt_rs (Gt_rs evanescent, eta^{rs} Gt_rs = 4-d, "
                        "Gt_rs p^s = 0)",
    "order_of_operations": "ALL index contractions (incl. the external 4D projection) BEFORE the Laurent expansion; d "
                           "symbolic through MS-bar subtraction and finite-part extraction; (d-4) x pole terms retained; "
                           "premature d = 4 is detected (PrematureD4Substitution)",
    "evanescent": "evanescent remainders DO arise (Gt structures in every exported graph; (4-d) x pole finite terms after "
                  "contraction); they are retained, never dropped (the p14 'none arise' statement is withdrawn)",
    "literature_background_only": "Siegel PLB 84 (1979) 193, PLB 94 (1980) 37; Stockinger hep-ph/0503129; "
                                  "Signer-Stockinger arXiv:0807.4424",
    "scaleless_integrals": "PART of the definition (DR value of a scaleless massless integral) but NOT APPLIED in p14: "
                           "no tadpole value is assigned; D12 stays Missing; never replaced by zero",
    "massless": True, "IR": "no IR regulator needed at the integrand level; IR/UV separation of scaleless integrals is "
                            "deferred together with their evaluation (p15+)",
    "applies_to": ["D01", "D02", "D03", "D11 (P side, matching only)", "D12", "D13", "D14a", "D14b", "D14c"],
    "consistency_with_XVI_O": "XVI-O fixes D12/one-point by dimensional_regularization_m0 (coincident prescription); "
                              "P's DR is the same family; P does NOT import XVI-O's prescription VALUE 0 (D12 Missing). "
                              "XVI-O's D11 extension is analytic FP in position space (NOT momentum MS); the two are "
                              "related only through matching (M2-M4), not identified.",
}


def raise_map(A_):
    """d h^{mu nu}/d h_(A): orbit multiplicity (both orderings for off-diagonal independent components)."""
    m, n = A_
    R = sp.zeros(4, 4)
    R[m, n] += ETA[m, m] * ETA[n, n]
    if m != n:
        R[n, m] += ETA[m, m] * ETA[n, n]
    return R


def M1_identity():
    t0 = time.time()
    ints = A.build_integrands(A.base_rules())
    r = ints["D11"]
    body, sha = A.integrand_record("D11", r)
    exp_f = ROOT / "exports" / "P14_integrands" / "D11.json"
    exported_sha = json.loads(exp_f.read_text())["sha256"] if exp_f.is_file() else None
    l = sp.symbols("l0:4")
    p = sp.symbols("p0:4")
    D1, D2 = sp.symbols("D1 D2")           # l^2 + i0, (l-p)^2 + i0  (P's recorded denominators)
    kap = F.KAPPA
    names = list(l) + list(p)
    q = [l[a] - p[a] for a in range(4)]
    Ct = lambda k, a, b, D: k[a] * k[b] * I / D  # noqa: E731   C~_ab(k) = k_a k_b D~_F(k)
    # XVI-O kernel in momentum space: Pi~_{mu nu rho sigma} = (i k^2/4) V^{ab}_{mu nu} V^{cd}_{rho sigma}
    #   [C~_ac(l) C~_bd(q) + C~_ad(l) C~_bc(q)]   (FT of C(z)C(z) = convolution; C~ even)
    V = {(mu, nu, a, b): O.V_tensor(mu, nu, a, b, ETA) for mu in range(4) for nu in range(4)
         for a in range(4) for b in range(4)}
    G = {}
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    G[(a, b, c, d)] = sp.expand(Ct(l, a, c, D1) * Ct(q, b, d, D2) + Ct(l, a, d, D1) * Ct(q, b, c, D2))
    Vh = {}
    for Aidx, Acomp in enumerate(F.HC):
        R = raise_map(Acomp)
        Vh[Aidx] = {(a, b): sp.expand(sum(R[mu, nu] * V[(mu, nu, a, b)] for mu in range(4) for nu in range(4)))
                    for a in range(4) for b in range(4)}
    bad, checked, nonzero = [], 0, 0
    pref = r["prefactor"]
    for Aidx in range(10):
        for Bidx in range(10):
            O_ = sum(Vh[Aidx][(a, b)] * Vh[Bidx][(c, d)] * G[(a, b, c, d)]
                     for a in range(4) for b in range(4) for c in range(4) for d in range(4)
                     if Vh[Aidx][(a, b)] != 0 and Vh[Bidx][(c, d)] != 0)
            O_ = sp.expand(I * kap ** 2 / 4 * O_)
            Np = r["N"].get((Aidx, Bidx))
            Ps = Np.to_sympy(names) if Np is not None else sp.Integer(0)
            P_ = sp.expand(-I * pref * Ps / (D1 * D2))
            checked += 1
            nonzero += O_ != 0
            if sp.expand(P_ - O_) != 0:
                bad.append([str(F.HC[Aidx]), str(F.HC[Bidx])])
    return {"identity": "-i * prefactor_P * N^P_{AB}(l,p)/(D1 D2)  ==  (i kappa^2/4) R_A R_B V V [C~(l)C~(l-p) + "
                        "C~(l)C~(l-p)]_{AB}",
            "D1": "l^2 + i0", "D2": "(l-p)^2 + i0", "P_prefactor": str(pref), "P_routing": r["routing"],
            "XVI_O_V_tensor": "code/matter_loop/d11_tensor.py::V_tensor (frozen, imported)",
            "XVI_O_prefactor": "i kappa^2/4 (O5_Gate2_normalized_D11)",
            "C_tilde": "C~_ab(k) = k_a k_b * i/(k^2+i0)  (FT of C = -d_a d_b D_F, d -> ik)",
            "raising_map": "h^{mu nu} = eta^{mu a} eta^{nu b} h_ab; d/dh_(ab) carries orbit multiplicity 2 for a != b",
            "normalisation": "Gamma_1^(2) = (1/2) int h^{mu nu} Pi_{mu nu rho sigma} h^{rho sigma} (XVI-O) <-> "
                             "Gamma_1^{AB} = d^2 Gamma_1/dh_A dh_B (P ordered extraction); i Gamma_1 = graph sum",
            "component_pairs_checked": checked, "nonzero_pairs": int(nonzero), "mismatches": bad,
            "recomputed_integrand_sha256": sha, "exported_integrand_sha256": exported_sha,
            "bound_to_export": exported_sha == sha if exported_sha else None,
            "pass": bool(not bad and checked == 100 and nonzero > 0 and (exported_sha in (None, sha))),
            "seconds": round(time.time() - t0, 1)}


def M3_local_space(order=4):
    """degree-<order> local hh structures in XVI-O's convention (lower kernel indices; symmetric in mu<->nu, rho<->sigma,
    (mu nu)<->(rho sigma)) and their transverse subspace (p^mu T_{mu nu rho sigma} = 0)."""
    p = sp.symbols("p0:4")
    slots = [(0, "U"), (1, "U"), (2, "U"), (3, "U")]   # field h^{mu nu} upper => kernel indices lower (p_a, eta_ab)
    S = CT.structures(slots, order)
    perms = [(0, 1, 2, 3), (1, 0, 2, 3), (0, 1, 3, 2), (1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 0, 1), (2, 3, 1, 0), (3, 2, 1, 0)]
    comps = [c for c in __import__("itertools").product(range(4), repeat=4)]
    mons = None
    rows = []
    for T in S:
        sym = {}
        for c in comps:
            sym[c] = sp.expand(sum(T.get(tuple(c[i] for i in pm), 0) for pm in perms) * sp.Rational(1, 8))
        rows.append(sym)
    # rank of the symmetrised structures
    def vec(sym):
        out = {}
        for c, v in sym.items():
            if v != 0:
                for mon, cf in sp.Poly(v, *p).terms():
                    out[(c, mon)] = cf
        return out
    from fractions import Fraction as Fr
    vecs = [{k: Fr(int(v.p), int(v.q)) for k, v in vec(s).items()} for s in rows]
    keep, kv = [], []
    for s, v in zip(rows, vecs):
        if CT.rank(kv + [v]) > len(kv):
            kv.append(v)
            keep.append(s)
    dim = len(keep)
    # transversality: sum_mu p^mu T_{mu nu rho sigma} = 0 for the general combination
    x = sp.symbols(f"x0:{dim}")
    eqs = []
    for nu in range(4):
        for rho in range(4):
            for sg in range(4):
                e = sp.expand(sum(x[i] * sum(ETA[mu, mu] * p[mu] * keep[i][(mu, nu, rho, sg)] for mu in range(4))
                                  for i in range(dim)))
                if e != 0:
                    eqs += [cf for _, cf in sp.Poly(e, *p).terms()]
    M = sp.Matrix([[sp.diff(e, xi) for xi in x] for e in eqs]) if eqs else sp.zeros(0, dim)
    tdim = dim - M.rank()
    return {"order": order, "dimension": dim, "transverse_subspace_dimension": int(tdim),
            "matches_counterterm_hh_sector": None}


M3_WORDING = ("Kernel scaling degree at most eight; degree of divergence at most four; hence the local ambiguity has "
              "derivative order at most four.")
N4 = ("normalization condition N4 (EXPLICIT, imposed): L_match is homogeneous of degree exactly four in p, i.e. it "
      "contains no mu^4 (order-0) and no mu^2 p^2 (order-2) contact terms.  This is NOT implied by 'no other scale': "
      "mu itself is a scale, so mu^{4-|alpha|} d^alpha delta with |alpha| = 0, 2 are dimensionally allowed")


def M3_contact_analysis(glob, ext):
    """corrected M3: scaling-degree labels from the XVI-O certificates, the conditional statement, and the explicit
    enumeration of the bounded contact space (orders 0, 2, 4; odd orders impossible with 4 indices from p and eta)."""
    sd_u = ext["u_mu_R"]["sd_max"]
    kk = glob["Pi_tr"]["scaling_degree_K_uR"]
    sd_k = kk["sd_bound"]
    labels = {"scalar_extension_scaling_degree": sd_u, "kernel_differential_order": kk["differential_order_K"],
              "kernel_scaling_degree_bound": sd_k, "degree_of_divergence_bound": sd_k - 4,
              "local_contact_derivative_order_bound": sd_k - 4,
              "contact_scaling_degree_rule": "sd(d^alpha delta) = 4 + |alpha|  (in 4 dimensions)",
              "labels_consistent": bool(sd_u == 4 and sd_k == 8 and sd_u + kk["differential_order_K"] == sd_k)}
    orders = {o: M3_local_space(o) for o in (0, 2, 4)}
    return {
        "labels": labels, "wording": M3_WORDING,
        "conditional_on": "M2_nonlocal_agreement_on_U (defined, NOT verified)",
        "conditional_statement": "IF M2 holds, then L_match vanishes on U = R^4 \\ {0}, hence is supported at {0}; "
                                 "with kernel scaling degree <= 8 it is a finite sum of d^alpha delta with "
                                 "4 + |alpha| <= 8, i.e. it lies in the bounded contact space of derivative order <= 4",
        "bounded_contact_space": {f"order_{o}": {"mu_power": 4 - o, "dimension": r["dimension"],
                                                 "transverse_subspace_dimension": r["transverse_subspace_dimension"]}
                                  for o, r in orders.items()},
        "odd_orders": "absent: four tensor indices built from p and eta need an even number of p's",
        "normalization_condition": N4,
        "lower_degree_contacts_excluded_by_N4": {f"order_{o}_mu{4 - o}": orders[o]["dimension"] for o in (0, 2)},
        "under_N4": "L_match lies in the order-4 (degree-4) hh span", "_order4": orders[4]}


def main():
    t0 = time.time()
    cert = lambda n: json.loads((ROOT / "certificates" / f"{n}.json").read_text())  # noqa: E731
    g2 = cert("O5_Gate2_normalized_D11")
    ext = cert("O5_D11_scalar_extension")
    glob = cert("O5_D11_global_representation")
    g4 = cert("O5_Gate4_Ward_D12_onepoint")
    ten = cert("O5_D11_tensor")
    ww = cert("O5_D11_Ww_reference")
    ctd_f = ROOT / "certificates" / f"{PC.CERT_PREFIX}_counterterm_domain.json"
    ctd = json.loads(ctd_f.read_text()) if ctd_f.is_file() else None
    qo_f = ROOT / "certificates" / f"{PC.CERT_PREFIX}_quantum_object.json"
    qo = json.loads(qo_f.read_text()) if qo_f.is_file() else None
    import source_manifest as SM
    prov = SM.check_xvio_provenance(ROOT)
    # ---- prescription checks
    P = F.propagators()
    pc = {"propagators_are_verified_Hessian_inverses": bool(P["graviton"]["full_h_b_inverse_verified"]
                                                            and P["ghost"]["M0_is_q2_times_constant"]),
          "scalar_i0_matches_Gate0": g2["D_F"] == "i/(k^2+i0)",
          "XVI_O_coincident_prescription_is_DR_m0": (g4["D12"]["coincident_prescription"] == "dimensional_regularization_m0"
                                                     and g4["one_point"]["prescription"] == "dimensional_regularization_m0"),
          "XVI_O_D11_is_NOT_momentum_MS": ext["NOT_momentum_MS"] is True,
          "no_value_imported_D12": True,
          "quantum_object_defined": bool(qo and qo.get("quantum_action_defined"))}
    dr_f = ROOT / "certificates" / f"{PC.CERT_PREFIX}_dred_rules.json"
    dr = json.loads(dr_f.read_text()) if dr_f.is_file() else None
    pc["operational_DRED_rules_verified"] = bool(dr and dr.get("dred_rules_verified") is True
                                                 and dr.get("mutations_all_rejected") is True)
    pc["evanescent_remainders_retained"] = bool(dr and dr.get("evanescent_parts_present_in_exports") is True)
    power = {}
    amp_f = ROOT / "certificates" / f"{PC.CERT_PREFIX}_amplitude_rules.json"
    amp = json.loads(amp_f.read_text()) if amp_f.is_file() else None
    if amp:
        for g, rec in amp["graphs"].items():
            nden = len(rec["denominators"])
            deg = rec["numerator_degree"]
            power[g] = {"denominators": rec["denominators"], "numerator_degree": deg,
                        "superficial_degree": 4 + deg - 2 * nden,
                        "all_feynman_i0": all(d.endswith("+i0") for d in rec["denominators"])}
    pc["all_denominators_feynman_i0"] = bool(power) and all(v["all_feynman_i0"] for v in power.values())
    prescription_ok = all(v is True for v in pc.values())
    # ---- D11 matching
    m0 = {"baseline": "S_inv (XVI-N invariant extended action), NOT S_D",
          "no_switch_fields": bool(qo and qo["Q1_transformed_variables"]["no_switch_or_insertion_fields"]),
          "a1_vertex_XVI_O": g2["vertex_tensor"]["from"], "a1_P": "a1 = (1/2) tau eta - h (scalar_B_series, XI-A)",
          "NOT_S_D_P13": json.loads((ROOT / "certificates" / "P13_gauge_fixing_map.json").read_text())[
              "invariant_vs_transformed_kept_separate"]["NOT_S_D"]}
    m0["pass"] = bool(m0["no_switch_fields"] and m0["NOT_S_D_P13"] and g2["vertex_tensor"]["from"] == "a1 = (1/2) tau eta - h")
    m1 = M1_identity()
    m3c = M3_contact_analysis(glob, ext)
    o4 = m3c.pop("_order4")
    m3 = {**m3c, "dimension": o4["dimension"], "transverse_subspace_dimension": o4["transverse_subspace_dimension"],
          "matches_counterterm_hh_sector": None}
    if ctd:
        m3["matches_counterterm_hh_sector"] = ctd["kappa2"]["basis_size_by_sector"].get("h.h") == m3["dimension"]
    ans = g4["contact_ansatz"]["basis"]
    m3["XVI_O_contact_ansatz_ids"] = [b["id"] for b in ans]
    m3["XVI_O_order4_elements"] = sum(1 for b in ans if b["order"] == 4)
    m3["XVI_O_ansatz_NOT_proved_spanning"] = g4["contact_ansatz"].get("NOT_proved_spanning")
    m3["comparison_with_XVI_O_ansatz"] = (
        "XVI-O's contact ansatz is a candidate list (NOT_proved_spanning) with 3 named order-4 entries, one of them "
        "the collective 'L4_mixed'; P enumerates the order-4 space explicitly: 5 structures (transverse subspace 2). "
        "No contradiction; P's list is the explicit one used for M3/M4")
    m3["XVI_O_order_lt_4_elements_excluded_by_N4"] = [b["id"] for b in ans if b["order"] < 4]
    m3["pass"] = bool(m3["dimension"] == 5 and m3["matches_counterterm_hh_sector"] is True
                      and m3["labels"]["labels_consistent"]
                      and all(v["dimension"] > 0 for v in m3["bounded_contact_space"].values()))
    matching = {
        "baseline_M0": m0,
        "lemmas_referenced": {
            "lem:d11-prefactor": {"XVI_O": "Pi = (i kappa^2/4) T", "status": g2["status_prefactor"], "pass": g2["pass"],
                                  "used_in": "M1 (prefactor i kappa^2/4 imported, compared exactly)"},
            "lem:analytic_FP_u_mu_R_o70": {"prescription_id": ext["prescription_id"], "pass": ext["pass"],
                                           "u_mu_R": ext["u_mu_R"], "used_in": "M2/M5 (XVI-O side only)"},
            "lem:BV_rules_on_U": {"status": glob["lem_BV_rules_on_U"]["status"], "pass": glob["lem_BV_rules_on_U"]["pass"],
                                  "all_256_symbolic": glob["all_256_symbolic"]["pass"],
                                  "alpha": glob["coefficients"]["alpha"], "beta": glob["coefficients"]["beta"],
                                  "used_in": "M2 (XVI-O's Pi_tr^R on U is the matching target)"}},
        "M1_integrand_identity": m1,
        "M2_nonlocal_agreement_on_U": {
            "definition": "for all test functions f in D(U), U = R^4 \\ {0}: <FT^{-1}[P^DR_{AB}](z), f> = "
                          "<R_A R_B Pi_tr^R(z), f>, Pi_tr^R = (i kappa^2/4) K u^R_mu (alpha = A^2/60, beta = A^2/18, "
                          "A = 1/(4 pi^2)); mu-independent on U",
            "status": "defined_not_verified", "requires": "evaluated DR D11 amplitude (Batch, p15+)",
            "integrand_level_evidence": "M1 (exact integrand identity) -- not a proof of M2"},
        "M3_local_difference": {"definition": "L_match := FT^{-1}[P^DR_{AB}] - R_A R_B Pi_tr^R, a distribution "
                                              "supported at z = 0 IF M2 holds", **m3,
                                "status": "conditional on M2; space enumerated; degree 4 imposed by N4; L_match not computed"},
        "M4_finite_adjustments": {
            "rule": "under M2 and N4, L_match (and any finite renormalization) is booked ONLY as P-side counterterms "
                    "in the hh sector of P14_counterterm_domain (5 elements; transverse subspace 2 if the P amplitude "
                    "is transverse); u^R_mu is NOT modified; without N4 the order-0/2 contacts (mu^4, mu^2 p^2) would "
                    "have to be added to that sector",
            "u_R_extra_c_delta_XVI_O": ext["u_mu_R"]["extra_c_delta"], "u_R_c_delta_added_by_P": False,
            "scalar_extension_prescription_preserved": ext["prescription_id"] == "analytic_FP_u_mu_R_o70",
            "XVI_O_D11_kernel_counterterm": g4["D11_kernel_counterterm"]},
        "M5_residue": {"r": ext["minkowski_residue"]["r_with_sign_and_i"],
                       "derived_from": ext["minkowski_residue"]["r_derived_from"],
                       "holomorphy_proof_pass": ext["phi_m1_holomorphy_proof"]["pass"],
                       "statement": "r = -i pi^2 is XVI-O-side, valid only AFTER constructive holomorphy of "
                                    "F(zeta) = (Q-i0)^zeta; P's MS-bar 1/eps pole is P-side; no identification of the "
                                    "P pole with r is asserted in p14"},
        "M6_provenance": {"files": len(prov), "all_pinned_ok": all(v["ok"] for v in prov.values()),
                          "pins": {k: v["pin"] for k, v in prov.items() if "d11" in k or k.endswith(".tex")}},
        "M7_projected_vs_bulk": {"XVI_O_kernel_Ward_NOT_functional_ST4b":
                                 g4["Ward_and_CT"]["kernel_two_point_Ward"]["NOT_functional_ST4b"],
                                 "symmetry_restored_bulk_XVI_O": g4["symmetry_restored_bulk"],
                                 "statement": PC.PROJECTED_VS_BULK},
        "conventions": {"XVI_O_index_convention": ten["index_convention"], "XVI_O_Pi": ten["Pi"],
                        "P_components": "independent lower h_(mn), m<=n", "map": m1["raising_map"],
                        "W_w_reference_id": ww["prescription_id"]},
    }
    prov_ok = bool(prov) and all(v["ok"] for v in prov.values())
    D11_defined = bool(m0["pass"] and m1["pass"] and m3["pass"] and prov_ok and g2["pass"] and ext["pass"]
                       and glob["pass"] and g4["Ward_and_CT"]["kernel_two_point_Ward"]["NOT_functional_ST4b"]
                       and ext["u_mu_R"]["extra_c_delta"] is False)
    rec = {"landmark": "XVI-P", "revision": PC.REVISION,
           "deliverable": "P.5 entry D2: quantum prescription and D11 matching note",
           "quantum_prescription_defined": prescription_ok, "D11_matching_defined": D11_defined,
           "D11_matching_verified": False,
           "D11_matching_verified_reason": "M2 (nonlocal agreement on U) and L_match require the evaluated DR D11 "
                                           "amplitude (p15+); only M0, M1, M3-space, M4-M7 are established",
           "prescription": PRESCRIPTION, "prescription_checks": pc, "power_counting": power,
           "D12_status": "Missing", "D12_value_imported": False,
           "matching": matching, "loop_evaluations_performed": False, "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{PC.CERT_PREFIX}_prescription_D11_matching.json", rec)
    print(json.dumps({"quantum_prescription_defined": prescription_ok, "D11_matching_defined": D11_defined,
                      "M1": {k: m1[k] for k in ("component_pairs_checked", "nonzero_pairs", "mismatches", "bound_to_export",
                                                "pass", "seconds")},
                      "M3": {k: m3[k] for k in ("labels", "bounded_contact_space", "dimension",
                                                "transverse_subspace_dimension", "XVI_O_order4_elements",
                                                "matches_counterterm_hh_sector", "pass")},
                      "prov_ok": prov_ok, "checks": pc, "seconds": rec["seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
