"""XVI-P p15 tests: first P.5 calculation (Batch A, D13), the disclosed p14r contract correction (structural R
  +> 5
safeguard in dred.py, finding F1 of the p14r independent rebuild) with the reviewer's toys as regression tests
  +> , and
the p15 release status."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
for p in ("code/p5_calc", "code/p5_entry", "code/classical", "tools"):
    sys.path.insert(0, str(ROOT / p))
import p15_conventions as QC  # noqa: E402
import dred as DR  # noqa: E402

CERT = ROOT / "certificates"


def cj(name):
    return json.loads((CERT / name).read_text())


# ================================================================ the disclosed contract correction (finding 
  +> F1)
M, A1, A2 = sp.symbols("m a1 a2")
A0 = M ** 2 * (1 / DR.eps + A1 + A2 * DR.eps)          # J = m^2 A0 = int l^2/(l^2 - m^2)


def _eta_toy(mutation=None, enforce=True):
    """reviewer toy A (eta-projected): eta^{rs} int l_r l_s/(l^2 - m^2) = eta^{rs} ghat_rs J/d = J."""
    DR._RED.clear()
    DR._LIFT.clear()
    P = DR.Pipeline(DR.Rules(), mutation, enforce)
    tot = sp.expand(sum(DR.ETA[r] * P.reduced_component([r, r], with_p=False, tag="RTT") for r in range(4)))
    tot = DR.eta_trace_Gt(tot, P.rules)
    return P.laurent(tot, {sp.Symbol("J_RTT[1,0]"): M ** 2 * A0})


def test_reviewer_eta_trace_toy_false_positive_fixed():
    """p14r heuristic: raised on this CORRECT d-free result.  Structural guard: no exception, finite a1 m^4.""
  +> "
    out = _eta_toy()
    assert sp.simplify(out["finite"] - A1 * M ** 4) == 0 and sp.simplify(out["pole"] - M ** 4 / DR.eps) == 0


def test_reviewer_eta_trace_toy_false_negative_fixed():
    """p14r heuristic: did NOT raise under premature_d4 (finite m^4 (a1 - 1/2)).  Structural guard: raises."""
    with pytest.raises(DR.PrematureD4Substitution):
        _eta_toy("premature_d4")
    forced = _eta_toy("premature_d4", enforce=False)          # display only (authorised path, recorded)
    assert sp.simplify(forced["finite"] - M ** 4 * (A1 - sp.Rational(1, 2))) == 0


def test_opaque_dimension_refuses_every_unauthorised_substitution():
    e = DR.d ** 2 / (DR.d - 1) + sp.Symbol("x")
    for bad in (lambda: e.subs(DR.d, 4), lambda: e.xreplace({DR.d: 4}), lambda: e.subs({DR.d: 4 - 2 * DR.eps})
  +> ,
                lambda: sp.Integer(3) * DR.d + 1 and (3 * DR.d).subs(DR.d, sp.Rational(7, 2))):
        with pytest.raises(DR.PrematureD4Substitution):
            bad()
    n0 = DR.D_PROVENANCE.get("test: authorised", 0)
    assert DR.substitute_d(e, 4, "test: authorised") == sp.Rational(16, 3) + sp.Symbol("x")
    assert DR.D_PROVENANCE["test: authorised"] == n0 + 1
    assert e.subs(sp.Symbol("x"), 1).has(DR.d)                 # other substitutions are unaffected


def _ghat_contract(red, con, with_p, tag):
    B, C = DR.reduce_tensor(2, with_p, red, tag)
    tot = 0
    for b, c in zip(B, C):
        tot += c * DR.contract([(sp.Integer(1), t + (("g", "h", "m0", "m1"),)) for t in b["terms"]], con).get(
  +> (), 0)
    return sp.expand(tot)


def test_reviewer_A0_mixing_toy():
    """reduce with tr ghat = d but contract with tr ghat = 4: refused; forced display shifts the finite part b
  +> y +m^4/2."""
    DR._RED.clear()
    J = {sp.Symbol("J_RAT[1,0]"): M ** 2 * A0}
    good = DR.Pipeline().laurent(_ghat_contract(DR.Rules(), DR.Rules(), False, "RAT"), J)
    assert sp.simplify(good["finite"] - A1 * M ** 4) == 0
    with pytest.raises(DR.NumericTraceForbidden):
        _ghat_contract(DR.Rules(), DR.Rules(trace_hat=4), False, "RAT")
    mixed = _ghat_contract(DR.Rules(), DR.Rules(trace_hat=4, display_only=True), False, "RAT")
    forced = DR.Pipeline(enforce=False).laurent(mixed, J)
    assert sp.simplify(forced["finite"] - good["finite"] - M ** 4 / 2) == 0


