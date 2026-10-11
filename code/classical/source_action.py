#!/usr/bin/env python3
"""p11 (c) [unchanged since p10]: source/antifield action built from the derived transformations.

S_ext = S_field + S_af,   S_af = sum_A sigma_A int Phi*_A (s Phi^A)   (antifield on the left)
sigma_A is SOLVED from the generator rule  (S, Phi^A) = s Phi^A  under the XVI-N bracket,
using the graded engine (no sign table imported).  Includes the nonminimal (cbar,b) pair
required by Psi.  S_field = sum_k kappa^(k-2) int ell_k  +  (1/2) int B^{mn}(h) d_m phi d_n phi,
with B = sqrt(-g) g^{-1} = eta + kappa a1 + kappa^2 a2 re-derived here and identified with the
exported XI-A a1, a2 (O2_scalar_action_authoritative).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graded_jets import GE, D, bracket, euler, comps, kappa_coeff, ghost_number  # noqa: E402
from bv_model import KAPPA, A, I, s_map, S_af, hc, ANTI  # noqa: E402
import conventions as C  # noqa: E402
import certio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GH = {"h": 0, "c": 1, "cb": -1, "b": 0, "phi": 0, "K": -1, "cs": -2, "cbs": 0, "bs": -1, "phis": -1}


def derive_sigma(s):
    """For each field: find sigma in {+1,-1} with (sigma Phi* sPhi, int mu Phi) = mu sPhi."""
    out = {}
    for f in ("h", "c", "cb", "phi"):
        found = []
        for sig in (1, -1):
            ok = True
            for c in comps(f):
                img = s[(f, c)]
                Str = (GE.gen(ANTI[f], c) * img).scale(sig)
                test = GE.gen("mu", c if not isinstance(c, tuple) or c else 0) * GE.gen(f, c)
                br = bracket(Str, test)
                ref = GE.gen("mu", c if not isinstance(c, tuple) or c else 0) * img
                if not (br - ref).is_zero():
                    ok = False
                    break
            if ok:
                found.append(sig)
        out[f] = found
    return out


def sigma_formula_check(sig):
    """Closed form: sigma_A = (-1)^{|Phi^A|}  (derived above; compared, not assumed)."""
    par = {"h": 0, "c": 1, "cb": 1, "phi": 0}
    return {f: (sig[f] == [(-1) ** par[f]]) for f in par}


def scalar_B_series():
    """B^{mn} = sqrt(-g) g^{mn} through kappa^2 at a point (algebraic in h); compare to XI-A a1,a2."""
    H = sp.Matrix(4, 4, lambda i, j: sp.Symbol(f"h{min(i,j)}{max(i,j)}"))
    eta = sp.diag(*C.ETA)
    k = KAPPA
    g = eta + k * H
    ginv = eta - k * eta * H * eta + k**2 * eta * H * eta * H * eta
    det = sp.expand(g.det())
    sq = sp.series(sp.sqrt(-det), k, 0, 3).removeO()
    B = (sq * ginv).applyfunc(lambda e: sp.expand(sp.series(sp.expand(e), k, 0, 3).removeO()))
    hup = eta * H * eta
    tau = sum(eta[i, i] * H[i, i] for i in range(4))
    gg = sum(H[i, j] * hup[i, j] for i in range(4) for j in range(4))
    a1 = sp.Rational(1, 2) * tau * eta - hup
    b2 = sp.Rational(1, 8) * tau**2 - sp.Rational(1, 4) * gg
    hmix = eta * H  # h^mu_rho
    a2 = hmix * hup - sp.Rational(1, 2) * tau * hup + b2 * eta
    ok1 = all(sp.expand(B[i, j].coeff(k, 1) - a1[i, j]) == 0 for i in range(4) for j in range(4))
    ok2 = all(sp.expand(B[i, j].coeff(k, 2) - a2[i, j]) == 0 for i in range(4) for j in range(4))
    ok0 = all(sp.expand(B[i, j].coeff(k, 0) - eta[i, j]) == 0 for i in range(4) for j in range(4))
    return B, {"B0_eta": ok0, "a1_matches_XI_A": ok1, "a2_matches_XI_A": ok2}


def scalar_density(nmax=2, mutate_a2=None):
    """L_phi = 1/2 B^{mn}(h) d_m phi d_n phi as engine element through kappa^nmax."""
    B, _ = scalar_B_series()
    dphi = [D(GE.gen("phi", ()), m) for m in range(4)]
    out = GE()
    for m in range(4):
        for n in range(4):
            e = sp.expand(sum(B[m, n].coeff(KAPPA, j) * KAPPA**j for j in range(nmax + 1)))
            if mutate_a2 is not None:
                e = e + (mutate_a2 * KAPPA**2 * sp.Symbol("h00") ** 2 if (m, n) == (0, 0) else 0)
            if e == 0:
                continue
            # build GE coefficient: polynomial in undifferentiated h symbols
            coef = GE()
            P = sp.Poly(e, *[sp.Symbol(f"h{i}{j}") for i in range(4) for j in range(i, 4)])
            for mon, cc in P.terms():
                t = GE.const(cc)
                idx = 0
                for i in range(4):
                    for j in range(i, 4):
                        for _ in range(mon[idx]):
                            t = t * hc(i, j)
                        idx += 1
                coef = coef + t
            out = out + coef * dphi[m] * dphi[n]
    return out.scale(sp.Rational(1, 2))


def build_X_inv(sigma=None, drop=(), s=None):
    """Antifield + nonminimal part of the invariant extended action (antifield-linear)."""
    s = s or s_map(lam=1)
    sigma = sigma or {"h": 1, "c": -1, "cb": -1, "phi": 1}
    fields = tuple(f for f in ("h", "c", "phi", "cb") if f not in drop)
    return S_af(s, sigma, fields)


def antifield_transformations(X):
    """s Phi*_A = (S, Phi*_A) restricted to the X part (S_field part adds E_Phi(S_field))."""
    out = {}
    for f, fs in [("h", "K"), ("c", "cs"), ("cb", "cbs"), ("phi", "phis")]:
        c = comps(f)[0]
        test = GE.gen("mu", 0) * GE.gen(fs, c)
        br = bracket(X, test)
        out[f"{fs}{c}"] = {"terms": len(br.t), "kappa_orders": sorted({sp.degree(v, KAPPA) for v in br.t.values()})}
    return out


def main():
    t0 = time.time()
    s = s_map(lam=1)
    sig = derive_sigma(s)
    sig_closed = sigma_formula_check(sig)
    unique = all(len(v) == 1 for v in sig.values())
    sigma = {f: v[0] for f, v in sig.items()} if unique else None
    xvin = {"h": 1, "phi": 1, "c": -1, "cb": -1}
    matches_xvin = sigma == xvin
    X = build_X_inv(sigma)
    gh = ghost_number(X, GH)
    by_kappa = {n: len(kappa_coeff(X, KAPPA, n).t) for n in range(4)}
    _, Bchk = scalar_B_series()
    aft = antifield_transformations(X)
    passed = bool(unique and matches_xvin and all(sig_closed.values()) and gh == {0}
                  and all(Bchk.values()) and by_kappa[2] == 0 and by_kappa[3] == 0)
    cert = {
        "revision": C.REVISION, "gate": "P13_source_action",
        "bracket": C.ANTIBRACKET, "generator_rule": C.GENERATOR_RULE,
        "sigma_solutions": sig, "sigma_unique": unique, "sigma": sigma,
        "sigma_closed_form": "sigma_A = (-1)^{|Phi^A|}  (derived: right derivative of Phi* X past X gives (-1)^{|Phi|+1}, generator rule adds -1)",
        "sigma_closed_form_check": sig_closed,
        "matches_XVI_N_S_af": matches_xvin,
        "S_af": ("int K^{mn}(s h)_mn + int phi*(s phi) - int c*_mu (s c^mu) - int cbar*^mu (s cbar_mu)"
                 " = int K^{mn}[a(d_m c_n+d_n c_m) + kappa a (L_c h)_mn] + kappa a int phi* c.d phi"
                 " - kappa a int c*_mu c^r d_r c^mu - i int cbar*^mu b_mu"),
        "K_vs_symmetric_hstar": "K^{mn} = w_mn h*^{mn}, w=1 (m=n), 2 (m<n); pairing over all 16 components",
        "nonminimal_included": True, "b_star_term": "absent (s b = 0)",
        "X_terms_by_kappa_order": by_kappa,
        "X_kappa2_terms": by_kappa[2],
        "X_ghost_number": sorted(gh),
        "antifield_linear": True,
        "antifield_transformations_X_part": aft,
        "S_field": {"grav": C.S_EH, "scalar": C.S_SCALAR, "scalar_B_identification": Bchk,
                    "grav_identification": "exports/ell{2,3,4}_generating_polynomial.srepr (sha in P13_quartic_verified)"},
        "baseline": C.BASELINE,
        "execution_pass": passed, "claim_status": "source_action_constructed" if passed else "incomplete",
        "scope": "S_inv extended action through O(kappa^2), antifield-linear (closed algebra), nonminimal (cbar,b) pair",
        "pass": passed, "seconds": round(time.time() - t0, 2),
    }
    (ROOT / "certificates" / "P13_source_action.json").write_text(certio.dumps(cert))
    print(json.dumps({"pass": passed, "sigma": sig, "gh": sorted(gh), "by_kappa": by_kappa, "B": Bchk,
                      "sec": cert["seconds"]}, indent=1, default=str))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
