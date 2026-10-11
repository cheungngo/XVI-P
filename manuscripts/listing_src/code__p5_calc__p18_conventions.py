#!/usr/bin/env python3
"""XVI-P p18 conventions: P.5 calculation, fourth step (D11: discharge of the matching premise M2, evaluation 
  +> of D11
under the declared prescription, the full hh slot D01+D02+D03+D11+D12; p17 reviewer findings H1-H5).

Layering.  p14r contract (code/p5_entry/*)  ->  p15 layer  ->  p16 layer  ->  p17 layer (code/p5_calc/{hh_slot
  +> ,
p17_conventions,release_p17}.py; byte-identical, sha256 below)  ->  p18 layer (code/p5_calc/{d11,p18_conventio
  +> ns,
release_p18}.py, P18_*).  The p18 gate (release_p18.py) runs after the p14r, p15, p16 and p17 gates and requir
  +> es all
four to be accepted.

Disclosed CONTRACT revision in p18 (DISCLOSED_CONTRACT_REVISIONS_P18): code/p5_entry/dred.py documentation onl
  +> y
(H3 stale comment, H5 parse_d(srepr(e)) raises).  No new contract file: no evanescent h.h counterterm is neede
  +> d by the
ch-projected slot (D11 has p_m G_D11 = 0 identically in d; certificates/P18_hh_slot.json).
"""
from __future__ import annotations

REVISION = "p18"
VERSION_LABEL = "XVI-P p18"           # single version variable (manuscript footer is checked against it)
CERT_PREFIX = "P18"
CONTRACT_REVISION = "p18 (p14r contract + disclosed p15/p16/p17/p18 revisions)"
DATE = "2026-10-09"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p18.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p18.json"
P17_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p17.json"      # written by the reviewer;
  +>  never here
P17_INDEPENDENT_REPORT_SHA256 = "92542a2215c24b984e2220f69ac52698d6b09dbb6b860402bbc367d970c176eb"
P17_SOURCE_TREE_SHA256 = "2a5a6317f7322db910c26fb257e589b28aa017df740879194e0ac2eb505ddd92"
P17_SOURCE_ZIP_SHA256 = "7f4f61df9ce9c6483d76fa7b7b024591d6abfbae80ddc3dc0bee387245d25416"
P17_ARCHIVED_RECORDS = {
    "archival/p17/reference_values_p17.json": "d4345c282aee89676ee7d0b077fd8fc94ebd8735cd78499550b2666a0b9103b
  +> 1",
    "archival/p17/reproducibility/author_rebuild_report_p17.json":
        "bd7d8baeabb6337a07234f93dd098b11ab0f95d6ccb640f016d827d952a0bd6f",
    "archival/p17/reproducibility/independent_rebuild_report_p17.json": P17_INDEPENDENT_REPORT_SHA256,
    # per-file sha256 list of the released p17 source-only zip (base of the p18 change log; works source-only)
    "archival/p17/p17_source_files.json": "2b4ccc98c86d0977b71921275b9cc797002ff877e0bf8f466ae86e9ace4cdc42",
}
P17_SOURCE_LIST = "archival/p17/p17_source_files.json"

HH_SLOT_GRAPHS = ("D01", "D03", "D11")            # + D02 = D12 = 0 (P15_batchA.json)
SLOT_ROW = "(S0,Gamma1^[2]) s2 K:K.c"
INVENTORY_P18 = ("D01", "D02", "D03", "D11", "D12", "D13", "D14a", "D14b", "D14c")

# the three ch slots (P13_ch_source_audit surviving rows) and where each input is evaluated
INPUT_EVALUATION_P18 = {
    "D01": "certificates/P16_batchC.json", "D03": "certificates/P16_batchC.json",
    "D02": "certificates/P15_batchA.json", "D12": "certificates/P15_batchA.json",
    "D13": "certificates/P15_D13.json",
    "D14a": "certificates/P15_batchA.json", "D14b": "certificates/P15_batchA.json",
    "D14c": "certificates/P15_batchA.json",
    "D11": "certificates/P18_D11.json",
}

