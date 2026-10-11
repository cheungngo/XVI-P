"""XVI-P p18 tests: M2 discharge (route B recomputed covariantly here, independently of d11.py), D11 evaluatio
  +> n, the
full hh slot (seven external assignments incl. c hat / h tilde, H2), the transverse coordinates, the inventory
  +>  behind
quantum_inputs_evaluated, H1 extended static scan (planted violations), H3/H5 dred documentation revision (AST
unchanged), p18 status / hard stops / p17 independent record, change log, p18 gate mutations."""
from __future__ import annotations
import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
for p in ("code/p5_calc", "code/p5_entry", "code/classical", "tools"):
    sys.path.insert(0, str(ROOT / p))
import contract_registry as CR  # p22 (disclosed): registered contract revision
import p18_conventions as QC  # noqa: E402
import p17_conventions as Q17  # noqa: E402
import p16_conventions as Q16  # noqa: E402
import p15_conventions as Q15  # noqa: E402
import dred as DR  # noqa: E402

CERT = ROOT / "certificates"
PKG = ("code/p5_calc", "code/p5_entry")
I = sp.I


def cj(name):
    return json.loads((CERT / name).read_text())


def rs():
    # p19: the p18 LAYER record (the top-level RELEASE_STATUS.json is the p19 status)
    return json.loads((CERT / "P18_release.json").read_text())


def P(text):
    return DR.parse_d(text.replace("p.p", "pp"), {"I": sp.I})


def Z(text):
    """certificate coordinate string (no d) -> number"""
    return DR.parse_d(text, {"I": sp.I})


# ================================================================ H1: extended static scan (pattern check, no
  +> t a proof)
FORBIDDEN_NAMES = {"eval", "exec", "parse_expr", "lambdify", "ufuncify", "autowrap", "all_coeffs"}
PROBE_FUNCTIONS = {"f3_hardening"}         # release_p16 / release_p17 guard probes (deliberate hazards, must 
  +> raise)
PARSERS = {"sympify", "S", "parse_expr"}
SYMBOL_MAKERS = {"Symbol", "symbols", "Dummy", "var"}
HAZARD_ATTRS = {"subs", "xreplace", "replace", "evalf", "n", "eval", "func", "as_poly", "all_coeffs", "doit",
                "rewrite", "__class__", "sympify"}
OPAQUE_D_VALUES = ("d", "dred.d", "DR.d")


def _name(f):
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None


def _src(src, node):
    return ast.get_source_segment(src, node) or ""


