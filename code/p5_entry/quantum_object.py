#!/usr/bin/env python3
"""XVI-P p14 Deliverable 1: the quantum object, computed directly in TRANSFORMED variables.

  S_Psi(Phi, Phi*') = sum_k kappa^{k-2} ell_k + S_phi + X(Phi, Phi*' + eps dPsi/dPhi),  eps = -1 (derived, P13 gate)
  Gamma_Psi = S_Psi + hbar Gamma_1 + O(hbar^2);  Gamma_1 = -i log Z_1PI;  i Gamma_1 = sum of 1PI one-loop graphs.

Mechanical content (all recomputed here): term patterns of X by kappa order; integrated fields vs external
antifields; the b decision (retained & integrated) incl. the explicit elimination computation; source spectators of
Gamma_1; kappa bookkeeping (every vertex kappa^{legs-2}; per graph sum(n_v - 2) = E = kappa power of the integrand);
Fourier/propagator/i0 from the verified Hessian inverses; the classical pullback kept separate from any quantum
gauge-change theorem.  No loop is evaluated.
"""
from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "code" / "classical"))
import feynman as F  # noqa: E402
import p14_conventions as PC  # noqa: E402
import counterterm_domain as CT  # noqa: E402
import certio  # noqa: E402
from graded_jets import _KEY  # noqa: E402

FIELDS = ("h", "c", "cb", "b", "phi")
ANTIFIELDS = ("K", "cs", "cbs", "bs", "phis")
GRAPH_VERTICES = {"D01": ["V3_grav", "V3_grav"], "D02": ["V4_grav"], "D03": ["V_cb_c_h", "V_cb_c_h"],
                  "D11": ["V_h_phi_phi", "V_h_phi_phi"], "D12": ["V_hh_phi_phi"], "D13": ["V_K_c_h", "V_cb_c_h"],
                  "D14a": ["V3_grav"], "D14b": ["V_cb_c_h"], "D14c": ["V_h_phi_phi"]}
GRAPH_EXTERNAL = {"D01": 2, "D02": 2, "D03": 2, "D11": 2, "D12": 2, "D13": 2, "D14a": 1, "D14b": 1, "D14c": 1}


def patterns(G):
    """species multiset of every monomial of a GE density (odd keys + even jet symbols)."""
    out = set()
    for key, val in G.t.items():
        odd = [k[0] for k in key]
        for t in sp.Add.make_args(sp.expand(val)):
            ev = []
            for s, e in t.as_powers_dict().items():
                if s in _KEY:
                    ev += [_KEY[s][0]] * int(e)
            out.add(".".join(sorted(odd + ev, key=lambda f: (FIELDS + ANTIFIELDS).index(f))))
    return sorted(out)


def b_elimination(X0):
    """solve E_b(X^(0)) = 0 algebraically (b enters undifferentiated) and substitute."""
    v = sp.expand(X0.t.get((), 0))
    bsyms = [s for s in v.free_symbols if s in _KEY and _KEY[s][0] == "b"]
    assert all(_KEY[s][2] == () for s in bsyms), "b differentiated: elimination not algebraic"
    bsyms = sorted(bsyms, key=lambda s: _KEY[s][1])
    sol = sp.solve([sp.diff(v, s) for s in bsyms], bsyms, dict=True)
    assert len(sol) == 1
    red = sp.expand(v.xreplace(sol[0]))
    cbs = [s for s in red.free_symbols if s in _KEY and _KEY[s][0] == "cbs"]
    quad = [t for t in sp.Add.make_args(red) if sum(sp.degree(t, s) for s in cbs) == 2]
    lin_h = [t for t in sp.Add.make_args(red) if sum(sp.degree(t, s) for s in cbs) == 1]
    hess = sp.hessian(v, bsyms)
    return {"b_components": [str(s) for s in bsyms], "b_hessian_constant": all(x.free_symbols == set() for x in hess),
            "b_hessian_det": str(hess.det()), "solution_b0": str(sol[0][bsyms[0]])[:160],
            "after_elimination_terms": len(sp.Add.make_args(red)),
            "cbar_star_quadratic_terms": len(quad), "cbar_star_linear_terms": len(lin_h),
            "quadratic_example": str(quad[0]) if quad else None,
            "reading": "eliminating b makes S_Psi QUADRATIC in cbar*' (and shifts the cbar*'-linear terms into "
                       "h-dependent ones); retaining b keeps S_Psi linear in all external antifields"}


