#!/usr/bin/env python3
"""XVI-P p14: executable momentum-space Feynman-rule engine for S_Psi(Phi,Phi*') (NO loop integration).

Conventions (XVI-O Gate 0, frozen; restated in notes P14_P5_entry_contract.tex):
  weight e^{iS};  f(x) = int d^4k/(2pi)^4 e^{ikx} f~(k), all momenta INCOMING, (2pi)^4 delta(sum k) stripped;
  d_r -> i k_r (lower components);  eta = diag(+,-,-,-);  k^2 = eta^{rs} k_r k_s.

ORDERED vertex extraction (single definition used for every vertex, every propagator, every Gamma_1 coefficient and
the 0-dimensional Berezin shadow models):
  V[L1, L2, ..., Ln] := d^L_{Ln}( ... d^L_{L2}( d^L_{L1} F ) ... )|_{fields = 0},
  each leg L = (field, component or polarisation, incoming momentum), plane wave substituted.  Leg 1 is the LEFTMOST
  factor:  F = A B f (A,B odd)  =>  V[A,B] = f.  For even legs the result is the unnormalised variation
  (V4 = [t1 t2 t3 t4] ell_4(sum t_i h_i), the frozen p13 POLARIZATION convention); Feynman vertex = i kappa^n V.
Graviton legs use the 10 INDEPENDENT components h_(mn), m<=n (the variables of the exports and of S_af).
"""
from __future__ import annotations
import itertools
import os
import sys
from fractions import Fraction as Fr
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "code" / "classical"))
import conventions as C  # noqa: E402
from graded_jets import GE, pdiff, kappa_coeff, H_COMPS, _KEY, PARITY  # noqa: E402
import bv_model as BV  # noqa: E402
import source_action as SA  # noqa: E402
import gauge_fixing_map as GF  # noqa: E402
import planewave_exact as PW  # noqa: E402

ETA = (1, -1, -1, -1)
I = sp.I
KAPPA = BV.KAPPA
A_GH = BV.A
HC = list(H_COMPS)
HIDX = {mn: i for i, mn in enumerate(HC)}
W_OFF = [1 if m == n else 2 for (m, n) in HC]      # tensor multiplicity of an independent component


def mutations():
    return set(filter(None, os.environ.get("P14_MUTATIONS", "").split(",")))


# ======================================================================================================
# sparse exact polynomials (monomial = sorted tuple of variable ids, coefficient = Fraction)
# ======================================================================================================
class SP:
    __slots__ = ("d",)

    def __init__(self, d=None):
        self.d = d if d is not None else {}

    @staticmethod
    def const(c):
        c = Fr(c)
        return SP({(): c}) if c else SP()

    @staticmethod
    def var(v, c=1):
        c = Fr(c)
        return SP({(v,): c}) if c else SP()

    def copy(self):
        return SP(dict(self.d))

    def is_zero(self):
        return not self.d

    def __eq__(self, o):
        return isinstance(o, SP) and self.d == o.d

    def __hash__(self):
        return hash(frozenset(self.d.items()))

    def iadd(self, o, c=1):
        c = Fr(c)
        if not c:
            return self
        d = self.d
        for m, v in o.d.items():
            nv = d.get(m, 0) + c * v
            if nv:
                d[m] = nv
            else:
                d.pop(m, None)
        return self

    def __add__(self, o):
        return self.copy().iadd(o)

    def __sub__(self, o):
        return self.copy().iadd(o, -1)

    def __neg__(self):
        return SP({m: -v for m, v in self.d.items()})

    def scale(self, c):
        c = Fr(c)
        return SP({m: v * c for m, v in self.d.items()}) if c else SP()

    def __mul__(self, o):
        if not isinstance(o, SP):
            return self.scale(o)
        r = {}
        for m1, v1 in self.d.items():
            for m2, v2 in o.d.items():
                m = tuple(sorted(m1 + m2))
                nv = r.get(m, 0) + v1 * v2
                if nv:
                    r[m] = nv
                else:
                    r.pop(m, None)
        return SP(r)

    def iadd_prod(self, a, b, c=1):
        """self += c * a * b"""
        c = Fr(c)
        d = self.d
        for m1, v1 in a.d.items():
            cv1 = c * v1
            for m2, v2 in b.d.items():
                m = tuple(sorted(m1 + m2))
                nv = d.get(m, 0) + cv1 * v2
                if nv:
                    d[m] = nv
                else:
                    d.pop(m, None)
        return self

    def subs(self, mp):
        """substitute variables by SP values (mp: var id -> SP); unmapped variables kept."""
        out = SP()
        cache = {}
        for m, v in self.d.items():
            t = SP.const(v)
            for x in m:
                if x in mp:
                    t = t * mp[x]
                else:
                    t = t * SP.var(x)
            out.iadd(t)
        return out

    def degree(self):
        return max((len(m) for m in self.d), default=0)

    def to_sympy(self, names):
        return sp.Add(*[sp.Rational(v.numerator, v.denominator) * sp.Mul(*[names[x] for x in m])
                        for m, v in self.d.items()])

    def canonical(self, names):
        """deterministic serialisation [[ [var names...], 'p/q' ], ...] sorted."""
        rows = [[[names[x] for x in m], f"{v.numerator}/{v.denominator}"] for m, v in self.d.items()]
        rows.sort(key=lambda r: (len(r[0]), r[0]))
        return rows