HARD_STOPS_P18 = {
    "projected_defect_computed": "not_earned",
    "projected_identity_verified": "not_earned",
    "projected_restoration_verified": "not_earned",
    "bulk_symmetry_restored": False,
    "symmetry_restored": False,
    "O1_closure": "NOT_CLOSED",
    "insertion_status": "Frozen_negative_obstruction_preserved",
    "XV_B_opened": False,
    "XIV_J_opened": False,
    "Route_B_discharged": False,
    "u_R_c_delta_added": False,
    "XVI_P_registered": False,
}
# flags that p18 may EARN, each only if its certificate says so (release_p18 reads them; never set by hand)
EARNABLE_P18 = ("D11_matching_verified", "D11_evaluated", "quantum_inputs_evaluated")

# p17 layer: byte-identical in p18 (sha256 from XVI-P-p17-source-only.zip; release_p18 recomputes them)
P17_CALC_SHA256 = {
    "code/p5_calc/hh_slot.py": "14330d4b9337773e759fd36262b7bd4653d3cc0b83bed4cdc6dec62b2c216465",
    "code/p5_calc/p17_conventions.py": "a239a2b695e8d58bf8b8405c0ed4a98433da7034b6b255d2477866c5b6db306c",
    "code/p5_calc/release_p17.py": "390b263089aa9e794805030d61d8ed773878083927750272ca4e983f10600d92",
}
P14R_CONTRACT_FILES_CHANGED_IN_P18 = ("code/p5_entry/dred.py",)
NEW_CONTRACT_FILES_P18 = ()                       # no evanescent h.h counterterm file (slot decoupling incl. 
  +> D11)
P17_DRED_SHA256 = "7b0e46c3d0086fce0f7fec01a7d5e33021435e88cb15c99de176683fb65638c8"     # dred.py as released
  +>  in p17
# sha256 of ast.dump of the p17 dred.py with every docstring removed (release_p18.ast_sha; Python-version depe
  +> ndent:
# computed with the build interpreter; the p18 revision must keep it -- comments/docstrings only)
P17_DRED_AST_SHA256 = "8a32857a194bd0de67bc7f529c06f975124b3989c97e04ec344582f6b9a4e6ea"

