#!/usr/bin/env python3
"""XVI-P p15 Batch B: D13, the kappa^2 K'.c source coefficient (open ghost line + graviton line), fully evaluated.

Gamma_1 contains  int K'_(a') G_{a' nu} c^nu ;  G_{a' nu}(p) = V_{Gamma_1}[K'_(a')(-p), c^nu(p)] (ordered extraction),
iGamma_1 integrand = prefactor * N / ((l^2 + i0)((p-l)^2 + i0))  =>  G = -i * prefactor * int N/(D1 D2).
Result convention:  G_{(mn) nu}(p) = kappa^2 * N_eps * Ghat_{(mn) nu}(p),  N_eps = i S_eps/(16 pi^2)  (integrals.py).

Route 1  frozen export (sha-pinned) -> frozen dred Pipeline (R3 lift, R4 Gram/PV reduction in ghat, ledger) -> J[a,b]
         via the library (S0 for every cancelled propagator) -> R1(d, p, Gt) * MB.
Route 2  integrand REGENERATED here from S_Psi (feynman.pw_vertex, own leg loop; rule table: S_f, loop sign, external
         sign, K'/c leg order) -> Feynman parameters, l = k + x p, symmetric integration in QdS -> R2 * MB (no S0).
Covariant form  Ghat = sum_i A_i(d) T_i + sum_j B_j(d) E_j  times MB, with
   T1 = eta_mn p_nu p^2, T2 = (eta_m nu p_n + eta_n nu p_m) p^2, T3 = p_m p_n p_nu      (4D structures)
   E1 = Gt_mn p_nu p^2,  E2 = (Gt_m nu p_n + Gt_n nu p_m) p^2                       (evanescent structures)
fitted EXACTLY in d on the faithful realization Gt = (4-d) M (integrals.realization), several p and M.
Laurent / MS-bar with d kept symbolic until the expansion (R5); premature d = 4 is caught (frozen exception class).
"""
from __future__ import annotations
import itertools
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
import p15_conventions as QC  # noqa: E402

d, eps = dred.d, dred.eps
I = sp.I
ETA = dred.ETA
LS = sp.symbols("l0:4")
PS = sp.symbols("p0:4")
PP = IL.PP
MB = IL.MB
HC = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
P_NUMS = [[sp.Integer(3), sp.Integer(1), sp.Integer(-2), sp.Integer(5)],
          [sp.Rational(7, 2), sp.Integer(-1), sp.Integer(4), sp.Integer(2)],
          [sp.Integer(2), sp.Rational(-3, 2), sp.Integer(1), sp.Integer(-1)]]
SEEDS = (11, 12)


# ================================================================================================ helpers
def eta(a, b):
    return ETA[a] if a == b else 0


def gt(a, b):
    return dred.Gt(a, b)


def pp_expr():
    return sum(ETA[r] * PS[r] ** 2 for r in range(4))


def structures():
    """component tensors (keyed (ap, nu)) of the 4D and evanescent structures (lower indices; p lower)."""
    T = {"T1": {}, "T2": {}, "T3": {}, "E1": {}, "E2": {}}
    for ap, (m, n) in enumerate(HC):
        for nu in range(4):
            k = (ap, nu)
            T["T1"][k] = eta(m, n) * PS[nu] * PP
            T["T2"][k] = (eta(m, nu) * PS[n] + eta(n, nu) * PS[m]) * PP
            T["T3"][k] = PS[m] * PS[n] * PS[nu]
            T["E1"][k] = gt(m, n) * PS[nu] * PP
            T["E2"][k] = (gt(m, nu) * PS[n] + gt(n, nu) * PS[m]) * PP
    return T


STRUCT_4D = ("T1", "T2", "T3")
STRUCT_EV = ("E1", "E2")


def key_of(s):
    a, b = s.split(",")
    return int(a), int(b)


# ================================================================================================ route 1
def load_export():
    import batchA
    return batchA.load_export("D13")


def route1(mutation=None, enforce=True):
    """frozen export -> frozen dred Pipeline -> {(ap,nu): R1 (coefficient of MB)} ; ledger."""
    body, pin = load_export()
    P = dred.Pipeline(mutation="premature_d4" if mutation == "premature_d4" else None, enforce=enforce)
    Jv = IL.J_values("D13", [(a, b) for a in range(3) for b in range(5)])
    out = {}
    for comp, rows in body["numerator"].items():
        tot = 0
        for names, cf in rows:
            lc = sorted(int(v[1]) for v in names if v.startswith("l"))
            pc = sp.Mul(*[sp.Symbol(v) for v in names if v.startswith("p")])
            tot += sp.Rational(cf) * pc * P.reduced_component(lc, with_p=True, tag="D13")
        tot = sp.expand(tot)
        if mutation == "drop_evanescent":
            tot = sp.expand(tot.xreplace({s: 0 for s in tot.free_symbols if s.name.startswith("Gt_")}))
        R = sp.expand(tot.xreplace(Jv))
        out[key_of(comp)] = sp.expand(R / MB) if R != 0 else sp.Integer(0)
    pref = sp.sympify(body["prefactor"], locals={"kappa": sp.Symbol("kappa")})
    norm = sp.simplify(-I * pref / sp.Symbol("kappa") ** 2)          # Ghat = norm * R1
    return {k: sp.expand(norm * v) for k, v in out.items()}, P.ledger, pin, str(pref)


