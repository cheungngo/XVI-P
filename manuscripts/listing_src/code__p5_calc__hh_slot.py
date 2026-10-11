#!/usr/bin/env python3
"""XVI-P p17: do the evanescent poles of D01/D03 (kappa^2 hh self-energy) enter the ch-projected slot?

Row.  The hh two-point function of Gamma1 enters the ch projection of the one-loop identity ONLY through the r
  +> ow
(S0, Gamma1^[2]) s2 K:K.c (ledgers/P13_ch_dependency_rows.json; graphs D01, D02, D03, D11, D12):
    X_hh[c, h] = int (s h)_{(mn)}(p; c) G^{(mn)(rs)}(p) h_(rs)(-p),
where (s h)_{(mn)} = delta S0 / delta K^{(mn)} at linear order in c is read off the frozen S_Psi^(0) (the K.c 
  +> monomial;
exact covariant form recovered by an exact unique fit, H1) and G is the certified covariant hh vertex (P16_bat
  +> chC.json;
recomputed here by batchC.evaluate_graph and compared with the certificate).

Proof (exact in d; R1/R2: p in QdS, so p.gt = 0; no trace taken):
  H1  s h = (i/2)(p_m eta_nv + p_n eta_mv) c^v up to the fitted normalisation: LONGITUDINAL in (mn).
  H2  hence X_g = (contraction of p_m G_g^{(mn)(rs)}) only: every structure with gt on m or n drops (p.gt = 0)
  +> .
  H3  p_m (G_D01 + G_D03)^{(mn)(rs)} = 0 as a covariant tensor identity in free n, r, s, exactly in d -- both 
  +> the 4D
      and the evanescent (gt) parts separately; D02 = D12 = 0 (p15).  So X_{D01+D02+D03+D12} = 0 for every ext
  +> ernal
      assignment (Q4S, QdS, tilde, mixed): the D01/D03 evanescent poles DECOUPLE from the slot -- as a sum (th
  +> e ghost
      loop D03 cancels the longitudinal part of the graviton bubble D01), not graph by graph.
  H4  controls: X_D01 and X_D03 are individually NONZERO, including for gt-carrying external components (the
      cancellation is not a trivial drop-out of the evanescent structures); the 4D poles individually are not
      transverse, their sum is.
  Mutations (each must make the summed slot nonzero and be rejected): wrong relative sign of D03 (phase), D03 
  +> x 2
  (symmetry factor), evanescent part of D03 dropped (naive 4D), trace operator eta_mn p_v in place of s h.
Sharper 4D statement: the five p14r h.h directions span ALL five symmetric 4-derivative 4D structures, so 'pol
  +> e in
the span' is automatic; the non-automatic statement is that the summed 4D pole lies in the TRANSVERSE subspace
(the kernel of z -> p_m sum_i z_i B_i), of dimension 2, while the D01 and D03 poles individually do not.
D11 is NOT evaluated (M2 undischarged): its slot contribution is open; the D01/D03 statement does not depend o
  +> n it.
Phase (G6): every Ghat is defined with the same N_eps = i S_eps/(16 pi^2); D01/D03 carry an overall I (Ghat = 
  +> -i pref/
kappa^2 int, real export prefactors), D13 (prefactor I kappa^2) is real; the D01/D03 RELATIVE phase is tested 
  +> by H3
(mutation 'wrong relative sign' breaks it); s h carries an explicit i, so X_hh is real like the D13 slot.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import dred  # noqa: E402
import covariant as C  # noqa: E402
import e2_evanescent as E2M  # noqa: E402
import batchC as BC  # noqa: E402
import p17_conventions as QC  # noqa: E402

d = dred.d
PP = C.PP
PS = sp.symbols("p0:4")
I = sp.I
SPEC_KC = [("pair", ("m", "n")), ("vec", "v")]
GRAPHS = ("D01", "D03")
EXT = E2M.EXT


def log(m):
    print(f"[hh_slot {time.strftime('%H:%M:%S')}] {m}", flush=True)


def s(x):
    return str(sp.factor(x)) if x != 0 else "0"


# ---------------------------------------------------------------- H1: the slot operator from the frozen S0
def kc_operator():
    import counterterm_domain as CT
    import feynman as F
    S0 = CT.S0_density()
    polys = {}
    for a, mn in enumerate(F.HC):
        for v in range(4):
            val = F.pw_vertex(S0, [{"f": "K", "c": mn, "k": [-x for x in PS]}, {"f": "c", "c": v, "k": list(PS
  +> )}])
            if val != 0:
                polys[f"{a},{v}"] = sp.expand(val / I)            # the vertex is i x (real polynomial)
    fits = {}
    for off in (1, 2):
        for up in (False, True):
            f = C.covariant_fit({}, SPEC_KC, 1, offdiag=off, upper=up, polys=polys)
            fits[(off, up)] = f
    good = [(k, f) for k, f in fits.items() if f["exact"] and f["unique"] and f["terms"]]
    if not good:
        return None, {"exact": False, "candidates": {str(k): f["exact"] for k, f in fits.items()}}, polys
    (off, up), f = good[0]
    terms = []
    for orb, sc, c in f["terms"]:
        for facs in sorted(orb, key=str):
            terms.append((I * c * sc, list(facs)))
    return terms, {"exact": True, "unique": True, "offdiag_weight": off, "upper": up, "n_components": len(poly
  +> s),
                   "rank": f["rank"], "n_ansatz": f["n_ansatz"],
                   "covariant": sorted(([str(I * c * sc), [list(x) for x in sorted(orb, key=str)[0]]] for orb,
  +>  sc, c in f["terms"]),
                                       key=json.dumps)}, polys


def longitudinal_op(terms):
    return all(any(fct in (("p", "m"), ("p", "n")) for fct in facs) for _, facs in terms)


def trace_operator():
    """mutation M4: eta_mn p_v (not longitudinal)."""
    return [(I, [("g4", "m", "n"), ("p", "v")])]


# ---------------------------------------------------------------- the slot
def g_terms(A, scale=1, drop_evanescent=False):
    out = []
    for (orb, e), cf in A.items():
        if drop_evanescent and C.is_evanescent(orb):
            continue
        for facs in sorted(orb, key=str):
            out.append((scale * cf * PP ** e, list(facs)))
    return out


def slot_value(op_terms, gterms, ext):
    """X = op_{(mn) v} c^v G^{(mn)(rs)} a_r b_s (h_rs = a_(r b_s)), exact in d."""
    cn, an, bn = ext
    terms = []
    for co, fo in op_terms:
        for cg, fg in gterms:
            for (x, y) in ((an, bn), (bn, an)):
                facs = E2M.to_dred(fo) + E2M.to_dred(fg) + [("v", cn, "v"), ("v", x, "r"), ("v", y, "s")]
                terms.append((co * cg / 2, facs))
    res = E2M.contract_all(terms)
    assert all(k == () for k in res), "open indices left"
    return sp.factor(sp.cancel(sp.together(sp.expand(res.get((), 0)))))   # exact zero test in the opaque d


def p_dot_G(gterms):
    """p_m G^{(mn)(rs)} with free n, r, s (covariant tensor identity)."""
    res = E2M.contract_all([(c, E2M.to_dred(f) + [("v", "p", "m")]) for c, f in gterms])
    out = {}
    for k, v in sorted(res.items(), key=lambda kv: str(kv[0])):
        v = sp.cancel(sp.together(sp.expand(v)))      # exact zero test (rational functions of the opaque d)
        if v != 0:
            out[str(k)] = sp.factor(v)
    return out


def per_structure(A, op_terms):
    """for each structure orbit of G: does it reach the slot (any external assignment)?"""
    out = {}
    for k in sorted(A, key=lambda k: C.label(*k)):
        vals = {name: slot_value(op_terms, g_terms({k: sp.Integer(1)}), ext) for name, ext in EXT.items()}
        out[C.label(*k)] = {"evanescent": C.is_evanescent(k[0]),
                            "reaches_slot": any(v != 0 for v in vals.values()),
                            "gt_on_differentiated_pair": any(f[0] == "gt" and ("m" in f[1:] or "n" in f[1:])
                                                             for f in sorted(k[0])[0])}
    return out


# ---------------------------------------------------------------- 4D poles: transverse subspace of the p14r s
  +> pan
def pole_vec(A, keys):
    return {k: dred.substitute_d(A[k], 4, "hh_slot: UV pole A(4) of a 4D structure (after exact-d algebra)")
            for k in keys}


def pair_swap_class(label):
    """canonical class of a 4D structure label under the pair exchange (mn) <-> (rs)."""
    def canon(lab):
        toks = []
        for t in lab.split(" "):
            if "_" in t and not t.startswith("(p.p)"):
                head, idx = t.split("_", 1)
                t = head + "_" + "".join(sorted(idx))
            toks.append(t)
        return " ".join(sorted(toks))
    swapped = label.translate(str.maketrans({"m": "r", "n": "s", "r": "m", "s": "n"}))
    return min(canon(label), canon(swapped))


def transverse_analysis(polevecs, basis):
    zs = sp.symbols(f"z0:{len(basis)}")
    comb = {}
    for z, b in zip(zs, basis):
        for k, v in b["coords"].items():
            comb[k] = comb.get(k, 0) + z * v
    lon = BC.longitudinal_projection(comb)
    eqs = [sp.expand(v) for v in lon.values()]          # sympy objects (no string parsing)
    M = sp.Matrix([[sp.diff(e, z) for z in zs] for e in eqs]) if eqs else sp.zeros(0, len(zs))
    rank = M.rank()
    kernel = [list(v) for v in M.nullspace()]
    res = {"basis_dimension": len(basis), "span_is_all_4D_structures": None,
           "longitudinal_constraint_rank": rank, "transverse_subspace_dimension": len(basis) - rank,
           "transverse_basis_in_p14r_coordinates": [[str(x) for x in v] for v in kernel], "graphs": {}}
    keys4 = sorted({k for b in basis for k in b["coords"]}, key=lambda k: C.label(*k))
    classes = {pair_swap_class(C.label(*k)) for k in keys4}
    rank_b = sp.Matrix([[b["coords"].get(k, 0) for k in keys4] for b in basis]).rank()
    res["n_4D_orbit_labels"] = len(keys4)
    res["dim_pair_symmetric_4D_structures"] = len(classes)        # (mn) <-> (rs) symmetric combinations
    res["basis_rank"] = rank_b
    res["span_is_all_4D_structures"] = rank_b == len(classes) == len(basis)
    for name, vec in polevecs.items():
        z, ok = BC.pole_in_hh_basis(vec, basis)
        zz = [sp.nsimplify(x) for x in z] if z else None
        trans = bool(zz is not None and all(sp.expand(sum(r * x for r, x in zip(M.row(i), zz))) == 0
                                             for i in range(M.rows)))
        res["graphs"][name] = {"coordinates_p14r_basis": [str(x) for x in zz] if zz else None, "in_span": ok,
                               "transverse": trans}
    return res


# ---------------------------------------------------------------- main
def main():
    import certio
    t0 = time.time()
    cert = json.loads((ROOT / "certificates" / "P16_batchC.json").read_text())
    log("H1: K.c operator from S0")
    op, opfit, polys = kc_operator()
    evs, A = {}, {}
    for g in GRAPHS:
        log(f"{g}: covariant vertex (batchC.evaluate_graph)")
        evs[g] = BC.evaluate_graph(g)
        A[g] = evs[g]["A"]
    cert_equal = all(
        all(sp.cancel(v - dred.parse_d(cert["graphs"][g]["result"][C.label(*k)]["A_exact_d_times_MB"])) == 0
            for k, v in A[g].items()) and len(A[g]) == len(cert["graphs"][g]["result"]) for g in GRAPHS)
    log("H2/H3: slot values")
    slots = {g: {n: slot_value(op, g_terms(A[g]), e) for n, e in EXT.items()} for g in GRAPHS}
    slots_sum = {n: sp.factor(slots["D01"][n] + slots["D03"][n]) for n in EXT}
    ev_only = {g: {k: v for k, v in A[g].items() if C.is_evanescent(k[0])} for g in GRAPHS}
    d4_only = {g: {k: v for k, v in A[g].items() if not C.is_evanescent(k[0])} for g in GRAPHS}
    pdG = {g: p_dot_G(g_terms(A[g])) for g in GRAPHS}
    pdG_sum = p_dot_G(g_terms(A["D01"]) + g_terms(A["D03"]))
    pdG_ev_sum = p_dot_G(g_terms(ev_only["D01"]) + g_terms(ev_only["D03"]))
    pdG_4d_sum = p_dot_G(g_terms(d4_only["D01"]) + g_terms(d4_only["D03"]))
    pdG_ev = {g: p_dot_G(g_terms(ev_only[g])) for g in GRAPHS}
    ev_slot = {g: {n: slot_value(op, g_terms(ev_only[g]), e) for n, e in EXT.items()} for g in GRAPHS}
    log("per-structure table")
    struct = {g: per_structure(A[g], op) for g in GRAPHS}
    log("mutations")
    muts = {}
    for name, gt3 in (("M1_wrong_relative_sign_D03", g_terms(A["D03"], -1)),
                      ("M2_D03_times_2_symmetry_factor", g_terms(A["D03"], 2)),
                      ("M3_D03_evanescent_dropped_naive_4D", g_terms(A["D03"], drop_evanescent=True))):
        vals = {n: slot_value(op, g_terms(A["D01"]) + gt3, e) for n, e in EXT.items()}
        nz = any(v != 0 for v in vals.values())
        muts[name] = {"summed_slot_nonzero": nz, "rejected": nz, "accepted_as_rejection": nz,
                      "slot_values": {n: s(v) for n, v in vals.items()}}
    vals = {n: slot_value(trace_operator(), g_terms(A["D01"]) + g_terms(A["D03"]), e) for n, e in EXT.items()}
    nz = any(v != 0 for v in vals.values())
    muts["M4_trace_operator_in_place_of_s_h"] = {"summed_slot_nonzero": nz, "rejected": nz, "accepted_as_rejec
  +> tion": nz,
                                                 "slot_values": {n: s(v) for n, v in vals.items()}}
    log("4D poles: transverse subspace of the p14r h.h span")
    basis = BC.hh_basis()
    keys = {g: BC.four_d_keys(A[g]) for g in GRAPHS}
    pv = {g: pole_vec(A[g], keys[g]) for g in GRAPHS}
    tot = {}
    for g in GRAPHS:
        for k, v in pv[g].items():
            tot[k] = tot.get(k, 0) + v
    tr = transverse_analysis({"D01": pv["D01"], "D03": pv["D03"], "D01+D03": tot}, basis)
    ev_poles_sum = {}
    for g in GRAPHS:
        for k, v in ev_only[g].items():
            ev_poles_sum[C.label(*k)] = ev_poles_sum.get(C.label(*k), 0) + dred.substitute_d(
                v, 4, "hh_slot: evanescent UV pole A(4) (record only)")
    led = json.loads((ROOT / "ledgers" / "P13_ch_dependency_rows.json").read_text())["rows"]
    hh_rows = sorted(r["id"] for r in led if any(g.split("_")[0] in GRAPHS for g in r.get("graphs", [])))
    row_rec = {r["id"]: {"Gamma1_pattern": r.get("Gamma1_pattern"), "S_monomial": r.get("S_monomial"),
                         "differentiated": r.get("differentiated"), "graphs": r.get("graphs"),
                         "status": r.get("status")} for r in led if r["id"] in hh_rows}
    controls = {
        "ledger_hh_graphs_enter_exactly_one_row": hh_rows == [QC.SLOT_ROW]
        and row_rec[QC.SLOT_ROW]["Gamma1_pattern"] == "h^2" and row_rec[QC.SLOT_ROW]["S_monomial"] == "K.c",
        "H1_operator_exact_unique": bool(opfit.get("exact")),
        "H1_operator_longitudinal": bool(op) and longitudinal_op(op),
        "vertex_equals_P16_certificate": cert_equal,
        "H3_p_dot_G_sum_zero_exact_in_d": not pdG_sum,
        "H3_evanescent_part_p_dot_G_sum_zero": not pdG_ev_sum,
        "H3_4D_part_p_dot_G_sum_zero": not pdG_4d_sum,
        "H3_slot_sum_zero_all_external_assignments": all(v == 0 for v in slots_sum.values()),
        "H4_D01_slot_nonzero": any(v != 0 for v in slots["D01"].values()),
        "H4_D03_slot_nonzero": any(v != 0 for v in slots["D03"].values()),
        "H4_evanescent_parts_individually_reach_slot": all(any(v != 0 for v in ev_slot[g].values()) for g in G
  +> RAPHS),
        "H4_4D_poles_individually_not_transverse": not tr["graphs"]["D01"]["transverse"] and
        not tr["graphs"]["D03"]["transverse"],
        "4D_pole_sum_transverse": tr["graphs"]["D01+D03"]["transverse"],
        "transverse_subspace_dimension_2": tr["transverse_subspace_dimension"] == 2,
        "hh_basis_spans_all_pair_symmetric_4D_structures": tr["span_is_all_4D_structures"],
        "D01_plus_D03_coordinates_in_transverse_kernel": tr["graphs"]["D01+D03"]["in_span"],
        "mutations_all_rejected": all(v["accepted_as_rejection"] for v in muts.values()),
    }
    proven = all(controls.values())
    surviving = []          # evanescent structures of D01+D03 reaching the slot after summation
    if not controls["H3_evanescent_part_p_dot_G_sum_zero"]:
        surviving = sorted(pdG_ev_sum)
    rec = {
        "landmark": "XVI-P", "revision": QC.REVISION,
        "deliverable": "D01/D03 evanescent poles vs the ch-projected slot (row (S0,Gamma1^[2]) s2 K:K.c)",
        "question": ("do the evanescent (gt) UV poles of D01/D03 enter the ch-projected one-loop identity?"),
        "verdict": ("DECOUPLED (proof): as the sum D01 + D03 (+ D02 = D12 = 0); not graph by graph" if proven 
  +> else
                    ("PARTIALLY DECOUPLED" if surviving else "NOT ESTABLISHED")),
        "status": "decoupled_from_ch_slot_proven_as_sum" if proven else "open",
        "surviving_evanescent_structures_in_slot": surviving,
        "row": "(S0, Gamma1^[2]) s2 K:K.c (ledgers/P13_ch_dependency_rows.json; graphs D01, D02, D03, D11, D12
  +> ); "
               "the hh two-point function enters no other ch row (computed from the ledger: rows_with_D01_D03)
  +> ",
        "rows_with_D01_D03": row_rec,
        "functional": "X_hh[c,h] = int (s h)_{(mn)}(p; c) G^{(mn)(rs)}(p) h_(rs)(-p)",
        "operator_s_h": opfit,
        "proof": {
            "H1": "s h read off S_Psi^(0) (K.c monomial): exact unique covariant form, longitudinal in (mn)",
            "H2": "X_g depends on G only through p_m G^{(mn)(rs)}; p in QdS so p.gt = 0 removes gt on (mn)",
            "H3": "p_m (G_D01 + G_D03)^{(mn)(rs)} = 0 identically in d (4D and evanescent parts separately); "
                  "X_{D01+D03} = 0 for every external assignment; D02 = D12 = 0 (P15_batchA.json)",
            "H4": "controls: X_D01, X_D03 individually nonzero (also their evanescent parts); 4D poles individ
  +> ually "
                  "not transverse",
            "order": "one loop: the ch projection is linear in Gamma1; the cancellation is exact in d (not O(e
  +> ps)); "
                     "no product of evanescent poles arises"},
        "p_dot_G": {"D01": pdG["D01"], "D03": pdG["D03"], "D01+D03": pdG_sum,
                    "evanescent_D01": pdG_ev["D01"], "evanescent_D03": pdG_ev["D03"],
                    "evanescent_D01+D03": pdG_ev_sum},
        "slot_values": {g: {n: s(v) for n, v in slots[g].items()} for g in GRAPHS} |
                       {"D01+D03": {n: s(v) for n, v in slots_sum.items()}},
        "per_structure": struct,
        "evanescent_poles_D01_plus_D03_in_hh_green_function": {k: s(v) for k, v in sorted(ev_poles_sum.items()
  +> )},
        "consequence": ("no evanescent h.h counterterm is required by the ch-projected identity at one loop, s
  +> o NO "
                        "contract revision is made for it.  The summed evanescent poles of the hh Green functi
  +> on are "
                        "nonzero (list above) but TRANSVERSE; renormalising the hh Green function itself would
  +>  need "
                        "evanescent h.h counterterms -- relevant only outside this projection and NOT claimed.
  +>   D11 "
                        "(same row) is NOT evaluated: its slot contribution is open."),
        "four_D_poles": {**tr, "note": ("the five p14r h.h directions span all five symmetric 4-derivative 4D 
  +> "
                                        "structures, so span membership is automatic; the sharper, non-automat
  +> ic "
                                        "statement is transversality: the summed pole lies in the 2-dim transv
  +> erse "
                                        "subspace, the individual poles do not")},
        "phase_convention_G6": ("G = kappa^2 N_eps Ghat, N_eps = i S_eps/(16 pi^2) for every graph; D01/D03 Gh
  +> at = "
                                "-i pref/kappa^2 int (real export prefactors kappa^2/2, -kappa^2) carry an ove
  +> rall I; "
                                "D13 Ghat (prefactor I kappa^2) is real; s h = i(...) so X_hh is real like the
  +>  D13 slot; "
                                "the D01/D03 relative phase is tested by H3 (mutation M1 breaks it); the D13 v
  +> s hh relative "
                                "phase is not tested by a nonzero identity (both slot contributions vanish)"),
        "D11": "NOT evaluated (M2 undischarged); its contribution to this row is open",
        "controls": controls, "mutations": muts, "decoupling_proven": proven,
        "authorised_d_substitutions": dict(sorted(dred.D_PROVENANCE.items())),
        "quantum_inputs_evaluated": "not_earned", "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_hh_slot.json", rec)
    print(json.dumps({"verdict": rec["verdict"], "controls": controls,
                      "transverse": {k: v["transverse"] for k, v in tr["graphs"].items()},
                      "coords": {k: v["coordinates_p14r_basis"] for k, v in tr["graphs"].items()},
                      "mutations": {k: v["accepted_as_rejection"] for k, v in muts.items()}}, indent=1))
    return 0 if proven else 1


if __name__ == "__main__":
    raise SystemExit(main())