def from_sympy(expr, varmap):
    """sympy polynomial with coefficients in Q(i), homogeneous in the phase -> (phase m, SP) with expr = i^m * SP.
    varmap: sympy Symbol -> var id."""
    expr = sp.expand(expr)
    if expr == 0:
        return 0, SP()
    re_d, im_d = {}, {}
    for t in sp.Add.make_args(expr):
        num, rest = t.as_independent(*varmap.keys(), as_Add=False)
        mono = []
        for b, e in rest.as_powers_dict().items():
            if b == 1:
                continue
            mono += [varmap[b]] * int(e)
        mono = tuple(sorted(mono))
        re_, im_ = sp.Rational(sp.re(num)), sp.Rational(sp.im(num))
        if re_:
            re_d[mono] = re_d.get(mono, 0) + Fr(int(re_.p), int(re_.q))
        if im_:
            im_d[mono] = im_d.get(mono, 0) + Fr(int(im_.p), int(im_.q))
    re_d = {k: v for k, v in re_d.items() if v}
    im_d = {k: v for k, v in im_d.items() if v}
    if re_d and im_d:
        raise ValueError("vertex not phase-homogeneous")
    return (0, SP(re_d)) if re_d else (1, SP(im_d))


# ======================================================================================================
# S_Psi(Phi, Phi*') in transformed variables
# ======================================================================================================
_CACHE = {}


def derived_eps():
    import json
    for f in sorted((ROOT / "certificates").glob(f"{C.CERT_PREFIX}_gauge_fixing_map.json")):
        return json.loads(f.read_text())["derived_eps"]
    return GF.build()[0]["derived_eps"]


def S_psi_parts():
    """kappa-graded GE densities: X^(n) (antifield + nonminimal + gauge-fixing, transformed variables) and
    S_phi^(n) (scalar); the graviton part sum_k kappa^{k-2} ell_k is handled from the exports (fast path)."""
    if "parts" in _CACHE:
        return _CACHE["parts"]
    eps = derived_eps()
    assert eps == -1, "derived antifield shift orientation changed"
    X = GF.transformed_X(SA.build_X_inv(), BV.Psi_density(), eps)
    Xn = {n: kappa_coeff(X, KAPPA, n) for n in (0, 1, 2)}
    if "omit_ghost_transport_term" in mutations():
        # MUTATION: drop the c^r d_r h (transport) term of the ghost-graviton vertex: c.cb.h monomials with an
        # undifferentiated ghost c
        t = {}
        for k, v in Xn[1].t.items():
            fs = [x[0] for x in k]
            if "cb" in fs and "c" in fs and any(x[0] == "c" and x[2] == () for x in k):
                continue
            t[k] = v
        Xn[1] = GE(t)
    Sphi = SA.scalar_density(2)
    Pn = {n: kappa_coeff(Sphi, KAPPA, n) for n in (0, 1, 2)}
    _CACHE["parts"] = {"eps": eps, "X": Xn, "phi": Pn}
    return _CACHE["parts"]


# ======================================================================================================
# ordered plane-wave extraction on GE densities
# ======================================================================================================
def _jetfac(J, k):
    v = sp.Integer(1)
    for j in J:
        v = v * I * k[j]
    return v


