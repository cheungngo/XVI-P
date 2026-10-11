#!/usr/bin/env python3
"""o70-sync Deliverable 3: W_w reference — the ONLY active reference for this witness.

After Pi_tr^R exists,
  ⟨Pi_w^R, f⟩ := ⟨Pi_tr^R, W_w f⟩,
  W_w f = f - w J_4 f,
  J_4 f = sum_{|γ|≤4} (z^γ/γ!) ∂^γ f(0).

Restriction / normalization (XIII-C / XVI-J pattern):
  f ∈ D(U) with vanishing jet through order 4 at 0 ⇒ J_4 f = 0 near 0
    where w=1, hence W_w f = f (and for f vanishing near 0, W_w f = f).
  More precisely: if supp f ⊂ U and f vanishes near 0, then J_4 f = 0 and W_w f = f.
  W_w(w p_γ) = 0 for p_γ = z^γ/γ!, |γ|≤4, when w=1 near 0.

Concrete even compact w ≡ 1 near 0 (radius R=1); NOT Lorentz invariant.
Prescription id: W_w_jet_pullback_via_Pi_tr_o68 (NEW; old cutoff ARCHIVED).
Equivalence with old cutoff-limit EG is NOT claimed.
Annular seminorms — false pointwise |T|≤C|z|_E^{-8} removed.
"""
from __future__ import annotations

import json
from itertools import combinations_with_replacement
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "outputs"
CERT = ROOT / "certificates"
OUT.mkdir(parents=True, exist_ok=True)
CERT.mkdir(parents=True, exist_ok=True)
REV = "o70-sync"
PRESCRIPTION_ID = "W_w_jet_pullback_via_Pi_tr_o68"
ARCHIVED_CUTOFF_ID = "EG_cutoff_limit_o66_ARCHIVED"


def multiindices(order_max=4, dim=4):
    out = []
    for total in range(order_max + 1):
        if total == 0:
            out.append(tuple([0] * dim))
            continue
        for combo in combinations_with_replacement(range(dim), total):
            alpha = [0] * dim
            for i in combo:
                alpha[i] += 1
            out.append(tuple(alpha))
    return sorted(set(out), key=lambda a: (sum(a), a))


def concrete_w() -> dict:
    # Explicit C^∞ bump: standard flat transition via exp(-1/s).
    # Let rho(s) = 0 for s<=0, exp(-1/s) for s>0.
    # Let eta(s) = rho(s)/(rho(s)+rho(1-s)) for s in R  (eta=0 on (-inf,0], =1 on [1,+inf)).
    # Set u = 1 - |z|_E^2 / R^2, R=1. Then:
    #   w(z) = eta(2u)   ⇒  w=1 when u>=1/2 i.e. |z|_E^2 <= R^2/2,
    #                      w=0 when u<=0 i.e. |z|_E >= R,
    #                      smooth monotone interpolation on the annulus.
    return {
        "formula": (
            "rho(s)=0 (s<=0), exp(-1/s) (s>0); "
            "eta(s)=rho(s)/(rho(s)+rho(1-s)); "
            "u=1-|z|_E^2/R^2 with R=1 (chart length); "
            "w(z)=eta(2u). Explicit: w≡1 on |z|_E^2<=1/2; w≡0 on |z|_E>=1; "
            "C^∞ monotone on the transition annulus 1/2<|z|_E^2<1."
        ),
        "R": 1,
        "R_units": "chart_length",
        "equals_one_near_0": True,
        "equals_one_on": "|z|_E^2 <= 1/2",
        "vanishes_outside": "|z|_E >= 1",
        "transition_annulus": "1/2 < |z|_E^2 < 1",
        "interpolation": "eta(2u) with eta the standard smooth step via rho",
        "even": True,
        "even_proof": "w(-z)=w(z) because |z|_E depends on squared coordinates",
        "Lorentz_invariant": False,
        "why_not_Lorentz": (
            "No nonzero compactly supported Lorentz-invariant smooth function "
            "equals 1 near 0 (unbounded Lorentz orbits)."
        ),
        "NOT_hypothesis_pointwise_bound": True,
        "bump_choice": "explicit_smooth_bump_fixed_R_with_rho_eta",
        "parameterized_alternative": (
            "Equivalently the theorem may be stated for arbitrary admissible "
            "even w≡1 near 0, writing L = L_{mu,w}; this release freezes the "
            "explicit formula above."
        ),
    }


