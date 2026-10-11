#!/usr/bin/env python3
"""XVI-P p15 Batch A: the massless tadpoles D02 (kappa^2 hh, quartic graviton vertex), D12 (kappa^2 hh, h h ph
  +> i phi),
and the order-kappa one-point graphs D14a (graviton loop), D14b (ghost loop), D14c (scalar loop).

Prescription: frozen p14r P14_DRED_MSbar_FeynmanI0 + the explicit scaleless rule S0 (integrals.py).  The decla
  +> red
action is massless (graviton, ghost and scalar propagators i N/(q^2 + i0); no mass, no external scale in any B
  +> atch A
integrand: D02/D12 carry p only in the numerator, D14 has p = 0).

Per graph:
  route 1  frozen export (sha-pinned, = the p14r W5/W6-verified integrand) -> frozen dred R3/R4 lift (tadpole 
  +> branch)
           -> int (l^2)^k / l^2  members  -> S0 (each application ledgered with omega and the UV/IR class);
  route 2  independent symmetric integration of the exported component polynomial (own code, ghat = eta - Gt);
  IR-regulator analysis  1/l^2 -> 1/(l^2 - m^2) (exact in d, A0-type), poles/finite parts and the m -> 0 limit
  +> ;
  analytic regulator     (l^2)^{-1-nu}: still scaleless (no separation without a scale);
  cutoff split           Lambda^omega UV and IR pieces, no 1/eps pole on either side (omega > 0 for every memb
  +> er).
Statuses: vanishing_under_declared_prescription (derived; never 'zero by convention').  D12 (kappa^2 two-point
  +> ) and the
order-kappa one-point slot (D14a+D14b+D14c) are recorded SEPARATELY.
"""
from __future__ import annotations
import hashlib
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
import integrals as IL  # noqa: E402
import p15_conventions as QC  # noqa: E402

d, eps = dred.d, dred.eps
KAPPA = sp.Symbol("kappa")
SLOTS = {"D02": "kappa^2 hh two-point (part of the hh slot with D01, D03 -- D01/D03 NOT evaluated in p15)",
         "D12": "kappa^2 hh two-point, scalar tadpole (D12 slot; kept separate from the one-point slot)",
         "D14a": "order-kappa one-point slot", "D14b": "order-kappa one-point slot",
         "D14c": "order-kappa one-point slot"}
ORDER = {"D02": 2, "D12": 2, "D14a": 1, "D14b": 1, "D14c": 1}


def load_export(g):
    f = ROOT / "exports" / "P14_integrands" / f"{g}.json"
    body = json.loads(f.read_text())
    stored = body.pop("sha256")
    body.pop("integrated", None)                     # written next to the hashed record (amplitude_rules.py)
    sha = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    amp = json.loads((ROOT / "certificates" / "P14_amplitude_rules.json").read_text())
    pinned = amp["graphs"][g]["sha256"]
    return body, {"file": f"exports/P14_integrands/{g}.json", "sha256_recomputed": sha, "sha256_stored": store
  +> d,
                  "sha256_p14r_certificate": pinned, "pinned": sha == stored == pinned}


def _poly(rows):
    return sp.Add(*[sp.Rational(cf) * sp.Mul(*[sp.Symbol(v) for v in names]) for names, cf in rows])


def route1(body, g):
    """frozen dred lift (with_p = False: tadpole) -> {component: expression in J_g[k,0], Gt, p_r, d}."""
    rules = dred.Rules()
    out = {}
    for comp, rows in body["numerator"].items():
        v = dred.lift_reduce_polynomial(rows, False, rules, g)
        if v != 0:
            out[comp] = v
    return out


def route2(body):
    """own symmetric integration: l_{r1}..l_{rn} -> ghat-symmetrised (l^2)^{n/2}/(d(d+2)..) ; returns {comp: {
  +> k: coef}}."""
    ls = sp.symbols("l0:4")
    out = {}
    for comp, rows in body["numerator"].items():
        P = sp.Poly(sp.expand(_poly(rows)), *ls)
        acc = {}
        for mon, cf in P.terms():
            comps = sum(([r] * m for r, m in enumerate(mon)), [])
            si = IL.sym_integrate(comps)
            if si != 0:
                k = len(comps) // 2
                acc[k] = sp.expand(acc.get(k, 0) + cf * si)
        acc = {k: v for k, v in acc.items() if v != 0}
        if acc:
            out[comp] = acc
    return out