def _leg_derivative(G, leg):
    f, k = leg["f"], leg["k"]
    out = GE()
    if PARITY[f]:
        for key in G.keys_of(f, leg["c"]):
            out = out + pdiff(G, key, "L").scale(_jetfac(key[2], k))
    else:
        pol = leg.get("pol") or {(): 1}
        for key in G.keys_of(f):
            w = pol.get(key[1], 0)
            if w == 0:
                continue
            out = out + pdiff(G, key, "L").scale(w * _jetfac(key[2], k))
    return out


def pw_vertex(F, legs):
    """ordered extraction V[L1..Ln] (leg 1 innermost = leftmost factor), fields set to zero afterwards."""
    G = F
    for leg in legs:
        G = _leg_derivative(G, leg)
        if G.is_zero():
            return sp.Integer(0)
    v = G.t.get((), sp.Integer(0))
    z = {s: 0 for s in v.free_symbols if s in _KEY}
    return sp.expand(v.xreplace(z))


def ksym(leg):
    return [sp.Symbol(f"kk{leg}_{r}") for r in range(4)]


def esym_pol(leg):
    return {mn: sp.Symbol(f"ee{leg}_{mn[0]}{mn[1]}") for mn in HC}


class VT:
    """vertex tensor: V = i^phase * sum_{comps} [comp-indexed SP in leg momenta (var id 4*leg + r)]."""

    def __init__(self, name, legs, phase, T, kappa_power, origin):
        self.name, self.legs, self.phase, self.T = name, legs, phase % 4, T
        self.kappa_power, self.origin = kappa_power, origin

    def nnz(self):
        return sum(len(p.d) for p in self.T.values())


def ge_vertex(name, F, spec, kappa_power, origin):
    """spec: list of (field, comp-range) ; graviton legs get symbolic polarisations; returns VT with integer comp
    indices (graviton: HIDX; vector: 0..3; scalar: 0)."""
    n = len(spec)
    kvars = {}
    for leg in range(n):
        for r, s in enumerate(ksym(leg)):
            kvars[s] = 4 * leg + r
    odd_ranges = [list(range(4)) if f in ("c", "cb", "b", "cs", "cbs", "bs") else
                  (HC if f == "K" else [None]) for f, _ in spec]
    T, phase = {}, None
    for combo in itertools.product(*odd_ranges):
        legs = []
        for leg, ((f, _), cc) in enumerate(zip(spec, combo)):
            if f == "h":
                legs.append({"f": "h", "pol": esym_pol(leg), "k": ksym(leg)})
            elif f == "phi":
                legs.append({"f": "phi", "pol": {(): 1}, "k": ksym(leg)})
            elif PARITY[f] == 0:
                legs.append({"f": f, "pol": {cc: 1}, "k": ksym(leg)})
            else:
                legs.append({"f": f, "c": cc, "k": ksym(leg)})
        v = pw_vertex(F, legs)
        if v == 0:
            continue
        # split by graviton polarisation components
        hlegs = [leg for leg, (f, _) in enumerate(spec) if f == "h"]
        polsyms = {}
        for leg in hlegs:
            for mn, s in esym_pol(leg).items():
                polsyms[s] = (leg, HIDX[mn])
        P = sp.Poly(v, *polsyms.keys()) if polsyms else None
        items = P.terms() if P is not None else [((), v)]
        for mon, cf in items:
            comps = []
            for leg, (f, _) in enumerate(spec):
                if f == "h":
                    idx = [polsyms[s][1] for s, e in zip(polsyms.keys(), mon) if e and polsyms[s][0] == leg]
                    assert len(idx) == 1
                    comps.append(idx[0])
                elif f == "phi":
                    comps.append(0)
                else:
                    cc = combo[leg]
                    comps.append(HIDX[cc] if f == "K" else cc)
            ph, poly = from_sympy(sp.expand(cf.as_expr() if hasattr(cf, "as_expr") else cf), kvars)
            if poly.is_zero():
                continue
            if phase is None:
                phase = ph
            assert ph == phase, f"{name}: mixed phases"
            T.setdefault(tuple(comps), SP()).iadd(poly)
    T = {k: v for k, v in T.items() if not v.is_zero()}
    return VT(name, [f for f, _ in spec], phase or 0, T, kappa_power, origin)