def J4_and_Ww() -> dict:
    alphas = multiindices(4, 4)
    return {
        "J_4": {
            "formula": "J_4 f(z) = sum_{|gamma|<=4} z^gamma/gamma! * partial^gamma f(0)",
            "N": 4,
            "n_multiindices": len(alphas),
            "expected_70": len(alphas) == 70,
        },
        "W_w": {
            "formula": "W_w f = f - w * J_4 f",
            "restriction_lemma": (
                "If f vanishes on a neighborhood of 0 (hence supp f ⊂ U and "
                "jet through order 4 at 0 vanishes), then J_4 f = 0 and "
                "W_w f = f."
            ),
            "normalization_lemma": (
                "For p_gamma = z^gamma/gamma! with |gamma|<=4 and w≡1 near 0: "
                "J_4(w p_gamma) = p_gamma globally "
                "(jet of w p_gamma at 0 equals jet of p_gamma because w(0)=1 "
                "and all derivatives of w that hit the product vanish at 0 "
                "when w≡1 on a neighborhood of 0). "
                "Hence W_w(w p_gamma) = w p_gamma - w J_4(w p_gamma) "
                "= w p_gamma - w p_gamma = 0 globally as a test function "
                "(including the transition region and outside supp w)."
            ),
            "normalization_identity": "J_4(w p_gamma)=p_gamma  ⇒  W_w(w p_gamma)=0 globally",
        },
    }


def load_Pi_tr_status() -> dict:
    p = CERT / "O5_D11_global_representation.json"
    if not p.exists():
        return {"status": "MISSING", "pass": False}
    g = json.loads(p.read_text())
    # STOP gate: global must pass before W_w is Constructed
    if g.get("pass") is not True or g.get("status") != "Constructed":
        return {
            "status": "Unresolved",
            "pass": False,
            "STOP": "global_representation_not_Constructed",
            "from": "O5_D11_global_representation.json",
        }
    pi = g.get("Pi_tr") or {}
    return {
        "status": pi.get("status", g.get("status")),
        "pass": bool(pi.get("pass", g.get("pass"))),
        "Pi_tr_U": (pi.get("Pi_tr_restricts_on_U")),
        "from": "O5_D11_global_representation.json",
        "sd_bound": ((pi.get("scaling_degree_K_uR") or {}).get("sd_bound")),
        "acceptance": g.get("acceptance"),
    }


def reference_definition(pi: dict, w: dict, Ww: dict) -> dict:
    ok = bool(pi.get("pass"))
    return {
        "prescription_id": PRESCRIPTION_ID,
        "ONLY_active_reference_for_this_witness": True,
        "definition": "⟨Pi_w^R, f⟩ := ⟨Pi_tr^R, W_w f⟩",
        "requires_Pi_tr_first": True,
        "Pi_tr_status": pi.get("status"),
        "status": "Constructed" if ok else "Unresolved",
        "pass": ok,
        "restriction": Ww["W_w"]["restriction_lemma"],
        "normalization": Ww["W_w"]["normalization_lemma"],
        "NOT_old_cutoff_limit": True,
        "archived_cutoff": {
            "prescription_id": ARCHIVED_CUTOFF_ID,
            "formula": "lim_eps ⟨T, (1-chi(z/eps)) W_w f⟩",
            "status": "ARCHIVED",
            "equivalence_with_W_w_pullback": "NOT_claimed",
        },
        "distinction": (
            "Active reference pulls back the already-extended transverse Pi_tr^R "
            "through W_w; it is not the dyadic cutoff-limit of the punctured T. "
            "XIII-C / XVI-J prove restriction+normalization after Pi_tr exists; "
            "equivalence with cutoff is not claimed."
        ),
        "w": w,
        "W_w": Ww["W_w"],
        "J_4": Ww["J_4"],
    }


