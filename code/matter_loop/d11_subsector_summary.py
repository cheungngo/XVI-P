#!/usr/bin/env python3
"""o70-sync: authoritative D11 summary from Gates 0-4 + calculation results.

Fail-safe:
  missing scaling evidence -> Unresolved (never default 8)
  missing D12 evidence -> Missing (never default 0)
  require revision/convention IDs
  separate build_completed / checks_passed / scientific_verdict_earned
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
LED.mkdir(parents=True, exist_ok=True)

REV = "o70-sync"
FORBIDDEN_STATUS = "Constructed_subsector_under_prescription"


def load(name: str) -> dict:
    p = CERT / name
    if not p.exists():
        return {"status": "MISSING", "pass": False, "revision": None}
    return json.loads(p.read_text())


def main():
    build_completed = True
    g0 = load("O5_matter_convention_sheet.json")
    g1 = load("O5_Gate1_mixed_scalar_noether.json")
    g2 = load("O5_Gate2_normalized_D11.json")
    g3 = load("O5_Gate3_extension.json")
    g4 = load("O5_Gate4_Ward_D12_onepoint.json")
    tensor = load("O5_D11_tensor.json")
    divs = load("O5_D11_contracted_divergences.json")
    verdict = load("O5_matter_loop_subsector_verdict.json")
    route1 = load("O5_Route1_transverse.json")
    sc_ext = load("O5_D11_scalar_extension.json")
    g_rep = load("O5_D11_global_representation.json")
    ww_ref = load("O5_D11_Ww_reference.json")
    c_mom = load("O5_D11_contact_moments.json")

    # Fail-safe scaling
    sc = tensor.get("scaling", {})
    if sc.get("status") == "Constructed" and sc.get("scaling_degree_sd") is not None:
        sd_status = "Constructed"
        sd_val = sc["scaling_degree_sd"]
    else:
        sd_status = "Unresolved"
        sd_val = None  # NEVER default 8

    # Fail-safe D12
    d12 = g4.get("D12")
    if not isinstance(d12, dict) or "value" not in d12:
        d12_status = "Missing"
        d12_value = None
    else:
        d12_status = d12.get("status", "Missing")
        d12_value = d12.get("value")

    one = g4.get("one_point")
    if not isinstance(one, dict) or "value" not in one:
        one_status = "Missing"
        one_value = None
    else:
        one_status = one.get("status", "Missing")
        one_value = one.get("value")

    gates = {
        "Gate0": g0.get("status"),
        "Gate1": g1.get("status"),
        "Gate2_prefactor": g2.get("status_prefactor", g2.get("status")),
        "Gate2_tensor": tensor.get("status"),
        "Gate3": g3.get("status"),
        "Gate3_result_3a": g3.get("result_3a_D11_extension"),
        "Gate4": g4.get("status"),
        "Route1": route1.get("status"),
    }
    three = {
        "1_tensor": tensor.get("status"),
        "2_divergences": divs.get("status"),
        "3_extension_contacts": (g4.get("result_3") or {}).get("combined", "Partial"),
    }
    revisions = {
        "Gate0": g0.get("revision"),
        "Gate1": g1.get("revision"),
        "Gate2": g2.get("revision"),
        "Gate3": g3.get("revision"),
        "Gate4": g4.get("revision"),
        "tensor": tensor.get("revision"),
        "divs": divs.get("revision"),
        "scalar_ext": sc_ext.get("revision"),
        "global_rep": g_rep.get("revision"),
        "Ww": ww_ref.get("revision"),
        "contact": c_mom.get("revision"),
        "route1": route1.get("revision"),
        "verdict": verdict.get("revision"),
    }
    # rev_ok: every tracked revision equals this release (NOT merely non-null)
    rev_ok = all(v == REV for v in revisions.values())

    four_deliverables_ok = all([
        sc_ext.get("pass") is True and sc_ext.get("status") == "Constructed",
        g_rep.get("pass") is True and g_rep.get("status") == "Constructed",
        ww_ref.get("pass") is True and ww_ref.get("status") == "Constructed",
        c_mom.get("pass") is True and c_mom.get("status") == "Constructed",
    ])

    # Single final_earned predicate drives status + earned + scientific_verdict_earned
    prerequisite_checks = bool(
        gates["Gate0"] == "Constructed"
        and bool(g1.get("pass"))
        and bool(g2.get("route_agreement", {}).get("pass"))
        and tensor.get("status") == "Constructed"
        and divs.get("status") == "Constructed"
        and route1.get("pass") is True
        and g4.get("pass") is True
        and four_deliverables_ok
    )
    revision_checks = bool(rev_ok)
    prescription_checks = bool(
        (ww_ref.get("prescription_id") == "W_w_jet_pullback_via_Pi_tr_o68")
        and (c_mom.get("active_Ww_prescription_id") == "W_w_jet_pullback_via_Pi_tr_o68")
        and (g4.get("active_Ww_prescription_id") == "W_w_jet_pullback_via_Pi_tr_o68")
        and bool((g4.get("prescription_match_derived") or {}).get("match"))
    )
    gate_checks = bool(g4.get("pass") is True and (g3.get("result_3a_D11_extension") == "Constructed"))
    verdict_checks = bool(verdict.get("earned") is True)

    final_earned = bool(
        prerequisite_checks
        and revision_checks
        and prescription_checks
        and gate_checks
        and verdict_checks
    )
    checks_passed = bool(final_earned)  # same predicate — no stale promotion
    scientific_verdict_earned = bool(final_earned)
    earned = bool(final_earned)

    if final_earned:
        status = FORBIDDEN_STATUS
    else:
        status = "summary_from_gates_NOT_subsector_Constructed"
        if verdict.get("subsector_verdict") == FORBIDDEN_STATUS and not four_deliverables_ok:
            raise SystemExit(
                "FAIL: FORBIDDEN status without all four deliverables Constructed"
            )

    cert = {
        "revision": REV,
        "gate": "O.5_D11_matter_loop_subsector",
        "status": status,
        "pass": False,
        "build_completed": build_completed,
        "checks_passed": checks_passed,
        "scientific_verdict_earned": scientific_verdict_earned,
        "final_earned": final_earned,
        "promotion_predicate": {
            "prerequisite_checks": prerequisite_checks,
            "revision_checks": revision_checks,
            "prescription_checks": prescription_checks,
            "gate_checks": gate_checks,
            "verdict_checks": verdict_checks,
        },
        "pass_means": (
            "Authoritative summary from Gates + calculation results 1-3. "
            f"Subsector earned={earned}. Scaling fail-safe: {sd_status} (sd={sd_val}). "
            f"D12 fail-safe: {d12_status} (value={d12_value})."
        ),
        "diagram_id": "D11_hh_scalar_loop",
        "NOT_completed_bulk_quantum_sector": True,
        "symmetry_restored": False,
        "symmetry_restored_subsector": bool(verdict.get("symmetry_restored_subsector")),
        "authoritative_source": "Gates + d11_tensor/divergences via d11_subsector_summary.py",
        "withdrawn_o62_builder": "withdrawn/o62-matter/d11_scalar_loop_hh.py",
        "gates": gates,
        "three_results": three,
        "revisions": revisions,
        "convention_ids_ok": rev_ok,
        "subsector_verdict": verdict.get("subsector_verdict", "WITHDRAWN"),
        "earned": earned,
        "prefactor": g2.get("prefactor", "Unresolved"),
        "D_F": "i/(k^2+i0)",
        "scaling": {
            "status": sd_status,
            "scaling_degree_sd": sd_val,
            "NOT_default_8": True,
            "from": "O5_D11_tensor.json",
        },
        "tensor_kernel": {
            "status": tensor.get("status"),
            "Pi_prefactor": g2.get("prefactor"),
            "T_0000_witness": (tensor.get("spacelike_witness") or {}).get("T_0000"),
            "NOT_XVI_M_selected_graph": True,
        },
        "divergences": {
            "status": divs.get("status"),
            "from": "O5_D11_contracted_divergences.json",
        },
        "extension": {
            "status": g3.get("status"),
            "result_3a": g3.get("result_3a_D11_extension"),
            "from_gate": "O5_Gate3_extension.json",
        },
        "retained_Ward": {
            "status": g4.get("status"),
            "result_3": g4.get("result_3"),
            "from_gate": "O5_Gate4_Ward_D12_onepoint.json",
            "symmetry_restored": False,
        },
        "D12_tadpole_companion": {
            "id": "D12_hh_scalar_tadpole",
            "status": d12_status,
            "value_under_prescription": d12_value,
            "NOT_default_0": True,
        },
        "one_point": {
            "status": one_status,
            "value": one_value,
            "NOT_default_0": True,
        },
        "intermediate_wording": (
            "D11 Wick/determinant normalization established. Actual tensor product, "
            "scaling witness, and off-diagonal Ward verification tracked separately. "
            + (
                "o70-sync: alpha=A^2/60, beta=A^2/18; u_mu^R (r=-i pi^2); W_w; contact L; "
                "kernel Ward by substitution. Bulk O.1 NOT_CLOSED."
                if earned else
                "Prerequisites or promotion checks incomplete (not a Gate2/extension status claim)."
            )
        ),
        "Route1": {
            "status": route1.get("status"),
            "alpha": (route1.get("ansatz_alpha_beta") or {}).get("alpha"),
            "beta": (route1.get("ansatz_alpha_beta") or {}).get("beta"),
            "NOT_defaulted": True,
            "a": (route1.get("ansatz_a_b") or {}).get("a"),
            "b": (route1.get("ansatz_a_b") or {}).get("b"),
            "Pi_tr": (route1.get("Pi_tr") or {}).get("status"),
            "L": (route1.get("counterterm_L") or {}).get("status"),
            "Ward_sub": ((route1.get("counterterm_L") or {}).get("Ward_by_substitution") or {}).get("status"),
        },
        "FORBIDDEN_STATUS_rejected_unless_earned": FORBIDDEN_STATUS,
        "four_deliverables": {
            "1_scalar_extension": sc_ext.get("status"),
            "2_global_representation": g_rep.get("status"),
            "3_Ww_reference": ww_ref.get("status"),
            "4_contact_moments": c_mom.get("status"),
            "all_pass": four_deliverables_ok,
        },
        "acceptance_conjunction_includes_four_deliverables": True,
    }
    text = json.dumps(cert, indent=2) + "\n"
    (OUT / "O5_D11_scalar_loop_hh.json").write_text(text)
    (CERT / "O5_D11_scalar_loop_hh.json").write_text(text)

    frag = {
        "revision": REV,
        "D11_subsector": {
            "status": status,
            "gates": gates,
            "three_results": three,
            "build_completed": build_completed,
            "checks_passed": checks_passed,
            "scientific_verdict_earned": scientific_verdict_earned,
            "symmetry_restored": False,
            "earned": earned,
            "cert": "O5_D11_scalar_loop_hh.json",
        },
        "D12_tadpole": cert["D12_tadpole_companion"],
    }
    (OUT / "D11_subsector_status.json").write_text(json.dumps(frag, indent=2) + "\n")
    (LED / "D11_subsector_status.json").write_text(json.dumps(frag, indent=2) + "\n")
    print(json.dumps({
        "D11_status": status,
        "gates": gates,
        "three": three,
        "sd": sd_val,
        "sd_status": sd_status,
        "D12": d12_value,
        "earned": earned,
        "checks_passed": checks_passed,
        "scientific_verdict_earned": scientific_verdict_earned,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
