#!/usr/bin/env python3
"""XVI-P p19 conventions: P.5 identity step (the projected one-loop kappa^2 ch-identity defect assembled from the
evaluated inputs; counterterm solve in the declared domain; D cap ker sigma_0); p18 reviewer findings I1-I3.

Layering.  p14r contract (code/p5_entry/*)  ->  p15 .. p17 layers  ->  p18 layer (code/p5_calc/{d11,p18_conventions,
release_p18}.py; byte-identical, sha256 below)  ->  p19 layer (code/p5_calc/{defect,p19_conventions,release_p19}.py,
P19_*).  The p19 gate (release_p19.py) runs after the p14r, p15, p16, p17 and p18 gates and requires all five accepted.

No contract revision in p19: every p14r contract file (code/p5_entry/*) is byte-identical to p18 (release_p19 checks).
"""
from __future__ import annotations

REVISION = "p19"
VERSION_LABEL = "XVI-P p19"           # single version variable (manuscript footer is checked against it)
CERT_PREFIX = "P19"
CONTRACT_REVISION = "p19 (p14r contract + disclosed p15/p16/p17/p18 revisions; none in p19)"
DATE = "2026-10-09"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p19.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p19.json"
P18_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p18.json"      # written by the reviewer; never here
P18_INDEPENDENT_REPORT_SHA256 = "893f167ef7124d981c0569ca386035aed06e0dbb0c90a2362a6ceeafd1930cb2"
P18_SOURCE_TREE_SHA256 = "bfab3b4b318fc37f2fcca209d097d27a24955e3b3d8469f5a8ab2e904ace7094"
P18_SOURCE_ZIP_SHA256 = "7c7d5451adb459092edc2606e1b3322909325000d47bab89c14b7f7a6d25c92f"
P18_ARCHIVED_RECORDS = {
    "archival/p18/reference_values_p18.json": "8a867f9eb57af673d9c7d70a19910a6afe2e80630bf6c4a245bd2ca2c99a35bf",
    "archival/p18/reproducibility/author_rebuild_report_p18.json":
        "13da1ba2eaf9cab1e1c3990bb50c41e66996ed52147e303d6bf28d22cefa5fa5",
    "archival/p18/reproducibility/independent_rebuild_report_p18.json": P18_INDEPENDENT_REPORT_SHA256,
    # per-file sha256 list of the released p18 source-only zip (base of the p19 change log; works source-only)
    "archival/p18/p18_source_files.json": "9b5ebcb021597a7345cfd2c36d9486d42a21e38c77fd19bd8aec4d6a60c3a1f3",
}
P18_SOURCE_LIST = "archival/p18/p18_source_files.json"

# the ch dependency rows (ledgers/P13_ch_dependency_rows.json, surviving) and their inputs
ROW_HH = "(S0,Gamma1^[2]) s2 K:K.c"
ROW_KC = "(S0,Gamma1^[2]) s1 h:h^2"
ROW_1PT = "(S1,Gamma1^[1]) s2 K:K.c.h"
ROWS = {ROW_HH: ("D01", "D02", "D03", "D11", "D12"), ROW_KC: ("D13",), ROW_1PT: ("D14a", "D14b", "D14c")}
INVENTORY_P19 = ("D01", "D02", "D03", "D11", "D12", "D13", "D14a", "D14b", "D14c")
HH_EVALUATED = ("D01", "D03", "D11")               # D02 = D12 = 0 (P15_batchA.json)

HARD_STOPS_P19 = {
    "bulk_symmetry_restored": False,               # stays false regardless (the identity is PROJECTED onto ch only)
    "symmetry_restored": False,
    "O1_closure": "NOT_CLOSED",
    "insertion_status": "Frozen_negative_obstruction_preserved",
    "XV_B_opened": False,
    "XIV_J_opened": False,
    "Route_B_discharged": False,
    "u_R_c_delta_added": False,
    "XVI_P_registered": False,
}
# flags that p19 may EARN, each only if its certificate says so (release_p19 reads them; never set by hand)
EARNABLE_P19 = ("projected_defect_computed", "projected_identity_verified", "projected_restoration_verified")

# p18 layer: byte-identical in p19 (sha256 from XVI-P-p18-source-only.zip; release_p19 recomputes them)
P18_CALC_SHA256 = {
    "code/p5_calc/d11.py": "432e1e91cf8d56001e49ffc5b673262ceb5438abb6a9d51b3477d613a7c7698d",
    "code/p5_calc/p18_conventions.py": "ea8ee2e148a873490050a09ea17d1a34297713f955c6bad134d9c3bc4b31f66e",
    "code/p5_calc/release_p18.py": "73a052ddf3ea2bfb2fcb4f1f6ee08c66752530580385769879a3556aafe0a0f5",
}
P18_DRED_SHA256 = "14c11a512c1609c9f9a7829dcb68e71a94c8ac3d38497e2dcac110a1b8d5e81c"     # dred.py as released in p18
NEW_CONTRACT_FILES_P19 = ()
DISCLOSED_CONTRACT_REVISIONS_P19 = {}