def scan(path, root=ROOT):
    """AST pattern scan for value paths the runtime guard cannot hook (p17 patterns + H1).  Returns (violation
  +> s,
    parse_sites).  violations: builtin eval/exec, parse_expr, lambdify/ufuncify/autowrap, any `.eval(` call,
    `.replace(` with a non-string first argument, `.func(` rebuilds; H1: a call OF a call to Poly/as_poly
    (Poly(e, d)(4), e.as_poly(d)(4)), all_coeffs (Horner evaluation), type(x)(..) and x.__class__(..) rebuilds
  +> ,
    getattr with a non-literal or hazardous attribute name, aliased import/assignment of sympify/S/parse_expr,
    sympify/S locals whose 'd' value is not the opaque d, plain Symbol('d')/symbols('d')/Dummy('d') creation.
    parse_sites: every sympify / S call without a 'd' local (must be on the reviewed list)."""
    src = path.read_text()
    tree = ast.parse(src)
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.name
    bad, sites = [], []

    def flag(node, what):
        bad.append(f"{rel}:{node.lineno}:{what}")

    def visit(node, fn=None):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = node.name
        probe = fn in PROBE_FUNCTIONS
        if isinstance(node, ast.ImportFrom) and not probe:
            for a in node.names:
                if a.name in PARSERS and a.asname and a.asname != a.name:
                    flag(node, f"aliased import {a.name} as {a.asname}")
        if isinstance(node, ast.Assign) and not probe:
            v = node.value
            if _name(v) in PARSERS and isinstance(v, (ast.Attribute, ast.Name)):
                flag(node, f"alias assignment of {_name(v)}")
        if isinstance(node, ast.Call) and not probe:
            f = node.func
            name = _name(f)
            if name in FORBIDDEN_NAMES:
                flag(node, name)
            if name == "replace" and isinstance(f, ast.Attribute) and node.args:
                a = node.args[0]
                if not (isinstance(a, ast.Constant) and isinstance(a.value, str)):
                    flag(node, "replace(non-literal)")
            if name == "func" and isinstance(f, ast.Attribute):
                flag(node, ".func(rebuild)")
            if isinstance(f, ast.Call) and _name(f.func) in ("Poly", "as_poly", "poly", "type"):
                flag(node, f"{_name(f.func)}(..)(call)")
            if name == "__class__" and isinstance(f, ast.Attribute):
                flag(node, "__class__(rebuild)")
            if name == "getattr":
                at = node.args[1] if len(node.args) > 1 else None
                if not (isinstance(at, ast.Constant) and isinstance(at.value, str)) or at.value in HAZARD_ATTR
  +> S:
                    flag(node, "getattr(indirection)")
            if name in SYMBOL_MAKERS and node.args:
                a = node.args[0]
                if isinstance(a, ast.Constant) and isinstance(a.value, str) and "d" in a.value.replace(",", " 
  +> ").split():
                    flag(node, f"plain {name}('d')")
            if name in ("sympify", "S"):
                loc = {k.arg: k.value for k in node.keywords}.get("locals")
                if isinstance(loc, ast.Dict):
                    for k, v in zip(loc.keys, loc.values):
                        if isinstance(k, ast.Constant) and k.value == "d" and _src(src, v) not in OPAQUE_D_VAL
  +> UES:
                            flag(node, "sympify locals 'd' not the opaque d")
        if isinstance(node, ast.Call):
            name = _name(node.func)
            if name in ("sympify", "S"):
                loc = {k.arg: k.value for k in node.keywords}.get("locals")
                has_d = isinstance(loc, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == "d" for k
  +>  in loc.keys)
                if not has_d:
                    sites.append(f"{rel}::{fn}::{_src(src, node)}")
        for ch in ast.iter_child_nodes(node):
            visit(ch, fn)
    visit(tree)
    return bad, sites


def _pkg_files():
    return [f for d in PKG for f in sorted((ROOT / d).glob("*.py"))]


def test_h1_static_scan_package_clean_and_sites_reviewed():
    bad, sites = [], []
    for f in _pkg_files():
        b, s = scan(*CR.scan_view(f))   # p22: p18 contract core of the registered dred revision
        bad += b
        sites += s
    assert not bad, bad
    assert not sorted(set(sites) - set(QC.PARSE_SITES_REVIEWED))                 # every site reviewed
    assert not sorted(set(QC.PARSE_SITES_REVIEWED) - set(sites))                 # no stale entry


PLANTS = {
    "poly_call": "import sympy as sp\ndef f(e, d):\n    return sp.Poly(e, d)(4)\n",
    "as_poly_call": "def f(e, d):\n    return e.as_poly(d)(4)\n",
    "horner_all_coeffs": "import sympy as sp\ndef f(e, d):\n    c = sp.Poly(e, d).all_coeffs()\n    return c\n
  +> ",
    "type_rebuild": "def f(e):\n    return type(e)(*e.args)\n",
    "class_rebuild": "def f(e):\n    return e.__class__(*e.args)\n",
    "getattr_dynamic": "def f(e, m):\n    return getattr(e, m)\n",
    "getattr_hazard": "def f(e, d):\n    return getattr(e, 'subs')(d, 4)\n",
    "aliased_import": "from sympy import sympify as sy\ndef f(t):\n    return t\n",
    "alias_assign": "import sympy as sp\nsy = sp.sympify\n",
    "locals_plain_d": "import sympy as sp\ndef f(t):\n    return sp.sympify(t, locals={'d': sp.Symbol('x')})\n
  +> ",
    "plain_symbol_d": "import sympy as sp\nD = sp.Symbol('d')\n",
    "plain_symbols_d": "import sympy as sp\nA, D = sp.symbols('a d')\n",
    "eval_srepr": "def f(s):\n    return eval(s)\n",
    "func_rebuild": "def f(e):\n    return e.func(*e.args)\n",
    "replace_named": "def g(x):\n    return x\ndef f(e):\n    return e.replace(g, g)\n",
}


@pytest.mark.parametrize("name", sorted(PLANTS))
def test_h1_scan_detects_planted_violation(tmp_path, name):
    f = tmp_path / f"{name}.py"
    f.write_text(PLANTS[name])
    bad, _ = scan(f, tmp_path)
    assert bad, name


def test_h1_scan_allows_the_opaque_d_and_literal_getattr(tmp_path):
    f = tmp_path / "ok.py"
    f.write_text("import sympy as sp\nimport dred\nd = dred.d\ndef f(t, o):\n    x = getattr(o, 'active', Fals
  +> e)\n"
                 "    return sp.sympify(t, locals={'d': dred.d}), sp.sympify(t, locals={'d': d}), x\n")
    bad, sites = scan(f, tmp_path)
    assert not bad and not sites


