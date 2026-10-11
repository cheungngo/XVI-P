#!/usr/bin/env python3
"""XVI-P p22 conventions: the 'bigger fronts' release after p21 (user-approved), WITH a disclosed contract rev
  +> ision.

  EV-M2  evanescent components of D11: the provable matching statement (local evanescent poles + exact decoupl
  +> ing of the
         renormalised evanescent remainder on QdS external legs); NOT matched to XVI-O (no counterpart; the g4
  +>  -> ghat and
         g4-kept continuations of the 4D kernel are both refuted).  D11_matching_verified_scope widened accord
  +> ingly.
  EV-CT  p22 CONTRACT REVISION (declared): evanescent counterterms -- h.h gt-operators (D01 + D03 + D11), K'.c
  +>  E2
         (D13), and the ghost-equation partner cb.c SE (Sigma) -- coefficient = -(UV pole).  Checked: sigma_0 
  +> closure
         (h.c, c.b; c.cbs unreachable), projected identity unchanged, remnants (QdS: none; Q4S trace mode: a f
  +> inite
         O(eps) x pole term, disclosed as a scheme convention).  P.5 calculation status -> renormalized (one l
  +> oop,
         kappa^2, two-point functions, MS-bar DRED + p22 evanescent counterterms, QdS external legs).
  G      p22 CONTRACT REVISION: runtime d guard (code/p5_entry/dred.py, one delimited additive block; the p18 
  +> text is
         byte-identical outside it -- contract_registry.dred_revision).  Entry-point guards on subs / xreplace
  +>  /
         replace / evalf(subs) / Poly value + coefficient accessors / coeff / as_independent / as_coeff_expone
  +> nt / series
         / collect / limit / Lambda(d, .) / d == d.  The static allow-list scan is kept as the SECONDARY barri
  +> er.
  K      gate: no prefix exemptions (tools/, manuscript/ included); every added, modified or removed file vs t
  +> he p21
         zip must be listed in DISCLOSED_REVISIONS_P22; earlier-layer notes and added code files are covered.
  T      science text: the p20 'Absolute pin: OPEN' passage is marked inline [superseded in p21].
"""
from __future__ import annotations
from p21_conventions import (ROW_HH, ROW_KC, ROW_1PT, ROWS, HH_EVALUATED, P18_CALC_SHA256,  # noqa: F401
                             P18_DRED_SHA256, RUN_SPECIFIC_KEYS, HARD_STOPS_P21, EARNABLE_P21, OPEN_PINS_P21,
                             INVENTORY_P21, DECOMPOSE_ATTRS, SYMPY_ALIAS_ALLOWED, SYMBOL_MAKERS)
import p21_conventions as _Q21

REVISION = "p22"
VERSION_LABEL = "XVI-P p22"
CERT_PREFIX = "P22"
CONTRACT_REVISION = ("p22 (p14r contract + disclosed p15/p16/p17/p18 revisions + the DISCLOSED p22 contract re
  +> vision: "
                     "evanescent counterterms (EV-CT) and the runtime d guard in code/p5_entry/dred.py)")
DATE = "2026-10-10"
AUTHOR_REPORT = "reproducibility/author_rebuild_report_p22.json"
INDEPENDENT_REPORT_CURRENT = "reproducibility/independent_rebuild_report_p22.json"
P21_INDEPENDENT_REPORT = "reproducibility/independent_rebuild_report_p21.json"      # written by the reviewer;
  +>  never here