DISCLOSED_TEST_REVISIONS_P19 = {    # test files changed vs the p18 zip (release_p19 change log)
    "tests/test_p14.py": "names p18 -> p19 (reference file, source zip, author report, status revision); "
                         "generated prefixes certificates/ledgers P19_, manuscript/body/P19-",
    "tests/test_p18.py": "rs() reads the p18 LAYER record certificates/P18_release.json; the live p18 independent "
                         "report is bound to the p18 tree (pending or False here); test-file change log accepts "
                         "p18 or disclosed p19 revisions; build label is the current revision",
}
RUN_SPECIFIC_KEYS = ("reproducibility", "author_rebuild_passed", "independent_rebuild_passed",
                     "live_report_identical_to_archived", "live_report_present", "archived_zip_sha256_ok",
                     "list_equals_archived_zip")

# I2 (p18 reviewer): the extended static scan (tests/test_p19.py; a PATTERN CHECK, NOT A PROOF) also lists every
# package call of Poly.terms() / Poly.coeffs() (Horner-type evaluation route); each site is reviewed: the Poly
# generators are never d (loop momenta, polarisation symbols, Feynman parameter x, D1/D2, q, l.l/l.p, external dot
# products); coefficients may carry d but terms()/coeffs() do not evaluate them.
COEFF_SITES_REVIEWED = {
    "code/p5_calc/batchA.py::route2::P.terms()": "generators: loop momentum components l0..l3",
    "code/p5_calc/batchC.py::count_quadratic_component_terms::sp.Poly(tot, *gts).monoms()":
        "generators: Gt_* evanescent metric symbols (degree count only)",
    "code/p5_calc/covariant.py::fp_term::sp.Poly(expr, *gens).terms()":
        "generators: loop/external momentum symbols, K2, KP, Feynman parameter X",
    "code/p5_calc/d13.py::ck_basis::sp.Poly(e, *PS).coeffs()": "generators: external momentum components PS",
    "code/p5_calc/d13.py::ccb_basis::sp.Poly(e, *PS).coeffs()": "generators: external momentum components PS",
    "code/p5_calc/defect.py::ghost_equation_relation::sp.Poly(e, *PS).coeffs()":
        "generators: external momentum components PS (K1 probe)",
    "code/p5_calc/defect.py::_eqs::sp.Poly(x, *syms).terms()":
        "generators: external dot products (d and the unknowns excluded explicitly)",
    "code/p5_calc/integrals.py::J_two_point::sp.Poly(num, D1, D2).terms()": "generators: propagator symbols D1, D2",
    "code/p5_calc/integrals.py::fp_two_point::P.terms()": "generators: shifted loop momenta k0..k3",
    "code/p5_calc/integrals.py::fp_two_point::Px.terms()": "generator: Feynman parameter x",
    "code/p5_entry/counterterm_domain.py::density::P.terms()": "generators: momentum components p0..p3",
    "code/p5_entry/counterterm_domain.py::two_point_vector::sp.Poly(rest, *p).monoms()":
        "generators: momentum components p0..p3 (exponents only)",
    "code/p5_entry/dred.py::_integral_functional::P.terms()": "generators: l.l, l.p (J_tag names; nothing evaluated)",
    "code/p5_entry/feynman.py::ge_vertex::P.terms()": "generators: graviton polarisation symbols (esym_pol)",
    "code/p5_entry/hessian_route.py::_ell_monomials::sp.Poly(e, *gens).terms()":
        "generators: free symbols of the classical 4D ell_k jets (field/momentum names); a d-like name would raise "
        "(index parse of the name, rational coefficients cf.p/cf.q required): fails closed",
    "code/p5_entry/prescription_d11.py::vec::sp.Poly(v, *p).terms()": "generators: momentum components p0..p3",
    "code/p5_entry/prescription_d11.py::M3_local_space::sp.Poly(e, *p).terms()": "generators: momentum components p0..p3",
    "code/p5_entry/shadow.py::expect::P.terms()": "generator: q",
}
POLY_GENERATOR_CALL_SITES_REVIEWED = {     # I2: Poly(.., *<call>) sites (generators built at run time)
    "code/p5_entry/feynman.py::ge_vertex::sp.Poly(v, *polsyms.keys())":
        "generators: graviton polarisation symbols esym_pol(leg) (dict keys); d never a key",
}
