#!/usr/bin/env python3
"""
grav_density.py — EH cubic density ell_3, FP Lagrangian, A=2G_lin, Q_nu, operators.
Full 4D coordinate dependence. Exact rational sympy.
"""
from __future__ import annotations
import itertools
import sympy as sp

ETA = [1, -1, -1, -1]


def kron(i, j):
    return 1 if i == j else 0


def mz():
    return [[sp.Integer(0) for _ in range(4)] for _ in range(4)]


def tr_eta(M):
    return sum(ETA[a] * M[a][a] for a in range(4))


def raise_m(M):
    out = mz()
    for mu in range(4):
        for nu in range(4):
            out[mu][nu] = sp.expand(ETA[mu] * ETA[nu] * M[mu][nu])  # eta diagonal
    return out


def P_of(M):
    t = tr_eta(M)
    out = mz()
    for mu in range(4):
        for nu in range(4):
            out[mu][nu] = sp.expand(M[mu][nu] - sp.Rational(1, 2) * ETA[mu] * kron(mu, nu) * t)
    return out


def atoms(G):
    GU = raise_m(G)
    tau = sp.expand(tr_eta(G))
    u0 = [[ETA[i] * kron(i, j) for j in range(4)] for i in range(4)]
    u1 = [[sp.expand(-GU[i][j]) for j in range(4)] for i in range(4)]
    u2 = mz()
    for mu in range(4):
        for nu in range(4):
            acc = 0
            for lam in range(4):
                acc += ETA[mu] * G[mu][lam] * GU[lam][nu]
            u2[mu][nu] = sp.expand(acc)
    b1 = sp.Rational(1, 2) * tau
    gg = sum(G[mu][nu] * GU[mu][nu] for mu in range(4) for nu in range(4))
    b2 = sp.expand(sp.Rational(1, 8) * tau**2 - sp.Rational(1, 4) * gg)
    return u0, u1, u2, b1, b2, tau, GU


