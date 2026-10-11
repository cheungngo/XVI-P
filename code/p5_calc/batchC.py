#!/usr/bin/env python3
"""XVI-P p16 Batch C: D01 (h^3-h^3 graviton bubble) and D03 (closed ghost loop), the kappa^2 hh two-point graphs of
the (S0, Gamma1^[2]) s2 K:K.c row, evaluated under the frozen p14r prescription (DRED R1-R6, Feynman +i0, MS-bar,
S0) with d opaque (dred.substitute_d only).  D11 (scalar loop) is NOT evaluated (M2 undischarged).

Convention.  G_{(mn)(rs)}(p) = coefficient tensor of the ordered two-point vertex V_Gamma1[h_(mn)(p), h_(rs)(-p)] with
UPPER external indices (dual to the lower field components h_(mn); exported component (a, b) = weight(a) weight(b)
x tensor component, weight 2 for an off-diagonal field component), G = kappa^2 N_eps Ghat, N_eps = i S_eps/(16 pi^2),
Ghat = -i * prefactor/kappa^2 * int N/(D1 D2) = sum_s A_s(d) s MB,  MB = 1/eps + 2 - L,  L = log(-p^2/mu^2 - i0).

Routes (covariant.py; the p14r component route is NOT used for rank-4 numerators -- finding C1):
  C1 exact covariant form of the frozen export (polynomial identity on all 100 components; unique ansatz solution);
  C3a Feynman parameters (no S0, no Gram);  C3b frozen dred.reduce_tensor (Gram/PV) + certified J library (S0);
  R  integrand REGENERATED from S_Psi (feynman.pw_vertex, own leg loops, rule-table S_f / loop sign / propagator i's)
     and compared with the export as an exact polynomial identity (G = prefactor * N).
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
sys.path.insert(0, str(ROOT / "code" / "p5_entry"))
sys.path.insert(0, str(ROOT / "code" / "classical"))
import dred  # noqa: E402
import integrals as IL  # noqa: E402
import covariant as C  # noqa: E402
import p16_conventions as QC  # noqa: E402

d, eps = dred.d, dred.eps
I = sp.I
KAPPA = sp.Symbol("kappa")
LS = sp.symbols("l0:4")
PS = sp.symbols("p0:4")
HC = C.HC
SPEC = [("pair", ("m", "n")), ("pair", ("r", "s"))]
PAIRS = [("m", "n"), ("r", "s")]
GRAPHS = ("D01", "D03")
SLOT = "kappa^2 hh two-point (row (S0,Gamma1^[2]) s2 K:K.c with D02, D11, D12; D11 NOT evaluated)"


def log(msg):
    print(f"[batchC {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load(g):
    import batchA
    return batchA.load_export(g)


def norm_of(pref):
    return sp.simplify(-I * pref / KAPPA ** 2)


# ------------------------------------------------------------------------------------------------ regeneration
_V = {}


def _vt():
    import feynman as F
    if not _V:
        _V["F"] = F
        _V["X"] = F.S_psi_parts()["X"][1]
        P = F.propagators()
        _V["Pinv"] = P["graviton"]["Pinv"]
        _V["Gh"] = P["ghost"]["numerator"]
    return _V


def ell_density(k):
    """the EH vertex density ell_k (frozen export) as a GE density (same construction as
    counterterm_domain.S0_density for ell_2); pw_vertex then performs its own leg extraction."""
    import feynman as F
    from graded_jets import GE, esym
    e, _ = F.PW.load_ell(k)
    sub = {}
    for (m, n) in F.HC:
        sub[sp.Symbol(f"H{m}{n}")] = sp.Symbol(f"h{m}{n}")
        for r in range(4):
            sub[sp.Symbol(f"dH{m}{n}_{r}")] = sp.Symbol(f"h{m}{n}_d{r}")
    for (m, n) in F.HC:
        esym(("h", (m, n), ()))
        for r in range(4):
            esym(("h", (m, n), (r,)))
    return GE.const(e.xreplace(sub))


def mom(cl, cp):
    return [cl * LS[r] + cp * PS[r] for r in range(4)]


def regen(g, S_f=None, loop_sign=None):
    """G_regen = pref2 * N2 (component polynomials), own extraction from S_Psi."""
    V = _vt()
    F, X, Pinv, Gh = V["F"], V["X"], V["Pinv"], V["Gh"]
    hleg = lambda a, k: {"f": "h", "pol": {HC[a]: 1}, "k": k}  # noqa: E731
    N = {}
    if g == "D01":
        X = ell_density(3)
        S_f = sp.Rational(1, 2) if S_f is None else S_f
        loop_sign = 1 if loop_sign is None else loop_sign
        VA, VB = {}, {}
        for a in range(10):
            for c in range(10):
                for e in range(10):
                    v = F.pw_vertex(X, [hleg(a, mom(0, 1)), hleg(c, mom(-1, 0)), hleg(e, mom(1, -1))])
                    if v != 0:
                        VA[(a, c, e)] = v
                    w = F.pw_vertex(X, [hleg(a, mom(0, -1)), hleg(c, mom(1, 0)), hleg(e, mom(-1, 1))])
                    if w != 0:
                        VB[(a, c, e)] = w
        pv = [(c, dd, Pinv[c, dd]) for c in range(10) for dd in range(10) if Pinv[c, dd] != 0]
        WB = {}
        for (b, dd, f), poly in VB.items():
            for c, d2, pcd in pv:
                if d2 != dd:
                    continue
                for e, f2, pef in pv:
                    if f2 != f:
                        continue
                    WB[(b, c, e)] = WB.get((b, c, e), 0) + poly * pcd * pef
        for (a, c, e), pa in VA.items():
            for b in range(10):
                wb = WB.get((b, c, e))
                if wb is not None:
                    N[(a, b)] = N.get((a, b), 0) + pa * wb
        pref2 = S_f * loop_sign * I ** 2 * I ** 2          # vertices (i kappa)^2 / kappa^2 ; two graviton props i
    elif g == "D03":
        S_f = 1 if S_f is None else S_f
        loop_sign = -1 if loop_sign is None else loop_sign
        VA, VB = {}, {}
        for rho in range(4):
            for mu in range(4):
                for a in range(10):
                    v = F.pw_vertex(X, [{"f": "cb", "c": rho, "k": mom(-1, 0)}, {"f": "c", "c": mu, "k": mom(1, -1)},
                                        hleg(a, mom(0, 1))])
                    if v != 0:
                        VA[(rho, mu, a)] = v
                    w = F.pw_vertex(X, [{"f": "cb", "c": rho, "k": mom(-1, 1)}, {"f": "c", "c": mu, "k": mom(1, 0)},
                                        hleg(a, mom(0, -1))])
                    if w != 0:
                        VB[(rho, mu, a)] = w
        gh = [(m, r, Gh[m, r]) for m in range(4) for r in range(4) if Gh[m, r] != 0]
        for (rho, mu, a), pa in VA.items():
            for m2, s, g1 in gh:
                if m2 != mu:
                    continue
                for (s2, nu, b), pb in VB.items():
                    if s2 != s:
                        continue
                    for n2, r2, g2 in gh:
                        if n2 == nu and r2 == rho:
                            N[(a, b)] = N.get((a, b), 0) + pa * g1 * pb * g2
        pref2 = S_f * loop_sign * I ** 2                    # ghost numerators carry their i (M0^{-1})
    else:
        raise ValueError(g)
    return {k: sp.expand(pref2 * v) for k, v in N.items() if sp.expand(v) != 0}


def regen_equals_export(g, body, G2):
    pref = sp.sympify(body["prefactor"], locals={"kappa": KAPPA}) / KAPPA ** 2
    bad = 0
    for a in range(10):
        for b in range(10):
            e = C.export_poly(body["numerator"].get(f"{a},{b}", []), LS, PS) * pref
            if sp.expand(e - G2.get((a, b), 0)) != 0:
                bad += 1
    return {"components": 100, "mismatches": bad, "agree": bad == 0}


# ------------------------------------------------------------------------------------------------ evaluation
def evaluate_graph(g, fit=None, drop_evanescent_in=None):
    body, pin = load(g)
    pref = sp.sympify(body["prefactor"], locals={"kappa": KAPPA})
    if fit is None:
        fit = C.covariant_fit(body["numerator"], SPEC, 4, offdiag=2, upper=True)
    res = {}
    for meth in ("fp", "pv"):
        r = C.evaluate(fit["terms"], meth, g)
        if drop_evanescent_in == meth:
            r = {k: v for k, v in r.items() if not any(f[0] == "gt" for f in k)}
        o, ok = C.by_orbit(r, PAIRS, norm_of(pref))
        res[meth] = (o, ok)
    o1, o2 = res["fp"][0], res["pv"][0]
    agree = set(o1) == set(o2) and all(sp.cancel(o1[k] - o2[k]) == 0 for k in o1)
    return {"body": body, "pin": pin, "pref": pref, "fit": fit, "A": o1, "A_pv": o2, "routes_agree": agree,
            "orbit_consistent": res["fp"][1] and res["pv"][1]}


def exchange_symmetric(A):
    """(mn) <-> (rs) exchange symmetry of the result (Bose symmetry of the hh two-point function)."""
    sw = {"m": "r", "n": "s", "r": "m", "s": "n"}
    group = C.sym_group(PAIRS)
    for (orb, e), cf in A.items():
        img = C.orbit(C.relabel(sorted(orb)[0], sw), group)
        if sp.cancel(A.get((img, e), 0) - cf) != 0:
            return False
    return True


def hh_basis():
    """the p14r h.h counterterm directions (CT.sector_basis('h','h',4)) as ordered two-point vertices
    V[h_(mn)(p), h_(rs)(-p)] (same extraction as the export), written covariantly (same convention as G)."""
    import counterterm_domain as CT
    import feynman as F
    dens = CT.sector_basis("h", "h", 4)
    keep, _ = CT.independent(dens, [("h", "h")])
    out = []
    for dn in keep:
        polys = {}
        for a in range(10):
            for b in range(10):
                v = F.pw_vertex(dn, [{"f": "h", "pol": {HC[a]: 1}, "k": list(PS)},
                                     {"f": "h", "pol": {HC[b]: 1}, "k": [-x for x in PS]}])
                if v != 0:
                    polys[f"{a},{b}"] = v
        fit = C.covariant_fit({}, SPEC, 4, offdiag=2, upper=True, polys=polys)
        coords = {}
        for orb, sc, c in fit["terms"]:
            e = sp.degree(sc, C.PP)
            coords[(orb, e)] = coords.get((orb, e), 0) + c
        out.append({"density": str(dn)[:200], "fit_exact": fit["exact"], "coords": coords})
    return out


def four_d_keys(A):
    return sorted([k for k in A if not C.is_evanescent(k[0])], key=lambda k: C.label(*k))


def pole_in_hh_basis(vec, basis):
    """solve sum_k z_k basis_k = vec (4D structures; covariant coordinates; the basis vertex is i x density)."""
    keys = sorted(set(vec) | {k for b in basis for k in b["coords"]}, key=lambda k: C.label(*k))
    zs = sp.symbols(f"z0:{len(basis)}")
    eqs = [sp.expand(sum(z * b["coords"].get(k, 0) for z, b in zip(zs, basis)) - vec.get(k, 0)) for k in keys]
    sol = sp.solve(eqs, zs, dict=True)
    if not sol:
        return None, False
    return [sp.simplify(sol[0].get(z, z)) for z in zs], all(not sp.sympify(sol[0].get(z, z)).free_symbols
                                                             for z in zs)


def component_route_unfaithful():
    """demonstration of finding C1: sum_rs eta^rr eta^ss Gt_rs Gt_rs (abstract value tr(gtilde.gtilde) = 4 - d)
    under the linear realization Gt = (4-d) M is realization-dependent and != 4 - d."""
    vals = []
    for pn in ([3, 1, -2, 5], [sp.Rational(7, 2), -1, 4, 2]):
        for sd in (11, 12):
            gm = IL.realization([sp.Integer(x) for x in pn], sd)
            e = sum(dred.ETA[r] * dred.ETA[s] * dred.Gt(r, s) ** 2 for r in range(4) for s in range(4))
            vals.append(sp.factor(e.xreplace(gm)))
    distinct = len({str(v) for v in vals})
    return {"expression": "sum_rs eta^rr eta^ss Gt_rs Gt_rs", "abstract_value": "4 - d",
            "realized_values": [str(v) for v in vals], "realization_dependent": distinct > 1,
            "equals_abstract": all(sp.cancel(v - (4 - d)) == 0 for v in vals)}


def count_quadratic_component_terms(g, body):
    P = dred.Pipeline()
    n = 0
    for comp, rows in body["numerator"].items():
        tot = 0
        for names, cf in rows:
            lc = sorted(int(v[1]) for v in names if v.startswith("l"))
            pc = sp.Mul(*[sp.Symbol(v) for v in names if v.startswith("p")])
            tot += sp.Rational(cf) * pc * P.reduced_component(lc, with_p=True, tag=g)
        tot = sp.expand(tot)
        gts = [s for s in tot.free_symbols if s.name.startswith("Gt_")]
        if gts and max(sum(m) for m in sp.Poly(tot, *gts).monoms()) >= 2:
            n += 1
    return n


def s(x):
    return str(sp.simplify(x)) if not isinstance(x, str) else x


# ------------------------------------------------------------------------------------------------ main
def laurent_table(A):
    import d13 as D13
    out = {}
    for key in sorted(A, key=lambda k: C.label(*k)):
        ex = D13.expand_coeff(A[key])
        out[key] = ex
    return out


def longitudinal_projection(A):
    """slot role (row (S0,Gamma1^[2]) s2 K:K.c): s h_(mn) = d_(m c_n) is longitudinal, so only p_m G^{(mn)(rs)}
    enters; returns {label of remaining structure (free n, r, s): coefficient(d) of MB}."""
    import e2_evanescent as E2M
    terms = []
    for (orb, e), cf in A.items():
        for facs in orb:
            terms.append((cf * C.PP ** e, E2M.to_dred(list(facs)) + [("v", "p", "m")]))
    res = E2M.contract_all(terms)
    out = {}
    for k, v in res.items():
        lab = " ".join(f"{f[1] if f[0] == 'g' else f[1]}_{''.join(f[2:])}" for f in k)
        out[lab] = sp.factor(v)
    return out


def mutations(evs, regens):
    out = {}
    # M1 wrong ghost-loop sign (D03): regenerated with loop sign +1 != export
    Gm = regen("D03", loop_sign=1)
    cm = regen_equals_export("D03", evs["D03"]["body"], Gm)
    out["wrong_ghost_loop_sign_D03"] = {"changes_result": True, "rejected": not cm["agree"],
                                        "reason": f"regenerated (loop sign +1) != frozen export: {cm['mismatches']} "
                                                  "components (the result flips sign: A -> -A)"}
    # M2 wrong symmetry factor (D01: S_f = 1 instead of 1/2); S_f enters only the prefactor -> 2 x regenerated
    Gs = {k: 2 * v for k, v in regens["D01"].items()}
    cs = regen_equals_export("D01", evs["D01"]["body"], Gs)
    out["wrong_symmetry_factor_D01"] = {"changes_result": True, "rejected": not cs["agree"],
                                        "reason": f"S_f = 1 regeneration != export: {cs['mismatches']} components"}
    # M3 premature d = 4 (structural R5 safeguard)
    k0 = next(iter(evs["D01"]["A"]))
    a0 = evs["D01"]["A"][k0]
    try:
        sp.sympify(a0).subs(d, 4)
        out["premature_d4"] = {"rejected": False, "changes_result": None}
    except dred.PrematureD4Substitution as exc:
        lt = laurent_table({k0: a0})[k0]
        out["premature_d4"] = {"rejected": True,
                               "changes_result": any(laurent_table({k: v})[k]["d_dependence_shift_of_local_part"] != 0
                                                     for g in GRAPHS for k, v in evs[g]["A"].items()),
                               "reason": f"PrematureD4Substitution at the substitution site: {exc}",
                               "example": {"structure": C.label(*k0), "local_if_d4_first":
                                           str(lt["finite_if_d_set_to_4_first"]), "certified_finite": str(lt["finite"])}}
    # M4 dropped evanescent (gt -> 0 in the Feynman-parameter route only)
    ev4 = evaluate_graph("D01", fit=evs["D01"]["fit"], drop_evanescent_in="fp")
    out["drop_evanescent_gt"] = {"changes_result": set(ev4["A"]) != set(evs["D01"]["A"]),
                                 "rejected": not ev4["routes_agree"],
                                 "reason": "Feynman-parameter route with gt dropped != PV route (ghat kept): R6 "
                                           "retention check fails"}
    # M5 wrong external index position (lower instead of upper) -> no exact covariant form
    f5 = C.covariant_fit(evs["D03"]["body"]["numerator"], SPEC, 4, offdiag=2, upper=False)
    out["wrong_external_index_position"] = {"changes_result": True, "rejected": not f5["exact"],
                                            "reason": f"covariant form with lower external indices: exact = "
                                                      f"{f5['exact']} ({f5['bad_components'][:2]})"}
    # M6 off-diagonal component weight 1 -> no exact covariant form
    f6 = C.covariant_fit(evs["D03"]["body"]["numerator"], SPEC, 4, offdiag=1, upper=True)
    out["wrong_offdiagonal_weight"] = {"changes_result": True, "rejected": not f6["exact"],
                                       "reason": f"off-diagonal weight 1: exact = {f6['exact']}"}
    # M7 the p14r component route with the linear Gt realization (finding C1)
    cr = component_route_unfaithful()
    out["component_route_linear_realization"] = {"changes_result": not cr["equals_abstract"],
                                                 "rejected": cr["realization_dependent"],
                                                 "reason": "Gt-quadratic component sums are realization-dependent "
                                                           f"under Gt = (4-d) M: {cr['realized_values'][:2]} vs 4 - d"}
    for v in out.values():
        v["accepted_as_rejection"] = bool(v["rejected"] and v["changes_result"])
    return out


def main():
    import certio
    t0 = time.time()
    IL.LEDGER.clear()
    evs, regens, recs = {}, {}, {}
    for g in GRAPHS:
        log(f"{g}: covariant fit + FP/PV routes")
        evs[g] = evaluate_graph(g)
        log(f"{g}: regeneration from S_Psi")
        regens[g] = regen(g)
    s0 = list(IL.LEDGER)
    log("D13 control through the covariant route")
    import batchA
    b13, _ = batchA.load_export("D13")
    f13 = C.covariant_fit(b13["numerator"], [("pair", ("m", "n")), ("vec", "v")], 3)
    r13 = C.evaluate(f13["terms"], "fp", "D13")
    o13, _ = C.by_orbit(r13, [("m", "n")], norm_of(sp.sympify(b13["prefactor"], locals={"kappa": KAPPA})))
    cert13 = json.loads((ROOT / "certificates" / "P15_D13.json").read_text())["result"]
    want = {"T2": "g4_mv p_n (p.p)^1", "T3": "p_m p_n p_v", "E2": "gt_mv p_n (p.p)^1"}
    got = {C.label(*k): v for k, v in o13.items()}
    d13_ok = (len(got) == 3 and all(sp.cancel(got[lab] - sp.sympify(cert13[t]["A_exact_d_times_MB"],
                                                                     locals={"d": d})) == 0 for t, lab in want.items())
              and all(cert13[t]["A_exact_d_times_MB"] == "0" for t in ("T1", "E1")))
    log("p14r h.h counterterm basis")
    basis = hh_basis()
    log("component-route demonstration")
    comp_quad = {g: count_quadratic_component_terms(g, evs[g]["body"]) for g in GRAPHS}
    log("mutations")
    muts = mutations(evs, regens)
    graphs = {}
    ok_all = True
    total4 = {}
    for g in GRAPHS:
        ev = evs[g]
        A = ev["A"]
        lt = laurent_table(A)
        rg = regen_equals_export(g, ev["body"], regens[g])
        pole4 = {k: lt[k]["pole"] for k in four_d_keys(A)}
        for k, v in pole4.items():
            total4[k] = total4.get(k, 0) + v
        z, zok = pole_in_hh_basis(pole4, basis)
        ev_pole = {C.label(*k): str(lt[k]["pole"]) for k in A if C.is_evanescent(k[0])}
        ev_nonzero = any(lt[k]["pole"] != 0 for k in A if C.is_evanescent(k[0]))
        ctrl = {"export_sha_pinned": ev["pin"]["pinned"], "covariant_form_exact": ev["fit"]["exact"],
                "covariant_form_unique": ev["fit"]["unique"], "orbit_consistent": ev["orbit_consistent"],
                "route_FP_equals_route_PV_exact_in_d": ev["routes_agree"],
                "regenerated_integrand_equals_export": rg["agree"],
                "exchange_symmetric_mn_rs": exchange_symmetric(A),
                "nonlocal_equals_minus_pole": all(sp.simplify(lt[k]["nonlocal_L_coefficient"] + lt[k]["pole"]) == 0
                                                  for k in A),
                "pole_4D_in_p14r_hh_span": bool(zok),
                "R5_d_retained": any(sp.sympify(v).has(d) for v in A.values())}
        ok = all(ctrl.values())
        ok_all = ok_all and ok
        status = "renormalized" if ok and not ev_nonzero else ("regulated" if ok else "unevaluated")
        assert status in QC.STATUS_VALUES
        table = {C.label(*k): {"evanescent": C.is_evanescent(k[0]), "A_exact_d_times_MB": s(lt[k]["exact_d"]),
                               "UV_pole": s(lt[k]["pole"]), "MSbar_finite": s(lt[k]["finite"]),
                               "nonlocal_coefficient_of_L": s(lt[k]["nonlocal_L_coefficient"]),
                               "local_polynomial": s(lt[k]["local"]),
                               "finite_if_d_set_to_4_first": s(lt[k]["finite_if_d_set_to_4_first"]),
                               "local_shift_from_d_dependence": s(lt[k]["d_dependence_shift_of_local_part"])}
                 for k in sorted(A, key=lambda k: C.label(*k))}
        graphs[g] = {"slot": SLOT, "export": ev["pin"], "prefactor_export": str(ev["pref"]),
                     "normalization": f"Ghat = {norm_of(ev['pref'])} * int N/(D1 D2) / N_eps",
                     "covariant_form": {k: v for k, v in ev["fit"].items() if k != "terms"},
                     "result": table, "status": status,
                     "sector_status": {"4D": "renormalized (pole in the p14r h.h span)" if ok else "regulated",
                                       "evanescent": ("regulated: evanescent poles NONZERO, retained (R6); no "
                                                      "evanescent h.h counterterm is declared" if ev_nonzero
                                                      else "pole zero")},
                     "UV_pole_in_p14r_hh_basis": [s(x) for x in z] if z else None,
                     "evanescent_poles": ev_pole, "evanescent_pole_nonzero": ev_nonzero,
                     "longitudinal_projection_p_m_G": {k: str(v) for k, v in sorted(longitudinal_projection(A).items())},
                     "regeneration": rg, "component_route_Gt_quadratic_components": comp_quad[g],
                     "controls": ctrl, "evaluated": ok}
    controls = {"D13_reproduced_by_covariant_route": d13_ok,
                "hh_basis_fits_exact": all(b["fit_exact"] for b in basis) and len(basis) == 5,
                "R5_structural_safeguard_active": muts["premature_d4"]["rejected"],
                "mutations_all_rejected": all(v["accepted_as_rejection"] for v in muts.values()),
                **{f"{g}_evaluated": graphs[g]["evaluated"] for g in GRAPHS}}
    batchC_ok = ok_all and all(controls.values())
    zt, ztok = pole_in_hh_basis(total4, basis)
    rec = {"landmark": "XVI-P", "revision": QC.REVISION, "deliverable": "P.5 calculation Batch C: D01, D03 (kappa^2 hh)",
           "prescription": "frozen p14r P14_DRED_MSbar_FeynmanI0 + S0 (P15_integral_library.json); covariant route "
                           "(covariant.py, finding C1)",
           "convention": __doc__.split("Convention.")[1].split("Routes")[0].strip(),
           "finding_C1_component_route": {
               "statement": ("the p14r per-component R3 lift produces Gt-quadratic component sums for rank-4 "
                             "numerators (D01/D03) whose abstract value cannot be recovered after the component sums; "
                             "the linear realization Gt = (4-d)M is not faithful there; Batch C therefore uses the "
                             "covariant route (C1-C5), which evaluates the same rules R1-R6 with free external indices "
                             "only"),
               "components_with_Gt_quadratic_terms": comp_quad, "demonstration": component_route_unfaithful(),
               "D13_unaffected": "rank 3, linear in Gt; reproduced exactly by the covariant route (control)",
               "contract_change": False},
           "graphs": graphs, "D01_plus_D03_4D_pole_in_p14r_hh_basis": [s(x) for x in zt] if zt else None,
           "hh_basis": [{"density": b["density"], "coords": {C.label(*k): str(v) for k, v in b["coords"].items()}}
                        for b in basis],
           "D11": "NOT evaluated (M2 undischarged); the hh slot is incomplete (D01 + D02 + D03 + D11 + D12)",
           "controls": controls, "mutations": muts,
           "batchC_evaluated": {
               "execution": batchC_ok,
               "claim": ("D01 and D03 evaluated in closed form under the declared prescription (covariant route): "
                         "exact covariant integrands (verified on all 100 components, regenerated from S_Psi), two "
                         "independent loop-integration routes agree exactly in d, 4D UV poles local and in the p14r "
                         "h.h span, MS-bar finite parts = nonlocal log + local quartic polynomial, evanescent poles "
                         "recorded (R6), mutations rejected") if batchC_ok else "not established",
               "scope": ("two graphs (D01, D03) of the kappa^2 hh slot; massless; MS-bar at mu; external momenta in "
                         "QdS; evanescent structures retained (their poles are NONZERO and not absorbed: no evanescent "
                         "h.h counterterm is declared); D11 NOT evaluated, so the hh slot is incomplete; NOT "
                         "quantum_inputs_evaluated")},
           "scaleless_rule_applications": sorted(s0, key=lambda r: json.dumps(r, sort_keys=True)),   # deterministic order "authorised_d_substitutions": dict(dred.D_PROVENANCE),
           "loop_evaluations_performed": True, "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_batchC.json", rec)
    print(json.dumps({"batchC_evaluated": batchC_ok, "controls": controls,
                      "graphs": {g: {"status": graphs[g]["status"], "controls": graphs[g]["controls"],
                                     "z": graphs[g]["UV_pole_in_p14r_hh_basis"]} for g in GRAPHS},
                      "mutations": {k: [v["changes_result"], v["rejected"]] for k, v in muts.items()},
                      "seconds": rec["seconds"]}, indent=1))
    return 0 if batchC_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