# ======================================================================================================
# graviton vertices from the exports (fast path; i^2 = -1 folded into the stored coefficients)
# ======================================================================================================
def ell_terms(k):
    e, sha = PW.load_ell(k)
    out = []
    for t in sp.Add.make_args(sp.expand(e)):
        c, rest = t.as_coeff_Mul()
        facs = []
        for b, ex in rest.as_powers_dict().items():
            nm = b.name
            if nm.startswith("dH"):
                facs += [((int(nm[2]), int(nm[3])), int(nm.split("_")[1]))] * int(ex)
            else:
                facs += [((int(nm[1]), int(nm[2])), None)] * int(ex)
        assert len(facs) == k and sum(1 for f in facs if f[1] is not None) == 2
        out.append((Fr(int(c.p), int(c.q)), facs))
    return out, sha


def grav_vertex(k):
    key = f"V{k}"
    if key in _CACHE:
        return _CACHE[key]
    terms, sha = ell_terms(k)
    T = {}
    for c, facs in terms:
        for perm in itertools.permutations(range(k)):
            comps = [None] * k
            mom = []
            for f, leg in zip(facs, perm):
                comps[leg] = HIDX[f[0]]
                if f[1] is not None:
                    mom.append(4 * leg + f[1])
            d = T.setdefault(tuple(comps), {})
            m = tuple(sorted(mom))
            d[m] = d.get(m, 0) - c          # (i k)(i k) = -k k
    T = {kk: SP({m: v for m, v in d.items() if v}) for kk, d in T.items()}
    T = {kk: v for kk, v in T.items() if not v.is_zero()}
    vt = VT(f"V{k}_grav", ["h"] * k, 0, T, k - 2, f"exports/ell{k}_generating_polynomial.srepr (sha {sha[:16]})")
    _CACHE[key] = vt
    return vt


def vt_eval(vt, pols, moms):
    """evaluate on legs: pols[leg] = {comp idx: SP}, moms[leg][r] = SP  ->  SP (phase NOT applied)."""
    out = SP()
    mp = {}
    for leg, mm in enumerate(moms):
        for r in range(4):
            mp[4 * leg + r] = mm[r]
    for comps, poly in vt.T.items():
        coef = SP.const(1)
        ok = True
        for leg, cidx in enumerate(comps):
            pv = pols[leg].get(cidx)
            if pv is None or pv.is_zero():
                ok = False
                break
            coef = coef * pv
        if not ok:
            continue
        out.iadd(coef * poly.subs(mp))
    return out


def vt_route(vt, route):
    """substitute leg momenta by linear combinations of loop l (vars 0..3) and external p (vars 4..7):
    route[leg] = (cl, cp)  =>  k_leg = cl*l + cp*p.  Returns {comps: SP(l,p)}."""
    mp = {}
    for leg, (cl, cp) in enumerate(route):
        for r in range(4):
            mp[4 * leg + r] = SP({m: v for m, v in (((r,), Fr(cl)), ((4 + r,), Fr(cp))) if v})
    return {comps: poly.subs(mp) for comps, poly in vt.T.items()}


# ======================================================================================================
# all vertices of S_Psi (inventory of conventions.py / ch_source_audit: kappa^0..kappa^2)
# ======================================================================================================
def vertices():
    if "verts" in _CACHE:
        return _CACHE["verts"]
    P = S_psi_parts()
    X, Ph = P["X"], P["phi"]
    V = {
        "V2_grav": grav_vertex(2), "V3_grav": grav_vertex(3), "V4_grav": grav_vertex(4),
        "M0_ghost": ge_vertex("M0_ghost", X[0], [("cb", 0), ("c", 0)], 0, "X^(0): cbar.c (c-bar left)"),
        "V_cb_c_h": ge_vertex("V_cb_c_h", X[1], [("cb", 0), ("c", 0), ("h", 0)], 1, "X^(1): cbar.c.h"),
        "V_K_c": ge_vertex("V_K_c", X[0], [("K", 0), ("c", 0)], 0, "X^(0): K'.c (source-linear, tree)"),
        "V_K_c_h": ge_vertex("V_K_c_h", X[1], [("K", 0), ("c", 0), ("h", 0)], 1, "X^(1): K'.c.h"),
        "V_cs_c_c": ge_vertex("V_cs_c_c", X[1], [("cs", 0), ("c", 0), ("c", 0)], 1, "X^(1): c*.c.c"),
        "V_phis_c_phi": ge_vertex("V_phis_c_phi", X[1], [("phis", 0), ("c", 0), ("phi", 0)], 1, "X^(1): phi*.c.phi"),
        "V_b_h": ge_vertex("V_b_h", X[0], [("b", 0), ("h", 0)], 0, "X^(0): b.h (gauge fixing)"),
        "V_b_b": ge_vertex("V_b_b", X[0], [("b", 0), ("b", 0)], 0, "X^(0): b.b"),
        "V_cbs_b": ge_vertex("V_cbs_b", X[0], [("cbs", 0), ("b", 0)], 0, "X^(0): cbar*'.b (nonminimal, tree)"),
        "M_phi": ge_vertex("M_phi", Ph[0], [("phi", 0), ("phi", 0)], 0, "S_phi^(0)"),
        "V_h_phi_phi": ge_vertex("V_h_phi_phi", Ph[1], [("h", 0), ("phi", 0), ("phi", 0)], 1, "S_phi^(1): a1"),
        "V_hh_phi_phi": ge_vertex("V_hh_phi_phi", Ph[2], [("h", 0), ("h", 0), ("phi", 0), ("phi", 0)], 2,
                                  "S_phi^(2): a2"),
    }
    _CACHE["verts"] = V
    return V