# ================================================================================================ route 2 (regeneration)
_VCACHE = {}


def _vertices():
    import feynman as F
    if "X" not in _VCACHE:
        _VCACHE["X"] = F.S_psi_parts()["X"]
        P = F.propagators()
        _VCACHE["Pinv"] = P["graviton"]["Pinv"]
        _VCACHE["Gh"] = P["ghost"]["numerator"]
        _VCACHE["F"] = F
    return _VCACHE


def mom(cl, cp):
    return [cl * LS[r] + cp * PS[r] for r in range(4)]


def regen_integrand(first="K", order=("K", "c", "h")):
    """N2[(a, nu)] = sum vk * <c cbar> * vg * <h h>  with the first vertex V[first(-p), c^mu(l), h_c(p-l)] taken in the
    rule-table leg order; first = 'K' (D13) or 'cb' (ghost self-energy, same topology).  No exported data used."""
    V = _vertices()
    F, X, Pinv, Gh = V["F"], V["X"][1], V["Pinv"], V["Gh"]
    ckey = ("first", first, tuple(order))
    if ckey in _VCACHE:
        return _VCACHE[ckey]
    comps_first = range(10) if first == "K" else range(4)
    vk = {}
    for a in comps_first:
        for mu in range(4):
            for c in range(10):
                if first == "K":
                    lg = {"K": {"f": "K", "c": HC[a], "k": mom(0, -1)}}
                else:
                    lg = {"K": {"f": "cb", "c": a, "k": mom(0, -1)}}
                lg["c"] = {"f": "c", "c": mu, "k": mom(1, 0)}
                lg["h"] = {"f": "h", "pol": {HC[c]: 1}, "k": mom(-1, 1)}
                v = F.pw_vertex(X, [lg[x] for x in order])
                if v != 0:
                    vk[(a, mu, c)] = v
    if "vg" not in _VCACHE:
        vg = {}
        for rho in range(4):
            for nu in range(4):
                for dd in range(10):
                    v = F.pw_vertex(X, [{"f": "cb", "c": rho, "k": mom(-1, 0)}, {"f": "c", "c": nu, "k": mom(0, 1)},
                                        {"f": "h", "pol": {HC[dd]: 1}, "k": mom(1, -1)}])
                    if v != 0:
                        vg[(rho, nu, dd)] = v
        _VCACHE["vg"] = vg
    vg = _VCACHE["vg"]
    gh = [(mu, rho, Gh[mu, rho]) for mu in range(4) for rho in range(4) if Gh[mu, rho] != 0]
    pv = [(c, dd, Pinv[c, dd]) for c in range(10) for dd in range(10) if Pinv[c, dd] != 0]
    N = {}
    for a in comps_first:
        for nu in range(4):
            tot = 0
            for mu, rho, g in gh:
                for c, dd, pval in pv:
                    x1 = vk.get((a, mu, c))
                    if x1 is None:
                        continue
                    x2 = vg.get((rho, nu, dd))
                    if x2 is None:
                        continue
                    tot += x1 * g * x2 * pval
            tot = sp.expand(tot)
            if tot != 0:
                N[(a, nu)] = tot
    _VCACHE[ckey] = N
    return N


def route2(S_f=1, loop_sign=1, ext_sign=1, order=("K", "c", "h"), first="K"):
    """Ghat2 = -i * pref2/kappa^2 * R2,  pref2 = ext * S_f * loop * (i kappa)^2 * i  (propagator i's: ghost numerator
    already carries i (M0^{-1}) -> one explicit i for the graviton propagator, as in build_integrands)."""
    N = regen_integrand(first, order)
    pref_over_k2 = sp.Integer(ext_sign) * sp.nsimplify(S_f) * loop_sign * (I ** 2) * I
    norm = sp.expand(-I * pref_over_k2)
    out = {}
    for k, poly in N.items():
        R = IL.fp_two_point(poly, LS, PS)
        out[k] = sp.expand(norm * R / MB)
    return out