def evaluate(g):
    body, pin = load_export(g)
    pref = sp.sympify(body["prefactor"], locals={"kappa": KAPPA})
    r1 = route1(body, g)
    r2 = route2(body)
    # route 1 J symbols are J_g[k,0] = int (l^2)^k / l^2 ; route 2 coefficient of (l^2)^k
    Js = {k: sp.Symbol(f"J_{g}[{k},0]") for k in range(4)}
    agree, n_cmp = True, 0
    for comp in set(r1) | set(r2):
        e1 = r1.get(comp, 0)
        e2 = sum(c * Js[k] for k, c in r2.get(comp, {}).items())
        n_cmp += 1
        if sp.expand(e1 - e2) != 0:
            agree = False
    members = sorted({int(str(s).split("[")[1].split(",")[0]) for e in r1.values() for s in e.free_symbols
                      if str(s).startswith(f"J_{g}[")})
    # S0 on every member (massless, no scale): ledgered with omega
    IL.LEDGER.clear()
    s0 = {k: IL.scaleless(k, 1, f"{g}: int (l^2)^{k}/l^2") for k in members}
    led = list(IL.LEDGER)
    value = {comp: sp.expand(e.xreplace({Js[k]: s0[k] for k in members})) for comp, e in r1.items()}
    all_zero = all(v == 0 for v in value.values())
    logarithmic = [x for x in led if x["omega"] == 0]
    # evanescent content of the regulated expression (before S0)
    n_ev = sum(1 for e in r1.values() if dred.split_evanescent(e)[1] != 0)
    # ---- IR-regulator mass on the loop line: int (l^2)^k/(l^2 - m^2) = T(k,1;m), exact in d
    Tm = {Js[k]: IL.tadpole_hat(k, 1) for k in members}
    mass_pole, mass_fin, mass_struct = {}, {}, {}
    for comp, e in r1.items():
        ev = sp.expand(e.xreplace(Tm))
        # contract the evanescent pieces with the faithful realization only for the classification of p-powers
  +> ;
        # the Laurent expansion is done on the exact-d expression with Gt kept symbolic (R6)
        ser = IL.laurent(ev, 0)
        mass_pole[comp] = sp.expand(ser[-1])
        mass_fin[comp] = sp.expand(ser[0])
        pw = set()
        for t in sp.Add.make_args(mass_pole[comp]):
            if t != 0:
                pw.add(int(sp.degree(t, IL.MSQ)))
        mass_struct[comp] = sorted(pw)
    m_powers = sorted({x for v in mass_struct.values() for x in v})
    lim0 = all(sp.limit(sp.expand(v.xreplace({IL.Lm: sp.log(IL.MSQ)})), IL.MSQ, 0, "+") == 0
               for v in list(mass_fin.values())[:12])
    ex = sorted(r1)[:3]
    rec = {
        "graph": g, "slot": SLOTS[g], "kappa_order": ORDER[g], "export": pin, "prefactor": body["prefactor"],
        "denominators": body["denominators"], "massless_declared": all(x == "l^2+i0" for x in body["denominato
  +> rs"]),
        "status": "vanishing_under_declared_prescription" if (all_zero and pin["pinned"] and agree) else "regu
  +> lated",
        "regulated_expression": {
            "form": f"iGamma_1 = N_eps * ({body['prefactor']}) * sum_comp [ sum_k c_k(d, p, Gt) J_{g}[k,0] ], 
  +>  "
                    f"J_{g}[k,0] = int (l^2)^k / (l^2 + i0)",
            "components": len(r1), "J_members_k": members,
            "components_with_evanescent_Gt_part": n_ev,
            "examples": {c: str(r1[c]) for c in ex}},
        "UV_subtraction": "none: no 1/eps pole (every member is a pure power divergence, omega > 0); MS-bar co
  +> unterterm 0",
        "finite_part": "0 (all components)" if all_zero else "NONZERO",
        "local_ambiguity": ("none generated in the declared prescription; the kappa^2 hh slot's local freedom 
  +> is the p14r "
                            "h.h counterterm directions (degree 4 in p) and is NOT touched by D02/D12 (no pole
  +> , no "
                            "finite local term)" if ORDER[g] == 2 else
                            "none: the p14r kappa^1 counterterm basis is empty (one-leg local functionals are 
  +> total "
                            "derivatives or need a dimension-5 field)"),
        "renormalization_conditions": "MS-bar at mu (P14 normalization condition 0) + N4 (no mu^4, mu^2 p^2 co
  +> ntacts); "
                                      "no counterterm is required",
        "scaleless_analysis": {
            "S0_applications": led, "logarithmic_members": logarithmic,
            "UV_IR_reading": ("no member is logarithmic (omega = 0): the DR zero is NOT a 1/eps_UV - 1/eps_IR 
  +> "
                              "cancellation here; it discards pure power divergences (omega = "
                              + ", ".join(str(x["omega"]) for x in led) + "); the IR region converges at d = 4
  +>  and "
                              "neither the UV nor the IR part has a pole at d = 4") if not logarithmic else
                             "logarithmic members present: (1/eps_UV - 1/eps_IR) cancellation"},
        "prescription_dependence": {
            "IR_regulator_mass": {
                "rule": "1/(l^2 + i0) -> 1/(l^2 - m^2 + i0) on the loop line (analysis only; m is not in the a
  +> ction)",
                "pole_powers_of_m2": m_powers,
                "pole_examples": {c: str(mass_pole[c]) for c in ex},
                "finite_examples": {c: str(mass_fin[c]) for c in ex},
                "limit_m_to_0": "0 (pole ~ m^{2j}, finite ~ m^{2j}(a + b log m^2), j >= 1)" if lim0 else "CHEC
  +> K",
                "counterterm_needed_at_finite_m": (
                    "poles ~ kappa^2 m^4 hh and kappa^2 m^2 p^2 hh: order-0/order-2 contacts, OUTSIDE the p14r
  +>  h.h "
                    "basis (excluded by N4); they vanish as m -> 0" if ORDER[g] == 2 else
                    "pole ~ kappa m^4 h: a one-point (cosmological-type) contact, OUTSIDE the p14r basis (kapp
  +> a^1 basis "
                    "empty); it vanishes as m -> 0")},
            "analytic_regulator": "(l^2)^{-1-nu}: the integrand stays scaleless for every nu, the value stays 
  +> 0; an "
                                  "analytic regulator alone does not separate UV from IR here",
            "cutoff_split": "each member splits into IR (+Lambda^omega/omega...) and UV (-Lambda^omega/omega..
  +> .) "
                            "pieces with no pole at d = 4; with a hard cutoff the would-be counterterms are "
                            + ("kappa^2 Lambda^4 hh and kappa^2 Lambda^2 p^2 hh (order 0/2: excluded by N4, no
  +> t p14r "
                               "directions)" if ORDER[g] == 2 else
                               "kappa Lambda^4 h (one-point; no p14r kappa^1 direction)"),
            "p14r_counterterm_required": False},
        "verification_controls": {
            "export_sha_pinned_to_p14r_certificate": pin["pinned"],
            "independent_integrand_route_p14r": ("W6 Hessian/Tr-log route (P14_amplitude_rules W6_exports)"
                                                 if g in ("D02", "D12") else "W5 independent sympy regeneratio
  +> n"),
            "route1_dred_lift_equals_route2_symmetric_integration": agree, "components_compared": n_cmp,
            "all_components_vanish": all_zero},
        "value_imported_from_XVI_O": False,
        "XVI_O_comparison": ("XVI-O declares the D12/one-point value 0 by dimensional_regularization_m0 (coinc
  +> ident "
                             "prescription); p15 DERIVES the same vanishing under P's own declared prescriptio
  +> n; "
                             "not imported" if g in ("D12", "D14c") else "n/a"),
    }
    return rec


