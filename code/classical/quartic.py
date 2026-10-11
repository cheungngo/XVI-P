#!/usr/bin/env python3
"""p11 quartic stage: build + export ell_2, ell_3, ell_4 (Gamma-Gamma density) and verify DETERMINISTICALLY.

Exports: exports/ell{2,3,4}_generating_polynomial.srepr, exports/V4_grav.json, exports/ell4_conventions.json
Certificates: certificates/P13_quartic_verified.json (+ P13_boundary_identity.json via boundary_identity.run)

ACCEPTANCE (all exact symbolic, no sampling):
  C1 q q^{-1} = 1 + O(eps^5), all 10 components symbolic
  C2 log(-det q) = tr log(eta^{-1} q) through eps^4 and [sqrt-series]^2 = -det q through eps^4, all 10 components
  C3 boundary identity sqrt(-g)R - L_GG = - d_mu B^mu (boundary_identity.py: generic jets + conformal control)
  C4 exported ell_k == independent series evaluator run over the polynomial ring of the 50 jet symbols (identity)
  C5 ell_3 - XII-C ell_3 (XVI-N grav_density.ell3_and_curvature, symbolic jets) has identically vanishing Euler
     derivatives (=> equal modulo a total divergence; same sign and normalisation)
  C6 ell_2 - XI-A Fierz-Pauli (XVI-N grav_density.FP_density): same Euler test
  C7 Noether s0 ell_{n+2} + s1 ell_{n+1} ~ 0, n = 0,1,2, on the EXPORTED polynomials (grav_noether.py, Euler test)
REGRESSION CONTROLS (sampled, NOT acceptance): numeric evaluator vs export at random jets; plane-wave polarised
  cubic/quadratic regression; plane-wave Noether.
MUTATIONS (each must fail a deterministic acceptance test):
  M1 one ell_4 coefficient x 7/5 -> C7 kappa^2; M2 ell_4 sign -> C7 kappa^2; M3 swapped contraction -> C4, C5, C6, C7;
  M4 missing sqrt eps^2 coefficient -> C4, C7 kappa^2; M5 wrong inverse sign -> C1; M6 stale ell_4 hash -> sha check;
  M7 wrong boundary orientation (+d B) -> C3 (generic and conformal).
"""
from __future__ import annotations
import contextlib, hashlib, io, itertools, json, random, sys, time
from fractions import Fraction as Fr
from pathlib import Path
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import conventions as C  # noqa: E402
import certio  # noqa: E402
import planewave_exact as PW  # noqa: E402
import series_eval as SE  # noqa: E402
import grav_noether as GN  # noqa: E402
import jetpoly as J  # noqa: E402
import boundary_identity as BI  # noqa: E402
from inverse_metric_series import product_qid_minus_one, eta_matrix  # noqa: E402

import inherited  # noqa: E402  (p13: pinned inherited inputs; workspace or vendored copy, sha256-verified)
GRAV_DENSITY = "XVI-N-r10/code/prep/grav_density.py"
EXPORTS = ROOT / "exports"
CERT = ROOT / "certificates"
eps = sp.symbols("eps")

CONVENTIONS = {
    "revision": C.REVISION, "eta": "diag(+,-,-,-)",
    "q": "eta + eps H, eps = kappa, H = h (lowered, symmetric); affine parametrisation",
    "S_EH": "-(2/kappa^2) int sqrt(-q) R",
    "density": C.L_GG, "boundary_identity": C.BOUNDARY_IDENTITY,
    "ell_k": "-2 [eps^k] L_GG ; S_EH = sum_k kappa^{k-2} int ell_k (integrated, compact support)",
    "IBP": "total derivatives dropped only inside the integrated action (orientation of the dropped divergence irrelevant)",
    "truncation": "O(eps^4) inclusive", "jets": "H{m}{n} = h_mn (m<=n), dH{m}{n}_{r} = d_r h_mn", "a_ghost": "1/2",
    "polarization": C.POLARIZATION,
}


