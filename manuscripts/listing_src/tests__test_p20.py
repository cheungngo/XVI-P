"""XVI-P p20 tests: correction release of p19 (K1 orientation; restoration redefined; full-closure mutation de
  +> tector;
D11 ratio pin; J1 wording; extended static scan -- a PATTERN CHECK, NOT A PROOF; release gate fail-closed with
  +>  no
stale RELEASE_STATUS)."""
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
for p in ("code/p5_calc", "code/p5_entry", "code/classical", "tools", "tests"):
    sys.path.insert(0, str(ROOT / p))
import contract_registry as CR  # p22 (disclosed): registered contract revision
import p20_conventions as QC  # noqa: E402
import p19_conventions as Q19  # noqa: E402
import p21_conventions as Q21  # noqa: E402   (p21: reviewed-site lists)

CERT = ROOT / "certificates"


def cj(name):
    return json.loads((CERT / name).read_text())


def rs():
    # p21 (disclosed): the p20 LAYER record (the top-level RELEASE_STATUS.json is the p21 status)
    return json.loads((CERT / "P20_release.json").read_text())


# ================================================================ K1: orientation and full closure
def test_k1_live_orientation_ratio_minus_one():
    import defect as DF
    r, ok = DF.orientation_ratio()
    assert ok and [sp.sympify(x) for x in r] == [-1, -1]


def test_k1_live_tree_controls():
    """tree level: V_S0[cb,c] = 2iD V_S0[K,c]; sigma_0(S0_Kc + S0_cbc) = 0 while sigma_0(S0_Kc) alone is nonze
  +> ro."""
    import defect as DF
    t = DF.tree_controls()
    assert t["ghost_equation_tree_V_cbc_eq_2iD_V_Kc"] is True
    assert t["sigma0_S0Kc_plus_S0cbc_entries"] == 0 and t["sigma0_S0Kc_alone_entries (control, nonzero)"] > 0
    assert t["S0_Kc_terms"] > 0 and t["S0_cbc_terms"] > 0 and t["ok"] is True


def test_k1_full_closure_complete_counterterm():
    c = cj("P19_defect.json")
    k = c["counterterm_solve"]["K1_ghost_closure_convention"]
    assert k["relative_factor_derived"] == "1" and k["derived_equals_P15"] is True
    assert k["Sigma_pole_routeG_c_cb_coordinates"] == ["3/8", "-1/4"]
    assert k["Sigma_local_routeG_c_cb_coordinates"] == ["2/3", "-5/12"]
    assert k["full_closure_complete_S_ct"] == {"closed": True, "entries": 0, "sectors": []}
    assert k["full_closure_S_ct_without_ccb (p19 package S_ct)"]["sectors"] == ["c.b"]
    assert k["full_closure_S_ct_without_ccb (p19 package S_ct)"]["entries"] == 88
    assert k["full_closure_unconverted (p19 error)"]["entries"] == 88
    assert c["corrected_in_revision"].startswith("p20")


def test_k1_sigma_conversion_consistent_with_p15():
    """Sigma(c,cb) = orientation ratio x Sigma(cb,c) with the P15 fit."""
    k = cj("P19_defect.json")["counterterm_solve"]["K1_ghost_closure_convention"]
    cbc = [sp.Rational(x) for x in k["z_cb_P15_sigma_fit_cbc_orientation"]]
    r = [sp.Rational(x) for x in k["orientation_ratio_routeG_over_cbc"]]
    assert [a * b for a, b in zip(cbc, r)] == [sp.Rational(x) for x in k["Sigma_pole_routeG_c_cb_coordinates"]
  +> ]


def test_quotient_coordinates_with_and_without_sigma():
    c = cj("P19_defect.json")
    assert c["quotient_coordinates"]["pole"] == ["0", "0", "0", "-3/8", "1/4"]       # h.h + c.K only = -[Sigm
  +> a]
    assert c["quotient_coordinates_Sigma_alone_routeG"]["pole"] == ["0", "0", "0", "3/8", "-1/4"]
    assert all(x == "0" for p in c["quotient_coordinates_including_Sigma"].values() for x in p)
    assert "(c,cb)" in c["quotient_reading_p20"]