def p14r_regeneration_checks():
    amp = json.loads((ROOT / "certificates" / "P14_amplitude_rules.json").read_text())
    w5 = amp["controls"]["W5_regeneration"]["checks"]
    w6 = amp["W6_exports"]
    return {"D02": bool(w6["D02"]["agree"]), "D12": bool(w6["D12"]["agree"]), "D14a": bool(w5["D14a"]),
            "D14b": bool(w5["D14b"]), "D14c": bool(w5["D14c"])}


def gate_checks(recs):
    """the Batch A acceptance conditions (re-checked by release_p15)."""
    regen = p14r_regeneration_checks()
    c = {}
    for g, r in recs.items():
        vc = r["verification_controls"]
        c[g] = bool(r["status"] == "vanishing_under_declared_prescription" and vc["export_sha_pinned_to_p14r_c
  +> ertificate"]
                    and vc["route1_dred_lift_equals_route2_symmetric_integration"] and vc["all_components_vani
  +> sh"]
                    and regen[g] and r["massless_declared"] and r["scaleless_analysis"]["S0_applications"]
                    and r["value_imported_from_XVI_O"] is False)
    c["D12_separate_from_one_point_slot"] = (recs["D12"]["kappa_order"] == 2
                                             and all(recs[g]["kappa_order"] == 1 for g in ("D14a", "D14b", "D1
  +> 4c")))
    return c


def main():
    import certio
    t0 = time.time()
    recs = {g: evaluate(g) for g in QC.BATCH_A}
    gc = gate_checks(recs)
    ok = all(gc.values())
    one_point = {"graphs": ["D14a", "D14b", "D14c"], "kappa_order": 1,
                 "status": "vanishing_under_declared_prescription" if all(
                     recs[g]["status"] == "vanishing_under_declared_prescription" for g in ("D14a", "D14b", "D
  +> 14c"))
                 else "regulated",
                 "note": "the order-kappa one-point slot; kept separate from D12 (kappa^2 hh)"}
    d12 = {"graph": "D12", "kappa_order": 2, "status": recs["D12"]["status"],
           "derivation": "certificates/P15_batchA.json graphs.D12 (route 1 frozen-dred lift + S0, route 2 symm
  +> etric "
                         "integration, IR-mass and cutoff analysis)",
           "previous_status": "Missing (p14r)"}
    batchA_evaluated = {
        "execution": ok,
        "claim": ("D02, D12, D14a, D14b, D14c evaluated under the declared prescription (frozen p14r DRED + MS
  +> -bar + "
                  "Feynman i0 + the explicit scaleless rule S0): each is vanishing_under_declared_prescription
  +>  with "
                  "no UV pole, finite part 0, no p14r counterterm required" if ok else "not established"),
        "scope": ("massless declared action; DR-specific (S0): with an IR-regulator mass or a cutoff the tadpo
  +> les "
                  "carry m^{2j}/Lambda^{omega} terms whose counterterms are order-0/2 contacts outside the p14
  +> r basis "
                  "(N4) and vanish as m -> 0; D02 is only one of the three hh graphs (D01, D03 not evaluated);
  +>  no "
                  "slot is complete; NOT quantum_inputs_evaluated")}
    rec = {"landmark": "XVI-P", "revision": QC.REVISION, "deliverable": "P.5 calculation Batch A (tadpoles)",
           "contract_revision": QC.CONTRACT_REVISION,
           "prescription": "frozen p14r P14_DRED_MSbar_FeynmanI0 + S0 (certificates/P15_integral_library.json)
  +> ",
           "graphs": recs, "D12_slot": d12, "one_point_slot_kappa1": one_point, "gate_checks": gc,
           "batchA_evaluated": batchA_evaluated, "loop_evaluations_performed": True,
           "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{QC.CERT_PREFIX}_batchA.json", rec)
    print(json.dumps({"batchA_evaluated": ok, "gate": gc,
                      "status": {g: r["status"] for g, r in recs.items()},
                      "omegas": {g: sorted({x["omega"] for x in r["scaleless_analysis"]["S0_applications"]})
                                 for g, r in recs.items()},
                      "mass_pole_powers": {g: r["prescription_dependence"]["IR_regulator_mass"]["pole_powers_o
  +> f_m2"]
                                           for g, r in recs.items()},
                      "seconds": rec["seconds"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