def test_h1_disclosure_wording():
    txt = (ROOT / "code" / "p5_entry" / "dred.py").read_text()
    assert "pattern check, not a proof" in txt and "tests/test_p18.py" in txt


# ================================================================ H3 / H5: dred documentation revision
def test_h3_h5_dred_revision_is_documentation_only():
    import release_p18 as R
    assert (R.ast_sha(ROOT / "code" / "p5_entry" / "dred.py") == QC.P17_DRED_AST_SHA256
            or CR.dred_revision(ROOT)["state"] == "p18 + p22 guard block")     # p22: registered additive revi
  +> sion
    assert hashlib.sha256((ROOT / "code" / "p5_entry" / "dred.py").read_bytes()).hexdigest() != QC.P17_DRED_SH
  +> A256
    txt = (ROOT / "code" / "p5_entry" / "dred.py").read_text()
    assert "tests/test_p16.py scans the package code for them" not in txt                    # H3 stale commen
  +> t gone
    assert "srepr" in txt and "RAISES PlainDimensionSymbol" in txt                           # H5 documented
    hdr = (ROOT / "code" / "p5_calc" / "p18_conventions.py").read_text()
    assert "STORED STRINGS" in hdr                                                          # H3 header correc
  +> ted


def test_h5_parse_d_srepr_raises():
    e = DR.d ** 2 + 1
    with pytest.raises(DR.PlainDimensionSymbol):
        DR.parse_d(sp.srepr(e))
    assert sp.cancel(DR.parse_d(str(e)) - e) == 0