def build_and_export(from_cache=None):
    t0 = time.time()
    if from_cache is not None and Path(from_cache).exists():
        import pickle
        ell = {k: sp.sympify(v) for k, v in pickle.load(open(from_cache, "rb"))["ell"].items()}
        how = f"cache {Path(from_cache).name} (written by the same builder)"
    else:
        from ell4_full_polynomial import expand_L_gamma_jet
        with contextlib.redirect_stdout(io.StringIO()):
            coeffs, _, _ = expand_L_gamma_jet(order=4)
        ell = {k: sp.expand(-2 * coeffs[k]) for k in range(5)}
        how = "fresh build ell4_full_polynomial.expand_L_gamma_jet(order=4)"
    out = {}
    for k in (2, 3, 4):
        (EXPORTS / f"ell{k}_generating_polynomial.srepr").write_text(sp.srepr(ell[k]) + "\n")
        e, h = PW.load_ell(k)
        out[k] = {"sha256": h, "terms_reproducibility": len(sp.Add.make_args(e))}
    out["ell0_zero"] = ell[0] == 0
    out["ell1_zero"] = ell[1] == 0
    out["build"] = how
    out["seconds"] = round(time.time() - t0, 1)
    (EXPORTS / "ell4_conventions.json").write_text(certio.dumps(CONVENTIONS))
    return out


# ---------------- C1 / M5 ----------------
def inverse_control(order=4):
    Hs = sp.Matrix(4, 4, lambda m, n: sp.Symbol(f"Hc{min(m, n)}{max(m, n)}"))
    rem = product_qid_minus_one(Hs, eps, order=order)
    fails = [(i, j) for i in range(4) for j in range(4) if sp.expand(rem[i, j]) != 0]
    return {"test": "q q^{-1} = 1 + O(eps^5), 10 symbolic components", "pass": not fails, "failures": fails}


def wrong_inverse_rejected():
    Hs = sp.Matrix(4, 4, lambda m, n: sp.Symbol(f"Hc{min(m, n)}{max(m, n)}"))
    eta = eta_matrix()
    bad = eta + eps * (eta * Hs * eta)
    prod = sp.expand((eta + eps * Hs) * bad) - sp.eye(4)
    return any(sp.expand(prod[i, j]) != 0 for i in range(4) for j in range(4))


# ---------------- C2 ----------------
def det_tracelog_generic():
    from sympy.polys.rings import ring
    from sympy import QQ
    IDX = [(m, n) for m in range(4) for n in range(m, 4)]
    R, e, *hs = ring("e," + ",".join(f"H{m}{n}" for m, n in IDX), QQ)
    Hm = {(m, n): hs[IDX.index((min(m, n), max(m, n)))] for m in range(4) for n in range(4)}
    Mm = [[C.ETA[i] * Hm[(i, j)] for j in range(4)] for i in range(4)]       # eta^{-1} H

    def trunc(p, n=4):
        return R({mon: c for mon, c in p.terms() if mon[0] <= n})
    # -det(eta + e H) = det(1 + e M)
    one_eM = [[(R(1) if i == j else R(0)) + e * Mm[i][j] for j in range(4)] for i in range(4)]
    det = R(0)
    for perm in itertools.permutations(range(4)):
        sgn = 1
        for i in range(4):
            for j in range(i + 1, 4):
                if perm[i] > perm[j]:
                    sgn = -sgn
        t = R(sgn)
        for i in range(4):
            t = t * one_eM[i][perm[i]]
        det += t
    x = det - 1
    logdet, xp = R(0), R(1)
    for j in range(1, 5):
        xp = trunc(xp * x)
        logdet += xp * QQ((-1) ** (j + 1), j)
    trlog, Mp = R(0), [[R(1) if i == j else R(0) for j in range(4)] for i in range(4)]
    for k in range(1, 5):
        Mp = [[sum((Mp[i][l] * Mm[l][j] for l in range(4)), R(0)) for j in range(4)] for i in range(4)]
        trlog += e ** k * sum((Mp[i][i] for i in range(4)), R(0)) * QQ((-1) ** (k + 1), k)
    # binomial sqrt series used by the independent evaluator: [sqrt(1+x)]^2 = 1+x mod e^5
    sq, term, coef = R(1), R(1), Fr(1)
    for k in range(1, 5):
        coef = coef * (Fr(1, 2) - (k - 1)) / k
        term = trunc(term * x)
        sq += term * QQ(coef.numerator, coef.denominator)
    return {"test": "log(-det q) = tr log(eta^{-1} q) and sqrt-series^2 = -det q, through eps^4, 10 symbolic components",
            "logdet_equals_trlog": trunc(logdet) == trunc(trlog),
            "sqrt_series_squared_equals_minus_det": trunc(sq * sq) == trunc(det),
            "pass": trunc(logdet) == trunc(trlog) and trunc(sq * sq) == trunc(det)}


