#!/usr/bin/env python3
"""XVI-P p14 control W1: brute-force 0-dimensional Wick/Berezin shadow models.

For every graph topology the corresponding 0-dimensional model (same vertex shapes, same leg orders, same field
statistics; random exact rational couplings; 2 ghost modes so that index order and transposition errors are visible)
is integrated EXACTLY:  bosons by Gaussian moments generated from int e^{i m q^2/2 + J q}, ghosts by Berezin
integration in a finite Grassmann algebra, Gamma_1 = -i log <e^{i S_int}> (quantum-quadratic S_int => one loop, 1PI).
The target Gamma_1 coefficient is read off with the SAME ordered extraction as feynman.pw_vertex and compared with
the declared rule (symmetry factor, closed-ghost-loop sign, external-order sign, i-factors, Delta = i V2^{-1},
<c cbar> = i M0^{-1}).  Nothing here is fitted: the rule table is an input, the Berezin/Wick value is computed.
"""
from __future__ import annotations
import itertools
import random
import sympy as sp

I = sp.I


class GA:
    """finite superalgebra: {sorted tuple of odd generator ids: sympy coefficient (even symbols allowed)}"""
    __slots__ = ("t",)

    def __init__(self, t=None):
        self.t = {k: v for k, v in (t or {}).items() if v != 0}

    @staticmethod
    def even(x):
        return GA({(): sp.sympify(x)})

    @staticmethod
    def odd(g):
        return GA({(g,): sp.Integer(1)})

    def __add__(self, o):
        r = dict(self.t)
        for k, v in o.t.items():
            r[k] = sp.expand(r.get(k, 0) + v)
        return GA(r)

    def scale(self, x):
        return GA({k: sp.expand(v * x) for k, v in self.t.items()})

    def __mul__(self, o):
        if not isinstance(o, GA):
            return self.scale(o)
        r = {}
        for k1, v1 in self.t.items():
            for k2, v2 in o.t.items():
                if set(k1) & set(k2):
                    continue
                seq = list(k1 + k2)
                sgn = 1
                for i in range(len(seq)):
                    for j in range(len(seq) - 1 - i):
                        if seq[j] > seq[j + 1]:
                            seq[j], seq[j + 1] = seq[j + 1], seq[j]
                            sgn = -sgn
                k = tuple(seq)
                r[k] = sp.expand(r.get(k, 0) + sgn * v1 * v2)
        return GA(r)

    def dL(self, g):
        """left derivative wrt odd generator g"""
        r = {}
        for k, v in self.t.items():
            if g in k:
                i = k.index(g)
                nk = k[:i] + k[i + 1:]
                r[nk] = sp.expand(r.get(nk, 0) + (-1) ** i * v)
        return GA(r)

    def d_even(self, s):
        return GA({k: sp.diff(v, s) for k, v in self.t.items()})

    def at(self, subs):
        return GA({k: sp.expand(v.subs(subs)) for k, v in self.t.items()})

    def tcoeff(self, t, n):
        return GA({k: sp.expand(v).coeff(t, n) for k, v in self.t.items()})


def ga_exp(X, t, order):
    out, term = GA.even(1), GA.even(1)
    for n in range(1, order + 1):
        term = (term * X).scale(sp.Rational(1, n))
        term = GA({k: sp.expand(sum(sp.expand(v).coeff(t, j) * t ** j for j in range(order + 1)))
                   for k, v in term.t.items()})
        out = out + term
    return out


def ga_log1p(X, t, order):
    out, pw = GA(), GA.even(1)
    for n in range(1, order + 1):
        pw = pw * X
        pw = GA({k: sp.expand(sum(sp.expand(v).coeff(t, j) * t ** j for j in range(order + 1)))
                 for k, v in pw.t.items()})
        out = out + pw.scale(sp.Rational((-1) ** (n + 1), n))
    return out


def boson_moments(m, nmax):
    """<q^n> under e^{i m q^2/2}: generated from Z(J)/Z(0) = exp(i J^2/(2m)) (completing the square)."""
    J = sp.Symbol("J")
    gen = sp.series(sp.exp(I * J ** 2 / (2 * m)), J, 0, nmax + 1).removeO()
    return {n: sp.simplify(sp.diff(gen, J, n).subs(J, 0)) for n in range(nmax + 1)}


def expect(F, quantum_odd, S0, bosons, nmax_q=8):
    """<F> = Berezin_quantum(F e^{iS0}) / Berezin_quantum(e^{iS0}), then Gaussian boson moments.
    quantum odd generators have the LARGEST ids (background odd generators sort to the left)."""
    full = tuple(sorted(quantum_odd))

    def ber(G):
        r = {}
        for k, v in G.t.items():
            qpart = tuple(x for x in k if x in quantum_odd)
            if qpart == full:
                bg = tuple(x for x in k if x not in quantum_odd)
                assert k == bg + full
                r[bg] = sp.expand(r.get(bg, 0) + v)
        return GA(r)
    E0 = ga_exp(S0.scale(I), sp.Symbol("_u"), len(full)).at({sp.Symbol("_u"): 1}) if S0 is not None else GA.even(1)
    num = ber(F * E0) if quantum_odd else F
    den = ber(E0) if quantum_odd else GA.even(1)
    d0 = den.t.get((), 0)
    assert len(den.t) == 1 and d0 != 0
    num = num.scale(1 / d0)
    for q, m in bosons:
        mom = boson_moments(m, nmax_q)
        r = {}
        for k, v in num.t.items():
            P = sp.Poly(sp.expand(v), q)
            r[k] = sp.expand(sum(c * mom[e[0]] for e, c in P.terms()))
        num = GA(r)
    return num


