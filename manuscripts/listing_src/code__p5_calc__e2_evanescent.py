#!/usr/bin/env python3
"""XVI-P p16 priority 1: does the D13 evanescent E2 pole (pole 1/16, A_E2 = 3/(16(d-1))) decouple from the
ch-projected slot?  Deterministic symbolic proof + mutation controls.

Where D13 enters the ch projection (P13 ch dependency rows, ledgers/P13_ch_dependency_rows.json): ONLY through
  +>  the row
(S0, Gamma1^[2]) s1 h:h^2, i.e. the slot functional
      X_D13[c, h] = int G_{(mn) nu}(p) c^nu(p) E^{(mn)(rs)}(p) h_(rs)(-p),
with G = delta Gamma1/delta K' (the D13 coefficient, G = kappa^2 N_eps sum_i A_i(d) T_i MB) and E = the operat
  +> or of
the h^2 monomials of S_Psi^(0) (delta S0/delta h at b = 0: the linearised Einstein-Hilbert operator; the b.h a
  +> nd b^2
monomials are separate rows and carry no h-only leg).

Proof (all steps exact in d, with the DRED objects of R1/R2: g4 = ghat + gtilde, p in QdS, external c, h with 
  +> Q4S
indices as declared, and also restricted to QdS or to Q(4-d)S):
  L1  E is TRANSVERSE: p_m E^{(mn)(rs)} = 0 as a covariant identity (verified on the exact covariant form of E
      recovered from the frozen S0 density; the contraction uses only g4.p = p and needs no trace, so it holds
  +>  for
      every d and for Q4S external indices).
  L2  E2_{(mn) nu} = (gt_{m nu} p_n + gt_{n nu} p_m) p^2 is LONGITUDINAL in (mn) (each term carries p_n or p_m
  +> ).
  L3  hence E2 . E = 0 identically: X_slot[E2] = 0 for every external assignment (Q4S, QdS, Q(4-d)S), exactly 
  +> in d, to
      all orders in eps.  The E2 pole therefore DECOUPLES from the ch-projected slot (not merely O(eps)).
  L4  the slot map is not trivial: X_slot[T1] and X_slot[E1] are nonzero (non-longitudinal structures), and th
  +> e D13
      coefficients A_T1 = A_E1 = 0 (P15_D13.json), so D13's whole contribution to the ch slot vanishes.
Mutation controls (each must make the E2 slot contribution NONZERO and be rejected by the L1/L2 checks):
  M1 the gauge-fixed (de Donder) operator q^2 P (Schur complement, NOT the h^2-monomial operator) in place of 
  +> E;
  M2 E1 = gt_mn p_nu p^2 (non-longitudinal) in place of E2;
  M3 E2 with its (mn) indices contracted in the wrong slot (E2_{(m nu) n}).
Scope: the ch-projected one-loop kappa^2 identity (one loop: the identity is linear in Gamma1, so no product o
  +> f two
evanescent poles occurs at this order).  The E2 pole remains a UV pole of the epsilon-scalar (Gt) component of
  +>  the
K'.c Green function of Gamma1; it does not enter the ch projection.
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
import dred  # noqa: E402
import covariant as C  # noqa: E402
import p16_conventions as QC  # noqa: E402

d = dred.d
PP = C.PP
PS = sp.symbols("p0:4")
HC = C.HC
SPEC_HH = [("pair", ("m", "n")), ("pair", ("r", "s"))]

STRUCT = {"T1": [(("g4", "m", "n"), ("p", "v"))], "T2": [(("g4", "m", "v"), ("p", "n")), (("g4", "n", "v"), ("
  +> p", "m"))],
          "T3": [(("p", "m"), ("p", "n"), ("p", "v"))], "E1": [(("gt", "m", "n"), ("p", "v"))],
          "E2": [(("gt", "m", "v"), ("p", "n")), (("gt", "n", "v"), ("p", "m"))]}
PPOW = {"T1": 1, "T2": 1, "T3": 0, "E1": 1, "E2": 1}
KIND = {"g4": "4", "gt": "t", "gh": "h"}


def to_dred(facs):
    out = []
    for f in facs:
        if f[0] in KIND:
            out.append(("g", KIND[f[0]], f[1], f[2]))
        else:
            out.append(("v", f[0] if f[0] == "p" else f[0], f[1]))
    return out


def operator_from_polys(polys):
    """exact covariant form of an h.h two-point operator given by its component polynomials in p (upper indice
  +> s,
    off-diagonal weight 2 -- the field-component convention of the frozen extraction)."""
    fit = C.covariant_fit({}, SPEC_HH, 2, offdiag=2, upper=True, polys=polys)
    terms = []
    for orb, sc, c in fit["terms"]:
        if any(f[0] == "l" for f in sorted(orb)[0]):
            raise ValueError("operator depends on l")
        for facs in orb:
            terms.append((c * sc, list(facs)))
    return terms, fit


def S0_hh_operator():
    import counterterm_domain as CT
    import feynman as F
    S0 = CT.S0_density()
    polys = {}
    for a in range(10):
        for b in range(10):
            v = F.pw_vertex(S0, [{"f": "h", "pol": {HC[a]: 1}, "k": list(PS)},
                                 {"f": "h", "pol": {HC[b]: 1}, "k": [-x for x in PS]}])
            if v != 0:
                polys[f"{a},{b}"] = v
    return polys


def gauge_fixed_operator():
    """M1: q^2 P (Schur complement of the b block; the de Donder gauge-fixed kinetic operator), same conventio
  +> n."""
    import feynman as F
    Pm = F.P_matrix()
    q2 = sum(dred.ETA[r] * PS[r] ** 2 for r in range(4))
    return {f"{a},{b}": sp.expand(q2 * Pm[a, b]) for a in range(10) for b in range(10) if Pm[a, b] != 0}


def contract_all(terms):
    rules = dred.Rules()
    out = {}
    for c, facs in terms:
        r = dred.contract([(sp.Integer(1), tuple(facs))], rules)
        for k, v in r.items():
            out[k] = sp.expand(out.get(k, 0) + c * v)
    return {k: v for k, v in out.items() if v != 0}


def transversality(Eterms):
    """L1: p_m E^{(mn)(rs)} with free n, r, s."""
    res = contract_all([(c, to_dred(f) + [("v", "p", "m")]) for c, f in Eterms])
    return {"residual_terms": len(res), "transverse": not res}


def longitudinal(name, struct=None):
    """L2: every term of the structure carries p_m or p_n."""
    st = struct or STRUCT[name]
    return all(any(f == ("p", "m") or f == ("p", "n") for f in t) for t in st)


EXT = {"Q4S (declared, R2)": ("c", "a", "b"), "QdS (hat)": ("c^", "a^", "b^"),
       "c tilde, h hat": ("c~", "a^", "b^"), "c tilde, h mixed": ("c~", "a~", "b^"),
       "c hat, h mixed": ("c^", "a~", "b^"), "all tilde": ("c~", "a~", "b~")}


def slot(struct_terms, Eterms, ext, ppow=1):
    """X = G_{mn v} c^v E^{mn rs} a_r b_s  (h_rs = a_(r b_s) symmetrised)."""
    cn, an, bn = ext
    terms = []
    for gt_ in struct_terms:
        for c, ef in Eterms:
            for (x, y) in ((an, bn), (bn, an)):
                facs = to_dred(list(gt_)) + to_dred(ef) + [("v", cn, "v"), ("v", x, "r"), ("v", y, "s")]
                terms.append((c * PP ** ppow / 2, facs))
    res = contract_all(terms)
    assert all(k == () for k in res), "open indices left"
    return sp.expand(res.get((), 0))


def has_trace_factor(expr):
    """does the (nonzero) slot value carry an explicit (4 - d) factor (an O(eps) trace)?"""
    return bool(expr != 0 and sp.cancel(expr / (4 - d)).is_polynomial() and sp.factor(expr).has(4 - d))


def main():
    import certio
    t0 = time.time()
    polys = S0_hh_operator()
    E, fitE = operator_from_polys(polys)
    L1 = transversality(E)
    table = {}
    for nm in STRUCT:
        table[nm] = {lab: str(sp.factor(slot(STRUCT[nm], E, ext, PPOW[nm]))) for lab, ext in EXT.items()}
    E2_zero_everywhere = all(v == "0" for v in table["E2"].values())
    nontrivial = any(v != "0" for v in table["T1"].values()) and any(v != "0" for v in table["E1"].values())
    d13 = json.loads((ROOT / "certificates" / "P15_D13.json").read_text())
    A = {k: sp.sympify(d13["result"][k]["A_exact_d_times_MB"], locals={"d": d}) for k in STRUCT}
    d13_slot = {lab: str(sp.factor(sum(A[k] * slot(STRUCT[k], E, ext, PPOW[k]) for k in STRUCT if A[k] != 0)))
                for lab, ext in EXT.items()}
    # ---- mutations
    muts = {}
    Egf, fitgf = operator_from_polys(gauge_fixed_operator())
    L1gf = transversality(Egf)
    v1 = {lab: str(sp.factor(slot(STRUCT["E2"], Egf, ext))) for lab, ext in EXT.items()}
    muts["M1_gauge_fixed_operator_qq2P"] = {"E2_slot_nonzero": any(v != "0" for v in v1.values()),
                                            "rejected": not L1gf["transverse"], "slot_values": v1,
                                            "reason": f"L1 fails: p_m (q^2 P)^(mn)(rs) has {L1gf['residual_ter
  +> ms']} "
                                                      "residual terms (q^2 P is not the h^2-monomial operator 
  +> of the "
                                                      "slot and is not transverse)"}
    v2 = {lab: table["E1"][lab] for lab in EXT}
    muts["M2_E1_in_place_of_E2"] = {"E2_slot_nonzero": any(v != "0" for v in v2.values()),
                                    "rejected": not longitudinal("E1"), "slot_values": v2,
                                    "reason": "L2 fails: gt_mn p_nu p^2 is not longitudinal in (mn)"}
    wrong = [(("gt", "m", "n"), ("p", "v")), (("gt", "v", "n"), ("p", "m"))]
    v3 = {lab: str(sp.factor(slot(wrong, E, ext))) for lab, ext in EXT.items()}
    muts["M3_wrong_index_slot"] = {"E2_slot_nonzero": any(v != "0" for v in v3.values()),
                                   "rejected": not longitudinal("E2w", wrong), "slot_values": v3,
                                   "reason": "L2 fails for the mis-slotted structure (gt_mn p_nu term)"}
    for v in muts.values():
        v["accepted_as_rejection"] = bool(v["E2_slot_nonzero"] and v["rejected"])
    controls = {"E_covariant_form_exact": fitE["exact"], "E_covariant_form_unique": fitE["unique"],
                "L1_E_transverse": L1["transverse"], "L2_E2_longitudinal": longitudinal("E2"),
                "L3_E2_slot_zero_all_externals": E2_zero_everywhere, "L4_slot_map_nontrivial": nontrivial,
                "D13_A_T1_and_A_E1_zero": A["T1"] == 0 and A["E1"] == 0,
                "D13_slot_contribution_zero": all(v == "0" for v in d13_slot.values()),
                "mutations_all_rejected": all(v["accepted_as_rejection"] for v in muts.values())}
    proven = all(controls.values())
    rec = {"landmark": "XVI-P", "revision": QC.REVISION, "deliverable": "p16 priority 1: E2 evanescent pole vs
  +>  the ch slot",
           "question": "does the D13 E2 pole (1/16; A_E2 = 3/(16(d-1))) decouple from the ch-projected slot?",
           "outcome": "DECOUPLED (proof)" if proven else "OPEN (proof incomplete)",
           "E2_status": "decoupled_from_ch_slot_proven" if proven else "open",
           "slot": {"row": "(S0, Gamma1^[2]) s1 h:h^2 (ledgers/P13_ch_dependency_rows.json; the only row conta
  +> ining D13)",
                    "functional": "X_D13[c,h] = int G_{(mn) nu}(p) c^nu(p) E^{(mn)(rs)}(p) h_(rs)(-p)",
                    "E": "operator of the h^2 monomials of S_Psi^(0) (counterterm_domain.S0_density, pw_vertex
  +>  "
                         "extraction; exact covariant form recovered, unique)",
                    "E_fit": {k: v for k, v in fitE.items() if k != "terms"},
                    "E_covariant": sorted(([str(c), [list(f) for f in fa]] for c, fa in E), key=json.dumps)[:4
  +> 0]},   # deterministic
           "proof": {"L1": "p_m E^{(mn)(rs)} = 0 (covariant identity; only g4.p = p used, no trace) -> " + str
  +> (L1),
                     "L2": "E2_{(mn)nu} = (gt_{m nu} p_n + gt_{n nu} p_m) p^2 is longitudinal in (mn)",
                     "L3": "E2 . E = 0 identically: slot value 0 for every external assignment, exact in d",
                     "L4": "T1, E1 (non-longitudinal) give nonzero slot values; A_T1 = A_E1 = 0 for D13",
                     "order": ("one loop: the ch projection of the one-loop identity is LINEAR in Gamma1; the 
  +> E2 "
                               "contribution is exactly zero (not O(eps)); no product of evanescent poles aris
  +> es "
                               "at this order")},
           "slot_table": table, "external_assignments": {k: list(v) for k, v in EXT.items()},
           "D13_slot_contribution": d13_slot,
           "consequence": ("the E2 pole does not enter the ch-projected identity; no evanescent counterterm is
  +>  needed "
                           "for the slot, so NO contract revision is made for E2.  The E2 pole remains a UV po
  +> le of the "
                           "epsilon-scalar (Gt) component of the K'.c Green function of Gamma1 (R6: retained, 
  +> recorded); "
                           "its renormalization is relevant only outside the ch projection (other projections,
  +>  higher "
                           "loops) and is NOT claimed here" if proven else
                           "proof incomplete: an evanescent counterterm is required (contract revision)"),
           "D13_graph_status": "regulated (unchanged: the E2 pole is not absorbed by a declared counterterm); 
  +> "
                               "ch-slot status: zero contribution (proven)",
           "mutations": muts, "controls": controls, "E2_decoupling_proven": proven,
           "authorised_d_substitutions": dict(dred.D_PROVENANCE),
           "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_E2_evanescent.json", rec)
    print(json.dumps({"outcome": rec["outcome"], "controls": controls, "E2": table["E2"], "T1": table["T1"],
                      "E1": table["E1"], "D13_slot": d13_slot,
                      "mutations": {k: [v["E2_slot_nonzero"], v["rejected"]] for k, v in muts.items()},
                      "seconds": rec["seconds"]}, indent=1))
    return 0 if proven else 1


if __name__ == "__main__":
    raise SystemExit(main())