# ======================================================================================================
# propagators (from the verified Hessians; i0 Feynman: 1/(q^2 + i0))
# ======================================================================================================
def P_matrix():
    return sp.Matrix(10, 10, lambda i, j: GF.P_bilinear(HC[i], HC[j]))


def deDonder_tensor_numerator():
    """cross-reference only: (1/2)(eta_mr eta_ns + eta_ms eta_nr) - 1/2 eta_mn eta_rs at representative indices."""
    def e(a, b):
        return ETA[a] if a == b else 0
    return sp.Matrix(10, 10, lambda i, j: sp.Rational(1, 2) * (e(HC[i][0], HC[j][0]) * e(HC[i][1], HC[j][1])
                                                                + e(HC[i][0], HC[j][1]) * e(HC[i][1], HC[j][0]))
                     - sp.Rational(1, 2) * e(*HC[i]) * e(*HC[j]))


def propagators():
    """Delta_X(q) = i * (V2_X(-q, q))^{-1}; ghost <c^mu(q) cbar_rho(-q)> = i (M0^{-1})_{mu rho} with
    M0_{rho mu}(q) = V[cbar_rho(-q), c^mu(q)] (Berezin-derived rule, checked in the W1 shadow)."""
    if "props" in _CACHE:
        return _CACHE["props"]
    q = sp.symbols("q0:4")
    q2 = sum(ETA[r] * q[r] ** 2 for r in range(4))
    V = vertices()
    names = {4 * leg + r: sp.Symbol(f"kk{leg}_{r}") for leg in range(4) for r in range(4)}
    sub = {**{sp.Symbol(f"kk0_{r}"): -q[r] for r in range(4)}, **{sp.Symbol(f"kk1_{r}"): q[r] for r in range(4)}}

    def mat(vt, n1, n2):
        M = sp.zeros(n1, n2)
        for (i, j), poly in vt.T.items():
            M[i, j] += (I ** vt.phase) * poly.to_sympy(names).xreplace(sub)
        return M.applyfunc(sp.expand)
    Mhh = mat(V["V2_grav"], 10, 10)
    Mbh = mat(V["V_b_h"], 4, 10)          # V[b(-q), h(q)]
    Mbb = mat(V["V_b_b"], 4, 4)
    # V[h(-q), b(q)] = V[b(q), h(-q)] (even legs commute) -> q -> -q in Mbh, transposed
    Mhb = Mbh.xreplace({q[r]: -q[r] for r in range(4)}).T
    M = sp.BlockMatrix([[Mhh, Mhb], [Mbh, Mbb]]).as_explicit()
    Pm = P_matrix()
    Pinv = Pm.inv()
    Mbbinv = Mbb.inv()
    S = (Mhh - Mhb * Mbbinv * Mbh).applyfunc(sp.cancel)
    schur_ok = (S - q2 * Pm).applyfunc(sp.cancel) == sp.zeros(10, 10)
    Sinv = Pinv / q2
    inv_hh = Sinv
    inv_hb = (-Sinv * Mhb * Mbbinv).applyfunc(sp.cancel)
    inv_bh = (-Mbbinv * Mbh * Sinv).applyfunc(sp.cancel)
    inv_bb = (Mbbinv + Mbbinv * Mbh * Sinv * Mhb * Mbbinv).applyfunc(sp.cancel)
    Minv = sp.BlockMatrix([[inv_hh, inv_hb], [inv_bh, inv_bb]]).as_explicit()
    full_inverse_ok = (M * Minv).applyfunc(sp.cancel) == sp.eye(14)
    dd = deDonder_tensor_numerator()
    # ghost
    M0 = mat(V["M0_ghost"], 4, 4)
    m0 = (M0 / q2).applyfunc(sp.cancel)
    m0_const = all(sp.diff(x, qq) == 0 for x in m0 for qq in q)
    gh_num = (I * m0.inv()).applyfunc(sp.nsimplify)     # Delta_gh = gh_num / q^2
    Mphi = sp.expand(mat(V["M_phi"], 1, 1)[0, 0])
    phi_num = sp.nsimplify(I * q2 / Mphi)
    out = {
        "q": q, "q2": q2,
        "graviton": {"Pinv": Pinv, "numerator": "i (P^{-1})_{ab}", "denominator": "q^2 + i0",
                     "schur_equals_q2P": schur_ok, "full_h_b_inverse_verified": full_inverse_ok,
                     "Pinv_equals_deDonder_tensor_at_representatives": (Pinv - dd) == sp.zeros(10, 10),
                     "inverse_blocks": {"hh": "P^{-1}/q^2", "hb": str(sp.factor(inv_hb[0, 0])) + " (entry [00,0])",
                                        "bb_constant_part": str(Mbbinv)},
                     "Mbb": str(Mbb), "Minv": Minv},
        "ghost": {"M0": M0, "m0": m0, "M0_is_q2_times_constant": m0_const, "numerator": gh_num,
                  "rule": "<c^mu(q) cbar_rho(-q)> = i (M0^{-1})_{mu rho} = numerator_{mu rho}/(q^2+i0)"},
        "scalar": {"V2": Mphi, "numerator": phi_num, "rule": "i/(q^2+i0)"},
    }
    _CACHE["props"] = out
    return out


