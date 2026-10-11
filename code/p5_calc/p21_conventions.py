#!/usr/bin/env python3
"""XVI-P p21 conventions: small release from p20 (no scope expansion), from the p20 independent-rebuild findings.

  A  absolute D11 pin: sign and magnitude of the D11 pole derived from 1/2 Tr ln (minimal scalar loop) under the
     package's declared conventions (G = Gamma^(2); N_eps = i S_eps/(16 pi^2) and the +1/eps bubble pole fix the Wick
     direction; g = eta + kappa h; eta = (+,-,-,-)) and compared with the heat-kernel a_2 = C^2/120 + R^2/72: exact
     equality, both spins (d11_pin.absolute_pin; p20 had it OPEN).  Mutations x2 and sign flip detected.
  G  gate: top-level *_pin_status keys checked against the nested statuses; release_p20 run standalone re-checks the
     p18 layer (quantum_inputs_evaluated) and the graph inventory instead of trusting the P19 layer record.
  S  d-evaluation scan: the enumerated pattern list (test_p16 .. test_p20) is complemented by an ALLOW-LIST scan
     (tests/test_p21.py): expression-tree decomposition, sympy callable aliases, and dynamic symbol names are refused
     everywhere except at reviewed sites listed below, plus a RUNTIME check that stored exact-d amplitudes re-parse
     with the opaque d and reproduce their poles only through substitute_d.  Still a check, not a proof.
  D  disclosure: the p20 edit of manuscript/notes/P19_defect.tex is listed (DISCLOSED_MANUSCRIPT_REVISIONS); the
     reference key /p19/change_log_vs_p18 is renamed (it was recomputed on the current tree, not the p19 release log).

Layering.  ... -> p19 layer -> p20 layer (p20_conventions.py byte-identical; d11_pin.py and release_p20.py DISCLOSED
p21 revisions) -> p21 layer (code/p5_calc/{p21_conventions,release_p21}.py, P21_*).  No contract revision.
"""
from __future__ import annotations
from p20_conventions import (ROW_HH, ROW_KC, ROW_1PT, ROWS, HH_EVALUATED, P18_CALC_SHA256,  # noqa: F401
                             P18_DRED_SHA256, RUN_SPECIFIC_KEYS, HARD_STOPS_P20, EARNABLE_P20, OPEN_PINS_P20)
from p20_conventions import COEFF_SITES_REVIEWED as _C20, POLY_GENERATOR_CALL_SITES_REVIEWED as _G20

REVISION = "p21"
VERSION_LABEL = "XVI-P p21"
CERT_PREFIX = "P21"
CONTRACT_REVISION = "p21 (p14r contract + disclosed p15/p16/p17/p18 revisions; none in p19, p20 or p21)"
DATE = "2026-10-09"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p21.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p21.json"
P20_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p20.json"      # written by the reviewer; never here
P20_INDEPENDENT_REPORT_SHA256 = "e8f358f9c4f13c76693968211b49e04d546a0bb3a4c0ab4b1a0e485f62595389"
P20_SOURCE_TREE_SHA256 = "2c0aa1533b5a64d65f9169cc510ea3f0761c9471f9601cdec6973a2aa8d45700"
P20_SOURCE_ZIP_SHA256 = "ca32ce018933f12d1a623217d6a98d647817360dd12211e2e9469cf850a63bb2"
P20_INDEPENDENT_SAME_BOX = True     # disclosed: the p20 independent rebuild ran on the same box
P20_ARCHIVED_RECORDS = {
    "archival/p20/reference_values_p20.json": "4877f5dedc84e6dc07fdc9a72077d3098308bb95c168cba36cafdda23d719e04",
    "archival/p20/reproducibility/author_rebuild_report_p20.json":
        "686e2c9c7835e3d4331cf8bcb0c3176661d1e7bfbb146a19bbca4d3135856ac0",
    "archival/p20/reproducibility/independent_rebuild_report_p20.json": P20_INDEPENDENT_REPORT_SHA256,
    "archival/p20/p20_source_files.json": "8031db7fb5fd4832affbc5721a104af554ad9404b665bd7634a11b441d6d64cc",
}
P20_SOURCE_LIST = "archival/p20/p20_source_files.json"
INVENTORY_P21 = ("D01", "D02", "D03", "D11", "D12", "D13", "D14a", "D14b", "D14c")
HARD_STOPS_P21 = dict(HARD_STOPS_P20)
EARNABLE_P21 = EARNABLE_P20 + ("D11_absolute_pin_verified",)
OPEN_PINS_P21 = tuple(x for x in OPEN_PINS_P20 if not x.startswith("D11_absolute"))