# ================================================================================================ fit / Laurent
def _realized_rows(G, p_num, gm):
    S = structures()
    names = STRUCT_4D + STRUCT_EV
    rows, rhs = [], []
    for k in sorted(set(G) | set(S["T1"])):
        rows.append([IL.realize(S[nm][k], p_num, gm) for nm in names])
        rhs.append(IL.realize(G.get(k, 0), p_num, gm))
    return rows, rhs


def exact_fit(A, b, n):
    """exact solution of the overdetermined linear system A x = b (entries rational in d): n independent rows are
    selected at a generic numerical d, the n x n system is solved exactly, and EVERY row is verified exactly."""
    dg = sp.Rational(173, 37)
    chosen, M = [], []
    for i, row in enumerate(A):
        cand = M + [[dred.substitute_d(x, dg, "d13.exact_fit: numerical rank test for row selection only (the solve "
                                            "and the verification of every row are exact in d)") for x in row]]
        if sp.Matrix(cand).rank() > len(M):
            M, chosen = cand, chosen + [i]
        if len(chosen) == n:
            break
    if len(chosen) < n:
        return None, False
    As = sp.Matrix([A[i] for i in chosen])
    bs = sp.Matrix([b[i] for i in chosen])
    sol = [sp.factor(sp.cancel(x)) for x in As.LUsolve(bs)]
    ok = all(sp.cancel(sum(sp.sympify(a) * x for a, x in zip(row, sol)) - rhs) == 0 for row, rhs in zip(A, b))
    return sol, ok


def fit(G):
    """exact covariant fit; returns ({name: coefficient(d)}, residual_ok, n_equations)."""
    names = STRUCT_4D + STRUCT_EV
    A, b = [], []
    for pn in P_NUMS:
        for s in SEEDS:
            gm = IL.realization(pn, s)
            r, h = _realized_rows(G, pn, gm)
            A += r
            b += h
    sol, ok = exact_fit(A, b, len(names))
    return dict(zip(names, sol)), ok, len(b)


def expand_coeff(c):
    """A(d) * MB  ->  {pole, finite, nonlocal (coefficient of L), local}; d = 4 - 2 eps, MB = 1/eps + 2 - L + O(eps)."""
    ms = IL.master_series(1)
    mbs = ms[-1] / eps + ms[0] + ms[1] * eps
    a = dred.substitute_d(c, 4 - 2 * eps, "d13.expand_coeff: Laurent expansion after all contractions and the fit")
    ser = sp.series(sp.expand(a * mbs), eps, 0, 1).removeO()
    pole = sp.simplify(ser.coeff(eps, -1))
    fin = sp.expand(sp.simplify(ser.coeff(eps, 0)))
    nonloc = sp.expand(fin.coeff(IL.L))
    loc = sp.expand(fin - nonloc * IL.L)
    a4 = sp.simplify(dred.substitute_d(c, 4, "d13.expand_coeff: diagnostic A(4) (d-dependence proof only)"))
    da4 = sp.simplify(dred.substitute_d(sp.diff(sp.sympify(c), d), 4, "d13.expand_coeff: diagnostic A'(4)"))
    return {"exact_d": sp.factor(c), "A_at_4": a4, "dA_dd_at_4": da4, "pole": pole, "finite": fin,
            "nonlocal_L_coefficient": nonloc, "local": loc,
            "finite_if_d_set_to_4_first": sp.expand(a4 * (2 - IL.L)),
            "d_dependence_shift_of_local_part": sp.expand(loc - 2 * a4)}


# ================================================================================================ counterterm basis (p14r)
def ck_basis():
    """the p14r c.K' counterterm directions as ordered two-point vertices V[K'_(a')(-p), c^nu(p)] (same convention
    as G), and their coordinates on T1..T3."""
    import counterterm_domain as CT
    import feynman as F
    dens = CT.sector_basis("c", "K", 3)
    keep, _ = CT.independent(dens, [("c", "K")])
    S = structures()
    basis = []
    for dn in keep:
        Vk = {}
        for ap in range(10):
            for nu in range(4):
                v = F.pw_vertex(dn, [{"f": "K", "c": HC[ap], "k": [-x for x in PS]}, {"f": "c", "c": nu, "k": list(PS)}])
                if v != 0:
                    Vk[(ap, nu)] = sp.expand(v.xreplace({}))
        # coordinates on T1..T3 (exact, symbolic p)
        cs = sp.symbols("c1:4")
        eqs = []
        for k in set(Vk) | set(S["T1"]):
            e = sp.expand(Vk.get(k, 0) - sum(c * S[nm][k].xreplace({PP: pp_expr()}) for c, nm in zip(cs, STRUCT_4D)))
            if e != 0:
                eqs += sp.Poly(e, *PS).coeffs()
        sol = sp.solve(eqs, cs, dict=True)
        basis.append({"density": str(dn)[:300], "T_coordinates": [sp.simplify(sol[0][c]) for c in cs] if sol else None})
    return basis


