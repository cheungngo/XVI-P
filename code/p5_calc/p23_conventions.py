"""XVI-P p23 conventions (stage release on the O.1 direction).  Inherits p22; adds the O.1 requirement record, the one-loop
power counting / enlarge-rule check and the P.6 ENTRY inventory (kappa^3 three-point, topology level), the p23 contract
revision (polynomial-domain refusal in dred.py, one delimited block after the p22 block), the EV value check and the
'two-point / QdS' qualifier in the title line."""
from p22_conventions import *  # noqa: F401,F403
import p22_conventions as _Q22

REVISION = "p23"
VERSION_LABEL = "XVI-P p23"
CERT_PREFIX = "P23"
DATE = "2026-10-10"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p23.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p23.json"
CONTRACT_REVISION = ("p23 (p14r contract + disclosed p15/p16/p17/p18 revisions + the p22 contract revision + the DISCLOSED "
                     "p23 contract revision: polynomial-domain refusal for d and Dummy-only internal renames, one "
                     "delimited block appended to code/p5_entry/dred.py; p18 core and p22 block byte-identical)")

# --------------------------------------------------------------- p22 layer in p23
P22_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p22.json"
P22_INDEPENDENT_REPORT_SHA256 = "023e5b83b1eba35d7c27b75841f446cb259580808410dbfb00253ea0122b15f3"
P22_SOURCE_TREE_SHA256 = "1bc6edff6ca0788bb0fee4e8bf259bf8a0c80791f6dd08be77f79e56b492a50c"
P22_SOURCE_ZIP_SHA256 = "ade2fa5c2dac6614c41ae38dc97d7c485975015a134650734d466ea6ffdef76f"
P22_SOURCE_LIST = "archival/p22/p22_source_files.json"
P22_ARCHIVED_RECORDS = {
    "archival/p22/p22_source_files.json": "75fb3bf4dfcbf6ddffe98ad6dae061a85cce8d4b070ca71ad826b544dc3c0111",
    "archival/p22/reference_values_p22.json": "0d55633950c993e905627774d3962285f3bbdc7372208c9975170300601eef72",
    "archival/p22/reproducibility/author_rebuild_report_p22.json":
        "ef5055428a0a550526857094dd0defe7ed00e76ff6ad5b55de4e6ad1451d1b34",
    "archival/p22/reproducibility/independent_rebuild_report_p22.json": P22_INDEPENDENT_REPORT_SHA256,
    "archival/p22/certificates/P22_evanescent.json": "91ea75b7da0d839513611f19665d1008c38fe0c90da326d49008099d1ce4d463",
}
EARNABLE_P23 = _Q22.EARNABLE_P22 + ("O1_requirement_recorded", "one_loop_power_counting_verified",
                                    "P6_entry_inventory", "d_poly_domain_refusal_verified", "EV_values_verified")
HARD_STOPS_P23 = dict(_Q22.HARD_STOPS_P22)
OPEN_PINS_P23 = tuple(_Q22.OPEN_PINS_P22)
P5_STATUS_P23 = _Q22.P5_STATUS_P22
TITLE_QUALIFIER = "P.5 renormalized at one loop kappa^2 for the two-point functions with QdS external legs"

# --------------------------------------------------------------- O.1 (read-only source, verbatim copy pinned)
O1_LEDGER = "provenance/XVI-O/O_quantum_target.json"
O1_LEDGER_SHA256 = "3cd3d1ba491381ba0a73d1677bfed10d3743e0575f61c71c325e626e4a78a645"   # = XVI-O/ledgers/O_quantum_target.json (o70-sync)
P6_ENTRY_E3_GRAPHS = 15
P6_ENTRY_E3_BY_EXTERNAL = {"K,c,h": 2, "c,c,cs": 1, "c,cb,h": 2, "c,phi,phis": 1, "h,h,h": 5, "h,phi,phi": 4}
ONE_POINT_E1_GRAPHS = 3

