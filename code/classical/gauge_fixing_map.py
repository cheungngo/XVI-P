#!/usr/bin/env python3
"""p11 (a): gauge-fixing map from Psi = -i int cbar_mu (2 D^mu[h] - b^mu), in transformed variables.

Derived here (graded engine + exact plane waves), nothing imported:
  * odd left/right derivatives of Psi agree (Psi odd);
  * S_af(Phi* = dPsi/dPhi) = - s Psi  (mod d) under the XVI-N bracket and derived sigma_A;
  * shift orientation eps in  Phi* = Phi*' + eps dPsi/dPhi  is fixed by requiring the transformed
    Hessians to equal the stated propagator kernels (K = -Box P, ghost i cbar Box c, scalar -Box);
  * canonicity of the map (bracket preservation) on ALL 23 antifield components (276 pairs + 23 mixed);
  * Hessians for a GENERIC symbolic momentum k (p11): Schur complement of the b-block equals k^2 P identically
    and, by the block-inverse formula, (M^{-1})_hh = (k^2 P)^{-1} (deterministic; no momentum sample);
  * transformed action S_Psi(Phi,Phi*') = S(Phi, Phi*' + eps dPsi/dPhi) keeps external antifields;
  * inverse map; Gamma_Psi(Phi,Phi*') := Gamma(Phi, Phi*' + eps dPsi/dPhi) is a DEFINED classical
    pullback/interface, NOT an independently established quantum gauge-change theorem.
"""
from __future__ import annotations
import json, os, random, sys, time
from fractions import Fraction as Fr
from pathlib import Path
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graded_jets import (GE, D, bracket, euler, comps, kappa_coeff, subst, s_apply,  # noqa: E402
                         is_divergence, divergence_residual, ghost_number, _KEY, H_COMPS)
from bv_model import KAPPA, A, I, s_map, Psi_density, delta_Psi, hc, cv, deDonder_of, lie_sym  # noqa: E402
from source_action import build_X_inv, scalar_density  # noqa: E402
import planewave_exact as PW  # noqa: E402
import conventions as C  # noqa: E402
import certio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GH = {"h": 0, "c": 1, "cb": -1, "b": 0, "phi": 0, "K": -1, "cs": -2, "cbs": 0, "bs": -1, "phis": -1,
      "lam": 0, "mu": 0}
ANTI_OF = {"h": "K", "c": "cs", "cb": "cbs", "b": "bs", "phi": "phis"}


def shift_map(Psi, eps, mutate=None):
    """Old antifields in terms of new: Phi*_A = Phi*'_A + eps dPsi/dPhi^A."""
    dP = delta_Psi(Psi, "L")
    km = {}
    for (f, c), v in dP.items():
        if mutate == "halve_offdiag_h" and f == "h" and c[0] != c[1]:
            v = v.scale(sp.Rational(1, 2))
        km[(ANTI_OF[f], c)] = GE.gen(ANTI_OF[f], c) + v.scale(eps)
    return km


def transformed_X(X_inv, Psi, eps, mutate=None):
    return subst(X_inv, shift_map(Psi, eps, mutate))


def field_only(F):
    """Set every antifield to zero."""
    zero = {(af, c): GE() for af in ("K", "cs", "cbs", "bs", "phis") for c in comps(af)}
    return subst(F, zero)


# ---------- plane-wave bilinear forms of even quadratic GE densities ----------
def pw_bilinear(F, w1, w2):
    """F even, quadratic in even fields. w = {field: (pol dict comp->Fr, k list)}.
    Returns coefficient of t1 t2 with d -> i k (exact, sympy)."""
    t1, t2 = sp.symbols("t1 t2")
    subs = {}
    for coef in F.t.values():
        for s_ in coef.free_symbols:
            kk = _KEY.get(s_)
            if kk is None:
                continue
            f, c, J = kk
            val = 0
            for t, w in ((t1, w1), (t2, w2)):
                if f in w:
                    pol, k = w[f]
                    v = sp.Rational(pol.get(c, 0))
                    for j in J:
                        v *= I * sp.sympify(k[j])
                    val += t * v
            subs[s_] = val
    tot = sum(sp.expand(v.xreplace(subs)) for key, v in F.t.items() if key == ())
    return sp.expand(tot).coeff(t1, 1).coeff(t2, 1)


