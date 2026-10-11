#!/usr/bin/env python3
"""XVI-P p20 conventions: CORRECTION release of p19 (no scope expansion), from the p19 independent-rebuild findings.

  K1  orientation fix: the P15 ghost self-energy Sigma is (cb,c)-oriented, the route-G c.cb slots are (c,cb); the
      Grassmann orientation ratio (-1) is measured and applied; the derived relative factor +1 then gives full sigma_0
      closure of the complete one-loop kappa^2 MS-bar counterterm (p19 'closure fails / needs -1' RETRACTED, erratum).
  R   projected_restoration_verified REDEFINED (p19 definition followed from identity + locality): full sigma_0
      closure of the complete MS-bar S_ct incl. c.cb, Sigma held fixed; scope one-loop kappa^2 counterterm only.
  B   blind spots: full-closure mutation detector (drop D13, flip K.c); D11 normalisation pin (d11_pin.py ->
      P20_D11_pin.json: ratio pin derived; absolute pin OPEN).
  J1  wording; scan patterns extended (pattern check, not a proof); release reject leaves no stale RELEASE_STATUS.

Layering.  p14r contract -> p15 .. p18 layers (byte-identical) -> p19 layer (code/p5_calc/{defect,p19_conventions,
release_p19}.py, P19_*; defect.py and release_p19.py are DISCLOSED p20 revisions, p19_conventions.py byte-identical)
-> p20 layer (code/p5_calc/{d11_pin,p20_conventions,release_p20}.py, P20_*).  No contract revision in p20.
"""
from __future__ import annotations
from p19_conventions import (ROW_HH, ROW_KC, ROW_1PT, ROWS, HH_EVALUATED, P18_CALC_SHA256,  # noqa: F401
                             P18_DRED_SHA256, RUN_SPECIFIC_KEYS)
from p19_conventions import COEFF_SITES_REVIEWED as _C19, POLY_GENERATOR_CALL_SITES_REVIEWED as _G19
from p19_conventions import HARD_STOPS_P19, EARNABLE_P19

REVISION = "p20"
VERSION_LABEL = "XVI-P p20"
CERT_PREFIX = "P20"
CONTRACT_REVISION = "p20 (p14r contract + disclosed p15/p16/p17/p18 revisions; none in p19 or p20)"
DATE = "2026-10-09"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p20.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p20.json"
P19_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p19.json"      # written by the reviewer; never here
P19_INDEPENDENT_REPORT_SHA256 = "1b01f1d8e509afedcfd73d91685806205c56e7fe57a500b3a0bf008dd2811f45"
P19_SOURCE_TREE_SHA256 = "fcf90354d746e244fa2839048118bd8d64b1859ffd3825c0bfa3e1138ee88f36"
P19_SOURCE_ZIP_SHA256 = "da9242752d2e3753d8b2ce7fbb21e7cdb28487cc7966c2ca52d1ef1376658875"
P19_INDEPENDENT_SAME_BOX = True     # disclosed: the p19 independent rebuild ran on the same box
P19_ARCHIVED_RECORDS = {
    "archival/p19/reference_values_p19.json": "08f10fa86305ccb03a57dbae65ec22b6991724931af7f954a8c4ca4aea9c44af",
    "archival/p19/reproducibility/author_rebuild_report_p19.json":
        "5f0715f3b4ae756b261a0d757fd8247ede1bae1fc0c9ea8762635971b20ec1e4",
    "archival/p19/reproducibility/independent_rebuild_report_p19.json": P19_INDEPENDENT_REPORT_SHA256,
    "archival/p19/p19_source_files.json": "01b34cc820a3ceb42669ab2a534b82afb2fd6320634276093f8eae41914e37c6",
}
P19_SOURCE_LIST = "archival/p19/p19_source_files.json"
INVENTORY_P20 = ("D01", "D02", "D03", "D11", "D12", "D13", "D14a", "D14b", "D14c")
HARD_STOPS_P20 = dict(HARD_STOPS_P19)
EARNABLE_P20 = EARNABLE_P19 + ("D11_ratio_pin_verified",)
OPEN_PINS_P20 = ("D11_absolute_normalisation (Ghat -> a_2 map not derived)",)

# p19 layer in p20: p19_conventions.py byte-identical; defect.py, release_p19.py DISCLOSED revisions
P19_CONVENTIONS_SHA256 = "aa8560c22dd55fa6b4305368dad0cc95b9b5cf1ef6f50329d17ea2d03cd430af"
P19_RELEASED_SHA256 = {
    "code/p5_calc/defect.py": "4c154fb173b39aac7931234f78fa445b8039264f6ee07eb6e40785e349f7c8c5",
    "code/p5_calc/release_p19.py": "48dfe84616bab72b0c467642aec97998c26e9f24d51aeeef85f448fa00eb191b",
}
DISCLOSED_P19_LAYER_REVISIONS_P20 = {
    "code/p5_calc/defect.py": ("K1 orientation fix (measured ratio, Sigma converted to route-G (c,cb)); tree controls; "
                               "full sigma_0 closure of the complete MS-bar S_ct; restoration REDEFINED; full-closure "
                               "mutation detector; p19 criterion relabelled route-consistency control; J1 wording; "
                               "K1 erratum texts"),
    "code/p5_calc/release_p19.py": ("claim texts: K1 erratum (p19 'closure fails / needs -1' retracted); restoration "
                                    "content checks on the p20 definition; reject removes stale RELEASE_STATUS.json"),
}
NEW_CONTRACT_FILES_P20 = ()
DISCLOSED_CONTRACT_REVISIONS_P20 = {}
DISCLOSED_TEST_REVISIONS_P20 = {
    "tests/test_p14.py": "names p19 -> p20; generated prefixes P20_",
    "tests/test_p19.py": ("K1 tests corrected (orientation, full closure with derived +1); restoration on the p20 "
                          "definition; J1 wording; p19 independent report bound to the p19 tree; scan sites = p19 + "
                          "p20 reviewed lists"),
}
COEFF_SITES_REVIEWED = dict(_C19)
COEFF_SITES_REVIEWED.update({
    "code/p5_calc/d11_pin.py::curvature_forms::sp.Poly(sp.expand(f - a * q2 - b * q0), *gens).coeffs()":
        "generators: metric perturbation symbols h_ab (no d anywhere in d11_pin)",
})
POLY_GENERATOR_CALL_SITES_REVIEWED = dict(_G19)
