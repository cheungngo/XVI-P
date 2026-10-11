#!/usr/bin/env python3
"""XVI-P p22: evanescent components of the one-loop kappa^2 two-point functions (priorities 1 and 2).

  EV-M2  what the 8 evanescent (gt) D11 structures must satisfy.  XVI-O is strictly 4D, so "match XVI-O" has n
  +> o
         content for them.  Tested exactly (opaque d, covariant contraction):
           (i)   locality: every evanescent UV pole is a constant times a polynomial structure in p (local ope
  +> rator);
           (ii)  continuation hypotheses: are the evanescent components the d-dim continuation of the 4D kerne
  +> l?
                 g4 -> ghat (= g4 - gt) continuation and g4-kept continuation, tested on all 2^4 hat/tilde ext
  +> ernal
                 assignments -- both are REFUTED (recorded, not hidden);
           (iii) 4D decoupling: every evanescent structure (pole, finite part, nonlocal L part alike) vanishes
                 identically on hatted (4D) external legs, exactly in d.
         The provable matching statement is therefore EV-M2 = (i) + (iii): after the evanescent MS-bar subtrac
  +> tion the
         evanescent components are a pure local evanescent counterterm plus a finite evanescent remainder that
  +>  is
         identically zero on 4D external configurations; nothing is matched to XVI-O.
  EV-CT  p22 CONTRACT REVISION: evanescent counterterms (h.h gt-operators for D01/D03/D11; K'.c gt-operator E2
  +>  for D13;
         and its ghost-equation partner, the gt part SE of the ghost self-energy, c.cb) with coefficient = -(p
  +> ole).
         Checked: (a) sigma_0 closure in every sector they can reach (h.c: p.T = 0, E.E2 = 0; c.b: calibrated 
  +> on the
         closed 4D pair), (b) they leave the ch-projected identity unchanged (slot values zero, exact in d), (
  +> c) the
         finite evanescent remnants and O(eps) x pole effects at this order.
"""
from __future__ import annotations
import itertools
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p_ in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical"):
    sys.path.insert(0, str(p_))
import dred  # noqa: E402
import covariant as C  # noqa: E402
import e2_evanescent as E2M  # noqa: E402
import hh_slot as H  # noqa: E402
import batchC as BC  # noqa: E402
import p22_conventions as QC  # noqa: E402

I = sp.I
d = dred.d
PP = C.PP
CERT = ROOT / "certificates"
GRAPHS = ("D01", "D03", "D11")


def log(m):
    print(f"[evanescent {time.strftime('%H:%M:%S')}] {m}", flush=True)


def s(x):
    return str(sp.factor(x)) if x != 0 else "0"


def jl(name):
    return json.loads((CERT / name).read_text())


def zero(res):
    return all(sp.cancel(sp.together(v)) == 0 for v in res.values())


def pole(A):
    return dred.substitute_d(A, 4, "evanescent: UV pole A(4) of an evanescent structure (after exact-d algebra
  +> )")


# ------------------------------------------------------------------ tensor helpers (free indices m n r s)
def full_contract(gterms, ext):
    """T^{mnrs} x_m y_n z_r w_s, scalar, exact in d."""
    x, y, z, w = ext
    res = E2M.contract_all([(c, E2M.to_dred(f) + [("v", x, "m"), ("v", y, "n"), ("v", z, "r"), ("v", w, "s")])
                            for c, f in gterms])
    assert all(k == () for k in res)
    return sp.cancel(sp.together(res.get((), 0)))


EXT4 = [tuple(f"{n}{k}" for n, k in zip("abce", ks)) for ks in itertools.product("^~", repeat=4)]


def swap_g4_to_gh(gterms):
    out = []
    for c, f in gterms:
        out.append((c, [("gh",) + tuple(x[1:]) if x[0] == "g4" else x for x in f]))
    return out


