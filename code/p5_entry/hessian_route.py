#!/usr/bin/env python3
"""XVI-P p14r W6: INDEPENDENT regeneration of D01, D02, D03, D12 from the one-loop expansion of the functional
(super)trace log of the field-dependent Hessian of S_Psi -- NOT from the Feynman-rule assembler.

Not used here: amplitude_rules.build_integrands, the rule table (S_f, loop signs, i^phase bookkeeping),
feynman.vertices(), feynman.grav_vertex/ell_terms/vt_route, feynman.propagators().
Used: the action itself -- the graviton generating polynomials ell_k (S_grav = sum_k kappa^{k-2} int ell_k, frozen
exports) differentiated by an own monomial routine, and the GE densities X^(n), S_phi^(n) of S_Psi
(feynman.S_psi_parts) differentiated by the generic plane-wave functional derivative (feynman.pw_vertex).

Weight e^{iS}.  Quadratic form S_2 = 1/2 int phi_X(-q) H_XY(q) phi_Y(q), H_XY(q) = V[X(-q), Y(q)]; G := H^{-1}.
  bosons (Gaussian, det^{-1/2}):  i Gamma_1 = -1/2 Tr log H(Phi)
     => i Gamma^{AB} = -1/2 Tr(G U2^{AB}) + 1/2 Tr(G U1^A G U1^B)
  ghosts (Berezin, det^{+1}, S_gh = cbar M c with M_{rho mu}(q) = V[cbar_rho(-q), c^mu(q)]):  i Gamma_1 = + Tr log M
     => i Gamma^{AB} = - Tr(G U1^A G U1^B)        (no cbar.c.h.h term: X^(2) = 0, checked)
with U1^A = kappa d/dh_A of the field-dependent Hessian, U2^{AB} = kappa^2 d^2/dh_A dh_B, and the trace routing
  Tr(G U_A G U_B) = sum G_XY(l) U_A[Y(-l), Z(l-p), h_A(p)] G_ZW(l-p) U_B[W(p-l), X(l), h_B(-p)].
The graviton G is the hh block of the inverse of the full 14x14 (h, b) Hessian (b has no interaction: X^(1) has no
field-only monomial, checked), computed here.  The result is compared with prefactor * N of the exported integrands
(the Feynman-rule route) component by component, exactly, as polynomials after multiplying by the denominators.
"""
from __future__ import annotations
import json
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "code" / "classical"))
import feynman as F  # noqa: E402
import planewave_exact as PW  # noqa: E402

I = sp.I
L = sp.symbols("l0:4")
P = sp.symbols("p0:4")
VARS = list(L) + list(P)
HC = list(F.HC)
HIDX = {mn: i for i, mn in enumerate(HC)}
GRAPHS = ("D01", "D02", "D03", "D12")
_REF = {}


# ---------------------------------------------------------------- own monomial differentiation of ell_k
def _ell_monomials(k):
    e, sha = PW.load_ell(k)
    gens = sorted(e.free_symbols, key=lambda s: s.name)
    out = []
    for mon, cf in sp.Poly(e, *gens).terms():
        facs = []
        for g, ex in zip(gens, mon):
            if not ex:
                continue
            nm = g.name
            if nm.startswith("dH"):
                head, r = nm[2:].split("_")
                facs += [(HIDX[(int(head[0]), int(head[1]))], int(r))] * ex
            else:
                facs += [(HIDX[(int(nm[1]), int(nm[2]))], None)] * ex
        out.append((Fr(int(cf.p), int(cf.q)), facs))
    return out, sha


def _lin(route, r):
    """component r of the leg momentum cl*l + cp*p as {var index: coeff}."""
    cl, cp = route
    d = {}
    if cl:
        d[r] = Fr(cl)
    if cp:
        d[4 + r] = Fr(cp)
    return d


def ell_table(k, routes):
    """V[h_c1(k1), ..., h_ck(kk)] of int ell_k for all component tuples; returns {comps: {(i,j): Fr}} (the two
    derivative factors give (i k)(i k) = -k k)."""
    import itertools
    mons, _ = _ell_monomials(k)
    T = {}
    perms = list(itertools.permutations(range(k)))
    for c, facs in mons:
        for perm in perms:
            comps = [None] * k
            der = []
            for (comp, r), leg in zip(facs, perm):
                comps[leg] = comp
                if r is not None:
                    der.append(_lin(routes[leg], r))
            assert len(der) == 2
            d = T.setdefault(tuple(comps), {})
            for i, a in der[0].items():
                for j, b in der[1].items():
                    key = (i, j) if i <= j else (j, i)
                    d[key] = d.get(key, 0) - c * a * b
    return {kk: {m: v for m, v in d.items() if v} for kk, d in T.items() if any(d.values())}