def basis_waves(k):
    out = []
    for (m, n) in H_COMPS:
        out.append(("h", (m, n), {"h": ({(m, n): Fr(1)}, k)}))
    for mu in range(4):
        out.append(("b", mu, {"b": ({mu: Fr(1)}, k)}))
    return out


_ELL2 = {}


def ell2_bilinear_symbolic(e1, e2, k):
    """ell2 bilinear on symmetric basis tensors, legs (e1, k) and (e2, -k), symbolic k; d -> i k."""
    if "e" not in _ELL2:
        _ELL2["e"] = PW.load_ell(2)[0]
    t1, t2 = sp.symbols("t1 t2")
    sub = {}
    for m, n in H_COMPS:
        a = (1 if (m, n) == e1 else 0)
        b = (1 if (m, n) == e2 else 0)
        sub[sp.Symbol(f"H{m}{n}")] = t1 * a + t2 * b
        for r in range(4):
            sub[sp.Symbol(f"dH{m}{n}_{r}")] = t1 * a * I * k[r] - t2 * b * I * k[r]
    return sp.expand(sp.expand(_ELL2["e"].xreplace(sub)).coeff(t1, 1).coeff(t2, 1))


def ell2_bilinear(cp2, e1, e2, k):
    """Exact ell2 bilinear on symmetric basis tensors (uniform 2 derivatives: i*(-i)=+1 for k,-k)."""
    def E(mn):
        e = [[Fr(0)] * 4 for _ in range(4)]
        e[mn[0]][mn[1]] = e[mn[1]][mn[0]] = Fr(1)
        return e
    km = [-x for x in k]
    val = PW.polarize(lambda j: PW.eval_poly(cp2, j), [PW.tensor_jet(E(e1), k), PW.tensor_jet(E(e2), km)])
    return sp.Rational(-val.numerator, val.denominator)   # i^2 = -1 stripped factor


def P_bilinear(e1, e2):
    def E(mn):
        e = [[0] * 4 for _ in range(4)]
        e[mn[0]][mn[1]] = e[mn[1]][mn[0]] = 1
        return e
    a, b = E(e1), E(e2)
    dot = sum(C.ETA[m] * C.ETA[n] * a[m][n] * b[m][n] for m in range(4) for n in range(4))
    t1 = sum(C.ETA[m] * a[m][m] for m in range(4))
    t2 = sum(C.ETA[m] * b[m][m] for m in range(4))
    return sp.Rational(dot) - sp.Rational(1, 2) * t1 * t2


def hessian_check(gf_density, cp2=None, k=None):
    """(h,b) block Hessian of ell2 + gf for GENERIC symbolic k = (k0,k1,k2,k3): exact identities in Q(k).
    M = [[A, B], [C, D]] (h|b).  If det D != 0 and S = A - B D^{-1} C is invertible, the block-inverse formula gives
    (M^{-1})_hh = S^{-1}.  We prove S = k^2 P identically, so the hh propagator is (k^2 P)^{-1} = P^{-1}/k^2."""
    ks = list(sp.symbols("k0:4")) if k is None else k
    km = [-x for x in ks]
    basis = basis_waves(ks)
    n = len(basis)
    M = sp.zeros(n, n)
    for i, (fi, ci, wi) in enumerate(basis):
        for j, (fj, cj, wj) in enumerate(basis):
            w2 = {f: (pol, km) for f, (pol, _) in wj.items()}
            v = pw_bilinear(gf_density, wi, w2)
            if fi == "h" and fj == "h":
                v += ell2_bilinear_symbolic(ci, cj, ks)
            M[i, j] = sp.expand(v)
    k2 = sp.expand(sum(C.ETA[r] * ks[r] ** 2 for r in range(4)))
    Mhh, Mhb, Mbh, Mbb = M[:10, :10], M[:10, 10:], M[10:, :10], M[10:, 10:]
    dD = sp.factor(Mbb.det())
    res = {"momentum": "generic symbolic k = (k0,k1,k2,k3); identities in Q(k) (no sample)",
           "det_Mbb": str(dD), "Mbb_det_nonzero": dD != 0}
    if dD != 0:
        K = (Mhh - Mhb * Mbb.inv() * Mbh).applyfunc(sp.cancel)
        Pm = sp.Matrix(10, 10, lambda i, j: k2 * P_bilinear(H_COMPS[i], H_COMPS[j]))
        res["schur_equals_k2P"] = (K - Pm).applyfunc(sp.cancel) == sp.zeros(10, 10)
        detP = sp.factor(Pm.det())
        res["det_k2P"] = str(detP)
        res["propagator_hh_equals_inv_k2P"] = bool(res["schur_equals_k2P"] and detP != 0)
        res["propagator_argument"] = "block-inverse formula: (M^{-1})_hh = (A - B D^{-1} C)^{-1} = (k^2 P)^{-1}"
    else:
        res["schur_equals_k2P"] = False
        res["propagator_hh_equals_inv_k2P"] = False
    return res