# ---------------- C4 ----------------
def export_identity(contraction="correct", drop_sqrt_eps2=False):
    R, ell = SE.symbolic_ell(contraction=contraction, drop_sqrt_eps2=drop_sqrt_eps2)
    res = {}
    for k in (2, 3, 4):
        e, _ = PW.load_ell(k)
        res[f"ell{k}"] = ell[k] == R.from_expr(e)
    return {"test": "export == independent series evaluator over QQ[50 jet symbols] (polynomial identity)",
            "results": res, "pass": all(res.values())}, R, ell


def evaluator_regression(samples=3, seed=11):
    rng = random.Random(seed)
    ok = True
    for k in (2, 3, 4):
        cp = PW.compile_poly(PW.load_ell(k)[0])
        for _ in range(samples):
            H = PW.rnd_sym(rng)
            dH = [PW.rnd_sym(rng) for _ in range(4)]
            j = [Fr(0)] * len(PW.VARS)
            for m, n in PW.INDEX:
                j[PW.VPOS[f"H{m}{n}"]] = H[m][n]
                for r in range(4):
                    j[PW.VPOS[f"dH{m}{n}_{r}"]] = dH[r][m][n]
            ok &= PW.eval_poly(cp, j) == SE.ell_from_jet(H, dH)[k]
    return {"role": "regression control (sampled; NOT acceptance)", "samples_per_k": samples, "agree": ok}


# ---------------- C5 / C6 ----------------
def _gd():
    sys.path.insert(0, str(inherited.resolve(GRAV_DENSITY).parent))
    with contextlib.redirect_stdout(io.StringIO()):
        import grav_density as GD
    return GD


