#!/usr/bin/env python3
"""Graded (Grassmann) jet algebra for local BV functionals (p10; unchanged in p11).

Element = density in the superjet algebra:  {odd_monomial(tuple of odd jet keys, canonical
order): commuting sympy coefficient in even jet symbols}.  Jet key = (field, comp, J) with
J a sorted tuple of derivative directions.  Provides graded product, total derivatives D_a,
left/right partial derivatives, left/right Euler operators, the XVI-N antibracket
    (F,G) = sum_A [ E^R_{Phi^A}(F) E^L_{Phi*_A}(G) - E^R_{Phi*_A}(F) E^L_{Phi^A}(G) ],
and the divergence test  f ~ 0  <=>  E_u(f) = 0 for every generator u (no constant term).
Nothing in this module chooses a physics sign; it only implements graded calculus.
"""
from __future__ import annotations
import itertools
import sympy as sp

FIELD_ORDER = ["h", "c", "cb", "b", "phi", "K", "cs", "cbs", "bs", "phis", "lam", "mu", "z"]
_FORD = {f: i for i, f in enumerate(FIELD_ORDER)}
PARITY = {"h": 0, "c": 1, "cb": 1, "b": 0, "phi": 0,
          "K": 1, "cs": 0, "cbs": 0, "bs": 1, "phis": 1,
          "lam": 0, "mu": 0, "z": 1}
PAIRS = [("h", "K"), ("c", "cs"), ("cb", "cbs"), ("b", "bs"), ("phi", "phis")]
H_COMPS = [(m, n) for m in range(4) for n in range(m, 4)]
VEC_COMPS = [0, 1, 2, 3]


def comps(field):
    if field in ("h", "K"):
        return H_COMPS
    if field in ("phi", "phis"):
        return [()]
    return VEC_COMPS


def set_parity(field, p):
    PARITY[field] = p


def _ckey(comp):
    return comp if isinstance(comp, tuple) else (comp,)


def sortkey(key):
    f, c, J = key
    return (_FORD[f], _ckey(c), len(J), J)


_SYM = {}
_KEY = {}


def esym(key):
    s = _SYM.get(key)
    if s is None:
        f, c, J = key
        cs = "".join(map(str, _ckey(c)))
        js = ("_d" + "".join(map(str, J))) if J else ""
        s = sp.Symbol(f"{f}{cs}{js}")
        _SYM[key] = s
        _KEY[s] = key
    return s


def shift(key, a):
    f, c, J = key
    return (f, c, tuple(sorted(J + (a,))))


def _sort_sign(seq):
    """Return (sign, sorted tuple) or (0, None) if a repeated odd generator occurs."""
    lst = list(seq)
    n = len(lst)
    sign = 1
    keys = [sortkey(x) for x in lst]
    for i in range(n):
        for j in range(n - 1 - i):
            if keys[j] > keys[j + 1]:
                keys[j], keys[j + 1] = keys[j + 1], keys[j]
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                sign = -sign
            elif keys[j] == keys[j + 1]:
                return 0, None
    return sign, tuple(lst)


class GE:
    __slots__ = ("t",)

    def __init__(self, t=None):
        self.t = {}
        if t:
            for k, v in t.items():
                v = sp.expand(v)
                if v != 0:
                    self.t[k] = v

    # constructors
    @staticmethod
    def const(x):
        return GE({(): sp.sympify(x)})

    @staticmethod
    def gen(field, comp, J=()):
        key = (field, comp, tuple(sorted(J)))
        if PARITY[field] == 0:
            return GE({(): esym(key)})
        return GE({(key,): sp.Integer(1)})

    def copy(self):
        g = GE()
        g.t = dict(self.t)
        return g

    def is_zero(self):
        return not self.t

    def __add__(self, o):
        if not isinstance(o, GE):
            o = GE.const(o)
        r = dict(self.t)
        for k, v in o.t.items():
            r[k] = sp.expand(r.get(k, 0) + v)
            if r[k] == 0:
                del r[k]
        g = GE(); g.t = r
        return g

    __radd__ = __add__

    def __neg__(self):
        g = GE(); g.t = {k: -v for k, v in self.t.items()}
        return g

    def __sub__(self, o):
        return self + (-o if isinstance(o, GE) else GE.const(-o))

    def __rsub__(self, o):
        return GE.const(o) + (-self)

    def scale(self, x):
        x = sp.sympify(x)
        return GE({k: v * x for k, v in self.t.items()})

    def __mul__(self, o):
        if not isinstance(o, GE):
            return self.scale(o)
        r = {}
        for k1, v1 in self.t.items():
            for k2, v2 in o.t.items():
                sgn, k = _sort_sign(k1 + k2)
                if sgn == 0:
                    continue
                r[k] = r.get(k, 0) + sgn * v1 * v2
        return GE(r)

    def __rmul__(self, x):
        return self.scale(x)

    def parity_terms(self):
        return {len(k) % 2 for k in self.t}

    def keys_of(self, field=None, comp=None):
        """All jet keys (even & odd) occurring."""
        out = set()
        for k, v in self.t.items():
            for x in k:
                out.add(x)
            for s in v.free_symbols:
                kk = _KEY.get(s)
                if kk is not None:
                    out.add(kk)
        if field is not None:
            out = {x for x in out if x[0] == field and (comp is None or x[1] == comp)}
        return out

    def __repr__(self):
        return " + ".join(f"({v})*{list(k)}" for k, v in self.t.items()) or "0"


