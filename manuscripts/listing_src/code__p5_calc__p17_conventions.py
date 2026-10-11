#!/usr/bin/env python3
"""XVI-P p17 conventions: P.5 calculation, third step (D01/D03 evanescent poles vs the ch-projected slot;
p16 reviewer findings G1-G6).

Layering.  p14r contract (code/p5_entry/*)  ->  p15 layer (byte-identical; P15_CALC_SHA256 in p16_conventions)
  +>   ->
p16 layer (code/p5_calc/{covariant,batchC,e2_evanescent,p16_conventions,release_p16}.py; byte-identical, sha25
  +> 6
below)  ->  p17 layer (code/p5_calc/{hh_slot,p17_conventions,release_p17}.py, P17_*).  The p17 gate (release_p
  +> 17.py)
runs after the p14r, p15 and p16 gates and requires all three to be accepted.

Disclosed CONTRACT revision in p17 (DISCLOSED_CONTRACT_REVISIONS_P17): code/p5_entry/dred.py only -- the guard
  +> ed
string loader parse_d / assert_opaque_d (G2) and corrected guard-coverage wording (G1, G3), on top of the p15 
  +> F1 and
p16 F3 revisions.  NO evanescent h.h counterterm is added: the D01/D03 evanescent poles decouple from the
ch-projected slot as the SUM D01 + D03 (proof in certificates/P17_hh_slot.json); no new contract file.
"""
from __future__ import annotations

REVISION = "p17"
VERSION_LABEL = "XVI-P p17"           # single version variable (manuscript footer is checked against it)
CERT_PREFIX = "P17"
CONTRACT_REVISION = "p17 (p14r contract + disclosed p15/p16/p17 revisions)"
DATE = "2026-10-08"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p17.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p17.json"
P16_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p16.json"      # written by the reviewer;
  +>  never here
P16_INDEPENDENT_REPORT_SHA256 = "1a8861964afe7ae4d4b38aaae5381230d8cda82610c51ef2b7919ebd6e326843"
P16_SOURCE_TREE_SHA256 = "90b4a6659cddd341436a59d285a56eb14bdd575bb56e69faf4ba75be4d7b549e"
P16_SOURCE_ZIP_SHA256 = "56d5887daa7a96dcc7cf2f70c6735e802125c9b19a33ac17a3ef975e330fef57"
P16_ARCHIVED_RECORDS = {
    "archival/p16/reference_values_p16.json": "a1fda1e67a4a0033014f40b8bdac57b4daacfa507588e0765bb7139587b053d
  +> 9",
    "archival/p16/reproducibility/author_rebuild_report_p16.json":
        "b4f9bcf38244eb4f51d1ebbba335caf20c1f6cc405b7fca90f174808fa02691d",
    "archival/p16/reproducibility/independent_rebuild_report_p16.json": P16_INDEPENDENT_REPORT_SHA256,
    # per-file sha256 list of the released p16 source-only zip (base of the p17 change log; works source-only)
    "archival/p16/p16_source_files.json": "3e0412c82d161de998eb7bcdcb16fd01b608a6bcc48cc72d18409e2606715de8",
}
P16_SOURCE_LIST = "archival/p16/p16_source_files.json"

HH_SLOT_GRAPHS = ("D01", "D03")
SLOT_ROW = "(S0,Gamma1^[2]) s2 K:K.c"
NOT_EVALUATED_P17 = ("D11",)                       # M2 undischarged

HARD_STOPS_P17 = {
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

# p16 layer: byte-identical in p17 (sha256 from XVI-P-p16-source-only.zip; release_p17 recomputes them)
P16_CALC_SHA256 = {
    "code/p5_calc/covariant.py": "71976d189280ac49a4513b8b0e6503d69930a28a4d5e991dee3f1bdb63cbf817",
    "code/p5_calc/batchC.py": "017154a961ee2539ffb038dc8c60107e6bf9a922e340e326abc3bb82cde6574c",
    "code/p5_calc/e2_evanescent.py": "2027b5ea9c29a89ca5c6fd74bd6507999415ba56939f2cf661f9b3505d405ea4",
    "code/p5_calc/p16_conventions.py": "915fd26ea2d59313b9bd20208a6b360bb29809a4a9487fb5f912c49f917e0f71",
    "code/p5_calc/release_p16.py": "b016c1c5833970e0c891c55aaf6f318d449a5ab7d4c79819fb12b3f8cfd60736",
}
P14R_CONTRACT_FILES_CHANGED_IN_P17 = ("code/p5_entry/dred.py",)
NEW_CONTRACT_FILES_P17 = ()                       # no evanescent h.h counterterm file (decoupling proven)
P16_DRED_SHA256 = "57f6159aa8946f5a69781cf098227489fa07b66fd150fc6c58f8489df064a725"     # dred.py as released
  +>  in p16

DISCLOSED_CONTRACT_REVISIONS_P17 = {
    "code/p5_entry/dred.py": {
        "kind": "contract revision (disclosed), p17 (on top of the p15 F1 and p16 F3 revisions)",
        "finding": "G1/G2/G3, reproducibility/independent_rebuild_report_p16.json",
        "why": ("G2: sympify of a stored string yields a plain Symbol('d') that is not the opaque d (subs/has 
  +> against "
                "dred.d then silently do nothing); G1/G3: the p16 docstring/disclosure overstated the coverage
  +>  of the "
                "guard and of the static scan"),
        "change": ("new guarded loader dred.parse_d(text) (locals {'d': opaque d}; refuses a result with a pla
  +> in "
                   "symbol named d), dred.assert_opaque_d(expr) and exception PlainDimensionSymbol; docstring 
  +> now "
                   "states exactly what the runtime guard refuses and what it does not (Wild-pattern match, C/
  +> Fortran "
                   "printers); unhookable value paths (replace with ANY function query, string round-trips via
  +>  "
                   "sympify/S/parse_expr/eval/exec, srepr+eval, Poly(..).eval, e.func(*args) rebuilds) are exc
  +> luded "
                   "by the extended static AST scan (tests/test_p17.py), a pattern check, not a proof"),
        "rules_R1_R6_changed": False,
        "released_values_affected": False,
        "why_unaffected": ("only functions were added (no existing code path changed); the P14/P15/P16 certifi
  +> cate "
                           "content hashes recomputed in p17 equal those of archival/p16/reference_values_p16.
  +> json "
                           "(tests/test_p17.py)"),
    },
}
DISCLOSED_TEST_REVISIONS_P17 = {    # test files changed vs the p16 zip (release_p17 change log)
    "tests/test_p14.py": ("source-set / zip / reference names p16 -> p17 (SM.ZIP_NAME, SM.REFERENCE_FILE, auth
  +> or report "
                          "path, resumed-build placeholder zip); generated-prefix list extended by P17_* certi
  +> ficates/"
                          "ledgers and the P17 results table; top-level status revision p17. No assertion weak
  +> ened."),
    "tests/test_p16.py": ("rs() reads the p16 LAYER record certificates/P16_release.json (the top-level "
                          "RELEASE_STATUS.json is now the p17 status); the footer test checks that the build's
  +>  CURRENT "
                          "label is 'XVI-P <current revision>' (no longer equal to the p16 label); the p16 lay
  +> er's own "
                          "independent flag may be False (the live p16 report is bound to the p16 tree) or pen
  +> ding. "
                          "Three lines; all other p16 assertions unchanged."),
}
# G1: package call sites of sympify / S with a non-literal argument, reviewed: each receives a sympy object (n
  +> ever a
# stored string) and would FAIL CLOSED on a string through the downstream opaque-d checks; any new site fails 
  +> the scan.
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