def to_ct_coordinates(Tcoef, basis):
    """express sum_i Tcoef_i T_i in the p14r c.K' basis: solve sum_k z_k basis_k = Tcoef."""
    M = sp.Matrix([[b["T_coordinates"][i] for b in basis] for i in range(3)])
    z = M.LUsolve(sp.Matrix(Tcoef))
    return [sp.simplify(x) for x in z], M.rank() == 3


# ================================================================================================ ghost equation (BRST sanity)
def deDonder_apply(G):
    """2 i D^rho[G_{..nu}] at K = p:  D^rho T = i p_s eta^{rr} eta^{ss} T_{r s} - 1/2 i eta^{rr} p_r tr T,
    T_mn = G_{(min,max) nu}, trace over the quasi-4D external index (R4/R5 external projection)."""
    out = {}
    idx = {mn: a for a, mn in enumerate(HC)}
    for rho in range(4):
        for nu in range(4):
            T = lambda m, n: G.get((idx[(min(m, n), max(m, n))], nu), 0)  # noqa: E731
            tr = sum(ETA[m] * T(m, m) for m in range(4))
            D = sum(I * PS[s] * ETA[rho] * ETA[s] * T(rho, s) for s in range(4)) - sp.Rational(1, 2) * I * ETA[rho] * PS[rho] * tr
            v = sp.expand(2 * I * D)
            if v != 0:
                out[(rho, nu)] = v
    return out


def compare_realized(G1, G2, keys=None):
    bad, n = [], 0
    for pn in P_NUMS[:2]:
        for s in SEEDS:
            gm = IL.realization(pn, s)
            for k in (keys or sorted(set(G1) | set(G2))):
                n += 1
                df = sp.cancel(IL.realize(G1.get(k, 0), pn, gm) - IL.realize(G2.get(k, 0), pn, gm))
                if df != 0:
                    bad.append({"comp": list(k), "diff": str(df)[:120]})
    return {"compared": n, "mismatches": bad[:4], "n_mismatches": len(bad), "agree": not bad}