def xvin_symbolic():
    GD = _gd()
    sm = {}
    S = lambda m, n: (min(m, n), max(m, n))  # noqa: E731
    G = [[None] * 4 for _ in range(4)]
    dG = [[[None] * 4 for _ in range(4)] for _ in range(4)]
    ddG = [[[[None] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for m in range(4):
        for n in range(4):
            a, b = S(m, n)
            nm = f"G{a}{b}"
            G[m][n] = sp.Symbol(nm)
            sm[nm] = ("h", (a, b), ())
            for r in range(4):
                nm = f"dG{a}{b}_{r}"
                dG[r][m][n] = sp.Symbol(nm)
                sm[nm] = ("h", (a, b), (r,))
                for q in range(4):
                    r1, q1 = min(r, q), max(r, q)
                    nm = f"ddG{a}{b}_{r1}{q1}"
                    ddG[r][q][m][n] = sp.Symbol(nm)
                    sm[nm] = ("h", (a, b), (r1, q1))
    x3 = GD.ell3_and_curvature(G, dG, ddG)["ell3"]
    fp = GD.FP_density(G, dG)
    return J.from_sympy(x3, sm), J.from_sympy(fp, sm)


def regression_deterministic(ell_jet, X3, FP):
    c3 = GN.divergence_equal(ell_jet[3], X3)
    c2 = GN.divergence_equal(ell_jet[2], FP)
    wrong = GN.divergence_equal(ell_jet[3], J.scale(X3, -1))
    return {"cubic": {"test": "E_h(ell3 - ell3_XIIC) = 0 for all 10 components (exact)", **c3,
                      "NOT_XII_C_quartic": True, "NOT_Ward_identity": True},
            "quadratic": {"test": "E_h(ell2 - FP_XIA) = 0 for all 10 components (exact)", **c2},
            "sign_discrimination": {"ell3 + ell3_XIIC is a divergence": wrong["divergence"]},
            "source": GRAV_DENSITY,
            "source_sha256": inherited.sha(inherited.resolve(GRAV_DENSITY)),
            "source_pin_ok": inherited.sha(inherited.resolve(GRAV_DENSITY)) == inherited.PINS[GRAV_DENSITY]["sha256"]}


def planewave_regression(samples=1, seed=17):
    """Sampled regression control (NOT acceptance)."""
    GD = _gd()
    rng = random.Random(seed)

    def jet(legs):
        G = [[sp.Rational(sum(e[m][n] for e, _ in legs)) for n in range(4)] for m in range(4)]
        dG = [[[sp.Rational(sum(k[a] * e[m][n] for e, k in legs)) for n in range(4)] for m in range(4)] for a in range(4)]
        ddG = [[[[sp.Rational(sum(k[a] * k[b] * e[m][n] for e, k in legs)) for n in range(4)] for m in range(4)]
                for b in range(4)] for a in range(4)]
        return G, dG, ddG

    def pol(f, legs):
        tot = 0
        for r in range(1, len(legs) + 1):
            for S in itertools.combinations(range(len(legs)), r):
                tot += (-1) ** (len(legs) - r) * f([legs[i] for i in S])
        return sp.Rational(tot)
    ok = True
    for _ in range(samples):
        ks = [PW.rnd_vec(rng) for _ in range(2)]
        ks.append(PW.neg(PW.vadd(*ks)))
        legs = [(PW.rnd_sym(rng), k) for k in ks]
        ok &= sp.Rational(SE.polarized_ell(3, legs)) == pol(lambda L: GD.ell3_and_curvature(*jet(L))["ell3"], legs)
    return {"role": "regression control (sampled; NOT acceptance)", "samples": samples, "agree": ok}


def V4_polarization():
    return {"convention": C.POLARIZATION,
            "definition": "V4[h1,h2,h3,h4] := [t1 t2 t3 t4] ell_4(sum_i t_i h_i) = D^4 ell_4(0)[h1,h2,h3,h4]",
            "normalisation": "UNnormalised fourth variation; the normalised symmetric 4-linear form is V4/4! (not used)",
            "implemented_by": "planewave_exact.polarize / series_eval.polarized_ell (inclusion-exclusion) compute V4",
            "where_factors_enter": {"1/4!": "only in S2 = (1/4!) V4[h,h,h,h]; cancelled by the 4! leg assignments",
                                    "i": "vertex factor i from e^{iS}", "kappa": "kappa^2 (S = sum kappa^{k-2} int ell_k)",
                                    "D02_symmetry_factor": "1/2 at graph level (two legs contracted)",
                                    "D02_vertex_rule": "i kappa^2 V4[h1,h2,h3,h4]"},
            "D02_quantum_evaluated": False}


def main(from_cache=None):
    t0 = time.time()
    built = build_and_export(from_cache)
    print("built", {k: built[k] for k in (2, 3, 4)}, flush=True)
    c1 = inverse_control()
    c2 = det_tracelog_generic()
    bi = BI.run()
    (CERT / f"{C.CERT_PREFIX}_boundary_identity.json").write_text(certio.dumps(bi))
    c4, R, ell_ring = export_identity()
    names = [str(g) for g in R.gens]
    ell_jet, shas = GN.load_export_polys()
    X3, FP = xvin_symbolic()
    reg = regression_deterministic(ell_jet, X3, FP)
    c7 = GN.noether(ell_jet)
    c7_params = GN.parameters(shas, transport=1)
    c7_accept = certio.accepted_orders(c7)
    c7_ok = all(c7_accept.values()) and not certio.invariant_violations(c7)
    print("C1..C7", c1["pass"], c2["pass"], bi["C3_proved"], c4["pass"], reg["cubic"]["divergence"],
          reg["quadratic"]["divergence"], c7_ok, flush=True)
    # mutations (deterministic)
    e4 = dict(ell_jet[4])
    k0 = sorted(e4)[len(e4) // 2]
    e4[k0] *= Fr(7, 5)
    m1 = GN.noether({2: ell_jet[2], 3: ell_jet[3], 4: e4})["kappa2"]["Q_identically_zero"]
    m2 = GN.noether({2: ell_jet[2], 3: ell_jet[3], 4: J.scale(ell_jet[4], -1)})["kappa2"]["Q_identically_zero"]
    c4_sw, Rs, sw = export_identity(contraction="swapped")
    swj = {k: GN.ring_to_jet(sw[k], names) for k in (2, 3, 4)}
    reg_sw = regression_deterministic(swj, X3, FP)
    no_sw = GN.noether(swj)
    c4_ds, Rd, ds = export_identity(drop_sqrt_eps2=True)
    dsj = {k: GN.ring_to_jet(ds[k], names) for k in (2, 3, 4)}
    no_ds = GN.noether(dsj)
    stale_txt = (EXPORTS / "ell4_generating_polynomial.srepr").read_text().strip().replace("Integer(2)", "Integer(3)", 1)
    stale = hashlib.sha256(str(sp.sympify(stale_txt)).encode()).hexdigest() != built[4]["sha256"]
    muts = [
        {"mutation": "M1_corrupt_one_ell4_coefficient_x7/5", "failing_test": "C7 kappa^2 (Q != 0)", "rejected": not m1},
        {"mutation": "M2_wrong_overall_norm_ell4_sign", "failing_test": "C7 kappa^2 (Q != 0)", "rejected": not m2},
        {"mutation": "M3_swapped_GammaGamma_contraction", "failing_test": "C4, C5, C6, C7",
         "detail": {"C4": c4_sw["results"], "C5": reg_sw["cubic"]["divergence"], "C6": reg_sw["quadratic"]["divergence"],
                    "C7": {k: v["Q_identically_zero"] for k, v in no_sw.items()}},
         "rejected": (not c4_sw["pass"]) and not reg_sw["cubic"]["divergence"]
         and not all(v["Q_identically_zero"] for v in no_sw.values())},
        {"mutation": "M4_missing_sqrt_eps2_coefficient", "failing_test": "C4 ell4, C7 kappa^2",
         "detail": {"C4": c4_ds["results"], "C7": {k: v["Q_identically_zero"] for k, v in no_ds.items()}},
         "rejected": (not c4_ds["pass"]) and not no_ds["kappa2"]["Q_identically_zero"]},
        {"mutation": "M5_wrong_inverse_sign", "failing_test": "C1", "rejected": wrong_inverse_rejected()},
        {"mutation": "M6_stale_ell4_hash", "failing_test": "sha256 vs certificate", "rejected": stale},
        {"mutation": "M7_wrong_boundary_orientation (+d_mu B^mu)", "failing_test": "C3 generic + conformal",
         "rejected": (not bi["generic_jet_proof_old_orientation"]["identically_zero"])
         and bi["conformal_control_old_orientation_fails"]["fails"]},
    ]
    controls = {"C1": c1["pass"], "C2": c2["pass"], "C3": bi["C3_proved"], "C4": c4["pass"],
                "C5": reg["cubic"]["divergence"], "C6": reg["quadratic"]["divergence"], "C7": c7_ok}
    muts_ok = all(m["rejected"] for m in muts)
    verified = all(controls.values()) and muts_ok
    cert = {
        "revision": C.REVISION, "gate": "quartic_generator_verified",
        "execution_pass": True,
        "claim_status": "verified" if verified else "Partial",
        "scope": "classical EH quartic density ell_4 (Gamma-Gamma form, affine q = eta + kappa h) on declared conventions",
        "quartic_generator_verified": verified,
        "acceptance_controls_deterministic": controls,
        "all_acceptance_deterministic": True,
        "D02_vertex_available": verified, "D02_quantum_evaluated": False,
        "ell2_sha256": built[2]["sha256"], "ell3_sha256": built[3]["sha256"], "ell4_sha256": built[4]["sha256"],
        "terms_reproducibility": {k: built[k]["terms_reproducibility"] for k in (2, 3, 4)},
        "NOT_acceptance_by_term_count": True, "build": built, "conventions": CONVENTIONS,
        "controls": {"C1_inverse": c1, "C2_det_tracelog_generic": c2,
                     "C3_boundary_identity": f"{C.CERT_PREFIX}_boundary_identity.json (C3_proved={bi['C3_proved']})",
                     "C4_export_identity": c4, "C5_C6_regression": reg, "C7_noether_exact": c7,
                     "C7_parameters": c7_params, "C7_accepted_orders": c7_accept},
        "regression_controls_sampled_NOT_acceptance": {"evaluator_numeric": evaluator_regression(),
                                                       "planewave_cubic": planewave_regression()},
        "identification_of_exported_coefficients": (
            "exports/ell_k (sha above) == -2[eps^k] L_GG(eta + eps h) as polynomials (C4, independent evaluator); "
            "L_GG = sqrt(-g)R + d_mu B^mu exactly (C3); hence int ell_k = [kappa^{k-2}] S_EH for compact support."),
        "mutations": muts, "mutations_all_rejected": muts_ok,
        "polarization": V4_polarization(),
        "seconds": round(time.time() - t0, 1),
        "pass": verified,
    }
    (CERT / f"{C.CERT_PREFIX}_quartic_verified.json").write_text(certio.dumps(cert))
    v4 = {"id": "V4_grav", "revision": C.REVISION, "status": "Constructed" if verified else "not_verified",
          "quartic_generator_verified": verified, "D02_vertex_available": verified, "D02_quantum_evaluated": False,
          "ell4_sha256": built[4]["sha256"], "ell4_srepr_path": "exports/ell4_generating_polynomial.srepr",
          "terms_reproducibility": built[4]["terms_reproducibility"], "NOT_acceptance_by_term_count": True,
          "conventions": CONVENTIONS, "polarization": V4_polarization()}
    (EXPORTS / "V4_grav.json").write_text(certio.dumps(v4))
    print(json.dumps({"verified": verified, "controls": controls,
                      "mutations": {m["mutation"]: m["rejected"] for m in muts}, "sec": cert["seconds"]}, indent=1))
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