# p20 layer in p21: p20_conventions.py byte-identical; d11_pin.py, release_p20.py DISCLOSED revisions
P20_CONVENTIONS_SHA256 = "325a7b296d7fc50ea06dae2ebfd6735be14bbd7907f328d435420c1348bf901b"
P20_RELEASED_SHA256 = {
    "code/p5_calc/d11_pin.py": "a31b718a36da390ef8814d400c36f698711142302a86d6f7e852a4e5b7142ae8",
    "code/p5_calc/release_p20.py": "034a6eba47c216b34ac49e7fc9b67d9e07dc0dab0c592b3e335ef10e36eb9fd2",
}
DISCLOSED_P20_LAYER_REVISIONS_P21 = {
    "code/p5_calc/d11_pin.py": ("absolute_pin(): sign and magnitude derived from 1/2 Tr ln under the declared "
                                "conventions (Minkowski quadratic forms curvature_forms_eta); absolute pin PASS; "
                                "mutations x2 and sign flip; top-level absolute_pin_status from the derivation"),
    "code/p5_calc/release_p20.py": ("absolute pin PASS required; top-level / nested status consistency; standalone "
                                    "run re-checks the p18 layer (q earned) and the graph inventory; claim texts"),
}
# p20 reviewer finding P19_note_edit_disclosure: manuscript edits of earlier-layer notes are disclosed here
DISCLOSED_MANUSCRIPT_REVISIONS = {
    "manuscript/notes/P19_defect.tex": {
        "p19_sha256": "04b974b5ea742c6885f3d694ccad6bda7908105c0a23bf483e96bc113d90bbc8",
        "p20_sha256": "1c71a71a48ce9c1749bd2164a0f720a3589f2d679877cfd04309d69670e5dfa8",
        "revised_in": "p20",
        "change": ("K1 paragraph retracted/rewritten (Grassmann orientation erratum), restoration definition REDEFINED, "
                   "J1 wording, blind-spot text; marked inline [corrected in p20] / [REDEFINED in p20]; unchanged in "
                   "p21")},
}
NEW_CONTRACT_FILES_P21 = ()
DISCLOSED_CONTRACT_REVISIONS_P21 = {}
DISCLOSED_TEST_REVISIONS_P21 = {
    "tests/test_p14.py": "names p20 -> p21; generated prefixes P21_",
    "tests/test_p19.py": "reviewed coefficient sites read from p21_conventions (adds the d11_pin Minkowski form site)",
    "tests/test_p20.py": ("D11 pin tests: absolute pin PASS (p21) instead of OPEN; gate mutations on the p21 checks; "
                          "reviewed sites from p21_conventions; status/version expectations p21"),
}
COEFF_SITES_REVIEWED = dict(_C20)
COEFF_SITES_REVIEWED.update({
    "code/p5_calc/d11_pin.py::curvature_forms_eta::sp.Poly(sp.expand(f - a * q2 - b * q0), *gens).coeffs()":
        "generators: metric perturbation symbols h_ab (no d anywhere in d11_pin)",
})
POLY_GENERATOR_CALL_SITES_REVIEWED = dict(_G20)

# ---------------------------------------------------------------------------------- allow-list scan (S, p21)
# attributes / helpers that decompose a sympy expression tree (rebuild paths with no hook in the opaque d)
DECOMPOSE_ATTRS = ("args", "func", "make_args", "as_ordered_terms", "as_ordered_factors", "as_coefficients_dict",
                   "as_coeff_add", "as_coeff_mul", "as_coeff_Add", "as_coeff_Mul", "as_independent", "as_two_terms",
                   "as_numer_denom", "as_powers_dict", "as_terms", "as_content_primitive", "as_base_exp",
                   "as_coeff_exponent", "preorder_traversal", "postorder_traversal", "iter_args", "_args",
                   "as_expr_dict")
