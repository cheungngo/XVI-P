#!/usr/bin/env python3
"""XVI-P p14 Deliverable 3: the one-loop counterterm DOMAIN at kappa^1 and kappa^2 (an order-bounded EFT const
  +> raint
list; NOT an admission -- XIV-J and XV-B are not opened).

Mechanical enumeration (no hand-written basis):
  * species table (dimension, ghost number, phi -> -phi parity, statistics) derived from S_Psi: [kappa] = -1, 
  +> every
    interaction vertex is kappa^{legs-2}  =>  the one-loop kappa^n part of Gamma_1 has exactly n external legs
  +>  and the
    local counterterm operator has mass dimension 4 + n (massless theory, no other scale in the prescription);
  * permitted external species = legs of loop-capable vertices (>= 2 quantum legs) of the verified vertex inve
  +> ntory;
  * for every admissible species pair the Lorentz-covariant two-leg structures are GENERATED from eta and the 
  +> leg
    momentum p (all index pairings), turned into GE densities X_I d_J Y_K, and represented by their ordered
    two-point vertex V[X(-p), Y(p)] (total derivatives vanish identically in this representation);
  * dimensions are exact-rational ranks.
Equivalences: sigma_0 = (S_Psi^(0), . ) (XVI-N antibracket, frozen orientation) applied to every generated
ghost-number -1, dimension-5 bilinear Xi (antifield-linear Xi = field redefinitions / canonical transformation
  +> s;
field-only Xi = s-exact gauge-fixing directions); the quotient dimension is dim D - dim(D cap Im sigma_0).
"""
from __future__ import annotations
import itertools
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
import p14_conventions as PC  # noqa: E402
import certio  # noqa: E402
from graded_jets import GE, DJ, bracket, PARITY  # noqa: E402

I = sp.I
ETA = F.ETA
# field: (mass dimension, ghost number, phi-parity (Z2), index type)   index types: 'L2' sym lower pair, 'U2' 
  +> sym upper
# pair (dual), 'U1' upper vector, 'L1' lower vector, '' scalar
SPECIES = {
    "h": (1, 0, 0, "L2"), "c": (1, 1, 0, "U1"), "cb": (1, -1, 0, "L1"), "b": (2, 0, 0, "U1"), "phi": (1, 0, 1,
  +>  ""),
    "K": (2, -1, 0, "U2"), "cs": (2, -2, 0, "L1"), "cbs": (2, 0, 0, "U1"), "bs": (1, -1, 0, "L1"), "phis": (2,
  +>  -1, 1, ""),
}
ORDER = ["h", "c", "cb", "b", "phi", "K", "cs", "cbs", "bs", "phis"]
NIDX = {"L2": 2, "U2": 2, "U1": 1, "L1": 1, "": 0}



def _num_word(n):
    w = {0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9:
  +>  "Nine",
         10: "Ten", 11: "Eleven"}
    return w.get(n, str(n))

def loop_capable_species():
    """species occurring as legs of vertices with >= 2 quantum (field) legs, from the verified inventory."""
    V = F.vertices()
    fields = {"h", "c", "cb", "b", "phi"}
    out, used = set(), {}
    for nm, vt in V.items():
        if nm in ("M0_ghost", "M_phi", "V2_grav", "V_b_b", "V_b_h"):
            continue                                  # kinetic/gauge-fixing bilinears (propagators)
        nq = sum(1 for f in vt.legs if f in fields)
        if nq >= 2 and vt.kappa_power >= 1:
            out |= set(vt.legs)
            used[nm] = vt.legs
    return out, used


