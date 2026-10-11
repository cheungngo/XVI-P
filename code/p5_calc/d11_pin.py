"""XVI-P p20 -- D11 normalisation pin (p19 independent-rebuild blind spot: 'drop D11' is invisible to the projected
identity and to full sigma_0 closure, because the D11 pole is transverse, hence sigma_0-closed by itself).

DERIVED here from package data (certificates/P18_D11.json, the released 4D UV pole of the D11 scalar loop):
  * the spin-2 / spin-0 decomposition of the 4D (non-evanescent) D11 pole with the Barnes-Rivers projectors, using
    the package's own structure convention (covariant.orbit over the symmetric pairs (m,n), (r,s));
  * transversality p^m T_mnrs = 0 (convention guard) and absence of spin-1 / spin-0w parts;
  * the quadratic forms of the curvature invariants on g = eta + h (linearised Riemann, built here):
    C^2 -> (1/2) p^4 h P2 h, R^2 -> 3 p^4 h P0s h, Gauss-Bonnet E -> 0.
COMPARED with an EXTERNAL literature value (not package-derived): the a_2 (Seeley-DeWitt) coefficient of a minimally
coupled real scalar, (1/120) C^2 + (1/2)(xi - 1/6)^2 R^2 (+ E, box R), xi = 0  =>  (1/120) C^2 + (1/72) R^2
[Birrell & Davies, Quantum Fields in Curved Space (1982), sec. 6.2; 't Hooft & Veltman, Ann. Inst. H. Poincare A20
(1974) 69].  Prediction: spin-2 : spin-0 = (1/120)(1/2) : (1/72)(3) = 1/240 : 1/24 = 1 : 10.

PIN (ratio, derived + compared): c0 / c2 = 10 from the certificate.
ABSOLUTE PIN (p21, disclosed revision; p20 had it OPEN): absolute_pin() derives the sign and magnitude of the D11
pole from 1/2 Tr ln under the package's declared conventions (G = Gamma^(2) from amplitude_rules Gate 0 + G6; Wick
direction from N_eps = i/(16 pi^2) and the +1/eps bubble pole; g = eta + kappa h; eta = (+,-,-,-)) and compares with
the heat-kernel a_2: exact equality (ratio 1) for both spins.  External inputs: mathematics only (a_2 values, the
heat-kernel pole formula); no external convention choice.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "code" / "p5_entry"))
sys.path.insert(0, str(ROOT / "code" / "classical"))
import covariant as C  # noqa: E402
import dred  # noqa: E402   (guarded loader parse_d)
import p20_conventions as QC  # noqa: E402

CERT = ROOT / "certificates"
IDX = ("m", "n", "r", "s")
PAIRS = [("m", "n"), ("r", "s")]
LIT = {"C2": sp.Rational(1, 120), "R2_xi0": sp.Rational(1, 72),
       "source": ("Birrell & Davies, Quantum Fields in Curved Space (CUP 1982), sec. 6.2 (a_2 of a scalar field); "
                  "'t Hooft & Veltman, Ann. Inst. H. Poincare A20 (1974) 69 -- EXTERNAL, not package-derived")}


def parse_key(key):
    """'g4_mr p_n p_s (p.p)^1' -> (factors, power of p.p); only 4D (g4, p) structures."""
    facs, e = [], 0
    for tok in key.split():
        if tok.startswith("(p.p)^"):
            e = int(tok[len("(p.p)^"):])
        elif tok.startswith("g4_"):
            facs.append(("g4", tok[3], tok[4]))
        elif tok.startswith("p_"):
            facs.append(("p", tok[2]))
        else:
            raise ValueError(f"not a 4D structure: {key}")
    return C.canon(facs), e


def tensor(coeffs, eta, p, scale=None):
    """T[m][n][r][s] from {key: coefficient} with the package orbit convention."""
    group = C.sym_group(PAIRS)
    pp = sum(eta[a] * p[a] ** 2 for a in range(4))
    T = {}
    for m in range(4):
        for n in range(4):
            for r in range(4):
                for s_ in range(4):
                    asg = dict(zip(IDX, (m, n, r, s_)))
                    v = 0
                    for key, c in coeffs.items():
                        facs, e = parse_key(key)
                        val = 0
                        for f in C.orbit(facs, group):
                            t = sp.Integer(1)
                            for x in f:
                                if x[0] == "g4":
                                    t *= eta[asg[x[1]]] if asg[x[1]] == asg[x[2]] else 0
                                else:
                                    t *= p[asg[x[1]]]
                            val += t
                        v += c * val * pp ** e
                    T[m, n, r, s_] = sp.expand(v)
    return T, pp


def projectors(eta, p, pp):
    def th(a, b):     # theta with both indices DOWN
        return (eta[a] if a == b else 0) - p[a] * p[b] / pp
    P2, P0, P1 = {}, {}, {}
    for m in range(4):
        for n in range(4):
            for r in range(4):
                for s_ in range(4):
                    S = (th(m, r) * th(n, s_) + th(m, s_) * th(n, r)) / 2
                    P0[m, n, r, s_] = th(m, n) * th(r, s_) / 3
                    P2[m, n, r, s_] = S - P0[m, n, r, s_]
    return P2, P0


def contract(A, B, eta):
    """A_mnrs B^mnrs (indices raised with eta, eta diagonal +-1)."""
    return sp.nsimplify(sp.expand(sum(A[k] * B[k] * eta[k[0]] * eta[k[1]] * eta[k[2]] * eta[k[3]] for k in A)))


def spin_parts(T, eta, p, pp):
    P2, P0 = projectors(eta, p, pp)
    n2, n0 = contract(P2, P2, eta), contract(P0, P0, eta)       # 5, 1
    c2 = sp.simplify(contract(T, P2, eta) / n2 / pp ** 2)
    c0 = sp.simplify(contract(T, P0, eta) / n0 / pp ** 2)
    resid = {k: sp.simplify(T[k] - pp ** 2 * (c2 * P2[k] + c0 * P0[k])) for k in T}
    trans = all(sp.simplify(sum(eta[m] * p[m] * T[m, n, r, s_] for m in range(4))) == 0
                for n in range(4) for r in range(4) for s_ in range(4))
    return {"c2": c2, "c0": c0, "n2": n2, "n0": n0, "transverse": trans,
            "only_spin2_spin0s": all(v == 0 for v in resid.values())}


def curvature_forms(p):
    """Euclidean quadratic forms (h_{-p} M h_p) of Riem^2, Ric^2, R^2 for g = delta + h, d -> i p; returned as
    coefficients on p^4 P2 and p^4 P0s (and the residual check)."""
    eta = (1, 1, 1, 1)
    pp = sum(x ** 2 for x in p)
    H = {}
    hs = {}
    for a in range(4):
        for b in range(a, 4):
            hs[a, b] = hs[b, a] = sp.Symbol(f"h{a}{b}")

    def riem(a, b, c, d_):    # linearised R_abcd = 1/2 (d_b d_c h_ad + d_a d_d h_bc - d_a d_c h_bd - d_b d_d h_ac); d -> i p
        return -sp.Rational(1, 2) * (p[b] * p[c] * hs[a, d_] + p[a] * p[d_] * hs[b, c] - p[a] * p[c] * hs[b, d_]
                                     - p[b] * p[d_] * hs[a, c])
    Rm = {(a, b, c, d_): riem(a, b, c, d_) for a in range(4) for b in range(4) for c in range(4) for d_ in range(4)}
    Ric = {(b, d_): sum(Rm[a, b, a, d_] for a in range(4)) for b in range(4) for d_ in range(4)}
    R = sum(Ric[a, a] for a in range(4))
    # h_{-p} = h_p for real h and a quadratic form in p (even): the bilinear is the square
    forms = {"Riem2": sp.expand(sum(v ** 2 for v in Rm.values())), "Ric2": sp.expand(sum(v ** 2 for v in Ric.values())),
             "R2": sp.expand(R ** 2)}
    forms["C2"] = sp.expand(forms["Riem2"] - 2 * forms["Ric2"] + forms["R2"] / 3)
    forms["E_GaussBonnet"] = sp.expand(forms["Riem2"] - 4 * forms["Ric2"] + forms["R2"])
    P2, P0 = projectors(eta, p, pp)

    def hPh(P):
        return sp.expand(sum(hs[m, n] * P[m, n, r, s_] * hs[r, s_] for (m, n, r, s_) in P) * pp ** 2)
    q2, q0 = hPh(P2), hPh(P0)
    a, b = sp.symbols("a b")
    out = {}
    gens = sorted(set(hs.values()), key=str)
    for k, f in forms.items():
        sol = sp.solve(sp.Poly(sp.expand(f - a * q2 - b * q0), *gens).coeffs(), [a, b], dict=True)
        out[k] = {"P2": sp.nsimplify(sol[0][a]), "P0s": sp.nsimplify(sol[0][b])} if sol else None
    return out



# ------------------------------------------------------------------------------------------------ p21: ABSOLUTE pin
def curvature_forms_eta(p, eta):
    """quadratic forms (coefficients on (p.p)^2 h P2 h and (p.p)^2 h P0s h, all indices contracted with eta) of
    Riem^2, Ric^2, R^2, C^2, E for g = eta + h at second order; d -> -i p (plane wave e^{-ip.x}); exact."""
    pp = sum(eta[a] * p[a] ** 2 for a in range(4))
    hs = {}
    for a in range(4):
        for b in range(a, 4):
            hs[a, b] = hs[b, a] = sp.Symbol(f"h{a}{b}")
    up = [sp.Integer(eta[a]) for a in range(4)]          # diagonal eta, eta^{-1} = eta

    def riem(a, b, c, d_):      # all lower; linearised; d_a d_b -> -p_a p_b
        return -sp.Rational(1, 2) * (p[b] * p[c] * hs[a, d_] + p[a] * p[d_] * hs[b, c] - p[a] * p[c] * hs[b, d_]
                                     - p[b] * p[d_] * hs[a, c])
    rng = range(4)
    Rm = {(a, b, c, d_): riem(a, b, c, d_) for a in rng for b in rng for c in rng for d_ in rng}
    Ric = {(b, d_): sum(up[a] * Rm[a, b, a, d_] for a in rng) for b in rng for d_ in rng}
    R = sum(up[a] * Ric[a, a] for a in rng)
    forms = {"Riem2": sp.expand(sum(v ** 2 * up[k[0]] * up[k[1]] * up[k[2]] * up[k[3]] for k, v in Rm.items())),
             "Ric2": sp.expand(sum(v ** 2 * up[k[0]] * up[k[1]] for k, v in Ric.items())), "R2": sp.expand(R ** 2)}
    forms["C2"] = sp.expand(forms["Riem2"] - 2 * forms["Ric2"] + forms["R2"] / 3)
    forms["E_GaussBonnet"] = sp.expand(forms["Riem2"] - 4 * forms["Ric2"] + forms["R2"])
    P2, P0 = projectors(eta, p, pp)

    def hPh(P):                 # h_mn P^{mnrs} h_rs
        return sp.expand(sum(hs[m, n] * P[m, n, r, s_] * hs[r, s_] * up[m] * up[n] * up[r] * up[s_]
                             for (m, n, r, s_) in P) * pp ** 2)
    q2, q0 = hPh(P2), hPh(P0)
    a, b = sp.symbols("a b")
    gens = sorted(set(hs.values()), key=str)
    out = {}
    for k, f in forms.items():
        sol = sp.solve(sp.Poly(sp.expand(f - a * q2 - b * q0), *gens).coeffs(), [a, b], dict=True)
        out[k] = {"P2": sp.nsimplify(sol[0][a]), "P0s": sp.nsimplify(sol[0][b])} if sol else None
    return out


def absolute_pin(c2, c0, eta, p):
    """Exact derivation of the SIGN and MAGNITUDE of the D11 pole from 1/2 Tr ln (minimal scalar loop) under the
    package's declared conventions, compared with the heat-kernel a_2.  Returns (record, pass)."""
    import integrals as IL
    import amplitude_rules as AR
    import p18_conventions as Q18
    import conventions as CC
    pi = sp.pi
    decl = {   # package declarations (checked verbatim; a change of any convention breaks the pin)
        "N_eps = i S_eps/(16 pi^2)": "N_eps = i S_eps/(16 pi^2)" in (IL.__doc__ or ""),
        "Gamma_1 = -i * graph sum": "Gamma_1 = -i * graph sum" in (AR.__doc__ or ""),
        "i Gamma_1 = int prefactor N/prod(q^2+i0)": "i Gamma_1^{(ext)} = int d^d l/(2pi)^d  prefactor * N(l,p)" in (AR.__doc__ or ""),
        "G6: G = kappa^2 N_eps Ghat, Ghat = -i prefactor/kappa^2 int N/(D1D2)": (
            "G = kappa^2 N_eps Ghat" in Q18.PHASE_CONVENTION_G6 and "Ghat = -i * prefactor/kappa^2" in Q18.PHASE_CONVENTION_G6),
        "g = eta + kappa h": CC.METRIC_PARAMETRISATION.startswith("g_{mu nu} = eta_{mu nu} + kappa h_{mu nu}"),
        "S_phi = (1/2) int sqrt(-g) g^{mu nu} d phi d phi (minimal, xi = 0)": CC.S_SCALAR.startswith(
            "S_phi = (1/2) int sqrt(-g) g^{mu nu} d_mu phi d_nu phi"),
        "eta = (+,-,-,-)": tuple(int(x) for x in eta) == (1, -1, -1, -1),
        "d = 4 - 2 eps; Ihat(1,1) pole = +1/eps": IL.master_series()[-1] == 1,
    }
    N = sp.I / (16 * pi ** 2)                          # N_eps at the pole (S_eps -> 1)
    # (1) G = Gamma_1^(2):  G = kappa^2 N_eps Ghat = -i pref int N/(D1D2) and i Gamma = pref int N/prod  =>  G = Gamma
    G_over_Gamma = sp.simplify((-sp.I) * sp.I)        # = 1
    # (2) Wick direction from the package: int d^dl_M/(2pi)^d 1/((l^2+i0)((l+p)^2+i0)) = N_eps * (1/eps + ...)
    #     = +i x (positive Euclidean bubble 1/(16 pi^2 eps))  =>  d^dl_M = s_W i d^dl_E with s_W = +1 (l0 = i l4)
    s_W = sp.sign(sp.im(N)) * sp.sign(IL.master_series()[-1])
    # (3) dual rotation x0 = -i s_W x4: L_M = 1/2(phi_0^2 - grad^2) -> -L_E, d^4x_M = -i s_W d^4x_E  => i S_M = -s_W S_E
    f0, f4, fg = sp.symbols("phi_0 phi_4 phi_grad")
    LM = sp.Rational(1, 2) * (f0 ** 2 - fg ** 2)
    LM_rot = LM.subs(f0, sp.I * s_W * f4)                # d/dx0 = i s_W d/dx4
    LE = sp.Rational(1, 2) * (f4 ** 2 + fg ** 2)
    iSM_over_SE = sp.simplify(sp.I * (-sp.I * s_W) * LM_rot / LE)       # must be -1 (convergent e^{-S_E})
    # (4) e^{i Gamma_M} = e^{-Gamma_E}, Gamma_M = int d^4x_M L_M = -i s_W int d^4x_E L_M  =>  L_M^eff = -s_W L_E^eff
    LM_over_LE = -s_W
    # (5) heat kernel (EXTERNAL mathematics, Euclidean, positive operator): Tr ln Delta |_div = -(1/(16 pi^2 eps)) int a_2,
    #     W_E = (1/2) Tr ln  =>  L_E,div = -a_2/(32 pi^2 eps); a_2 = C^2/120 + (1/2)(xi-1/6)^2 R^2 (+E, box R), xi = 0
    LE_div_per_a2 = -1 / (32 * pi ** 2)
    LM_div_per_a2 = LM_over_LE * LE_div_per_a2         # coefficient of a_2/eps in L_M
    # (6) quadratic forms in Minkowski (eta of the package), g = eta + kappa h  -> kappa^2 h ... h
    cf = curvature_forms_eta(p, eta)
    # Gamma^(2) = 2 x (coefficient of the quadratic form)  (Gamma >= (1/2) h T h with T = Gamma^(2); W2 16-component)
    pred2 = 2 * LM_div_per_a2 * (LIT["C2"] * cf["C2"]["P2"] + LIT["R2_xi0"] * cf["R2"]["P2"])
    pred0 = 2 * LM_div_per_a2 * (LIT["C2"] * cf["C2"]["P0s"] + LIT["R2_xi0"] * cf["R2"]["P0s"])
    # package: Gamma^(2)|_pole = G|_pole = kappa^2 N_eps Ghat_UV_pole / eps  (per kappa^2/eps)
    pkg2, pkg0 = sp.simplify(G_over_Gamma * N * c2), sp.simplify(G_over_Gamma * N * c0)
    r2 = sp.simplify(pkg2 / pred2) if pred2 != 0 else None
    r0 = sp.simplify(pkg0 / pred0) if pred0 != 0 else None
    ok = bool(all(decl.values()) and G_over_Gamma == 1 and s_W == 1 and iSM_over_SE == -1
              and cf["E_GaussBonnet"] == {"P2": 0, "P0s": 0} and r2 == 1 and r0 == 1)
    rec = {"package_declarations_checked": decl,
           "steps": {"1_G_equals_Gamma2": str(G_over_Gamma),
                     "2_wick_sign_s_W_from_N_eps_and_Ihat_pole": str(s_W),
                     "3_i_S_M_over_S_E (must be -1)": str(iSM_over_SE),
                     "4_L_M_eff_over_L_E_eff": str(LM_over_LE),
                     "5_L_M_div_per_a2_over_eps": str(LM_div_per_a2),
                     "6_minkowski_quadratic_forms": {k: ({kk: str(vv) for kk, vv in v.items()} if v else None)
                                                     for k, v in cf.items()}},
           "package_Gamma2_pole_per_kappa2_over_eps": {"spin2": str(pkg2), "spin0s": str(pkg0)},
           "heat_kernel_prediction_per_kappa2_over_eps": {"spin2": str(pred2), "spin0s": str(pred0)},
           "ratio_package_over_prediction": {"spin2": str(r2), "spin0s": str(r0)},
           "external_inputs": ["a_2 coefficients of a minimally coupled real scalar: C^2/120, (1/2)(xi-1/6)^2 R^2 "
                               "(Birrell-Davies sec. 6.2; 't Hooft-Veltman 1974)",
                               "heat-kernel pole Tr ln Delta|_div = -(1/(16 pi^2 eps)) int a_2 (Euclidean, d = 4-2eps)"],
           "convention_choices_external": "none: every convention (G vs Gamma^(2), Minkowski i, Wick direction, "
                                          "sign of W_div, N_eps, kappa normalisation, signature) is fixed by the "
                                          "package declarations checked above",
           "status": "PASS" if ok else "FAIL"}
    return rec, ok