def main():
    t0 = time.time()
    P = F.S_psi_parts()
    X, Ph = P["X"], P["phi"]
    pats = {n: patterns(X[n]) for n in (0, 1, 2)}
    phipats = {n: patterns(Ph[n]) for n in (0, 1, 2)}
    gf = json.loads((ROOT / "certificates" / "P13_gauge_fixing_map.json").read_text())
    sa = json.loads((ROOT / "certificates" / "P13_source_action.json").read_text())
    amp_f = ROOT / "certificates" / f"{PC.CERT_PREFIX}_amplitude_rules.json"
    amp = json.loads(amp_f.read_text()) if amp_f.is_file() else None
    conv = (ROOT / "notes" / "quantum_convention_sheet.tex").read_text()
    # -------- Q1 transformed variables
    Q1 = {"eps_derived": P["eps"], "gauge_fixing_cert_eps": gf["derived_eps"],
          "S_Psi_equals_S_plus_sPsi_mod_d": gf["S_Psi_equals_S_plus_sPsi_mod_d"],
          "NOT_S_D": gf["invariant_vs_transformed_kept_separate"]["NOT_S_D"],
          "Psi": gf["Psi"],
          "X_patterns_by_kappa": pats, "S_phi_patterns_by_kappa": phipats,
          "X_terms_by_kappa_P13": sa["X_terms_by_kappa_order"],
          "no_switch_or_insertion_fields": not any(f in p for n in pats for p in pats[n] for f in ("lam", "mu", "z"))}
    Q1["ok"] = bool(Q1["eps_derived"] == -1 == Q1["gauge_fixing_cert_eps"] and Q1["S_Psi_equals_S_plus_sPsi_mod_d"]
                    and Q1["NOT_S_D"] and Q1["no_switch_or_insertion_fields"] and not pats[2])
    # -------- Q2 integrated fields vs external antifields
    lc, used = CT.loop_capable_species()
    b_orders = [n for n in (0, 1, 2) if any("b" in p.split(".") for p in pats[n])]
    b_pats = [p for p in pats[0] if "b" in p.split(".")]
    elim = b_elimination(X[0])
    Pr = F.propagators()
    Q2 = {"integrated": ["h_(mn) (10 independent components)", "c^mu", "cbar_mu", "phi", "b^mu (retained)"],
          "external_antifields": {"K'_(mn)": "h*' (10 comps, sigma_h = +1)", "c*'_mu": "c*'", "cbar*'^mu": "cbar*'",
                                  "phi*'": "phi*'", "b*'": "absent (s b = 0)"},
          "external_antifields_retained_P13": gf["external_antifields_retained"],
          "b_decision": "RETAINED and integrated",
          "b_justification": {
              "b_occurs_only_at_kappa_orders": b_orders, "b_patterns": b_pats,
              "no_b_interaction_vertex": b_orders == [0] and all(len(p.split(".")) == 2 for p in b_pats),
              "Mbb_constant_invertible": elim["b_hessian_constant"] and elim["b_hessian_det"] not in ("0",),
              "full_h_b_inverse_verified": Pr["graviton"]["full_h_b_inverse_verified"],
              "schur_complement_equals_q2_P": Pr["graviton"]["schur_equals_q2P"],
              "elimination": elim},
          "loop_capable_species": sorted(lc),
          "Gamma1_independent_of": sorted(set(ANTIFIELDS) - lc),
          "source_spectators": "cbar*' couples only via cbar*'.b (one quantum leg; tree, one-particle reducible "
                               "through the b-h mixing) and b*' is absent => Gamma_1 (1PI) is independent of cbar*', "
                               "b*'; K', c*', phi*' enter Gamma_1 through K'.c.h, c*'.c.c, phi*'.c.phi"}
    Q2["ok"] = bool(Q2["b_justification"]["no_b_interaction_vertex"] and Q2["b_justification"]["Mbb_constant_invertible"]
                    and Q2["b_justification"]["full_h_b_inverse_verified"] and elim["cbar_star_quadratic_terms"] > 0
                    and set(Q2["Gamma1_independent_of"]) == {"bs", "cbs"} and {"K", "cs", "phis"} <= lc)
    # -------- Q3 1PI / Gamma_1, vacuum and one-point normalization
    W1 = (amp or {}).get("controls", {}).get("W1_wick_berezin_shadow", {})
    Q3 = {"weight": "e^{i S_Psi/hbar}", "Gamma": "Gamma_Psi[Phi, Phi*'] = S_Psi + hbar Gamma_1 + O(hbar^2); Legendre "
          "transform in the fields Phi = (h, c, cbar, b, phi) only; antifields Phi*' are spectators (not transformed)",
          "Gamma1": "Gamma_1 = (i/2) STr log S_Psi^{(2)} (fields only) = -i log Z|_1PI; i Gamma_1 = sum of 1PI one-loop "
                    "graphs (graph i's from vertices i kappa^n V and propagators i M^{-1})",
          "gate0_consistency": {"Gamma_1 = -i log Z in convention sheet": "Gamma_{1,\\mathrm{matter}}=-i\\log Z" in conv,
                                "e^{iS/hbar} in convention sheet": "$e^{iS/\\hbar}$" in conv,
                                "W1 Berezin/Wick shadow pass": W1.get("pass")},
          "vacuum_normalization": "Z normalised so that Gamma_1[0] = 0 (field-independent vacuum graphs dropped)",
          "one_point_normalization": "the one-point function Gamma_1^{(1)} (graphs D14a, D14b, D14c) is RETAINED as "
                                     "part of the object: no tadpole-cancellation condition and no background shift "
                                     "imposed; its value is not assigned here (no zero is substituted)",
          "background": "fields of Gamma are the classical (mean) fields; <h> is not shifted"}
    Q3["ok"] = bool(all(v is True for v in Q3["gate0_consistency"].values()))
    # -------- Q4 Fourier / propagators / i0
    Q4 = {"fourier": "f(x) = int d^4k/(2pi)^4 e^{ikx} f~(k), d_mu -> i k_mu, incoming momenta (Gate 0: d -> ik)",
          "eta": "diag(+,-,-,-)",
          "graviton": "<h_a h_b>(q) = i (P^{-1})_{ab} / (q^2 + i0)  (independent components; de Donder)",
          "ghost": "<c^mu(q) cbar_rho(-q)> = i (M0^{-1})_{mu rho} = -delta_{mu rho}/(q^2 + i0), M0 = -i q^2 delta",
          "scalar": "<phi phi>(q) = i/(q^2 + i0)",
          "b": "b retained: mixed (h,b) inverse verified; b-lines never enter a loop (no b vertex)",
          "i0": "Feynman: every propagator denominator q^2 + i0 (D_F = i/(k^2+i0), Gate 0)",
          "checks": {"Pinv_equals_deDonder": Pr["graviton"]["Pinv_equals_deDonder_tensor_at_representatives"],
                     "schur_q2P": Pr["graviton"]["schur_equals_q2P"],
                     "full_h_b_inverse": Pr["graviton"]["full_h_b_inverse_verified"],
                     "ghost_M0_q2_const": Pr["ghost"]["M0_is_q2_times_constant"],
                     "D_F convention sheet": "D_F(k)=i/(k^2+i0)" in conv,
                     "d -> ik convention sheet": "\\partial_\\mu\\to ik_\\mu" in conv,
                     "propagators_match_transformed_Hessians_P13": gf["propagators_match_transformed_Hessians"]}}
    Q4["ok"] = bool(all(v is True for v in Q4["checks"].values()))
    # -------- Q5 coupling / loop bookkeeping
    V = F.vertices()
    vk = {nm: {"legs": len(vt.legs), "kappa_power": vt.kappa_power,
               "kappa_eq_legs_minus_2": vt.kappa_power == len(vt.legs) - 2} for nm, vt in V.items()}
    gk = {}
    for g, vs in GRAPH_VERTICES.items():
        s = sum(V[v].kappa_power for v in vs)
        pref = (amp or {}).get("graphs", {}).get(g, {}).get("prefactor")
        m = re.search(r"kappa\*\*(\d+)", pref or "")
        kp = int(m.group(1)) if m else (1 if pref and "kappa" in pref else None)
        gk[g] = {"vertices": vs, "sum_n_minus_2": s, "external_legs": GRAPH_EXTERNAL[g], "integrand_prefactor": pref,
                 "integrand_kappa_power": kp, "ok": s == GRAPH_EXTERNAL[g] and (kp is None or kp == s)}
    Q5 = {"rule": "S_Psi = sum_n kappa^n S^(n); each vertex with n legs is O(kappa^{n-2}); one loop: Gamma_1 at kappa^k "
                  "has exactly k external legs (sum over vertices of (n_v - 2) = E); hbar counts loops (one loop = hbar^1)",
          "orders": "P.5 scope: one loop, kappa^1 (one-point) and kappa^2 (two-point incl. K'c)",
          "vertices": vk, "graphs": gk, "amplitude_cert_present": amp is not None}
    Q5["ok"] = bool(all(v["kappa_eq_legs_minus_2"] for v in vk.values()) and all(v["ok"] for v in gk.values())
                    and amp is not None and all(v["integrand_kappa_power"] is not None for v in gk.values()))
    # -------- Q6 classical pullback vs quantum theorem
    rel = gf["source_identity_relation"]
    Q6 = {"classical_pullback": rel["relation"], "classical_instance_verified": rel["classical_instance_verified"],
          "status_P13": rel["status"],
          "statement": "Gamma_Psi is DEFINED here directly in transformed variables. The relation Gamma_Psi(Phi,Phi*') = "
                       "Gamma(Phi, Phi*' - dPsi/dPhi) is used ONLY as the classical pullback (verified at tree level, "
                       "P13). No quantum gauge-(in)dependence theorem is asserted or used; any such statement is a "
                       "separate (p15+) object.",
          "quantum_gauge_change_theorem_asserted": False}
    Q6["ok"] = bool(rel["classical_instance_verified"] and "NOT an independently established quantum" in rel["status"])
    ok = all(q["ok"] for q in (Q1, Q2, Q3, Q4, Q5, Q6))
    rec = {"landmark": "XVI-P", "revision": PC.REVISION, "deliverable": "P.5 entry D1: quantum object",
           "quantum_action_defined": ok, "definition": "Q1..Q6 all ok",
           "S_Psi": "sum_k kappa^{k-2} ell_k + S_phi + X(Phi, Phi*' + eps dPsi/dPhi), eps = -1",
           "Q1_transformed_variables": Q1, "Q2_fields_antifields_b": Q2, "Q3_1PI_vacuum_onepoint": Q3,
           "Q4_fourier_propagators_i0": Q4, "Q5_kappa_loop_bookkeeping": Q5, "Q6_pullback_vs_theorem": Q6,
           "loop_evaluations_performed": False, "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{PC.CERT_PREFIX}_quantum_object.json", rec)
    print(json.dumps({"quantum_action_defined": ok, **{k: rec[k]["ok"] for k in rec if k.startswith("Q")},
                      "b_elim": {k: elim[k] for k in ("b_hessian_det", "cbar_star_quadratic_terms")},
                      "Gamma1_indep": Q2["Gamma1_independent_of"], "seconds": rec["seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