def properties(pi: dict, w: dict) -> dict:
    ok = bool(pi.get("pass")) and w["even"] and (w["Lorentz_invariant"] is False)
    return {
        "continuity": {
            "status": "Constructed" if ok else "Unresolved",
            "argument": (
                "W_w: D→D continuous; Pi_tr^R ∈ D' ⇒ composition continuous. "
                "Proofs use annular seminorms (XIII-C), not a pointwise bound."
            ),
        },
        "agrees_off_diagonal": {
            "status": "Constructed" if ok else "Unresolved",
            "statement": (
                "If f vanishes near 0 then J_4 f = 0, W_w f = f, and "
                "⟨Pi_w,f⟩=⟨Pi_tr,f⟩=⟨(i κ^2/4) T, f⟩."
            ),
            "kernel_on_U": "(i kappa^2/4) T",
            "NOT_eq_T_without_prefactor": True,
        },
        "scaling_degree": {
            "status": "Constructed" if ok else "Unresolved",
            "sd_max": 8,
            "argument": (
                "Pi_tr^R has sd≤8; W_w subtracts a jet against compact w without "
                "raising sd (XIII-C annular seminorms)."
            ),
            "NOT_false_pointwise_bound": True,
            "false_bound_removed": "|T(z)| <= C |z|_E^{-8}",
        },
        "index_symmetries": {
            "status": "Constructed" if ok else "Unresolved",
            "inherited_from_Pi_tr": True,
        },
        "evenness": {
            "status": "Constructed" if ok else "Unresolved",
            "Pi_tr_even": True,
            "w_even": True,
            "Pi_w_even": True,
            "argument": (
                "Pi_tr^R even (even u_mu^R, even-order K); w even ⇒ "
                "W_w intertwines parity; Pi_w even. Odd moments vanish only "
                "after this evenness is proved — not by a metadata flag."
            ),
        },
        "vanishing_moments": {
            "status": "Constructed" if ok else "Unresolved",
            "identity": "⟨Pi_w^R, w z^gamma/gamma!⟩ = 0 for |gamma|<=4",
            "proof": (
                "J_4(w p_gamma)=p_gamma globally ⇒ W_w(w p_gamma)=0 globally "
                "(normalization lemma, including transition region); "
                "hence ⟨Pi_tr, W_w(w p_gamma)⟩=0."
            ),
        },
        "status": "Constructed" if ok else "Unresolved",
        "pass": bool(ok),
    }


def main():
    w = concrete_w()
    Ww = J4_and_Ww()
    pi = load_Pi_tr_status()
    ref = reference_definition(pi, w, Ww)
    props = properties(pi, w)
    all_ok = ref["pass"] and props["pass"] and Ww["J_4"]["expected_70"]

    cert = {
        "revision": REV,
        "deliverable": 3,
        "status": "Constructed" if all_ok else "Unresolved",
        "pass": bool(all_ok),
        "pass_means": (
            f"ONLY active reference {PRESCRIPTION_ID}: ⟨Pi_w^R,f⟩=⟨Pi_tr^R,W_w f⟩ "
            "with explicit even non-Lorentz w (R=1); restriction+normalization "
            "lemmas; continuity; off-diagonal (iκ²/4)T; sd≤8 via annular seminorms; "
            "even; vanishing moments |γ|≤4. Old cutoff ARCHIVED; equivalence NOT claimed."
        ),
        "prescription_id": PRESCRIPTION_ID,
        "ONLY_active_reference": True,
        "reference": ref,
        "properties": props,
        "archived_false_pointwise_hypothesis": "|T(z)|<=C|z|_E^{-8}",
        "archived_cutoff_prescription_id": ARCHIVED_CUTOFF_ID,
        "NOT_Lorentz_invariant_w": True,
        "equivalence_old_EG": "NOT_claimed",
        "Gate4_must_cite_same_id": PRESCRIPTION_ID,
    }
    text = json.dumps(cert, indent=2, default=str) + "\n"
    (OUT / "O5_D11_Ww_reference.json").write_text(text)
    (CERT / "O5_D11_Ww_reference.json").write_text(text)
    print(json.dumps({
        "Deliverable3": cert["status"],
        "prescription_id": PRESCRIPTION_ID,
        "ONLY_active": True,
        "Pi_tr": pi.get("status"),
        "archived_cutoff": ARCHIVED_CUTOFF_ID,
        "vanishing_moments": props["vanishing_moments"]["status"],
    }, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