def test_reviewer_B0_mixing_toy():
    """ghat_{mu nu} int l^mu l^nu/(l^2 (l-p)^2) = J[1,0] = 0 (scaleless); the d/4 mixing gives -p^2/6."""
    DR._RED.clear()
    p2, b1, b2 = sp.symbols("p2 b1 b2")
    J = {sp.Symbol("J_RBT[1,0]"): sp.Integer(0), sp.Symbol("J_RBT[0,2]"): p2 ** 2 * (1 / DR.eps + b1 + b2 * DR
  +> .eps) / 4}
    pp = {sp.Symbol("p.p"): p2}
    good = DR.Pipeline().laurent(_ghat_contract(DR.Rules(), DR.Rules(), True, "RBT").xreplace(pp), J)
    assert sp.simplify(good["finite"]) == 0 and sp.simplify(good["pole"]) == 0
    with pytest.raises(DR.NumericTraceForbidden):
        _ghat_contract(DR.Rules(), DR.Rules(trace_hat=4), True, "RBT")
    mixed = _ghat_contract(DR.Rules(), DR.Rules(trace_hat=4, display_only=True), True, "RBT").xreplace(pp)
    forced = DR.Pipeline(enforce=False).laurent(mixed, J)
    assert sp.simplify(forced["finite"] + p2 / 6) == 0