def _sym(d):
    return sp.Add(*[sp.Rational(v.numerator, v.denominator) * VARS[i] * VARS[j] for (i, j), v in d.items()])


# ---------------------------------------------------------------- Hessians and inverses (own)
def _pw(dens, legs):
    return F.pw_vertex(dens, legs)


def h_leg(a, k):
    return {"f": "h", "pol": {HC[a]: 1}, "k": k}


def mom(cl, cp):
    return [cl * L[r] + cp * P[r] for r in range(4)]


def graviton_inverse():
    """full (h, b) Hessian H(q) at q = l; G_hh = (H^{-1})_hh via the Schur complement; checks S = q^2 C, C const."""
    S = F.S_psi_parts()
    X0 = S["X"][0]
    q2 = sum(F.ETA[r] * L[r] ** 2 for r in range(4))
    T2 = ell_table(2, [(-1, 0), (1, 0)])
    Hhh = sp.zeros(10, 10)
    for (a, b), d in T2.items():
        Hhh[a, b] += _sym(d)
    Xhh = sp.zeros(10, 10)
    for a in range(10):
        for b in range(10):
            Xhh[a, b] = _pw(X0, [h_leg(a, mom(-1, 0)), h_leg(b, mom(1, 0))])
    Hhh = (Hhh + Xhh).applyfunc(sp.expand)
    bl = lambda r, k: {"f": "b", "pol": {r: 1}, "k": k}  # noqa: E731
    Hhb = sp.Matrix(10, 4, lambda a, r: _pw(X0, [h_leg(a, mom(-1, 0)), bl(r, mom(1, 0))]))
    Hbh = sp.Matrix(4, 10, lambda r, a: _pw(X0, [bl(r, mom(-1, 0)), h_leg(a, mom(1, 0))]))
    Hbb = sp.Matrix(4, 4, lambda r, s: _pw(X0, [bl(r, mom(-1, 0)), bl(s, mom(1, 0))]))
    bb_const = all(sp.diff(x, v) == 0 for x in Hbb for v in L)
    Schur = (Hhh - Hhb * Hbb.inv() * Hbh).applyfunc(sp.cancel)
    C = (Schur / q2).applyfunc(sp.cancel)
    C_const = all(sp.diff(x, v) == 0 for x in C for v in L)
    Cinv = C.inv()
    H = sp.BlockMatrix([[Hhh, Hhb], [Hbh, Hbb]]).as_explicit()
    # full inverse check (block formula) H * Hinv == 1
    Ghh = Cinv / q2
    Ghb = -Ghh * Hhb * Hbb.inv()
    Gbh = -Hbb.inv() * Hbh * Ghh
    Gbb = Hbb.inv() + Hbb.inv() * Hbh * Ghh * Hhb * Hbb.inv()
    G = sp.BlockMatrix([[Ghh, Ghb], [Gbh, Gbb]]).as_explicit()
    full_ok = (H * G).applyfunc(sp.cancel) == sp.eye(14)
    return {"Cinv": Cinv, "X0_hh_part_zero": Xhh == sp.zeros(10, 10), "Hbb_constant": bb_const,
            "schur_is_q2_times_constant": C_const, "full_14x14_inverse_verified": full_ok}


def ghost_inverse():
    X0 = F.S_psi_parts()["X"][0]
    q2 = sum(F.ETA[r] * L[r] ** 2 for r in range(4))
    M0 = sp.Matrix(4, 4, lambda rho, mu: _pw(X0, [{"f": "cb", "c": rho, "k": mom(-1, 0)},
                                                  {"f": "c", "c": mu, "k": mom(1, 0)}]))
    m = (M0 / q2).applyfunc(sp.cancel)
    const = all(sp.diff(x, v) == 0 for x in m for v in L)
    return {"minv": m.inv(), "M0_is_q2_times_constant": const}        # G_gh(q) = minv / q^2


