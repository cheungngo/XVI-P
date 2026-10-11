#!/usr/bin/env python3
"""p11 C3: the boundary identity  sqrt(-g) R - L_GG = - d_mu B^mu  (CORRECTED orientation), exact in sympy.

Definitions (Ricci convention of the former, now archived, ell4_verify.py, kept verbatim):
  G^r_{mn} = 1/2 g^{rs}(d_m g_{sn} + d_n g_{sm} - d_s g_{mn})
  R^r_{s m n} = d_m G^r_{n s} - d_n G^r_{m s} + G^r_{m l} G^l_{n s} - G^r_{n l} G^l_{m s},  R_{sn} = R^r_{s r n},
  R = g^{sn} R_{sn};   L_GG = sqrt(-g) g^{mn}(G^a_{mb}G^b_{na} - G^a_{mn}G^b_{ab});
  B^mu = sqrt(-g)(g^{mu nu} G^l_{nu l} - g^{l nu} G^mu_{l nu}).

(0) VACUITY of the p09/p10 C3: on g = eta + A(x0) e_00 e_00 only G^0_00 != 0 and R = L_GG = B = 0, so the old
    check compared 0 with 0 (it could not detect the orientation error).
(i) Orientation: the correct statement is sqrt(-g)R - L_GG + d_mu B^mu = 0; "+ d_mu B^mu" (p09/p10) is wrong.
(ii) Nontrivial conformal control: g = f(x0,x1,x2,x3) eta, generic f, exact:
     sqrt(-g)R = -3 Box f + (3/(2f))(df)^2, L_GG = (3/(2f))(df)^2, B^mu = 3 d^mu f; the old orientation leaves -6 Box f.
(iii) Generic jet proof (all 10 metric components, symbolic first and second jets, exact polynomial ring over QQ):
     with G^{ab} the inverse metric as 10 free symmetric symbols, d_c G^{ab} := -G^{ar} d_c g_{rs} G^{sb} (from
     G g = 1) and the Jacobi lemma d_mu sqrt(-g) = (1/2) sqrt(-g) G^{ab} d_mu g_{ab}, the identity divided by
     sqrt(-g) reads   R - l + d_mu b^mu + (1/2) G^{ab} d_mu g_{ab} b^mu = 0   (L_GG = sqrt(-g) l, B = sqrt(-g) b),
     which is verified as an IDENTICALLY vanishing polynomial in 10 + 40 + 100 variables (it holds even for free G).
     Jacobi lemma: d/dt det(g + t delta)|_0 = tr(adj(g) delta) and adj(g) g = det(g) 1, polynomial identities in
     10 + 10 generic symmetric symbols; hence d ln(-det g) = G^{ab} dg_{ab} on G = g^{-1}.
Consequence: S_EH = -(2/kappa^2) int sqrt(-g)R = -(2/kappa^2) int L_GG for compactly supported h (a divergence
integrates to zero whatever its sign), so the integrated-action identification of ell_k is UNAFFECTED by the
orientation correction; only the stated boundary vector orientation changes.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import conventions as C  # noqa: E402
import certio  # noqa: E402

ETA = C.ETA
X = sp.symbols("x0:4")


def _geom(g, ginv, sq):
    Gam = [[[sp.simplify(sum(ginv[r, s] * (sp.diff(g[s, n], X[m]) + sp.diff(g[s, m], X[n]) - sp.diff(g[m, n], X[s]))
                             for s in range(4)) / 2) for n in range(4)] for m in range(4)] for r in range(4)]

    def riem(r, sig, m, n):
        e = sp.diff(Gam[r][n][sig], X[m]) - sp.diff(Gam[r][m][sig], X[n])
        e += sum(Gam[r][m][l] * Gam[l][n][sig] - Gam[r][n][l] * Gam[l][m][sig] for l in range(4))
        return e
    Ric = sp.Matrix(4, 4, lambda s, n: sum(riem(r, s, r, n) for r in range(4)))
    SR = sp.simplify(sq * sum(ginv[a, b] * Ric[a, b] for a in range(4) for b in range(4)))
    L = 0
    for mu in range(4):
        for nu in range(4):
            L += ginv[mu, nu] * (sum(Gam[a][mu][b] * Gam[b][nu][a] for a in range(4) for b in range(4))
                                 - sum(Gam[a][mu][nu] * Gam[b][a][b] for a in range(4) for b in range(4)))
    L = sp.simplify(sq * L)
    B = [sp.simplify(sq * sum(ginv[mu, nu] * Gam[l][nu][l] - ginv[l, nu] * Gam[mu][l][nu]
                              for nu in range(4) for l in range(4))) for mu in range(4)]
    divB = sp.simplify(sum(sp.diff(B[m], X[m]) for m in range(4)))
    return Gam, SR, L, B, divB


def vacuity_of_old_support():
    A = sp.Function("A")(X[0])
    eta = sp.diag(*ETA)
    H = sp.zeros(4)
    H[0, 0] = A
    g = eta + H
    Gam, SR, L, B, divB = _geom(g, g.inv(), sp.sqrt(-g.det()))
    nz = [f"G^{r}_{m}{n}" for r in range(4) for m in range(4) for n in range(m, 4) if sp.simplify(Gam[r][m][n]) != 0]
    return {"support": "g = eta + A(x0) e_00 (p09/p10 C3)", "nonzero_Christoffels": nz,
            "sqrt_g_R": str(SR), "L_GG": str(L), "B": [str(b) for b in B], "div_B": str(divB),
            "vacuous": SR == 0 and L == 0 and all(b == 0 for b in B) and divB == 0,
            "why": "locally flat: x0 -> int sqrt(1+A) dx0 removes A; Gamma^0_00 alone gives R = 0, both GammaGamma "
                   "contractions equal (Gamma^0_00)^2 g^00 and cancel, and B^0 = sqrt(-g)(g^00 G^0_00 - g^00 G^0_00) = 0. "
                   "The p10 source comment 'keeps dB nontrivial' was false."}


def conformal_control(orientation=+1):
    """orientation=+1: sqrt(-g)R - L + dB (correct); orientation=-1: sqrt(-g)R - L - dB (p09/p10 statement)."""
    f = sp.Function("f")(*X)
    eta = sp.diag(*ETA)
    Gam, SR, L, B, divB = _geom(f * eta, eta / f, f ** 2)
    box = sum(ETA[m] * sp.diff(f, X[m], 2) for m in range(4))
    df2 = sum(ETA[m] * sp.diff(f, X[m]) ** 2 for m in range(4))
    resid = sp.simplify(SR - L + orientation * divB)
    return {
        "metric": "g = f(x0,x1,x2,x3) eta, generic f (all four coordinates), exact",
        "orientation": "sqrt(-g)R - L_GG + d_mu B^mu" if orientation > 0 else "sqrt(-g)R - L_GG - d_mu B^mu (p09/p10)",
        "residual": str(resid), "residual_zero": resid == 0,
        "closed_forms_verified": {
            "sqrt(-g)R = -3 Box f + (3/(2f))(df)^2": sp.simplify(SR - (-3 * box + sp.Rational(3, 2) * df2 / f)) == 0,
            "L_GG = (3/(2f))(df)^2": sp.simplify(L - sp.Rational(3, 2) * df2 / f) == 0,
            "B^mu = 3 d^mu f": all(sp.simplify(B[m] - 3 * ETA[m] * sp.diff(f, X[m])) == 0 for m in range(4)),
        },
        "nontrivial": SR != 0 and L != 0 and divB != 0 and any(b != 0 for b in B),
    }


def _ring_setup():
    from sympy.polys.rings import ring
    from sympy import QQ
    IDX = [(a, b) for a in range(4) for b in range(a, 4)]
    names = ([f"G{a}{b}" for a, b in IDX] + [f"g{c}_{a}{b}" for c in range(4) for a, b in IDX]
             + [f"gg{c}{d}_{a}{b}" for c in range(4) for d in range(c, 4) for a, b in IDX])
    R_, *gens = ring(",".join(names), QQ)
    return R_, dict(zip(names, gens)), QQ


def generic_jet_proof(orientation=+1):
    t0 = time.time()
    R_, V, QQ = _ring_setup()
    S = lambda a, b: (min(a, b), max(a, b))  # noqa: E731
    G = lambda a, b: V["G%d%d" % S(a, b)]  # noqa: E731
    dg = lambda c, a, b: V["g%d_%d%d" % ((c,) + S(a, b))]  # noqa: E731

    def ddg(c, d, a, b):
        c, d = min(c, d), max(c, d)
        return V["gg%d%d_%d%d" % ((c, d) + S(a, b))]
    Z = R_(0)
    r4 = range(4)
    dG = {(c, a, b): sum((-G(a, r) * dg(c, r, s) * G(s, b) for r in r4 for s in r4), Z) for c in r4 for a in r4 for b in r4}
    T = lambda m, s, n: dg(m, s, n) + dg(n, s, m) - dg(s, m, n)  # noqa: E731
    dT = lambda c, m, s, n: ddg(c, m, s, n) + ddg(c, n, s, m) - ddg(c, s, m, n)  # noqa: E731
    half = QQ(1, 2)
    Gam = {(r, m, n): sum((G(r, s) * T(m, s, n) for s in r4), Z) * half for r in r4 for m in r4 for n in r4}
    dGam = {(c, r, m, n): sum((dG[(c, r, s)] * T(m, s, n) + G(r, s) * dT(c, m, s, n) for s in r4), Z) * half
            for c in r4 for r in r4 for m in r4 for n in r4}

    def riem(r, sig, m, n):
        e = dGam[(m, r, n, sig)] - dGam[(n, r, m, sig)]
        for l in r4:
            e += Gam[(r, m, l)] * Gam[(l, n, sig)] - Gam[(r, n, l)] * Gam[(l, m, sig)]
        return e
    Ric = {(s, n): sum((riem(r, s, r, n) for r in r4), Z) for s in r4 for n in r4}
    Rs = sum((G(a, b) * Ric[(a, b)] for a in r4 for b in r4), Z)
    trG = [sum((Gam[(b, a, b)] for b in r4), Z) for a in r4]
    ell = Z
    for mu in r4:
        for nu in r4:
            ell += G(mu, nu) * (sum((Gam[(a, mu, b)] * Gam[(b, nu, a)] for a in r4 for b in r4), Z)
                                - sum((Gam[(a, mu, nu)] * trG[a] for a in r4), Z))
    b = [sum((G(mu, nu) * trG[nu] - sum((G(l, nu) * Gam[(mu, l, nu)] for l in r4), Z) for nu in r4), Z) for mu in r4]
    dtrG = {(c, a): sum((dGam[(c, bb, a, bb)] for bb in r4), Z) for c in r4 for a in r4}
    divb = Z
    for mu in r4:
        for nu in r4:
            divb += dG[(mu, mu, nu)] * trG[nu] + G(mu, nu) * dtrG[(mu, nu)]
            for l in r4:
                divb -= dG[(mu, l, nu)] * Gam[(mu, l, nu)] + G(l, nu) * dGam[(mu, mu, l, nu)]
    jac = [sum((G(a, bb) * dg(m, a, bb) for a in r4 for bb in r4), Z) * half for m in r4]
    divB_over_sqrt = divb + sum((jac[m] * b[m] for m in r4), Z)        # (1/sqrt(-g)) d_mu (sqrt(-g) b^mu)
    resid = Rs - ell + orientation * divB_over_sqrt
    return {"variables": {"inverse_metric_free_symmetric": 10, "first_jets": 40, "second_jets": 100},
            "orientation": "+d_mu B^mu (correct)" if orientation > 0 else "-d_mu B^mu (p09/p10)",
            "terms": {"R": len(Rs.terms()), "l": len(ell.terms()), "div_b": len(divb.terms())},
            "residual_terms": len(resid.terms()), "identically_zero": resid == 0,
            "holds_for_free_G": resid == 0, "seconds": round(time.time() - t0, 2)}


def jacobi_lemma():
    """d/dt det(g + t d)|_0 = tr(adj(g) d)  and  adj(g) g = det(g) 1 for generic symmetric g, d (10 + 10 symbols)."""
    gs = sp.Matrix(4, 4, lambda a, b: sp.Symbol(f"q{min(a, b)}{max(a, b)}"))
    ds = sp.Matrix(4, 4, lambda a, b: sp.Symbol(f"d{min(a, b)}{max(a, b)}"))
    t = sp.Symbol("t")
    det = (gs + t * ds).det(method="berkowitz")
    lhs = sp.expand(sp.diff(det, t).subs(t, 0))
    adj = gs.adjugate()
    rhs = sp.expand(sum(adj[a, b] * ds[b, a] for a in range(4) for b in range(4)))
    adj_ok = sp.expand(adj * gs - gs.det() * sp.eye(4)) == sp.zeros(4, 4)
    return {"derivative_of_det_equals_tr_adj": sp.expand(lhs - rhs) == 0, "adj_g_equals_det_one": adj_ok,
            "consequence": "d_mu sqrt(-g) = (1/2) sqrt(-g) g^{ab} d_mu g_ab ; d_c g^{ab} = - g^{ar} d_c g_rs g^{sb}"}


def run():
    t0 = time.time()
    vac = vacuity_of_old_support()
    conf = conformal_control(+1)
    conf_old = conformal_control(-1)
    gen = generic_jet_proof(+1)
    gen_old = generic_jet_proof(-1)
    jac = jacobi_lemma()
    ok = (vac["vacuous"] and conf["residual_zero"] and conf["nontrivial"] and all(conf["closed_forms_verified"].values())
          and not conf_old["residual_zero"] and gen["identically_zero"] and not gen_old["identically_zero"]
          and jac["derivative_of_det_equals_tr_adj"] and jac["adj_g_equals_det_one"])
    return {
        "revision": C.REVISION, "gate": "C3_boundary_identity",
        "statement": C.BOUNDARY_IDENTITY, "L_GG": C.L_GG,
        "orientation_correction": "p09/p10 stated sqrt(-q)R - L_GG = + d_mu B^mu; correct is - d_mu B^mu",
        "old_C3_vacuity": vac,
        "conformal_control_correct_orientation": conf,
        "conformal_control_old_orientation_fails": {"residual": conf_old["residual"], "fails": not conf_old["residual_zero"],
                                                    "equals": "-6 Box f"},
        "generic_jet_proof": gen, "generic_jet_proof_old_orientation": gen_old,
        "jacobi_lemma": jac,
        "integrated_action_unaffected": ("int d_mu B^mu = 0 under compact support for either sign, so "
                                         "S_EH = -(2/kappa^2) int L_GG and ell_k = -2[eps^k]L_GG are unchanged"),
        "evidence_kind": "deterministic exact symbolic (sympy; polynomial ring over QQ for (iii))",
        "C3_proved": ok, "execution_pass": True, "claim_status": "proved" if ok else "Partial",
        "scope": "exact non-perturbative identity on the jet space of a generic metric (any signature-compatible g)",
        "seconds": round(time.time() - t0, 1),
    }


def main():
    cert = run()
    (ROOT / "certificates" / f"{C.CERT_PREFIX}_boundary_identity.json").write_text(certio.dumps(cert))
    print(json.dumps({k: cert[k] for k in ("C3_proved", "seconds")}, indent=1),
          cert["generic_jet_proof"]["residual_terms"], cert["generic_jet_proof_old_orientation"]["residual_terms"])
    return 0 if cert["C3_proved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