P21_INDEPENDENT_REPORT_SHA256 = "8a582b332cd242689c54b1f962dc88270b9592040c0ba432576a505f0e36a60d"
P21_SOURCE_TREE_SHA256 = "b835353ffe16a8ff159e2916fe3efdf2b9d89a4d512e80e9e6da587cecd0fe5e"
P21_SOURCE_ZIP_SHA256 = "a71d6b5203bc3914833db9fd13b9d186bef93d1ae3007b2e4c99fdfce11e0678"
P21_INDEPENDENT_SAME_BOX = True     # disclosed: the p21 independent rebuild ran on the same box
P21_SOURCE_LIST = "archival/p21/p21_source_files.json"
P21_ARCHIVED_RECORDS = {
    "archival/p21/reference_values_p21.json": "96ae946bb9d9c59e7128e3497669e3e9987b046e921f87e7f9a7e425d6aeeb4
  +> 6",
    "archival/p21/reproducibility/author_rebuild_report_p21.json":
        "a5f886ad6ac6b8cff9580236e7c3ddf2ab6d8d1f875173eb092ff01e4a8fb0cf",
    "archival/p21/reproducibility/independent_rebuild_report_p21.json": P21_INDEPENDENT_REPORT_SHA256,
    "archival/p21/p21_source_files.json": "b1f8704b51d1b2b223de6fe83c4956628f19d50682823ef8757af775405778b8",
}
INVENTORY_P22 = INVENTORY_P21
HARD_STOPS_P22 = dict(HARD_STOPS_P21)
EARNABLE_P22 = EARNABLE_P21 + ("evanescent_M2_verified", "evanescent_counterterms_verified", "d_runtime_guard_
  +> verified")
OPEN_PINS_P22 = tuple(OPEN_PINS_P21)
P5_STATUS_P22 = ("renormalized (one loop, kappa^2, two-point functions hh / K'.c / cb.c; MS-bar in DRED with t
  +> he p22 "
                 "evanescent counterterms; external legs in QdS)")

# --------------------------------------------------------------- p21 layer in p22
P21_CONVENTIONS_SHA256 = None        # filled at freeze (tools/p22_pins.py) from the p21 zip file list
# every file added / modified / removed vs the p21 zip, with its reason (K: no prefix exemptions)
DISCLOSED_REVISIONS_P22 = {
    # contract (p22 contract revision)
    "code/p5_entry/dred.py": "CONTRACT REVISION p22: runtime d guard (one delimited additive block; p18 text u
  +> nchanged)",
    # new p22 code
    "code/p5_calc/p22_conventions.py": "new: p22 conventions",
    "code/p5_calc/evanescent.py": "new: EV-M2 and EV-CT (priorities 1, 2)",
    "code/p5_calc/contract_registry.py": "new: registry of the post-p18 contract revision (consulted by layer 
  +> gates)",
    "code/p5_calc/release_p22.py": "new: p22 release gate",
    # earlier-layer gates (disclosed p22 revisions; consult contract_registry)
    "code/p5_calc/release_p18.py": "p22: accept the registered dred.py revision in place of the p17 AST identi
  +> ty",
    "code/p5_calc/release_p19.py": ("p22: contract identity accepts the registered dred.py revision; p18-layer
  +>  pin "
                                    "accepts the registered release_p18.py revision"),
    "code/p5_calc/release_p20.py": ("p22: change log ignores the registered contract revision; p18-layer pin a
  +> ccepts "
                                    "the registered release_p18.py revision"),
    "code/p5_calc/release_p21.py": ("p22: change log ignores the registered contract revision and treats the p
  +> 22 "
                                    "revised files (contract_registry.P22_REVISED_FILES) as disclosed"),
    # tests
    "tests/test_p14.py": "names p21 -> p22",
    "tests/test_p16.py": "the replace(lambda x: x == d, ..) demonstration now RAISES (p22 runtime guard)",
    "tests/test_p17.py": ("g1 scan reviews the p18 contract core of the registered dred revision "
                          "(contract_registry.scan_view; the p22 block is covered by the runtime probe + scan4
  +> )"),
    "tests/test_p18.py": ("h1 scan via contract_registry.scan_view; h3/h5 accept the registered p18+p22-block 
  +> dred state"),
    "tests/test_p19.py": ("i2 scan via contract_registry.scan_view; p18 calc layer accepts the registered p22 
  +> revision "
                          "of release_p18.py (contract_registry.layer_file_ok)"),
    "tests/test_p20.py": ("status / version expectations p22; p21 tree no longer current; scan3 via scan_view;
  +>  p18 calc "
                          "layer via contract_registry.layer_file_ok"),
    "tests/test_p21.py": ("scan allow-lists read from p22_conventions; the power-base subs limitation test now
  +>  asserts the "
                          "p22 fix; status/version expectations p22; p21 layer independent flag not current"),
    "tests/test_p22.py": "new: p22 tests",
    # manuscript
    "manuscript/notes/P20_correction.tex": "inline [superseded in p21] marker on the 'Absolute pin: OPEN' item
  +> ",
    "manuscript/notes/P22_evanescent.tex": "new: p22 note",
    "manuscript/body/XVI-P-body.tex": "input of the p22 note",
    # tools / docs / reproducibility
    "tools/build.py": "p22 build: release_p22 stage, p22 listings, value blocks, generated files",
    "tools/source_manifest.py": "reference file / zip name p22; p21 archive records",
    "tools/rebuild_from_source.py": "p22 reference values, release criteria, archival pins",
    "README.md": "p22 section", "REBUILD_INSTRUCTIONS.md": "p22 instructions",
}
DISCLOSED_PREFIXES_ADDED_P22 = ("archival/p21/",)     # the p21 archive (records pinned in P21_ARCHIVED_RECORD
  +> S)