def scalar_inverse():
    Ph0 = F.S_psi_parts()["phi"][0]
    q2 = sum(F.ETA[r] * L[r] ** 2 for r in range(4))
    Hphi = sp.expand(_pw(Ph0, [{"f": "phi", "pol": {(): 1}, "k": mom(-1, 0)}, {"f": "phi", "pol": {(): 1}, "k": mom(1, 0)}]))
    c = sp.cancel(Hphi / q2)
    return {"cinv": 1 / c, "Hphi_is_q2_times_constant": not c.free_symbols - {F.KAPPA}}


def structural_checks():
    S = F.S_psi_parts()
    X = S["X"]
    return {"X1_has_no_field_only_monomial (no b.h.h, h^3 in X)": () not in X[1].t,
            "X2_is_zero (no cbar.c.h.h, no ghost tadpole at kappa^2)": X[2].is_zero()}


# ---------------------------------------------------------------- the Hessian-route integrands
def reference():
    """{graph: {(A,B): numerator}} with numerator := (i Gamma^{AB} integrand) x prod of the denominators."""
    if "ref" in _REF:
        return _REF["ref"]
    t0 = time.time()
    kap = F.KAPPA
    gi, gh, sc = graviton_inverse(), ghost_inverse(), scalar_inverse()
    Ci = {(i, j): gi["Cinv"][i, j] for i in range(10) for j in range(10) if gi["Cinv"][i, j] != 0}
    Ci_cols = {}
    for (i, j), v in Ci.items():
        Ci_cols.setdefault(i, []).append((j, v))
    out = {}
    # D01: + 1/2 Tr(G U_A G U_B), U = kappa V3
    UA = ell_table(3, [(0, 1), (-1, 0), (1, -1)])     # h_A(p), Y(-l), Z(l-p)
    UB = ell_table(3, [(0, -1), (-1, 1), (1, 0)])     # h_B(-p), W(p-l), X(l)
    UAs = {k: _sym(v) for k, v in UA.items()}
    UBs = {k: _sym(v) for k, v in UB.items()}
    # W_B[(B, Z, Y)] = sum_{W,X} Cinv[Z,W] U_B[B,W,X] Cinv[X,Y]
    WB = {}
    for (B, W, X), u in UBs.items():
        for (Z, Wc) in [(z, v) for (z, w), v in Ci.items() if w == W]:
            for (Y, v2) in Ci_cols.get(X, []):
                WB[(B, Z, Y)] = WB.get((B, Z, Y), 0) + Wc * u * v2
    N = {}
    for (A, Y, Z), u in UAs.items():
        for B in range(10):
            w = WB.get((B, Z, Y))
            if w is not None:
                N[(A, B)] = N.get((A, B), 0) + u * w
    out["D01"] = {k: sp.expand(sp.Rational(1, 2) * kap ** 2 * v) for k, v in N.items()}
    # D02: - 1/2 Tr(G U2), U2 = kappa^2 V4[h_A(p), h_B(-p), Y(-l), X(l)]
    U4 = ell_table(4, [(0, 1), (0, -1), (-1, 0), (1, 0)])
    N = {}
    for (A, B, Y, X), d in U4.items():
        v = Ci.get((X, Y))
        if v is not None:
            N[(A, B)] = N.get((A, B), 0) + v * _sym(d)
    out["D02"] = {k: sp.expand(-sp.Rational(1, 2) * kap ** 2 * v) for k, v in N.items()}
    # D03: - Tr(G U_A G U_B), ghosts; U = kappa X^(1) third variation
    X1 = F.S_psi_parts()["X"][1]
    mi = gh["minv"]

    def gv(rho, mu, h, k_cb, k_c, k_h):
        return _pw(X1, [{"f": "cb", "c": rho, "k": k_cb}, {"f": "c", "c": mu, "k": k_c}, h_leg(h, k_h)])
    VA = {(r, m, a): gv(r, m, a, mom(-1, 0), mom(1, -1), mom(0, 1)) for r in range(4) for m in range(4) for a in range(10)}
    VB = {(r, m, b): gv(r, m, b, mom(-1, 1), mom(1, 0), mom(0, -1)) for r in range(4) for m in range(4) for b in range(10)}
    N = {}
    for a in range(10):
        for b in range(10):
            tot = 0
            for m1 in range(4):
                for r1 in range(4):
                    if mi[m1, r1] == 0:
                        continue
                    for m2 in range(4):
                        ua = VA[(r1, m2, a)]
                        if ua == 0:
                            continue
                        for r2 in range(4):
                            if mi[m2, r2] == 0:
                                continue
                            tot += mi[m1, r1] * ua * mi[m2, r2] * VB[(r2, m1, b)]
            tot = sp.expand(-kap ** 2 * tot)
            if tot != 0:
                N[(a, b)] = tot
    out["D03"] = N
    # D12: - 1/2 Tr(G_phi U2), U2 = kappa^2 S_phi^(2) fourth variation
    Ph2 = F.S_psi_parts()["phi"][2]
    N = {}
    for a in range(10):
        for b in range(10):
            v = _pw(Ph2, [h_leg(a, mom(0, 1)), h_leg(b, mom(0, -1)), {"f": "phi", "pol": {(): 1}, "k": mom(-1, 0)},
                          {"f": "phi", "pol": {(): 1}, "k": mom(1, 0)}])
            v = sp.expand(-sp.Rational(1, 2) * kap ** 2 * sc["cinv"] * v)
            if v != 0:
                N[(a, b)] = v
    out["D12"] = N
    meta = {"graviton_inverse": {k: v for k, v in gi.items() if k != "Cinv"},
            "ghost": {"M0_is_q2_times_constant": gh["M0_is_q2_times_constant"]},
            "scalar": {"Hphi_is_q2_times_constant": sc["Hphi_is_q2_times_constant"]},
            "structural": structural_checks(), "seconds": round(time.time() - t0, 1)}
    _REF["ref"] = (out, meta)
    return _REF["ref"]