# ------------------------------------------------------------------------------------------------------
def structures(slots, k):
    """all covariant structures: slots = list of (slot id, position 'L'|'U'); returns list of dicts
    {component tuple: sympy poly in p0..p3}.  p is the lower momentum p_a (d_a -> i p_a on leg 2)."""
    p = sp.symbols("p0:4")
    p2 = sum(ETA[a] * p[a] ** 2 for a in range(4))
    n = len(slots)
    out = []
    for npv in range(0, min(n, k) + 1):
        if (k - npv) % 2:
            continue
        for psl in itertools.combinations(range(n), npv):
            rest = [i for i in range(n) if i not in psl]
            for match in _matchings(rest):
                T = {}
                for comps in itertools.product(range(4), repeat=n):
                    v = p2 ** ((k - npv) // 2)
                    for i in psl:
                        a = comps[i]
                        v = v * (ETA[a] * p[a] if slots[i][1] == "L" else p[a])     # p^a for a lower slot
                    for (i, j) in match:
                        a, b = comps[i], comps[j]
                        if a != b:
                            v = 0
                            break
                        if slots[i][1] == slots[j][1]:
                            v = v * ETA[a]
                    if v != 0:
                        T[comps] = sp.expand(v)
                if T:
                    out.append(T)
    return out


def _matchings(lst):
    if not lst:
        yield []
        return
    a = lst[0]
    for i in range(1, len(lst)):
        rest = lst[1:i] + lst[i + 1:]
        for m in _matchings(rest):
            yield [(a, lst[i])] + m


def slots_of(f, base):
    t = SPECIES[f][3]
    pos = "L" if t.startswith("L") else "U"
    return [(base + j, pos) for j in range(NIDX[t])]


def gen_comp(f, comps):
    """GE generator for a tensor component; symmetric pairs map to the independent component (dual U2 source
    K^{mn} = K'_(mn)/w so that sum_{m,n} K^{mn} X_mn = sum_{m<=n} K'_(mn) X_mn)."""
    t = SPECIES[f][3]
    if t in ("L2", "U2"):
        m, n = comps
        g = GE.gen(f, (min(m, n), max(m, n)))
        return g.scale(sp.Rational(1, 2)) if (t == "U2" and m != n) else g
    if t in ("U1", "L1"):
        return GE.gen(f, comps[0])
    return GE.gen(f, ())


def density(X, Y, T, nx):
    """sum_{comps} T(comps)(p) X_{comps[:nx]} Y_{comps[nx:]} with p_a -> -i d_a acting on Y."""
    p = sp.symbols("p0:4")
    out = GE()
    for comps, poly in T.items():
        P = sp.Poly(poly, *p)
        gx = gen_comp(X, comps[:nx])
        for mon, cf in P.terms():
            J = sum(([a] * e for a, e in enumerate(mon)), [])
            gy = DJ(gen_comp(Y, comps[nx:]), J)
            out = out + (gx * gy).scale(cf * (-I) ** len(J))
    return out


def comp_range(f):
    t = SPECIES[f][3]
    if t in ("L2", "U2"):
        return [(m, n) for m in range(4) for n in range(m, 4)]
    if t in ("U1", "L1"):
        return list(range(4))
    return [()]


def two_point_vector(G, sectors):
    """coordinates of a gh-0 bilinear density: ordered two-point vertex V[X_I(-p), Y_J(p)] for every target se
  +> ctor
    (X <= Y in ORDER) -> {(sector, I, J, monomial, re|im): Fraction}."""
    p = sp.symbols("p0:4")
    pm = [-x for x in p]
    vec = {}
    for (X, Y) in sectors:
        for ci in comp_range(X):
            for cj in comp_range(Y):
                legs = []
                for f, cc, k in ((X, ci, pm), (Y, cj, list(p))):
                    if f == "h":
                        legs.append({"f": "h", "pol": {cc: 1}, "k": k})
                    elif f == "phi":
                        legs.append({"f": "phi", "pol": {(): 1}, "k": k})
                    elif PARITY[f] == 0:
                        legs.append({"f": f, "pol": {cc: 1}, "k": k})
                    else:
                        legs.append({"f": f, "c": cc, "k": k})
                v = F.pw_vertex(G, legs)
                if v == 0:
                    continue
                for t in sp.Add.make_args(sp.expand(v)):
                    num, rest = t.as_independent(*p, as_Add=False)
                    mono = tuple(sp.Poly(rest, *p).monoms()[0]) if rest != 1 else (0, 0, 0, 0)
                    for part, val in (("re", sp.re(num)), ("im", sp.im(num))):
                        if val != 0:
                            key = (X, Y, str(ci), str(cj), mono, part)
                            vec[key] = vec.get(key, Fr(0)) + Fr(int(sp.Rational(val).p), int(sp.Rational(val).
  +> q))
    return {k: v for k, v in vec.items() if v}


def rank(vectors):
    """exact rational rank (Gaussian elimination on sparse dict vectors)."""
    rows = [dict(v) for v in vectors if v]
    basis = []                       # list of (pivot key, row)
    for r in rows:
        r = dict(r)
        for piv, b in basis:
            if piv in r:
                f = r[piv] / b[piv]
                for k, v in b.items():
                    nv = r.get(k, 0) - f * v
                    if nv:
                        r[k] = nv
                    else:
                        r.pop(k, None)
        if r:
            piv = min(r)
            basis.append((piv, r))
    return len(basis)


def admissible_pairs(n, species):
    """unordered species pairs (n = 2) or singles (n = 1): ghost number 0, phi-parity even, derivative count >
  +> = 0."""
    out = []
    if n == 1:
        for f in sorted(species, key=ORDER.index):
            d, g, z, _ = SPECIES[f]
            if g == 0 and z == 0:
                out.append(((f,), 4 + n - d))
        return out
    sp_ = sorted(species, key=ORDER.index)
    for i, X in enumerate(sp_):
        for Y in sp_[i:]:
            dX, gX, zX, _ = SPECIES[X]
            dY, gY, zY, _ = SPECIES[Y]
            if X == Y and PARITY[X] == 1:
                pass
            k = 4 + n - dX - dY
            if gX + gY == 0 and (zX + zY) % 2 == 0 and k >= 0:
                out.append(((X, Y), k))
    return out


def sector_basis(X, Y, k):
    sl = slots_of(X, 0) + slots_of(Y, 10)
    nx = NIDX[SPECIES[X][3]]
    dens = [density(X, Y, T, nx) for T in structures(sl, k)]
    return [d for d in dens if not d.is_zero()]


def independent(dens, sectors):
    vecs, keep = [], []
    r0 = 0
    for d in dens:
        v = two_point_vector(d, sectors)
        r1 = rank(vecs + [v])
        if r1 > r0:
            vecs.append(v)
            keep.append(d)
            r0 = r1
    return keep, vecs


def S0_density():
    """S_Psi at kappa^0 as one GE density: ell_2 (exports, rebuilt as a GE density) + X^(0) + S_phi^(0)."""
    P = F.S_psi_parts()
    e2, _ = F.PW.load_ell(2)
    sub = {}
    for (m, n) in F.HC:
        sub[sp.Symbol(f"H{m}{n}")] = sp.Symbol(f"h{m}{n}")
        for r in range(4):
            sub[sp.Symbol(f"dH{m}{n}_{r}")] = sp.Symbol(f"h{m}{n}_d{r}")
    from graded_jets import esym, _KEY  # noqa: F401  (register jet symbols)
    for (m, n) in F.HC:
        esym(("h", (m, n), ()))
        for r in range(4):
            esym(("h", (m, n), (r,)))
    ell2 = GE.const(e2.xreplace(sub))
    return ell2 + P["X"][0] + P["phi"][0]


def S0_check(S0):
    """S_Psi^(0) density reproduces the verified kappa^0 Hessians (V2_grav all 100 components; M0 = -i q^2 del
  +> ta)."""
    q = sp.symbols("q0:4")
    qm = [-x for x in q]
    vt = F.vertices()["V2_grav"]
    mq = [[F.SP.var(r, -1) for r in range(4)], [F.SP.var(r) for r in range(4)]]
    bad = 0
    for a in F.HC:
        for b in F.HC:
            v = F.pw_vertex(S0, [{"f": "h", "pol": {a: 1}, "k": qm}, {"f": "h", "pol": {b: 1}, "k": list(q)}])
            w = F.vt_eval(vt, [{F.HIDX[a]: F.SP.const(1)}, {F.HIDX[b]: F.SP.const(1)}], mq).to_sympy(q) * I **
  +>  vt.phase
            bad += sp.expand(v - w) != 0
    q2 = sum(ETA[a] * q[a] ** 2 for a in range(4))
    gh = all(sp.expand(F.pw_vertex(S0, [{"f": "cb", "c": m, "k": qm}, {"f": "c", "c": n, "k": list(q)}])
                       - (-I * q2 if m == n else 0)) == 0 for m in range(4) for n in range(4))
    return {"hh_vs_V2_grav_mismatches": int(bad), "ghost_M0_ok": bool(gh), "ok": bool(bad == 0 and gh)}


def main():
    t0 = time.time()
    lc, used = loop_capable_species()
    permitted = sorted(lc, key=ORDER.index)
    excluded = [f for f in ORDER if f not in lc]
    # ---- kappa^1: one leg, dimension 5, momentum zero
    k1 = []
    for (f,), k in admissible_pairs(1, lc):
        k1.append({"species": f, "derivatives": k, "dimension_ok": k >= 0,
                   "surviving_mod_total_derivatives": k == 0, "reason": "a one-leg local functional with k>0 d
  +> erivatives "
                   "is a total derivative; k = 0 needs a dimension-5 field (none)"})
    k1_basis = [x for x in k1 if x["surviving_mod_total_derivatives"]]
    # ---- kappa^2: two legs, dimension 6
    pairs = admissible_pairs(2, lc)
    sectors = [pr for pr, _ in pairs]
    basis, vecs, per_sector = [], [], {}
    for (X, Y), k in pairs:
        keep, v = independent(sector_basis(X, Y, k), [(X, Y)])
        per_sector[f"{X}.{Y}"] = {"derivatives": k, "dimension": len(keep),
                                  "structures": [repr(d)[:160] for d in keep]}
        basis += keep
        vecs += [two_point_vector(d, sectors) for d in keep]
    dimD = rank(vecs)
    # ---- equivalences: sigma_0 on gh -1, dim 5 bilinears (all species incl. b, cbar*', b*')
    S0 = S0_density()
    s0chk = S0_check(S0)
    xi_pairs = []
    allsp = list(SPECIES)
    for i, X in enumerate(sorted(allsp, key=ORDER.index)):
        for Y in sorted(allsp, key=ORDER.index)[i:]:
            dX, gX, zX, _ = SPECIES[X]
            dY, gY, zY, _ = SPECIES[Y]
            k = 5 - dX - dY
            if gX + gY == -1 and (zX + zY) % 2 == 0 and k >= 0:
                xi_pairs.append(((X, Y), k))
    all_sectors = []
    for i, X in enumerate(sorted(allsp, key=ORDER.index)):
        for Y in sorted(allsp, key=ORDER.index)[i:]:
            if SPECIES[X][1] + SPECIES[Y][1] == 0 and (SPECIES[X][2] + SPECIES[Y][2]) % 2 == 0 \
                    and 6 - SPECIES[X][0] - SPECIES[Y][0] >= 0:
                all_sectors.append((X, Y))
    D_full = [two_point_vector(d, all_sectors) for d in basis]
    images, xi_rec = [], {}
    for (X, Y), k in xi_pairs:
        dens = sector_basis(X, Y, k)
        ims = []
        for d in dens:
            im = bracket(S0, d)
            ims.append(two_point_vector(im, all_sectors))
        kind = "antifield-linear (field redefinition / canonical transformation)" if \
            any(SPECIES[s][1] < 0 and s in ("K", "cs", "phis", "bs") or s == "cbs" for s in (X, Y)) else \
            "field-only (s-exact gauge-fixing direction)"
        xi_rec[f"{X}.{Y}"] = {"derivatives": k, "candidates": len(dens), "image_rank": rank(ims), "kind": kind
  +> }
        images += ims
    r_im = rank(images)
    r_sum = rank(D_full + images)
    inter = dimD + r_im - r_sum
    by_sector_cap = {}
    off = 0
    for (X, Y), k in pairs:
        n_ = per_sector[f"{X}.{Y}"]["dimension"]
        Ds = D_full[off:off + n_]
        off += n_
        by_sector_cap[f"{X}.{Y}"] = n_ + r_im - rank(Ds + images)
    rec = {
        "landmark": "XVI-P", "revision": PC.REVISION, "deliverable": "P.5 entry D3: counterterm domain",
        "kind": "order-bounded EFT constraint list (one loop, kappa^1 and kappa^2); NOT an admission",
        "XIV_J_opened": False, "XV_B_opened": False,
        "dimensions": {f: SPECIES[f][0] for f in ORDER} | {"kappa": -1},
        "ghost_numbers": {f: SPECIES[f][1] for f in ORDER},
        "phi_parity": {f: SPECIES[f][2] for f in ORDER},
        "power_counting": "every interaction vertex is kappa^{legs-2} (amplitude_rules vertex inventory) => on
  +> e-loop "
                          "kappa^n terms have n external legs and local operator dimension 4+n; massless, no o
  +> ther scale",
        "permitted_species": permitted, "excluded_species": excluded,
        "exclusion_reason": "not a leg of any loop-capable vertex (b only in kappa^0 bilinears; cbar*' only in
  +>  cbar*'.b; "
                            "b*' absent since s b = 0)",
        "loop_capable_vertices": used,
        "permitted_source_dependence": "K' only in the K'.c sector at kappa^2; c*' and phi*' enter first in th
  +> ree-leg "
                                       "terms (c*'.c.c, phi*'.c.phi) at kappa^3 (outside the order bound); cba
  +> r*', b*' "
                                       "never",
        "symmetries": ["Lorentz covariance (structures generated from eta and p; parity-odd eps structures van
  +> ish for "
                       "two-leg terms with one momentum)", "phi -> -phi (with phi*' -> -phi*')", "ghost number
  +>  0",
                       "Bose/Fermi symmetry of identical legs (ordered two-point representation)"],
        "kappa1": {"candidates": k1, "basis": k1_basis, "basis_size": len(k1_basis)},
        "kappa2": {"sectors": per_sector, "basis_size": dimD,
                   "basis_size_by_sector": {s: v["dimension"] for s, v in per_sector.items()}},
        "equivalences": {
            "total_derivatives": "built in: two-point momentum representation with momentum conservation",
            "sigma0": "sigma_0 = (S_Psi^(0), .) with the frozen XVI-N antibracket (graded_jets.bracket)",
            "S0_density_check": s0chk,
            "Xi_classes": xi_rec, "image_rank": r_im, "domain_cap_image": inter,
            "sector_cap_image": by_sector_cap,
            "candidate_directions_by_sector": {s_: per_sector[s_]["dimension"] - v for s_, v in by_sector_cap.
  +> items()},
            "quotient_dimension": dimD - inter,
            "reading": "domain elements in Im sigma_0 are removable by field redefinitions/canonical transform
  +> ations "
                       "(antifield-linear Xi) or are s-exact (field-only Xi). "
                       f"{_num_word(dimD - inter)} candidate directions modulo the computed exact equivalences
  +> , before "
                       "imposing the relevant identity constraints.",
            "cohomology_caveat": "NOT a cohomological classification: that needs D cap ker sigma_0 (the identi
  +> ty "
                                 "constraints, i.e. sigma_0-closedness of the counterterm) and the quotient "
                                 "(D cap ker sigma_0)/(D cap Im sigma_0); D cap ker sigma_0 has NOT been compu
  +> ted. The "
                                 "count above is D/(D cap Im sigma_0) only, an upper bound for the cohomologic
  +> al count",
            "D_cap_ker_sigma0_computed": False},
        "normalization_conditions": [
            "MS-bar in the declared prescription (P14_prescription_D11_matching): counterterms are pure poles 
  +> at scale mu",
            "no dimension-4 (two-derivative) counterterm at kappa^2: kappa and the h normalisation are not ren
  +> ormalised at "
            "this order -- an IMPOSED normalization condition (N4 of P14_prescription_D11_matching M3: no mu^2
  +>  p^2 or "
            "mu^4 contacts), not a consequence of masslessness, since mu is a scale; no kappa^1 counterterm (e
  +> mpty domain)",
            "finite adjustments only inside this domain; the D11 matching difference L_match is booked in the 
  +> hh sector",
            "u^R_mu (XVI-O) is never modified: no c delta"],
        "counterterm_domain_defined": False,
        "seconds": None,
    }
    expected_ok = (dimD == sum(v["dimension"] for v in per_sector.values()) and not k1_basis)
    rec["counterterm_domain_defined"] = bool(expected_ok and inter <= dimD and r_im > 0 and s0chk["ok"])
    rec["seconds"] = round(time.time() - t0, 1)
    certio.write(ROOT / "certificates" / f"{PC.CERT_PREFIX}_counterterm_domain.json", rec)
    print(json.dumps({"kappa1": len(k1_basis), "kappa2": dimD, "by_sector": rec["kappa2"]["basis_size_by_secto
  +> r"],
                      "sigma0_image_rank": r_im, "domain_cap_image": inter, "sector_cap": by_sector_cap, "quot
  +> ient": dimD - inter,
                      "Xi": {k: (v["candidates"], v["image_rank"]) for k, v in xi_rec.items()},
                      "defined": rec["counterterm_domain_defined"], "seconds": rec["seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