GENERATED_EXEMPT_P22 = ("reproducibility/reference_values_p22.json",
                        "reproducibility/reference_values_p21.json")   # generated p21 reference, archived und
  +> er archival/p21
DISCLOSED_MANUSCRIPT_REVISIONS_P22 = {
    "manuscript/notes/P20_correction.tex": {
        "p21_sha256": "138c858852906d4daf3ed86d2e48a8d5ee8ef48717514bde00d4ca7151d3e7fb", "revised_in": "p22",
        "change": "inline [superseded in p21] marker on the 'Absolute pin: OPEN' item (reviewer stale_OPEN_tex
  +> t)"},
}
P22_PINNED_SHA256 = {   # frozen: exact sha256 of every disclosed changed/added code/test/tool/note file (p22_
  +> conventions itself, README.md, REBUILD_INSTRUCTIONS.md: tree/zip sha only -- their manifest hashes must n
  +> ot appear in a PDF)
    "code/p5_calc/contract_registry.py": "70367b9df076c582214459f3afedf534aafd528b5fbae0659c588f2e9a1b2c22",
    "code/p5_calc/evanescent.py": "8e5755f435ed822ea2ba033dabc6ec6237a494337e429ef0793d38b9132da7a6",
    "code/p5_calc/release_p18.py": "f2e8743b4902b4304679c68b994dfc9c6df4a0b769827eb2693a72495a4e9c5b",
    "code/p5_calc/release_p19.py": "4d048345270a39a77cc30f71d3bdcbef17fffec6c44c1ac89487135ea3555970",
    "code/p5_calc/release_p20.py": "a1afba60c21c923886e682b960dda8b2619353712517f078c9967ad9c57e4d5f",
    "code/p5_calc/release_p21.py": "be1257870ad2944db009f1fe9f68f4c5cbadcb53f391d64ae881fc6b97330329",
    "code/p5_calc/release_p22.py": "8f6a0a2fd3d572f37a1dfe4bff26a56cbc7d4421fd8bc17572728077a1c2f269",
    "code/p5_entry/dred.py": "1f994759452b9d76eea3cc3a90e02bbb1ed237f9c0865a99d1bc5a2cbe0b08bc",
    "manuscript/body/XVI-P-body.tex": "fadeae094ce611234ef3a15c79826b3b00172fd9759697803d3d68758506629b",
    "manuscript/notes/P20_correction.tex": "b36516c84f6bb1acc5b80b7c384e16c54a0ec2a26af0f4a9a3dc81e98e634ddf",
    "manuscript/notes/P22_evanescent.tex": "49c8ff716c5f916dfcfd773613652cdb1190e226e68256d27ab2d68ddd97345c",
    "tests/test_p14.py": "0b8292eac118aaaa0ac56495f81ed75a92fb6f5bf86deb336343883e483c89a5",
    "tests/test_p16.py": "3abd2bca6d1cb29ef4a1a788e1ba1249daf31035e825bb10228b1aa2f1c29ed3",
    "tests/test_p17.py": "1e542ce116a5c5508bab74761fcd4b591f379840a814895ea7733c3c97ae2028",
    "tests/test_p18.py": "757676b25a71067d4150d0293b512d5d09da97c86686c16b97954ff8ac11e619",
    "tests/test_p19.py": "3578e13b4bfa9d429a551add3c3572672e569baec3517a69098aae158817a60c",
    "tests/test_p20.py": "274d9186979f00056f77ddf7a53e941f7e4e5e2d766a826ea291fe9555a4c668",
    "tests/test_p21.py": "067359ea2fa94e1228d5db1d3f7d7fc4f0af4e0468daa69b74638ccf23e5af0a",
    "tests/test_p22.py": "d8cbebcf34e960a59d718e2b8a3622dcc5f3941f012022cf3abc511d4801f663",
    "tools/build.py": "5e7ed48ee2f6dc5542a9da2579e736928660a947bb3a574da96db15d8e127248",
    "tools/rebuild_from_source.py": "56d7d205739e95574cd86ba820580ea4d39a3863bd008ed7e1ed827b800ab496",
    "tools/source_manifest.py": "46f1ae5f397a3f7e300b9e0679617b95b26a93d1a8e8da3f0eb106b43cc406c7",
}