def _assembler_side(rec):
    """prefactor * N from a Feynman-rule record (in-memory SP polys)."""
    names = {r: L[r] for r in range(4)} | {4 + r: P[r] for r in range(4)}
    return {k: sp.expand(rec["prefactor"] * v.to_sympy(names)) for k, v in rec["N"].items()}


def _export_side(g, root=ROOT):
    body = json.loads((Path(root) / "exports" / "P14_integrands" / f"{g}.json").read_text())
    pref = sp.sympify(body["prefactor"], locals={"kappa": F.KAPPA})
    vm = {str(v): v for v in VARS}
    out = {}
    for key, rows in body["numerator"].items():
        poly = sp.Add(*[sp.Rational(cf) * sp.Mul(*[vm[n] for n in names]) for names, cf in rows])
        out[tuple(int(x) for x in key.split(","))] = sp.expand(pref * poly)
    return out, body["sha256"]


def compare(mine, theirs):
    keys = set(mine) | set(theirs)
    bad = [list(k) for k in sorted(keys) if sp.expand(mine.get(k, 0) - theirs.get(k, 0)) != 0]
    return {"components": len(keys), "nonzero_components": sum(1 for k in keys if mine.get(k, 0) != 0),
            "mismatches": bad[:10], "n_mismatches": len(bad), "agree": not bad and bool(keys)}


def W6(ints):
    """control for amplitude_rules.verify: Hessian route == assembler integrands (current rules)."""
    ref, meta = reference()
    checks, detail = {}, {}
    for g in GRAPHS:
        c = compare(ref[g], _assembler_side(ints[g]))
        detail[g] = c
        checks[f"{g}_hessian_route_equals_integrand"] = c["agree"]
    for k, v in meta["graviton_inverse"].items():
        if isinstance(v, bool) and k != "X0_hh_part_zero":
            checks[f"graviton_{k}"] = v
    checks["ghost_M0_is_q2_times_constant"] = meta["ghost"]["M0_is_q2_times_constant"]
    checks.update({f"structural: {k}": v for k, v in meta["structural"].items()})
    return {"checks": checks, "pass": all(checks.values()), "detail": detail,
            "route": "Tr log of the field-dependent Hessian of S_Psi (independent of the Feynman-rule assembler)",
            "X0_hh_part_zero": meta["graviton_inverse"]["X0_hh_part_zero"], "seconds": meta["seconds"]}


def compare_exports(root=ROOT):
    ref, _ = reference()
    res = {}
    for g in GRAPHS:
        th, sha = _export_side(g, root)
        res[g] = {**compare(ref[g], th), "export_sha256": sha}
    res["all_agree"] = all(v["agree"] for v in res.values() if isinstance(v, dict))
    return res


if __name__ == "__main__":
    t0 = time.time()
    r = compare_exports()
    _, meta = reference()
    print(json.dumps({"exports": {g: {k: v for k, v in r[g].items() if k != "mismatches"} if isinstance(r[g], dict)
                                  else r[g] for g in r}, "meta": meta, "seconds": round(time.time() - t0, 1)},
                     indent=1, default=str))
    raise SystemExit(0 if r["all_agree"] else 1)