def test_contract_and_layers_identical():
    cur = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    assert sorted(k for k, h in Q15.P14R_CONTRACT_SHA256.items() if cur.get(k) != h) == ["code/p5_entry/dred.p
  +> y"]
    assert set(cur) == set(Q15.P14R_CONTRACT_SHA256)
    for k, h in {**Q16.P15_CALC_SHA256, **Q17.P16_CALC_SHA256, **QC.P17_CALC_SHA256}.items():
        assert hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == h, k


def test_p14_to_p17_certificate_values_unchanged_vs_p17_reference():
    import certio
    ref = json.loads((ROOT / "archival" / "p17" / "reference_values_p17.json").read_text())["values"]
    ch = ref["certificate_content_sha256_ignoring_timings"]
    diff = [n for n, h in ch.items()
            if n.startswith(("P13_", "P14_", "P15_", "P16_", "P17_"))
            and n not in ("P15_release", "P16_release", "P17_release")
            and certio.file_content_sha(CERT / f"{n}.json", QC.RUN_SPECIFIC_KEYS) != h]
    assert not diff, diff


# ================================================================ priority 1: M2
def test_m2_certificate_verdict_controls_mutations():
    c = cj("P18_D11_M2.json")
    assert c["revision"] == "p18" and c["D11_matching_verified"] is True and c["verdict"].startswith("DISCHARG
  +> ED")
    assert all(v is True for v in c["controls"].values()) and len(c["controls"]) == 8
    assert c["route_B"]["pairs"] == 100 and c["route_B"]["mismatches"] == 0 and c["route_B"]["nonzero_pairs"] 
  +> > 0
    assert sp.simplify(Z(c["route_B"]["constant"]) + I / 4) == 0
    assert c["FT_constant"]["c_FT_from_DR_bubble"] == "I*pi**2" == c["FT_constant"]["c_FT_from_minus_r"]
    assert len(c["mutations"]) == 6 and all(v["accepted_as_rejection"] and v["mismatches"] > 0
                                            for v in c["mutations"].values())
    assert c["route_A"]["M1"]["pass"] is True and c["route_A"]["XVI_O"]["ok"] is True
    assert "4D" in c["scope"] and len(c["evanescent_L_coefficients"]) == 8
    assert c["D11_matching_verified_scope"] == "4D components"
    assert c["evanescent_components_matching"]["status"] == "not_applicable_not_verified"
    assert c["M3_status"]["status"].startswith("unconditional on the 4D components")


def test_m2_covariant_recheck_independent_of_d11_code():
    """the nonlocal coefficient -A(4) of the 4D structures, read from P18_D11.json, against the hand expansion
  +>  of
    -(i/4)(Dhat2/60 + Dhat0/18), Phat_mn = p_m p_n - g_mn p^2 (one representative per orbit)."""
    res = cj("P18_D11.json")["result"]
    want = {"p_m p_n p_r p_s": -I / 60, "g4_mn p_r p_s (p.p)^1": I / 80, "g4_rs p_m p_n (p.p)^1": I / 80,
            "g4_mn g4_rs (p.p)^2": -I / 80, "g4_mr p_n p_s (p.p)^1": I / 480, "g4_mr g4_ns (p.p)^2": -I / 480}
    four = {k: v for k, v in res.items() if not v["evanescent"]}
    assert set(four) == set(want)
    for k, w in want.items():
        assert sp.simplify(-P(four[k]["nonlocal_coefficient_of_L"]) - w) == 0, k      # L-coeff = -A(4) = X


# ================================================================ D11 evaluation
def test_d11_evaluated_controls_mutations():
    c = cj("P18_D11.json")
    assert c["evaluated"] is True and c["D11_evaluated"] is True and c["D11_matching_verified"] is True
    assert len(c["controls"]) == 14 and all(v is True for v in c["controls"].values())
    assert c["controls"]["exactly_degree_four_every_structure"] and c["controls"]["N4_no_order_0_or_2_contact_
  +> arises"]
    assert "N4" in c["prescription_usage"]["N4_contact_exclusions"]
    assert sorted(c["mutations"]) == sorted(("premature_d4", "drop_evanescent_gt", "wrong_external_index_posit
  +> ion",
                                             "wrong_offdiagonal_weight"))
    assert all(v["accepted_as_rejection"] for v in c["mutations"].values())
    assert c["evanescent_pole_nonzero"] is True and c["longitudinal_projection_p_m_G"] == {}
    assert len(c["result"]) == 14


def test_d11_laurent_consistency():
    for k, v in cj("P18_D11.json")["result"].items():
        a = P(v["A_exact_d_times_MB"])
        a4 = DR.substitute_d(a, 4, "test_p18: A(4)")
        da = DR.substitute_d(sp.diff(a, DR.d), 4, "test_p18: A'(4)")
        assert sp.simplify(P(v["UV_pole"]) - a4) == 0, k
        L = sp.Symbol("L")
        assert sp.simplify(P(v["MSbar_finite"]) - (a4 * (2 - L) - 2 * da)) == 0, k


# ================================================================ full hh slot
def test_full_slot_verdict_and_seven_assignments():
    c = cj("P18_hh_slot.json")
    assert c["decoupling_proven_full_row"] is True and c["surviving_evanescent_structures_in_slot"] == []
    assert c["D11_reopens_evanescent_question"] is False
    assert all(v is True for v in c["controls"].values()) and len(c["controls"]) == 11
    sv = c["slot_values"]
    assert len(sv["D01+D03+D11"]) == 7 and "c hat, h tilde" in sv["D01+D03+D11"]                 # H2
    assert all(v == "0" for v in sv["D01+D03+D11"].values()) and all(v == "0" for v in sv["D11"].values())
    # H2: the reviewer's value X_D01 = p.p^2 a~.b~ c^.p/16 = -X_D03 (purely through the evanescent gt_rs p_n s
  +> tructure)
    assert sv["D01"]["c hat, h tilde"] == "a~.b~*c^.p*p.p**2/16" and sv["D03"]["c hat, h tilde"] == "-a~.b~*c^
  +> .p*p.p**2/16"
    assert any(v != "0" for v in sv["D11_under_trace_operator"].values())
    assert c["p_dot_G"]["D11"] == {} and c["p_dot_G"]["D01+D03+D11"] == {}
    assert all(v["accepted_as_rejection"] for v in c["mutations"].values())


def test_full_slot_transverse_coordinates():
    fd = cj("P18_hh_slot.json")["four_D_poles"]
    k1, k2 = [[sp.Rational(x) for x in v] for v in fd["transverse_basis_in_p14r_coordinates"]]
    z = {g: [Z(x) for x in fd["graphs"][g]["coordinates_p14r_basis"]] for g in ("D11", "D01+D03", "D01+D03+D11
  +> ")}
    a, b = sp.symbols("a b")
    sol = lambda w: sp.solve([a * u + b * v - x for u, v, x in zip(k1, k2, w)], [a, b], dict=True)  # noqa: E7
  +> 31
    assert sol(z["D11"]) == [{a: I / 240, b: -I / 120}]
    assert sol(z["D01+D03"]) == [{a: 61 * I / 120, b: -7 * I / 20}]
    assert sol(z["D01+D03+D11"]) == [{a: 41 * I / 80, b: -43 * I / 120}]
    assert all(fd["graphs"][g]["transverse"] for g in z)


def test_readback_detects_mutation_inside_wrapped_value():
    """the long full-slot verdict is wrapped in the listing; a mutation inside it must still fail the readback
  +> ."""
    import build as B
    rel = "certificates/P18_hh_slot.json"
    txt = B.wrap_lines(B.ascii_clean((ROOT / rel).read_text()))
    page = txt[: len(txt) // 2] + "\n" + QC.VERSION_LABEL + " | page 7\n" + txt[len(txt) // 2:]
    assert B.readback_values(page, ROOT, rel, page)["pass"] is True
    v = B.value_snippets(ROOT, rel)[0]
    assert v.startswith('"verdict"') and v not in page                       # wrapped: not verbatim
    bad = page.replace("D11 by itself", "D11 BY itself", 1)
    assert bad != page and B.readback_values(bad, ROOT, rel, bad)["pass"] is False


def test_inventory_and_quantum_inputs_flag():
    c = cj("P18_hh_slot.json")
    assert set(c["inventory"]) == set(QC.INVENTORY_P18) and all(v["evaluated"] for v in c["inventory"].values(
  +> ))
    # fresh-build ordering regression (presync #2): every input certificate, incl. this run's P18_D11.json, is
  +>  present
    assert all(v["present"] is True for v in c["inventory"].values())
    assert c["quantum_inputs_evaluated"] == "earned"
    led = json.loads((ROOT / "ledgers" / "P13_graph_inventory.json").read_text())["graphs"]
    assert {k.split("_")[0] for k in led} == set(QC.INVENTORY_P18)                 # independent: the P13 ledg
  +> er
    rows = json.loads((ROOT / "ledgers" / "P13_ch_dependency_rows.json").read_text())["rows"]
    req = {g.split("_")[0] for r in rows if r["status"].startswith("surviving") for g in r["graphs"]}
    assert req == set(QC.INVENTORY_P18) and len({r["id"] for r in rows if r["status"].startswith("surviving")}
  +> ) == 3
    lst = rs()["quantum_inputs_inventory"]
    assert {x["graph"] for x in lst} == req and all(x["evaluated"] for x in lst)
    assert not [x for x in lst if not x["status"] or "missing" in x["status"].lower()
                or "unevaluated" in x["status"].lower()]


# ================================================================ status
def test_p18_release_status_and_flags():
    s = rs()
    assert s["revision"] == "p18" and s["publication"] == "accepted" and s["release_claim_accepted"] is True
    assert s["D11_matching_verified"] is True and s["D11_evaluated"] is True
    assert s["D11_matching_verified_scope"] == "4D components"
    assert s["D11_evanescent_components_matching"] == "not_applicable_not_verified"
    assert s["M3_status"].startswith("unconditional on the 4D components")
    assert s["quantum_inputs_evaluated"] == "earned" and s["hh_full_row_decoupling_proven"] is True
    assert s["projected_identity_verified"] == "not_earned" and s["projected_restoration_verified"] == "not_ea
  +> rned"
    assert s["projected_defect_computed"] == "not_earned"
    assert s["hard_stops"] == QC.HARD_STOPS_P18 and s["hard_stops_hold"] is True
    assert s["symmetry_restored"] is False and s["bulk_symmetry_restored"] is False and s["O1_closure"] == "NO
  +> T_CLOSED"
    assert s["XVI_P_registered"] is False and s["Route_B_discharged"] is False and s["u_R_c_delta_added"] is F
  +> alse
    assert s["XV_B_opened"] is False and s["XIV_J_opened"] is False and s["evanescent_hh_counterterm_added"] i
  +> s False
    assert s["insertion_status"] == "Frozen_negative_obstruction_preserved"
    assert s["XVI_M_sha256"].startswith("41aa1099") and s["XVI_M_pin_ok"] is True
    assert s["milestones"]["status"]["P.5_identity"] == "open"
    assert s["independent_rebuild_passed"] in ("pending", False)   # p19: the live p18 report is bound to the 
  +> p18 tree
    assert s["contract_identity"]["added"] == [] and s["contract_identity"]["changed_vs_p14r"] == ["code/p5_en
  +> try/dred.py"]


def test_p17_independent_rebuild_recorded_and_not_inherited():
    s = rs()
    rec = s["p17_independent_rebuild"]
    assert s["independent_rebuild_passed_p17"] is True
    assert rec["report_sha256"] == QC.P17_INDEPENDENT_REPORT_SHA256 and rec["pins_ok"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P17_SOURCE_TREE_SHA256
    assert rec["bound_to_source_zip_sha256"] == QC.P17_SOURCE_ZIP_SHA256
    assert "SAME-BOX" in rec["caveat"] and rec["mismatches"] == 0
    import source_manifest as SM
    assert SM.tree_sha(ROOT) != QC.P17_SOURCE_TREE_SHA256


def test_change_log_vs_p17():
    s = rs()
    cl = s["change_log_vs_p17"]
    assert cl["base_pinned_ok"] is True
    base = json.loads((ROOT / QC.P17_SOURCE_LIST).read_text())["files"]
    import source_manifest as SM
    cur = {r: hashlib.sha256((ROOT / r).read_bytes()).hexdigest() for r in SM.source_files(ROOT) if r != SM.RE
  +> FERENCE_FILE}
    changed = sorted(set(cur) ^ set(base) | {k for k in set(cur) & set(base) if cur[k] != base[k]} | {SM.REFER
  +> ENCE_FILE})
    assert sorted(cl["added"] + cl["removed"] + cl["modified"]) == changed
    assert SM.REFERENCE_FILE in cl["added"] and cl["contract_files_changed"] == ["code/p5_entry/dred.py"]
    import p19_conventions as Q19                                  # p19: tests revised in p18 or (disclosed) 
  +> in p19
    assert (set(x for x in cl["modified"] if x.startswith("tests/")   # p22 filter
                and not __import__("contract_registry").p22_revised(x))
            <= set(QC.DISCLOSED_TEST_REVISIONS_P18) | set(Q19.DISCLOSED_TEST_REVISIONS_P19))


def test_version_label_p18():
    import build as B
    assert QC.VERSION_LABEL == "XVI-P p18" and B.QC.VERSION_LABEL == f"XVI-P {B.QC.REVISION}"   # p19: current
  +>  label
    for f in ("certificates/P18_D11_M2.json", "certificates/P18_D11.json", "certificates/P18_hh_slot.json"):
        assert f in B.VALUE_BLOCKS


# ================================================================ p18 gate mutations
def _copy():
    d = Path(tempfile.mkdtemp(prefix="p18gate_"))
    for sub in ("code", "certificates", "ledgers", "exports", "tools", "archival", "reproducibility", "provena
  +> nce", "tests"):
        if (ROOT / sub).exists():
            shutil.copytree(ROOT / sub, d / sub, ignore=shutil.ignore_patterns("__pycache__", "*.zip", "*.pdf"
  +> ))
    for f in ("README.md", "REBUILD_INSTRUCTIONS.md", "RELEASE_STATUS.json"):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, d / f)
    (d / "manuscript").mkdir()
    shutil.copy(ROOT / "manuscript" / "preamble.tex", d / "manuscript" / "preamble.tex")
    return d


def _edit_cert(d, name, fn):
    f = d / "certificates" / name
    c = json.loads(f.read_text())
    fn(c)
    f.write_text(json.dumps(c, indent=1))


def _m2_control(d):
    _edit_cert(d, "P18_D11_M2.json", lambda c: c["controls"].__setitem__("route_B_all_100_pairs_agree", False)
  +> )


def _m2_mutation_accepted(d):
    _edit_cert(d, "P18_D11_M2.json", lambda c: c["mutations"]["alpha_beta_swapped"].__setitem__(
        "accepted_as_rejection", False))


def _d11_not_evaluated(d):
    _edit_cert(d, "P18_D11.json", lambda c: c.__setitem__("evaluated", False))


def _surviving_structure(d):
    _edit_cert(d, "P18_hh_slot.json", lambda c: c.__setitem__("surviving_evanescent_structures_in_slot",
                                                               ["gt_rs p_m p_n (p.p)^1"]))


def _m2_scope_dropped(d):
    _edit_cert(d, "P18_D11_M2.json", lambda c: c.pop("D11_matching_verified_scope"))


def _inventory_hole(d):
    _edit_cert(d, "P15_D13.json", lambda c: c["D13_evaluated"].__setitem__("execution", False))


def _tamper_p17_layer(d):
    f = d / "code" / "p5_calc" / "hh_slot.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _dred_code_change(d):
    f = d / "code" / "p5_entry" / "dred.py"
    f.write_text(f.read_text() + "\n_TAMPER = 1\n")


def _new_contract_file(d):
    (d / "code" / "p5_entry" / "evanescent_hh_counterterm.py").write_text("# undisclosed contract file\n")


def _tamper_p17_report(d):
    f = d / "archival" / "p17" / "reproducibility" / "independent_rebuild_report_p17.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


def _projected_identity_claimed(d):
    _edit_cert(d, "P18_hh_slot.json", lambda c: c.__setitem__("projected_identity_verified", "earned"))


MUTS = [_m2_control, _m2_mutation_accepted, _m2_scope_dropped, _d11_not_evaluated, _surviving_structure, _inve
  +> ntory_hole,
        _tamper_p17_layer, _dred_code_change, _new_contract_file, _tamper_p17_report, _projected_identity_clai
  +> med]


@pytest.mark.parametrize("mut", MUTS, ids=lambda f: f.__name__)
def test_certificate_mutation_p18_gate_rejects_or_withholds(mut):
    d = _copy()
    try:
        mut(d)
        r = subprocess.run([sys.executable, "code/p5_calc/release_p18.py"], cwd=d, capture_output=True, text=T
  +> rue,
                           timeout=600)
        if mut is _inventory_hole:          # gate may publish, but must NOT earn quantum_inputs_evaluated
            if r.returncode == 0:
                assert json.loads((d / "RELEASE_STATUS.json").read_text())["quantum_inputs_evaluated"] == "not
  +> _earned"
            return
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d / "certificates" / "P18_release.json").exists()
        assert (d / "certificates" / "P18_release_rejected.json").exists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_p18_gate_accepts_unmodified_copy():
    d = _copy()
    try:
        r = subprocess.run([sys.executable, "code/p5_calc/release_p18.py"], cwd=d, capture_output=True, text=T
  +> rue,
                           timeout=600)
        assert r.returncode == 0, r.stdout[-1500:]
    finally:
        shutil.rmtree(d, ignore_errors=True)
