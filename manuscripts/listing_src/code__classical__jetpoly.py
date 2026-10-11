#!/usr/bin/env python3
"""p11: exact sparse polynomial algebra on the (even) jet space of h_{mn} (m<=n) and c^mu, with total
derivatives D_r, partial derivatives and Euler operators.  Coefficients: fractions.Fraction.  Deterministic.

Variable key = (field, comp, J): field in {"h","c"}, comp=(m,n) m<=n for h, mu for c (upper index),
J = sorted tuple of derivative directions.  Polynomial = dict{monomial(sorted tuple of var ids): Fraction}.
Here c is treated as a commuting placeholder: every density used is LINEAR in c, so grading is irrelevant.

Divergence lemma used for c-linear densities W:  W = c^mu Q_mu + d_r(...) with Q_mu = E_{c^mu}(W)
(integration by parts), so W is a total divergence iff E_{c^mu}(W) = 0 for all mu.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction as Fr

KEYS: list = []
IDS: dict = {}


def vid(key):
    i = IDS.get(key)
    if i is None:
        i = len(KEYS)
        KEYS.append(key)
        IDS[key] = i
    return i


def var(field, comp, J=()):
    return {(vid((field, comp, tuple(sorted(J)))),): Fr(1)}


def const(x):
    return {(): Fr(x)} if x else {}


def add(*ps):
    out = defaultdict(Fr)
    for p in ps:
        for m, c in p.items():
            out[m] += c
    return {m: c for m, c in out.items() if c}


def scale(p, x):
    x = Fr(x)
    return {m: c * x for m, c in p.items()} if x else {}


def mul(p, q):
    out = defaultdict(Fr)
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            out[tuple(sorted(m1 + m2))] += c1 * c2
    return {m: c for m, c in out.items() if c}


def shifted(i, r):
    f, comp, J = KEYS[i]
    return vid((f, comp, tuple(sorted(J + (r,)))))


def D(p, r):
    out = defaultdict(Fr)
    for m, c in p.items():
        for pos in range(len(m)):
            if pos and m[pos] == m[pos - 1]:
                continue
            k = m.count(m[pos])
            new = list(m)
            new[pos] = shifted(m[pos], r)
            out[tuple(sorted(new))] += c * k
    return {m: c for m, c in out.items() if c}


def pdiff(p, i):
    out = defaultdict(Fr)
    for m, c in p.items():
        k = m.count(i)
        if k:
            new = list(m)
            new.remove(i)
            out[tuple(new)] += c * k
    return {m: c for m, c in out.items() if c}


def euler(p, field, comp):
    """E_u(p) = sum_J (-D)_J dp/du_J."""
    js = sorted({KEYS[i][2] for m in p for i in m if KEYS[i][0] == field and KEYS[i][1] == comp})
    out = {}
    for J in js:
        t = pdiff(p, vid((field, comp, J)))
        for r in J:
            t = scale(D(t, r), -1)
        out = add(out, t)
    return out


def from_sympy(expr, symmap):
    """sympy polynomial -> jet poly, symmap: sympy Symbol name -> key."""
    import sympy as sp
    syms = [sp.Symbol(n) for n in symmap]
    P = sp.Poly(expr, *syms)
    ids = [vid(symmap[s.name]) for s in syms]
    out = {}
    for mon, c in P.terms():
        m = []
        for i, e in zip(ids, mon):
            m += [i] * e
        c = sp.Rational(c)
        out[tuple(sorted(m))] = Fr(int(c.p), int(c.q))
    return out


def ell_symmap():
    INDEX = [(m, n) for m in range(4) for n in range(m, 4)]
    sm = {f"H{m}{n}": ("h", (m, n), ()) for m, n in INDEX}
    sm.update({f"dH{m}{n}_{r}": ("h", (m, n), (r,)) for m, n in INDEX for r in range(4)})
    return sm


def describe(p, k=3):
    return [(" ".join(f"{KEYS[i][0]}{KEYS[i][1]}{'_' + ''.join(map(str, KEYS[i][2])) if KEYS[i][2] else ''}"
                      for i in m), str(c)) for m, c in list(p.items())[:k]]