def test_restoration_redefined_and_earned_only_on_full_closure():
    c = cj("P19_defect.json")
    fd = c["flag_definitions"]["projected_restoration_verified"]
    assert "FULL sigma_0 closure" in fd and "COMPLETE" in fd and "c.cb" in fd and "NOT bulk symmetry" in fd
    assert c["projected_restoration_verified"] == "earned" and c["bulk_symmetry_restored"] is False
    rc = c["route_consistency_control_p19_criterion"]
    assert rc["holds"] is True and "NOT a flag" in rc["label"]
    assert all(v is True for v in c["p20_controls"].values()) and len(c["p20_controls"]) >= 7


def test_full_closure_mutation_detector():
    det = cj("P19_defect.json")["full_closure_mutation_detector"]["cases"]
    assert det["drop_graph_D13 (c.K data = 0, Sigma held fixed)"]["detected"] is True
    assert det["flip_sign_Kc (c.K data -> -c.K, Sigma held fixed)"]["detected"] is True
    assert det["drop_graph_D13 (c.K data = 0, Sigma held fixed)"]["sectors"] == ["c.b"]
    for k in ("drop_graph_D01", "drop_graph_D03", "flip_phase_D03", "symmetry_factor_D03_x2"):
        assert det[k]["detected"] is True and det[k]["sectors"] == ["h.c"], k
    assert det["Sigma_orientation_unconverted (p19 error)"]["detected"] is True
    assert det["drop_graph_D11"]["detected"] is False          # recorded blind: covered by the D11 pin