# --------------------------------------------------------------- EV values checked by the gate (reviewer p22)
EV_EXPECTED = {
    "calibration_rho_from_4D_pair": "1/2", "coefficient_Kc_E2": "-1/16", "coefficient_ccb_SE": "1/8",
    "coefficients_hh_counterterm_sum": {
        "g4_mn gt_rs (p.p)^2": "-7*I/120", "g4_mr gt_ns (p.p)^2": "-I/160", "g4_rs gt_mn (p.p)^2": "-7*I/120",
        "gt_mn gt_rs (p.p)^2": "I/160", "gt_mn p_r p_s (p.p)^1": "7*I/120", "gt_mr gt_ns (p.p)^2": "I/160",
        "gt_mr p_n p_s (p.p)^1": "I/160", "gt_rs p_m p_n (p.p)^1": "7*I/120"},
}

# --------------------------------------------------------------- poly-domain refusal probe (reviewer p22 forms)
POLY_PLANTS_P23 = {
    "rem": "sp.rem(numer(e), d - 4, d)", "resultant": "sp.resultant(numer(e), d - 4, d)",
    "compose": "sp.compose(numer(e), 4, d)", "div": "sp.div(numer(e), d - 4, d)",
    "prem": "sp.prem(numer(e), d - 4, d)", "Poly_shift_as_coeff_add": "Poly(numer(e), d).shift(-4).as_expr().as_coeff_add()",
    "Poly_rem_method": "Poly(numer(e), d).rem(Poly(d - 4, d))", "Matrix_subs_rename": "Matrix([e]).subs(d, y).subs(y, 4)",
    "Matrix_xreplace_rename": "Matrix([e]).xreplace({d: y}).subs(y, 4)",
}

