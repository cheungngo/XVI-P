#!/usr/bin/env python3
"""p11: DETERMINISTIC gravitational Noether identities and divergence-equality tests (exact, jetpoly).

Noether at order kappa^n (n = 0, 1, 2), antifield number 0 of 2(S_field, X):
    W_n = sum_{m<=n'} E_{(mn')}(ell_{n+2}) (s0 h)_{mn'} + E_{(mn')}(ell_{n+1}) (s1 h)_{mn'}   [+ E(ell_n) s2 h
  +> , s2 = 0 derived]
with E the Euler operator for the independent component h_{mn'} (m<=n'), s0 h = a(d_m c_n + d_n c_m),
s1 h = a L_c h = a(c^r d_r h_mn + h_rn d_m c^r + h_mr d_n c^r), a = 1/2, c_n = eta_nn c^n.
W_n is linear in c, so W_n = c^mu Q_mu + divergence with Q_mu = E_{c^mu}(W_n); hence
    W_n is a total divergence  <=>  Q_mu = 0 identically (polynomial identity on the jet space).
This is an exact symbolic statement about the EXPORTED polynomials (no sampling).
"""
from __future__ import annotations
from fractions import Fraction as Fr
import jetpoly as J

ETA = (1, -1, -1, -1)
INDEX = [(m, n) for m in range(4) for n in range(m, 4)]
A = Fr(1, 2)


def _h(m, n):
    return J.var("h", (min(m, n), max(m, n)))


def _dh(m, n, r):
    return J.var("h", (min(m, n), max(m, n)), (r,))


def _c(mu, Jd=()):
    return J.var("c", mu, Jd)


def s0(m, n, a=A):
    return J.scale(J.add(J.scale(_c(n, (m,)), ETA[n]), J.scale(_c(m, (n,)), ETA[m])), a)


def s1(m, n, a=A, transport=1):
    t = []
    for r in range(4):
        if transport:
            t.append(J.mul(_c(r), _dh(m, n, r)))
        t.append(J.mul(_h(r, n), _c(r, (m,))))
        t.append(J.mul(_h(m, r), _c(r, (n,))))
    return J.scale(J.add(*t), a)


def load_export_polys():
    import planewave_exact as PW
    sm = J.ell_symmap()
    out, sha = {}, {}
    for k in (2, 3, 4):
        e, h = PW.load_ell(k)
        out[k] = J.from_sympy(e, sm)
        sha[k] = h
    return out, sha


def ring_to_jet(poly, names):
    sm = J.ell_symmap()
    ids = [J.vid(sm[nm]) for nm in names]
    out = {}
    for mon, c in poly.terms():
        m = []
        for i, e in zip(ids, mon):
            m += [i] * e
        out[tuple(sorted(m))] = Fr(int(c.numerator), int(c.denominator))
    return out


def euler_all(p):
    return {mn: J.euler(p, "h", mn) for mn in INDEX}


def _nz(p):
    """Drop zero-valued entries (jetpoly already never stores them; this makes the count/flag pair robust)."""
    return {m: c for m, c in p.items() if c != 0}


def parameters(shas=None, transport=1, a=A):
    return {"a_ghost": str(a), "transport_term": int(transport),
            "s0": "a(eta_nn d_m c^n + eta_mm d_n c^m)", "s1": "a(c^r d_r h_mn + h_rn d_m c^r + h_mr d_n c^r)",
            "ell_sha256": {f"ell{k}": shas[k] for k in sorted(shas)} if shas else None}


def noether(ell, transport=1):
    """ell: {2,3,4: jetpoly}.  Returns per order: Q term counts, zero flag, and the s0-piece-alone Q (mixing).
    Count and flag are derived from the SAME normalised list Q: zero == all(n == 0 for n in counts) (asserted)
  +> ."""
    E = {k: euler_all(ell[k]) for k in (2, 3, 4)}
    out = {}
    for n in (0, 1, 2):
        W0 = J.add(*[J.mul(E[n + 2][mn], s0(*mn)) for mn in INDEX])
        W = W0
        if n >= 1:
            W = J.add(W0, *[J.mul(E[n + 1][mn], s1(*mn, transport=transport)) for mn in INDEX])
        Q = [_nz(J.euler(W, "c", mu)) for mu in range(4)]
        Q0 = [_nz(J.euler(W0, "c", mu)) for mu in range(4)] if n >= 1 else Q
        counts = [len(q) for q in Q]
        zero = all(c == 0 for c in counts)
        assert zero == all(not q for q in Q), "count/flag invariant violated"
        out[f"kappa{n}"] = {"density": {0: "s0 ell2", 1: "s0 ell3 + s1 ell2", 2: "s0 ell4 + s1 ell3 (+ s2 ell2
  +> , s2 = 0)"}[n],
                            "W_terms": len(_nz(W)), "Q_terms": counts, "Q_identically_zero": zero,
                            "s0_piece_alone_Q_terms": [len(q) for q in Q0],
                            "residual_head": J.describe(Q[0]) if Q[0] else []}
    return out


def divergence_equal(p, q):
    """p - q is a total divergence  <=>  E_{h_mn}(p - q) = 0 for all 10 components (no constant term)."""
    d = J.add(p, J.scale(q, -1))
    res = {f"{m}{n}": len(J.euler(d, "h", (m, n))) for m, n in INDEX}
    return {"difference_terms": len(d), "euler_terms": res, "divergence": all(v == 0 for v in res.values())}