# ================================================================ D11 pin
def test_d11_pin_certificate():
    c = cj("P20_D11_pin.json")
    sd = c["spin_decomposition"]
    assert sd["c2_spin2"] == "-I/240" and sd["c0_spin0s"] == "-I/24" and sd["ratio_c0_over_c2"] == "10"
    assert sd["transverse"] is True and sd["only_spin2_and_spin0s"] is True
    assert c["ratio_pin"]["status"] == "PASS" and c["D11_ratio_pin_verified"] is True
    # p21 (disclosed): absolute pin derived (sign and magnitude); p20 had it OPEN
    assert c["absolute_pin"]["status"] == "PASS" and c["absolute_pin_status"] == "PASS"
    assert c["D11_absolute_pin_verified"] is True and c["corrected_in_revision"].startswith("p21")
    assert "Birrell" in c["literature_a2_minimal_scalar"]["source"]
    assert "EXTERNAL" in c["literature_a2_minimal_scalar"]["source"]
    m = c["mutations"]
    assert m["drop_graph_D11"]["detected_by_ratio_pin"] is True
    assert m["D11_normalisation_x2"]["detected_by_ratio_pin"] is False
    assert m["D11_normalisation_x2"]["detected_by_absolute_pin"] is True
    assert m["D11_sign_flip"]["detected_by_ratio_pin"] is False and m["D11_sign_flip"]["detected_by_absolute_p
  +> in"] is True


def test_d11_pin_live_recompute():
    import d11_pin as P
    import covariant as C
    cert = cj("P18_D11.json")
    import dred
    four = {k: dred.parse_d(str(v["UV_pole"]), {"I": sp.I}) for k, v in cert["result"].items() if not v["evane
  +> scent"]}
    eta = tuple(int(x) for x in C.ETA)
    p = (sp.Integer(2), sp.Rational(1, 3), sp.Integer(-1), sp.Integer(4))     # a different generic momentum
    T, pp = P.tensor(four, eta, p)
    r = P.spin_parts(T, eta, p, pp)
    assert r["c2"] == -sp.I / 240 and r["c0"] == -sp.I / 24 and r["transverse"] and r["only_spin2_spin0s"]


def test_curvature_quadratic_forms():
    import d11_pin as P
    f = P.curvature_forms((sp.Integer(1), sp.Integer(2), sp.Integer(-3), sp.Rational(1, 2)))
    assert f["C2"] == {"P2": sp.Rational(1, 2), "P0s": 0} and f["R2"] == {"P2": 0, "P0s": 3}
    assert f["E_GaussBonnet"] == {"P2": 0, "P0s": 0}
    assert (P.LIT["R2_xi0"] * 3) / (P.LIT["C2"] * sp.Rational(1, 2)) == 10


# ================================================================ J1 wording, retraction
def test_j1_wording():
    j = cj("P19_defect.json")["findings"]["J1_p14r_counterterm_domain_field"]
    assert "compatible real structure" in j and "physical field" not in j
    assert "compatible real structure" in cj("P19_defect.json")["field_note"]


def test_retraction_check_clean():
    s = rs()
    assert s["retraction_check"]["hits"] == {}
    import release_p20 as R
    ok, rec = R.retraction_check()
    assert ok, rec["hits"]
    note = (ROOT / "manuscript" / "notes" / "P20_correction.tex").read_text()
    assert "Erratum K1" in note and "retracted" in note


# ================================================================ scan (p19 reviewer gaps; a PATTERN CHECK, N
  +> OT A PROOF)
ARGS_ITER_CALLS = {"Add", "Mul", "Pow", "reduce", "func"}
ALIAS_WATCH = {"Poly", "poly", "sympify", "parse_expr", "Symbol", "symbols", "S", "N", "lambdify"}


def _iter_over_args(node):
    return any(isinstance(g.iter, ast.Attribute) and g.iter.attr == "args"
               for n in ast.walk(node) if isinstance(n, (ast.ListComp, ast.GeneratorExp, ast.SetComp))
               for g in n.generators)


def scan3(path, root=ROOT):
    """p20 additions on top of test_p19.scan2: rebuilds from comprehensions over e.args (Add/Mul/Pow/func/any
    starred call, functools.reduce), aliased imports of Poly/sympify/Symbol..., any __call__ attribute,
    as_coefficients_dict, Symbol/symbols(name=<run-time>) keywords, explicit .func(*..args) constructor rebuil
  +> ds."""
    import test_p19 as T19
    bad, sites = T19.scan2(path, root)
    src = path.read_text()
    tree = ast.parse(src)
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.name
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.asname and a.name in ALIAS_WATCH:
                    bad.append(f"{rel}:{node.lineno}:aliased import {a.name} as {a.asname}")
        if isinstance(node, ast.Attribute) and node.attr == "__call__":
            bad.append(f"{rel}:{node.lineno}:__call__")
        if isinstance(node, ast.Call):
            name = T19._name(node.func)
            if name == "as_coefficients_dict":
                bad.append(f"{rel}:{node.lineno}:as_coefficients_dict")
            if any(isinstance(a, ast.Starred) and _iter_over_args(a.value) for a in node.args):
                bad.append(f"{rel}:{node.lineno}:{name}(*[.. for .. in x.args]) rebuild")
            if name == "reduce" and any(_iter_over_args(a) or (isinstance(a, ast.Attribute) and a.attr == "arg
  +> s")
                                        for a in node.args):
                bad.append(f"{rel}:{node.lineno}:reduce over x.args")
            if name in T19.SYMBOL_MAKERS and any(k.arg in ("name", "names") and T19._d_like(k.value)
                                                 for k in node.keywords):
                bad.append(f"{rel}:{node.lineno}:{name}(name=<run-time>)")
            if name == "func" or (isinstance(node.func, ast.Attribute) and node.func.attr == "func"):
                if any(isinstance(a, ast.Starred) for a in node.args):
                    bad.append(f"{rel}:{node.lineno}:explicit .func(*..) constructor rebuild")
    return bad, sites


def _wrap(code):      # the p19 reviewer's plant template
    return "import sympy as sp\nfrom dred import d\n" f"def g(e):\n    {code}\n"


PLANTS3 = {
    "p18_explicit_constructor_rebuild": "return sp.Add(*[4 if x == d else x for x in e.args])",
    "p19_add_listcomp_over_args": "return sp.Add(*[4 if x == d else x for x in e.args])",
    "p19_poly_alias_import": "from sympy import Poly as Q\n    return Q(e, d)(4)",
    "p19_poly_dunder_call": "return sp.Poly.__call__(sp.Poly(e, d), 4)",
    "p19_as_coefficients_dict": "return sum(c * (4 if k == d else k) for k, c in e.as_coefficients_dict().item
  +> s())",
    "p19_reduce_rebuild": "import functools, operator\n    return functools.reduce(operator.add, [4 if x == d 
  +> else x for x in e.args])",
    "p19_symbol_kw_name": "return sp.Symbol(name=chr(100))",
    "func_starred_rebuild": "return e.func(*[4 if x == d else x for x in e.args])",
    "mul_genexp_over_args": "return sp.Mul(*(x for x in e.args if x != d))",
}


