#!/usr/bin/env python3
"""XVI-P p15 conventions: FIRST P.5 CALCULATION (Batch A: D02, D12, D14a-c; Batch B: D13).

Layering.  The p14r P.5-entry contract (code/p5_entry/*, P14_* certificates, revision label p14r) is the froze
  +> n
contract on which p15 evaluates.  p15 adds a calculation layer (code/p5_calc/*, P15_* certificates); the p15 r
  +> elease
gate (release_p15.py) runs AFTER the p14r contract gate and requires it to be accepted.

ONE disclosed contract revision (DISCLOSED_CONTRACT_CORRECTIONS): code/p5_entry/dred.py, after finding F1 of t
  +> he p14r
independent rebuild (the heuristic PrematureD4 guard had a false positive and a false negative).  Every other 
  +> p14r
contract file is byte-identical to p14r (P14R_CONTRACT_SHA256, checked by release_p15).  Released p14r values 
  +> are
unaffected: p14r applied Pipeline.laurent only to toy placeholders.
"""
from __future__ import annotations

REVISION = "p15"
CERT_PREFIX = "P15"
CONTRACT_REVISION = "p14r"
DATE = "2026-10-08"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p15.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p15.json"
P14R_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p14r.json"   # written by the reviewer; 
  +> never here
P14R_SOURCE_TREE_SHA256 = "a64c0ae365980fa6b077f991df4316347527613075e87f17fecfe422db6e3894"
P14R_SOURCE_ZIP_SHA256 = "19e8bf599daf102d8e23382544e6c6991ea307b2c3f31a0a97ad66d0b8a3dba3"

BATCH_A = ("D02", "D12", "D14a", "D14b", "D14c")
BATCH_B = ("D13",)
NOT_EVALUATED_P15 = ("D01", "D03", "D11")            # Batch C (p16) and the D11 matching (M2)

STATUS_VALUES = ("unevaluated", "regulated", "vanishing_under_declared_prescription", "renormalized")

# the p15 calculation-layer hard stops (the p14r contract hard stops are unchanged and checked by release_p14)
HARD_STOPS_P15 = {
    "quantum_inputs_evaluated": "not_earned",          # needs all three slots in one matched framework
    "projected_defect_computed": "not_earned",
    "projected_identity_verified": "not_earned",
    "projected_restoration_verified": "not_earned",
    "bulk_symmetry_restored": False,
    "symmetry_restored": False,
    "D11_matching_verified": False,
    "O1_closure": "NOT_CLOSED",
    "insertion_status": "Frozen_negative_obstruction_preserved",
    "XV_B_opened": False,
    "XIV_J_opened": False,
    "Route_B_discharged": False,
    "u_R_c_delta_added": False,
    "D01_evaluated": False, "D03_evaluated": False, "D11_evaluated": False,
}

# sha256 of the p14r contract code (from XVI-P-p14r-source-only.zip, tree a64c0ae3...); release_p15 recomputes
  +>  them
P14R_CONTRACT_SHA256 = {
    "code/p5_entry/amplitude_rules.py": "0daf63a3c8803d54514cb2aac29bea127c379e025f32c5b0219d365de5bdde4a",
    "code/p5_entry/counterterm_domain.py": "bf2eb6bdb9c64f4bd9e7fce459c6f8b1bf2167323589a3832e8c9ad4dcb91241",
    "code/p5_entry/dossier_p14.py": "94996ab4505219f9a40facffeebb3d9c419bbb8f4ecfbf3635d41705e53fb7e5",
    "code/p5_entry/dred.py": "ba85b00cd10e77d4274808f7dcaef1cb5b1934761fe8a81551e3c7405939ee20",
    "code/p5_entry/feynman.py": "4fab8b0d4a1cc0b4cd0be19ec30ace80559b92fa9808f1fc25c858599a389344",
    "code/p5_entry/freeze_p13.py": "9151ea2e22919319364c52fd42d2accab9af11ea17d15df8a3938149b31df0f1",
    "code/p5_entry/hessian_route.py": "a7bee01d140d07b06ae7ddfba5316ce4d7d43ac8fd00d497fa468ac8d1b6cee8",
    "code/p5_entry/p14_conventions.py": "687e4fa9bdcf0c87a2f71aec4470986997185b82507f608fdd888cf6a90aa5b4",
    "code/p5_entry/prescription_d11.py": "f05fc3de6c07bf542960388144f21aa51ba31993a890ef3fa306a287b25f33fb",
    "code/p5_entry/quantum_object.py": "ea4ebc5aa916ea975ba56ee9aacedeb67e3d483196b2920b77895f5b375e8c05",
    "code/p5_entry/release_p14.py": "d22cf1001e54ae4a4551497dbc1fd97a82d184984964d49d00826dc84e242217",
    "code/p5_entry/shadow.py": "de6556660359bc2d8ee00621d39004944a1a0f300200a0402c0b072a28e4648b",
}