# --------------------------------------------------------------- scan (secondary barrier): p21 allow-lists + 
  +> p22 guard sites
DECOMPOSE_SITES_REVIEWED = dict(_Q21.DECOMPOSE_SITES_REVIEWED)
DECOMPOSE_SITES_REVIEWED.update({
    "code/p5_entry/dred.py::_pairs_of_subs::args": "the wrapper's *args (subs call arguments), not an expressi
  +> on tree",
    "code/p5_entry/dred.py::_install::args": "the wrappers' *args (call arguments), not an expression tree",
})
DECOMPOSE_SITE_COUNTS = dict(_Q21.DECOMPOSE_SITE_COUNTS)
DECOMPOSE_SITE_COUNTS.update({"code/p5_entry/dred.py::_pairs_of_subs::args": 5, "code/p5_entry/dred.py::_insta
  +> ll::args": 7})
SYMPY_FROM_IMPORT_REVIEWED = dict(_Q21.SYMPY_FROM_IMPORT_REVIEWED)
SYMPY_FROM_IMPORT_REVIEWED.update({
    "code/p5_entry/dred.py::<module>::from sympy.core.basic import Basic as _Basic": "p22 guard: patched entry
  +>  point",
    "code/p5_entry/dred.py::<module>::from sympy.core.expr import Expr as _Expr": "p22 guard: patched entry po
  +> int",
    "code/p5_entry/dred.py::<module>::from sympy.core.evalf import EvalfMixin as _EvalfMixin": "p22 guard",
    "code/p5_entry/dred.py::<module>::from sympy.polys.polytools import Poly as _Poly": "p22 guard",
    "code/p5_entry/dred.py::_install::from sympy.core.basic import Atom as _Atom": "p22 guard",
    "code/p5_entry/dred.py::_install::import sympy as _sp": "p22 guard",
    "code/p5_entry/dred.py::_install::from sympy.core.function import Lambda as _Lambda": "p22 guard",
})
SYMBOL_SITES_REVIEWED = dict(_Q21.SYMBOL_SITES_REVIEWED)
VALUE_CALLS = _Q21.VALUE_CALLS
DVALUE_SITES_REVIEWED = dict(_Q21.DVALUE_SITES_REVIEWED)
DVALUE_SITE_COUNTS = dict(_Q21.DVALUE_SITE_COUNTS)
DALIAS_SITES_REVIEWED = dict(_Q21.DALIAS_SITES_REVIEWED)
COEFF_SITES_REVIEWED = dict(_Q21.COEFF_SITES_REVIEWED)
POLY_GENERATOR_CALL_SITES_REVIEWED = dict(_Q21.POLY_GENERATOR_CALL_SITES_REVIEWED)

# --------------------------------------------------------------- runtime guard (G)
GUARD_PLANTS_P22 = {   # reviewer p21 probe (8 forms x 4 expressions) + p21 VALUE_CALLS + extra; every one mus
  +> t RAISE
    "subs_d": "e.subs(d, 4)", "xreplace_d": "e.xreplace({d: 4})", "list_unpack_alias_then_subs": "D, = [d]; e.
  +> subs(D, 4)",
    "free_symbols_pop_subs": "e.subs([y for y in e.free_symbols if y.name == 'd'][0], 4)",
    "lambda_wrapper_Poly": "(lambda *a: sp.Poly(*a))(sp.expand(e * (d**2 - 1)), d).eval(4)",
    "coeff_extract": "sum(sp.expand(e).coeff(d, k) * 4**k for k in range(5))",
    "dunder_getattribute_eq": "sp.Add(*[4 if y == d else y for y in e.__getattribute__('args')])  (d among arg
  +> s)",
    "subs_power": "e.subs(d**2, 16)", "subs_dict": "e.subs({d: 4})", "subs_list": "e.subs([(d, 4)])",
    "evalf_subs": "e.evalf(subs={d: 4})", "N_subs": "sp.N(e, subs={d: 4})", "Lambda": "sp.Lambda(d, e)(4)",
    "Subs_doit": "sp.Subs(e, d, 4).doit()", "limit": "sp.limit(e, d, 4)", "replace": "e.replace(d, 4)",
    "replace_fn": "e.replace(lambda y: y == d, lambda y: 4)", "as_poly_call": "P.as_poly(d)(4)",
    "all_coeffs": "sp.Poly(P, d).all_coeffs()", "as_expr_values": "sp.Poly(P, d).as_expr(4)",
    "collect": "sp.collect(e, d, evaluate=False)", "as_independent": "e.as_independent(d)",
    "series": "e.series(d, 4, 2)", "rename_then_value": "e.subs(d, sp.Dummy())", "lambdify": "sp.lambdify(d, e
  +> )(4)",
    "getattr_subs": "getattr(e, 'subs')(d, 4)", "methodcaller": "operator.methodcaller('subs', d, 4)(e)",
    "unbound_Basic_subs": "sp.Basic.subs(e, d, 4)",
    "Symbol_new_classmethod": "e.subs(sp.Symbol.__new__(type(d), 'd'), 4)  (reviewer p21: Symbol_new_classmeth
  +> od)",
    "Function_call_d": "sp.Function('f')(e).subs(d, 4)  (reviewer p21: Function_call_d)",
}
RUNTIME_GUARD_RESIDUE_P22 = (
    "NOT runtime-interceptable (code-review matters; the static allow-list scan is the secondary barrier): ide
  +> ntity / "
    "name / type tests in hand-written expression-tree rebuilds (`x is d`, x.name == 'd', isinstance), string 
  +> "
    "round-trips (str(e).replace('d', '4')), low-level polynomial representations (Poly.rep, DMP, polyutils di
  +> ct "
    "builders), and code that disguises its module name as sympy.  Symbol.__new__(Symbol, 'd') yields a PLAIN 
  +> d that "
    "does not match the opaque d (no value is produced); parse_d / assert_opaque_d refuse plain d in loaded da
  +> ta.")