@pytest.mark.parametrize("name", sorted(PLANTS3))
def test_scan3_detects_reviewer_plants(tmp_path, name):
    f = tmp_path / f"{name}.py"
    f.write_text(_wrap(PLANTS3[name]))
    bad, _ = scan3(f, tmp_path)
    assert bad, name


def test_scan3_package_clean():
    bad = []
    for d in ("code/p5_calc", "code/p5_entry"):
        for f in sorted((ROOT / d).glob("*.py")):
            bad += scan3(*CR.scan_view(f))[0]   # p22: p18 contract core
    assert not bad, bad


def test_scan3_allows_benign_forms(tmp_path):
    f = tmp_path / "ok.py"
    f.write_text("import sympy as sp\nfrom sympy import Poly\ndef f(e, a, b):\n    s = sp.Symbol(name='x')\n"
                 "    return sp.Add(*[a, b]), sp.Add(*[t for t in (a, b)]), Poly(e, a).terms(), s\n")
    bad, _ = scan3(f, tmp_path)
    assert not bad, bad


def test_scan_disclosure_wording():
    assert "pattern check, not a proof" in (ROOT / "README.md").read_text()


# ================================================================ status
def test_p20_release_status_and_flags():
    s = rs()
    assert s["revision"] == "p20" and s["publication"] == "accepted" and s["execution_pass"] is True
    for k in QC.EARNABLE_P20:
        assert s[k] == "earned", k
    assert s["bulk_symmetry_restored"] is False and s["symmetry_restored"] is False and s["O1_closure"] == "NO
  +> T_CLOSED"
    assert s["hard_stops"] == QC.HARD_STOPS_P20 and s["hard_stops_hold"] is True
    assert s["XVI_P_registered"] is False and s["Route_B_discharged"] is False and s["u_R_c_delta_added"] is F
  +> alse
    assert s["independent_rebuild_passed"] is not True and s["independent_rebuild_passed_p19"] is True   # p21
  +>  tree
    assert s["open_pins"] == list(Q21.OPEN_PINS_P21) and s["D11_absolute_pin_verified"] == "earned"     # p21
    assert "RETRACTED" in s["erratum_p19"]["K1"] and "REDEFINED" in s["erratum_p19"]["restoration"]
    assert s["milestones"]["status"]["P.5_identity"].count("bulk symmetry NOT restored") == 1


