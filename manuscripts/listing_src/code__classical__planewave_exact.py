#!/usr/bin/env python3
"""Exact-rational plane-wave evaluator for local action densities (p10; unchanged in p11).

Method (declared): a local density f that is multilinear after polarisation is a total
divergence iff its polarised plane-wave value vanishes for all momentum-conserving
momenta (sum k = 0): int d_mu V^mu -> i (sum k)_mu V^mu = 0.  We evaluate polarised
values EXACTLY over Q (fractions.Fraction) at random rational momenta/polarisations.
Every density used here has a uniform total derivative count n_d, so the common
factor i^{n_d} is stripped (d_mu -> k_mu).  p11: plane-wave evaluations are REGRESSION CONTROLS only.
No acceptance statement relies on them; the deterministic proofs are the Euler-operator identities in
grav_noether.py / quartic.py and the exact symbolic identities listed in P13_quartic_verified.json.

Jets: H{m}{n} = h_{mn}, dH{m}{n}_{r} = d_r h_{mn} (ell4_full_polynomial naming).
"""
from __future__ import annotations
import hashlib, itertools, json, random
from fractions import Fraction as Fr
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
ETA = (1, -1, -1, -1)
INDEX = [(m, n) for m in range(4) for n in range(m, 4)]
VARS = [f"H{m}{n}" for m, n in INDEX] + [f"dH{m}{n}_{r}" for r in range(4) for m, n in INDEX]
VPOS = {v: i for i, v in enumerate(VARS)}


def load_ell(k: int, path: Path | None = None):
    """Load exported ell_k (sympy) and its sha256(str)."""
    p = path or (EXPORTS / f"ell{k}_generating_polynomial.srepr")
    expr = sp.sympify(p.read_text().strip())
    return expr, hashlib.sha256(str(expr).encode()).hexdigest()


def compile_poly(expr):
    """sympy polynomial in jet symbols -> list[(Fraction, ((pos,pow),...))]."""
    syms = [sp.Symbol(v) for v in VARS]
    P = sp.Poly(expr, *syms)
    out = []
    for mon, c in P.terms():
        c = sp.Rational(c)
        fac = tuple((i, e) for i, e in enumerate(mon) if e)
        out.append((Fr(int(c.p), int(c.q)), fac))
    return out


def eval_poly(cp, jet):
    tot = Fr(0)
    for c, fac in cp:
        v = c
        for i, e in fac:
            x = jet[i]
            if x == 0:
                v = 0
                break
            v *= x ** e if e > 1 else x
        if v:
            tot += v
    return tot


# ---------- plane-wave jets ----------
def tensor_jet(eps, k):
    """Symmetric lowered polarisation eps[m][n], momentum k (lower) -> jet vector."""
    j = [Fr(0)] * len(VARS)
    for m, n in INDEX:
        j[VPOS[f"H{m}{n}"]] = Fr(eps[m][n])
        for r in range(4):
            j[VPOS[f"dH{m}{n}_{r}"]] = Fr(k[r]) * Fr(eps[m][n])
    return j


def jet_add(*js):
    return [sum(x) for x in zip(*js)]


def polarize(evalf, Xs):
    """Coefficient of t1..tn in f(sum t_i X_i) for f homogeneous of degree n=len(Xs)."""
    n = len(Xs)
    tot = Fr(0)
    for r in range(1, n + 1):
        for S in itertools.combinations(range(n), r):
            tot += (-1) ** (n - r) * evalf(jet_add(*[Xs[i] for i in S]))
    return tot


# ---------- random rational data ----------
def rnd_frac(rng, lo=-9, hi=9):
    while True:
        p = rng.randint(lo, hi)
        q = rng.randint(1, 5)
        if p:
            return Fr(p, q)


def rnd_sym(rng):
    e = [[Fr(0)] * 4 for _ in range(4)]
    for m, n in INDEX:
        e[m][n] = e[n][m] = rnd_frac(rng)
    return e


def rnd_vec(rng):
    return [rnd_frac(rng) for _ in range(4)]


# ---------- BRST images of plane waves (d -> k, uniform i stripped) ----------
def lower(v):
    return [ETA[i] * v[i] for i in range(4)]


def s0_h_pol(zeta_up, kc, a):
    """s0 h_{mn} = a (d_m c_n + d_n c_m), c = zeta e^{i kc x} -> polarisation, momentum kc."""
    zl = lower(zeta_up)
    return [[a * (kc[m] * zl[n] + kc[n] * zl[m]) for n in range(4)] for m in range(4)]


def lie_c_h_pol(zeta_up, kc, eps, kh, a, transport=1, rotation=1):
    """a (L_c h)_{mn} = a( c^r d_r h_mn + h_rn d_m c^r + h_mr d_n c^r ); momentum kc+kh."""
    out = [[Fr(0)] * 4 for _ in range(4)]
    for m in range(4):
        for n in range(4):
            v = transport * sum(zeta_up[r] * kh[r] for r in range(4)) * eps[m][n]
            v += rotation * sum(eps[r][n] * kc[m] * zeta_up[r] for r in range(4))
            v += rotation * sum(eps[m][r] * kc[n] * zeta_up[r] for r in range(4))
            out[m][n] = a * v
    return out


def vadd(*vs):
    return [sum(x) for x in zip(*vs)]


def neg(v):
    return [-x for x in v]
