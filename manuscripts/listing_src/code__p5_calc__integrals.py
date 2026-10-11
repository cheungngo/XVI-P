#!/usr/bin/env python3
"""XVI-P p15: certified one-loop scalar-integral library (A0, B0, massless two-point family, ghat tensor reduc
  +> tion)
under the FROZEN p14r prescription (DRED R1-R6 of code/p5_entry/dred.py, Feynman +i0, MS-bar).

Normalisation.  Every integral  I = mu^{2 eps} int d^d l/(2 pi)^d (...)  (Minkowski, eta = +,-,-,-, all denomi
  +> nators
q^2 - m^2 + i0, d = 4 - 2 eps) is returned in units of  N_eps = i S_eps/(16 pi^2),  S_eps = (4 pi)^eps e^{-gam
  +> ma_E eps}:
I = N_eps * Ihat.  MS-bar (pole in 1/eps - gamma_E + log 4 pi) == drop the 1/eps poles of Ihat; finite part = 
  +> eps^0
coefficient of Ihat.  L := log(-p^2/mu^2 - i0),  Lm := log(m^2/mu^2).

Exact formulas (d symbolic):
  T(k,n;m)   = mu^{2eps} int (l^2)^k/(l^2-m^2)^n
             -> Ihat = (-1)^{n+k} e^{gamma eps} Gamma(k+d/2) Gamma(n-k-d/2)/(Gamma(d/2) Gamma(n)) (m^2)^{2+k-n
  +> } e^{-eps Lm}
  I(n1,n2)   = mu^{2eps} int 1/[(l^2)^{n1} ((l-p)^2)^{n2}]  (massless)
             -> Ihat = (-1)^{n1+n2} e^{gamma eps} G(n1,n2) (-p^2)^{2-n1-n2} e^{-eps L},
                G = Gamma(d/2-n1) Gamma(d/2-n2) Gamma(n1+n2-d/2) / (Gamma(n1) Gamma(n2) Gamma(d-n1-n2))
  A0(m) = T(0,1;m),  B0(p^2;0,0) = I(1,1) =: MB  (the only massless two-point master).

S0 SCALELESS RULE (explicit, stated, part of the declared prescription; applied ONLY to integrals with no scal
  +> e):
  int d^d l (l^2)^k / (l^2)^nu  (no mass, no external momentum in the integrand after shift)  :=  0.
  UV/IR reading (Euclidean radial split at an arbitrary Lambda; omega := 4 + 2k - 2 nu, s := d + 2k - 2 nu):
    IR part int_0^Lambda r^{s-1} dr = +Lambda^s/s (converges for Re s > 0), UV part int_Lambda^oo = -Lambda^s/
  +> s (converges
    for Re s < 0); each is continued in d and the sum is 0.
    omega = 0 (logarithmic): s = -2 eps, the two parts are -1/(2 eps_UV) and +1/(2 eps_IR) times Omega_d/(2pi)
  +> ^d, i.e.
      the zero is (1/eps_UV - 1/eps_IR)-type: a UV pole cancelled by an IR pole;
    omega > 0 (UV power divergence): neither part has a pole at d = 4 (IR part finite, UV part a pure Lambda^o
  +> mega
      power); the zero discards a power divergence; NO 1/eps pole on either side;
    omega < 0 (IR power divergence): mirror image.
  A ledger records omega and this classification for EVERY application.
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
import dred  # noqa: E402   (p14r DRED rules R1-R6; p15 contract correction = structural R5 safeguard only)

d, eps = dred.d, dred.eps
ETA = dred.ETA
L = sp.Symbol("L")            # log(-p^2/mu^2 - i0)
Lm = sp.Symbol("Lm")          # log(m^2/mu^2)
PP = sp.Symbol("p.p")          # p^2 (same symbol as the frozen contraction engine)
MSQ = sp.Symbol("m2")          # IR-regulator mass squared (analysis only; the declared action is massless)
MB = sp.Symbol("MB")           # massless bubble master Ihat(1,1) (symbol; exact value master_exact())
G_ = sp.gamma


class ScalelessRuleMisuse(Exception):
    """S0 requested for an integral that carries a scale."""


LEDGER = []


def scaleless(k, nu, context, has_scale=False):
    """S0: int d^d l (l^2)^k/(l^2)^nu := 0, with the UV/IR classification recorded."""
    if has_scale:
        raise ScalelessRuleMisuse(f"S0 applied to an integral with a scale ({context})")
    omega = 4 + 2 * k - 2 * nu
    kind = "logarithmic: (1/eps_UV - 1/eps_IR) cancellation" if omega == 0 else (
        f"UV power divergence Lambda^{omega}: no pole on either side at d = 4" if omega > 0 else
        f"IR power divergence Lambda^{omega}: no pole on either side at d = 4")
    LEDGER.append({"context": context, "k": int(k), "nu": int(nu), "omega": int(omega), "class": kind})
    return sp.Integer(0)


def lambda_split(k, nu):
    """symbolic radial split (Euclidean, per unit solid angle): IR + UV = 0; poles at d = 4 iff omega = 0."""
    Lam = sp.Symbol("Lambda", positive=True)
    s = d + 2 * k - 2 * nu
    ir, uv = Lam ** s / s, -Lam ** s / s
    at4 = dred.substitute_d(s, 4, "integrals.lambda_split: power-counting exponent at d = 4 (no integrand)")
    def pole(e):
        ser = sp.series(dred.substitute_d(e, 4 - 2 * eps, "integrals.lambda_split: Laurent expansion"), eps, 0
  +> ,
                        1).removeO()
        return sp.simplify(ser.coeff(eps, -1))
    return {"omega": int(4 + 2 * k - 2 * nu), "s_at_d4": int(at4), "sum_zero": sp.simplify(ir + uv) == 0,
            "IR_part": str(ir), "UV_part": str(uv),
            "IR_pole_at_d4": str(pole(ir)) if at4 == 0 else "0 (no pole)",
            "UV_pole_at_d4": str(pole(uv)) if at4 == 0 else "0 (no pole)"}


# ------------------------------------------------------------------------------------------------ exact maste
  +> rs
def G2(n1, n2):
    return G_(d / 2 - n1) * G_(d / 2 - n2) * G_(n1 + n2 - d / 2) / (G_(n1) * G_(n2) * G_(d - n1 - n2))


def master_exact():
    """Ihat(1,1) exact in d (with eps = (4-d)/2)."""
    e = (4 - d) / 2
    return sp.exp(sp.EulerGamma * e) * G2(1, 1) * sp.exp(-e * L)


def bubble_hat(n1, n2, context="I(n1,n2)"):
    """Ihat(n1,n2) for integer n1, n2: scaleless (S0) if n1 <= 0 or n2 <= 0; otherwise R(d) * MB with R ration
  +> al."""
    if n1 <= 0 or n2 <= 0:
        # after the shift l -> l + p (if n1 <= 0) the integrand is a polynomial in l over (l^2)^{n}: scaleless
        n = n2 if n1 <= 0 else n1
        return scaleless(0, n, context + f" [I({n1},{n2}) -> polynomial/(l^2)^{n}]")
    if (n1, n2) == (1, 1):
        return MB
    raise NotImplementedError("only I(1,1) and scaleless members are needed for Batch A/B")


def tadpole_hat(k, n, msq=MSQ):
    """T(k,n;m) exact in d (massive; used for the IR-regulator analysis and as A0)."""
    e = (4 - d) / 2
    return ((-1) ** (n + k) * sp.exp(sp.EulerGamma * e) * G_(k + d / 2) * G_(n - k - d / 2) / (G_(d / 2) * G_(
  +> n))
            * msq ** (2 + k - n) * sp.exp(-e * Lm))


def laurent(expr, order=1):
    e = sp.expand(dred.substitute_d(expr, 4 - 2 * eps, "integrals.laurent: d = 4 - 2 eps after all contraction
  +> s"))
    ser = sp.series(e, eps, 0, order + 1).removeO()
    return {k: sp.simplify(ser.coeff(eps, k)) for k in range(-2, order + 1)}


_MBSER = {}


def master_series(order=1):
    if order not in _MBSER:
        _MBSER[order] = laurent(master_exact(), order)
    return _MBSER[order]


# ------------------------------------------------------------------------------------------------ two-point J
  +>  values
def J_two_point(a, b, context="J"):
    """J[a,b] = int (l.l)^a (l.p)^b / (D1 D2), D1 = l^2, D2 = (l-p)^2: l.p = (D1 + p^2 - D2)/2, every member w
  +> ith a
    cancelled propagator is scaleless (S0); returns R(d, p^2) * MB."""
    D1, D2 = sp.symbols("D1 D2")
    num = sp.expand(D1 ** a * ((D1 + PP - D2) / 2) ** b)
    tot = 0
    for (i, j), cf in sp.Poly(num, D1, D2).terms():
        tot += cf * bubble_hat(1 - i, 1 - j, context + f"[{a},{b}]")
    return sp.expand(tot)


def J_values(tag, pairs):
    return {sp.Symbol(f"J_{tag}[{a},{b}]"): J_two_point(a, b, f"J_{tag}") for (a, b) in pairs}


# ------------------------------------------------------------------------------------------------ Feynman-par
  +> ameter route
def _matchings(items):
    if not items:
        yield []
        return
    a = items[0]
    for k in range(1, len(items)):
        rest = items[1:k] + items[k + 1:]
        for m in _matchings(rest):
            yield [(a, items[k])] + m


def ghat(r, s):
    return (ETA[r] if r == s else 0) - dred.Gt(r, s)


def sym_integrate(comps):
    """k_{r1}..k_{rn} -> coefficient of (k^2)^{n/2} under symmetric integration in QdS (k in QdS, ghat project
  +> ions)."""
    n = len(comps)
    if n % 2:
        return sp.Integer(0)
    if n == 0:
        return sp.Integer(1)
    j = n // 2
    den = sp.Mul(*[d + 2 * i for i in range(j)])
    tot = 0
    for m in _matchings(list(range(n))):
        tot += sp.Mul(*[ghat(comps[a], comps[b]) for a, b in m])
    return sp.expand(tot / den)


def fp_ratio(j, alpha, beta):
    """[int_0^1 dx x^alpha (1-x)^beta Ihat_j(x)] / MB exact (rational in d): Ihat_j(x) is the hat of
    int (k^2)^j/(k^2 - Delta)^2, Delta = -x(1-x) p^2."""
    rf = sp.rf
    h = d / 2
    return sp.factor((-1) ** j * (-PP) ** j * rf(h, j) / rf(2 - j - h, j)
                     * rf(h - 1, alpha + j) * rf(h - 1, beta + j) / rf(d - 2, alpha + beta + 2 * j))


def fp_two_point(poly, lsym, psym):
    """Feynman-parameter evaluation of int poly(l, p)/(D1 D2) (D1 = l^2, D2 = (l-p)^2) as R(d) * MB, R rationa
  +> l;
    l = k + x p (x D2 + (1-x) D1 = k^2 + x(1-x) p^2); symmetric integration in QdS; NO scaleless rule used."""
    x = sp.Symbol("x")
    ks = sp.symbols("k0:4")
    sub = {lsym[r]: ks[r] + x * psym[r] for r in range(4)}
    e = sp.expand(sp.sympify(poly).xreplace(sub))
    if e == 0:
        return sp.Integer(0)
    P = sp.Poly(e, *ks)
    tot = 0
    for mon, cf in P.terms():
        comps = sum(([r] * m for r, m in enumerate(mon)), [])
        si = sym_integrate(comps)
        if si == 0:
            continue
        j = len(comps) // 2
        Px = sp.Poly(sp.expand(cf * si), x)
        for (ax,), cx in Px.terms():
            # x^ax with (1-x)^0
            tot += cx * fp_ratio(j, ax, 0)
    return sp.expand(tot) * MB


# ------------------------------------------------------------------------------------------------ faithful Gt
  +>  realization
def realization(p_num, seed):
    """Gt -> (4-d) M with M symmetric (lower indices), M_rs eta^{ss} p_s = 0, eta^{rs} M_rs = 1: a faithful mo
  +> del of
    the R1/R2/R4 relations for expressions linear in Gt (tr Gt = 4-d, Gt.p = 0)."""
    import random
    rnd = random.Random(seed)
    pu = [ETA[r] * p_num[r] for r in range(4)]                 # p^r
    basis = []
    for _ in range(12):
        v = [sp.Rational(rnd.randint(-9, 9), rnd.randint(1, 5)) for _ in range(4)]
        # project out p:  v.p = sum eta^{rr} v_r p_r ; make v.p = 0 by adjusting with a vector u with u.p != 0
        vp = sum(ETA[r] * v[r] * p_num[r] for r in range(4))
        pp = sum(ETA[r] * p_num[r] ** 2 for r in range(4))
        v = [v[r] - vp / pp * p_num[r] for r in range(4)]
        basis.append(v)
        if len(basis) == 3:
            break
    lam = [sp.Rational(rnd.randint(1, 9), rnd.randint(1, 4)) for _ in basis]
    M = sp.zeros(4, 4)
    for l_, v in zip(lam, basis):
        M += l_ * sp.Matrix(4, 1, v) * sp.Matrix(1, 4, v)
    tr = sum(ETA[r] * M[r, r] for r in range(4))
    assert tr != 0
    M = M / tr
    assert all(sp.simplify(sum(M[r, s] * pu[s] for s in range(4))) == 0 for r in range(4))
    return {sp.Symbol(f"Gt_{min(r, s)}{max(r, s)}"): (4 - d) * M[r, s] for r in range(4) for s in range(4)}


def realize(expr, p_num, gt_map, psym=None):
    psym = psym or sp.symbols("p0:4")
    pp = sum(ETA[r] * p_num[r] ** 2 for r in range(4))
    rep = {psym[r]: p_num[r] for r in range(4)}
    rep[PP] = pp
    rep.update(gt_map)
    return sp.expand(sp.sympify(expr).xreplace(rep))


# ------------------------------------------------------------------------------------------------ certificati
  +> on
def _numeric_master(dval):
    """Euclidean numerical check: int d^d l_E/(2pi)^d 1/(l^2 (l-p)^2) at p_E^2 = 1, non-integer d (convergent 
  +> for
    2 < d < 4), by radial x polar integration, vs the Gamma formula."""
    import mpmath as mp
    mp.mp.dps = 20
    D = mp.mpf(dval)
    omega_dm2 = 2 * mp.pi ** ((D - 1) / 2) / mp.gamma((D - 1) / 2)       # area of S^{d-2}
    def f(r, th):
        den = (r - mp.cos(th)) ** 2 + mp.sin(th) ** 2
        return r ** (D - 3) * mp.sin(th) ** (D - 2) / den if den else mp.mpf(0)

    def radial(th):
        c = mp.cos(th)
        pts = [0, c, 2, mp.inf] if c > 0 else [0, 1, mp.inf]
        return mp.quad(lambda r: f(r, th), pts)
    val = mp.quad(radial, [0, mp.mpf(1) / 100, mp.mpf(1) / 10, mp.pi])
    num = omega_dm2 * val / (2 * mp.pi) ** D
    exact = mp.gamma(2 - D / 2) * mp.gamma(D / 2 - 1) ** 2 / mp.gamma(D - 2) / (4 * mp.pi) ** (D / 2)
    return float(num), float(exact)


def _numeric_tadpole(dval, k=0):
    """Euclidean: int d^d l_E/(2pi)^d (l^2)^k/(l^2+1), convergent for 0 < d + 2k < 2, vs the Gamma formula."""
    import mpmath as mp
    mp.mp.dps = 20
    D = mp.mpf(dval)
    area = 2 * mp.pi ** (D / 2) / mp.gamma(D / 2)
    val = mp.quad(lambda r: r ** (D - 1 + 2 * k) / (r * r + 1), [0, 1, mp.inf])
    num = area * val / (2 * mp.pi) ** D
    exact = mp.gamma(k + D / 2) * mp.gamma(1 - k - D / 2) / mp.gamma(D / 2) / (4 * mp.pi) ** (D / 2)
    return float(num), float(exact)


def certify():
    t0 = time.time()
    out = {}
    s = master_series(1)
    out["B0_massless_laurent"] = {"pole": str(s[-1]), "finite": str(s[0]), "order_eps": str(s[1]),
                                  "ok": sp.simplify(s[-1] - 1) == 0 and sp.simplify(s[0] - (2 - L)) == 0
                                  and s[-2] == 0}
    a0 = laurent(tadpole_hat(0, 1), 0)
    out["A0_laurent"] = {"pole": str(a0[-1]), "finite": str(a0[0]),
                         "ok": sp.simplify(a0[-1] - MSQ) == 0 and sp.simplify(a0[0] - MSQ * (1 - Lm)) == 0}
    nb = [_numeric_master(x) for x in (2.6, 3.3, 3.7)]
    out["B0_exact_d_numeric"] = {"d_values": [2.6, 3.3, 3.7], "numeric_vs_formula": nb,
                                 "ok": all(abs(a - b) < 1e-8 * abs(b) for a, b in nb)}
    nt = [_numeric_tadpole(x, 0) for x in (0.7, 1.5)] + [_numeric_tadpole(x, 1) for x in (-0.6,)]
    out["T_exact_d_numeric"] = {"cases": ["d=0.7,k=0", "d=1.5,k=0", "d=-0.6,k=1"], "numeric_vs_formula": nt,
                                "ok": all(abs(a - b) < 1e-8 * abs(b) for a, b in nt)}
    # tensor reduction (frozen dred R3/R4) + J values (S0)  ==  Feynman parameters (no S0), exact in d, all co
  +> mponents
    rules = dred.Rules()
    lsym, psym = sp.symbols("l0:4"), sp.symbols("p0:4")
    p_nums = [[sp.Integer(3), sp.Integer(1), sp.Integer(-2), sp.Integer(5)],
              [sp.Rational(7, 2), sp.Integer(-1), sp.Integer(4), sp.Integer(2)]]
    Jv = J_values("LIB", [(a, b) for a in range(3) for b in range(5)])
    bad, checked = [], 0
    for n in range(0, 4):
        for comps in itertools.combinations_with_replacement(range(4), n):
            r1 = dred.lift_reduce_monomial(list(comps), True, rules, "LIB")
            r1 = sp.expand(r1.xreplace(Jv))
            r2 = fp_two_point(sp.Mul(*[lsym[c] for c in comps]), lsym, psym)
            for pn in p_nums:
                for seed in (1, 2):
                    gm = realization(pn, seed)
                    diff = sp.simplify((realize(r1, pn, gm) - realize(r2, pn, gm)) / MB)
                    checked += 1
                    if diff != 0:
                        bad.append({"comps": list(comps), "p": [str(x) for x in pn], "diff": str(diff)})
    out["tensor_reduction_vs_feynman_parameters"] = {"ranks": [0, 1, 2, 3], "checks": checked, "mismatches": b
  +> ad[:5],
                                                     "n_mismatches": len(bad), "ok": not bad,
                                                     "note": "route 1 uses S0 for every cancelled propagator; 
  +> route 2 "
                                                             "uses none (Delta != 0): agreement certifies S0 o
  +> n this family"}
    out["J_table"] = {str(k): str(v) for k, v in Jv.items() if v != 0}
    out["scaleless_rule"] = {"statement": "S0: int d^d l (l^2)^k/(l^2)^nu := 0 when the integrand carries no s
  +> cale",
                             "lambda_split": {f"omega={4 + 2 * k - 2 * nu}": lambda_split(k, nu)
                                              for (k, nu) in ((1, 1), (0, 1), (0, 2), (0, 3))},
                             "misuse_guard": _misuse_guard()}
    # mass-regulator limit of the scaleless members: T(k,1;m) -> 0 as m -> 0 for Re d > 2 - 2k
    out["mass_regulator_limit"] = {f"k={k}": {"exact": str(tadpole_hat(k, 1)),
                                              "m2_power": str(sp.simplify(d / 2 + k - 1)),
                                              "vanishes_as_m_to_0_for": f"Re d > {2 - 2 * k}"} for k in (0, 1,
  +>  2)}
    out["i0"] = {"L": "log(-p^2/mu^2 - i0) = log|p^2/mu^2| - i pi theta(p^2)  (Feynman +i0)",
                 "Lm": "log(m^2/mu^2) (m^2 - i0)"}
    out["ok"] = all(v.get("ok", True) for v in out.values() if isinstance(v, dict))
    out["seconds"] = round(time.time() - t0, 1)
    return out


def _misuse_guard():
    try:
        scaleless(0, 1, "A0 with m != 0 (mutation: S0 on a massive tadpole)", has_scale=True)
        return {"rejected": False}
    except ScalelessRuleMisuse as exc:
        return {"rejected": True, "reason": str(exc)}


def main():
    import p15_conventions as QC
    import certio
    LEDGER.clear()
    res = certify()
    rec = {"landmark": "XVI-P", "revision": QC.REVISION, "deliverable": "P.5 calculation: one-loop integral li
  +> brary",
           "prescription": "frozen p14r P14_DRED_MSbar_FeynmanI0 (DRED R1-R6, Feynman +i0, MS-bar); S0 stated 
  +> explicitly",
           "normalisation": "I = N_eps * Ihat, N_eps = i S_eps/(16 pi^2), S_eps = (4 pi)^eps e^{-gamma_E eps},
  +>  mu^{2 eps}; "
                            "MS-bar = drop the poles of Ihat",
           "library_certified": bool(res["ok"]), **res, "S0_ledger_size": len(LEDGER)}
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_integral_library.json", rec)
    print(json.dumps({"library_certified": rec["library_certified"], "seconds": res["seconds"],
                      "checks": {k: v.get("ok") for k, v in res.items() if isinstance(v, dict) and "ok" in v}}
  +> , indent=1))
    return 0 if rec["library_certified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