def ell3_and_curvature(G, dG, ddG):
    """
    XII-C finite curvature + ell_3 = -2(r_3+b1 r2+b2 r1).
    G[mu][nu] value, dG[a][mu][nu]=∂_a G_mu nu, ddG[a][b][mu][nu]=∂_a ∂_b G.
    Returns dict with ell3, r1,r2,r3, b1,b2, Gamma, R, J3, etc.
    """
    u0, u1, u2, b1, b2, tau, GU = atoms(G)
    Us = [u0, u1, u2]

    def Gamma(n, rho, mu, nu):
        # (1/2) u_{n-1}^{rho lam} (∂_mu G_nu lam + ∂_nu G_mu lam - ∂_lam G_mu nu)
        acc = 0
        for lam in range(4):
            term = dG[mu][nu][lam] + dG[nu][mu][lam] - dG[lam][mu][nu]
            acc += Us[n - 1][rho][lam] * term
        return sp.expand(sp.Rational(1, 2) * acc)

    # Need ∂_alpha Gamma: differentiate product
    # Gamma depends on u_{n-1}(G) and dG. For n=1, u0=const.
    def dGamma(n, rho, mu, nu, alpha):
        # ∂_alpha [ (1/2) u^{rho lam} T_lam ] with T = ∂_mu G_nu + ...
        acc = 0
        for lam in range(4):
            T = dG[mu][nu][lam] + dG[nu][mu][lam] - dG[lam][mu][nu]
            dT = ddG[alpha][mu][nu][lam] + ddG[alpha][nu][mu][lam] - ddG[alpha][lam][mu][nu]
            # ∂ u_{n-1}^{rho lam}
            if n == 1:
                du = 0
            elif n == 2:
                # u1 = -G^{rho lam} = -ETA[rho]ETA[lam] G[rho][lam]
                du = -ETA[rho] * ETA[lam] * dG[alpha][rho][lam]
            else:  # n==3, u2^{rho lam}= G^rho_s G^{s lam}
                # ∂(ETA[rho] G[rho][s] * GU[s][lam])
                du = 0
                for s in range(4):
                    du += ETA[rho] * dG[alpha][rho][s] * GU[s][lam]
                    du += ETA[rho] * G[rho][s] * ETA[s] * ETA[lam] * dG[alpha][s][lam]
            acc += du * T + Us[n - 1][rho][lam] * dT
        return sp.expand(sp.Rational(1, 2) * acc)

    Gam = {}
    dGam = {}
    for n in (1, 2, 3):
        for rho, mu, nu in itertools.product(range(4), repeat=3):
            Gam[(n, rho, mu, nu)] = Gamma(n, rho, mu, nu)
        for rho, mu, nu, al in itertools.product(range(4), repeat=4):
            dGam[(n, rho, mu, nu, al)] = dGamma(n, rho, mu, nu, al)

    def R(n, mu, nu):
        acc = 0
        for rho in range(4):
            acc += dGam[(n, rho, mu, nu, rho)] - dGam[(n, rho, mu, rho, nu)]
        for a in range(1, n):
            b = n - a
            for rho, lam in itertools.product(range(4), repeat=2):
                acc += Gam[(a, rho, rho, lam)] * Gam[(b, lam, mu, nu)]
                acc -= Gam[(a, rho, nu, lam)] * Gam[(b, lam, mu, rho)]
        return sp.expand(acc)

    def r(n):
        acc = 0
        for i in range(n):
            Rn = R(n - i, 0, 0)  # placeholder
            for mu, nu in itertools.product(range(4), repeat=2):
                acc += Us[i][mu][nu] * R(n - i, mu, nu)
        return sp.expand(acc)

    # fix r properly
    def r_n(n):
        acc = 0
        for i in range(n):
            for mu, nu in itertools.product(range(4), repeat=2):
                acc += Us[i][mu][nu] * R(n - i, mu, nu)
        return sp.expand(acc)

    r1, r2, r3 = r_n(1), r_n(2), r_n(3)
    ell = sp.expand(-2 * (r3 + b1 * r2 + b2 * r1))

    # R_n tensors for J3
    R1 = [[R(1, mu, nu) for nu in range(4)] for mu in range(4)]
    R2 = [[R(2, mu, nu) for nu in range(4)] for mu in range(4)]

    # V1_{mu nu} = R1 - 1/2 eta r1; V2 = R2 - 1/2 eta r2 - 1/2 G r1
    V1 = mz(); V2 = mz()
    for mu in range(4):
        for nu in range(4):
            V1[mu][nu] = sp.expand(R1[mu][nu] - sp.Rational(1, 2) * ETA[mu] * kron(mu, nu) * r1)
            V2[mu][nu] = sp.expand(
                R2[mu][nu]
                - sp.Rational(1, 2) * ETA[mu] * kron(mu, nu) * r2
                - sp.Rational(1, 2) * G[mu][nu] * r1
            )
    # Raise V indices: V^{mu nu} = ETA[mu]ETA[nu] V_{mu nu}
    V1u = raise_m(V1)
    V2u = raise_m(V2)
    # J3^{mu nu} = 2( V2u + b1 V1u - G^mu_a V1^{a nu} - G^nu_a V1^{a mu} )
    # G^mu_a = ETA[mu] G[mu][a]
    J3 = mz()
    for mu in range(4):
        for nu in range(4):
            acc = V2u[mu][nu] + b1 * V1u[mu][nu]
            for a in range(4):
                acc -= ETA[mu] * G[mu][a] * V1u[a][nu]
                acc -= ETA[nu] * G[nu][a] * V1u[a][mu]
            J3[mu][nu] = sp.expand(2 * acc)
    return {
        "ell3": ell,
        "r1": r1,
        "r2": r2,
        "r3": r3,
        "b1": b1,
        "b2": b2,
        "J3": J3,
        "R1": R1,
        "Gam": Gam,
    }