def box(F):
    acc = GE()
    for r in range(4):
        acc = acc + D(D(F, r), r).scale(C.ETA[r])
    return acc


def ghost_kinetic_check(Xf0, sign_expected=1):
    """E^L_{cbar_mu}(field-only kappa^0) == i Box c^mu (stated XVI-N V2_ghost)."""
    ok = True
    for mu in range(4):
        lhs = euler(Xf0, "cb", mu, "L")
        rhs = box(cv(mu)).scale(I * sign_expected)
        ok &= (lhs - rhs).is_zero()
    return ok


def ghost_graviton_vertex_check(Xf1):
    """E^L_{cbar_mu}(field-only kappa^1) == 2 i a D^mu[L_c h] (XVI-N V3_cbar_c_h factor kappa*2ia)."""
    xi = [cv(r) for r in range(4)]
    Lch = lie_sym(xi, [[hc(m, n) for n in range(4)] for m in range(4)])
    DL = deDonder_of(Lch)
    ok = True
    for mu in range(4):
        lhs = euler(Xf1, "cb", mu, "L")
        rhs = DL[mu].scale(2 * I * A)
        ok &= (lhs - rhs).is_zero()
    return ok


def canonicity(Psi, eps, mutate=None):
    """(Phi*'_A, Phi*'_B) ~ 0 and (Phi*'_A, Phi^B) = (Phi*_A, Phi^B) with smeared even tests."""
    new = {}
    dP = delta_Psi(Psi, "L")
    for (f, c), v in dP.items():
        if mutate == "halve_offdiag_h" and f == "h" and c[0] != c[1]:
            v = v.scale(sp.Rational(1, 2))
        new[(ANTI_OF[f], c)] = GE.gen(ANTI_OF[f], c) - v.scale(eps)   # Phi*' = Phi* - eps dPsi
    keys = ([("K", mn) for mn in H_COMPS] + [("cbs", m) for m in range(4)] + [("bs", m) for m in range(4)]
            + [("cs", m) for m in range(4)] + [("phis", ())])
    fails = []
    for i, ka in enumerate(keys):
        for kb in keys[i:]:
            F = GE.gen("lam", 0) * new[ka]
            G = GE.gen("mu", 0) * new[kb]
            if not is_divergence(bracket(F, G)):
                fails.append(f"({ka},{kb})")
    mixed = []
    for ka in keys:
        f = {v: k for k, v in ANTI_OF.items()}[ka[0]]
        F = GE.gen("lam", 0) * new[ka]
        G = GE.gen("mu", 0) * GE.gen(f, ka[1])
        Fo = GE.gen("lam", 0) * GE.gen(ka[0], ka[1])
        if not (bracket(F, G) - bracket(Fo, G)).is_zero():
            mixed.append(str(ka))
    return {"antifield_antifield_fails": fails, "antifield_field_fails": mixed,
            "pass": not fails and not mixed, "pairs_tested": len(keys) * (len(keys) + 1) // 2 + len(keys)}


def build(eps_override=None, mutate=None):
    s = s_map(lam=1)
    X_inv = build_X_inv()
    Psi = Psi_density()
    out = {}
    out["Psi_parity_odd"] = Psi.parity_terms() == {1}
    out["Psi_ghost_number"] = sorted(ghost_number(Psi, GH))
    dL, dR = delta_Psi(Psi, "L"), delta_Psi(Psi, "R")
    out["left_equals_right_for_odd_Psi"] = all((dL[k] - dR[k]).is_zero() for k in dL)
    out["dPsi"] = {
        "dPsi/dh_mn": "2i (d^(m cbar^n) - 1/2 eta^{mn} d.cbar) * w_mn-pairing (independent comps m<=n)",
        "dPsi/dcbar_mu": "-i (2 D^mu[h] - b^mu)", "dPsi/db_mu": "+i cbar^mu", "dPsi/dc": "0", "dPsi/dphi": "0"}
    out["dPsi_nonzero_components"] = sorted(f"{f}{c}" for (f, c), v in dL.items() if not v.is_zero())
    sPsi = s_apply(Psi, s)
    SafdPsi = subst(X_inv, {(ANTI_OF[f], c): v for (f, c), v in dL.items()})
    SafdPsi = field_only(SafdPsi)
    rel_minus = is_divergence(SafdPsi + sPsi)
    rel_plus = is_divergence(SafdPsi - sPsi)
    out["S_af_at_dPsi_vs_sPsi"] = {"S_af(dPsi) ~ -sPsi": rel_minus, "S_af(dPsi) ~ +sPsi": rel_plus}
    # Hessian-based orientation
    cp2 = None
    k = list(sp.symbols("k0:4"))
    orient = {}
    for eps in (1, -1):
        Xt = transformed_X(X_inv, Psi, eps)
        Xf = field_only(Xt)
        Xf0 = kappa_coeff(Xf, KAPPA, 0)
        gf_hb = GE({key: v for key, v in Xf0.t.items() if key == ()})
        hess = hessian_check(gf_hb, cp2, k)
        orient[eps] = {"hessian": hess, "ghost_kinetic_i_box": ghost_kinetic_check(Xf0)}
    good = [e for e, d in orient.items()
            if d["hessian"]["schur_equals_k2P"] and d["hessian"]["propagator_hh_equals_inv_k2P"]
            and d["ghost_kinetic_i_box"]]
    eps = eps_override if eps_override is not None else (good[0] if len(good) == 1 else None)
    out["orientation_scan"] = {str(e): d for e, d in orient.items()}
    out["derived_eps"] = good[0] if len(good) == 1 else None
    out["map"] = {
        "fields": "Phi'^A = Phi^A (all fields unchanged)",
        "antifields": f"Phi*_A = Phi*'_A + ({eps}) dPsi/dPhi^A   i.e.  Phi*'_A = Phi*_A - ({eps}) dPsi/dPhi^A",
        "inverse": f"Phi^A = Phi'^A ; Phi*'_A = Phi*_A - ({eps}) dPsi/dPhi^A",
        "explicit": {"K'^{mn}": f"K^{{mn}} - ({eps}) dPsi/dh_mn", "cbar*'^mu": f"cbar*^mu - ({eps})(-i)(2D^mu[h]-b^mu)",
                     "b*'^mu": f"b*^mu - ({eps})(i cbar^mu)", "c*'": "c*", "phi*'": "phi*"},
    }
    if eps is None:
        out["pass"] = False
        return out, None
    Xt = transformed_X(X_inv, Psi, eps, mutate)
    out["S_Psi_equals_S_plus_sPsi_mod_d"] = is_divergence(field_only(Xt) - sPsi) if True else None
    Xf = field_only(Xt)
    out["gauge_fixed_pieces"] = {
        "kappa0_ghost_kinetic_i_box": ghost_kinetic_check(kappa_coeff(Xf, KAPPA, 0)),
        "kappa1_ghost_graviton_2ia_D[L_c h]": ghost_graviton_vertex_check(kappa_coeff(Xf, KAPPA, 1)),
        "kappa2_field_only_terms": len(kappa_coeff(Xf, KAPPA, 2).t),
        "kappa2_ghost_vertex_absent_derived": len(kappa_coeff(Xf, KAPPA, 2).t) == 0,
        "b_sector": "b(2D-b): eliminating b gives +D_mu D^mu",
    }
    hess = orient[eps]["hessian"]
    Ssc = scalar_density(0)
    ph = pw_bilinear(Ssc, {"phi": ({(): Fr(1)}, k)}, {"phi": ({(): Fr(1)}, [-x for x in k])})
    k2 = sum(C.ETA[r] * k[r] ** 2 for r in range(4))
    out["propagators"] = {
        "graviton": {"stated": "K = -Box P (includes S_gf)", **hess},
        "ghost": {"stated": "i cbar Box c", "match": orient[eps]["ghost_kinetic_i_box"]},
        "scalar": {"stated": "-Box (m=0)", "match": sp.simplify(ph - k2) == 0},
        "momentum": "generic symbolic (k0,k1,k2,k3)",
    }
    out["propagators_match_transformed_Hessians"] = bool(hess["schur_equals_k2P"] and hess["propagator_hh_equals_inv_k2P"]
                                                         and orient[eps]["ghost_kinetic_i_box"] and sp.simplify(ph - k2) == 0)
    out["canonicity"] = canonicity(Psi, eps, mutate)
    out["external_antifields_retained"] = sorted({x[0] for kk in Xt.t for x in kk if x[0] in ("K", "phis", "bs")} |
                                                 {str(s_)[:3] for v in Xt.t.values() for s_ in v.free_symbols
                                                  if str(s_).startswith(("cs", "cbs"))})
    out["invariant_vs_transformed_kept_separate"] = {
        "invariant_extended": "S_ext = S_field + S_af(Phi*)  [nonminimal pair included; Psi not applied]",
        "transformed": f"S_Psi(Phi,Phi*') = S_ext(Phi, Phi*' + ({eps}) dPsi/dPhi)  [external antifields retained]",
        "NOT_S_D": True}
    out["source_identity_relation"] = {
        "relation": f"Gamma_Psi(Phi,Phi*') := Gamma(Phi, Phi*' + ({eps}) dPsi/dPhi)",
        "classical_instance_verified": out["S_Psi_equals_S_plus_sPsi_mod_d"],
        "status": ("DEFINED classical pullback/interface along the canonical antifield shift; NOT an independently "
                   "established quantum gauge-change theorem (no quantum Gamma is constructed here)"),
        "ch_relevant_feed": ("cbar*-dependence of the invariant functional maps to h-dependence: "
                             f"cbar* = cbar*' + ({eps})(-i)(2D[h]-b); h*, b* shifts carry cbar (vanish on ch pattern)"),
        "related_not_identical": True}
    out["source_identity_relation_defined"] = True
    ok = bool(out["Psi_parity_odd"] and out["Psi_ghost_number"] == [-1] and out["left_equals_right_for_odd_Psi"]
              and rel_minus and not rel_plus and out["derived_eps"] == -1 and out["S_Psi_equals_S_plus_sPsi_mod_d"]
              and all(v for kk, v in out["gauge_fixed_pieces"].items() if isinstance(v, bool))
              and out["propagators_match_transformed_Hessians"] and out["canonicity"]["pass"])
    out["gauge_fixing_map_constructed"] = ok
    out["pass"] = ok
    return out, Xt


def main():
    t0 = time.time()
    muts = [m for m in os.environ.get("P13_MUTATIONS", "").split(",") if m]
    out, _ = build(mutate="halve_offdiag_h" if "alter_gf_shift" in muts else None)
    cert = {"revision": C.REVISION, "gate": "gauge_fixing_map_constructed", "Psi": C.PSI,
            **out,
            "execution_pass": True, "mutations_from_env": muts,
            "claim_status": "Constructed" if out["pass"] else "Partial",
            "scope": "classical BV gauge fixing of S_inv extended action by declared Psi; linear de Donder; through O(kappa^2)",
            "NOT_import_shift_sign": True,
            "obstruction_respected": "No insertion completion; XVI-N thm:massless-obstruction untouched; XV-B not opened; Route B not discharged",
            "seconds": round(time.time() - t0, 2)}
    (ROOT / "certificates" / "P13_gauge_fixing_map.json").write_text(certio.dumps(cert))
    print(json.dumps({k: cert[k] for k in ("pass", "derived_eps", "S_af_at_dPsi_vs_sPsi", "S_Psi_equals_S_plus_sPsi_mod_d",
                                           "gauge_fixed_pieces", "propagators_match_transformed_Hessians", "canonicity",
                                           "seconds")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