# ================================================================================================ main evaluation
def log(msg):
    print(f"[d13 {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def evaluate():
    t0 = time.time()
    log("route 1")
    G1, ledger, pin, pref = route1()
    t1 = time.time()
    log("route 2")
    G2 = route2()
    t2 = time.time()
    log("compare")
    agree = compare_realized(G1, G2)
    log("fit")
    fit1, ok1, neq = fit(G1)
    fit2, ok2, _ = fit(G2)
    same_fit = all(sp.cancel(fit1[k] - fit2[k]) == 0 for k in fit1)
    log("laurent")
    exp = {k: expand_coeff(v) for k, v in fit1.items()}
    log("ck basis")
    basis = ck_basis()
    pole4 = [exp[k]["pole"] for k in STRUCT_4D]
    loc4 = [exp[k]["local"] for k in STRUCT_4D]
    nonl4 = [exp[k]["nonlocal_L_coefficient"] for k in STRUCT_4D]
    zpole, full = to_ct_coordinates(pole4, basis)
    zloc, _ = to_ct_coordinates(loc4, basis)
    znl, _ = to_ct_coordinates(nonl4, basis)
    ev_pole = {k: exp[k]["pole"] for k in STRUCT_EV}
    t3 = time.time()
    # ghost equation: evaluated ghost self-energy (route 2, cbar external) == 2 i D[G] (route 1)
    log("ghost equation")
    Sig = route2(first="cb")
    DG = deDonder_apply(G1)
    ghost_eq = compare_realized(Sig, DG)
    t4 = time.time()
    return {"G1": G1, "G2": G2, "fit": fit1, "fit2": fit2, "fit_exact": ok1 and ok2, "fit_equations": neq,
            "routes_agree": agree, "fits_agree": same_fit, "exp": exp, "basis": basis, "basis_full_rank": full,
            "z_pole": zpole, "z_local": zloc, "z_nonlocal": znl, "ev_pole": ev_pole, "ledger": ledger, "pin": pin,
            "prefactor": pref, "ghost_equation": ghost_eq, "Sigma": Sig,
            "timing": {"route1": round(t1 - t0, 1), "route2": round(t2 - t1, 1), "fit_laurent_ct": round(t3 - t2, 1),
                       "ghost_eq": round(t4 - t3, 1)}}


def mutations(base):
    """each mutation must CHANGE the result and be REJECTED by a control."""
    out = {}
    ref = base["fit"]

    def differs(f):
        return any(sp.cancel(f[k] - ref[k]) != 0 for k in ref)
    # 1 wrong ghost-loop sign: a closed-ghost-loop (-1) applied to the OPEN ghost line of D13 (route 2 regenerated)
    Gm = route2(loop_sign=-1)
    fm, _, _ = fit(Gm)
    cmpm = compare_realized(base["G1"], Gm)
    out["wrong_ghost_loop_sign"] = {"changes_result": differs(fm), "rejected": not cmpm["agree"],
                                    "reason": f"route 1 (frozen export) != regenerated route 2: {cmpm['n_mismatches']} "
                                              "mismatches; W1 shadow: D13 has no closed ghost loop",
                                    "pole_T_if_accepted": [str(sp.simplify(dred.substitute_d(
                                        fm[k], 4, "d13.mutation display: pole"))) for k in STRUCT_4D]}
    # 2 dropped evanescent term via premature d = 4 (frozen Pipeline mutation) -> structural R5 safeguard
    #   (p15 contract correction: the opaque d raises AT the substitution; the p14r heuristic guard is withdrawn)
    try:
        route1(mutation="premature_d4")
        out["premature_d4"] = {"rejected": False, "changes_result": None}
    except dred.PrematureD4Substitution as exc:
        Gp, _, _, _ = route1(mutation="premature_d4", enforce=False)        # display only (authorised path)
        fp_, okp, _ = fit(Gp)
        exp_if = {k: expand_coeff(fp_[k]) for k in fp_}                   # authorised Laurent path (display)
        loc_if = [str(exp_if[k]["local"]) for k in STRUCT_4D]
        out["premature_d4"] = {"rejected": True, "changes_result": differs(fp_),
                               "reason": f"PrematureD4Substitution (structural, at the substitution site): {exc}",
                               "fit_d_free_if_not_caught": not any(sp.sympify(v).has(d) for v in fp_.values()),
                               "local_part_if_not_caught_T": loc_if,
                               "local_part_certified_T": [str(base["exp"][k]["local"]) for k in STRUCT_4D],
                               "note": ("the Gt realization Gt = (4-d) M reintroduces d after the premature "
                                        "substitution (the false-negative mechanism of finding F1); only the "
                                        "structural safeguard catches it"),
                               "pole_T_if_not_caught": [str(exp_if[k]["pole"]) for k in STRUCT_4D + STRUCT_EV]}
    # 3 dropped evanescent (Gt -> 0, i.e. ghat -> eta before the contraction)
    Gd, ledd, _, _ = route1(mutation="drop_evanescent")
    fd, _, _ = fit(Gd)
    cmpd = compare_realized(Gd, base["G2"])
    out["drop_evanescent_Gt"] = {"changes_result": differs(fd), "rejected": not cmpd["agree"],
                                 "reason": f"route 1 with Gt dropped != route 2 (ghat kept): {cmpd['n_mismatches']} "
                                           "mismatches; R6 retention check fails",
                                 "fit_if_accepted": {k: str(v) for k, v in fd.items()}}
    # 4 wrong symmetry factor (S_f = 1/2 for D13)
    Gs = route2(S_f=sp.Rational(1, 2))
    fs, _, _ = fit(Gs)
    cmps = compare_realized(base["G1"], Gs)
    out["wrong_symmetry_factor"] = {"changes_result": differs(fs), "rejected": not cmps["agree"],
                                    "reason": f"route 1 != route 2 with S_f = 1/2: {cmps['n_mismatches']} mismatches"}
    # 5 wrong K'/c ordering (rule-table leg order (c, K', h))
    Go = route2(order=("c", "K", "h"))
    fo, _, _ = fit(Go)
    cmpo = compare_realized(base["G1"], Go)
    out["wrong_K_c_ordering"] = {"changes_result": differs(fo), "rejected": not cmpo["agree"],
                                 "reason": f"route 1 != route 2 with leg order (c, K', h): {cmpo['n_mismatches']} "
                                           "mismatches"}
    for v in out.values():
        v["accepted_as_rejection"] = bool(v["rejected"] and v["changes_result"])
    return out


SIG_DESC = {"S1": "delta^rho_nu p^4", "S2": "p^rho p_nu p^2", "SE": "Gt^rho_nu p^4 (evanescent)"}


def sigma_structures(rho, nu):
    """mixed-index structures of Sigma^rho_nu (upper rho = eta^{rho rho} x lower; the ghost equation 2 i D^rho[G]
    carries the upper index)."""
    f = ETA[rho]
    return [f * eta(rho, nu) * PP ** 2, f * PS[rho] * PS[nu] * PP, f * gt(rho, nu) * PP ** 2]


def ccb_basis():
    """the p14r c.cb counterterm directions (CT.sector_basis('cb','c',4)) as two-point vertices V[cb_rho(-p),
    c^nu(p)] and their exact coordinates on S1, S2."""
    import counterterm_domain as CT
    import feynman as F
    dens = CT.sector_basis("cb", "c", 4)
    keep, _ = CT.independent(dens, [("cb", "c")])
    out = []
    for dn in keep:
        cs = sp.symbols("s1:3")
        eqs = []
        for rho in range(4):
            for nu in range(4):
                v = F.pw_vertex(dn, [{"f": "cb", "c": rho, "k": [-x for x in PS]}, {"f": "c", "c": nu, "k": list(PS)}])
                st = sigma_structures(rho, nu)
                e = sp.expand(v - sum(c * x.xreplace({PP: pp_expr()}) for c, x in zip(cs, st[:2])))
                if e != 0:
                    eqs += sp.Poly(e, *PS).coeffs()
        sol = sp.solve(eqs, cs, dict=True)
        out.append({"density": str(dn)[:300], "S_coordinates": [sp.simplify(sol[0][c]) for c in cs] if sol else None})
    return out


def sigma_pole_in_ccb(Sig):
    """the ghost self-energy (route 2, cbar external) fitted exactly on S1, S2, SE; its 4D pole expressed in the p14r
    c.cb directions; the evanescent pole recorded separately."""
    A, b = [], []
    for pn in P_NUMS:
        for sd in SEEDS:
            gm = IL.realization(pn, sd)
            for rho in range(4):
                for nu in range(4):
                    A.append([IL.realize(x, pn, gm) for x in sigma_structures(rho, nu)])
                    b.append(IL.realize(Sig.get((rho, nu), 0), pn, gm))
    sol, ok = exact_fit(A, b, 3)
    if sol is None:
        return {"fit_exact": False, "pole_local_and_in_p14r_c_cb_span": False}
    ex = {nm: expand_coeff(c) for nm, c in zip(("S1", "S2", "SE"), sol)}
    basis = ccb_basis()
    full = all(bb["S_coordinates"] is not None for bb in basis) and len(basis) == 2
    z = None
    if full:
        M = sp.Matrix([[bb["S_coordinates"][i] for bb in basis] for i in range(2)])
        full = M.rank() == 2
        if full:
            z = [sp.simplify(x) for x in M.LUsolve(sp.Matrix([ex["S1"]["pole"], ex["S2"]["pole"]]))]
    return {"fit_exact": ok, "structures": SIG_DESC,
            "coefficients_exact_d": {k: str(v["exact_d"]) for k, v in ex.items()},
            "pole": {k: str(v["pole"]) for k, v in ex.items()},
            "local": {k: str(v["local"]) for k, v in ex.items()},
            "p14r_c_cb_basis": [{"density": bb["density"], "S_coordinates": [str(c) for c in bb["S_coordinates"]]}
                                for bb in basis],
            "pole_in_p14r_c_cb_coordinates": [str(x) for x in z] if z else None,
            "evanescent_pole_SE": str(ex["SE"]["pole"]),
            "pole_local_and_in_p14r_c_cb_span": bool(ok and full)}


def s(x):
    return str(sp.simplify(x)) if not isinstance(x, str) else x


def _opaque_d_refuses(fit1):
    """the structural R5 safeguard (p15 contract correction): any substitution of d outside dred.substitute_d raises."""
    try:
        sp.sympify(fit1["T2"]).subs(d, 4)
        return False
    except dred.PrematureD4Substitution:
        return True


def main():
    import certio
    t0 = time.time()
    IL.LEDGER.clear()
    base = evaluate()
    s0 = list(IL.LEDGER)
    log("mutations")
    muts = mutations(base)
    log("sigma pole")
    sig = sigma_pole_in_ccb(base["Sigma"])
    exp = base["exp"]
    ev_pole_nonzero = any(exp[k]["pole"] != 0 for k in STRUCT_EV)
    d_matters = any(exp[k]["d_dependence_shift_of_local_part"] != 0 for k in STRUCT_4D)
    controls = {
        "export_sha_pinned": base["pin"]["pinned"],
        "route1_equals_route2_exact_in_d": base["routes_agree"]["agree"],
        "covariant_fit_exact": base["fit_exact"], "fits_agree": base["fits_agree"],
        "pole_local_in_p14r_cK_span": base["basis_full_rank"],
        "ghost_equation_2iD_G_equals_ghost_self_energy": base["ghost_equation"]["agree"],
        "ghost_self_energy_pole_in_p14r_c_cb_span": sig["pole_local_and_in_p14r_c_cb_span"],
        "nonlocal_equals_minus_pole": all(sp.simplify(exp[k]["nonlocal_L_coefficient"] + exp[k]["pole"]) == 0
                                          for k in exp),
        "R5_d_retained": any(sp.sympify(v).has(d) for v in base["fit"].values()),
        "R5_structural_safeguard_active": _opaque_d_refuses(base["fit"]),
        "mutations_all_rejected": all(v["accepted_as_rejection"] for v in muts.values()),
    }
    ok = all(controls.values())
    T_desc = {"T1": "eta_mn p_nu p^2", "T2": "(eta_m nu p_n + eta_n nu p_m) p^2", "T3": "p_m p_n p_nu",
              "E1": "Gt_mn p_nu p^2", "E2": "(Gt_m nu p_n + Gt_n nu p_m) p^2"}
    result = {k: {"structure": T_desc[k], "A_exact_d_times_MB": s(exp[k]["exact_d"]), "UV_pole": s(exp[k]["pole"]),
                  "MSbar_finite": s(exp[k]["finite"]), "nonlocal_coefficient_of_L": s(exp[k]["nonlocal_L_coefficient"]),
                  "local_polynomial": s(exp[k]["local"]),
                  "finite_if_d_set_to_4_first": s(exp[k]["finite_if_d_set_to_4_first"]),
                  "local_shift_from_d_dependence": s(exp[k]["d_dependence_shift_of_local_part"])}
              for k in STRUCT_4D + STRUCT_EV}
    # graph status (one of QC.STATUS_VALUES): 'renormalized' only if EVERY pole is absorbed by a declared counterterm.
    # The p14r contract declares no evanescent counterterm, so a nonzero evanescent pole keeps the graph at
    # 'regulated'; the 4D sector is reported separately.
    status = "renormalized" if ok and not ev_pole_nonzero else "regulated"
    assert status in QC.STATUS_VALUES
    sector_status = {"4D_structures_T1_T3": "renormalized" if ok else "regulated",
                     "evanescent_structures_E1_E2": ("regulated: pole nonzero (E2), recorded and retained (R6); its "
                                                     "counterterm is an evanescent K'.c operator NOT in the p14r 4D "
                                                     "basis (the p14r contract declares no evanescent counterterm: "
                                                     "open contract item, not absorbed)") if ev_pole_nonzero else
                                                    "pole zero"}
    D13_evaluated = {
        "execution": ok,
        "claim": ("D13 (kappa^2 K'.c) evaluated in closed form under the declared prescription: the UV pole of the 4D "
                  "structures is local and in the span of the three p14r c.K' directions (the evanescent E2 pole is "
                  "recorded, not absorbed), MS-bar finite part = nonlocal log(-p^2/mu^2) part + "
                  "local cubic polynomial, two independent routes agree exactly in d, ghost equation verified, "
                  "mutations rejected") if ok else "not established",
        "scope": ("one graph (D13) of the K'.c slot at kappa^2; MS-bar at mu with N_eps = i S_eps/(16 pi^2); external "
                  "momenta in QdS (R2); evanescent Gt structures retained "
                  + ("(their pole is NONZERO: an evanescent K'.c counterterm outside the p14r 4D basis is needed for "
                     "full DRED renormalization)" if ev_pole_nonzero else "(their pole vanishes)")
                  + "; NOT quantum_inputs_evaluated; the slot's identity role is not evaluated (Batch C, D11 M2)")}
    rec = {"landmark": "XVI-P", "revision": QC.REVISION, "deliverable": "P.5 calculation Batch B: D13 (K'.c, kappa^2)",
           "contract_revision": QC.CONTRACT_REVISION,
           "prescription": "frozen p14r P14_DRED_MSbar_FeynmanI0 + S0 (certificates/P15_integral_library.json)",
           "convention": ("G_{(mn) nu}(p) = V_Gamma1[K'_(mn)(-p), c^nu(p)] = kappa^2 * (i S_eps/(16 pi^2)) * Ghat, "
                          "Ghat = sum A_i(d) T_i * MB, MB = Ihat(1,1) = 1/eps + 2 - L + O(eps), "
                          "L = log(-p^2/mu^2 - i0); indices lower (K' slot dual to h_(mn), c^nu -> lower nu); "
                          "p_r lower components; p^2 = eta^{rs} p_r p_s"),
           "export": base["pin"], "prefactor_export": base["prefactor"],
           "status": status, "sector_status": sector_status,
           "evanescent_counterterm_declared_in_p14r": False, "result": result,
           "UV_pole_in_p14r_cK_basis": {"coordinates": [s(x) for x in base["z_pole"]],
                                        "basis": [{"density": b["density"], "T_coordinates": [s(c) for c in b["T_coordinates"]]}
                                                  for b in base["basis"]]},
           "local_polynomial_in_p14r_cK_basis": [s(x) for x in base["z_local"]],
           "nonlocal_in_p14r_cK_basis": [s(x) for x in base["z_nonlocal"]],
           "MSbar_counterterm": ("delta S = - kappa^2 (i S_eps/(16 pi^2)) (1/eps) * sum_k z_k O_k  (O_k the p14r c.K' "
                                 "densities, z = UV_pole coordinates); plus, for the evanescent structures, "
                                 + ("an evanescent counterterm (Gt_mn p_nu p^2, (Gt p + Gt p) p^2) NOT in the p14r basis"
                                    if ev_pole_nonzero else "nothing (pole zero)")),
           "evanescent_pole_nonzero": ev_pole_nonzero,
           "local_ambiguity": ("finite renormalization along the three p14r c.K' directions: G^R -> G^R + kappa^2 "
                               "(i/(16 pi^2)) sum_k f_k O_k; a change of scale mu -> mu' shifts the local polynomial by "
                               "+ A_i(4) log(mu'^2/mu^2) along the UV-pole direction"),
           "renormalization_conditions": ("MS-bar at mu: counterterm = pure pole (P14 normalization condition 0); "
                                          "no lower-degree K'.c contact (mu^2 K' dc) is generated (no scale but mu; pole "
                                          "is cubic in p); u^R_mu (XVI-O) not modified; an alternative momentum "
                                          "subtraction at p^2 = -M^2 differs by the finite renormalization "
                                          "A_i(4) log(M^2/mu^2) - (local MS-bar polynomial) along the same directions"),
           "absorptive_part": "for timelike p^2 > 0: L = log(p^2/mu^2) - i pi, Im Ghat = + pi * sum A_i(4) T_i",
           "d_dependence": {"evanescent_d_terms_matter": bool(d_matters or ev_pole_nonzero),
                            "local_shift_from_d_dependence_T": {k: result[k]["local_shift_from_d_dependence"]
                                                                for k in STRUCT_4D},
                            "evanescent_structure_poles": {k: result[k]["UV_pole"] for k in STRUCT_EV},
                            "statement": ("the (d-4) x pole terms change the local finite polynomial (premature d = 4 "
                                          "gives a different MS-bar finite part); the difference is local and lies in "
                                          "the p14r c.K' span (a scheme-type finite renormalization), so it matters "
                                          "for the finite part in the declared scheme" if d_matters else
                                          "the (d-4) x pole terms vanish for the 4D structures")},
           "authorised_d_substitutions": dict(dred.D_PROVENANCE),
           "independent_cross_check_route": ("route 2: integrand regenerated from the rule tables (feynman.pw_vertex; "
                                             "no exported data) and evaluated by Feynman parameters with d symbolic "
                                             "(integrals.fp_two_point; no Gram/PV reduction, no S0); agrees with route "
                                             "1 (frozen export -> dred Pipeline) exactly in d"),
           "scaleless_rule_applications": s0, "dred_ledger_reductions_introducing_d": sum(1 for x in base["ledger"]
                                                                                          if x.get("introduces_d")),
           "controls": controls,
           "route_comparison": base["routes_agree"], "fit_equations": base["fit_equations"],
           "ghost_equation": {**base["ghost_equation"],
                              "statement": "Sigma_{rho nu}(p) [one-loop ghost self-energy, same topology, evaluated "
                                           "by route 2 from the cbar.c.h vertex] == 2 i D^rho_p[G_{.. nu}] with "
                                           "D^rho T = d_s T^{rho s} - 1/2 d^rho tr T (linear de Donder gauge: ghost "
                                           "equation); exact in d on the faithful Gt realization"},
           "ghost_self_energy_pole": sig,
           "mutations": muts, "mutations_all_rejected": controls["mutations_all_rejected"],
           "D13_evaluated": D13_evaluated, "loop_evaluations_performed": True,
           "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_D13.json", rec)
    print(json.dumps({"D13_evaluated": ok, "status": status, "controls": controls,
                      "pole_T": {k: result[k]["UV_pole"] for k in result},
                      "local_T": {k: result[k]["local_polynomial"] for k in result},
                      "z_pole": rec["UV_pole_in_p14r_cK_basis"]["coordinates"],
                      "mutations": {k: [v["changes_result"], v["rejected"]] for k, v in muts.items()},
                      "timing": base["timing"], "seconds": rec["seconds"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