def D(F: GE, a: int) -> GE:
    """Total derivative d_a (even derivation)."""
    r = {}
    for k, v in F.t.items():
        # coefficient
        dv = 0
        for s in v.free_symbols:
            kk = _KEY.get(s)
            if kk is not None:
                dv += sp.diff(v, s) * esym(shift(kk, a))
        if dv != 0:
            r[k] = r.get(k, 0) + dv
        # odd generators
        for i in range(len(k)):
            nk = k[:i] + (shift(k[i], a),) + k[i + 1:]
            sgn, sk = _sort_sign(nk)
            if sgn:
                r[sk] = r.get(sk, 0) + sgn * v
    return GE(r)


def DJ(F, J):
    for a in J:
        F = D(F, a)
    return F


def pdiff(F: GE, key, side="L") -> GE:
    """Left/right partial derivative wrt a jet generator."""
    f = key[0]
    r = {}
    if PARITY[f] == 0:
        s = esym(key)
        for k, v in F.t.items():
            dv = sp.diff(v, s)
            if dv != 0:
                r[k] = r.get(k, 0) + dv
    else:
        for k, v in F.t.items():
            if key in k:
                i = k.index(key)
                sgn = (-1) ** i if side == "L" else (-1) ** (len(k) - 1 - i)
                nk = k[:i] + k[i + 1:]
                r[nk] = r.get(nk, 0) + sgn * v
    return GE(r)


def euler(F: GE, field, comp, side="L") -> GE:
    out = GE()
    for key in F.keys_of(field, comp):
        J = key[2]
        term = DJ(pdiff(F, key, side), J)
        if len(J) % 2:
            term = -term
        out = out + term
    return out


def bracket(F: GE, G: GE, pairs=PAIRS) -> GE:
    """XVI-N antibracket density (orientation frozen in conventions.ANTIBRACKET)."""
    out = GE()
    for f, fs in pairs:
        for c in comps(f):
            a = euler(F, f, c, "R")
            if not a.is_zero():
                b = euler(G, fs, c, "L")
                if not b.is_zero():
                    out = out + a * b
            a2 = euler(F, fs, c, "R")
            if not a2.is_zero():
                b2 = euler(G, f, c, "L")
                if not b2.is_zero():
                    out = out - a2 * b2
    return out


def divergence_residual(F: GE):
    """Return {(field,comp): E^L_u(F)} for all u with nonzero Euler image (empty <=> F ~ 0)."""
    res = {}
    fields = {k[0] for k in F.keys_of()}
    for f in fields:
        for c in comps(f) if f not in ("lam", "mu", "z") else sorted({k[1] for k in F.keys_of(f)}, key=str):
            e = euler(F, f, c, "L")
            if not e.is_zero():
                res[(f, c)] = e
    return res


def is_divergence(F: GE) -> bool:
    return not divergence_residual(F)


def kappa_coeff(F: GE, kappa, n) -> GE:
    return GE({k: sp.expand(v).coeff(kappa, n) for k, v in F.t.items()})


def subst(F: GE, key_map: dict) -> GE:
    """Substitute undifferentiated generators: key_map[(field,comp)] = GE (same parity).
    Generators with derivative jets in F for substituted fields raise."""
    out = GE()
    for k, v in F.t.items():
        # even part: expand v as polynomial in substituted even symbols
        evsubs = {}
        for s in v.free_symbols:
            kk = _KEY.get(s)
            if kk is not None and (kk[0], kk[1]) in key_map and PARITY[kk[0]] == 0:
                if kk[2]:
                    raise ValueError(f"derivative jet of substituted even field: {kk}")
                evsubs[s] = key_map[(kk[0], kk[1])]
        # build coefficient as GE
        if evsubs:
            syms = list(evsubs)
            P = sp.Poly(v, *syms)
            coefGE = GE()
            for mon, cc in P.terms():
                t = GE.const(cc)
                for s, e in zip(syms, mon):
                    for _ in range(e):
                        t = t * evsubs[s]
                coefGE = coefGE + t
        else:
            coefGE = GE.const(v)
        # odd part, left to right
        prod = coefGE
        for x in k:
            if (x[0], x[1]) in key_map:
                if x[2]:
                    raise ValueError(f"derivative jet of substituted odd field: {x}")
                prod = prod * key_map[(x[0], x[1])]
            else:
                prod = prod * GE({(x,): sp.Integer(1)})
        out = out + prod
    return out


def s_apply(F: GE, s_of: dict) -> GE:
    """Left odd derivation s:  s F = sum_u (s u) d^L F / d u,  s(u_J) = D_J(s u).
    s_of[(field, comp)] = GE image of the undifferentiated generator."""
    out = GE()
    for key in F.keys_of():
        fc = (key[0], key[1])
        if fc not in s_of:
            continue
        su = DJ(s_of[fc], key[2])
        dF = pdiff(F, key, "L")
        if not dF.is_zero() and not su.is_zero():
            out = out + su * dF
    return out


def ghost_number(F: GE, gh: dict) -> set:
    vals = set()
    for k, v in F.t.items():
        g0 = sum(gh[x[0]] for x in k)
        for term in sp.Add.make_args(sp.expand(v)):
            g = g0
            for s, e in term.as_powers_dict().items():
                kk = _KEY.get(s)
                if kk is not None:
                    g += gh[kk[0]] * int(e)
            vals.add(g)
    return vals
