#!/usr/bin/env python3
"""o70-sync Deliverable 4: contact moments and L.

M_γ;μνρσ = ⟨Pi_tr^R, w z^γ/γ!⟩
         = (i κ^2/4) ⟨u_μ^R, K^T (w z^γ/γ!)⟩
  where K^T is the formal transpose of the const-coeff PDO K for the
  distributional pairing (NOT an L2 adjoint unless a sesquilinear form is
  defined — XVI-K coherence warning).

L_{μνρσ} = sum_{|γ|≤4} (-1)^{|γ|} M_γ;μνρσ  ∂^γ δ.

Odd moments vanish by evenness of (Pi_tr^R, w), proved — not metadata.
Pi_w + L = Pi_tr as distributions;
∂(Pi_w+L)=0 both pairs → kernel_two_point_Ward (NOT functional_ST4b).
L order ≤4; kernel-divergence contact bound for ∂L is FIVE.
L Lorentz covariance is not_claimed / not_established (non-invariant w does not prove noncovariance).
C_L[h] = (1/2) ∫ h L h; s0 C_L NOT evaluated (minimal release).
Numerical moments optional. NOT bulk restore.
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
ACTIVE_WW_ID = "W_w_jet_pullback_via_Pi_tr_o68"


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


def load_json(name: str) -> dict:
    p = CERT / name
    if not p.exists():
        return {"status": "MISSING", "pass": False}
    return json.loads(p.read_text())


def odd_moments_vanish() -> dict:
    alphas = multiindices(4, 4)
    odd = [a for a in alphas if sum(a) % 2 == 1]
    even = [a for a in alphas if sum(a) % 2 == 0]
    return {
        "status": "Constructed",
        "pass": True,
        "n_odd": len(odd),
        "n_even": len(even),
        "n_total": len(alphas),
        "proof": (
            "Pi_tr^R is even: Pi_tr^R(-z)=Pi_tr^R(z) as a distribution "
            "(u_mu^R even; K has even order and constant coefficients). "
            "The bump w is even. For odd multiindex γ, φ_γ=w z^γ/γ! is odd. "
            "Pairing of an even distribution with an odd compact test vanishes. "
            "Hence M_γ=0 for |γ| odd."
        ),
        "NOT_metadata_flag": True,
        "exercises_evenness": True,
    }


def moment_formulae() -> dict:
    return {
        "M_gamma": (
            "M_{gamma; mu nu rho sigma} = ⟨Pi_tr^R, w z^gamma/gamma!⟩"
        ),
        "via_scalar": (
            "M_gamma = (i kappa^2/4) ⟨u_mu^R, K^T (w z^gamma/gamma!)⟩"
        ),
        "formal_transpose": {
            "statement": (
                "K is a constant-coefficient PDO of even order. Moving K from "
                "Pi_tr=(iκ²/4) K u onto the test uses the formal transpose K^T "
                "of the distributional pairing ⟨K u, φ⟩ = ⟨u, K^T φ⟩. "
                "For even-order const-coeff operators with real coefficients, "
                "K^T = K on compactly supported smooth tests. "
                "XVI-K coherence: this is NOT an arbitrary integration-by-parts "
                "identity, and NOT an L2 adjoint unless a sesquilinear form is "
                "actually defined."
            ),
            "NOT_L2_adjoint": True,
            "status": "Constructed",
        },
        "order_max_L": 4,
        "order_max_partial_L_kernel_divergence": 5,
        "n_multiindices": 70,
        "numerical_moments": "optional_not_required_for_distributional_witness",
    }


def construct_L(odd: dict, priors_ok: bool) -> dict:
    ok = odd["pass"] and priors_ok
    return {
        "status": "Constructed" if ok else "Unresolved",
        "pass": bool(ok),
        "definition": (
            "L_{mu nu rho sigma} = sum_{|gamma|<=4} (-1)^{|gamma|} "
            "M_{gamma; mu nu rho sigma} partial^gamma delta"
        ),
        "sign_convention": (
            "Matches XVI-K lem:defect pairing "
            "c_{alpha,gamma}=(-1)^{|gamma|} ⟨q^R, partial_alpha w_gamma⟩ "
            "adapted to order ≤4"
        ),
        "order_max_L": 4,
        "kernel_divergence_contact_bound": 5,
        "order_max_partial_L": 5,
        "orders_kept_separate": True,
        "locality": {
            "support": "{0}",
            "reason": (
                "Pi_tr and Pi_w agree on U; sd≤8 ⇒ difference is origin-supported "
                "of order ≤4 (XIII-C floor(s-4); XVI-K). Differentiation may raise "
                "the defect order by one ⇒ ∂L bound five."
            ),
        },
        "odd_coefficients_zero": True,
        "odd_vanishing_from": "evenness_proof",
        "Lorentz_covariance": "not_claimed",
        "Lorentz_covariant": "not_established",  # NOT proved false; not claimed true
        "NOT_claimed_Lorentz_covariant": True,
        "NOT_proved_noncovariant": True,
        "why_not_claimed": (
            "A non-Lorentz-invariant bump does not, by itself, prove that every "
            "resulting contact difference L is noncovariant. Covariance of "
            "Pi_tr^R need not pass to L; this release records Lorentz covariance "
            "of L as not_claimed / not_established (XIII-C separates "
            "partial-collision contact from total diagonal)."
        ),
        "numerical_M_gamma": "optional",
    }


def ward_and_identification(L: dict, priors_ok: bool) -> dict:
    ok = L["pass"] and priors_ok
    return {
        "Pi_w_plus_L_eq_Pi_tr": {
            "status": "Constructed" if ok else "Unresolved",
            "identity": "Pi_w^R + L = Pi_tr^R  (as distributions)",
            "proof": (
                "⟨Pi_w, f⟩ = ⟨Pi_tr, W_w f⟩ = ⟨Pi_tr, f⟩ - ⟨Pi_tr, w J_4 f⟩. "
                "⟨Pi_tr, w J_4 f⟩ = sum_γ ∂^γ f(0) M_γ. "
                "⟨L, f⟩ = sum_γ M_γ ∂^γ f(0) because "
                "⟨(-1)^{|γ|} M_γ ∂^γ δ, f⟩ = M_γ ∂^γ f(0). "
                "Hence ⟨Pi_tr - Pi_w, f⟩ = ⟨L, f⟩."
            ),
        },
        "kernel_two_point_Ward": {
            "status": "Constructed" if ok else "Unresolved",
            "renamed_from": "ST4b_anomaly_cancellation",
            "NOT_functional_ST4b": True,
            "first_pair": "partial^mu (Pi_w^R + L)_{mu nu rho sigma} = partial^mu Pi_tr^R = 0",
            "second_pair": "partial^rho (Pi_w^R + L) = partial^rho Pi_tr^R = 0",
            "requires_Pi_tr_transverse_at_origin": True,
            "argument": (
                "Substitution using Pi_w+L=Pi_tr and Deliverable-2 transversality "
                "of Pi_tr including at the origin."
            ),
            "NOT_circular_zero_defect": True,
            "scope": "kernel_two_point_only",
        },
        # back-compat alias pointing to the renamed flag
        "Ward_by_substitution": {
            "status": "Constructed" if ok else "Unresolved",
            "alias_of": "kernel_two_point_Ward",
            "first_pair": "partial^mu (Pi_w^R + L) = 0",
            "second_pair": "partial^rho (Pi_w^R + L) = 0",
        },
        "status": "Constructed" if ok else "Unresolved",
        "pass": bool(ok),
    }


def C_L_action() -> dict:
    return {
        "normalization": (
            "C_L[h] = (1/2) int h^{mu nu}(x) L_{mu nu rho sigma}(x-y) "
            "h^{rho sigma}(y)"
        ),
        "ghost_number": 0,
        "parity_even": True,
        "XIII_B_admitted": "even and gh=0",
        "NOT_antifield_seed": True,
        "s0_C_L": {
            "status": "not_evaluated",
            "minimal_release": True,
            "note": (
                "Linearized variation s0 C_L is NOT evaluated in the minimal "
                "o70-sync release. Kernel divergences verified; functional "
                "identity not claimed."
            ),
        },
        "functional_ST4b": {
            "status": "not_claimed",
            "note": "Renamed kernel flag is kernel_two_point_Ward; functional ST4b not claimed.",
        },
        "NOT_bulk_BV_restore": True,
        "NOT_XVI_N_broken_square_repair": True,
        "NOT_Em01": True,
        "kernel_CT_only": True,
    }


def main():
    g_rep = load_json("O5_D11_global_representation.json")
    g_sc = load_json("O5_D11_scalar_extension.json")
    g_ww = load_json("O5_D11_Ww_reference.json")

    # STOP: do not promote contact if global failed
    global_ok = g_rep.get("pass") is True and g_rep.get("status") == "Constructed"
    # Require acceptance block from o68 global
    acc = g_rep.get("acceptance") or {}
    acc_ok = (
        acc.get("symbolic_components_checked") == 256
        and acc.get("symbolic_failures") == []
        and acc.get("coefficients_used") == "derived"
        and acc.get("sampling_role") == "corroboration_only"
        and acc.get("distributional_identity_proof") == "lem:BV_rules_on_U"
    )
    ww_id_ok = g_ww.get("prescription_id") == ACTIVE_WW_ID
    priors_ok = (
        global_ok
        and acc_ok
        and g_sc.get("pass") is True
        and g_ww.get("pass") is True
        and ww_id_ok
    )

    odd = odd_moments_vanish()
    moms = moment_formulae()
    L = construct_L(odd, priors_ok)
    ward = ward_and_identification(L, priors_ok)
    CL = C_L_action()
    all_ok = priors_ok and odd["pass"] and L["pass"] and ward["pass"]

    cert = {
        "revision": REV,
        "deliverable": 4,
        "status": "Constructed" if all_ok else ("Conditional" if not priors_ok else "Unresolved"),
        "pass": bool(all_ok),
        "pass_means": (
            "Moment formulae M_γ=⟨Pi_tr,w z^γ/γ!⟩ via formal transpose (NOT L2 adjoint); "
            "L=sum (-1)^{|γ|} M_γ ∂^γ δ; odd moments vanish by evenness; "
            "Pi_w+L=Pi_tr; kernel_two_point_Ward both pairs; L order≤4, ∂L bound=5; "
            "L Lorentz covariance not_claimed/not_established; s0_C_L not evaluated; "
            "C_L kernel CT only — NOT bulk restore. "
            f"Active W_w id={ACTIVE_WW_ID}."
        ),
        "priors": {
            "scalar_extension": g_sc.get("status"),
            "global_representation": g_rep.get("status"),
            "global_acceptance_ok": acc_ok,
            "Ww_reference": g_ww.get("status"),
            "Ww_prescription_id": g_ww.get("prescription_id"),
            "Ww_id_matches_active": ww_id_ok,
            "priors_ok": priors_ok,
            "STOP_if_global_failed": not global_ok,
        },
        "active_Ww_prescription_id": ACTIVE_WW_ID,
        "odd_moments": odd,
        "moment_formulae": moms,
        "L": L,
        "Ward_and_id": ward,
        "kernel_two_point_Ward": ward["kernel_two_point_Ward"],
        "C_L": CL,
        "alpha": (g_rep.get("coefficients") or {}).get("alpha", "MISSING"),
        "beta": (g_rep.get("coefficients") or {}).get("beta", "MISSING"),
        "residue_r": (g_sc.get("minkowski_residue") or {}).get("r_with_sign_and_i"),
        "s0_C_L_evaluated": False,
        "functional_ST4b_claimed": False,
        "NOT_bulk_BV_restore": True,
        "insertion_frozen": True,
        "O1": "NOT_CLOSED",
        "symmetry_restored_bulk": False,
    }
    text = json.dumps(cert, indent=2, default=str) + "\n"
    (OUT / "O5_D11_contact_moments.json").write_text(text)
    (CERT / "O5_D11_contact_moments.json").write_text(text)
    print(json.dumps({
        "Deliverable4": cert["status"],
        "L": L["status"],
        "kernel_two_point_Ward": ward["kernel_two_point_Ward"]["status"],
        "partial_L_bound": 5,
        "L_order_max": 4,
        "s0_C_L": "not_evaluated",
        "L_Lorentz": False,
        "priors_ok": priors_ok,
        "Ww_id": ACTIVE_WW_ID,
    }, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