DISCLOSED_CONTRACT_REVISIONS_P18 = {
    "code/p5_entry/dred.py": {
        "kind": "contract revision (disclosed), p18: COMMENTS/DOCSTRING ONLY (on top of p15 F1, p16 F3, p17 G1
  +> -G3)",
        "finding": "H3/H5, reproducibility/independent_rebuild_report_p17.json",
        "why": ("H3: OpaqueDimension.matches comment named tests/test_p16.py as the scan (now tests/test_p18.p
  +> y); "
                "H5: parse_d(srepr(e)) raises PlainDimensionSymbol (fails closed) but this was not documented"
  +> ),
        "change": "comment/docstring text only; no statement executed by Python changed (AST-equal, tests/test
  +> _p18.py)",
        "rules_R1_R6_changed": False,
        "released_values_affected": False,
        "why_unaffected": ("the module AST without docstrings equals that of the p17 dred.py (tests/test_p18.p
  +> y); "
                           "the P14..P17 certificate content hashes recomputed in p18 equal "
                           "archival/p17/reference_values_p17.json"),
    },
}
DISCLOSED_TEST_REVISIONS_P18 = {    # test files changed vs the p17 zip (release_p18 change log)
    "tests/test_p16.py": ("test_f4_value_block_readback_detects_a_changed_value: the planted mutation is appli
  +> ed to a "
                          "snippet that occurs VERBATIM in the typeset page (the p18 full-slot verdict is long
  +> er than "
                          "the 110-column wrap, so str.replace on the wrapped page was a no-op and the test co
  +> uld not "
                          "plant its mutation). The readback itself was correct (a mutation inside the wrapped
  +>  verdict "
                          "is detected; tests/test_p18.py::test_readback_detects_mutation_inside_wrapped_value
  +> ). One "
                          "line; no assertion weakened."),
    "tests/test_p14.py": ("source-set / zip / reference / author-report names p17 -> p18; generated-prefix lis
  +> t "
                          "extended by P18_* certificates/ledgers and the P18 results table; top-level status 
  +> revision "
                          "p18. (Its quantum_inputs_evaluated assertions read the p14r CONTRACT record "
                          "certificates/P14_release.json and are unchanged.) No assertion weakened."),
    "tests/test_p17.py": ("rs() reads the p17 LAYER record certificates/P17_release.json (the top-level "
                          "RELEASE_STATUS.json is now the p18 status); the version-label test checks that the 
  +> build's "
                          "CURRENT label is 'XVI-P <current revision>'; the p17 layer's own independent flag (
  +> recomputed "
                          "by release_p17.py against the CURRENT tree) may be False (the reviewer's live p17 r
  +> eport is "
                          "bound to the p17 tree) or pending (source-only rebuild); the p17 PASS itself is rec
  +> orded by "
                          "release_p18 as independent_rebuild_passed_p17. Three lines; all other p17 assertion
  +> s "
                          "unchanged."),
}
# H1/H3: package call sites of sympify / S (and aliases) with a non-literal argument, reviewed.  Two kinds (H3
  +> : the
# p17 header said "never a stored string", which was inaccurate for 7 entries): (a) in-process sympy objects, 
  +> and (b)
# STORED STRINGS that provably contain no d (export prefactor strings -- kappa only, checked by tests -- and t
  +> he frozen