def test_p19_independent_recorded_and_not_inherited():
    s = rs()
    rec = s["p19_independent_rebuild"]
    assert rec["report_sha256"] == QC.P19_INDEPENDENT_REPORT_SHA256 and rec["pins_ok"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P19_SOURCE_TREE_SHA256
    assert rec["bound_to_source_zip_sha256"] == QC.P19_SOURCE_ZIP_SHA256 and rec["mismatches"] == 0
    import source_manifest as SM
    assert SM.tree_sha(ROOT) != QC.P19_SOURCE_TREE_SHA256


def test_layers_and_disclosed_revisions():
    assert hashlib.sha256((ROOT / "code/p5_calc/p19_conventions.py").read_bytes()).hexdigest() == QC.P19_CONVE
  +> NTIONS_SHA256
    for k, h in QC.P18_CALC_SHA256.items():   # p22: or the registered p22 revision of that layer file
        assert CR.layer_file_ok(k, hashlib.sha256((ROOT / k).read_bytes()).hexdigest(), h), k
    for k, h in QC.P19_RELEASED_SHA256.items():
        assert hashlib.sha256((ROOT / k).read_bytes()).hexdigest() != h and k in QC.DISCLOSED_P19_LAYER_REVISI
  +> ONS_P20


def test_change_log_vs_p19():
    cl = rs()["change_log_vs_p19"]
    assert cl["base_pinned_ok"] is True and cl["contract_files_changed"] == []
    import source_manifest as SM
    base = json.loads((ROOT / QC.P19_SOURCE_LIST).read_text())["files"]
    cur = {r: hashlib.sha256((ROOT / r).read_bytes()).hexdigest() for r in SM.source_files(ROOT) if r != SM.RE
  +> FERENCE_FILE}
    changed = sorted(set(cur) ^ set(base) | {k for k in set(cur) & set(base) if cur[k] != base[k]} | {SM.REFER
  +> ENCE_FILE})
    assert sorted(cl["added"] + cl["removed"] + cl["modified"]) == changed
    assert sorted(x for x in cl["modified"] if x.startswith("tests/") and not __import__("contract_registry").
  +> p22_revised(x)) == sorted(   # p22 filter
        x for x in QC.DISCLOSED_TEST_REVISIONS_P20 if not __import__("contract_registry").p22_revised(x))
    mod_code = sorted(x for x in cl["modified"] if x.startswith("code/") and not __import__("contract_registry
  +> ").p22_revised(x))
    assert mod_code == sorted(x for x in QC.DISCLOSED_P19_LAYER_REVISIONS_P20
                              if not __import__("contract_registry").p22_revised(x)), mod_code
    for f in ("code/p5_calc/d11_pin.py", "code/p5_calc/release_p20.py", "code/p5_calc/p20_conventions.py",
              "tests/test_p20.py", "manuscript/notes/P20_correction.tex", "archival/p19/README.md"):
        assert f in cl["added"], f


def test_version_label_p20():
    import build as B
    assert QC.VERSION_LABEL == "XVI-P p20" and B.QC.VERSION_LABEL == f"XVI-P {B.QC.REVISION}"   # p21: current
  +>  label
    assert "certificates/P20_D11_pin.json" in B.VALUE_BLOCKS


# ================================================================ p20 gate mutations (fail closed; no stale s
  +> tatus)
def _copy():
    d = Path(tempfile.mkdtemp(prefix="p20gate_"))
    for sub in ("code", "certificates", "ledgers", "exports", "tools", "archival", "reproducibility", "provena
  +> nce",
                "tests"):
        if (ROOT / sub).exists():
            shutil.copytree(ROOT / sub, d / sub, ignore=shutil.ignore_patterns("__pycache__", "*.zip", "*.pdf"
  +> ))
    for f in ("README.md", "REBUILD_INSTRUCTIONS.md", "RELEASE_STATUS.json"):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, d / f)
    (d / "manuscript" / "notes").mkdir(parents=True)
    (d / "manuscript" / "body").mkdir(parents=True)
    for f in ("manuscript/notes/P19_defect.tex", "manuscript/notes/P20_correction.tex",
              "manuscript/body/P19-results-table.tex", "manuscript/body/XVI-P-body.tex"):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, d / f)
    return d


def _edit(d, name, fn):
    f = d / "certificates" / name
    c = json.loads(f.read_text())
    fn(c)
    f.write_text(json.dumps(c, indent=1))


def _k1(c):
    return c["counterterm_solve"]["K1_ghost_closure_convention"]


def _closure_broken(d):
    _edit(d, "P19_defect.json", lambda c: _k1(c)["full_closure_complete_S_ct"].__setitem__("closed", False))


def _orientation_wrong(d):
    _edit(d, "P19_defect.json", lambda c: _k1(c).__setitem__("orientation_ratio_routeG_over_cbc", ["1", "1"]))


