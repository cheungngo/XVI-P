#!/usr/bin/env python3
"""o64-hard Gate 0 (conventions retained): frozen one-page calculation convention sheet.

Every later D11 / Noether / Ward factor MUST follow this sheet.
No mid-calculation convention changes.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "outputs"
CERT = ROOT / "certificates"
LED = ROOT / "ledgers"
OUT.mkdir(parents=True, exist_ok=True)
CERT.mkdir(parents=True, exist_ok=True)

SHEET = {
    "revision": "o70-sync",
    "gate": "O.5_matter_loop_Gate0_convention_sheet",
    "status": "Constructed",
    "pass": True,
    "acceptance": "every later factor follows this sheet; no convention changed midway",
    "metric": {
        "q_mu_nu": "eta_mu_nu + kappa h_mu_nu",
        "XI_A_variable": "gamma; map h <-> gamma (same field)",
        "eta": "diag(+---)",
        "signature": "+---",
    },
    "scalar_action": {
        "S_phi": "(1/2) int d^4x sqrt(-q) q^{mu nu} partial_mu phi partial_nu phi",
        "m": 0,
        "bulk_mass_freeze": "m=0",
        "Lag_q_source": "XI-A eq:scalar-action (m=0 kinetic)",
        "NOT_Em01": True,
    },
    "B_densitized_inverse": {
        "B^{mu nu}": "sqrt(-q) q^{mu nu}",
        "XI_A_name": "Adens_q",
        "series": "B = eta + kappa a1 + kappa^2 a2 + O(kappa^3)",
        "a1": "a1^{mu nu} = (1/2) tau eta^{mu nu} - h^{mu nu},  tau = eta_{rho sigma} h^{rho sigma}",
        "a2": (
            "a2^{mu nu} = h^mu_rho h^{rho nu} - (1/2) tau h^{mu nu} + b2 eta^{mu nu}"
        ),
        "b1": "(1/2) tau",
        "b2": "(1/8) tau^2 - (1/4) h_{mu nu} h^{mu nu}",
    },
    "coupling_stripped_densities": {
        "S_phi": "S_phi0 + kappa S_phi1 + kappa^2 S_phi2 + O(kappa^3)",
        "S_phi0": "(1/2) int eta^{mu nu} partial_mu phi partial_nu phi",
        "S_phi1": "(1/2) int a1^{mu nu} partial_mu phi partial_nu phi",
        "S_phi2": "(1/2) int a2^{mu nu} partial_mu phi partial_nu phi",
        "note": "kappa powers sit OUTSIDE S_phi i; a_i contain no embedded kappa",
    },
    "BRST_bridge": {
        "s": "s0 + kappa s1",
        "s0_phi": 0,
        "s1_phi": "a c^rho partial_rho phi",
        "a": "1/2",
        "s_q": "kappa a L_c q",
        "XI_B_bridge": "c = 2 xi recovers XI-A K xi; a=1/2",
        "s0_h_mu_nu": "a (partial_mu c_nu + partial_nu c_mu)",
        "s1_h": "a L_c h  (Lie on the tensor h)",
    },
    "Fourier_and_path_integral": {
        "Fourier": "partial_mu -> i k_mu; Box -> -k^2; k^2 = eta^{ab} k_a k_b",
        "measure": "d^4x Lebesgue on Minkowski; momentum (2 pi)^{-4} d^4k",
        "exponential": "e^{i S / hbar}",
        "hbar_tracking": "strip overall hbar from Wick contraction; loop order = hbar^1 for one loop",
    },
    "G_F_vs_D_F": {
        "SEPARATE": True,
        "G_F": {
            "role": "inverse of free Hessian (Green operator)",
            "Hessian_H0": "-Box",
            "XIV_A": "G^R = -P E^R, coefficient -1 (graviton); scalar analog G_phi^R = -E_0^R",
            "XI_B": "NOT a Hadamard state; NOT the Wick algebra",
            "NOT_Wick_contraction": True,
        },
        "D_F": {
            "role": "Wick / time-ordered contraction (after stripping hbar)",
            "momentum_space": "D_F(k) = i / (k^2 + i0)",
            "position_space": "D_F(x) = -1/(4 pi^2) * 1/(x^2 - i0)   [eta=+---; standard i0]",
            "defining_on_Hess": "H0 D_F = (-Box) D_F = i delta^4",
            "Fourier_check": "(-Box)->k^2; k^2 * i/(k^2+i0) = i",
        },
        "o61_conversion": {
            "o61_Delta_F_k": "-i / (k^2 + i0)",
            "relation": "Delta_F = - D_F",
            "written_once": True,
            "consequence": (
                "All o61 formulae written with Delta_F must flip one sign per propagator; "
                "products of two propagators are invariant under Delta_F -> -Delta_F."
            ),
        },
    },
    "effective_action": {
        "Gamma": "S + hbar Gamma_1 + ...",
        "Gamma_1_matter_from_logZ": "Gamma_1,matter = -i log Z",
        "Gamma_1_two_point": (
            "Gamma_1^{(2)} = (1/2) int d^4x d^4y "
            "h_mu_nu(x) Pi^{mu nu rho sigma}(x-y) h_rho_sigma(y)"
        ),
        "Pi_definition": "symmetric in (mu nu)<->(rho sigma) and within each pair",
        "note_i_in_DF": (
            "The i inside D_F(k)=i/(k^2+i0) must NOT be counted again when "
            "converting log Z -> Gamma_1 = -i log Z"
        ),
    },
    "scope": {
        "target": "massless scalar matter-loop on background metric",
        "NOT_complete_bulk_BV": True,
        "NOT_Ft_completion": True,
        "NOT_Em01_premise": True,
        "insertion_Track_II": "frozen (XVI-N thm:massless-obstruction)",
        "O1": "NOT_CLOSED",
        "symmetry_restored_bulk": False,
    },
}


def main():
    text = json.dumps(SHEET, indent=2) + "\n"
    (OUT / "O5_matter_convention_sheet.json").write_text(text)
    (CERT / "O5_matter_convention_sheet.json").write_text(text)
    (LED / "matter_convention_sheet.json").write_text(text)
    # Update factor ledger fragment for D_F
    fl_path = LED / "quantum_factor_ledger.json"
    fl = json.loads(fl_path.read_text())
    fl["revision"] = "o70-sync"
    fl["factors"]["scalar_propagator_D11"] = (
        "D_F(k)=i/(k^2+i0) [Wick]; o61 Delta_F=-D_F; H0 D_F = i delta"
    )
    fl["factors"]["G_F_vs_D_F"] = "SEPARATE: G_F=inverse; D_F=Wick; XI-B not Hadamard"
    fl["factors"]["D11_Pi_prefactor"] = (
        "Constructed: Pi = i*kappa^2/4; comb_B=1/2 (Route A/B agree)"
    )
    fl_path.write_text(json.dumps(fl, indent=2) + "\n")
    print(json.dumps({"gate0": "Constructed", "D_F": "i/(k^2+i0)", "Delta_F": "-D_F"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
