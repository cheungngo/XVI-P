#!/usr/bin/env python3
"""Independent evaluator of ell_n = -2 [eps^n] L_GammaGamma(eta + eps H) (truncated power series in eps).

Coded independently of ell4_full_polynomial (Neumann-series inverse, permutation determinant, binomial sqrt).
Generic over the coefficient domain `num`:
  * num = fractions.Fraction  -> exact numeric evaluation at a jet (regression controls);
  * num = symbolic ring        -> exact POLYNOMIAL in the 50 jet symbols (deterministic identity with the export).

contraction: "correct"   L = sqrt(-q) q^{mn}(G^a_{mb} G^b_{na} - G^a_{mn} G^b_{ab})
             "swapped"   L = sqrt(-q) q^{mn}(G^a_{ma} G^b_{nb} - G^a_{mn} G^b_{ab})   (mutation)
"""
from __future__ import annotations
import itertools
from fractions import Fraction as Fr

ETA = (1, -1, -1, -1)
N = 5


def ell_from_jet(H, dH, nmax=4, contraction="correct", drop_sqrt_eps2=False, num=Fr):
    """H[m][n], dH[r][m][n] in the coefficient domain.  Returns {k: ell_k} for k <= nmax."""
    n = nmax + 1
    Z = num(0)

    def sc(c):
        return [num(c)] + [Z] * (n - 1)

    def smul(a, b):
        out = [Z] * n
        for i in range(n):
            if a[i] == 0:
                continue
            for j in range(n - i):
                if b[j] != 0:
                    out[i + j] = out[i + j] + a[i] * b[j]
        return out

    def sadd(*xs):
        out = [Z] * n
        for x in xs:
            out = [u + v for u, v in zip(out, x)]
        return out

    def sscale(a, c):
        c = num(c)
        return [c * x for x in a]

    g = [[[num(ETA[i]) if i == j else Z, H[i][j]] + [Z] * (n - 2) for j in range(4)] for i in range(4)]
    M = [[num(ETA[i]) * H[i][j] for j in range(4)] for i in range(4)]
    ginv = [[[Z] * n for _ in range(4)] for _ in range(4)]
    P = [[num(1) if i == j else Z for j in range(4)] for i in range(4)]
    for k in range(n):
        for i in range(4):
            for j in range(4):
                ginv[i][j][k] = ginv[i][j][k] + num((-1) ** k * ETA[j]) * P[i][j]
        P = [[sum((P[i][l] * M[l][j] for l in range(4)), Z) for j in range(4)] for i in range(4)]
    det = [Z] * n
    for perm in itertools.permutations(range(4)):
        sgn = 1
        for i in range(4):
            for j in range(i + 1, 4):
                if perm[i] > perm[j]:
                    sgn = -sgn
        t = sc(sgn)
        for i in range(4):
            t = smul(t, g[i][perm[i]])
        det = sadd(det, t)
    x = [Z] + [-v for v in det[1:]]           # -det = 1 + x
    sq = sc(1)
    term = sc(1)
    coef = Fr(1)
    for k in range(1, n):
        coef = coef * (Fr(1, 2) - (k - 1)) / k
        term = smul(term, x)
        sq = sadd(sq, sscale(term, coef))
    if drop_sqrt_eps2:
        sq[2] = Z

    def dg(m, s, nn):
        return [Z, dH[m][s][nn]] + [Z] * (n - 2)
    Gam = [[[None] * 4 for _ in range(4)] for _ in range(4)]
    for r in range(4):
        for m in range(4):
            for nn in range(m, 4):
                acc = [Z] * n
                for s in range(4):
                    br = sadd(dg(m, s, nn), dg(nn, s, m), sscale(dg(s, m, nn), -1))
                    acc = sadd(acc, smul(ginv[r][s], br))
                Gam[r][m][nn] = Gam[r][nn][m] = sscale(acc, Fr(1, 2))
    trG = [sadd(*[Gam[b][a][b] for b in range(4)]) for a in range(4)]
    L0 = [Z] * n
    for mu in range(4):
        for nu in range(4):
            if contraction == "correct":
                quad = sadd(*[smul(Gam[a][mu][b], Gam[b][nu][a]) for a in range(4) for b in range(4)])
            elif contraction == "swapped":
                quad = smul(trG[mu], trG[nu])
            else:
                raise ValueError(contraction)
            tr = sadd(*[smul(Gam[a][mu][nu], trG[a]) for a in range(4)])
            L0 = sadd(L0, smul(ginv[mu][nu], sadd(quad, sscale(tr, -1))))
    L = smul(sq, L0)
    return {k: num(-2) * L[k] for k in range(n)}


def jet_from_legs(legs):
    """legs: list of (eps[m][n], k[r]) plane waves, d -> k (uniform i stripped). Sum of legs."""
    H = [[sum(e[m][nn] for e, _ in legs) for nn in range(4)] for m in range(4)]
    dH = [[[sum(k[r] * e[m][nn] for e, k in legs) for nn in range(4)] for m in range(4)] for r in range(4)]
    return H, dH


def polarized_ell(nn, legs, contraction="correct", **kw):
    """[t_1..t_n] ell_nn(sum t_i leg_i)  (= unnormalised n-th variation D^n ell_nn(0)[legs])."""
    tot = Fr(0)
    m = len(legs)
    for r in range(1, m + 1):
        for S in itertools.combinations(range(m), r):
            H, dH = jet_from_legs([legs[i] for i in S])
            tot += (-1) ** (m - r) * ell_from_jet(H, dH, nmax=nn, contraction=contraction, **kw)[nn]
    return tot


def symbolic_ell(nmax=4, **kw):
    """Exact polynomials ell_k in the 50 jet symbols H{m}{n}, dH{m}{n}_{r} (sympy PolyRing over QQ)."""
    from sympy.polys.rings import ring
    from sympy import QQ
    INDEX = [(m, n) for m in range(4) for n in range(m, 4)]
    names = [f"H{m}{n}" for m, n in INDEX] + [f"dH{m}{n}_{r}" for r in range(4) for m, n in INDEX]
    R, *gens = ring(",".join(names), QQ)
    V = dict(zip(names, gens))

    def num(x):
        x = Fr(x)
        return R(QQ(x.numerator, x.denominator))
    H = [[V["H%d%d" % (min(m, n), max(m, n))] for n in range(4)] for m in range(4)]
    dH = [[[V["dH%d%d_%d" % (min(m, n), max(m, n), r)] for n in range(4)] for m in range(4)] for r in range(4)]
    return R, ell_from_jet(H, dH, nmax=nmax, num=num, **kw)