def G_lin_up(G, dG, ddG):
    """G_lin^{mu nu} from XI-A eq:Glin; A = 2 G_lin."""
    bg = P_of(G)
    bg_up = raise_m(bg)
    # D^nu = ∂_mu bg^{mu nu}
    # Need ∂_mu bg_up etc.
    # Compute derivatives of bar G
    dbg = [[P_of([[dG[a][mu][nu] for nu in range(4)] for mu in range(4)]) for a in range(4)]]
    # simpler: bar = P(G), ∂_a bar = P(∂_a G) since P linear
    d_bg = [P_of([[dG[a][mu][nu] for nu in range(4)] for mu in range(4)]) for a in range(4)]
    d_bg_up = [raise_m(d_bg[a]) for a in range(4)]
    bg_up = raise_m(bg)

    # D^nu = sum_mu ∂_mu bg^{mu nu}
    Dive = [sp.expand(sum(d_bg_up[mu][mu][nu] for mu in range(4))) for nu in range(4)]
    # ∂_alpha D^nu
    # D^nu = sum_mu ∂_mu bg^{mu nu}, ∂_alpha D^nu = sum_mu ∂_alpha ∂_mu bg^{mu nu}
    dd_bg_up = []
    for a in range(4):
        row = []
        for b in range(4):
            # ∂_a ∂_b G
            ddG_ab = [[ddG[a][b][mu][nu] for nu in range(4)] for mu in range(4)]
            row.append(raise_m(P_of(ddG_ab)))
        dd_bg_up.append(row)
    dDive = [[sp.expand(sum(dd_bg_up[a][mu][mu][nu] for mu in range(4))) for nu in range(4)] for a in range(4)]

    # Box bg^{mu nu} = ∂_a ∂^a bg = sum_a ETA[a] ∂_a ∂_a bg_up  (since ∂^a = ETA[a] ∂_a)
    Box_bg = mz()
    for mu in range(4):
        for nu in range(4):
            Box_bg[mu][nu] = sp.expand(sum(ETA[a] * dd_bg_up[a][a][mu][nu] for a in range(4)))

    Glin = mz()
    for mu in range(4):
        for nu in range(4):
            # -1/2 Box bar^{mu nu} + ∂^{(mu} D^{nu)} - 1/2 eta^{mu nu} ∂_rho D^rho
            # ∂^mu D^nu = ETA[mu] ∂_mu D^nu
            dmu_Dnu = ETA[mu] * dDive[mu][nu]
            dnu_Dmu = ETA[nu] * dDive[nu][mu]
            divD = sum(dDive[r][r] for r in range(4))  # ∂_rho D^rho — wait D^rho is upstairs
            # ∂_rho D^rho = sum_rho ∂_rho D^rho
            divD = sp.expand(sum(dDive[rho][rho] for rho in range(4)))
            Glin[mu][nu] = sp.expand(
                -sp.Rational(1, 2) * Box_bg[mu][nu]
                + sp.Rational(1, 2) * (dmu_Dnu + dnu_Dmu)
                - sp.Rational(1, 2) * ETA[mu] * kron(mu, nu) * divD
            )
    return Glin


def A_of(G, dG, ddG):
    Glin = G_lin_up(G, dG, ddG)
    return [[sp.expand(2 * Glin[mu][nu]) for nu in range(4)] for mu in range(4)]


def Q_nu_of(v_up, G, dG):
    """Q_nu(v) = 2 ∂_mu (v^{mu rho} G_{rho nu}) - v^{mu rho} ∂_nu G_{mu rho}."""
    out = [sp.Integer(0)] * 4
    for nu in range(4):
        acc = 0
        for mu in range(4):
            for rho in range(4):
                # ∂_mu (v^{mu rho} G_rho nu) = (∂_mu v) G + v ∂_mu G
                # For polynomial evaluation we need dv — pass dG only for G part;
                # v is typically A(h) which depends on x — caller should pass dv or we only
                # use product rule with precomputed ∂v.
                pass
        out[nu] = acc
    return out


def Q_nu_of_with_dv(v_up, dv_up, G, dG):
    """dv_up[a][mu][nu] = ∂_a v^{mu nu}."""
    out = [sp.Integer(0)] * 4
    for nu in range(4):
        acc = 0
        for mu in range(4):
            for rho in range(4):
                acc += 2 * (
                    dv_up[mu][mu][rho] * G[rho][nu] + v_up[mu][rho] * dG[mu][rho][nu]
                )
                acc -= v_up[mu][rho] * dG[nu][mu][rho]
        out[nu] = sp.expand(acc)
    return out