def dhat(struct_terms, ppow):
    """de Donder operator (ghost equation, P15: Sigma = 2 i D[G]) without the i: D^m_v X = p_n X^{(mn)}_v
    - 1/2 p^m g4_{ab} X^{(ab)}_v  (free m, v)."""
    terms = []
    for t in struct_terms:
        ren = [tuple({"m": "a", "n": "b"}.get(i, i) if j else i for j, i in enumerate(f)) for f in t]
        terms.append((PP ** (ppow + 0), E2M.to_dred([tuple({"n": "b"}.get(i, i) if j else i for j, i in enumer
  +> ate(f))
                                                    for f in t]) + [("v", "p", "b")]))
        terms.append((-sp.Rational(1, 2) * PP ** ppow, E2M.to_dred(ren) + [("g", "4", "a", "b"), ("v", "p", "m
  +> ")]))
    return terms


def ytensor(name):
    """ghost self-energy structures (P15_D13 ghost_self_energy_pole), free m (= rho), v."""
    return {"S1": [(PP ** 2, E2M.to_dred([("g4", "m", "v")]))],
            "S2": [(PP, E2M.to_dred([("p", "m"), ("p", "v")]))],
            "SE": [(PP ** 2, E2M.to_dred([("gt", "m", "v")]))]}[name]


def close(terms):
    return E2M.contract_all(terms)


def main():
    import certio
    t0 = time.time()
    log("inputs: D01, D03, D11 exact-d amplitudes (batchC.evaluate_graph), P15_D13")
    A = {g: BC.evaluate_graph(g)["A"] for g in GRAPHS}
    ev = {g: {k: v for k, v in A[g].items() if C.is_evanescent(k[0])} for g in GRAPHS}
    four = {g: {k: v for k, v in A[g].items() if not C.is_evanescent(k[0])} for g in GRAPHS}
    d13 = jl("P15_D13.json")
    P = lambda t: dred.parse_d(str(t), {"I": I})  # noqa: E731
    A13 = {k: P(d13["result"][k]["A_exact_d_times_MB"]) for k in E2M.STRUCT}
    gse = d13["ghost_self_energy_pole"]
    sig_exact = {k: P(v) for k, v in gse["coefficients_exact_d"].items()}
    # ---------------------------------------------------------- coefficients (MS-bar: counterterm = -pole)
    evpole = {g: {C.label(*k): pole(v) for k, v in ev[g].items()} for g in GRAPHS}
    evpole_sum = {}
    for g in GRAPHS:
        for k, v in evpole[g].items():
            evpole_sum[k] = sp.nsimplify(evpole_sum.get(k, 0) + v)
    e2_pole, se_pole = pole(A13["E2"]), pole(sig_exact["SE"])
    stored_ok = (all(sp.simplify(pole(A13[k]) - P(d13["result"][k]["UV_pole"])) == 0 for k in E2M.STRUCT)
                 and all(sp.simplify(pole(sig_exact[k]) - P(gse["pole"][k])) == 0 for k in sig_exact))
    d11c = jl("P18_D11.json")["result"]
    d11_stored_ok = all(sp.simplify(evpole["D11"][k] - P(d11c[k]["UV_pole"])) == 0 for k in evpole["D11"])
    hhc = jl("P18_hh_slot.json")["evanescent_poles_D01_D03_D11_in_hh_green_function"]
    hh_stored_ok = set(hhc) == set(evpole_sum) and all(sp.simplify(evpole_sum[k] - P(hhc[k])) == 0 for k in hh
  +> c)
    pole_terms = {g: H.g_terms({k: pole(v) for k, v in ev[g].items()}) for g in GRAPHS}
    pole_sum_terms = sum((pole_terms[g] for g in GRAPHS), [])
    # ---------------------------------------------------------- EV-M2
    log("EV-M2: locality, continuation hypotheses, 4D decoupling")
    locality = all(not v.has(d) for g in GRAPHS for v in evpole[g].values())
    hat = tuple(f"{n}^" for n in "abce")
    dec4 = {}
    for g in GRAPHS:
        for k, v in ev[g].items():
            dec4[f"{g}: {C.label(*k)}"] = s(full_contract(H.g_terms({k: sp.Integer(1)}), hat))
    four_d_decoupled = all(v == "0" for v in dec4.values())
    cont = {}
    for g in ("D11",):
        full = H.g_terms(A[g])
        c_hat = swap_g4_to_gh(H.g_terms(four[g]))
        c_keep = H.g_terms(four[g])
        mis_hat = {"".join(e): s(full_contract(full, e) - full_contract(c_hat, e)) for e in EXT4}
        mis_keep = {"".join(e): s(full_contract(full, e) - full_contract(c_keep, e)) for e in EXT4}
        cont[g] = {"ghat_continuation_mismatches": {k: v for k, v in mis_hat.items() if v != "0"},
                   "g4_kept_continuation_mismatches": {k: v for k, v in mis_keep.items() if v != "0"},
                   "ghat_continuation_holds": all(v == "0" for v in mis_hat.values()),
                   "g4_kept_continuation_holds": all(v == "0" for v in mis_keep.values()),
                   "hatted_externals_agree_both": mis_hat["a^b^c^e^"] == "0" and mis_keep["a^b^c^e^"] == "0"}
    # ---------------------------------------------------------- EV-CT (a) closure
    log("EV-CT (a): sigma_0 closure, h.c and c.b")
    pdg = {g: {str(k): s(v) for k, v in H.p_dot_G(pole_terms[g]).items()} for g in GRAPHS}
    pdg_sum = {str(k): s(v) for k, v in H.p_dot_G(pole_sum_terms).items()}
    pdg_dd = {str(k): s(v) for k, v in H.p_dot_G(pole_terms["D01"] + pole_terms["D03"]).items()}
    E, fitE = E2M.operator_from_polys(E2M.S0_hh_operator())
    # E^{(mn)(rs)} E2_{(mn)v}: free r, s, v
    ee2 = close([(c * PP, E2M.to_dred(list(t)) + E2M.to_dred(f)) for t in E2M.STRUCT["E2"] for c, f in E])
    hc_closed = (not pdg_sum) and not ee2
    # c.b: image = alpha Dhat[X] + beta Y; calibrate beta/alpha on the closed 4D pair, then test the evanescen
  +> t pair.
    X4 = {k: pole(A13[k]) for k in ("T1", "T2", "T3")}
    Y4 = {k: pole(sig_exact[k]) for k in ("S1", "S2")}
    rho = sp.Symbol("rho")
    dx4 = sum((dhat([tuple(t) for t in E2M.STRUCT[k]], E2M.PPOW[k]) for k in X4 if X4[k] != 0), [])
    img4 = close([(c * X4[k], f) for k in X4 if X4[k] != 0
                  for c, f in dhat([tuple(t) for t in E2M.STRUCT[k]], E2M.PPOW[k])]
                 + [(rho * c * Y4[k], f) for k in Y4 for c, f in ytensor(k)])
    sol = sp.solve([sp.expand(v) for v in img4.values()], rho, dict=True)
    rho_val = sol[0][rho] if len(sol) == 1 else None
    del dx4
    if rho_val is not None:
        img_ev = close([(c * e2_pole, f) for c, f in dhat([tuple(t) for t in E2M.STRUCT["E2"]], 1)]
                       + [(rho_val * c * se_pole, f) for c, f in ytensor("SE")])
        img_ev_noSE = close([(c * e2_pole, f) for c, f in dhat([tuple(t) for t in E2M.STRUCT["E2"]], 1)])
        img_ev_flip = close([(-c * e2_pole, f) for c, f in dhat([tuple(t) for t in E2M.STRUCT["E2"]], 1)]
                            + [(rho_val * c * se_pole, f) for c, f in ytensor("SE")])
        exact_ghost_eq = close([(c * A13["E2"], f) for c, f in dhat([tuple(t) for t in E2M.STRUCT["E2"]], 1)]
                               + [(rho_val * c * sig_exact["SE"], f) for c, f in ytensor("SE")])
    else:
        img_ev = img_ev_noSE = img_ev_flip = exact_ghost_eq = {"calibration": "failed"}
    cb_closed = rho_val is not None and not img_ev
    # ---------------------------------------------------------- EV-CT (b) decoupling from the projected ident
  +> ity
    log("EV-CT (b): ch-slot values of the counterterms")
    op, opfit, _ = H.kc_operator()
    slot_hh = {n: s(H.slot_value(op, pole_sum_terms, e)) for n, e in H.EXT.items()}
    slot_hh_g = {g: {n: s(H.slot_value(op, pole_terms[g], e)) for n, e in H.EXT.items()} for g in GRAPHS}
    slot_kc = {n: s(e2_pole * E2M.slot(E2M.STRUCT["E2"], E, e, 1)) for n, e in E2M.EXT.items()}
    identity_unchanged = all(v == "0" for v in slot_hh.values()) and all(v == "0" for v in slot_kc.values())
    # ---------------------------------------------------------- EV-CT (c) remnants
    log("EV-CT (c): finite remnants and O(eps) x pole traces")
    traces = {}
    for g in GRAPHS:
        # g4^{mn} T_{mnrs} (a trace over one index pair; (4 - d) factors appear only through tr gt)
        r = close([(c, E2M.to_dred(f) + [("g", "4", "m", "n"), ("v", "a^", "r"), ("v", "b^", "s")])
                   for c, f in pole_terms[g]])
        traces[g] = s(sp.cancel(sp.together(r.get((), 0))))
    rsum = close([(c, E2M.to_dred(f) + [("g", "4", "m", "n"), ("v", "a^", "r"), ("v", "b^", "s")])
                  for c, f in pole_sum_terms])
    trace_sum = sp.cancel(sp.together(rsum.get((), 0)))
    remnants = {
        "finite_evanescent_remainder": "MS-bar finite parts (local + L) x gt-structures: recorded per structur
  +> e in "
                                       "P18_D11 / P16_batchC / P15_D13; NONZERO; identically zero on 4D (hatte
  +> d) "
                                       "external legs, exactly in d (four_d_decoupling below)",
        "O_eps_times_pole_at_this_order": ("none with QdS (hatted) external legs: all four indices are externa
  +> l, so "
                                           "tr gt = 4 - d never arises and the evanescent operators are ZERO o
  +> n hatted "
                                           "legs at every d; see the Q4S trace entry for the one place it can 
  +> arise"),
        "trace_of_pole_tensor_g4^{mn}T_mn,rs (hatted r,s)": {"per_graph": traces, "sum": s(trace_sum)},
        "O_eps_times_pole_Q4S_trace_external": {
            "finite_term_if_external_trace_mode_uses_g4": s(sp.cancel(trace_sum / (d - 4)) * (-2)),
            "rule": "(d - 4) x (1/eps) -> -2 (d = 4 - 2 eps); times the residue above",
            "status": ("NONZERO: a finite local transverse term arises iff the external trace mode is defined 
  +> with the "
                       "quasi-4D g4 (it then carries eps-scalar components); with QdS (hatted) external legs i
  +> t is "
                       "zero.  This is a scheme / external-state convention (DRED eps-scalar sector), disclose
  +> d: the "
                       "p22 renormalised result is stated for QdS external legs")},
        "where_O_eps_x_pole_would_enter": ("insertions of the evanescent counterterms into loops (two loops) o
  +> r into "
                                           "composite operators with traces: (4 - d) x (1/eps) = finite local 
  +> terms "
                                           "-- beyond this order; not evaluated, not claimed"),
    }
    # ---------------------------------------------------------- mutations
    muts = {
        "drop_D03_evanescent_ct (h.c)": bool(H.p_dot_G(pole_terms["D01"] + pole_terms["D11"])),
        "drop_D01_evanescent_ct (h.c)": bool(H.p_dot_G(pole_terms["D03"] + pole_terms["D11"])),
        "D03_evanescent_ct_x2 (h.c)": bool(H.p_dot_G(pole_terms["D01"] + pole_terms["D03"] + pole_terms["D03"]
                                                      + pole_terms["D11"])),
        "drop_SE_partner (c.b)": bool(img_ev_noSE),
        "flip_sign_E2_ct (c.b)": bool(img_ev_flip),
        "trace_operator_in_place_of_s0h (slot)": any(
            H.slot_value(H.trace_operator(), pole_sum_terms, e) != 0 for e in H.EXT.values()),
    }
    insensitive = {"D11_evanescent_ct_x2 (h.c)": ("p_m T_D11,ev = 0 by itself: the D11 evanescent counterterm 
  +> is "
                                                  "closed alone; its normalisation is pinned by the D11 pins, 
  +> not "
                                                  "by closure"),
                   "detected": bool(H.p_dot_G(pole_terms["D01"] + pole_terms["D03"] + pole_terms["D11"]
                                              + pole_terms["D11"]))}
    controls = {
        "poles_equal_stored_D13_and_Sigma": stored_ok, "D11_evanescent_poles_equal_stored": d11_stored_ok,
        "hh_evanescent_pole_sum_equals_P18_hh_slot": hh_stored_ok,
        "ev_poles_local": locality, "ev_four_D_decoupling_exact": four_d_decoupled,
        "ev_D11_hatted_externals_agree": cont["D11"]["hatted_externals_agree_both"],
        "hc_p_dot_T_ev_sum_zero": not pdg_sum, "hc_E_dot_E2_zero": not ee2,
        "hc_D01_D03_ev_sum_transverse": not pdg_dd, "hc_D01_alone_not_transverse": bool(pdg["D01"]),
        "cb_calibration_unique_on_4D_pair": rho_val is not None,
        "cb_ev_pair_closed": cb_closed, "ghost_equation_ev_exact_in_d": rho_val is not None and not exact_ghos
  +> t_eq,
        "identity_unchanged_hh_slot_zero_all_ext": all(v == "0" for v in slot_hh.values()),
        "identity_unchanged_kc_slot_zero_all_ext": all(v == "0" for v in slot_kc.values()),
        "D01_ev_ct_alone_reaches_slot": any(v != "0" for v in slot_hh_g["D01"].values()),
        "mutations_all_detected": all(muts.values()),
    }
    ok = all(controls.values())
    ev_m2_proven = locality and four_d_decoupled
    rec = {
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION,
        "deliverable": "p22 priorities 1-2: evanescent matching statement (EV-M2) and evanescent counterterms 
  +> (EV-CT)",
        "EV_M2": {
            "question": "what must the 8 evanescent D11 structures satisfy, given XVI-O has no evanescent coun
  +> terpart?",
            "candidates": {
                "match a d-dim continuation of the XVI-O kernel": (
                    "REFUTED for both natural continuations (g4 -> ghat; g4 kept): the exact D11 tensor differ
  +> s from "
                    "either continuation of its own 4D part on tilde external legs; XVI-O defines no other "
                    "continuation -- not a usable statement"),
                "vanish as eps -> 0 in the renormalised result": (
                    "TRUE in the stronger form: after subtraction, every evanescent component is identically Z
  +> ERO "
                    "on 4D external legs at every d (not merely O(eps))" if four_d_decoupled else "NOT ESTABLI
  +> SHED"),
                "be pure local evanescent operators": (
                    "TRUE for the UV poles (constants x polynomial gt-structures); FALSE for the finite parts 
  +> "
                    "(they carry L = log(-p^2/mu^2)): the finite remainder is nonlocal but evanescent"
                    if locality else "NOT ESTABLISHED")},
            "statement": ("EV-M2: the evanescent D11 poles are local evanescent operators (removed by the p22 
  +> "
                          "evanescent counterterm), and the renormalised evanescent remainder vanishes identic
  +> ally "
                          "on 4D external configurations, exactly in d.  No matching to XVI-O is asserted."),
            "verdict": "PROVEN (exact, opaque d)" if ev_m2_proven else "NOT ESTABLISHED",
            "locality": locality, "four_D_decoupling": dec4, "continuation_tests": cont},
        "D11_matching_verified_scope": (
            "4D components: M2 discharged (P18_D11_M2, unchanged); evanescent components: EV-M2 proven (local 
  +> poles + "
            "exact 4D decoupling of the renormalised remainder); NOT matched to XVI-O (no counterpart; both na
  +> tural "
            "d-dim continuations refuted)" if ev_m2_proven else "4D components only (P18); evanescent: not ver
  +> ified"),
        "EV_CT": {
            "contract_revision": ("p22: evanescent counterterms admitted outside the p14r 4D domain -- h.h ope
  +> rators "
                                  "O_k = 1/2 h_mn S_k^{(mn)(rs)}(gt, g4, p) h_rs for the 8 gt-structures of th
  +> e hh "
                                  "two-point function (D01 + D03 + D11), the K'.c operator K'^{mn} E2_{(mn)v} 
  +> c^v "
                                  "(D13) and its ghost-equation partner cb_m SE^m_v c^v (Sigma, gt p^4); "
                                  "coefficient = -(UV pole) (MS-bar, N_eps kappa^2 / eps normalisation of P14)
  +> "),
            "coefficients_hh_counterterm_per_graph": {g: {k: s(-v) for k, v in evpole[g].items()} for g in GRA
  +> PHS},
            "coefficients_hh_counterterm_sum": {k: s(-v) for k, v in sorted(evpole_sum.items())},
            "coefficient_Kc_E2": s(-e2_pole), "coefficient_ccb_SE": s(-se_pole),
            "a_closure": {"h.c": {"p_dot_T_ev_per_graph": pdg, "p_dot_T_ev_sum": pdg_sum, "E_dot_E2": len(ee2)
  +> ,
                                  "closed": hc_closed},
                          "c.b": {"calibration_rho_from_4D_pair": s(rho_val) if rho_val is not None else None,
                                  "image_ev_pair": {str(k): s(v) for k, v in img_ev.items()} if rho_val is not
  +>  None
                                  else img_ev, "closed": cb_closed,
                                  "ghost_equation_exact_in_d_gt_sector": rho_val is not None and not exact_gho
  +> st_eq},
                          "c.cbs": ("unreachable: S0's quadratic part is h.h, h.b, b.b, b.cbs (+ K.c, cb.c); s
  +> igma_0 "
                                    "of h.h, K'.c, cb.c bilinears lands in h.c and c.b only"),
                          "full_closure_with_4D_counterterm": ("closed: the 4D MS-bar counterterm is closed (P
  +> 20_defect, "
                                                               "unchanged) and sigma_0 is linear"
                                                               if hc_closed and cb_closed else "NOT closed")},
            "b_projected_identity": {"hh_slot_values_sum": slot_hh, "hh_slot_values_per_graph": slot_hh_g,
                                     "Kc_slot_values": slot_kc, "unchanged": identity_unchanged},
            "c_remnants": remnants},
        "mutations": muts, "insensitive_variations": insensitive, "controls": controls,
        "evanescent_counterterm_earned": ok,
        "EV_M2_status": "proven" if ev_m2_proven else "not proven",
        "EV_CT_status": "earned" if ok else "not earned",
        "P5_calculation_status": ("renormalized (one loop, kappa^2, two-point functions hh / K'.c / cb.c; MS-b
  +> ar in "
                                  "DRED with the p22 evanescent counterterms; external legs in QdS)" if ok els
  +> e
                                  "renormalized (4D) / regulated (evanescent poles nonzero, retained R6)"),
        "scope": ("one loop, kappa^2, the two-point functions entering the ch rows; NOT the one-point row beyo
  +> nd "
                  "kappa^1, not higher points, not two loops; not bulk symmetry, not O.1"),
        "authorised_d_substitutions": dict(dred.D_PROVENANCE),
        "seconds": round(time.time() - t0, 1),
    }
    certio.write(CERT / f"{QC.CERT_PREFIX}_evanescent.json", rec)
    log(f"EV-M2 {rec['EV_M2']['verdict']}; EV-CT earned={ok}; controls failing: "
        f"{[k for k, v in controls.items() if not v]}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
