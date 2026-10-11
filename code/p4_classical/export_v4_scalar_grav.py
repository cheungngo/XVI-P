#!/usr/bin/env python3
"""Export V4_scalar_grav (hhφφ) for D12 graph use — classical vertex only."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def export() -> dict:
    # Closed forms from O2_scalar_action_authoritative / XI-A Lag_q at m=0
    a2 = (
        "a2^{mu nu}[h] = h^mu_rho h^{rho nu} - (1/2) tau h^{mu nu} + b2[h] eta^{mu nu}, "
        "tau = eta_{rho sigma} h^{rho sigma}, "
        "b2 = (1/8) tau^2 - (1/4) h_{mu nu} h^{mu nu}"
    )
    density = "(kappa^2/2) a2^{mu nu}[h] partial_mu phi partial_nu phi   [m=0]"
    vertex = {
        "id": "V4_scalar_grav",
        "aka": "hhphiphi",
        "order": "kappa^2",
        "kappa_power": 2,
        "fields": "phi phi h h",
        "legs": {"phi": 2, "h": 2},
        "density": density,
        "a2_definition": a2,
        "b2_definition": "(1/8) tau^2 - (1/4) h_{mu nu} h^{mu nu}",
        "derived_from": "Lag_q |_{kappa^2} = (1/2) sqrt(-q) q^{mu nu} partial_mu phi partial_nu phi  => (kappa^2/2) a2 p p",
        "Lag_q": "(1/2) sqrt(-q) ( q^{mu nu} partial_mu phi partial_nu phi )  [m=0]",
        "n_derivatives_total": 2,
        "derivative_placement_default": "on_phi",
        "mass_factor": 0,
        "status": "Constructed",
        "source_certificates": [
            "certificates/O2_scalar_action_authoritative.json",
            "certificates/O2_vertex_catalogue.json",
        ],
        "matches_XI_A_V2": True,
        "usable_by_graph_generator": True,
        "D12_note": (
            "D12 uses this vertex with phi-phi self-contraction (two h external). "
            "Vertex Constructed; D12 amplitude evaluation remains Missing/not evaluated (quantum)."
        ),
        "NOT_D12_evaluated": True,
        "NOT_defaulted_D12_to_zero": True,
    }
    # Export path for graph generator
    export_path = ROOT / "exports" / "V4_scalar_grav.json"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(vertex, indent=2, ensure_ascii=False) + "\n"
    export_path.write_text(blob)
    vertex["export_path"] = str(export_path)
    vertex["export_sha256"] = hashlib.sha256(blob.encode()).hexdigest()
    return vertex


def main() -> int:
    v = export()
    print("V4_scalar_grav", v["status"], v["export_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