# --------------------------------------------------------------- disclosure (every change vs the p22 zip)
DISCLOSED_REVISIONS_P23 = {
    "code/p5_entry/dred.py": "p23 contract revision: polynomial-domain refusal + Dummy-only internal renames (appended block)",
    "code/p5_calc/contract_registry.py": "p23 block recognised; p22 block pinned byte-identical; p23 revised/added lists",
    "code/p5_calc/release_p21.py": "accepts the p23 registered revisions (contract_registry.P23_REVISED_FILES)",
    "code/p5_calc/release_p22.py": "accepts the registered p23 dred state and p23-disclosed files (pinned by the p23 gate)",
    "code/p5_calc/power_counting.py": "new: O.1 requirement, one-loop power counting, enlarge rule, P.6 entry inventory",
    "code/p5_calc/p23_conventions.py": "new",
    "code/p5_calc/release_p23.py": "new: p23 gate",
    "tests/test_p14.py": "p23 names / status expectations",
    "tests/test_p21.py": "allow-list scan reads p23 sites; status expectations",
    "tests/test_p22.py": "p22 layer record read from certificates/P22_release.json; version label current",
    "tests/test_p23.py": "new",
    "tools/build.py": "p23 stages (power_counting, release_p23), listings, value blocks, archival p22",
    "tools/source_manifest.py": "p23 zip / reference; p22 archive records",
    "tools/rebuild_from_source.py": "p23 reference / certificates / ledgers",
    "README.md": "p23 section; title line with the two-point / QdS qualifier",
    "REBUILD_INSTRUCTIONS.md": "p23",
    "manuscript/body/XVI-P-body.tex": "input of the p23 note",
    "manuscript/notes/P23_O1_scope.tex": "new: p23 note",
    "provenance/XVI-O/O_quantum_target.json": "new: verbatim read-only copy of the XVI-O O.1 ledger (sha pinned)",
}
GENERATED_EXEMPT_P23 = ("reproducibility/reference_values_p23.json", "reproducibility/reference_values_p22.json")
DISCLOSED_PREFIXES_ADDED_P23 = ("archival/p22/",)
P23_PINNED_SHA256 = {   # frozen: exact sha256 of every disclosed file (except p23_conventions itself, README.md, REBUILD_INSTRUCTIONS.md: tree/zip sha only -- their manifest hashes must not appear in a PDF)
    "code/p5_calc/contract_registry.py": "07f36b4f37c0c29e89e2fdc9093ab5b23e04dc32b80a9bd322e83c1af6be3669",
    "code/p5_calc/power_counting.py": "2d80c9d0da4b671ddba820bad820045fc1fe388ecc537e7a79725d82a9b24a75",
    "code/p5_calc/release_p21.py": "6bc5ce80f40ec311a662f078ac5be9e23d752f1fc37d4affefedb24a0d80a0cf",
    "code/p5_calc/release_p22.py": "6a9502c134e7fe55f70e7343e2515b4d66965eb167b606de6a37d8c748fe96a7",
    "code/p5_calc/release_p23.py": "505d5dc04b69e1ef54f3ca4aa0c8c67cf9c54872138c946eccf3a6c437275649",
    "code/p5_entry/dred.py": "24112d9a6584613474e96f538840a9ff6aecbf9ebd588cd890fd38d2e295de5a",
    "manuscript/body/XVI-P-body.tex": "2cf0dc365202b07590275721b152a2c9f17841fd45e05264eb052a0a92bde71b",
    "manuscript/notes/P23_O1_scope.tex": "68a691ebc8f5b3032f0fdae50c0e8c72f46d10e164e8bc44a11805c27e8cd424",
    "provenance/XVI-O/O_quantum_target.json": "3cd3d1ba491381ba0a73d1677bfed10d3743e0575f61c71c325e626e4a78a645",
    "tests/test_p14.py": "d5b2111a8efb60f1abc00c6910fa8ab0f8309bb35543d4fa25f2a4b41d7d4a34",
    "tests/test_p21.py": "4d7edc3f4b5e27c1d1aaa546f745666fc852979208425ee78c7f8d745e2879c8",
    "tests/test_p22.py": "764714b0f185356856811d96b01879933096a53d85c5dcc46e3efd3954341546",
    "tests/test_p23.py": "01486f56765e278a789afbe10273c2e751920bec214daaa592c77016ffc9c5f3",
    "tools/build.py": "8bf2de0e1b583eab4b3bfe46c09393d61c4ecdb5f7cecbd02e68ac73c48630c3",
    "tools/rebuild_from_source.py": "6770523164de112711014b616b0dc62564ce8e13f975705c2f50ba97820c2260",
    "tools/source_manifest.py": "a620ccb1a334c5d43557fe0ec91865b2a60d0d3d83519bd8f38d6444327957fd",
}

# --------------------------------------------------------------- scan allow-lists: reviewed p23 block sites (dred.py)
DECOMPOSE_SITES_REVIEWED = dict(_Q22.DECOMPOSE_SITES_REVIEWED)
DECOMPOSE_SITES_REVIEWED.update({
    "code/p5_entry/dred.py::_install_poly_refusal::args": "the wrappers' *args (call arguments), not an expression tree"})
DECOMPOSE_SITE_COUNTS = dict(_Q22.DECOMPOSE_SITE_COUNTS)
DECOMPOSE_SITE_COUNTS.update({"code/p5_entry/dred.py::_install_poly_refusal::args": 5})
SYMPY_FROM_IMPORT_REVIEWED = dict(_Q22.SYMPY_FROM_IMPORT_REVIEWED)
SYMPY_FROM_IMPORT_REVIEWED.update({
    "code/p5_entry/dred.py::_install_poly_refusal::import sympy as _sympy":
        "p23 guard installation: rebinds the guarded polytools functions in the sympy namespace",
    "code/p5_entry/dred.py::_install_poly_refusal::import sympy.polys.polytools as _pt":
        "p23 guard installation: wraps the polynomial functions / Poly methods that can evaluate d"})
