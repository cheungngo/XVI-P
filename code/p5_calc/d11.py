#!/usr/bin/env python3
"""XVI-P p18: D11 (scalar matter loop in the hh two-point function) -- discharge of the matching premise M2,
evaluation of D11 under the declared prescription, and the full hh slot D01 + D02 + D03 + D11 + D12.

M2 (certificates/P14_prescription_D11_matching.json, matching.M2_nonlocal_agreement_on_U):
    for all f in D(U), U = R^4 \\ {0}:  <FT^-1[P^DR_AB](z), f> = <R_A R_B Pi_tr^R(z), f>,
    Pi_tr^R = (i kappa^2/4) K u^R,  K = alpha D2 + beta D0,  alpha = A^2/60, beta = A^2/18, A = 1/(4 pi^2).

Route B (explicit, exact; primary).  P^DR = kappa^2 N_eps Ghat with Ghat = sum_s A_s(d) S_s MB, MB = 1/eps + 2 - L,
L = log(-p^2/mu^2 - i0): the NONLOCAL part of P^DR at d -> 4 is  -(i kappa^2/16 pi^2) L sum_s A_s(4) S_s(p); every other
term is a polynomial in p.  On the XVI-O side, FT[u^R](p) = c_FT log(-p^2 - i0) + const (Gel'fand-Shilov: u^R is the
finite part of (Q - i0)^zeta at zeta = -2, whose residue is r delta; hence c_FT = -r = i pi^2), and K -> Khat(p) with
d_m -> -i p_m (P_tr_mn -> p_m p_n - eta_mn p^2; fourth order, so the sign convention of the FT drops out).  M2 then
holds iff the two L-coefficients agree, i.e. for every 4D component pair (A, B):
    X_AB := sum_s A_s(4) S_s|_AB  ==  -4 pi^2 c_FT A^2 Y_AB = -(i/4) Y_AB,   Y_AB := R_A R_B (Dhat2/60 + Dhat0/18).
If they agree, FT^-1[P^DR] - R R Pi_tr^R has a polynomial Fourier transform, so it is supported at {0}: M2.  (mu enters
only through polynomials: mu-independence on U.)  c_FT is calibrated twice: (a) independently of XVI-O, from the
library DR master bubble: FT[D_F^2] = (i)^2 int 1/(k^2 (p-k)^2) = -N_eps MB, and D_F^2 = A^2 u; (b) -r with the
XVI-O residue r = -i pi^2 (M5).
Route A (structural; corroboration).  M1 (re-run here): -i pref N^P/(D1 D2) = (i kappa^2/4) R R V V [C~C~ + C~C~]
exactly (100/100), i.e. the P integrand IS the Fourier convolution of the XVI-O product T = V V (C C + C C); a
regularised convolution agrees with the pointwise product on U (any two extensions differ at z = 0 only); and
T = K u on U (XVI-O all_256_symbolic, re-run here, frozen code imported read-only).  Route A uses the cited
distribution-theory fact; Route B uses only the stated Fourier transform of (Q - i0)^zeta.
Scope.  4D (hatted) components only: XVI-O is strictly four-dimensional.  The evanescent (gt) structures of D11 have
NONZERO L-coefficients (recorded); they are epsilon-scalar components and are not part of M2's 4D statement.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "code" / "matter_loop", ROOT / "tools"):
    sys.path.insert(0, str(p))
import dred  # noqa: E402
import covariant as C  # noqa: E402
import batchC as BC  # noqa: E402
import hh_slot as H  # noqa: E402
import integrals as IL  # noqa: E402
import p18_conventions as QC  # noqa: E402

d = dred.d
I = sp.I
PI = sp.pi
ETA = (1, -1, -1, -1)
PS = sp.symbols("p0:4")
LS = sp.symbols("l0:4")
PPV = sum(ETA[i] * PS[i] ** 2 for i in range(4))
A_XVIO = 1 / (4 * PI ** 2)
ALPHA, BETA = sp.Rational(1, 60), sp.Rational(1, 18)          # alpha/A^2, beta/A^2 (XVI-O, derived; re-derived below)
EXT = dict(H.EXT, **{"c hat, h tilde": ("c^", "a~", "b~")})      # H2: the seventh assignment


def log(m):
    print(f"[d11 {time.strftime('%H:%M:%S')}] {m}", flush=True)


def s(x):
    return str(sp.factor(x)) if x != 0 else "0"


def a_at_4(A, why):
    return {k: dred.substitute_d(v, 4, f"d11: {why}") for k, v in A.items()}


# ---------------------------------------------------------------- the two L-coefficients, component by component
def x_component(A4, Ai, Bi, offdiag=2):
    """sum_s A_s(4) S_s on the 4D component pair (A, B) (same convention as the covariant fit: pair weight, upper
    external indices via ETA, lower p_r); gt structures vanish on 4D components."""
    import feynman as F
    (m, n), (r, s_) = F.HC[Ai], F.HC[Bi]
    asg = {"m": m, "n": n, "r": r, "s": s_}
    w = C.pair_weight(BC.SPEC, asg, offdiag, upper=True)
    tot = 0
    for (orb, e), c in A4.items():
        if C.is_evanescent(orb):
            continue
        tot += c * PPV ** e * C.orbit_value(orb, asg, LS, PS)
    return sp.expand(w * tot)


def _ph(a, b):
    return PS[a] * PS[b] - (ETA[a] if a == b else 0) * PPV


def khat(a, b, c, e, al, be):
    D0 = _ph(a, b) * _ph(c, e)
    D2 = sp.Rational(1, 2) * (_ph(a, c) * _ph(b, e) + _ph(a, e) * _ph(b, c)) - sp.Rational(1, 3) * D0
    return al * D2 + be * D0


def y_component(Ai, Bi, al=ALPHA, be=BETA):
    import feynman as F
    from prescription_d11 import raise_map
    RA, RB = raise_map(F.HC[Ai]), raise_map(F.HC[Bi])
    return sp.expand(sum(RA[a, b] * RB[c, e] * khat(a, b, c, e, al, be)
                         for a in range(4) for b in range(4) for c in range(4) for e in range(4)
                         if RA[a, b] != 0 and RB[c, e] != 0))


def compare(A4, c_ft, al=ALPHA, be=BETA, offdiag=2):
    """X_AB == -4 pi^2 c_FT A^2 Y_AB on all 100 component pairs (exact)."""
    k = sp.simplify(-4 * PI ** 2 * c_ft * A_XVIO ** 2)
    bad, nz = [], 0
    for i in range(10):
        for j in range(10):
            x = x_component(A4, i, j, offdiag)
            nz += x != 0
            if sp.expand(x - k * y_component(i, j, al, be)) != 0:
                bad.append([i, j])
    return {"pairs": 100, "nonzero_pairs": nz, "mismatches": len(bad), "first": bad[:3], "agree": not bad,
            "constant": str(k)}


def ft_constant():
    """c_FT (coefficient of log(-p^2 - i0) in FT[u^R]) two ways."""
    ms = IL.master_series(1)
    pole, fin = sp.expand(ms[-1]), sp.expand(ms[0])
    n_eps = I / (16 * PI ** 2)                                     # S_eps -> 1 (MS-bar)
    c_bubble = sp.expand(-n_eps * fin.coeff(IL.L))                 # FT[D_F^2] = (i)^2 N_eps MB
    c_a = sp.simplify(c_bubble / A_XVIO ** 2)
    m5 = json.loads((ROOT / "certificates" / "P14_prescription_D11_matching.json").read_text())["matching"]["M5_residue"]
    r_ok = m5["r"] == "-i * pi**2"                                 # string compared, not parsed
    r = -I * PI ** 2
    return {"master_pole": str(pole), "master_finite": str(fin), "pole_is_1": pole == 1,
            "L_coefficient_of_MB": str(fin.coeff(IL.L)),
            "c_FT_from_DR_bubble": str(c_a), "c_FT_from_minus_r": str(-r), "r_certificate": m5["r"],
            "r_certificate_as_expected": r_ok, "agree": bool(r_ok and sp.simplify(c_a + r) == 0),
            "value": c_a}


def xvio_controls():
    import d11_global_representation as O
    ab = O.derive_alpha_beta()
    Asym = O.A_SYM
    a_ok = sp.simplify(ab["alpha_sympy"] - Asym ** 2 * ALPHA) == 0 and sp.simplify(ab["beta_sympy"] - Asym ** 2 * BETA) == 0
    full = O.all_256_symbolic(ab["alpha_sympy"], ab["beta_sympy"])
    return {"alpha_beta_rederived": {"alpha": str(ab["alpha_sympy"]), "beta": str(ab["beta_sympy"]), "match": a_ok},
            "K_u_equals_T_all_256": {"status": full.get("status"), "pass": bool(full.get("pass")),
                                     "components": full.get("symbolic_components_checked"),
                                     "failures": len(full.get("symbolic_failures", []))},
            "ok": bool(a_ok and full.get("pass"))}


# ---------------------------------------------------------------- M2
def m2(evs):
    import prescription_d11 as PD
    A = evs["D11"]["A"]
    A4 = a_at_4(A, "L-coefficient A(4) of D11 (after exact-d algebra; M2 nonlocal comparison)")
    log("M2 calibration of c_FT")
    ft = ft_constant()
    c = ft["value"]
    log("M2 route B: 100 component pairs")
    main = compare(A4, c)
    log("M2 route A: M1 integrand identity and XVI-O K u = T")
    m1 = PD.M1_identity()
    xo = xvio_controls()
    trans = {"p_dot_G_4D_part": H.p_dot_G(H.g_terms({k: v for k, v in A.items() if not C.is_evanescent(k[0])})),
             "p_dot_G_evanescent_part": H.p_dot_G(H.g_terms({k: v for k, v in A.items() if C.is_evanescent(k[0])}))}
    trans["transverse_exact_in_d"] = not trans["p_dot_G_4D_part"] and not trans["p_dot_G_evanescent_part"]
    log("M2 mutations")
    A01_4 = a_at_4(evs["D01"]["A"], "M2 mutation: D01 in place of D11 (A(4))")
    muts = {
        "alpha_beta_swapped": compare(A4, c, al=BETA, be=ALPHA),
        "offdiagonal_weight_1": compare(A4, c, offdiag=1),
        "FT_log_constant_sign_flipped": compare(A4, -c),
        "symmetry_factor_doubled": compare({k: 2 * v for k, v in A4.items()}, c),
        "D01_in_place_of_D11": compare(A01_4, c),
        "D0_dropped_beta_0": compare(A4, c, be=0),
    }
    for v in muts.values():
        v["rejected"] = not v["agree"]
        v["accepted_as_rejection"] = v["rejected"]
    ev_L = {C.label(*k): s(-v) for k, v in sorted(A4.items(), key=lambda kv: C.label(*kv[0])) if C.is_evanescent(k[0])}
    controls = {"route_B_all_100_pairs_agree": main["agree"] and main["nonzero_pairs"] > 0,
                "FT_constant_two_calibrations_agree": ft["agree"],
                "route_A_M1_integrand_identity": m1.get("pass") is True and not m1.get("mismatches"),
                "route_A_XVI_O_K_u_equals_T": xo["ok"],
                "D11_transverse_exact_in_d": trans["transverse_exact_in_d"],
                "routes_FP_PV_agree": evs["D11"]["routes_agree"],
                "covariant_fit_exact_unique": bool(evs["D11"]["fit"]["exact"] and evs["D11"]["fit"]["unique"]),
                "mutations_all_rejected": all(v["accepted_as_rejection"] for v in muts.values())}
    ok = all(controls.values())
    return {
        "statement": ("M2 (P14_prescription_D11_matching.json): for all f in D(U), U = R^4 \\ {0}: <FT^-1[P^DR_AB], f> "
                      "= <R_A R_B Pi_tr^R, f>, Pi_tr^R = (i kappa^2/4) K u^R, alpha = A^2/60, beta = A^2/18"),
        "verdict": "DISCHARGED (4D components)" if ok else "NOT DISCHARGED",
        "D11_matching_verified": ok,
        "D11_matching_verified_scope": "4D components",
        "evanescent_components_matching": {
            "status": "not_applicable_not_verified",
            "what_they_are": ("the 8 D11 structures carrying gt (the (4-d)-dimensional part of g4 = ghat + gt): "
                              "components of the hh two-point function with at least one index pair in the "
                              "epsilon-scalar (4-d) directions of DRED; they vanish on hatted 4D components"),
            "why_not_matched": ("XVI-O (u^R_mu, K, Pi_tr^R) is strictly four-dimensional and has NO evanescent "
                                "counterpart; M2 is a 4D statement, so there is nothing to match them to. Their "
                                "L-coefficients are nonzero (recorded below); they are retained (R6) and drop out of "
                                "the ch-projected slot (p_m G_D11 = 0 for the evanescent part separately)")},
        "route_B": {"equation": "X_AB = -4 pi^2 c_FT A^2 Y_AB = -(i/4) Y_AB on every 4D component pair", **main},
        "FT_constant": {k: v for k, v in ft.items() if k != "value"},
        "route_A": {"M1": {k: m1.get(k) for k in ("component_pairs_checked", "nonzero_pairs", "mismatches", "pass",
                                                  "recomputed_integrand_sha256", "exported_integrand_sha256")},
                    "XVI_O": xo},
        "transversality": {k: (v if isinstance(v, bool) else {kk: str(vv) for kk, vv in v.items()})
                           for k, v in trans.items()},
        "mutations": muts, "controls": controls,
        "analytic_inputs_cited": [
            "Fourier transform of (Q - i0)^zeta (Gel'fand-Shilov): meromorphic in zeta, residue at zeta = -2 is "
            "r delta, so FT[u^R] = -r log(-p^2 - i0) + const (Route B; cross-checked by the DR bubble)",
            "a polynomial in p is the Fourier transform of a distribution supported at {0}",
            "Route A only: two extensions of the product V V (C C + C C) from U differ by a distribution supported "
            "at 0 (XVI-O lem:BV_rules_on_U, Constructed)"],
        "scope": ("4D (hatted) components; the evanescent gt structures are epsilon-scalar components outside the 4D "
                  "statement of M2 (their L-coefficients are nonzero and recorded); IR: the massless bubble at "
                  "p^2 != 0 is IR finite in DR (no scaleless pieces enter the nonlocal part); the XVI-N massless "
                  "obstruction concerns the classical insertion and is not touched"),
        "evanescent_L_coefficients": ev_L,
        "M3_status": {
            "status": "unconditional on the 4D components (M2 discharged there; cited analytic inputs above)",
            "statement": ("L_match = FT^-1[P^DR] - R R Pi_tr^R is supported at {0}; with kernel scaling degree <= 8 it is "
                          "a finite sum of d^alpha delta with |alpha| <= 4 (bounds 4/8/4 of P14 M3)"),
            "evanescent_components": "not applicable (no XVI-O counterpart; see evanescent_components_matching)"},
        "M3_consequence": ("with M2 discharged, L_match = FT^-1[P^DR] - R R Pi_tr^R is supported at 0; both sides are "
                           "transverse and homogeneous of degree four in p (massless; no mu^4, mu^2 p^2 contacts, "
                           "consistent with N4), so L_match lies in the 2-dim transverse subspace of the p14r h.h "
                           "span; its coordinates need the XVI-O finite constant of u^R and are NOT computed (M4: "
                           "booked as P-side hh counterterm; u^R_mu unmodified, no c delta)"),
    }


# ---------------------------------------------------------------- D11 evaluation (batchC certificate style)
def d11_mutations(ev):
    import feynman as F  # noqa: F401
    out = {}
    k0 = next(iter(ev["A"]))
    a0 = ev["A"][k0]
    try:
        a0.subs(d, 4)
        out["premature_d4"] = {"rejected": False, "changes_result": None}
    except dred.PrematureD4Substitution as exc:
        lt = BC.laurent_table(ev["A"])
        out["premature_d4"] = {"rejected": True,
                               "changes_result": any(v["d_dependence_shift_of_local_part"] != 0 for v in lt.values()),
                               "reason": f"PrematureD4Substitution: {exc}"}
    ev4 = BC.evaluate_graph("D11", fit=ev["fit"], drop_evanescent_in="fp")
    out["drop_evanescent_gt"] = {"changes_result": set(ev4["A"]) != set(ev["A"]), "rejected": not ev4["routes_agree"],
                                 "reason": "FP route with gt dropped != PV route (R6 retention check)"}
    f5 = C.covariant_fit(ev["body"]["numerator"], BC.SPEC, 4, offdiag=2, upper=False)
    out["wrong_external_index_position"] = {"changes_result": True, "rejected": not f5["exact"]}
    f6 = C.covariant_fit(ev["body"]["numerator"], BC.SPEC, 4, offdiag=1, upper=True)
    out["wrong_offdiagonal_weight"] = {"changes_result": True, "rejected": not f6["exact"]}
    for v in out.values():
        v["accepted_as_rejection"] = bool(v["rejected"] and v["changes_result"])
    return out


def d11_record(ev, m2rec):
    A = ev["A"]
    lt = BC.laurent_table(A)
    basis = BC.hh_basis()
    pole4 = {k: lt[k]["pole"] for k in BC.four_d_keys(A)}
    z, zok = BC.pole_in_hh_basis(pole4, basis)
    ev_nonzero = any(lt[k]["pole"] != 0 for k in A if C.is_evanescent(k[0]))
    muts = d11_mutations(ev)
    degs = {C.label(*k): sum(1 for t in C.label(*k).split() if t.startswith("p_")) + 2 * k[1] for k in A}
    ctrl = {"exactly_degree_four_every_structure": all(v == 4 for v in degs.values()),
            "N4_no_order_0_or_2_contact_arises": all(v == 4 for v in degs.values()),"export_sha_pinned": ev["pin"]["pinned"], "covariant_form_exact": ev["fit"]["exact"],
            "covariant_form_unique": ev["fit"]["unique"], "orbit_consistent": ev["orbit_consistent"],
            "route_FP_equals_route_PV_exact_in_d": ev["routes_agree"],
            "integrand_equals_XVI_O_convolution_M1": m2rec["controls"]["route_A_M1_integrand_identity"],
            "exchange_symmetric_mn_rs": BC.exchange_symmetric(A),
            "nonlocal_equals_minus_pole": all(sp.simplify(lt[k]["nonlocal_L_coefficient"] + lt[k]["pole"]) == 0
                                              for k in A),
            "pole_4D_in_p14r_hh_span": bool(zok),
            "R5_d_retained": any(v.has(d) for v in A.values()),
            "M2_discharged": m2rec["D11_matching_verified"],
            "mutations_all_rejected": all(v["accepted_as_rejection"] for v in muts.values())}
    ok = all(ctrl.values())
    table = {C.label(*k): {"evanescent": C.is_evanescent(k[0]), "A_exact_d_times_MB": BC.s(lt[k]["exact_d"]),
                           "UV_pole": BC.s(lt[k]["pole"]), "MSbar_finite": BC.s(lt[k]["finite"]),
                           "nonlocal_coefficient_of_L": BC.s(lt[k]["nonlocal_L_coefficient"]),
                           "local_polynomial": BC.s(lt[k]["local"]),
                           "finite_if_d_set_to_4_first": BC.s(lt[k]["finite_if_d_set_to_4_first"]),
                           "local_shift_from_d_dependence": BC.s(lt[k]["d_dependence_shift_of_local_part"])}
             for k in sorted(A, key=lambda k: C.label(*k))}
    return {"graph": "D11", "export": ev["pin"], "prefactor_export": str(ev["pref"]),
            "normalization": f"Ghat = {BC.norm_of(ev['pref'])} * int N/(D1 D2) / N_eps",
            "prescription": ("operational DRED (R1-R6), d opaque, MS-bar, Feynman +i0, N4 contact exclusions, M3 bounds "
                             "4/8/4, exactly-degree-four normalization (massless: every local term is a homogeneous "
                             "quartic in p)"),
            "covariant_form": {k: v for k, v in ev["fit"].items() if k != "terms"},
            "prescription_usage": {
                "exactly_degree_four_normalization": ("every structure S_s (p.p)^e of Ghat has total momentum degree 4 "
                                                      "(computed per structure: " + ", ".join(f"{k}: {v}" for k, v in
                                                                                             sorted(degs.items())) + ")"),
                "N4_contact_exclusions": ("used as stated: the order-0/2 contacts (mu^4, mu^2 p^2) excluded by N4 do not "
                                          "arise (massless; every pole and local MS-bar term is a homogeneous quartic "
                                          "in p), so N4 removes nothing here and no order-0/2 counterterm is needed"),
                "M3_bounds_4_8_4": "degree of divergence 4; local terms of derivative order exactly 4 <= 4"},
            "result": table, "evaluated": ok,
            "status": "renormalized (4D) / regulated (evanescent poles nonzero, retained R6)" if ok and ev_nonzero
            else ("renormalized" if ok else "unevaluated"),
            "UV_pole_in_p14r_hh_basis": [BC.s(x) for x in z] if z else None,
            "evanescent_poles": {C.label(*k): str(lt[k]["pole"]) for k in A if C.is_evanescent(k[0])},
            "evanescent_pole_nonzero": ev_nonzero,
            "longitudinal_projection_p_m_G": {k: str(v) for k, v in sorted(BC.longitudinal_projection(A).items())},
            "controls": ctrl, "mutations": muts}


# ---------------------------------------------------------------- the full hh slot
def slot_record(evs):
    op, opfit, _ = H.kc_operator()
    A = {g: evs[g]["A"] for g in QC.HH_SLOT_GRAPHS}
    gt = {g: H.g_terms(A[g]) for g in A}
    ev_only = {g: {k: v for k, v in A[g].items() if C.is_evanescent(k[0])} for g in A}
    allg = gt["D01"] + gt["D03"] + gt["D11"]
    slots = {g: {n: H.slot_value(op, gt[g], e) for n, e in EXT.items()} for g in A}
    slot_sum = {n: H.slot_value(op, allg, e) for n, e in EXT.items()}
    ev_slot_sum = {n: H.slot_value(op, sum((H.g_terms(ev_only[g]) for g in A), []), e) for n, e in EXT.items()}
    ev_slot_d11 = {n: H.slot_value(op, H.g_terms(ev_only["D11"]), e) for n, e in EXT.items()}
    pdG = {"D11": H.p_dot_G(gt["D11"]), "D01+D03+D11": H.p_dot_G(allg),
           "evanescent_D01+D03+D11": H.p_dot_G(sum((H.g_terms(ev_only[g]) for g in A), []))}
    tr_d11 = {n: H.slot_value(H.trace_operator(), gt["D11"], e) for n, e in EXT.items()}
    muts = {}
    for name, terms in (("M1_wrong_relative_sign_D03", gt["D01"] + H.g_terms(A["D03"], -1) + gt["D11"]),
                        ("M3_D03_evanescent_dropped_naive_4D", gt["D01"] + H.g_terms(A["D03"], drop_evanescent=True)
                         + gt["D11"])):
        vals = {n: H.slot_value(op, terms, e) for n, e in EXT.items()}
        nz = any(v != 0 for v in vals.values())
        muts[name] = {"rejected": nz, "accepted_as_rejection": nz}
    vals = {n: H.slot_value(H.trace_operator(), allg, e) for n, e in EXT.items()}
    muts["M4_trace_operator_in_place_of_s_h"] = {"rejected": any(v != 0 for v in vals.values()),
                                                 "accepted_as_rejection": any(v != 0 for v in vals.values())}
    basis = BC.hh_basis()
    pv = {g: H.pole_vec(A[g], BC.four_d_keys(A[g])) for g in A}
    tot = {}
    for g in A:
        for k, v in pv[g].items():
            tot[k] = tot.get(k, 0) + v
    tr = H.transverse_analysis({"D11": pv["D11"], "D01+D03": {k: pv["D01"].get(k, 0) + pv["D03"].get(k, 0)
                                                               for k in set(pv["D01"]) | set(pv["D03"])},
                                "D01+D03+D11": tot}, basis)
    ev_poles = {}
    for g in A:
        for k, v in ev_only[g].items():
            ev_poles[C.label(*k)] = ev_poles.get(C.label(*k), 0) + dred.substitute_d(
                v, 4, "d11: evanescent UV pole A(4) of the summed hh function (record only)")
    controls = {
        "operator_longitudinal": H.longitudinal_op(op),
        "p_dot_G_D11_zero_exact_in_d": not pdG["D11"],
        "p_dot_G_sum_zero_exact_in_d": not pdG["D01+D03+D11"],
        "p_dot_G_evanescent_sum_zero": not pdG["evanescent_D01+D03+D11"],
        "slot_sum_zero_all_7_assignments": all(v == 0 for v in slot_sum.values()),
        "evanescent_slot_sum_zero_all_7_assignments": all(v == 0 for v in ev_slot_sum.values()),
        "D01_D03_individually_nonzero_incl_c_hat_h_tilde": (any(v != 0 for v in slots["D01"].values())
                                                           and slots["D01"]["c hat, h tilde"] != 0
                                                           and slots["D03"]["c hat, h tilde"] != 0),
        "D11_reaches_slot_under_trace_operator": any(v != 0 for v in tr_d11.values()),
        "4D_pole_sum_D01_D03_D11_transverse": tr["graphs"]["D01+D03+D11"]["transverse"],
        "4D_pole_D11_transverse": tr["graphs"]["D11"]["transverse"],
        "mutations_all_rejected": all(v["accepted_as_rejection"] for v in muts.values()),
    }
    ok = all(controls.values())
    surviving = sorted(pdG["evanescent_D01+D03+D11"]) if pdG["evanescent_D01+D03+D11"] else []
    return {
        "row": QC.SLOT_ROW, "graphs": "D01 + D02 + D03 + D11 + D12 (D02 = D12 = 0, P15_batchA.json)",
        "verdict": ("DECOUPLED (proof, full row): p_m G = 0 exactly in d for D11 by itself and for D01 + D03 as a "
                    "sum; no evanescent structure survives in the slot" if ok else
                    ("EVANESCENT STRUCTURE SURVIVES" if surviving else "NOT ESTABLISHED")),
        "decoupling_proven_full_row": ok, "surviving_evanescent_structures_in_slot": surviving,
        "D11_reopens_evanescent_question": bool(surviving),
        "how_D11_decouples": ("graph by graph: D11 (scalar loop, conserved matter stress tensor) is transverse by itself, "
                              "4D and evanescent parts separately; its evanescent poles are nonzero but transverse. "
                              "Hence D11 mutations of phase or symmetry factor are NOT detectable by the slot (they are "
                              "tested by M2 instead); the slot sees D11 only through a non-longitudinal operator "
                              "(trace operator control: nonzero)"),
        "operator_s_h": opfit,
        "slot_values": {g: {n: s(v) for n, v in slots[g].items()} for g in A} |
                       {"D01+D03+D11": {n: s(v) for n, v in slot_sum.items()},
                        "evanescent_parts_D01+D03+D11": {n: s(v) for n, v in ev_slot_sum.items()},
                        "evanescent_part_D11": {n: s(v) for n, v in ev_slot_d11.items()},
                        "D11_under_trace_operator": {n: s(v) for n, v in tr_d11.items()}},
        "p_dot_G": {k: {kk: str(vv) for kk, vv in v.items()} for k, v in pdG.items()},
        "four_D_poles": tr,
        "evanescent_poles_D01_D03_D11_in_hh_green_function": {k: s(v) for k, v in sorted(ev_poles.items())},
        "consequence": ("no evanescent h.h counterterm is required by the ch-projected identity at one loop (D11 "
                        "included), so NO contract revision is made for it.  The summed evanescent poles of the hh "
                        "Green function are nonzero but transverse; renormalising the hh Green function itself would "
                        "need evanescent h.h counterterms -- outside this projection and NOT claimed."),
        "controls": controls, "mutations": muts}


# ---------------------------------------------------------------- inventory
def inventory():
    """every graph of every SURVIVING ch row (ledgers/P13_ch_dependency_rows.json), with its evaluation certificate."""
    led = json.loads((ROOT / "ledgers" / "P13_ch_dependency_rows.json").read_text())["rows"]
    out = {}
    for r in led:
        if not str(r.get("status", "")).startswith("surviving"):
            continue
        for gid in r.get("graphs", []):
            g = gid.split("_")[0]
            f = QC.INPUT_EVALUATION_P18.get(g, "MISSING")
            out[g] = {"row": r["id"], "graph_id": gid, "certificate": f, "present": (ROOT / f).is_file()}
    def flag(f, *keys):
        try:
            x = json.loads((ROOT / f).read_text())
            for k in keys:
                x = x[k]
            return x
        except (OSError, KeyError, TypeError, ValueError):
            return None
    stat = {g: v.get("status") for g, v in (flag("certificates/P15_batchA.json", "graphs") or {}).items()}
    for g in ("D02", "D12", "D14a", "D14b", "D14c"):
        out[g]["status"] = stat.get(g)
    for g in ("D01", "D03"):
        out[g]["status"] = flag("certificates/P16_batchC.json", "graphs", g, "status")
    out["D13"]["status"] = "evaluated (P15_D13.json)"
    out["D01"]["evaluated"] = flag("certificates/P16_batchC.json", "graphs", "D01", "evaluated") is True
    out["D03"]["evaluated"] = flag("certificates/P16_batchC.json", "graphs", "D03", "evaluated") is True
    out["D13"]["evaluated"] = flag("certificates/P15_D13.json", "D13_evaluated", "execution") is True
    claim = flag("certificates/P15_batchA.json", "batchA_evaluated", "claim") or ""
    for g in ("D02", "D12", "D14a", "D14b", "D14c"):
        out[g]["evaluated"] = (flag("certificates/P15_batchA.json", "batchA_evaluated", "execution") is True
                               and g in claim)
    return out


def main():
    import certio
    t0 = time.time()
    evs = {}
    for g in QC.HH_SLOT_GRAPHS:
        log(f"{g}: covariant vertex (batchC.evaluate_graph)")
        evs[g] = BC.evaluate_graph(g)
    m2rec = m2(evs)
    log(f"M2: {m2rec['verdict']}")
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_D11_M2.json",
                 {"landmark": "XVI-P", "revision": QC.REVISION, "deliverable": "D11 matching premise M2", **m2rec})
    if not m2rec["D11_matching_verified"]:
        log("M2 NOT discharged: D11 evaluation STOPPED (D11 stays NOT evaluated)")
        return 1
    log("D11 evaluation record")
    rec = d11_record(evs["D11"], m2rec)
    log("full hh slot")
    sl = slot_record(evs)
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_D11.json",
                 {"landmark": "XVI-P", "revision": QC.REVISION, "deliverable": "D11 evaluation under the declared "
                  "prescription", **rec, "D11_evaluated": rec["evaluated"],
                  "D11_matching_verified": m2rec["D11_matching_verified"],
                  "authorised_d_substitutions": dict(sorted(dred.D_PROVENANCE.items()))})
    # inventory AFTER P18_D11.json is written (fresh-build ordering fix: 'present' must see this run's cert)
    inv = inventory()
    inv["D11"]["evaluated"] = rec["evaluated"]
    inv["D11"]["status"] = rec["status"]
    no_missing = all(v["present"] and v.get("status") and "missing" not in str(v["status"]).lower()
                     and "unevaluated" not in str(v["status"]).lower() for v in inv.values())
    q_ok = (all(v.get("evaluated") for v in inv.values()) and set(inv) == set(QC.INVENTORY_P18) and no_missing
            and len({v["row"] for v in inv.values()}) == 3)
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_hh_slot.json",
                 {"landmark": "XVI-P", "revision": QC.REVISION,
                  "deliverable": "full hh slot (D01+D02+D03+D11+D12) vs the ch projection", **sl,
                  "inventory": inv, "quantum_inputs_evaluated": "earned" if q_ok else "not_earned",
                  "quantum_inputs_scope": ("every graph of the P13 inventory (three ch slots: hh, K.c, one-point) is "
                                           "evaluated under the one frozen prescription; this is NOT "
                                           "projected_identity_verified (the projected identity is not assembled)"),
                  "seconds": round(time.time() - t0, 1)})
    print(json.dumps({"M2": m2rec["verdict"], "M2_controls": m2rec["controls"], "D11_controls": rec["controls"],
                      "slot": sl["verdict"], "slot_controls": sl["controls"], "q": q_ok,
                      "coords": {k: v["coordinates_p14r_basis"] for k, v in sl["four_D_poles"]["graphs"].items()}},
                     indent=1))
    return 0 if (rec["evaluated"] and sl["decoupling_proven_full_row"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