# ======================================================================================================
# closed forms (independent hand-written plane-wave formulas) for W3
# ======================================================================================================
def _E(a):
    m, n = HC[a]
    e = [[0] * 4 for _ in range(4)]
    e[m][n] = e[n][m] = 1
    return e


def lie_closed(mu, a, kc, kh):
    """(L_c h)_{mn} with c = unit vector mu (momentum kc), h = E(a) (momentum kh), d -> i k."""
    e = _E(a)
    T = [[0] * 4 for _ in range(4)]
    for m in range(4):
        for n in range(4):
            T[m][n] = (I * kh[mu] * e[m][n] + I * e[mu][n] * kc[m] + I * e[m][mu] * kc[n])
    return T


def ghost_vertex_closed(rho, mu, a, kb, kc, kh):
    """V[cbar_rho, c^mu, h_a] from cbar_rho * 2 i a D^rho[L_c h] (XVI-N V3, stated):  D^rho T = d_nu T^{rho nu}
    - 1/2 d^rho tr T, total momentum K = kc + kh."""
    T = lie_closed(mu, a, kc, kh)
    K = [kc[r] + kh[r] for r in range(4)]
    tr = sum(ETA[m] * T[m][m] for m in range(4))
    D = sum(I * K[nu] * ETA[rho] * ETA[nu] * T[rho][nu] for nu in range(4)) - sp.Rational(1, 2) * I * ETA[rho] * K[rho] * tr
    return sp.expand(2 * I * A_GH * D)


def K_vertex_closed(ap, mu, a, kK, kc, kh):
    """V[K'_(ap), c^mu, h_a] from K'_(mn) a (L_c h)_mn (sigma_h = +1, independent components)."""
    m, n = HC[ap]
    return sp.expand(A_GH * lie_closed(mu, a, kc, kh)[m][n])


def a1_closed(a):
    """XI-A: a1^{mn} = 1/2 tau eta^{mn} - h^{mn} on E(a)."""
    e = _E(a)
    tau = sum(ETA[r] * e[r][r] for r in range(4))
    return [[sp.Rational(1, 2) * tau * (ETA[m] if m == n else 0) - ETA[m] * ETA[n] * e[m][n] for n in range(4)]
            for m in range(4)]


def h_phi_phi_closed(a, k1, k2):
    A1 = a1_closed(a)
    return sp.expand(-sp.Rational(1, 2) * sum(A1[m][n] * (k1[m] * k2[n] + k2[m] * k1[n])
                                              for m in range(4) for n in range(4)))
