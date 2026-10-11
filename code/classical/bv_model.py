#!/usr/bin/env python3
"""p10/p11 model builders on the graded jet engine: geometry -> s, source action, Psi.

Every object is built from declared geometry (conventions.py); signs that are results are
derived in brst_from_geometry.py / source_action.py / gauge_fixing_map.py, not here.
"""
from __future__ import annotations
import sympy as sp
from graded_jets import GE, D, H_COMPS, s_apply, kappa_coeff, euler, comps

ETA = (1, -1, -1, -1)
KAPPA = sp.Symbol("kappa")
A = sp.Rational(1, 2)
I = sp.I


def hc(m, n, J=()):
    return GE.gen("h", (min(m, n), max(m, n)), J)


def cv(mu, J=()):
    return GE.gen("c", mu, J)


def Dn(F, J):
    for a in J:
        F = D(F, a)
    return F


# ---------------- geometry ----------------
def metric(param="affine", kappa=KAPPA):
    """g_{mn}(h). 'affine': eta + kappa h ; 'exp2': eta + kappa h + kappa^2/2 h.eta.h (control)."""
    g = [[None] * 4 for _ in range(4)]
    for m in range(4):
        for n in range(4):
            e = GE.const(ETA[m] if m == n else 0) + hc(m, n).scale(kappa)
            if param == "exp2":
                acc = GE()
                for r in range(4):
                    acc = acc + (hc(m, r) * hc(r, n)).scale(ETA[r])
                e = e + acc.scale(kappa ** 2 / 2)
            g[m][n] = e
    return g


def lie_sym(xi, T):
    """(L_xi T)_{mn} = xi^r d_r T_mn + T_rn d_m xi^r + T_mr d_n xi^r  (xi left of T)."""
    out = [[None] * 4 for _ in range(4)]
    for m in range(4):
        for n in range(m, 4):
            acc = GE()
            for r in range(4):
                acc = acc + xi[r] * D(T[m][n], r)
                acc = acc + D(xi[r], m) * T[r][n]
                acc = acc + D(xi[r], n) * T[m][r]
            out[m][n] = out[n][m] = acc
    return out


def xi_field(kappa=KAPPA, a=A):
    return [cv(mu).scale(kappa * a) for mu in range(4)]


def ghost_ansatz(lam, kappa=KAPPA, a=A):
    """s xi^mu = lam xi^r d_r xi^mu  =>  s c^mu = (1/(kappa a)) s xi^mu."""
    xi = xi_field(kappa, a)
    out = {}
    for mu in range(4):
        acc = GE()
        for r in range(4):
            acc = acc + xi[r] * D(xi[mu], r)
        out[mu] = acc.scale(lam / (kappa * a))
    return out


def s_h_affine(kappa=KAPPA, a=A):
    """s h_{mn} = (1/kappa) L_xi g_{mn},  g = eta + kappa h (exact, all orders)."""
    g = metric("affine", kappa)
    Lg = lie_sym(xi_field(kappa, a), g)
    return {(m, n): Lg[m][n].scale(1 / kappa) for (m, n) in H_COMPS}


def s_phi(kappa=KAPPA, a=A):
    xi = xi_field(kappa, a)
    acc = GE()
    for r in range(4):
        acc = acc + xi[r] * D(GE.gen("phi", ()), r)
    return acc


def s_map(lam=1, kappa=KAPPA, a=A, nonminimal=True):
    """Full s on generators (affine parametrisation)."""
    s = {}
    for k, v in s_h_affine(kappa, a).items():
        s[("h", k)] = v
    for mu, v in ghost_ansatz(lam, kappa, a).items():
        s[("c", mu)] = v
    s[("phi", ())] = s_phi(kappa, a)
    if nonminimal:
        for mu in range(4):
            s[("cb", mu)] = GE.gen("b", mu).scale(I)
            s[("b", mu)] = GE()
    return s


def truncate_kappa(F, nmax, kappa=KAPPA):
    out = GE()
    for n in range(nmax + 1):
        out = out + kappa_coeff(F, kappa, n).scale(kappa ** n)
    return out


# --------------- source / antifield action ---------------
ANTI = {"h": "K", "c": "cs", "cb": "cbs", "b": "bs", "phi": "phis"}


def S_af(s, sigma, fields=("h", "c", "phi", "cb")):
    """S_af = sum_A sigma_A Phi*_A (s Phi^A)  (antifield written to the LEFT)."""
    out = GE()
    for f in fields:
        for c in comps(f):
            img = s.get((f, c))
            if img is None or img.is_zero():
                continue
            out = out + (GE.gen(ANTI[f], c) * img).scale(sigma[f])
    return out


# --------------- gauge fermion ---------------
def h_up(m, n):
    return hc(m, n).scale(ETA[m] * ETA[n])


def trace_h():
    acc = GE()
    for r in range(4):
        acc = acc + hc(r, r).scale(ETA[r])
    return acc


def deDonder_up(mu):
    """D^mu[h] = d_nu h^{mu nu} - 1/2 d^mu tr h."""
    acc = GE()
    for nu in range(4):
        acc = acc + D(h_up(mu, nu), nu)
    acc = acc - D(trace_h(), mu).scale(sp.Rational(1, 2) * ETA[mu])
    return acc


def deDonder_of(Tlow):
    """D^mu applied to an arbitrary symmetric lowered tensor (list of lists of GE)."""
    out = []
    for mu in range(4):
        acc = GE()
        for nu in range(4):
            acc = acc + D(Tlow[mu][nu].scale(ETA[mu] * ETA[nu]), nu)
        tr = GE()
        for r in range(4):
            tr = tr + Tlow[r][r].scale(ETA[r])
        acc = acc - D(tr, mu).scale(sp.Rational(1, 2) * ETA[mu])
        out.append(acc)
    return out


def Psi_density(coef_D=2, coef_b=1):
    """Psi = -i cbar_mu (coef_D D^mu[h] - coef_b b^mu)   (declared: coef_D=2, coef_b=1)."""
    acc = GE()
    for mu in range(4):
        bup = GE.gen("b", mu).scale(ETA[mu])
        acc = acc + GE.gen("cb", mu) * (deDonder_up(mu).scale(coef_D) - bup.scale(coef_b))
    return acc.scale(-I)


def delta_Psi(Psi, side="L"):
    """Variational derivatives of the gauge fermion w.r.t. every field component."""
    return {(f, c): euler(Psi, f, c, side) for f in ("h", "c", "cb", "b", "phi") for c in comps(f)}