def _sigma_unconverted(d):
    _edit(d, "P19_defect.json", lambda c: _k1(c).__setitem__("Sigma_pole_routeG_c_cb_coordinates", ["-3/8", "1
  +> /4"]))


def _derived_factor_minus_one(d):
    _edit(d, "P19_defect.json", lambda c: _k1(c).__setitem__("relative_factor_derived", "-1"))


def _detector_blind_d13(d):
    _edit(d, "P19_defect.json", lambda c: c["full_closure_mutation_detector"]["cases"][
        "drop_graph_D13 (c.K data = 0, Sigma held fixed)"].__setitem__("detected", False))


def _p20_control_false(d):
    _edit(d, "P19_defect.json", lambda c: c["p20_controls"].__setitem__("tree_sigma0_S0Kc_plus_S0cbc_zero", Fa
  +> lse))


def _retracted_text_back(d):
    f = d / "README.md"
    f.write_text(f.read_text() + "\nunder the derived convention (+1, K1) full c.b / ghost-sector closure FAIL
  +> S\n")


def _j1_old_wording(d):
    f = d / "manuscript" / "notes" / "P19_defect.tex"
    f.write_text(f.read_text() + "\nOver Q(i), the physical field.\n")


def _d11_pin_fail(d):
    _edit(d, "P20_D11_pin.json", lambda c: c["ratio_pin"].__setitem__("status", "FAIL"))


def _d11_absolute_failed(d):          # p21: absolute pin required
    _edit(d, "P20_D11_pin.json", lambda c: c["absolute_pin"].__setitem__("status", "FAIL"))


def _d11_top_level_status_inconsistent(d):     # p20 reviewer: top-level key unchecked
    _edit(d, "P20_D11_pin.json", lambda c: c.__setitem__("absolute_pin_status", "OPEN"))


def _d11_sign_flip_undetected(d):
    _edit(d, "P20_D11_pin.json", lambda c: c["mutations"]["D11_sign_flip"].__setitem__("detected_by_absolute_p
  +> in", False))


def _p18_q_not_earned(d):                     # p20 reviewer: standalone p20 gate must recheck the lower layer
  +> s
    _edit(d, "P18_release.json", lambda c: c.__setitem__("quantum_inputs_evaluated", "not_earned"))


def _bulk_claimed(d):
    _edit(d, "P19_defect.json", lambda c: c.__setitem__("bulk_symmetry_restored", True))


def _tamper_p19_report(d):
    f = d / "archival" / "p19" / "reproducibility" / "independent_rebuild_report_p19.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


def _p19_conventions_changed(d):
    f = d / "code" / "p5_calc" / "p19_conventions.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _p19_layer_rejected(d):
    _edit(d, "P19_release.json", lambda c: c.__setitem__("publication", "REJECTED"))


MUTS = [_closure_broken, _orientation_wrong, _sigma_unconverted, _derived_factor_minus_one, _detector_blind_d1
  +> 3,
        _p20_control_false, _retracted_text_back, _j1_old_wording, _d11_pin_fail, _d11_absolute_failed, _bulk_
  +> claimed,
        _tamper_p19_report, _p19_conventions_changed, _p19_layer_rejected,
        _d11_top_level_status_inconsistent, _d11_sign_flip_undetected, _p18_q_not_earned]


def _run(d, script="code/p5_calc/release_p20.py"):
    return subprocess.run([sys.executable, script], cwd=d, capture_output=True, text=True, timeout=600)


@pytest.mark.parametrize("mut", MUTS, ids=lambda f: f.__name__)
def test_certificate_mutation_p20_gate_rejects_without_stale_status(mut):
    d = _copy()
    try:
        assert (d / "RELEASE_STATUS.json").exists()
        mut(d)
        r = _run(d)
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d / "certificates" / "P20_release.json").exists()
        assert (d / "certificates" / "P20_release_rejected.json").exists()
        assert not (d / "RELEASE_STATUS.json").exists() and not (d / "certificates" / "RELEASE_STATUS.json").e
  +> xists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_p19_gate_reject_leaves_no_stale_status():
    d = _copy()
    try:
        _edit(d, "P18_release.json", lambda c: c.__setitem__("quantum_inputs_evaluated", "not_earned"))
        r = _run(d, "code/p5_calc/release_p19.py")
        assert r.returncode == 1
        assert not (d / "RELEASE_STATUS.json").exists() and not (d / "certificates" / "P19_release.json").exis
  +> ts()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_p20_gate_accepts_unmodified_copy():
    d = _copy()
    try:
        r = _run(d)
        assert r.returncode == 0, r.stdout[-1500:]
        s = json.loads((d / "RELEASE_STATUS.json").read_text())
        assert s["revision"] == "p20" and s["projected_restoration_verified"] == "earned"
        assert s["D11_ratio_pin_verified"] == "earned" and s["bulk_symmetry_restored"] is False
        assert s["D11_absolute_pin_verified"] == "earned"
    finally:
        shutil.rmtree(d, ignore_errors=True)