def N0_nu_of(v_up, dv_up):
    """N_{0,nu}(v) = 2 eta_{rho nu} ∂_mu v^{mu rho}."""
    out = [sp.Integer(0)] * 4
    for nu in range(4):
        acc = 0
        for rho in range(4):
            # ∂_mu v^{mu rho}
            div = sum(dv_up[mu][mu][rho] for mu in range(4))
            acc += 2 * ETA[rho] * kron(rho, nu) * div  # eta_{rho nu} = ETA[rho] if rho==nu else 0
            # eta_{rho nu} = ETA[nu]*kron(rho,nu) with both lowered: eta_{00}=1, eta_{ii}=-1
            # Actually eta_{rho nu} = ETA[rho]*kron(rho,nu)
        acc = 0
        for rho in range(4):
            div = sum(dv_up[mu][mu][rho] for mu in range(4))
            acc += 2 * (ETA[rho] * kron(rho, nu)) * div
        out[nu] = sp.expand(acc)
    return out


def C2_component(G, mu, nu, alpha, beta):
    u0, u1, u2, b1, b2, tau, GU = atoms(G)
    e = lambda a, b: ETA[a] * kron(a, b)
    term = b2 * (e(mu, nu) * e(alpha, beta) - sp.Rational(1, 2) * (e(mu, alpha) * e(beta, nu) + e(mu, beta) * e(alpha, nu)))
    C0 = e(mu, nu) * e(alpha, beta) - sp.Rational(1, 2) * (e(mu, alpha) * e(beta, nu) + e(mu, beta) * e(alpha, nu))
    term = b2 * C0
    sym_u1 = sp.Rational(1, 2) * (u1[mu][alpha] * e(beta, nu) + u1[mu][beta] * e(alpha, nu))
    sym_e = sp.Rational(1, 2) * (e(mu, alpha) * u1[beta][nu] + e(mu, beta) * u1[alpha][nu])
    term += b1 * (u1[mu][nu] * e(alpha, beta) + e(mu, nu) * u1[alpha][beta] - sym_u1 - sym_e)
    term += u2[mu][nu] * e(alpha, beta) + e(mu, nu) * u2[alpha][beta] + u1[mu][nu] * u1[alpha][beta]
    sym_u2 = sp.Rational(1, 2) * (u2[mu][alpha] * e(beta, nu) + u2[mu][beta] * e(alpha, nu))
    sym_e2 = sp.Rational(1, 2) * (e(mu, alpha) * u2[beta][nu] + e(mu, beta) * u2[alpha][nu])
    sym_uu = sp.Rational(1, 2) * (u1[mu][alpha] * u1[beta][nu] + u1[mu][beta] * u1[alpha][nu])
    term += -sym_u2 - sym_e2 - sym_uu
    return sp.expand(term)