def main(argv=None):
    t0 = time.time()
    cert = json.loads((CERT / "P18_D11.json").read_text())
    res = cert["result"]
    four = {k: dred.parse_d(str(v["UV_pole"]), {"I": sp.I}) for k, v in res.items() if not v["evanescent"]}
    eta = tuple(int(x) for x in C.ETA)
    p = (sp.Rational(3), sp.Rational(1), sp.Rational(2), sp.Rational(-5, 7))        # generic, p.p != 0
    T, pp = tensor(four, eta, p)
    sp_ = spin_parts(T, eta, p, pp)
    ratio = sp.simplify(sp_["c0"] / sp_["c2"]) if sp_["c2"] != 0 else None
    p_e = (sp.Rational(2), sp.Rational(-1), sp.Rational(3), sp.Rational(5, 3))
    cf = curvature_forms(p_e)
    lit2, lit0 = LIT["C2"] * cf["C2"]["P2"], LIT["R2_xi0"] * cf["R2"]["P0s"]
    lit_ratio = sp.simplify(lit0 / lit2)
    common = sp.simplify(sp_["c2"] / lit2) if lit2 else None
    common0 = sp.simplify(sp_["c0"] / lit0) if lit0 else None
    ratio_pin = bool(sp_["transverse"] and sp_["only_spin2_spin0s"] and ratio is not None and ratio == lit_ratio
                     and cf["C2"]["P0s"] == 0 and cf["E_GaussBonnet"] == {"P2": 0, "P0s": 0})

    absrec, abs_ok = absolute_pin(sp_["c2"], sp_["c0"], eta, p)

    def mutated(scale_all=None, drop=False, swap=False):
        co = {} if drop else {k: (scale_all or 1) * v for k, v in four.items()}
        if swap:     # exchange the two g4 g4 structures (a convention error)
            a_, b_ = "g4_mn g4_rs (p.p)^2", "g4_mr g4_ns (p.p)^2"
            co[a_], co[b_] = co[b_], co[a_]
        Tm, _ = tensor(co, eta, p)
        r = spin_parts(Tm, eta, p, pp)
        rr = sp.simplify(r["c0"] / r["c2"]) if r["c2"] != 0 else None
        ok = bool(r["transverse"] and r["only_spin2_spin0s"] and rr == lit_ratio)
        _, abs_m = absolute_pin(r["c2"], r["c0"], eta, p) if (r["c2"] != 0 and r["c0"] != 0) else (None, False)
        return {"c2": str(r["c2"]), "c0": str(r["c0"]), "ratio": str(rr), "ratio_pin_passes": ok,
                "detected_by_ratio_pin": not ok, "absolute_pin_passes": bool(abs_m),
                "detected_by_absolute_pin": not abs_m}
    muts = {"drop_graph_D11": mutated(drop=True), "D11_normalisation_x2": mutated(scale_all=2),
            "D11_sign_flip": mutated(scale_all=-1), "swap_g4g4_structures": mutated(swap=True)}
    rec = {"landmark": "XVI-P", "revision": QC.REVISION,
           "deliverable": "D11 normalisation pin via the trace-anomaly / C^2 coefficient (p19 reviewer blind spot)",
           "source_certificate": "certificates/P18_D11.json", "graph": "D11 (hh scalar loop, minimal coupling h.phi^2)",
           "input_4D_UV_pole": {k: str(v) for k, v in four.items()},
           "orbit_convention": "covariant.orbit over the symmetric pairs (m,n), (r,s) (as in the D11 fit)",
           "spin_decomposition": {"c2_spin2": str(sp_["c2"]), "c0_spin0s": str(sp_["c0"]),
                                  "projector_norms": [str(sp_["n2"]), str(sp_["n0"])],
                                  "transverse": sp_["transverse"], "only_spin2_and_spin0s": sp_["only_spin2_spin0s"],
                                  "ratio_c0_over_c2": str(ratio)},
           "curvature_quadratic_forms_derived": {k: ({kk: str(vv) for kk, vv in v.items()} if v else None)
                                                 for k, v in cf.items()},
           "literature_a2_minimal_scalar": {"C2": str(LIT["C2"]), "R2_xi0": str(LIT["R2_xi0"]), "source": LIT["source"],
                                            "predicted_spin2": str(lit2), "predicted_spin0s": str(lit0),
                                            "predicted_ratio": str(lit_ratio)},
           "ratio_pin": {"status": "PASS" if ratio_pin else "FAIL",
                         "statement": ("spin-0 : spin-2 of the D11 4D UV pole = 10 : 1, derived from the certificate; "
                                       "equals the minimal-scalar a_2 prediction (1/72)(3) : (1/120)(1/2)")},
           "absolute_pin": {"status": "PASS" if abs_ok else "FAIL",
                            "observed_common_factor_c2_vs_bare_a2": str(common),
                            "observed_common_factor_c0_vs_bare_a2": str(common0),
                            "derivation_p21": absrec,
                            "statement": ("p21: SIGN and MAGNITUDE derived exactly from 1/2 Tr ln of the minimal scalar "
                                          "loop under the package's declared conventions (G = Gamma^(2); N_eps = i/(16 "
                                          "pi^2) and the +1/eps bubble pole fix the Wick direction, i S_M = -S_E, L_M = "
                                          "-L_E; g = eta + kappa h; eta = (+,-,-,-)): Gamma^(2)|_pole = kappa^2/(16 pi^2 "
                                          "eps) [p^4 P2/240 + p^4 P0s/24], equal to the package pole kappa^2 N_eps "
                                          "Ghat/eps exactly (ratio 1, both spins).  External inputs are mathematics "
                                          "only (a_2 coefficients; heat-kernel pole formula); no external convention "
                                          "choice.  p20 had left this OPEN.")},
           "mutations": muts,
           "reading": ("drop D11 and a structure swap are detected by the ratio pin; an overall x2 or a sign flip keeps "
                       "the ratio and is detected by the absolute pin (p21) and, for x2, by M2 (P18)"),
           "corrected_in_revision": "p21 (absolute pin derived; p20 had it OPEN)",
           "D11_absolute_pin_verified": abs_ok,
           "D11_ratio_pin_verified": ratio_pin,
           "c2_spin2": str(sp_["c2"]), "c0_spin0s": str(sp_["c0"]), "ratio_c0_over_c2": str(ratio),
           "ratio_pin_status": "PASS" if ratio_pin else "FAIL", "absolute_pin_status": "PASS" if abs_ok else "FAIL",
           "seconds": round(time.time() - t0, 1)}
    import certio
    certio.write(CERT / f"{QC.CERT_PREFIX}_D11_pin.json", rec)
    print(json.dumps({k: rec[k] for k in ("spin_decomposition", "ratio_pin", "absolute_pin", "mutations",
                                          "curvature_quadratic_forms_derived")}, indent=1, default=str))
    return 0 if (ratio_pin and abs_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
