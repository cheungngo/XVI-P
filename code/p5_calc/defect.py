#!/usr/bin/env python3
"""XVI-P p19: the projected one-loop kappa^2 ch-identity DEFECT, assembled from the evaluated inputs, and the
counterterm solve in the declared domain (P.5 identity step).

Object.  The hbar^1 kappa^2 part of (S_Psi, Gamma_Psi) projected onto the ch pattern (one c, one h; P.3 frozen
projection, ledgers/P13_ch_dependency_rows.json).  Exactly three rows survive (the other three are derived zero):
  R_hh   (S0, Gamma1^[2]) s2 K:K.c      X_hh = int (s0 h)_(mn)(p; c) G_hh^{(mn)(rs)}(p) h_(rs)(-p)
                                        inputs D01 + D02 + D03 + D11 + D12  (D02 = D12 = 0, P15_batchA)
  R_Kc   (S0, Gamma1^[2]) s1 h:h^2      X_Kc = int G_Kc_{(mn) nu}(p) c^nu(p) E^{(mn)(rs)}(p) h_(rs)(-p)
                                        input D13 (G_Kc = sum A_i(d) T_i + B_j(d) E_j, P15_D13)
  R_1pt  (S1, Gamma1^[1]) s2 K:K.c.h    one-point h tadpoles D14a-c (vanishing under the declared prescription)
  defect  Delta[c, h] = s_hh X_hh + s_Kc X_Kc + X_1pt   (s = +-1: antibracket summand orientation; reported
          independent of s when every row vanishes).
Every A(d) is kept exact in the opaque d; Laurent / MS-bar only at the end (MB = 1/eps + 2 - L):
  pole = X(4),  nonlocal (coefficient of L) = -X(4),  local finite = 2 X(4) - 2 X'(4).

Route C (covariant, exact in d): the frozen slot contractions (hh_slot.slot_value with s0 h; e2_evanescent.slot with
  the h^2 operator E of S_Psi^(0)), seven external assignments (Q4S, QdS, tilde, mixed), evanescent parts separately.
Route G (graded jets, 4D): sigma_0 = (S_Psi^(0), .) (frozen antibracket) applied to the 11 p14r domain densities D;
  ranks, D cap ker sigma_0 (never computed before p19), D cap Im sigma_0, the ch projection P_ch sigma_0, quotient
  coordinates; the Gamma1 local data (pole, local finite) in the domain coordinates.
Counterterm solve: Delta + P_ch sigma_0 (x) = 0 for x in D, part by part (pole, nonlocal, local).  A nonlocal residual
  can never be cancelled by a local counterterm (obstruction); a local residual is cancellable iff it lies in the image.
Outcomes kept separate: projected_defect_computed / projected_identity_verified (regulated Gamma1: defect zero or
  cancelled by allowed counterterms) / projected_restoration_verified (renormalised Gamma1^R = Gamma1 + MS-bar
  counterterms of the declared domain satisfies the projected identity; scope ch projection only) /
  bulk_symmetry_restored (stays false: nothing beyond the ch projection is claimed).
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
sys.path.insert(0, str(ROOT / "code" / "p5_entry"))
sys.path.insert(0, str(ROOT / "code" / "classical"))
import dred  # noqa: E402
import covariant as C  # noqa: E402
import batchC as BC  # noqa: E402
import hh_slot as H  # noqa: E402
import e2_evanescent as E2M  # noqa: E402
import d13 as D13  # noqa: E402
import p19_conventions as QC  # noqa: E402

d = dred.d
I = sp.I
EXT = dict(H.EXT, **{"c hat, h tilde": ("c^", "a~", "b~")})      # the seven external assignments (p18 H2)
STRUCT = E2M.STRUCT
PPOW = E2M.PPOW
CERT = ROOT / "certificates"


def log(m):
    print(f"[defect {time.strftime('%H:%M:%S')}] {m}", flush=True)


def s(x):
    return str(sp.factor(x)) if x != 0 else "0"


def jl(name):
    return json.loads((CERT / name).read_text())


def P(text):
    return dred.parse_d(text, {"I": I})


# ================================================================ inputs (inventory; nothing Missing -> zero)
def inventory(drop=()):
    """every graph of every surviving ch row, re-read from its own certificate; returns (ok, rows)."""
    led = json.loads((ROOT / "ledgers" / "P13_ch_dependency_rows.json").read_text())["rows"]
    surv = {r["id"]: [g.split("_")[0] for g in r["graphs"]] for r in led if str(r["status"]).startswith("surviving")}
    ba = jl("P15_batchA.json")
    bc = jl("P16_batchC.json")["graphs"]
    d13 = jl("P15_D13.json")
    d11 = jl("P18_D11.json")
    st = {g: v.get("status") for g, v in ba["graphs"].items()}
    claim = ba.get("batchA_evaluated", {}).get("claim", "")
    ev = {g: ba.get("batchA_evaluated", {}).get("execution") is True and g in claim
          for g in ("D02", "D12", "D14a", "D14b", "D14c")}
    st |= {"D01": bc["D01"]["status"], "D03": bc["D03"]["status"], "D13": d13.get("status"), "D11": d11.get("status")}
    ev |= {"D01": bc["D01"]["evaluated"] is True, "D03": bc["D03"]["evaluated"] is True,
           "D13": d13.get("D13_evaluated", {}).get("execution") is True, "D11": d11.get("D11_evaluated") is True}
    rows = []
    for rid, gs in surv.items():
        for g in gs:
            present = g not in drop
            rows.append({"row": rid, "graph": g, "present": present, "evaluated": bool(present and ev.get(g)),
                         "status": st.get(g) if present else "MISSING"})
    ok = (set(surv) == set(QC.ROWS) and all(sorted(surv[r]) == sorted(QC.ROWS[r]) for r in QC.ROWS)
          and all(r["present"] and r["evaluated"] and r["status"] and "missing" not in str(r["status"]).lower()
                  for r in rows)
          and jl("P18_hh_slot.json").get("quantum_inputs_evaluated") == "earned")
    return ok, rows


# ================================================================ Laurent
def laurent(x):
    """X(d) * MB -> pole, nonlocal (coefficient of L), local finite."""
    if x == 0:
        return {"pole": sp.Integer(0), "nonlocal_L": sp.Integer(0), "local": sp.Integer(0)}
    ex = D13.expand_coeff(x)
    return {"pole": sp.expand(ex["pole"]), "nonlocal_L": sp.expand(ex["nonlocal_L_coefficient"]),
            "local": sp.expand(ex["local"])}


# ================================================================ Route C rows
def hh_row(A, op, scale=None, drop_ev=()):
    terms = []
    for g, Ag in A.items():
        terms += H.g_terms(Ag, (scale or {}).get(g, 1), drop_evanescent=g in drop_ev)
    return {n: H.slot_value(op, terms, e) for n, e in EXT.items()}


def kc_row(A13, E):
    return {n: sp.factor(sum(A13[k] * E2M.slot(STRUCT[k], E, e, PPOW[k]) for k in STRUCT if A13.get(k, 0) != 0))
            for n, e in EXT.items()}


def assemble(Xhh, Xkc, s_hh=1, s_kc=1):
    out = {}
    for n in EXT:
        tot = sp.factor(s_hh * Xhh[n] + s_kc * Xkc[n])
        out[n] = {"exact_d_times_MB": tot, **laurent(tot)}
    return out


def is_zero(defect, parts=("pole", "nonlocal_L", "local")):
    return all(sp.expand(v[p]) == 0 for v in defect.values() for p in parts)


# ================================================================ Route C counterterm images and solve
def ct_images_C(op, E, hhbasis, ckbasis):
    """ch images of the p14r h.h (5) and c.K (3) domain directions in the slot functionals (same conventions as the
    rows: hh directions through s0 h, c.K directions through E).  c.cb and phi.phi have no ch image (Route G)."""
    imgs = []
    for k, b in enumerate(hhbasis):
        v = hh_row({"b": b["coords"]}, op)
        imgs.append(("h.h#%d" % k, {n: sp.expand(dred.substitute_d(x, 4, "defect: 4D domain direction image (local, "
                                                                     "d-free after contraction)")) if x != 0 else
                                    sp.Integer(0) for n, x in v.items()}))
    for k, b in enumerate(ckbasis):
        A = {nm: b["T_coordinates"][i] for i, nm in enumerate(("T1", "T2", "T3"))}
        v = kc_row(A, E)
        imgs.append(("c.K#%d" % k, {n: sp.expand(x) for n, x in v.items()}))
    return imgs


def _eqs(vals, unknowns=()):
    """{assignment: expression} -> list of coefficient expressions (in the external dot products)."""
    out = []
    for n, x in vals.items():
        x = sp.expand(x)
        if x == 0:
            continue
        syms = sorted(x.free_symbols - {d} - set(unknowns), key=str)
        if not syms:
            out.append(x)
            continue
        for _, cf in sp.Poly(x, *syms).terms():
            out.append(cf)
    return out


def solve_C(target, imgs):
    """find x with sum_k x_k img_k + target = 0 on all assignments (exact)."""
    xs = sp.symbols(f"x0:{len(imgs)}")
    comb = {n: sum(x * im[1][n] for x, im in zip(xs, imgs)) + target.get(n, 0) for n in EXT}
    eqs = _eqs(comb, xs)
    M = sp.Matrix([[sp.diff(e, x) for x in xs] for e in eqs]) if eqs else sp.zeros(0, len(xs))
    sol = sp.linsolve(eqs, *xs) if eqs else sp.FiniteSet(tuple(sp.Integer(0) for _ in xs))
    return {"rank": M.rank() if eqs else 0, "solvable": sol != sp.EmptySet,
            "solution": [s(v) for v in list(sol)[0]] if sol != sp.EmptySet else None}


def image_rank_C(imgs):
    xs = sp.symbols(f"x0:{len(imgs)}")
    comb = {n: sum(x * im[1][n] for x, im in zip(xs, imgs)) for n in EXT}
    eqs = _eqs(comb, xs)
    M = sp.Matrix([[sp.diff(e, x) for x in xs] for e in eqs])
    return M.rank(), [[s(v) for v in col] for col in M.nullspace()]


def classify(defect, imgs):
    """ZERO / CANCELLABLE (local finite residual in the image) / OBSTRUCTION (nonlocal or outside the image)."""
    if is_zero(defect):
        return {"outcome": "ZERO", "residual": None}
    nl = {n: v["nonlocal_L"] for n, v in defect.items()}
    if any(sp.expand(x) != 0 for x in nl.values()):
        return {"outcome": "OBSTRUCTION (nonlocal residual: the L-coefficient of the defect is nonzero; no local "
                           "counterterm can cancel it)",
                "residual": {"nonlocal_L": {n: s(x) for n, x in nl.items()}}}
    pole = solve_C({n: v["pole"] for n, v in defect.items()}, imgs)
    loc = solve_C({n: v["local"] for n, v in defect.items()}, imgs)
    if pole["solvable"] and loc["solvable"]:
        return {"outcome": "NONZERO, CANCELLABLE by a counterterm in the declared domain", "pole_solution": pole,
                "local_solution": loc, "residual": {"local": {n: s(v["local"]) for n, v in defect.items()}}}
    return {"outcome": "OBSTRUCTION (local residual outside the image of the declared domain)",
            "residual": {"pole": {n: s(v["pole"]) for n, v in defect.items()},
                         "local": {n: s(v["local"]) for n, v in defect.items()}}}


# ================================================================ Route G (graded jets)
def relations(vecs):
    """sparse exact elimination: returns (rank, list of linear relations sum_i r_i vecs_i = 0 as dicts)."""
    basis, rels = [], []
    for i, v in enumerate(vecs):
        r = dict(v)
        comb = {i: Fr(1)}
        for piv, b, cb in basis:
            if piv in r:
                f = r[piv] / b[piv]
                for k, x in b.items():
                    nv = r.get(k, 0) - f * x
                    if nv:
                        r[k] = nv
                    else:
                        r.pop(k, None)
                for k, x in cb.items():
                    nc = comb.get(k, 0) - f * x
                    if nc:
                        comb[k] = nc
                    else:
                        comb.pop(k, None)
        if r:
            basis.append((min(r), r, comb))
        else:
            rels.append(comb)
    return len(basis), rels


class QI:
    """exact element of Q(i) as a pair of Fractions (Route G works over Q(i): the p14r densities carry explicit
    factors i for odd derivative counts, so a rational re/im split can count i-multiples as independent)."""
    __slots__ = ("re", "im")

    def __init__(self, re, im=Fr(0)):
        self.re, self.im = Fr(re), Fr(im)

    def __bool__(self):
        return bool(self.re or self.im)

    def __add__(self, o):
        return QI(self.re + o.re, self.im + o.im)

    def __sub__(self, o):
        return QI(self.re - o.re, self.im - o.im)

    def __mul__(self, o):
        return QI(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    def __truediv__(self, o):
        n = o.re * o.re + o.im * o.im
        return QI((self.re * o.re + self.im * o.im) / n, (self.im * o.re - self.re * o.im) / n)

    def sym(self):
        return sp.Rational(self.re.numerator, self.re.denominator) + I * sp.Rational(self.im.numerator,
                                                                                     self.im.denominator)


def complexify(v):
    """two_point_vector {(..., 're'|'im'): Fraction} -> {(...): QI}"""
    out = {}
    for k, x in v.items():
        kk = k[:-1]
        z = out.get(kk, QI(0))
        out[kk] = z + (QI(x) if k[-1] == "re" else QI(0, x))
    return {k: z for k, z in out.items() if z}


def relations_c(vecs):
    """exact elimination over Q(i): (rank, relations sum_i r_i vecs_i = 0 with r_i in Q(i))."""
    basis, rels = [], []
    for i, v in enumerate(vecs):
        r = dict(v)
        comb = {i: QI(1)}
        for piv, b, cb in basis:
            if piv in r:
                f = r[piv] / b[piv]
                for k, x in b.items():
                    nv = r.get(k, QI(0)) - f * x
                    if nv:
                        r[k] = nv
                    else:
                        r.pop(k, None)
                for k, x in cb.items():
                    nc = comb.get(k, QI(0)) - f * x
                    if nc:
                        comb[k] = nc
                    else:
                        comb.pop(k, None)
        if r:
            basis.append((min(r), r, comb))
        else:
            rels.append(comb)
    return len(basis), rels


def _c_vec(rel, n):
    return [rel[i].sym() if i in rel else sp.Integer(0) for i in range(n)]


def _frac_vec(rel, n):
    return [sp.Rational(rel.get(i, Fr(0)).numerator, rel.get(i, Fr(0)).denominator) for i in range(n)]


def route_g_vectors():
    """the 11 p14r domain densities, sigma_0 images (ghost +1 sectors), their ch parts, the domain vectors in the
    ghost-0 sectors and the Xi images (ghost -1, dim 5 bilinears; same enumeration as P14_counterterm_domain)."""
    import counterterm_domain as CD
    from graded_jets import bracket
    lc, _ = CD.loop_capable_species()
    pairs = CD.admissible_pairs(2, lc)
    basis, labels = [], []
    for (X, Y), k in pairs:
        keep, _ = CD.independent(CD.sector_basis(X, Y, k), [(X, Y)])
        basis += keep
        labels += [f"{X}.{Y}#{i}" for i in range(len(keep))]
    S0 = CD.S0_density()
    s0chk = CD.S0_check(S0)
    O, SPC = CD.ORDER, CD.SPECIES
    gh1 = [(X, Y) for i, X in enumerate(O) for Y in O[i:]
           if SPC[X][1] + SPC[Y][1] == 1 and (SPC[X][2] + SPC[Y][2]) % 2 == 0 and 7 - SPC[X][0] - SPC[Y][0] >= 0]
    sig = [CD.two_point_vector(bracket(S0, b), gh1) for b in basis]
    ch = [{k: v for k, v in x.items() if (k[0], k[1]) == ("h", "c")} for x in sig]
    gh0 = [(X, Y) for i, X in enumerate(O) for Y in O[i:]
           if SPC[X][1] + SPC[Y][1] == 0 and (SPC[X][2] + SPC[Y][2]) % 2 == 0 and 6 - SPC[X][0] - SPC[Y][0] >= 0]
    D_full = [CD.two_point_vector(b, gh0) for b in basis]
    ims = []
    for i, X in enumerate(O):
        for Y in O[i:]:
            k = 5 - SPC[X][0] - SPC[Y][0]
            if SPC[X][1] + SPC[Y][1] == -1 and (SPC[X][2] + SPC[Y][2]) % 2 == 0 and k >= 0:
                ims += [CD.two_point_vector(bracket(S0, dn), gh0) for dn in CD.sector_basis(X, Y, k)]
    return {"labels": labels, "S0_check": s0chk, "gh1": gh1, "sig": sig, "ch": ch, "D_full": D_full, "ims": ims}


def route_g(V, field="Q(i)"):
    """ranks, D cap ker sigma_0, D cap ker P_ch sigma_0, D cap Im sigma_0, quotient -- over Q(i) (primary) or over Q
    with the re/im split of the p14r domain certificate (comparison only)."""
    cplx = field == "Q(i)"
    rel = relations_c if cplx else relations
    conv = (lambda vs: [complexify(v) for v in vs]) if cplx else (lambda vs: vs)
    vec = _c_vec if cplx else _frac_vec
    labels = V["labels"]
    n = len(labels)
    sig, ch = conv(V["sig"]), conv(V["ch"])
    r_sig, ker = rel(sig)
    r_ch, kerP = rel(ch)
    r_D, _ = rel(conv(V["D_full"]))
    r_im, _ = rel(conv(V["ims"]))
    _, rel_int = rel(conv(V["D_full"]) + conv(V["ims"]))
    cand = [vec({i: v for i, v in r.items() if i < n}, n) for r in rel_int]
    cand = [c for c in cand if any(x != 0 for x in c)]
    Wc = sp.Matrix.hstack(*[sp.Matrix(c) for c in cand]).columnspace() if cand else []
    kerV = [vec(r, n) for r in ker]
    kerPV = [vec(r, n) for r in kerP]
    K = sp.Matrix.hstack(*[sp.Matrix(v) for v in kerV]) if kerV else sp.zeros(n, 0)
    KP = sp.Matrix.hstack(*[sp.Matrix(v) for v in kerPV]) if kerPV else sp.zeros(n, 0)
    im_in_ker = all(sp.Matrix.hstack(K, w).rank() == K.rank() for w in Wc)
    im_in_kerP = all(sp.Matrix.hstack(KP, w).rank() == KP.rank() for w in Wc)
    comp, M = [], sp.Matrix.hstack(*Wc) if Wc else sp.zeros(n, 0)
    for i in range(n):
        e = sp.zeros(n, 1)
        e[i] = 1
        if sp.Matrix.hstack(M, e).rank() > M.rank():
            M = sp.Matrix.hstack(M, e)
            comp.append(i)
    Bq = sp.Matrix.hstack(*([sp.eye(n)[:, i] for i in comp] + list(Wc)))

    def quotient(v):
        c = Bq.LUsolve(sp.Matrix(v))
        return [sp.expand(c[j]) for j in range(len(comp))]

    def apply(vecs, coords):
        out = {}
        for c, v in zip(coords, vecs):
            if c == 0:
                continue
            for k, x in v.items():
                xv = x.sym() if cplx else sp.Rational(x.numerator, x.denominator)
                out[k] = sp.expand(out.get(k, 0) + c * xv)
        return {k: v for k, v in out.items() if v != 0}

    sector_rank = {}
    for sec in ("h.h", "c.cb", "c.K", "phi.phi"):
        idx = [i for i, l in enumerate(labels) if l.startswith(sec + "#")]
        sector_rank[sec] = {"dim": len(idx), "sigma0_rank": rel([sig[i] for i in idx])[0],
                            "P_ch_sigma0_rank": rel([ch[i] for i in idx])[0]}
    return {"field": field, "labels": labels, "n": n, "S0_check": V["S0_check"],
            "gh1_sectors": [f"{a}.{b}" for a, b in V["gh1"]], "dim_D": r_D, "image_rank_sigma0_on_Xi": r_im,
            "sigma0_rank_on_D": r_sig, "dim_D_cap_ker_sigma0": len(kerV), "D_cap_ker_sigma0_basis": kerV,
            "P_ch_sigma0_rank_on_D": r_ch, "dim_D_cap_ker_P_ch_sigma0": len(kerPV), "ker_P_ch_basis": kerPV,
            "dim_D_cap_Im_sigma0": len(Wc), "D_cap_Im_sigma0_basis": [list(w) for w in Wc],
            "Im_in_ker_sigma0": im_in_ker, "Im_in_ker_P_ch_sigma0": im_in_kerP,
            "cohomology_dim": len(kerV) - len(Wc), "quotient_complement": [labels[i] for i in comp],
            "quotient_dim": len(comp), "sector_ranks": sector_rank,
            "_quotient": quotient, "_apply": apply, "_sig": sig, "_ch": ch}


# ================================================================ Gamma1 local data in the domain coordinates
def hh_parts(A, graphs, basis):
    tot = {}
    for g in graphs:
        for k in BC.four_d_keys(A[g]):
            tot[k] = tot.get(k, 0) + A[g][k]
    parts = {"pole": {}, "nonlocal_L": {}, "local": {}}
    for k, v in tot.items():
        lt = laurent(v)
        for p in parts:
            parts[p][k] = lt[p]
    out = {}
    for p, vec in parts.items():
        z, ok = BC.pole_in_hh_basis(vec, basis)
        out[p] = {"z": z, "in_span": ok}
    return out


def ghost_equation_relation():
    """K1 (p19, informational): the ghost-equation operator 2 i D^rho (D13.deDonder_apply, the operator P15 verified
    on the one-loop functions: Sigma = 2 i D[G_Kc]) applied to the p14r c.K domain vertices V[K'(-p), c(p)],
    expressed in the p14r c.cb domain vertices V[cb(-p), c(p)] (same pw_vertex machinery and leg conventions as the
    P15 fits).  Returns M with 2 i D V[c.K#j] = sum_m M[j][m] V[c.cb#m]."""
    import counterterm_domain as CD
    import feynman as F
    PS = D13.PS
    ck, _ = CD.independent(CD.sector_basis("c", "K", 3), [("c", "K")])
    cb, _ = CD.independent(CD.sector_basis("cb", "c", 4), [("cb", "c")])

    def vk(dn):
        out = {}
        for ap in range(10):
            for nu in range(4):
                v = F.pw_vertex(dn, [{"f": "K", "c": D13.HC[ap], "k": [-x for x in PS]}, {"f": "c", "c": nu, "k": list(PS)}])
                if v != 0:
                    out[(ap, nu)] = sp.expand(v)
        return out

    def vc(dn):
        out = {}
        for r in range(4):
            for nu in range(4):
                v = F.pw_vertex(dn, [{"f": "cb", "c": r, "k": [-x for x in PS]}, {"f": "c", "c": nu, "k": list(PS)}])
                if v != 0:
                    out[(r, nu)] = sp.expand(v)
        return out
    VC = [vc(dn) for dn in cb]
    M = []
    for dn in ck:
        g = D13.deDonder_apply(vk(dn))
        ms = sp.symbols(f"m0:{len(VC)}")
        eqs = []
        for k in set(g) | set().union(*VC):
            e = sp.expand(g.get(k, 0) - sum(m * V.get(k, 0) for m, V in zip(ms, VC)))
            if e != 0:
                eqs += sp.Poly(e, *PS).coeffs()
        sol = sp.solve(eqs, ms, dict=True)
        M.append([sol[0].get(m) for m in ms] if sol else None)
    return M


def orientation_ratio():
    """p20 K1 fix: route-G c.cb densities come from admissible_pairs in ORDER, i.e. the pair (c, cb); the P15 Sigma
    coordinates (d13.ccb_basis) use sector_basis('cb', 'c').  pw_vertex takes ordered left derivatives, so the two
    density families differ by a Grassmann sign.  Measured here (not assumed): r_k = V[routeG c.cb#k] / V[(cb,c)#k]
    on the same ordered legs [cb(-p), c(p)], required uniform over all components."""
    import counterterm_domain as CD
    import feynman as F
    PS = D13.PS
    g, _ = CD.independent(CD.sector_basis("c", "cb", 4), [("c", "cb")])
    q, _ = CD.independent(CD.sector_basis("cb", "c", 4), [("cb", "c")])
    out = []
    for dg, dq in zip(g, q):
        rs = set()
        for r in range(4):
            for nu in range(4):
                legs = [{"f": "cb", "c": r, "k": [-x for x in PS]}, {"f": "c", "c": nu, "k": list(PS)}]
                a, b = sp.expand(F.pw_vertex(dg, legs)), sp.expand(F.pw_vertex(dq, legs))
                if a == 0 and b == 0:
                    continue
                rs.add(sp.simplify(a / b) if b != 0 else None)
        out.append(rs.pop() if len(rs) == 1 and None not in rs else None)
    return out, len(g) == len(q) == 2


def tree_controls():
    """p20 tree-level controls on S0 itself: (i) the classical ghost equation V_S0[cb(-p), c(p)] = 2 i D V_S0[K(-p),
    c(p)] with the same operator P15 verified at one loop (D13.deDonder_apply); (ii) sigma_0(S0_Kc + S0_cbc) = 0 in
    every ghost +1 sector, S0_Kc / S0_cbc = the K.c and cb.c bilinear terms of the S0 density."""
    import counterterm_domain as CD
    import feynman as F
    from graded_jets import GE, bracket, _KEY
    PS = D13.PS
    S0 = CD.S0_density()
    vk, vc = {}, {}
    for ap in range(10):
        for nu in range(4):
            v = F.pw_vertex(S0, [{"f": "K", "c": D13.HC[ap], "k": [-x for x in PS]}, {"f": "c", "c": nu, "k": list(PS)}])
            if v != 0:
                vk[(ap, nu)] = sp.expand(v)
    for r in range(4):
        for nu in range(4):
            v = F.pw_vertex(S0, [{"f": "cb", "c": r, "k": [-x for x in PS]}, {"f": "c", "c": nu, "k": list(PS)}])
            if v != 0:
                vc[(r, nu)] = sp.expand(v)
    g = D13.deDonder_apply(vk)
    ghost_eq = bool(vk) and bool(vc) and all(sp.expand(g.get(k, 0) - vc.get(k, 0)) == 0 for k in set(g) | set(vc))

    def part(fields):
        out = GE()
        out.t = {k: v for k, v in S0.t.items() if len(k) == 2 and sorted(x[0] for x in k) == sorted(fields)
                 and not any(sym in _KEY for sym in v.free_symbols)}
        return out
    Skc, Scb = part(("K", "c")), part(("cb", "c"))
    O, SPC = CD.ORDER, CD.SPECIES
    gh1 = [(X, Y) for i, X in enumerate(O) for Y in O[i:]
           if SPC[X][1] + SPC[Y][1] == 1 and (SPC[X][2] + SPC[Y][2]) % 2 == 0 and 7 - SPC[X][0] - SPC[Y][0] >= 0]
    img_sum = CD.two_point_vector(bracket(S0, Skc + Scb), gh1)
    img_kc = CD.two_point_vector(bracket(S0, Skc), gh1)
    return {"ghost_equation_tree_V_cbc_eq_2iD_V_Kc": ghost_eq,
            "S0_Kc_terms": len(Skc.t), "S0_cbc_terms": len(Scb.t),
            "sigma0_S0Kc_plus_S0cbc_entries": len(img_sum),
            "sigma0_S0Kc_alone_entries (control, nonzero)": len(img_kc),
            "ok": bool(ghost_eq and Skc.t and Scb.t and not img_sum and img_kc)}


def main(argv=()):
    import certio
    t0 = time.time()
    ok_inv, inv_rows = inventory()
    ok_missing, rows_missing = inventory(drop=("D11",))          # control: Missing is refused, never zero
    if not ok_inv:
        log("inventory incomplete: the defect is NOT assembled (projected_defect_computed not earned)")
        certio.write(CERT / f"{QC.CERT_PREFIX}_defect.json",
                     {"landmark": "XVI-P", "revision": QC.REVISION, "projected_defect_computed": "not_earned",
                      "inventory": inv_rows, "reason": "inventory incomplete"})
        return 1
    log("inputs: D01, D03, D11 covariant vertices (batchC.evaluate_graph)")
    evs = {g: BC.evaluate_graph(g) for g in QC.HH_EVALUATED}
    A = {g: evs[g]["A"] for g in QC.HH_EVALUATED}
    d13c = jl("P15_D13.json")
    A13 = {k: P(d13c["result"][k]["A_exact_d_times_MB"]) for k in STRUCT}
    A13_naive = {k: P(v) for k, v in d13c["mutations"]["drop_evanescent_Gt"]["fit_if_accepted"].items()}
    log("operators: s0 h (K.c monomial of S0), E (h^2 monomials of S0), q^2 P (mutation)")
    op, opfit, _ = H.kc_operator()
    E, fitE = E2M.operator_from_polys(E2M.S0_hh_operator())
    Egf, _ = E2M.operator_from_polys(E2M.gauge_fixed_operator())
    # ---------------- Route C rows
    log("Route C: rows exact in d (7 external assignments)")
    Xhh = hh_row(A, op)
    Xkc = kc_row(A13, E)
    ev = {g: {k: v for k, v in A[g].items() if C.is_evanescent(k[0])} for g in A}
    Xhh_ev = hh_row(ev, op)
    Xkc_ev = kc_row({k: (A13[k] if k in ("E1", "E2") else 0) for k in STRUCT}, E)
    Xhh_g = {g: hh_row({g: A[g]}, op) for g in A}
    defect = assemble(Xhh, Xkc)
    signs = {f"s_hh={a},s_Kc={b}": is_zero(assemble(Xhh, Xkc, a, b)) for a in (1, -1) for b in (1, -1)}
    E2_alone = {n: E2M.slot(STRUCT["E2"], E, e, 1) for n, e in EXT.items()}
    T1_alone = {n: E2M.slot(STRUCT["T1"], E, e, 1) for n, e in EXT.items()}
    E1_alone = {n: E2M.slot(STRUCT["E1"], E, e, 1) for n, e in EXT.items()}
    # ---------------- domain directions in the slot functionals; solve
    log("domain bases (p14r h.h and c.K) and their ch images")
    hhb = BC.hh_basis()
    ckb = D13.ck_basis()
    imgs = ct_images_C(op, E, hhb, ckb)
    rankC, nullC = image_rank_C(imgs)
    outcome = classify(defect, imgs)
    # ---------------- Route G
    log("Route G: sigma_0 on the 11 domain densities, D cap ker, D cap Im, quotient")
    V = route_g_vectors()
    G = route_g(V, "Q(i)")
    Gq = route_g(V, "Q re/im split (p14r convention)")
    lab = G["labels"]
    n = G["n"]
    # Gamma1 local data in domain coordinates
    hp = hh_parts(A, QC.HH_EVALUATED, hhb)
    ckz = {"pole": [P(x) for x in d13c["UV_pole_in_p14r_cK_basis"]["coordinates"]],
           "local": [P(x) for x in d13c["local_polynomial_in_p14r_cK_basis"]],
           "nonlocal_L": [P(x) for x in d13c["nonlocal_in_p14r_cK_basis"]]}
    gse = d13c["ghost_self_energy_pole"]
    ccbz = {"pole": [P(x) for x in gse["pole_in_p14r_c_cb_coordinates"]],
            "local": [P(gse["local"][k]) for k in ("S1", "S2")]}
    data = {}
    for p in ("pole", "nonlocal_L", "local"):
        v = [sp.Integer(0)] * n
        for i, z in enumerate(hp[p]["z"]):
            v[lab.index(f"h.h#{i}")] = z
        for i, z in enumerate(ckz[p]):
            v[lab.index(f"c.K#{i}")] = z
        data[p] = v
    # Route G defect, sector by sector (relative sector normalisation not needed: each sector vanishes by itself)
    g_def = {}
    for p, v in data.items():
        g_def[p] = {sec: G["_apply"]([G["_ch"][i] for i in range(n) if lab[i].startswith(sec)],
                                     [v[i] for i in range(n) if lab[i].startswith(sec)]) for sec in ("h.h", "c.K")}
    g_zero = all(not x for per in g_def.values() for x in per.values())
    # quotient coordinates of the Gamma1 local data (ch sectors h.h and c.K; c.cb data recorded separately)
    quot = {p: [s(x) for x in G["_quotient"](v)] for p, v in data.items()}
    # MS-bar counterterm (pole) in ker P_ch sigma_0 and its full sigma_0 image by sector
    ct = [-x for x in data["pole"]]
    ct_ch = G["_apply"](G["_ch"], ct)
    ct_sig = G["_apply"](G["_sig"], ct)
    ct_sig_sectors = sorted({f"{k[0]}.{k[1]}" for k in ct_sig})
    # informational (beyond the ch projection): with the ghost self-energy pole (P15_D13, c.cb) added with a relative
    # factor lam, is the full MS-bar counterterm sigma_0-closed (all ghost +1 sectors, incl. c.b)?
    closure = {}
    for lam in (1, -1, I, -I):
        v = list(ct)
        for i, z in enumerate(ccbz["pole"]):
            v[lab.index(f"c.cb#{i}")] = -lam * z
        closure[str(lam)] = not G["_apply"](G["_sig"], v)
    # K1: is the relative factor -1 derived?  The verified ghost equation Sigma = 2 i D[G] maps the c.K coordinates z_K
    # to c.cb coordinates z_cb = M^T z_K (derived); sigma_0-closure of the full counterterm needs, per kernel pair
    # c.cb#k + c.K#(k+1), the opposite relation.  Record both; the factor is NOT taken from any declared convention.
    log("K1: ghost-equation relation on the domain (derived, not selected)")
    Mg = ghost_equation_relation()
    Mg_ok = all(r is not None and all(x is not None for x in r) for r in Mg)
    zK = ckz["pole"]
    z_cb_derived = [sp.expand(sum(Mg[j][m] * zK[j] for j in range(len(zK)))) for m in range(len(Mg[0]))] if Mg_ok else None
    derived_matches_p15 = bool(Mg_ok and all(sp.simplify(a - b) == 0 for a, b in zip(z_cb_derived, ccbz["pole"])))
    lam_derived = None
    for lam in (1, -1, I, -I):          # which factor makes the DERIVED c.cb data equal the P15 data used in the probe
        if Mg_ok and all(sp.simplify(lam * a - b) == 0 for a, b in zip(z_cb_derived, ccbz["pole"])):
            lam_derived = lam
            break
    closure_with_derived = closure.get(str(lam_derived)) if lam_derived is not None else None
    # ---------------- p20 K1 FIX (disclosed erratum of p19): orientation.  The P15 Sigma coordinates are (cb,c)-oriented;
    # the route-G slots are (c,cb).  Convert with the MEASURED orientation ratio, then test full sigma_0 closure of the
    # complete MS-bar counterterm (h.h + c.K + c.cb) with the DERIVED relative factor (+1) and Sigma held fixed.
    log("p20: orientation ratio, tree controls, full sigma_0 closure of the complete MS-bar counterterm")
    orient, orient_ok = orientation_ratio()
    orient_ok = bool(orient_ok and all(r is not None for r in orient) and len(set(orient)) == 1)
    sig_G = {pp: [z / r for z, r in zip(ccbz[pp], orient)] for pp in ccbz} if orient_ok else None
    tree = tree_controls()

    def full_image(zhh, zck, zcb, part="pole"):
        v = [sp.Integer(0)] * n
        for i, z in enumerate(zhh):
            v[lab.index(f"h.h#{i}")] = z
        for i, z in enumerate(zck):
            v[lab.index(f"c.K#{i}")] = z
        for i, z in enumerate(zcb):
            v[lab.index(f"c.cb#{i}")] = z
        img = G["_apply"](G["_sig"], [-x for x in v])
        return {"closed": not img, "entries": len(img), "sectors": sorted({f"{k[0]}.{k[1]}" for k in img})}
    zhh_full = hp["pole"]["z"]
    full_ct = full_image(zhh_full, ckz["pole"], sig_G["pole"]) if sig_G else {"closed": False, "entries": None,
                                                                              "sectors": ["orientation not established"]}
    full_ct_unconverted = full_image(zhh_full, ckz["pole"], ccbz["pole"])        # the p19 bookkeeping error
    full_ct_without_ccb = full_image(zhh_full, ckz["pole"], [0, 0])             # the p19 package S_ct (no c.cb)
    # full-closure test as a MUTATION DETECTOR (Gamma1 data level; Sigma held fixed)

    def hh_z(graphs=("D01", "D03", "D11"), scale=None):
        AA = {g: ({k: (scale or {}).get(g, 1) * v for k, v in A[g].items()}) for g in graphs}
        return hh_parts(AA, list(graphs), hhb)["pole"]["z"]
    sg = sig_G["pole"] if sig_G else [0, 0]
    detector = {
        "drop_graph_D11": full_image(hh_z(("D01", "D03")), ckz["pole"], sg),
        "drop_graph_D13 (c.K data = 0, Sigma held fixed)": full_image(zhh_full, [0, 0, 0], sg),
        "flip_sign_Kc (c.K data -> -c.K, Sigma held fixed)": full_image(zhh_full, [-x for x in ckz["pole"]], sg),
        "drop_graph_D03": full_image(hh_z(("D01", "D11")), ckz["pole"], sg),
        "drop_graph_D01": full_image(hh_z(("D03", "D11")), ckz["pole"], sg),
        "flip_phase_D03": full_image(hh_z(scale={"D03": -1}), ckz["pole"], sg),
        "symmetry_factor_D03_x2": full_image(hh_z(scale={"D03": 2}), ckz["pole"], sg),
        "Sigma_orientation_unconverted (p19 error)": full_ct_unconverted}
    for k_, v_ in detector.items():
        v_["detected"] = not v_["closed"]
    # ---------------- mutations (each must change the outcome)
    log("mutations")
    muts = {}

    def mut(name, Xh, Xk, note):
        dm = assemble(Xh, Xk)
        o = classify(dm, imgs)
        muts[name] = {"outcome": o["outcome"], "changes_outcome": o["outcome"] != outcome["outcome"],
                      "residual": o.get("residual"), "note": note,
                      **({"finite_counterterm": o.get("local_solution")} if "local_solution" in o else {})}
    mut("drop_graph_D03", hh_row({g: A[g] for g in ("D01", "D11")}, op), Xkc, "hh row without the ghost loop D03")
    mut("drop_graph_D01", hh_row({g: A[g] for g in ("D03", "D11")}, op), Xkc, "hh row without the graviton bubble D01")
    mut("flip_phase_D03", hh_row(A, op, scale={"D03": -1}), Xkc, "relative sign of D03 flipped")
    mut("symmetry_factor_D03_x2", hh_row(A, op, scale={"D03": 2}), Xkc, "D03 doubled")
    mut("wrong_projection_trace_operator_hh", hh_row(A, H.trace_operator()), Xkc,
        "eta_mn p_v in place of s0 h (not the P.3 projection)")
    mut("wrong_projection_gauge_fixed_operator_Kc", Xhh, kc_row(A13, Egf),
        "de Donder q^2 P in place of the h^2-monomial operator E (not the P.3 projection)")
    mut("naive_4D_D03_evanescent_dropped", hh_row(A, op, drop_ev=("D03",)), Xkc, "D03 Gt parts dropped")
    mut("naive_4D_D13_Gt_dropped", Xhh, kc_row(A13_naive, E),
        "D13 evaluated with Gt dropped (P15_D13 mutation fit: T1 = -(d-4)/(16(d-1)))")
    insensitive = {}
    for name, (Xh, Xk, why) in {
            "drop_graph_D11": (hh_row({g: A[g] for g in ("D01", "D03")}, op), Xkc,
                               "D11 is transverse by itself (p_m G_D11 = 0 exactly in d): the slot cannot see it; "
                               "covered by M2 (P18) and by the inventory refusal below"),
            "drop_graph_D13": (Xhh, {nn: sp.Integer(0) for nn in EXT},
                               "A_T1 = A_E1 = 0 and T2, T3, E2 are longitudinal: D13 reaches the slot with zero; "
                               "covered by the D13 certificate (two routes, mutations)"),
            "flip_row_sign_Kc": (Xhh, {nn: -x for nn, x in Xkc.items()}, "each row vanishes separately")}.items():
        o = classify(assemble(Xh, Xk), imgs)
        insensitive[name] = {"outcome": o["outcome"], "changes_outcome": o["outcome"] != outcome["outcome"],
                             "why_blind": why}
    missing_ctrl = {"D11_removed_from_inventory": {"inventory_ok": ok_missing,
                                                   "projected_defect_computed_if_removed": "not_earned" if not
                                                   ok_missing else "earned",
                                                   "changes_outcome": not ok_missing}}
    # ---------------- controls
    p14ct = jl("P14_counterterm_domain.json")["equivalences"]
    tr18 = jl("P18_hh_slot.json")["four_D_poles"]["transverse_basis_in_p14r_coordinates"]
    hh_idx = [lab.index(f"h.h#{i}") for i in range(5)]
    kerhh = [v for v in G["ker_P_ch_basis"] if all(v[i] == 0 for i in range(n) if i not in hh_idx)]
    span_eq = (sp.Matrix([[P(x) for x in r] for r in tr18]).rank() == 2 and
               sp.Matrix([[v[i] for i in hh_idx] for v in kerhh] + [[P(x) for x in r] for r in tr18]).rank() == 2
               and len(kerhh) == 2)
    controls = {
        "inventory_complete_no_missing": ok_inv,
        "missing_input_refused_not_zero": not ok_missing,
        "s0h_longitudinal": H.longitudinal_op(op),
        "E_transverse": E2M.transversality(E)["transverse"],
        "hh_row_zero_exact_in_d_all_7": all(x == 0 for x in Xhh.values()),
        "hh_row_evanescent_part_zero_all_7": all(x == 0 for x in Xhh_ev.values()),
        "hh_row_D01_D03_individually_nonzero": any(x != 0 for x in Xhh_g["D01"].values())
                                               and any(x != 0 for x in Xhh_g["D03"].values()),
        "Kc_row_zero_exact_in_d_all_7": all(x == 0 for x in Xkc.values()),
        "Kc_row_evanescent_part_zero_all_7": all(x == 0 for x in Xkc_ev.values()),
        "Kc_slot_map_nontrivial_T1_E1": any(x != 0 for x in T1_alone.values()) and any(x != 0 for x in E1_alone.values()),
        "E2_alone_zero_all_7": all(x == 0 for x in E2_alone.values()),
        "D13_A_T1_A_E1_zero_exact": A13["T1"] == 0 and A13["E1"] == 0,
        "onepoint_row_D14abc_vanishing": all(r["status"] == "vanishing_under_declared_prescription"
                                             for r in inv_rows if r["row"] == QC.ROW_1PT),
        "defect_zero_pole_nonlocal_local_all_7": is_zero(defect),
        "defect_independent_of_row_signs": all(signs.values()),
        "routeG_S0_check": G["S0_check"]["ok"],
        "routeG_defect_zero_by_sector": g_zero,
        "routeG_hh_local_data_in_span": all(hp[p]["in_span"] for p in hp),
        "routes_agree_on_ch_image_rank": rankC == G["P_ch_sigma0_rank_on_D"],
        "routeG_hh_kernel_equals_p18_transverse_subspace": span_eq,
        "D_cap_Im_inside_D_cap_ker_sigma0": G["Im_in_ker_sigma0"],
        "D_cap_Im_inside_ker_P_ch_sigma0": G["Im_in_ker_P_ch_sigma0"],
        "ghost_equation_relation_reproduces_P15_sigma_pole": derived_matches_p15,

        "MSbar_counterterm_in_ker_P_ch_sigma0": not ct_ch,
        "mutations_all_change_outcome": all(v["changes_outcome"] for v in muts.values()),
        "routeG_Q_split_reproduces_p14r_counts": (Gq["dim_D_cap_Im_sigma0"] == p14ct["domain_cap_image"]
                                                  and Gq["quotient_dim"] == p14ct["quotient_dimension"]
                                                  and Gq["image_rank_sigma0_on_Xi"] == p14ct["image_rank"]),
    }
    computed = all(controls[k] for k in ("inventory_complete_no_missing", "missing_input_refused_not_zero",
                                         "hh_row_D01_D03_individually_nonzero", "Kc_slot_map_nontrivial_T1_E1",
                                         "routeG_S0_check", "routes_agree_on_ch_image_rank",
                                         "mutations_all_change_outcome"))
    identity = computed and all(controls.values()) and outcome["outcome"] == "ZERO"
    # projected_restoration_verified (distinct from identity): the RENORMALISED one-loop functional Gamma_R = Gamma1 +
    # S_ct (S_ct = minus the MS-bar pole in the declared domain) satisfies the projected identity in every part, i.e.
    # P_ch sigma_0(S_ct) = 0 exactly, AND the linear solve for a finite symmetry-restoring counterterm in D returns
    # x = 0 (none required).  identity alone is a statement about the regulated Gamma1.
    p20_controls = {
        "orientation_ratio_uniform_minus_one": bool(orient_ok and orient[0] == -1),
        "tree_ghost_equation_V_cbc_eq_2iD_V_Kc": tree["ghost_equation_tree_V_cbc_eq_2iD_V_Kc"],
        "tree_sigma0_S0Kc_plus_S0cbc_zero": tree["ok"],
        "derived_ghost_relation_reproduces_P15_sigma": derived_matches_p15,
        "full_closure_detects_drop_D13_and_flip_Kc": bool(
            detector["drop_graph_D13 (c.K data = 0, Sigma held fixed)"]["detected"]
            and detector["flip_sign_Kc (c.K data -> -c.K, Sigma held fixed)"]["detected"]),
        "full_closure_detects_p19_orientation_error": detector["Sigma_orientation_unconverted (p19 error)"]["detected"],
        "S_ct_without_ccb_not_closed (c.cb counterterm is needed)": not full_ct_without_ccb["closed"]}
    renormalised_defect_zero = identity and not ct_ch        # p19 criterion -> p20: route-consistency CONTROL only
    # p20 REDEFINITION (p19 reviewer: the p19 criterion follows from the identity + locality): full sigma_0 closure
    # of the COMPLETE MS-bar counterterm S_ct (h.h + c.K + c.cb, Sigma held fixed, derived factor +1, orientation
    # converted) in every ghost +1 sector (h.c, c.b, c.cbs).  Scope: the one-loop kappa^2 counterterm.
    restoration = bool(identity and full_ct["closed"] and lam_derived == 1 and all(p20_controls.values()))
    rec = {
        "landmark": "XVI-P", "revision": QC.REVISION,
        "deliverable": "P.5 identity: projected one-loop kappa^2 ch-identity defect, counterterm solve",
        "object": ("Delta[c,h] = ch projection (P.3, frozen) of the hbar kappa^2 part of (S_Psi, Gamma_Psi) = "
                   "s_hh X_hh + s_Kc X_Kc + X_1pt (rows of ledgers/P13_ch_dependency_rows.json)"),
        "prescription": "declared (P14_prescription_D11_matching; DRED R1-R6; MS-bar; MB = 1/eps + 2 - L)",
        "inventory": inv_rows,
        "rows": {
            QC.ROW_HH: {"inputs": list(QC.ROWS[QC.ROW_HH]), "functional": "X_hh = int (s0 h)_(mn) G_hh^{(mn)(rs)} h_(rs)",
                        "value_exact_d_times_MB": {k: s(v) for k, v in Xhh.items()},
                        "evanescent_part": {k: s(v) for k, v in Xhh_ev.items()},
                        "per_graph": {g: {k: s(v) for k, v in x.items()} for g, x in Xhh_g.items()}},
            QC.ROW_KC: {"inputs": ["D13"], "functional": "X_Kc = int G_Kc_{(mn) nu} c^nu E^{(mn)(rs)} h_(rs)",
                        "value_exact_d_times_MB": {k: s(v) for k, v in Xkc.items()},
                        "evanescent_part": {k: s(v) for k, v in Xkc_ev.items()},
                        "D13_coefficients": {k: s(v) for k, v in A13.items()}},
            QC.ROW_1PT: {"inputs": ["D14a", "D14b", "D14c"], "value": "0 (each one-point tadpole vanishes under the "
                         "declared prescription, P15_batchA: evaluated, not Missing)"}},
        "external_assignments": {k: list(v) for k, v in EXT.items()},
        "defect": {k: {p: s(v[p]) for p in ("exact_d_times_MB", "pole", "nonlocal_L", "local")}
                   for k, v in defect.items()},
        "defect_zero_exact_in_d": is_zero(defect),
        "defect_row_sign_independence": signs,
        "evanescent_in_assembly": ("verified explicitly: the evanescent (gt) parts of the hh row (D01+D03+D11) and of the "
                                   "K.c row (D13 E1, E2) give ZERO for all seven external assignments, exactly in d; "
                                   "the evanescent poles themselves are nonzero (P18_hh_slot, P15_D13) -- they drop "
                                   "from the ch slots by the decoupling proofs, not by convention"),
        "route_G": {k: v for k, v in G.items() if not k.startswith("_")} | {
            "D_cap_ker_sigma0_basis": [[s(x) for x in v] for v in G["D_cap_ker_sigma0_basis"]],
            "ker_P_ch_basis": [[s(x) for x in v] for v in G["ker_P_ch_basis"]],
            "D_cap_Im_sigma0_basis": [[s(x) for x in v] for v in G["D_cap_Im_sigma0_basis"]]},
        "route_G_Q_split_p14r_convention": {k: v for k, v in Gq.items() if not k.startswith("_") and k not in (
            "D_cap_ker_sigma0_basis", "ker_P_ch_basis", "D_cap_Im_sigma0_basis")},
        "field_note": ("Route G is computed over Q(i) (primary) and, for comparison, over Q with the re/im split used "
                       "by the p14r domain certificate.  The p14r densities carry explicit factors i for odd derivative "
                       "counts (c.K: 3 derivatives), so over Q an i-multiple counts as independent: e.g. the ch image "
                       "of c.K#0 is i times an h.h image.  The counts over Q(i) equal the real dimensions under a "
                       "compatible real structure (one real coefficient per density, the i fixed by reality of the "
                       "action); ranks and solvability are quoted over Q(i)."),
        "gamma1_local_data_domain_coordinates": {
            "labels": lab, "convention": ("Ghat coordinates (G = kappa^2 N_eps Ghat MB) on the p14r densities; h.h "
                                          "from D01+D03+D11 (4D structures; D02 = D12 = 0), c.K from P15_D13; c.cb "
                                          "(ghost self-energy, P15_D13) recorded separately: not a ch input "
                                          "(P_ch sigma_0 = 0 on c.cb); phi.phi not an input (sigma_0 = 0 on it)"),
            **{p: [s(x) for x in v] for p, v in data.items()},
            "c_cb_ghost_self_energy (P15 (cb,c) orientation)": {p: [s(x) for x in v] for p, v in ccbz.items()},
            "c_cb_ghost_self_energy (route-G (c,cb) orientation, p20)": (
                {p: [s(x) for x in v] for p, v in sig_G.items()} if sig_G else None)},
        "quotient_coordinates": {"complement_directions": G["quotient_complement"], **quot,
                                 "reading": ("coordinates modulo D cap Im sigma_0 (field redefinitions / s-exact); the "
                                             "h.h pole is transverse, i.e. in D cap Im sigma_0, so its quotient "
                                             "coordinates vanish")},
        "quotient_coordinates_including_Sigma": {pp: [s(x) for x in G["_quotient"](
            [v_ if not lab[i_].startswith("c.cb#") else sig_G[pp][int(lab[i_][-1])] for i_, v_ in enumerate(data[pp])])]
            for pp in ("pole", "local")} if sig_G else None,
        "quotient_coordinates_Sigma_alone_routeG": {pp: [s(x) for x in G["_quotient"](
            [sig_G[pp][int(lab[i_][-1])] if lab[i_].startswith("c.cb#") else 0 for i_ in range(n)])]
            for pp in ("pole", "local")} if sig_G else None,
        "quotient_reading_p20": ("all in route-G (c,cb) labels: 'quotient_coordinates' is the class of the h.h + c.K "
                                 "Gamma1 data WITHOUT the ghost self-energy, = -[Sigma] (c.cb entries (-3/8, 1/4)); "
                                 "Sigma itself has c.cb coordinates (+3/8, -1/4) (P15's (cb,c) numbers carry the "
                                 "opposite sign); the complete data incl. Sigma have quotient 0, consistent with "
                                 "full closure and cohomology 0.  (The p19 reviewer read the p19 entries as Sigma in "
                                 "the wrong orientation; numerically they coincide with P15's (cb,c) Sigma.)"),
        "routeG_defect_by_sector": {p: {sec: len(v) for sec, v in per.items()} for p, per in g_def.items()},
        "counterterm_solve": {
            "system": "Delta + P_ch sigma_0(x) = 0, x in the declared domain D (11 directions), part by part",
            "rank_P_ch_sigma0_routeG": G["P_ch_sigma0_rank_on_D"], "rank_routeC": rankC,
            "routeC_image_relations": nullC,
            "outcome": outcome["outcome"], "residual": outcome.get("residual"),
            "solution": "x = 0 (no counterterm needed beyond the MS-bar poles); the identity-preserving finite "
                        "renormalisations are ker(P_ch sigma_0) cap D (dim %d), of which %d modulo D cap Im sigma_0"
                        % (G["dim_D_cap_ker_P_ch_sigma0"], G["dim_D_cap_ker_P_ch_sigma0"] - G["dim_D_cap_Im_sigma0"]),
            "MSbar_counterterm_ch_image_zero": not ct_ch,
            "MSbar_counterterm_full_sigma0_image_sectors": ct_sig_sectors,
            "full_closure_relative_factor_table_UNCONVERTED_p19_error": closure,
            "full_closure_reading": ("p20 (corrects p19): with the P15 Sigma coordinates converted from the (cb,c) to the "
                                     "route-G (c,cb) orientation (measured ratio -1), the DERIVED factor +1 gives full "
                                     "sigma_0 closure of the complete MS-bar counterterm (h.h + c.K + c.cb) in every "
                                     "ghost +1 sector; the p19 table above (factors 1, -1, i, -i on UNCONVERTED "
                                     "coordinates) is the bookkeeping error, kept for the erratum"),
            "K1_ghost_closure_convention": {
                "ghost_equation_operator": "2 i D^rho (d13.deDonder_apply), verified by P15: Sigma = 2 i D[G_Kc]",
                "M_2iD_cK_to_cbc": [[s(x) for x in r] if r else None for r in Mg],
                "z_cb_derived_from_cK_pole_cbc_orientation": [s(x) for x in z_cb_derived] if z_cb_derived else None,
                "z_cb_P15_sigma_fit_cbc_orientation": [s(x) for x in ccbz["pole"]],
                "derived_equals_P15": derived_matches_p15,
                "relative_factor_derived": s(lam_derived) if lam_derived is not None else None,
                "orientation_ratio_routeG_over_cbc": [s(x) for x in orient],
                "Sigma_pole_routeG_c_cb_coordinates": [s(x) for x in sig_G["pole"]] if sig_G else None,
                "Sigma_local_routeG_c_cb_coordinates": [s(x) for x in sig_G["local"]] if sig_G else None,
                "tree_controls": tree,
                "full_closure_complete_S_ct": full_ct,
                "full_closure_S_ct_without_ccb (p19 package S_ct)": full_ct_without_ccb,
                "full_closure_unconverted (p19 error)": full_ct_unconverted,
                "reading": ("ERRATUM to p19: the p19 statement 'closure fails with the derived factor, needs -1, "
                            "unresolved' was a Grassmann-orientation bookkeeping error (P15 (cb,c) coordinates placed "
                            "in route-G (c,cb) slots).  Corrected: derived +1, full closure holds (finding K1 of the "
                            "p19 independent rebuild).")},
            "note_full_sigma0": ("the h.h + c.K MS-bar counterterm ALONE has a nonzero (c, b) image (delta S0/delta h "
                                 "carries b); adding the c.cb ghost self-energy counterterm (correct orientation, "
                                 "derived factor +1) closes it: see K1_ghost_closure_convention.full_closure_complete_S_ct")},
        "D_cap_ker_sigma0": {"computed": True, "dim": G["dim_D_cap_ker_sigma0"], "dim_D_cap_Im_sigma0":
                             G["dim_D_cap_Im_sigma0"], "cohomology_dim": G["cohomology_dim"],
                             "sector_ranks": G["sector_ranks"]},
        "mutations": muts, "insensitive_variations": insensitive, "missing_control": missing_ctrl,
        "controls": controls,
        "why_zero": ("each surviving ch row vanishes separately in the projected slot; no counterterm cancellation and no "
                     "cancellation between rows is involved: (i) hh row (D01+D02+D03+D11+D12): full-row transverse "
                     "decoupling -- D01 and D03 are individually nonzero and cancel against each other in the slot "
                     "(p17/p18 transverse sum), D11 is transverse by itself, D02 = D12 = 0; (ii) K.c row (D13): D13 "
                     "reaches the ch slot only through T1 and E1 (T2, T3, E2 are longitudinal, E transverse) and "
                     "A_T1 = A_E1 = 0 exactly in d; (iii) one-point row: the tadpoles D14a-c vanish under the declared "
                     "prescription.  The defect is therefore zero without any counterterm (solve x = 0)."),
        "rests_on": ["M2 / D11 matching verified on the 4D components only (D11_matching_verified_scope = '4D "
                     "components'; evanescent components of the D11 matching: not applicable, not verified)",
                     "the evanescent decoupling proofs (P16 E2 decoupling, P17/P18 hh evanescent / full-row decoupling)",
                     "the frozen P.3 projection and the P13 ch dependency ledger (three surviving rows)",
                     "the declared prescription (DRED R1-R6, MS-bar, P14_prescription_D11_matching)"],
        "flag_definitions": {
            "projected_defect_computed": ("Delta = P_ch[(S_Psi, Gamma_Psi)]_{hbar kappa^2} assembled from every "
                                          "evaluated input of the three surviving rows (none Missing), exact in d, "
                                          "pole + nonlocal + MS-bar local parts, all seven external assignments"),
            "projected_identity_verified": ("Delta = 0 for the REGULATED one-loop functional Gamma1: pole, nonlocal "
                                            "and local parts vanish for all seven assignments, exactly in d, with all "
                                            "controls true and every mutation changing the outcome"),
            "projected_restoration_verified": ("p20 definition (replaces p19's, which follows from the identity + "
                                               "locality): FULL sigma_0 closure of the COMPLETE one-loop kappa^2 MS-bar "
                                               "counterterm S_ct = -(pole) in the declared domain, h.h + c.K + c.cb "
                                               "(ghost self-energy Sigma held fixed at its P15 value, orientation "
                                               "converted, derived relative factor +1), in every ghost +1 sector (h.c, "
                                               "c.b, c.cbs), together with projected_identity_verified.  Scope: the "
                                               "one-loop kappa^2 counterterm only; NOT bulk symmetry, NOT O.1"),
            "bulk_symmetry_restored": "hard stop: False regardless (not claimed; O.1 NOT_CLOSED)"},
        "renormalised_defect_zero": renormalised_defect_zero,
        "route_consistency_control_p19_criterion": {
            "label": ("route-consistency control (the p19 restoration criterion, NOT a flag): P_ch sigma_0(S_ct) = 0 for "
                      "the h.h + c.K MS-bar counterterm and the solve x = 0; implied by the identity + locality"),
            "holds": bool(renormalised_defect_zero and outcome["outcome"] == "ZERO")},
        "p20_controls": p20_controls,
        "full_closure_mutation_detector": {
            "test": "full sigma_0 closure (all ghost +1 sectors) of the complete MS-bar counterterm, Sigma held fixed",
            "cases": detector,
            "reading": ("detects drop D13 and flip K.c (the p19 blind spots) through the c.b sector, and the hh-row "
                        "mutations through h.c; drop D11 stays undetected (D11 transverse => its pole is sigma_0-closed "
                        "by itself): covered by M2 (P18) and the p20 D11 normalisation pin (P20_D11_pin.json)")},
        "findings": {
            "J1_p14r_counterterm_domain_field": ("FINDING ABOUT THE p14r CONTRACT (contract NOT modified): the p14r "
                                                 "counterterm-domain counts (Im sigma_0 3, quotient 8, D cap ker 5, "
                                                 "P_ch sigma_0 rank 4) are artefacts of a re/im split over Q (the "
                                                 "densities carry explicit i for odd derivative counts, so i-multiples "
                                                 "count as independent).  The counts over Q(i) -- sigma_0 rank 5, D cap "
                                                 "ker 6, D cap Im 6, cohomology 0, quotient 5, P_ch sigma_0 rank 3 (= "
                                                 "Route C) -- equal the real dimensions under a compatible real "
                                                 "structure.  The p14r certificate stays as released; both are reported"),
            "K1_ghost_closure_sign": ("p20 CORRECTION (erratum to p19): resolved -- an orientation bookkeeping error. "
                                      "With the P15 Sigma coordinates converted to the route-G (c,cb) orientation "
                                      "(ratio -1), the derived factor +1 gives full sigma_0 closure of the complete "
                                      "MS-bar counterterm in h.c, c.b, c.cbs.  The p19 text 'closure fails / needs -1 / "
                                      "unresolved' is retracted")},
        "projected_defect_computed": "earned" if computed else "not_earned",
        "projected_identity_verified": "earned" if identity else "not_earned",
        "projected_restoration_verified": "earned" if restoration else "not_earned",
        "bulk_symmetry_restored": False,
        "corrected_in_revision": "p20 (K1 orientation fix; restoration redefined; see the p20 erratum)",
        "scope": ("ch projection only (one c, one h; one loop; kappa^2; off-shell); the evanescent poles of the hh and "
                  "K.c Green functions remain regulated (not subtracted) and decouple from the ch slots; no statement "
                  "about higher orders or bulk symmetry.  projected_restoration_verified (p20 definition) additionally "
                  "tests full sigma_0 closure of the complete one-loop kappa^2 MS-bar counterterm in all ghost +1 "
                  "sectors (h.c, c.b, c.cbs) -- a statement about that counterterm only, not bulk symmetry, not O.1"),
        "authorised_d_substitutions": dict(sorted(dred.D_PROVENANCE.items())),
        "seconds": round(time.time() - t0, 1)}
    certio.write(CERT / f"{QC.CERT_PREFIX}_defect.json", rec)
    print(json.dumps({"outcome": outcome["outcome"], "computed": computed, "identity": identity,
                      "restoration": restoration, "controls": controls,
                      "mutations": {k: [v["outcome"][:40], v["changes_outcome"]] for k, v in muts.items()},
                      "kerD": G["dim_D_cap_ker_sigma0"], "ImD": G["dim_D_cap_Im_sigma0"], "quot_dim": G["quotient_dim"],
                      "Gq": {k: Gq[k] for k in ("dim_D_cap_ker_sigma0", "dim_D_cap_Im_sigma0", "quotient_dim",
                                                "P_ch_sigma0_rank_on_D", "image_rank_sigma0_on_Xi")},
                      "sector": G["sector_ranks"], "comp": G["quotient_complement"], "rankC": rankC,
                      "rankG": G["P_ch_sigma0_rank_on_D"], "quot": quot,
                      "K1": rec["counterterm_solve"]["K1_ghost_closure_convention"], "p20_controls": p20_controls,
                      "detector": {k: [v["closed"], v["sectors"]] for k, v in detector.items()},
                      "quot_incl_Sigma": rec["quotient_coordinates_including_Sigma"], "seconds": rec["seconds"]},
                     indent=1, default=str))
    return 0 if identity else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
