#!/usr/bin/env python3
"""XVI-P p16 conventions: P.5 calculation, second step (E2 evanescent analysis; Batch C: D01, D03).

Layering.  p14r contract (code/p5_entry/*, P14_*)  ->  p15 calculation layer (Batch A, D13; code/p5_calc/{inte
  +> grals,
batchA,d13,p15_conventions,release_p15}.py, P15_*; byte-identical to p15)  ->  p16 layer (covariant route, Bat
  +> ch C,
E2 analysis; code/p5_calc/{covariant,batchC,e2_evanescent,p16_conventions,release_p16}.py, P16_*).  The p16 ga
  +> te
(release_p16.py) runs after the p14r and p15 gates and requires both to be accepted.

Disclosed CONTRACT revision in p16 (DISCLOSED_CONTRACT_REVISIONS_P16): code/p5_entry/dred.py only -- F3 harden
  +> ing of
the opaque d (expr.replace / pattern matching / lambdify code printers) on top of the p15 F1 correction.  NO e
  +> vanescent
counterterm is added: the E2 decoupling from the ch-projected slot is PROVEN (P16_E2_evanescent.json).
All other p14r contract files are byte-identical to p14r; all p15 calculation files are byte-identical to p15.
"""
from __future__ import annotations

REVISION = "p16"
VERSION_LABEL = "XVI-P p16"           # single version variable (manuscript footer is checked against it)
CERT_PREFIX = "P16"
CONTRACT_REVISION = "p16 (p14r contract + disclosed p15/p16 revisions)"
DATE = "2026-10-08"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p16.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p16.json"
P15_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p15.json"      # written by the reviewer;
  +>  never here
P15_INDEPENDENT_REPORT_SHA256 = "6bc760c24f48d61fe066dde62cbe5b41daa7e4eafc347f8fd72e1a84fcab4713"
P15_SOURCE_TREE_SHA256 = "79f5375272d6e7327721572ae7eeff59d6bf69d2eb13d353204d38ce9c1dc84f"
P15_SOURCE_ZIP_SHA256 = "54325c1ff6c079e0389f96d9c0875524c73f6a706e079fd1734c1b1701c707d3"
P15_ARCHIVED_RECORDS = {
    "archival/p15/reference_values_p15.json": "0866adfe0f9dc281053b84dcabbe751a8a7425f522d37839373b4d373415cda
  +> 8",
    "archival/p15/reproducibility/author_rebuild_report_p15.json":
        "1e729eba3f3faa6a5cfbd1b55947245d643c7855756604c8a5b886cc28dbc5e6",
    # per-file sha256 list of the released p15 source-only zip (base of the F5 change log; works in a source-o
  +> nly tree)
    "archival/p15/p15_source_files.json": "09536539460ad68e09e15d1f92d1046afa8f4a3ee946b0396fa852ba28d1fbe8",
}
P15_SOURCE_LIST = "archival/p15/p15_source_files.json"

BATCH_C = ("D01", "D03")
NOT_EVALUATED_P16 = ("D11",)                       # M2 undischarged
STATUS_VALUES = ("unevaluated", "regulated", "vanishing_under_declared_prescription", "renormalized")

HARD_STOPS_P16 = {
    "quantum_inputs_evaluated": "not_earned",          # D11 open -> not every required input is evaluated
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
    "XVI_P_registered": False,
    "D11_evaluated": False,
}

# p15 calculation layer: byte-identical in p16 (sha256 from XVI-P-p15-source-only.zip; release_p16 recomputes 
  +> them)
P15_CALC_SHA256 = {
    "code/p5_calc/batchA.py": "5481edfed7331165a3ba68cb2cc229975b8e6e6c581bd0014ae983a7cf4d8e76",
    "code/p5_calc/d13.py": "55c01198a6074fb89a24c261d28bd413bbc5113b9d716aed4f43a55d7bb5dccb",
    "code/p5_calc/integrals.py": "3175f53d5c8ef2abd82ee5e1d19f3097185c0e121d612750485adf7ac82843dc",
    "code/p5_calc/p15_conventions.py": "4ff06f631512bc83196651057f41468debc6cf2d8d661f84139f097e436715d3",
    "code/p5_calc/release_p15.py": "9048a6c8414938ba79b7eae93cba760b6cbc5e5fcdc8e377efda39342f9ba9d0",
}
P14R_CONTRACT_FILES_CHANGED_IN_P16 = ("code/p5_entry/dred.py",)
NEW_CONTRACT_FILES_P16 = ()
P15_DRED_SHA256 = "290e440419cba3b6ba554bcb73dfad5cc2fc150af1b1567c3f90388cd6cc173b"     # dred.py as released
  +>  in p15

DISCLOSED_CONTRACT_REVISIONS_P16 = {
    "code/p5_entry/dred.py": {
        "kind": "contract revision (disclosed), p16 (on top of the p15 F1 correction)",
        "finding": "F3_opaque_d_bypass, reproducibility/independent_rebuild_report_p15.json",
        "why": ("OpaqueDimension guarded subs/xreplace/evalf(subs)/limit, but expr.replace(d, 4) and sympy.lam
  +> bdify "
                "bypassed it (the reviewer probe returned 0); no package code used those paths"),
        "change": ("OpaqueDimension.matches raises outside substitute_d (closes expr.replace(d, value) and pat
  +> tern "
                   "queries for d); the code-printer hooks used by lambdify (_lambdacode, _numpycode, _scipyco
  +> de, "
                   "_mpmathcode, _pythoncode, _cupycode, _jaxcode, _tensorflowcode) raise outside substitute_d
  +> ; "
                   "remaining value paths that the guard CANNOT hook -- replace with a callable query "
                   "(expr.replace(lambda x: x == d, ...)), Poly(.., d).eval, string round-trips -- are covered
  +>  by a "
                   "static AST scan of code/p5_calc and code/p5_entry (tests/test_p16.py) -- none is used"),
        "rules_R1_R6_changed": False,
        "released_values_affected": False,
        "why_unaffected": ("no package code used replace/lambdify/Poly.eval on d (static scan); the P14/P15 "
                           "certificate content hashes recomputed in p16 equal those of archival/p15/"
                           "reference_values_p15.json (tests/test_p16.py)"),
    },
}
DISCLOSED_TEST_REVISIONS_P16 = {    # test files changed vs the p15 zip (release_p16 change log, tests/test_p1
  +> 6.py F5)
    "tests/test_p14.py": ("source-set / zip / reference names p15 -> p16 (SM.ZIP_NAME, SM.REFERENCE_FILE, auth
  +> or report "
                          "path, resumed-build placeholder zip); generated-prefix list extended by P16_* certi
  +> ficates/"
                          "ledgers, the P16 results table and manuscript/version.tex; top-level status revisio
  +> n p16. "
                          "No assertion weakened."),
    "tests/test_p15.py": ("test_p15_release_status_and_hard_stops reads the p15 LAYER record certificates/"
                          "P15_release.json (the top-level RELEASE_STATUS.json is now the p16 status); its cur
  +> rent-tree "
                          "independent flag may be False (the p15 report is bound to the p15 tree) or pending 
  +> (report "
                          "absent in a source-only copy). All other p15 assertions unchanged."),
}
RUN_SPECIFIC_KEYS = ("reproducibility", "author_rebuild_passed", "independent_rebuild_passed",
                     "live_report_identical_to_archived", "live_report_present", "archived_zip_sha256_ok",
                     "list_equals_archived_zip")