def gamma1(S_int, t, order, quantum_odd, S0, bosons):
    E = expect(ga_exp(S_int.scale(I), t, order), quantum_odd, S0, bosons, nmax_q=2 * order + 2)
    X = E + GA.even(-1)
    return ga_log1p(X, t, order).scale(-I)


def ordered(F, legs):
    """same ordered extraction as feynman.pw_vertex: leg 1 innermost (leftmost factor); even legs = d/dsymbol."""
    G = F
    for kind, x in legs:
        G = G.dL(x) if kind == "odd" else G.d_even(x)
    return G


def _rq(rng):
    v = 0
    while v == 0:
        v = sp.Rational(rng.randint(-9, 9), rng.randint(1, 5))
    return v


def run_shadows(rules, seed=1414):
    """returns {graph: {"berezin_or_wick": value, "rule": value, "agree": bool}}"""
    rng = random.Random(seed)
    t = sp.Symbol("t")
    m, g, ga, gb = sp.symbols("m g g_a g_b", nonzero=True)
    Ha, Hb, q = sp.symbols("H_a H_b q")
    out = {}
    G = rules["graphs"]
    # ---------- bosonic topologies ----------
    def boson_case(name, S_int, order, target_bg, vertices, nprop):
        val = ordered(gamma1(S_int, t, order, [], None, [(q, m)]).tcoeff(t, order), target_bg).t.get((), 0)
        val = sp.simplify(val.subs({Ha: 0, Hb: 0}))
        delta = I / m                                   # Delta = i V2^{-1}, V2[q,q] = m
        rule = G[name]["S_f"] * G[name]["loop_sign"] * sp.Mul(*[I * v for v in vertices]) * delta ** nprop
        rule_gamma = sp.simplify(-I * rule)             # i Gamma_1^{(n)} = rule
        out[name] = {"value": str(val), "rule": str(rule_gamma), "agree": sp.simplify(val - rule_gamma) == 0}
    S_bub = GA.even(t * (ga / 2 * Ha * q ** 2 + gb / 2 * Hb * q ** 2))
    S_quart = GA.even(t * g / 2 * Ha * Hb * q ** 2)
    S_tad = GA.even(t * ga / 2 * Ha * q ** 2)
    V = lambda S, legs: sp.simplify(ordered(S.tcoeff(t, 1), legs).t.get((), 0))   # noqa: E731
    for name, (S, order, bg, verts, nprop) in {
        "D01": (S_bub, 2, [("even", Ha), ("even", Hb)],
                [V(S_bub, [("even", Ha), ("even", q), ("even", q)]), V(S_bub, [("even", Hb), ("even", q), ("even", q)])], 2),
        "D11": (S_bub, 2, [("even", Ha), ("even", Hb)],
                [V(S_bub, [("even", Ha), ("even", q), ("even", q)]), V(S_bub, [("even", Hb), ("even", q), ("even", q)])], 2),
        "D02": (S_quart, 1, [("even", Ha), ("even", Hb)],
                [V(S_quart, [("even", Ha), ("even", Hb), ("even", q), ("even", q)])], 1),
        "D12": (S_quart, 1, [("even", Ha), ("even", Hb)],
                [V(S_quart, [("even", Ha), ("even", Hb), ("even", q), ("even", q)])], 1),
        "D14a": (S_tad, 1, [("even", Ha)], [V(S_tad, [("even", Ha), ("even", q), ("even", q)])], 1),
        "D14c": (S_tad, 1, [("even", Ha)], [V(S_tad, [("even", Ha), ("even", q), ("even", q)])], 1),
    }.items():
        boson_case(name, S, order, bg, verts, nprop)
    # ---------- ghost topologies (2 modes; odd ids: background 0..3, quantum c=10,11  cb=20,21) ----------
    n = 2
    c = [10 + i for i in range(n)]
    cb = [20 + i for i in range(n)]
    M = sp.Matrix(n, n, lambda i, j: _rq(rng))
    while M.det() == 0:
        M = sp.Matrix(n, n, lambda i, j: _rq(rng))
    S0 = GA()
    for r_ in range(n):
        for u in range(n):
            S0 = S0 + (GA.odd(cb[r_]) * GA.odd(c[u])).scale(M[r_, u])          # cbar_rho M c^mu (cbar left)
    M0 = sp.Matrix(n, n, lambda r_, u: ordered(S0, [("odd", cb[r_]), ("odd", c[u])]).t.get((), 0))
    Dgh = I * M0.inv()                                    # rule: <c^mu cbar_rho> = i (M0^{-1})_{mu rho}
    # direct Berezin propagator check
    dir_prop = sp.Matrix(n, n, lambda u, r_: expect(GA.odd(c[u]) * GA.odd(cb[r_]), c + cb, S0, []).t.get((), 0))
    out["ghost_propagator"] = {"berezin": str(dir_prop), "rule": str(Dgh), "agree": (dir_prop - Dgh).applyfunc(sp.simplify) == sp.zeros(n, n)}
    Ga = sp.Matrix(n, n, lambda i, j: _rq(rng))
    Gb = sp.Matrix(n, n, lambda i, j: _rq(rng))
    Sg = GA()
    for r_ in range(n):
        for u in range(n):
            Sg = Sg + (GA.odd(cb[r_]) * GA.odd(c[u])).scale(t * (Ga[r_, u] * Ha + Gb[r_, u] * Hb))
    Va = sp.Matrix(n, n, lambda r_, u: ordered(Sg.tcoeff(t, 1), [("odd", cb[r_]), ("odd", c[u]), ("even", Ha)]).t.get((), 0))
    Vb = sp.Matrix(n, n, lambda r_, u: ordered(Sg.tcoeff(t, 1), [("odd", cb[r_]), ("odd", c[u]), ("even", Hb)]).t.get((), 0))
    g3 = gamma1(Sg, t, 2, c + cb, S0, [])
    val03 = sp.simplify(ordered(g3.tcoeff(t, 2), [("even", Ha), ("even", Hb)]).t.get((), 0).subs({Ha: 0, Hb: 0}))
    tr = sum((I * Va)[r_, u] * Dgh[u, s_] * (I * Vb)[s_, w] * Dgh[w, r_]
             for r_ in range(n) for u in range(n) for s_ in range(n) for w in range(n))
    rule03 = sp.simplify(-I * G["D03"]["loop_sign"] * G["D03"]["S_f"] * tr)
    out["D03"] = {"value": str(val03), "rule": str(rule03), "agree": sp.simplify(val03 - rule03) == 0}
    g14 = gamma1(Sg, t, 1, c + cb, S0, [])
    val14 = sp.simplify(ordered(g14.tcoeff(t, 1), [("even", Ha)]).t.get((), 0).subs({Ha: 0, Hb: 0}))
    tr1 = sum((I * Va)[r_, u] * Dgh[u, r_] for r_ in range(n) for u in range(n))
    rule14 = sp.simplify(-I * G["D14b"]["loop_sign"] * G["D14b"]["S_f"] * tr1)
    out["D14b"] = {"value": str(val14), "rule": str(rule14), "agree": sp.simplify(val14 - rule14) == 0}
    # ---------- D13: external odd source K_j (ids 0,1) and external ghost theta_nu (ids 2,3) ----------
    K = [0, 1]
    th = [2, 3]
    al = sp.Matrix(n, n, lambda i, j: _rq(rng))
    be = sp.Matrix(n, n, lambda i, j: _rq(rng))
    S13 = GA()
    for j in range(n):
        for u in range(n):
            S13 = S13 + (GA.odd(K[j]) * GA.odd(c[u])).scale(t * al[j, u] * q)       # K' c h   (K' left of c)
    for r_ in range(n):
        for nu in range(n):
            S13 = S13 + (GA.odd(cb[r_]) * GA.odd(th[nu])).scale(t * be[r_, nu] * q)  # cbar c_ext h
    order_K = rules["leg_order"]["K_c_h"]
    def legsK(j, u):
        d = {"K": ("odd", K[j]), "c": ("odd", c[u]), "h": ("even", q)}
        return [d[x] for x in order_K]
    VK = sp.Matrix(n, n, lambda j, u: ordered(S13.tcoeff(t, 1), legsK(j, u)).t.get((), 0))
    Vg = sp.Matrix(n, n, lambda r_, nu: ordered(S13.tcoeff(t, 1), [("odd", cb[r_]), ("odd", th[nu]), ("even", q)]).t.get((), 0))
    g13 = gamma1(S13, t, 2, c + cb, S0, [(q, m)])
    ext = rules["graphs"]["D13"]["ext_order"]
    agree13, vals = True, {}
    for j in range(n):
        for nu in range(n):
            d = {"K": ("odd", K[j]), "c": ("odd", th[nu])}
            val = sp.simplify(ordered(g13.tcoeff(t, 2), [d[x] for x in ext]).t.get((), 0))
            amp = sum((I * VK[j, u]) * Dgh[u, r_] * (I * Vg[r_, nu]) for u in range(n) for r_ in range(n)) * (I / m)
            rule = sp.simplify(-I * G["D13"]["ext_sign"] * G["D13"]["S_f"] * G["D13"]["loop_sign"] * amp)
            vals[f"{j}{nu}"] = [str(val), str(rule)]
            agree13 &= sp.simplify(val - rule) == 0
    out["D13"] = {"values_vs_rule": vals, "agree": bool(agree13)}
    return out