DISCLOSED_CONTRACT_CORRECTIONS = {
    "code/p5_entry/dred.py": {
        "kind": "p14r contract revision (disclosed), applied inside p15",
        "finding": "F1_premature_d4_guard_heuristic, reproducibility/independent_rebuild_report_p14r.json",
        "why": ("the p14r PrematureD4Substitution guard was a heuristic on the shape of the expression before 
  +> the "
                "Laurent expansion: FALSE POSITIVE on eta^{rs} int l_r l_s/(l^2-m^2) = J (correct, d-free) and
  +>  FALSE "
                "NEGATIVE under premature_d4 on the same integral (eta_trace_Gt reintroduces d via tr gtilde =
  +>  4-d: "
                "d J/4, finite error -m^4/2); the R5 docstring claim 'is detected' did not hold in general"),
        "change": ("structural, provenance-based safeguard: d is an OpaqueDimension (subs/xreplace raise "
                   "PrematureD4Substitution outside dred.substitute_d, which records every authorised use); nu
  +> meric "
                   "traces of ghat/gtilde refused (NumericTraceForbidden) unless display_only; the heuristic i
  +> s "
                   "removed; R5 docstring corrected; reviewer toys added as regression checks (reviewer_toys)"
  +> ),
        "rules_R1_R6_changed": False,
        "released_p14r_values_affected": False,
        "why_unaffected": "p14r applied Pipeline.laurent only to toy placeholders; no loop integral was evalua
  +> ted",
    },
}
# test-suite revision that accompanies the correction (tests are not contract code; disclosed for completeness
  +> )
DISCLOSED_TEST_REVISIONS = {
    "tests/test_p14.py": ("test_dred_trace_ghat_eq_4_rejected: a numeric trace is now refused (NumericTraceFor
  +> bidden); "
                          "the tr ghat = 4 display uses Rules(trace_hat=4, display_only=True); infrastructure 
  +> "
                          "assertions read the p14r contract record from certificates/P14_release.json (the to
  +> p-level "
                          "RELEASE_STATUS.json is the p15 status)"),
}
P14R_INDEPENDENT_REPORT_SHA256 = "09cda7db0d1f8e1cf7409212e4ee88ef60f21975e1367472f2c3ed45f1f7004b"
# the other archived p14r records shipped as source (read when the zips are written): pinned by sha256
P14R_ARCHIVED_RECORDS = {
    "archival/p14r/reference_values_p14r.json": "9e81749235d3cb115aacc748de0ae4f89c6eae81b3e99f45585d1ad36b328
  +> f48",
    "archival/p14r/reproducibility/author_rebuild_report_p14r.json":
        "2f7def0c65f954c4866a8d2efafcf117f31f7a357a023e85ce6f67182aff6db1",
}
# run-specific keys of the contract record (rebuild flags/records; freeze sub-records that depend on files abs
  +> ent from
# a source-only copy): excluded when release_p15 hashes its inputs (same list as tools/rebuild_from_source.py)
RUN_SPECIFIC_KEYS = ("reproducibility", "author_rebuild_passed", "independent_rebuild_passed",
                     "live_report_identical_to_archived", "live_report_present", "archived_zip_sha256_ok",
                     "list_equals_archived_zip")