# p13 classical srepr export).  Every entry says which.  Any new site fails the scan (tests/test_p18.py).
PARSE_SITES_REVIEWED = {
    'code/p5_calc/batchA.py::evaluate::sp.sympify(body["prefactor"], locals={"kappa": KAPPA})':
        'export prefactor STRING (kappa only; tests/test_p17.py checks every exported prefactor is d-free)',
    'code/p5_calc/batchC.py::regen_equals_export::sp.sympify(body["prefactor"], locals={"kappa": KAPPA})':
        'export prefactor STRING (kappa only; tests/test_p17.py checks every exported prefactor is d-free)',
    'code/p5_calc/batchC.py::evaluate_graph::sp.sympify(body["prefactor"], locals={"kappa": KAPPA})':
        'export prefactor STRING (kappa only; tests/test_p17.py checks every exported prefactor is d-free)',
    'code/p5_calc/batchC.py::main::sp.sympify(b13["prefactor"], locals={"kappa": KAPPA})':
        'export prefactor STRING (kappa only; tests/test_p17.py checks every exported prefactor is d-free)',
    'code/p5_calc/d13.py::route1::sp.sympify(body["prefactor"], locals={"kappa": sp.Symbol("kappa")})':
        'export prefactor STRING (kappa only; tests/test_p17.py checks every exported prefactor is d-free)',
    'code/p5_entry/hessian_route.py::_export_side::sp.sympify(body["prefactor"], locals={"kappa": F.KAPPA})':
        'export prefactor STRING (kappa only; tests/test_p17.py checks every exported prefactor is d-free)',
    'code/p5_calc/batchC.py::pole_in_hh_basis::sp.sympify(sol[0].get(z, z))':
        'argument is a sympy object computed in-process (never a stored string) (sympy.solve output)',
    'code/p5_calc/batchC.py::mutations::sp.sympify(a0)':
        'argument is a sympy object computed in-process (never a stored string) (A(d) of the evaluation; the p
  +> remature_d4 mutation must raise: certificate shows rejected=True)',
    'code/p5_calc/batchC.py::main::sp.sympify(v)':
        'argument is a sympy object computed in-process (never a stored string) (A(d) values; R5_d_retained ch
  +> eck)',
    'code/p5_calc/d13.py::exact_fit::sp.sympify(a)':
        'argument is a sympy object computed in-process (never a stored string) (matrix entries)',
    'code/p5_calc/d13.py::expand_coeff::sp.sympify(c)':
        'argument is a sympy object computed in-process (never a stored string) (fitted coefficient)',
    'code/p5_calc/d13.py::mutations::sp.sympify(v)':
        'argument is a sympy object computed in-process (never a stored string) (fitted values)',
    'code/p5_calc/d13.py::_opaque_d_refuses::sp.sympify(fit1["T2"])':
        'argument is a sympy object computed in-process (never a stored string) (fit result; the probe must ra
  +> ise: certificate shows it does)',
    'code/p5_calc/d13.py::main::sp.sympify(v)':
        'argument is a sympy object computed in-process (never a stored string) (fit values; R5_d_retained che
  +> ck)',
    'code/p5_calc/integrals.py::fp_two_point::sp.sympify(poly)':
        'argument is a sympy object computed in-process (never a stored string) (numerator polynomial)',
    'code/p5_calc/integrals.py::realize::sp.sympify(expr)':
        'argument is a sympy object computed in-process (never a stored string)',
    'code/p5_calc/release_p17.py::f3_hardening::sp.sympify(str(e))':
        "deliberate G2 hazard probe (the plain Symbol('d') must be caught by assert_opaque_d)",
    'code/p5_entry/dred.py::assert_opaque_d::sp.sympify(expr)':
        'argument is a sympy object computed in-process (never a stored string) (the checker itself)',
    'code/p5_entry/dred.py::parse_d::sp.sympify(text, locals=loc)':
        "the guarded loader itself (loc['d'] is the opaque d; the result is checked by assert_opaque_d)",
    'code/p5_entry/dred.py::substitute_d::sp.sympify(expr)':
        'argument is a sympy object computed in-process (never a stored string) (the authorised substitution)'
  +> ,
    'code/p5_entry/dred.py::substitute_d::sp.sympify(value)':
        'numeric substitution value (4 or 4 - 2 eps)',
    'code/p5_entry/dred.py::__init__::sp.sympify(trace_hat)':
        'display-only numeric trace (Rules(trace_hat=...), refused unless display_only)',
    'code/p5_entry/release_p14.py::classical_block::sp.sympify(txt)':
        'frozen p13 classical export ell*_generating_polynomial.srepr (4D, contains no d); hashed only',
    'code/p5_entry/shadow.py::even::sp.sympify(x)':
        'argument is a sympy object computed in-process (never a stored string) (scalar coefficient)',
}
RUN_SPECIFIC_KEYS = ("reproducibility", "author_rebuild_passed", "independent_rebuild_passed",
                     "live_report_identical_to_archived", "live_report_present", "archived_zip_sha256_ok",
                     "list_equals_archived_zip")
PHASE_CONVENTION_G6 = (
    "Overall phase (G6).  Every graph is exported as G = kappa^2 N_eps Ghat with N_eps = i S_eps/(16 pi^2) and
  +>  "
    "Ghat = -i * prefactor/kappa^2 * int N/(D1 D2).  For D01 (export prefactor kappa^2/2) and D03 "
    "(prefactor -kappa^2, closed ghost loop) the prefactor is real, so A(d) carries an overall factor I; for D
  +> 13 the "
    "exported prefactor is I*kappa^2, so A(d) is real.  The relative phase between graphs of the same slot is 
  +> fixed by "
    "the common -i and the real export prefactors (D01 vs D03: real ratio); it is checked by the exact cancell
  +> ation of "
    "the summed hh slot and by the rejected mutation M1 (relative sign).  Physical overall phase: not asserted
  +> .")
