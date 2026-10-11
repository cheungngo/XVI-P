#!/usr/bin/env python3
"""p11 (b) [unchanged since p10]: derive s = s0 + kappa s1 + kappa^2 s2 from the finite geometric transformati
  +> ons.

Finite data: g -> phi_t^* g (flow of xi), phi -> phi o flow;  infinitesimal L_xi.
Declared parametrisation g = eta + kappa h and ghost scaling xi = kappa a c (conventions.py).
Ghost law: ansatz s xi = lam xi.d xi; lam is SOLVED from s^2 g = 0 (not imported).
s2 per sector is READ OFF the exact kappa-expansion; it is a result, not a policy.
Control: the exponential parametrisation g = eta + kappa h + kappa^2/2 h eta h gives s2 != 0,
and dropping that s2 breaks s^2 = 0 at O(kappa^2) (mutation 'omitted s2').
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graded_jets import GE, D, s_apply, kappa_coeff, H_COMPS, ghost_number  # noqa: E402
from bv_model import (KAPPA, A, I, metric, lie_sym, xi_field, s_map, hc, cv,  # noqa: E402
                      ghost_ansatz)
import conventions as C  # noqa: E402
import certio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GH = {"h": 0, "c": 1, "cb": -1, "b": 0, "phi": 0, "K": -1, "cs": -2, "cbs": 0, "bs": -1, "phis": -1}


def kdeg(F):
    return max((sp.degree(sp.expand(v), KAPPA) for v in F.t.values()), default=-1)


def solve_ghost_law():
    lam = sp.Symbol("lam")
    s = s_map(lam=lam)
    eqs = set()
    for k in H_COMPS:
        for v in s_apply(s[("h", k)], s).t.values():
            eqs.add(sp.factor(v))
    for v in s_apply(s[("phi", ())], s).t.values():
        eqs.add(sp.factor(v))
    sols = None
    for e in eqs:
        r = set(sp.solve(sp.Eq(e, 0), lam)) if e.has(lam) else None
        if r is None:
            continue
        sols = r if sols is None else sols & r
    s2c = sum(len(s_apply(s[("c", mu)], s).t) for mu in range(4))
    return {"ansatz": "s xi^mu = lam xi^r d_r xi^mu",
            "condition": "s^2 h = 0 and s^2 phi = 0 for all jets",
            "lam_solutions": sorted(str(x) for x in (sols or [])),
            "n_independent_conditions": len(eqs),
            "s2_c_terms_any_lam": s2c,
            "s2_c_identically_zero_any_lam": s2c == 0,
            "derived_lam": 1 if sols == {1} else None}


def per_sector_expansion(s):
    out = {}
    for (f, c), img in s.items():
        if img.is_zero():
            orders = {k: 0 for k in range(4)}
        else:
            orders = {k: len(kappa_coeff(img, KAPPA, k).t) for k in range(4)}
        out.setdefault(f, {"terms_by_kappa_order": {}, "max_kappa_degree": -1})
        for k, n in orders.items():
            out[f]["terms_by_kappa_order"][k] = out[f]["terms_by_kappa_order"].get(k, 0) + n
        out[f]["max_kappa_degree"] = max(out[f]["max_kappa_degree"], kdeg(img))
    for f, d in out.items():
        d["s0_nonzero"] = d["terms_by_kappa_order"][0] > 0
        d["s1_nonzero"] = d["terms_by_kappa_order"][1] > 0
        d["s2_nonzero"] = d["terms_by_kappa_order"][2] > 0
        d["s3_nonzero"] = d["terms_by_kappa_order"][3] > 0
        d["s2"] = "nonzero" if d["s2_nonzero"] else "derived_zero"
    return out


def compare_to_xvin(s):
    """Regression: s0 h = a(d_m c_n + d_n c_m), s1 h = a L_c h, s c = kappa a c.dc (XVI-N)."""
    ok = True
    xi = [cv(r) for r in range(4)]
    hlow = [[hc(m, n) for n in range(4)] for m in range(4)]
    Lch = lie_sym(xi, hlow)
    for (m, n) in H_COMPS:
        img = s[("h", (m, n))]
        s0 = kappa_coeff(img, KAPPA, 0)
        R0 = (D(cv(n), m).scale(C.ETA[n]) + D(cv(m), n).scale(C.ETA[m])).scale(A)
        s1 = kappa_coeff(img, KAPPA, 1)
        ok &= (s0 - R0).is_zero() and (s1 - Lch[m][n].scale(A)).is_zero()
    for mu in range(4):
        ref = GE()
        for r in range(4):
            ref = ref + cv(r) * D(cv(mu), r)
        ok &= (s[("c", mu)] - ref.scale(KAPPA * A)).is_zero()
    return ok


def nilpotency(s, nmax=2):
    res = {}
    for (f, c), img in s.items():
        s2 = s_apply(img, s)
        res[f"{f}{c}"] = {k: len(kappa_coeff(s2, KAPPA, k).t) for k in range(nmax + 3)}
    allzero = all(all(v == 0 for v in d.values()) for d in res.values())
    return allzero, res


def exp2_control():
    """Nonlinear parametrisation control: derive s_k h (k<=2) from s g = L_xi g."""
    g = metric("exp2")
    Lg = lie_sym(xi_field(), g)
    sk = {}
    for k in range(3):
        cur = {}
        for (m, n) in H_COMPS:
            rhs = kappa_coeff(Lg[m][n], KAPPA, k + 1)
            if k >= 1:
                corr = GE()
                for r in range(4):
                    corr = corr + (sk[k - 1][(min(m, r), max(m, r))] * hc(r, n)
                                   + hc(m, r) * sk[k - 1][(min(r, n), max(r, n))]).scale(C.ETA[r])
                rhs = rhs - corr.scale(sp.Rational(1, 2))
            cur[(m, n)] = rhs
        sk[k] = cur
    s2_terms = sum(len(v.t) for v in sk[2].values())

    def smap(include_s2):
        s = {}
        for (m, n) in H_COMPS:
            img = sk[0][(m, n)] + sk[1][(m, n)].scale(KAPPA)
            if include_s2:
                img = img + sk[2][(m, n)].scale(KAPPA ** 2)
            s[("h", (m, n))] = img
        for mu, v in ghost_ansatz(1).items():
            s[("c", mu)] = v
        return s

    out = {}
    for inc in (True, False):
        s = smap(inc)
        bad = {}
        for (m, n) in [(0, 0), (0, 1), (1, 2)]:
            s2h = s_apply(s[("h", (m, n))], s)
            bad[f"h{m}{n}"] = {k: len(kappa_coeff(s2h, KAPPA, k).t) for k in range(3)}
        out["with_s2" if inc else "s2_omitted"] = {
            "s2h_terms_by_order_through_kappa2": bad,
            "nilpotent_through_kappa2": all(all(v == 0 for v in d.values()) for d in bad.values()),
        }
    return {"parametrisation": "g = eta + kappa h + kappa^2/2 h.eta.h (control only, NOT the declared one)",
            "s2_h_terms": s2_terms, "s2_h_nonzero": s2_terms > 0, **out}


def ghost_numbers(s):
    bad = []
    for (f, c), img in s.items():
        if img.is_zero():
            continue
        g = ghost_number(img, GH)
        if g != {GH[f] + 1}:
            bad.append((f, c, sorted(g)))
    return bad


def main():
    t0 = time.time()
    law = solve_ghost_law()
    s = s_map(lam=1)
    sectors = per_sector_expansion(s)
    nil_ok, nil = nilpotency(s)
    xvin = compare_to_xvin(s)
    ctrl = exp2_control()
    ghbad = ghost_numbers(s)
    s2_per_sector = {f: d["s2"] for f, d in sectors.items()}
    passed = bool(law["derived_lam"] == 1 and nil_ok and xvin and not ghbad
                  and all(v == "derived_zero" for v in s2_per_sector.values())
                  and ctrl["s2_h_nonzero"] and ctrl["with_s2"]["nilpotent_through_kappa2"]
                  and not ctrl["s2_omitted"]["nilpotent_through_kappa2"])
    cert = {
        "revision": C.REVISION, "gate": "P13_brst_from_geometry",
        "declared_inputs": {"parametrisation": C.METRIC_PARAMETRISATION, "ghost_scaling": C.GHOST_SCALING,
                            "nonminimal_pair": "s cbar_mu = i b_mu, s b_mu = 0 (contractible pair; XVI-N norma
  +> lisation i)",
                            "scalar": "phi -> phi o flow  =>  s phi = xi.d phi"},
        "ghost_law_derivation": law,
        "s_images": {
            "h": "s h_mn = (1/kappa) L_xi(eta+kappa h)_mn = a(d_m c_n + d_n c_m) + kappa a (L_c h)_mn   [exact
  +> ]",
            "c": "s c^mu = (1/(kappa a)) xi.d xi^mu = kappa a c^r d_r c^mu   [exact]",
            "phi": "s phi = kappa a c^r d_r phi   [exact]",
            "cbar": "s cbar_mu = i b_mu", "b": "s b_mu = 0"},
        "per_sector_kappa_expansion": sectors,
        "s2_per_sector": s2_per_sector,
        "s2_reason": ("derived: g is affine in h and L_xi is linear in g, so (1/kappa)L_{kappa a c}g has "
                      "kappa-degree exactly 1; s xi quadratic in xi gives s c of degree exactly 1; "
                      "s phi linear in xi; (cbar,b) pair kappa-independent. 'No invented s2' is NOT used."),
        "nilpotency_exact_all_orders": nil_ok,
        "nilpotency_terms_by_order": nil,
        "matches_XVI_N_s0_s1_sc": xvin,
        "ghost_number_violations": ghbad,
        "control_nonlinear_parametrisation": ctrl,
        "execution_pass": passed,
        "claim_status": "s2_derived_zero_all_sectors" if passed else "not_derived",
        "scope": "declared affine parametrisation g=eta+kappa h, ghost scaling xi=kappa a c, a=1/2; formal pow
  +> er series in kappa",
        "pass": passed,
        "seconds": round(time.time() - t0, 2),
    }
    (ROOT / "certificates" / "P13_brst_derivation.json").write_text(certio.dumps(cert))
    print(json.dumps({"pass": passed, "lam": law["lam_solutions"], "s2": s2_per_sector,
                      "nil": nil_ok, "xvin": xvin, "exp2_s2_nonzero": ctrl["s2_h_nonzero"],
                      "exp2_omit_fails": not ctrl["s2_omitted"]["nilpotent_through_kappa2"],
                      "sec": cert["seconds"]}, indent=1))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