def test_dred_certificate_records_the_correction():
    dr = cj("P14_dred_rules.json")
    c = dr["p15_contract_correction"]
    assert c["released_p14r_values_affected"] is False and "F1" in c["finding"]
    assert c["regression_toys"]["pass"] is True
    assert dr["mutations"]["premature_d4"]["rejected"] and dr["mutations"]["trace_ghat_eq_4"]["structurally_re
  +> fused"]
    src = (ROOT / "code" / "p5_entry" / "dred.py").read_text()
    assert "is a rule violation and is detected (PrematureD4)" not in src           # the p14r claim is correc
  +> ted
    assert "FALSE POSITIVE" in src and "FALSE NEGATIVE" in src and "OpaqueDimension" in src


def test_contract_byte_identical_except_disclosed_correction():
    cur = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    changed = sorted(k for k, h in QC.P14R_CONTRACT_SHA256.items() if cur.get(k) != h)
    assert changed == sorted(QC.DISCLOSED_CONTRACT_CORRECTIONS) == ["code/p5_entry/dred.py"]
    assert set(cur) == set(QC.P14R_CONTRACT_SHA256)
    assert QC.DISCLOSED_CONTRACT_CORRECTIONS["code/p5_entry/dred.py"]["released_p14r_values_affected"] is Fals
  +> e


# ================================================================ library, scaleless rule
def test_integral_library_certified():
    lib = cj("P15_integral_library.json")
    assert lib["library_certified"] is True and lib["revision"] == "p15"
    assert lib["tensor_reduction_vs_feynman_parameters"] and lib["B0_exact_d_numeric"] and lib["T_exact_d_nume
  +> ric"]


def test_scaleless_rule_is_explicit_and_refuses_scaleful_integrals():
    import integrals as IL
    with pytest.raises(IL.ScalelessRuleMisuse):
        IL.scaleless(0, 1, "test: massive tadpole", has_scale=True)
    n = len(IL.LEDGER)
    assert IL.scaleless(0, 2, "test: log") == 0 and IL.LEDGER[n]["omega"] == 0
    assert "1/eps_UV - 1/eps_IR" in IL.LEDGER[n]["class"]
    assert IL.scaleless(1, 1, "test: power") == 0 and "power divergence" in IL.LEDGER[n + 1]["class"]


# ================================================================ Batch A
def test_batchA_graphs():
    a = cj("P15_batchA.json")
    assert set(a["graphs"]) == set(QC.BATCH_A) and a["batchA_evaluated"]["execution"] is True
    for k, g in a["graphs"].items():
        assert g["status"] == "vanishing_under_declared_prescription", k
        assert g["value_imported_from_XVI_O"] is False
        assert g["verification_controls"]["route1_dred_lift_equals_route2_symmetric_integration"] is True
        assert g["scaleless_analysis"]["logarithmic_members"] == []          # NOT a 1/eps_UV - 1/eps_IR cance
  +> llation
        assert all(x["omega"] > 0 for x in g["scaleless_analysis"]["S0_applications"])
        assert g["prescription_dependence"]["p14r_counterterm_required"] is False
    assert a["D12_slot"]["status"] == "vanishing_under_declared_prescription" and a["D12_slot"]["derivation"]
    assert a["one_point_slot_kappa1"]["graphs"] == ["D14a", "D14b", "D14c"]
    assert a["gate_checks"]["D12_separate_from_one_point_slot"] is True


# ================================================================ Batch B: D13
def test_D13_values_and_controls():
    c = cj("P15_D13.json")
    r = c["result"]
    assert [r[k]["UV_pole"] for k in ("T1", "T2", "T3", "E1", "E2")] == ["0", "3/16", "-1/4", "0", "1/16"]
    assert [r[k]["local_polynomial"] for k in ("T1", "T2", "T3", "E1", "E2")] == ["0", "1/3", "-5/12", "0", "1
  +> /6"]
    assert all(sp.sympify(r[k]["nonlocal_coefficient_of_L"]) == -sp.sympify(r[k]["UV_pole"]) for k in r)
    assert c["UV_pole_in_p14r_cK_basis"]["coordinates"] == ["0", "3/8", "-1/4"]
    assert c["status"] == "regulated" and c["sector_status"]["4D_structures_T1_T3"] == "renormalized"
    assert c["evanescent_pole_nonzero"] is True and c["evanescent_counterterm_declared_in_p14r"] is False
    assert all(v is True for v in c["controls"].values()) and c["D13_evaluated"]["execution"] is True
    g = c["ghost_self_energy_pole"]
    assert g["pole_in_p14r_c_cb_coordinates"] == ["-3/8", "1/4"] and g["evanescent_pole_SE"] == "-1/8"


def test_D13_mutations_change_result_and_are_rejected():
    m = cj("P15_D13.json")["mutations"]
    assert set(m) == {"wrong_ghost_loop_sign", "premature_d4", "drop_evanescent_Gt", "wrong_symmetry_factor",
                      "wrong_K_c_ordering"}
    assert all(v["changes_result"] is True and v["rejected"] is True for v in m.values())
    assert "structural" in m["premature_d4"]["reason"]


def test_D13_premature_d4_is_refused_at_the_substitution():
    import d13
    with pytest.raises(DR.PrematureD4Substitution):
        d13.route1(mutation="premature_d4")


# ================================================================ p15 release status
def test_p15_release_status_and_hard_stops():
    rs = json.loads((CERT / "P15_release.json").read_text())        # p16: the p15 LAYER record (top level is 
  +> p16)
    assert rs["revision"] == "p15" and rs["contract_revision"] == "p14r" and rs["publication"] == "accepted"
    assert rs["batchA_evaluated"] is True and rs["D13_evaluated"] is True and rs["library_certified"] is True
    for k in ("batchA_evaluated", "D13_evaluated"):
        assert set(rs["flags"][k]) == {"execution", "claim", "scope"}
    assert rs["hard_stops"] == QC.HARD_STOPS_P15 and rs["hard_stops_hold"] is True
    assert rs["hard_stops"]["quantum_inputs_evaluated"] == "not_earned" and rs["O1_closure"] == "NOT_CLOSED"
    assert rs["bulk_symmetry_restored"] is False and rs["Route_B_discharged"] is False
    assert all(rs["graphs"][k]["status"] == "unevaluated" for k in QC.NOT_EVALUATED_P15)
    assert rs["D12_status"] == "vanishing_under_declared_prescription" and rs["D12_status_derivation"]
    assert rs["contract_identity"]["changed"] == ["code/p5_entry/dred.py"]
    assert rs["milestones"]["status"]["P.5_identity"] == "open"
    # p16: this layer record's current-tree flag reads the p15 report path, which (where present) is bound to 
  +> the p15
    # tree, so it is never true for the p16 tree; the p16 flag is in the top-level status
    assert rs["independent_rebuild_passed"] in ("pending", False)


def test_p14r_independent_rebuild_recorded_with_caveat():
    rs = json.loads((ROOT / "RELEASE_STATUS.json").read_text())
    rec = rs["p14r_independent_rebuild"]
    assert rs["independent_rebuild_passed_p14r"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P14R_SOURCE_TREE_SHA256
    assert rec["bound_to_source_zip_sha256"] == QC.P14R_SOURCE_ZIP_SHA256
    assert rec["report_sha256_pinned"] is True and "SAME-BOX" in rec["caveat"]
