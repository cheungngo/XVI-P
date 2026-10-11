#!/usr/bin/env python3
"""Executable tests for o70-sync proof/build consistency + Gates 0-4."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
ML = ROOT / "code" / "matter_loop"
REV = "o70-sync"
FORBIDDEN = "Constructed_subsector_under_prescription"
WW_ID = "W_w_jet_pullback_via_Pi_tr_o68"
XVI_M_HASH = "41aa109935f40ddee3109de62c46329c189b5408007970cc90ed5611dc4739ea"


def run(script: str) -> None:
    r = subprocess.run([PY, str(ML / script)], cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit(f"FAIL running {script} rc={r.returncode}")


def load(name: str) -> dict:
    return json.loads((ROOT / "certificates" / name).read_text())


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def math_mutation_tests() -> None:
    g2 = _load_module("d11_normalized", ML / "d11_normalized.py")
    A = g2.route_A_wick()
    comb = g2.derive_comb_B_from_trace()
    assert comb["pass"] is True
    assert comb["comb_B_sympy"] == sp.Rational(1, 2)
    B = g2.route_B_det(comb)

    A_mut = dict(A)
    A_mut["Pi_prefactor_sympy"] = -sp.symbols("kappa", positive=True) ** 2 / 8
    assert g2.agree_routes(A_mut, B)["pass"] is False

    B_mut = dict(B)
    B_mut["Pi_prefactor_sympy"] = -sp.symbols("kappa", positive=True) ** 2 / 8
    assert g2.agree_routes(A, B_mut)["pass"] is False

    agr = g2.agree_routes(A, B)
    assert agr["pass"] is True

    pi_wrong = sp.I * sp.symbols("kappa", positive=True) ** 2 / 2
    assert g2.agree_routes(A, {**B, "Pi_prefactor_sympy": pi_wrong})["pass"] is False

    ten = _load_module("d11_tensor", ML / "d11_tensor.py")
    wit = ten.spacelike_witness()
    assert wit["pass"] is True
    assert "24" in wit["T_0000_target"]

    div = _load_module("d11_divergences", ML / "d11_divergences.py")
    mut = div.mutations()
    assert mut["pass"] is True
    assert mut["results"]["drop_vertex_trace_detected"] is True
    assert mut["results"]["honest_zero"] is True

    r1 = _load_module("d11_route1", ML / "d11_route1_transverse.py")
    mut = r1.mutation_tests_alpha_beta()
    assert mut["pass"] is True
    assert mut["mutation_alpha_eq_0_detected"] is True
    assert mut["mutation_beta_eq_0_detected"] is True

    sc = _load_module("d11_scalar_extension", ML / "d11_scalar_extension.py")
    g0 = sc.gate0_box_normalization()
    assert g0["pass"] is True
    holo = sc.prove_phi_m1_holomorphy()
    assert holo["pass"] is True
    assert holo["NOT_from_zero_of_4zeta_zeta_minus_1_alone"] is True
    rec = sc.analytic_family_recurrence(g0, holo)
    assert rec["pass"] is True
    assert rec["r_with_sign_and_i"] == "-i * pi**2"
    assert rec["NOT_Wick_Jacobian_alone"] is True
    assert rec["proof_id"] == "lem:analytic_FP_u_mu_R_o70"
    eu = sc.euclidean_independent_sign_check()
    assert eu["pass"] is True
    assert eu["NOT_sole_justification"] is True

    gr = _load_module("d11_global", ML / "d11_global_representation.py")
    derived = gr.derive_alpha_beta()
    assert derived["pass"] is True
    assert derived["coefficients_used"] == "derived"
    assert derived["NOT_hardcoded_default"] is True

    print("math_mutation_tests: PASS")


def deletion_wrong_revision_tests() -> None:
    """Real deletion / wrong-revision / wrong-prescription mutation tests.

    Wrong prescription: mutate Ww id and pass through Gate4 + summary validator.
    Deletion: delete acceptance alone (do NOT also set pass=false/status).
    """
    import copy

    cert_dir = ROOT / "certificates"
    # --- baseline assertions ---
    ww = load("O5_D11_Ww_reference.json")
    assert ww["prescription_id"] == WW_ID
    assert ww["ONLY_active_reference"] is True
    assert ww["equivalence_old_EG"] == "NOT_claimed"

    cm = load("O5_D11_contact_moments.json")
    assert cm["active_Ww_prescription_id"] == WW_ID
    assert cm["s0_C_L_evaluated"] is False
    assert cm["functional_ST4b_claimed"] is False
    assert cm["kernel_two_point_Ward"]["status"] == "Constructed"
    assert cm["L"]["NOT_claimed_Lorentz_covariant"] is True
    assert cm["L"]["kernel_divergence_contact_bound"] == 5
    assert cm["L"].get("NOT_proved_noncovariant") is True
    assert cm["L"].get("Lorentz_covariance") == "not_claimed"
    assert cm["moment_formulae"]["formal_transpose"]["NOT_L2_adjoint"] is True

    gr = load("O5_D11_global_representation.json")
    acc = gr["acceptance"]
    assert acc["symbolic_components_checked"] == 256
    assert acc["symbolic_failures"] == []
    assert acc["coefficients_used"] == "derived"
    assert acc["sampling_role"] == "corroboration_only"
    assert acc["distributional_identity_proof"] == "lem:BV_rules_on_U"
    inv = gr.get("invariant_basis") or {}
    assert inv.get("independent_invariant_basis_verification_claimed") is False
    bv = gr.get("lem_BV_rules_on_U") or {}
    assert bv.get("pass") is True
    assert bv.get("NOT_n2_only") is True
    assert (bv.get("product_existence_vs_equality") or {}).get(
        "wavefront_supplies_existence_only"
    ) is True

    sc = load("O5_D11_scalar_extension.json")
    assert sc["proof_id"] == "lem:analytic_FP_u_mu_R_o70"
    assert sc["NOT_Wick_Jacobian_alone"] is True
    assert sc.get("NOT_from_pref_zero_alone") is True
    assert "normalization_derivation" in sc
    assert (sc.get("phi_m1_holomorphy_proof") or {}).get("pass") is True
    assert (sc.get("phi_m1_holomorphy_proof") or {}).get(
        "NOT_from_zero_of_4zeta_zeta_minus_1_alone"
    ) is True
    hol = (sc.get("analytic_family_recurrence") or {}).get(
        "ordinary_integrability_near_nonzero_null"
    ) or {}
    assert hol.get("requires") == "Re zeta > 1"
    assert hol.get("NOT_Re_zeta_gt_minus_1") is True
    prem = (sc.get("analytic_family_recurrence") or {}).get(
        "phi_m1_plus_zeta_holomorphic_near_0_BEFORE_division"
    ) or {}
    assert prem.get("premise_for_residue_division") is True
    assert prem.get("NOT_from_pref_zero_alone") is True

    g4 = load("O5_Gate4_Ward_D12_onepoint.json")
    assert g4["active_Ww_prescription_id"] == WW_ID
    assert g4["Gate4_cites_same_Ww_id_as_moments"] is True
    assert (g4.get("prescription_match_derived") or {}).get("NOT_hardcoded") is True
    assert g4["contact_defect"]["order_bound"] == 5
    assert g4["contact_defect"].get("NO_unsupported_improvement_5_to_4") is True
    assert g4["contact_defect"].get("ghost_number_defect") is None
    assert "kernel_two_point_Ward" in g4["Ward_and_CT"]
    assert g4["Ward_and_CT"]["kernel_two_point_Ward"]["NOT_functional_ST4b"] is True
    assert g4["Ward_and_CT"]["kernel_two_point_Ward"].get("ghost_number_defect") is None
    assert g4["Ward_and_CT"]["functional_defect_A1_ST4b"]["ghost_number_defect"] == 1

    g3 = load("O5_Gate3_extension.json")
    assert g3.get("extension_earned_via") == "active_Ww_jet_pullback"
    assert "archived" in str(g3.get("archived_dyadic_role", "")).lower() or g3.get(
        "archived_dyadic_role"
    )

    # --- wrong-revision: every active cert must be o70-sync ---
    names = [
        "O5_D11_scalar_extension.json",
        "O5_D11_global_representation.json",
        "O5_D11_Ww_reference.json",
        "O5_D11_contact_moments.json",
        "O5_Route1_transverse.json",
        "O5_Gate3_extension.json",
        "O5_Gate4_Ward_D12_onepoint.json",
        "O5_matter_loop_subsector_verdict.json",
        "O5_D11_scalar_loop_hh.json",
    ]
    for name in names:
        c = load(name)
        assert c.get("revision") == REV, f"{name} revision={c.get('revision')}"

    summary = _load_module("d11_subsector_summary", ML / "d11_subsector_summary.py")
    gate4_mod = _load_module("d11_ward_d12", ML / "d11_ward_d12.py")

    # --- REAL wrong-revision mutation ---
    d11_path = cert_dir / "O5_D11_scalar_extension.json"
    backup = d11_path.read_text()
    try:
        mut = json.loads(backup)
        mut["revision"] = "o00-wrong-revision"
        d11_path.write_text(json.dumps(mut, indent=2) + "\n")
        summary.main()
        d11_sum = load("O5_D11_scalar_loop_hh.json")
        assert d11_sum.get("convention_ids_ok") is False, "wrong revision must fail rev_ok"
        assert d11_sum.get("scientific_verdict_earned") is False
        assert d11_sum.get("final_earned") is False
        assert d11_sum.get("status") != FORBIDDEN
    finally:
        d11_path.write_text(backup)
        summary.main()

    # --- REAL wrong-prescription: mutate Ww id, pass through Gate4 + summary ---
    ww_path = cert_dir / "O5_D11_Ww_reference.json"
    cm_path = cert_dir / "O5_D11_contact_moments.json"
    ww_backup = ww_path.read_text()
    cm_backup = cm_path.read_text()
    g4_backup = (cert_dir / "O5_Gate4_Ward_D12_onepoint.json").read_text()
    verd_backup = (cert_dir / "O5_matter_loop_subsector_verdict.json").read_text()
    try:
        ww_mut = json.loads(ww_backup)
        ww_mut["prescription_id"] = "WRONG_PRESCRIPTION_ID"
        ww_path.write_text(json.dumps(ww_mut, indent=2) + "\n")
        # Pass through Gate4 validator (reads Ww + contact ids)
        gate4_mod.main()
        g4_after = load("O5_Gate4_Ward_D12_onepoint.json")
        match = (g4_after.get("prescription_match_derived") or {}).get("match")
        assert match is False, "Gate4 must detect wrong Ww prescription"
        assert g4_after.get("D11_kernel_counterterm") != "earned" or g4_after.get(
            "Gate4_cites_same_Ww_id_as_moments"
        ) is False
        # Final summary validator must also refuse promotion
        summary.main()
        d11_sum = load("O5_D11_scalar_loop_hh.json")
        assert d11_sum.get("scientific_verdict_earned") is False
        assert d11_sum.get("final_earned") is False
        assert d11_sum.get("status") != FORBIDDEN
    finally:
        ww_path.write_text(ww_backup)
        cm_path.write_text(cm_backup)
        (cert_dir / "O5_Gate4_Ward_D12_onepoint.json").write_text(g4_backup)
        (cert_dir / "O5_matter_loop_subsector_verdict.json").write_text(verd_backup)
        # rebuild dependents from good certs
        run("d11_ward_d12.py")
        run("d11_subsector_summary.py")

    # --- REAL deletion: delete acceptance ALONE (do not flip pass/status) ---
    gr_path = cert_dir / "O5_D11_global_representation.json"
    gr_backup = gr_path.read_text()
    try:
        gr_mut = json.loads(gr_backup)
        assert "acceptance" in gr_mut
        del gr_mut["acceptance"]
        # Leave pass/status unchanged — deletion alone must be detected
        gr_path.write_text(json.dumps(gr_mut, indent=2) + "\n")
        # Gate4 requires acceptance block for global_acc_ok
        gate4_mod.main()
        g4_after = load("O5_Gate4_Ward_D12_onepoint.json")
        assert g4_after.get("D11_kernel_counterterm") != "earned", (
            "Gate4 must not earn when acceptance is deleted alone"
        )
        verd_after = load("O5_matter_loop_subsector_verdict.json")
        assert verd_after.get("earned") is not True
        summary.main()
        d11_sum = load("O5_D11_scalar_loop_hh.json")
        assert d11_sum.get("final_earned") is False
        assert d11_sum.get("scientific_verdict_earned") is False
    finally:
        gr_path.write_text(gr_backup)
        run("d11_global_representation.py")
        run("d11_Ww_reference.py")
        run("d11_contact_moments.py")
        run("d11_extension.py")
        run("d11_route1_transverse.py")
        run("d11_ward_d12.py")
        run("d11_subsector_summary.py")

    print("deletion_wrong_revision_tests: PASS")



def metadata_consistency_tests() -> None:
    g3 = _load_module("d11_extension", ML / "d11_extension.py")
    cut = g3.concrete_cutoff()
    assert cut.get("archived_cutoff") is True or "ARCHIVED" in cut["reference_extension"]
    assert cut["w"]["Lorentz_invariant"] is False
    assert cut.get("active_prescription_id") == WW_ID or WW_ID in cut["reference_extension"]
    ww = load("O5_D11_Ww_reference.json")
    assert ww["prescription_id"] == WW_ID
    hyp = str(ww.get("archived_false_pointwise_hypothesis", ""))
    assert "pointwise" in hyp.lower() or "|T" in hyp
    # no `or True` escape
    assert ww["pass"] is True
    print("metadata_consistency_tests: PASS")


def run_all_builders() -> None:
    for s in [
        "convention_sheet.py",
        "mixed_scalar_noether.py",
        "d11_tensor.py",
        "d11_normalized.py",
        "d11_divergences.py",
        # Four math deliverables BEFORE Gate3 (active Ww earns result_3a)
        "d11_scalar_extension.py",
        "d11_global_representation.py",
        "d11_Ww_reference.py",
        "d11_contact_moments.py",
        "d11_extension.py",  # Gate3 via active Ww
        "d11_route1_transverse.py",
        "d11_ward_d12.py",
        "d11_subsector_summary.py",
    ]:
        run(s)


def check_certs() -> None:
    g0 = load("O5_matter_convention_sheet.json")
    g1 = load("O5_Gate1_mixed_scalar_noether.json")
    g2 = load("O5_Gate2_normalized_D11.json")
    g3 = load("O5_Gate3_extension.json")
    g4 = load("O5_Gate4_Ward_D12_onepoint.json")
    ten = load("O5_D11_tensor.json")
    div = load("O5_D11_contracted_divergences.json")
    d11 = load("O5_D11_scalar_loop_hh.json")
    verd = load("O5_matter_loop_subsector_verdict.json")
    sc = load("O5_D11_scalar_extension.json")
    gr = load("O5_D11_global_representation.json")
    ww = load("O5_D11_Ww_reference.json")
    cm = load("O5_D11_contact_moments.json")
    r1 = load("O5_Route1_transverse.json")

    assert g0["status"] == "Constructed"
    assert g1["pass"] is True
    assert g1.get("integrated", {}).get("XVI_N_master_still_broken") is False

    assert g2["status_prefactor"] == "Constructed"
    assert g2["comb_B_derivation"]["comb_B"] == "1/2"
    assert "24" in str(g2["tensor_kernel_scaling"]["contracted_tensor_witness"]["target"])

    assert ten["status"] == "Constructed"
    assert ten["spacelike_witness"]["T_0000_match"] is True
    assert ten["scaling"]["scaling_degree_sd"] == 8

    assert div["status"] == "Constructed"
    assert div["both_pairs"]["NOT_pushed_through_z_eq_0"] is True

    assert g3["result_3a_D11_extension"] == "Constructed"
    assert g3["status"] == "Partial"

    # Four deliverables
    assert sc["status"] == "Constructed"
    assert sc["proof_id"] == "lem:analytic_FP_u_mu_R_o70"
    assert sc["minkowski_residue"]["r_with_sign_and_i"] == "-i * pi**2"
    assert sc["conventions"]["NO_extra_c_delta_in_reference"] is True
    assert gr["status"] == "Constructed"
    assert gr["coefficients"]["alpha"] == "A**2/60"
    assert gr["coefficients"]["beta"] == "A**2/18"
    assert gr["coefficients"]["coefficients_used"] == "derived"
    assert gr["acceptance"]["symbolic_components_checked"] == 256
    assert gr["acceptance"]["symbolic_failures"] == []
    assert gr["Pi_tr"]["Pi_tr_restricts_on_U"] == "(i kappa^2 / 4) * T"
    assert gr["Pi_tr"]["NOT_Pi_tr_eq_T"] is True
    assert ww["status"] == "Constructed"
    assert ww["prescription_id"] == WW_ID
    assert cm["status"] == "Constructed"
    assert cm["L"]["status"] == "Constructed"
    assert cm["kernel_two_point_Ward"]["status"] == "Constructed"
    assert cm["odd_moments"]["NOT_metadata_flag"] is True

    assert g4["status"] == "Constructed"
    assert g4["result_3"]["contacts_3b"] == "Constructed"
    assert g4["symmetry_restored_bulk"] is False
    assert g4["symmetry_restored_subsector"] is True
    assert g4["D11_kernel_counterterm"] == "earned"
    assert g4["contact_defect"]["order_bound"] == 5
    assert g4["Ward_and_CT"]["functional_defect_A1_ST4b"]["ghost_number_defect"] == 1
    assert d11.get("four_deliverables", {}).get("all_pass") is True
    assert g4["active_Ww_prescription_id"] == WW_ID
    assert g4["Route1_primary"]["alpha"] == "A**2/60"
    assert g4["Route1_primary"]["beta"] == "A**2/18"

    assert r1["status"] == "Constructed"
    assert r1["ansatz_alpha_beta"]["alpha"] == "A**2/60"
    assert r1["ansatz_alpha_beta"]["NOT_defaulted"] is True
    assert r1["Pi_tr"]["NOT_Pi_tr_eq_T"] is True
    assert r1["NOT_corpus_P_trace_reversal"]["NOT_reusing_corpus_P"] is True

    assert verd["earned"] is True
    assert verd["subsector_verdict"] == FORBIDDEN
    assert verd["D11_kernel_counterterm"] == "earned"
    assert verd["symmetry_restored_bulk"] is False
    assert d11["status"] == FORBIDDEN
    assert d11["scaling"]["scaling_degree_sd"] == 8
    assert d11["scientific_verdict_earned"] is True
    assert d11["final_earned"] is True
    assert d11.get("promotion_predicate", {}).get("prerequisite_checks") is True
    assert d11["checks_passed"] is True
    assert d11["build_completed"] is True
    assert d11["symmetry_restored"] is False
    assert d11["revision"] == REV
    assert verd["revision"] == REV

    sys.path.insert(0, str(ROOT / "code" / "classical"))
    import inherited  # p13: pinned inherited input (workspace or vendored copy)
    h = hashlib.sha256(inherited.resolve("XVI-M.tex").read_bytes()).hexdigest()
    assert h == XVI_M_HASH

    print("check_certs: PASS")


def main():
    math_mutation_tests()
    run_all_builders()
    metadata_consistency_tests()
    deletion_wrong_revision_tests()
    check_certs()
    print("ALL test_matter_loop_gates: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