# reviewed sites  file::function::source-segment -> reason (count must match exactly)
DECOMPOSE_SITES_REVIEWED = {
    "code/p5_calc/batchA.py::evaluate::sp.Add.make_args":
        "iterates the mass-regulator pole terms to read their m2 degree (sp.degree); no expression is rebuilt",
    "code/p5_entry/counterterm_domain.py::two_point_vector::sp.Add.make_args":
        "terms of a d-free momentum polynomial -> monomial coordinates (read only)",
    "code/p5_entry/counterterm_domain.py::two_point_vector::t.as_independent":
        "split numeric coefficient / momentum monomial (read only; no d)",
    "code/p5_entry/feynman.py::from_sympy::sp.Add.make_args": "conversion into the frozen sparse polynomial type",
    "code/p5_entry/feynman.py::from_sympy::t.as_independent": "conversion into the frozen sparse polynomial type",
    "code/p5_entry/feynman.py::ell_terms::sp.Add.make_args": "loop-momentum term listing (frozen contract, p14r)",
    "code/p5_entry/feynman.py::ell_terms::t.as_coeff_Mul": "loop-momentum term listing (frozen contract, p14r)",
    "code/p5_entry/quantum_object.py::patterns::sp.Add.make_args": "field-content pattern listing (no d)",
    "code/p5_entry/quantum_object.py::patterns::t.as_powers_dict": "field-content pattern listing (no d)",
    "code/p5_entry/quantum_object.py::b_elimination::sp.Add.make_args": "term counting / degree filter (read only)",
    "code/p5_entry/feynman.py::from_sympy::rest.as_powers_dict": "monomial exponents for the frozen sparse type",
    "code/p5_entry/feynman.py::ell_terms::rest.as_powers_dict": "monomial exponents (frozen contract, p14r)",
}
DECOMPOSE_SITE_COUNTS = {"code/p5_entry/quantum_object.py::b_elimination::sp.Add.make_args": 3}
# sympy attributes that may be bound to a module-level / local alias (constants and two special functions)
SYMPY_ALIAS_ALLOWED = ("I", "pi", "E", "oo", "EulerGamma", "gamma", "rf")
# from-imports out of sympy submodules that were reviewed (no alias)
SYMPY_FROM_IMPORT_REVIEWED = {
    "code/p5_calc/covariant.py::covariant_fit::from sympy.polys.matrices import DomainMatrix":
        "exact rational linear algebra for the covariant fit (numbers only; no d)",
}
# symbol constructors: name must be a literal; non-literal names only at reviewed sites
SYMBOL_MAKERS = ("Symbol", "symbols", "Dummy", "Wild", "var")
SYMBOL_SITES_REVIEWED = {
    "code/p5_calc/release_p17.py::f3_hardening::sp.Symbol(\"d\")": (
        "deliberate PLAIN d in the F3 hardening demonstration (shows that the plain symbol is refused by "
        "assert_opaque_d / parse_d); never enters a value path"),
    "code/p5_entry/dred.py::dot::sp.Symbol(f\"{x}.{y}\")": "contraction symbols 'x.y' (always contain '.', never d)",
    "code/p5_calc/batchA.py::_poly::sp.Symbol(v)": "v ranges over stored monomial names l0..l3, p0..p3",
    "code/p5_calc/batchC.py::count_quadratic_component_terms::sp.Symbol(v)": "v startswith 'p' (momentum components)",
    "code/p5_calc/d13.py::route1::sp.Symbol(v)": "v startswith 'p' (momentum components)",
    "code/p5_entry/dred.py::lift_reduce_polynomial::sp.Symbol(v)": "v startswith 'p' (momentum components)",
}

# (d) p21 runtime finding: value calls that mention d are refused statically except at reviewed demonstration sites
VALUE_CALLS = ("subs", "evalf", "N", "n", "limit", "Lambda", "Subs", "doit", "lambdify", "series", "nsimplify")
DVALUE_SITES_REVIEWED = {        # each is an EXPECT-TO-RAISE demonstration of the R5 guard, never a value path
    "code/p5_calc/batchC.py::mutations::sp.sympify(a0).subs(d, 4)": "M3 premature-d4 demo (rejected recorded)",
    "code/p5_calc/d11.py::d11_mutations::a0.subs(d, 4)": "premature-d4 demo (rejected recorded)",
    'code/p5_calc/d13.py::_opaque_d_refuses::sp.sympify(fit1["T2"]).subs(d, 4)': "R5 safeguard demo",
    "code/p5_calc/release_p16.py::f3_hardening::sp.lambdify(d, e)": "F3 guard demo",
    "code/p5_calc/release_p16.py::f3_hardening::e.subs(d, 4)": "F3 guard demo",
    "code/p5_calc/release_p16.py::f3_hardening::e.evalf(subs={d: 4})": "F3 guard demo",
    "code/p5_calc/release_p17.py::f3_hardening::sp.lambdify(d, e)": "F3/G2 guard demo",
    "code/p5_calc/release_p17.py::f3_hardening::e.subs(d, 4)": "F3/G2 guard demo",
    "code/p5_calc/release_p17.py::f3_hardening::dred.parse_d(str(e)).subs(d, 4)": "G2 loader demo",
}
DALIAS_SITES_REVIEWED = {
    'code/p5_entry/dred.py::parse_d::loc["d"] = d': "the guarded loader binds the OPAQUE d as the parse local",
}
DVALUE_SITE_COUNTS = {}
RUNTIME_GUARD_LIMITATION_P21 = (
    "dred.OpaqueDimension does not intercept expr.subs(d, v) when d occurs only as a power base (e.g. 1/(d**2 - 1)): "
    "sympy's Pow substitution matches the base without calling the symbol's _subs.  Found by the p21 runtime check; "
    "contract (dred.py) NOT changed in p21 (no contract revision; out of scope).  Mitigation: static allow-list rule "
    "(d) refuses every subs/evalf/N/limit/Lambda/... call mentioning d and every rebinding of d outside reviewed "
    "demonstration sites; released premature-d4 demonstrations (P16_batchC, P18_D11) used components that raise.")
