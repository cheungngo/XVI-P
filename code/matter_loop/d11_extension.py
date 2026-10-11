#!/usr/bin/env python3
"""o70-sync Gate 3 / Result (3a): actual D11 tensor reference extension.

EG: <T_w^R, f> = lim_{eps↓0} <T, (1-chi(z/eps)) W_w f>
W_w subtracts the normal Taylor jet through order N=floor(sd-4)=4.
Dyadic annulus: on radius lambda=2^{-j}, remainder O(lambda^{N+1}) times
|T|~lambda^{-8} gives integrand ~ lambda^{4-8+5} = lambda^1 (summable).

Concrete noncovariant w, chi. Covariance repair tracked separately.
Optional FP route recorded; agreement FP-EG is origin-supported only after both exist.

candidate_list retained (NOT Constructed spanning set).
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


def multiindex_list(order_max: int, dim: int = 4):
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


def count_multiindices(order_max=4, dim=4) -> dict:
    alphas = multiindex_list(order_max, dim)
    by_order = {}
    for a in alphas:
        o = sum(a)
        by_order[o] = by_order.get(o, 0) + 1
    return {
        "N": order_max,
        "n_multiindices": len(alphas),
        "by_order": {str(k): v for k, v in sorted(by_order.items())},
        "expected_total": 70,
        "pass_count": len(alphas) == 70,
        "NOT_dimension_of_covariant_hh_CT_space": True,
    }


def load_scaling_evidence() -> dict:
    """Fail-safe: missing scaling evidence => Unresolved, never default 8."""
    p = CERT / "O5_D11_tensor.json"
    if not p.exists():
        return {"status": "Unresolved", "sd": None, "reason": "missing O5_D11_tensor.json"}
    t = json.loads(p.read_text())
    sc = t.get("scaling", {})
    if sc.get("status") != "Constructed" or sc.get("scaling_degree_sd") is None:
        return {
            "status": "Unresolved",
            "sd": None,
            "reason": "tensor scaling not Constructed; refuse default sd=8",
            "evidence_present": False,
        }
    return {
        "status": "Constructed",
        "sd": sc["scaling_degree_sd"],
        "evidence_present": True,
        "witness": sc.get("witness"),
        "from": "O5_D11_tensor.json",
    }


def concrete_cutoff() -> dict:
    return {
        "chi": {
            "formula": (
                "chi(u) = eta_smooth(1 - |u|_E^2), |u|_E Euclidean; "
                "eta_smooth(s)=1 for s>=1/2, =0 for s<=0, smooth monotone in between. "
                "Thus chi=1 on a neighborhood of the origin in u-space."
            ),
            "equals_one_near_origin": True,
        },
        "w": {
            "formula": (
                "w(z) = eta_smooth(1 - |z|_E^2 / R^2), R=1 (scheme choice); "
                "w=1 near 0, supp w compact in the Euclidean ball."
            ),
            "R": 1,
            "Lorentz_invariant": False,
            "why_not_Lorentz": (
                "No nonzero compactly supported Lorentz-invariant smooth function "
                "equals 1 near 0 (unbounded Lorentz orbits)."
            ),
        },
        "W_w": {
            "formula": (
                "W_w f(z) = f(z) - w(z) * sum_{|alpha|<=4} "
                "z^alpha/alpha! * partial^alpha f(0)"
            ),
            "N": 4,
            "description": (
                "subtracts the weighted normal Taylor jet of order N=4; "
                "NOT a projection onto polynomials"
            ),
        },
        "reference_extension": (
            "ARCHIVED cutoff: lim_eps <T, (1 - chi(z/eps)) W_w f>. "
            "ACTIVE reference is W_w jet-pullback via Pi_tr (prescription W_w_jet_pullback_via_Pi_tr_o68): <Pi_w^R,f>=<Pi_tr^R, W_w f>. Equivalence NOT claimed."
        ),
        "active_prescription_id": "W_w_jet_pullback_via_Pi_tr_o68",
        "archived_cutoff": True,
        "equivalence_cutoff_vs_Ww": "NOT_claimed",
        "withdrawn_o62_formula": "<T, chi_eps W_w f> with chi_eps=1 near 0",
    }


def dyadic_existence_for_D11(sd: int) -> dict:
    """XIII-C thm:primitive-extension instantiated for this homogeneous tensor.

    On annulus |z|~lambda=2^{-j}: |T| ~ lambda^{-sd}, W_w f = O(lambda^{N+1}),
    volume ~ lambda^4, exponent 4 + (N+1) - sd. For sd=8, N=4: lambda^{4-8+5}=lambda.
    Sum_j 2^{-j} < infty => continuous extension to jet-vanishing tests; assign
    the finite jet to define T_w^R on all tests.
    Ambiguity: sum_{|alpha|<=4} c_alpha partial^alpha delta.
    """
    if sd is None:
        return {
            "status": "Unresolved",
            "reason": "sd missing; refuse to run dyadic with default 8",
        }
    N = sd - 4  # floor(sd-4) for integer sd
    assert N == 4 and sd == 8
    exponent = 4 + (N + 1) - sd  # = 1
    return {
        "status": "Constructed",
        "theorem": "XIII-C thm:primitive-extension (instantiated for D11 tensor)",
        "sd": sd,
        "N": N,
        "annulus_exponent": exponent,
        "annulus_power": f"lambda^{{{4}-{sd}+{N+1}}} = lambda^{exponent}",
        "summable": exponent > 0,
        "argument": (
            f"Homogeneous degree -{sd} components of T (from O5_D11_tensor boundary-value "
            f"basis) are controlled by annular seminorms of homogeneity -{sd} (false pointwise bound |T|<=C|z|_E^{-8} removed as hypothesis). After jet subtraction, "
            f"W_w f = O(|z|^{N+1}). Dyadic annuli give summable bound with exponent "
            f"{exponent} > 0. Limit defining <T_w^R,f> exists for all f. "
            f"Two extensions differ by sum_{{|alpha|<={N}}} c_alpha partial^alpha delta."
        ),
        "balanced_covectors": "(p,-p) for relative-coordinate extension (XIII-C)",
        "NOT_XVI_J_order0": True,
        "w_Lorentz_invariant": False,
        "covariance_repair": {
            "status": "Partial",
            "note": (
                "Noncovariant Euclidean w produces a well-defined extension; "
                "Lorentz-breaking contact pieces sit in the ambiguity and must be "
                "cancelled by finite CT choice (Gate 4) or replaced by a covariant "
                "reference (optional FP route)."
            ),
        },
    }


def optional_finite_part() -> dict:
    return {
        "status": "Partial",
        "definition": "T_FP := FP_{zeta=0} [ mu^{2 zeta} (Q - i0)^zeta T ]",
        "constructed_Laurent": False,
        "note": (
            "Analytic finite-part route is not fully executed (no Laurent expansion "
            "of mu^{2 zeta}(Q-i0)^zeta T computed). Recorded as optional parallel track. "
            "XVI-J Fourier of d(z) is a boundary value, not this Laurent series."
        ),
        "agreement_with_EG": {
            "status": "Unresolved",
            "statement": (
                "If both T_FP and T_w^R exist, T_FP - T_w^R = sum_alpha c_alpha partial^alpha delta"
            ),
            "requires_both_extensions": True,
        },
    }


def candidate_list_hh() -> dict:
    candidates = [
        {"id": "C0_hh", "order": 0, "density": "h_{mu nu} h^{mu nu}"},
        {"id": "C0_trtr", "order": 0, "density": "tau^2"},
        {"id": "C2_hBoxh", "order": 2, "density": "h_{mu nu} Box h^{mu nu}"},
        {"id": "C2_trBox", "order": 2, "density": "tau Box tau"},
        {"id": "C2_dh_dh_IBP", "order": 2, "density": "partial h partial h", "independent_mod_IBP": False},
        {"id": "C2_div_div", "order": 2, "density": "(partial_mu h^{mu nu})(partial^rho h_{rho nu})",
         "o62_status": "OMITTED_from_o62_list"},
        {"id": "C2_div_dtr", "order": 2, "density": "(partial_mu h^{mu nu}) partial_nu tau",
         "o62_status": "OMITTED_from_o62_list"},
        {"id": "C4_Box2", "order": 4, "density": "h Box^2 h"},
        {"id": "C4_trBox2", "order": 4, "density": "tau Box^2 tau"},
        {"id": "C4_mixed_k4", "order": 4, "density": "mixed k^4 structures (candidate)"},
    ]
    return {
        "status": "candidate_list",
        "NOT_Constructed_spanning_set": True,
        "candidates": candidates,
        "n_listed": len(candidates),
        "independence_proven": False,
        "spans_covariant_hh_CT_space": False,
        "Lorentz_covariance_of_w": False,
        "note": "Counting 70 multiindices != dim of covariant hh CT space",
    }


def main():
    scaling = load_scaling_evidence()
    cut = concrete_cutoff()
    sd = scaling.get("sd")
    dyadic = dyadic_existence_for_D11(sd) if scaling["status"] == "Constructed" else {
        "status": "Unresolved",
        "reason": "no scaling evidence",
    }
    fp = optional_finite_part()
    basis = candidate_list_hh()
    mi = count_multiindices(4, 4)

    # Active extension witness: W_w jet-pullback via Pi_tr (NOT archived dyadic track).
    # Dyadic annulus retained as archived corroboration only.
    ww_path = CERT / "O5_D11_Ww_reference.json"
    g_path = CERT / "O5_D11_global_representation.json"
    ww = json.loads(ww_path.read_text()) if ww_path.exists() else {}
    g_rep = json.loads(g_path.read_text()) if g_path.exists() else {}
    ACTIVE_WW = "W_w_jet_pullback_via_Pi_tr_o68"
    ww_ok = (
        ww.get("pass") is True
        and ww.get("status") == "Constructed"
        and ww.get("prescription_id") == ACTIVE_WW
        and (g_rep.get("Pi_tr") or {}).get("pass") is True
        and scaling["status"] == "Constructed"
    )
    # Result 3a: D11 tensor extension existence via ACTIVE Ww reference
    ext_ok = bool(ww_ok)
    gate3_status = "Partial"  # covariance + spanning still open
    d11_ext_status = "Constructed" if ext_ok else "Unresolved"

    cert = {
        "revision": REV,
        "gate": "O.5_matter_loop_Gate3_extension",
        "result_3a_D11_extension": d11_ext_status,
        "status": gate3_status,
        "pass": False,  # Gate 3 full Constructed not claimed (covariance/spanning)
        "pass_means": (
            "D11 tensor extension existence earned via ACTIVE W_w jet-pullback "
            f"({ACTIVE_WW}) after Pi_tr^R exists; archived dyadic/cutoff EG is "
            "corroboration only (equivalence NOT claimed). Gate 3 remains Partial: "
            "w not Lorentz invariant (covariance repair Partial); candidate_list "
            "not a proved spanning set. Contacts/Ward are Result 3b (Gate 4)."
        ),
        "extension_earned_via": "active_Ww_jet_pullback",
        "archived_dyadic_role": "corroboration_only_NOT_earning_track",
        "scaling_evidence": scaling,
        "cutoff": cut,
        "dyadic_existence_D11": dyadic,
        "optional_finite_part": fp,
        "ambiguity": {
            "formula": "sum_{|alpha|<=4} c_alpha partial^alpha delta",
            "order_max": 4 if sd == 8 else None,
            "multiindex_count": mi,
        },
        "finite_tensor_basis": basis,
        "scalar_model_reference_extension": {
            "status": "Constructed_for_scalar_model",
            "note": "Retained; superseded as primary by active W_w jet-pullback (dyadic archived)",
        },
        "withdrawn_from_o62": [
            "chi_eps=1 near origin formula",
            "Constructed_spanning_set",
            "Lorentz-invariant Euclidean-radial w",
            "W as projection onto polynomials",
        ],
        "NOT_sector_solution": True,
        "NOT_Em01": True,
        "active_Ww_prescription_id": "W_w_jet_pullback_via_Pi_tr_o68",
        "active_reference": (
            "ONLY active D11 reference for the contact witness is "
            "W_w_jet_pullback_via_Pi_tr_o68 (Deliverable 3). "
            "Cutoff EG formula archived; equivalence NOT claimed."
        ),
        "Gate4_must_cite_same_Ww_id": True,
    }
    text = json.dumps(cert, indent=2) + "\n"
    (OUT / "O5_Gate3_extension.json").write_text(text)
    (CERT / "O5_Gate3_extension.json").write_text(text)
    print(json.dumps({
        "Gate3": cert["status"],
        "result_3a": d11_ext_status,
        "sd": sd,
        "dyadic": dyadic.get("status"),
        "annulus": dyadic.get("annulus_power"),
        "basis": basis["status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