def M2(G, dG, Gam1, Gam2):
    """M_2^{mu nu rho} = C0^{mu nu a b} Gamma_2^rho_{a b} + C1^{...} Gamma_1 — XII-C eq:M2.
    C0 from flat; C1 from XII-C. For time-only Dsource we need this.
    Simplified: use XII-C eq:actualsource Dsource = 2 C2 dd sigma - 2 M2 d sigma.
    """
    # C0 component
    def C0c(mu, nu, alpha, beta):
        e = lambda a, b: ETA[a] * kron(a, b)
        return e(mu, nu) * e(alpha, beta) - sp.Rational(1, 2) * (
            e(mu, alpha) * e(beta, nu) + e(mu, beta) * e(alpha, nu)
        )

    # C1 from XII-C eq:Ccoefficients — use atoms
    u0, u1, u2, b1, b2, tau, GU = atoms(G)

    def C1c(mu, nu, alpha, beta):
        e = lambda a, b: ETA[a] * kron(a, b)
        sym_u1 = sp.Rational(1, 2) * (u1[mu][alpha] * e(beta, nu) + u1[mu][beta] * e(alpha, nu))
        sym_e = sp.Rational(1, 2) * (e(mu, alpha) * u1[beta][nu] + e(mu, beta) * u1[alpha][nu])
        return sp.expand(
            b1 * C0c(mu, nu, alpha, beta)
            + u1[mu][nu] * e(alpha, beta)
            + e(mu, nu) * u1[alpha][beta]
            - sym_u1
            - sym_e
        )

    M = [[[sp.Integer(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for mu, nu, rho in itertools.product(range(4), repeat=3):
        acc = 0
        for a, b in itertools.product(range(4), repeat=2):
            acc += C0c(mu, nu, a, b) * Gam2[(2, rho, a, b)]
            acc += C1c(mu, nu, a, b) * Gam1[(1, rho, a, b)]
        M[mu][nu][rho] = sp.expand(acc)
    return M


def Dsource_time(G, dG, ddG, sig_p, sig_pp, curv):
    """Dsource^{mu nu} = 2 C2^{mu nu 00} sig'' - 2 M2^{mu nu 0} sig'  (time-only)."""
    Gam = curv["Gam"]
    M = M2(G, dG, Gam, Gam)
    Ds = mz()
    for mu in range(4):
        for nu in range(mu, 4):
            C200 = C2_component(G, mu, nu, 0, 0)
            acc = 2 * C200 * sig_pp - 2 * M[mu][nu][0] * sig_p
            Ds[mu][nu] = Ds[nu][mu] = sp.expand(acc)
    return Ds


def FP_density(G, dG):
    """Fierz-Pauli Lagrangian density (XI-A eq:FP)."""
    GU = raise_m(G)
    tau = tr_eta(G)
    # ∂_lam G_mu nu ∂^lam G^{mu nu}
    term1 = 0
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                term1 += dG[lam][mu][nu] * (ETA[lam] * ETA[mu] * ETA[nu] * dG[lam][mu][nu])
    # Actually ∂^lam = ETA[lam] ∂_lam, G^{mu nu}=ETA[mu]ETA[nu]G[mu][nu]
    term1 = 0
    for lam, mu, nu in itertools.product(range(4), repeat=3):
        dG_up = ETA[mu] * ETA[nu] * dG[lam][mu][nu]
        term1 += (ETA[lam] * dG[lam][mu][nu]) * dG_up  # ∂_lam G * ∂^lam G^{mu nu} — index mess
    # Cleaner: ∂^λ G_{μν} = ETA[λ] ∂_λ G_{μν}, and G^{μν} derivatives similarly
    term1 = 0
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                term1 += ETA[lam] * dG[lam][mu][nu] * ETA[mu] * ETA[nu] * dG[lam][mu][nu]
    # -2 (∂_mu G^{mu nu}) (∂^rho G_{rho nu})
    # G^{mu nu} = ETA[mu]ETA[nu] G[mu][nu]; ∂_alpha G^{mu nu} = ETA[mu]ETA[nu] ∂_alpha G[mu][nu]
    divG = [sp.expand(sum(ETA[mu] * ETA[nu] * dG[mu][mu][nu] for mu in range(4))) for nu in range(4)]
    # ∂_mu G^{mu nu} = sum_mu ETA[mu]ETA[nu] ∂_mu G[mu][nu]
    dmu_Gmunu = [0]*4
    for nu in range(4):
        dmu_Gmunu[nu] = sp.expand(sum(ETA[mu]*ETA[nu]*dG[mu][mu][nu] for mu in range(4)))
    term2 = 0
    for nu in range(4):
        # ∂^rho G_{rho nu} = ETA[rho] ∂_rho G[rho][nu]
        drG = sp.expand(sum(ETA[rho]*dG[rho][rho][nu] for rho in range(4)))
        term2 += dmu_Gmunu[nu] * drG
    term2 = -2 * term2
    # +2 (∂_mu G^{mu nu}) ∂_nu tau
    dtau = [sp.expand(sum(ETA[a]*dG[lam][a][a] for a in range(4))) for lam in range(4)]
    term3 = 0
    for nu in range(4):
        term3 += dmu_Gmunu[nu] * dtau[nu]
    term3 = 2 * term3
    # - ∂_lam tau ∂^lam tau
    term4 = -sp.expand(sum(ETA[lam]*dtau[lam]*dtau[lam] for lam in range(4)))
    return sp.expand(sp.Rational(1, 2) * (term1 + term2 + term3 + term4))


print("grav_density module OK")
