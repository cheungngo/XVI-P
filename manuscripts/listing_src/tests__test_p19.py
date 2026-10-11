"""XVI-P p19 tests: the projected one-loop kappa^2 ch-identity defect (P19_defect: rows, seven assignments, ev
  +> anescent
decoupling in the assembly, Route C / Route G agreement, field convention J1, quotient coordinates re-derived 
  +> here by
independent linear algebra, counterterm solve, controls / mutations / blind spots / missing control), I2 exten
  +> ded
static scan (pattern check, not a proof; planted violations; reviewed Poly.terms()/coeffs() sites), I1 fail-cl
  +> osed
gate (certificate mutations), I3 milestone wording, p19 status / hard stops / p18 independent record, change l
  +> og."""
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
import p19_conventions as QC  # noqa: E402
import p18_conventions as Q18  # noqa: E402
import p21_conventions as Q20  # noqa: E402   (p21: reviewed-site lists = p19 + p20 + p21; name kept)
import dred as DR  # noqa: E402

CERT = ROOT / "certificates"
PKG = ("code/p5_calc", "code/p5_entry")


def cj(name):
    return json.loads((CERT / name).read_text())


def rs():
    # p20 (disclosed): the p19 LAYER record (the top-level RELEASE_STATUS.json is the p20 status)
    return json.loads((ROOT / "certificates" / "P19_release.json").read_text())


def Z(text):
    return DR.parse_d(str(text), {"I": sp.I})


def V(lst):
    return sp.Matrix([Z(x) for x in lst])


# ================================================================ I2: extended static scan (pattern check, no
  +> t a proof)
ALIASABLE = {"eval", "exec", "compile", "__import__"}
REFLECT = {"vars", "globals", "locals"}
OPGET = {"attrgetter", "methodcaller"}
REBUILD = {"Add", "Mul", "Pow"}
SYMBOL_MAKERS = {"Symbol", "symbols", "Dummy", "var", "Wild"}
POLY_MAKERS = {"Poly", "poly", "as_poly"}
COEFF_ATTRS = {"terms", "coeffs", "monoms", "as_dict", "as_expr_dict"}


def _name(f):
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None


def _src(src, node):
    return ast.get_source_segment(src, node) or ""


def _d_like(node):
    """a Symbol name argument that is not a plain literal and could evaluate to 'd': any call (name built at r
  +> un
    time), a concatenation, or an f-string whose literal parts joined are '' or 'd' (literal characters always
    appear in the result, so f'dH{m}{n}_{r}' or f'{x}.{y}' can never be 'd')."""
    if isinstance(node, (ast.Call, ast.BinOp, ast.Name, ast.Subscript, ast.Attribute)):
        return isinstance(node, (ast.Call, ast.BinOp))
    if isinstance(node, ast.JoinedStr):
        lit = "".join(v.value for v in node.values if isinstance(v, ast.Constant) and isinstance(v.value, str)
  +> )
        return lit in ("", "d")
    return False


def scan2(path, root=ROOT):
    """I2 patterns (p18 reviewer gaps) on top of test_p18.scan: eval/exec aliases (assignment, import, builtin
  +> s
    attribute), vars()/globals()/locals() subscripts, operator.attrgetter/methodcaller, Add/Mul/Pow(*x.args)
    rebuilds, collect(..., evaluate=False), Poly/poly/as_poly with a non-literal generator expression that is 
  +> a
    call (generator built at run time), Symbol/symbols/Dummy/Wild with a run-time name that could be 'd'
    (call, concatenation, f-string not starting with a non-d literal).  Also returns every Poly coefficient
    extraction site (.terms()/.coeffs()/.monoms()/.as_dict()) which must be on COEFF_SITES_REVIEWED."""
    src = path.read_text()
    tree = ast.parse(src)
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.name
    bad, sites = [], []
    # names bound to a Poly/as_poly result anywhere in the module (I2: 'P = Poly(e, d); P(4)')
    poly_names = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                  and _name(n.value.func) in POLY_MAKERS for t in n.targets if isinstance(t, ast.Name)}

    def flag(node, what):
        bad.append(f"{rel}:{node.lineno}:{what}")

    def visit(node, fn=None):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = node.name
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in poly_names:
            flag(node, f"Poly held in {node.func.id} then called")
        if isinstance(node, ast.Assign) and _name(node.value) in ALIASABLE and isinstance(node.value, (ast.Nam
  +> e, ast.Attribute)):
            flag(node, f"alias of {_name(node.value)}")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                if a.name.split(".")[-1] in ALIASABLE | OPGET:
                    flag(node, f"import {a.name}")
        if isinstance(node, ast.Attribute) and node.attr in ALIASABLE and _name(node.value) in ("builtins", "_
  +> _builtins__"):
            flag(node, f"builtins.{node.attr}")
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Call) and _name(node.value.func) in 
  +> REFLECT:
            flag(node, f"{_name(node.value.func)}()[..]")
        if isinstance(node, ast.Call):
            f = node.func
            name = _name(f)
            if name in OPGET:
                flag(node, name)
            if name == "get" and isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call) \
                    and _name(f.value.func) in REFLECT:
                flag(node, f"{_name(f.value.func)}().get(..)")
            if name in REBUILD and any(isinstance(a, ast.Starred) and isinstance(a.value, ast.Attribute)
                                       and a.value.attr == "args" for a in node.args):
                flag(node, f"{name}(*x.args) rebuild")
            if name == "collect" and any(k.arg == "evaluate" and isinstance(k.value, ast.Constant)
                                         and k.value.value is False for k in node.keywords):
                flag(node, "collect(evaluate=False)")
            if name in POLY_MAKERS:
                gens = node.args[1:] if name != "as_poly" else node.args
                if any(isinstance(g, ast.Call) or (isinstance(g, ast.Starred) and isinstance(g.value, ast.Call
  +> ))
                       for g in gens) and f"{rel}::{fn}::{_src(src, node)}" not in QC.POLY_GENERATOR_CALL_SITE
  +> S_REVIEWED:
                    flag(node, f"{name}(generator built by a call)")
            sym_maker = name in SYMBOL_MAKERS and (name != "var" or _name(getattr(f, "value", None)) in (None,
  +>  "sp", "sympy"))
            if sym_maker and node.args and _d_like(node.args[0]):
                flag(node, f"{name}(run-time name)")
            if name in COEFF_ATTRS and isinstance(f, ast.Attribute) and not node.args:
                sites.append(f"{rel}::{fn}::{_src(src, node)}")
        for ch in ast.iter_child_nodes(node):
            visit(ch, fn)
    visit(tree)
    return bad, sites


def _pkg_files():
    return [f for d in PKG for f in sorted((ROOT / d).glob("*.py"))]


def test_i2_static_scan_package_clean_and_coeff_sites_reviewed():
    bad, sites = [], []
    for f in _pkg_files():
        b, s = scan2(f)
        bad += b
        sites += s
    assert not bad, bad
    rev = Q20.COEFF_SITES_REVIEWED
    assert not sorted(set(sites) - set(rev)), sorted(set(sites) - set(rev))
    assert not sorted(set(rev) - set(sites)), sorted(set(rev) - set(sites))
    assert all(v.startswith("generator") for v in rev.values())


def test_i2_p18_scan_still_clean_on_p19_package():
    import test_p18 as T18
    bad, sites = [], []
    for f in _pkg_files():
        b, s = T18.scan(*CR.scan_view(f))   # p22: p18 contract core
        bad += b
        sites += s
    assert not bad, bad
    assert set(sites) == set(Q18.PARSE_SITES_REVIEWED)


PLANTS2 = {
    "eval_alias_assign": "e = eval\ndef f(s):\n    return e(s)\n",
    "eval_builtins_attr": "import builtins\ndef f(s):\n    return builtins.eval(s)\n",
    "eval_import": "from builtins import eval as ev\n",
    "globals_subscript": "def f():\n    return globals()['d']\n",
    "locals_get": "def f(d):\n    return locals().get('d')\n",
    "sympy_var_call": "import sympy as sp\ndef f():\n    return sp.var(chr(100))\n",
    "symbol_fstring_only_var": "import sympy as sp\ndef f(k):\n    return sp.Symbol(f'{k}')\n",
    "vars_subscript": "import dred\ndef f():\n    return vars(dred)['d']\n",
    "attrgetter": "import operator\ndef f(e):\n    return operator.attrgetter('subs')(e)\n",
    "methodcaller": "from operator import methodcaller\ndef f(e, d):\n    return methodcaller('subs', d, 4)(e)
  +> \n",
    "poly_variable_then_called": "import sympy as sp\ndef f(e, d):\n    P = sp.Poly(e, d)\n    return P(4)\n",
    "as_poly_variable_then_called": "def f(e, d):\n    Q = e.as_poly(d)\n    return Q(4)\n",
    "vars_module_subscript": "import sympy as sp\ndef f(t):\n    return vars(sp)['sympify'](t)\n",
    "add_rebuild": "import sympy as sp\ndef f(e):\n    return sp.Add(*e.args[1:]), sp.Add(*e.args)\n",
    "mul_rebuild": "import sympy as sp\ndef f(e):\n    return sp.Mul(*e.args)\n",
    "collect_unevaluated": "import sympy as sp\ndef f(e, x):\n    return sp.collect(e, x, evaluate=False)\n",
    "poly_variable_call": "import sympy as sp\ndef f(e):\n    return sp.Poly(e, sp.Symbol(chr(100)))\n",
    "symbol_call_name": "import sympy as sp\ndef f():\n    return sp.Symbol(chr(100))\n",
    "symbol_fstring_d": "import sympy as sp\ndef f(k):\n    return sp.Symbol(f'd{k}')\n",
    "symbol_concat": "import sympy as sp\ndef f(k):\n    return sp.Symbol('d' + k)\n",
}


@pytest.mark.parametrize("name", sorted(PLANTS2))
def test_i2_scan_detects_planted_violation(tmp_path, name):
    f = tmp_path / f"{name}.py"
    f.write_text(PLANTS2[name])
    bad, _ = scan2(f, tmp_path)
    assert bad, name


def test_i2_scan_allows_benign_forms(tmp_path):
    f = tmp_path / "ok.py"
    f.write_text("import sympy as sp\ndef f(e, k, R):\n    a = sp.Symbol(f'dH{k}_0')\n    b = sp.symbols('p0:4
  +> ')\n"
                 "    c = sp.Symbol(f'{k}.{k}'), R.var(k), {k: v for k, v in locals().items()}\n"
                 "    P = sp.Poly(e, a, *b)\n    return sp.collect(e, a), sp.Add(*[a, b[0]]), P.terms()\n")
    bad, sites = scan2(f, tmp_path)
    assert not bad and sites == ["ok.py::f::P.terms()"]


def test_i2_unreviewed_coeff_site_is_reported(tmp_path):
    f = tmp_path / "new.py"
    f.write_text("import sympy as sp\ndef g(e, x):\n    return sp.Poly(e, x).coeffs()\n")
    _, sites = scan2(f, tmp_path)
    assert sites and not set(sites) <= set(Q20.COEFF_SITES_REVIEWED)


def test_i2_disclosure_wording():
    txt = (ROOT / "code" / "p5_calc" / "p19_conventions.py").read_text()
    assert "PATTERN CHECK, NOT A PROOF" in txt


# ================================================================ priority 1: the projected defect
def test_defect_inventory_complete():
    c = cj("P19_defect.json")
    inv = {x["graph"]: x for x in c["inventory"]}
    assert set(inv) == set(QC.INVENTORY_P19) and all(x["present"] and x["evaluated"] for x in inv.values())
    assert set(c["rows"]) == set(QC.ROWS) and len(QC.ROWS) == 3


def test_defect_zero_exact_in_d_all_seven_assignments_and_parts():
    c = cj("P19_defect.json")
    assert len(c["defect"]) == 7 and len(c["external_assignments"]) == 7
    assert "c hat, h tilde" in c["defect"]
    for a, v in c["defect"].items():
        for part in ("exact_d_times_MB", "pole", "nonlocal_L", "local"):
            assert Z(v[part]) == 0, (a, part)
    assert c["defect_zero_exact_in_d"] is True
    assert all(v == "true" or v is True for v in c["defect_row_sign_independence"].values())


def test_defect_evanescent_decoupling_in_assembly():
    c = cj("P19_defect.json")
    for row in (QC.ROW_HH, QC.ROW_KC):
        ev = c["rows"][row]["evanescent_part"]
        assert len(ev) == 7 and all(Z(x) == 0 for x in ev.values()), row
    assert c["evanescent_in_assembly"].startswith("verified explicitly")
    assert c["controls"]["hh_row_evanescent_part_zero_all_7"] is True
    assert c["controls"]["Kc_row_evanescent_part_zero_all_7"] is True


def test_defect_hh_row_nontrivial_cancellation():
    c = cj("P19_defect.json")
    pg = c["rows"][QC.ROW_HH]["per_graph"]
    assert any(str(x).strip() not in ("0", "") for x in pg["D01"].values())          # dot-product strings
    assert any(str(x).strip() not in ("0", "") for x in pg["D03"].values())
    assert c["controls"]["hh_row_D01_D03_individually_nonzero"] is True


def test_d13_slot_coefficients_from_p15():
    c = cj("P19_defect.json")
    co = c["rows"][QC.ROW_KC]["D13_coefficients"]
    assert Z(co["T1"]) == 0 and Z(co["E1"]) == 0
    d13 = cj("P15_D13.json")
    assert "D13_evaluated" in d13


def test_laurent_consistency_gamma1_local_data():
    g = cj("P19_defect.json")["gamma1_local_data_domain_coordinates"]
    assert len(g["pole"]) == len(g["nonlocal_L"]) == len(g["local"]) == 11
    assert all(Z(a) + Z(b) == 0 for a, b in zip(g["pole"], g["nonlocal_L"]))      # L-coefficient = -pole


def test_route_g_q_i_counts_and_cohomology():
    c = cj("P19_defect.json")
    g, q = c["route_G"], c["D_cap_ker_sigma0"]
    assert g["field"] == "Q(i)" and int(g["dim_D"]) == 11
    assert int(g["sigma0_rank_on_D"]) == 5 and int(g["dim_D_cap_ker_sigma0"]) == 6
    assert int(q["dim"]) == 6 and int(q["dim_D_cap_Im_sigma0"]) == 6 and int(q["cohomology_dim"]) == 0
    assert int(g["P_ch_sigma0_rank_on_D"]) == 3 and int(g["dim_D_cap_ker_P_ch_sigma0"]) == 8
    assert sum(int(s["dim"]) for s in q["sector_ranks"].values()) == 11
    # sector images overlap in the gh+1 space (c.cb#k + c.K#(k+1) in the kernel): per-sector ranks sum to more
    assert sum(int(s["sigma0_rank"]) for s in q["sector_ranks"].values()) >= int(g["sigma0_rank_on_D"])
    assert g["quotient_dim"] == 5 and g["Im_in_ker_sigma0"] is True


def test_field_convention_j1_q_split_reproduces_p14r():
    c = cj("P19_defect.json")
    s = c["route_G_Q_split_p14r_convention"]
    assert int(s["dim_D_cap_ker_sigma0"]) == 5 and int(s["dim_D_cap_Im_sigma0"]) == 3
    assert int(s["P_ch_sigma0_rank_on_D"]) == 4
    assert c["controls"]["routeG_Q_split_reproduces_p14r_counts"] is True
    # the mechanism: an i-multiple is dependent over Q(i) but independent after the re/im split over Q
    v = sp.Matrix([[1, sp.I], [sp.I, -1]])
    split = sp.Matrix([[sp.re(x) for x in v.row(r)] + [sp.im(x) for x in v.row(r)] for r in range(2)])
    assert v.rank() == 1 and split.rank() == 2


def test_d_cap_ker_basis_independent_and_contains_hh_pole():
    """independent linear algebra here: the certificate basis of D cap ker sigma_0 has rank 6 over Q(i), and t
  +> he hh
    part of the Gamma1 pole lies in its span (transverse => sigma_0-exact => zero quotient coordinates)."""
    c = cj("P19_defect.json")
    B = sp.Matrix.hstack(*[V(b) for b in c["route_G"]["D_cap_ker_sigma0_basis"]])
    assert B.shape == (11, 6) and B.rank() == 6
    pole = V(c["gamma1_local_data_domain_coordinates"]["pole"])
    hh = sp.Matrix(list(pole[:5]) + [0] * 6)
    assert sp.Matrix.hstack(B, hh).rank() == 6
    assert any(x != 0 for x in hh)


def test_quotient_coordinates_rederived():
    """reduce the Gamma1 data modulo D cap Im (= D cap ker here, cohomology 0) onto the complement
    (h.h#0, h.h#1, h.h#2, c.cb#0, c.cb#1): solve data = B y + C z for z, compare with the certificate."""
    c = cj("P19_defect.json")
    labels = c["gamma1_local_data_domain_coordinates"]["labels"]
    comp = c["quotient_coordinates"]["complement_directions"]
    assert comp == ["h.h#0", "h.h#1", "h.h#2", "c.cb#0", "c.cb#1"]
    B = sp.Matrix.hstack(*[V(b) for b in c["route_G"]["D_cap_ker_sigma0_basis"]])
    C = sp.Matrix.hstack(*[sp.Matrix([1 if l == k else 0 for l in labels]) for k in comp])
    M = sp.Matrix.hstack(B, C)
    assert M.rank() == 11
    for part in ("pole", "nonlocal_L", "local"):
        data = V(c["gamma1_local_data_domain_coordinates"][part])
        z = M.LUsolve(data)[6:, 0]
        want = [Z(x) for x in c["quotient_coordinates"][part]]
        assert [sp.nsimplify(sp.simplify(x)) for x in z] == want, part
    # the surviving quotient components are the ghost-sector (c.cb) ones; their pole equals minus the c.K pole
    q = [Z(x) for x in c["quotient_coordinates"]["pole"]]
    assert q[:3] == [0, 0, 0] and q[3:] == [sp.Rational(-3, 8), sp.Rational(1, 4)]


def test_counterterm_solve():
    s = cj("P19_defect.json")["counterterm_solve"]
    assert s["outcome"] == "ZERO" and s["residual"] is None
    assert int(s["rank_P_ch_sigma0_routeG"]) == int(s["rank_routeC"]) == 3
    assert s["MSbar_counterterm_ch_image_zero"] is True
    assert s["MSbar_counterterm_full_sigma0_image_sectors"] == ["c.b"]      # h.h + c.K only (without c.cb)
    # p20 (disclosed): the p19 factor table was computed on UNCONVERTED (cb,c) coordinates -- the K1 error
    cl = s["full_closure_relative_factor_table_UNCONVERTED_p19_error"]
    assert cl == {"1": False, "-1": True, "I": False, "-I": False}
    assert s["K1_ghost_closure_convention"]["full_closure_complete_S_ct"]["closed"] is True


def test_controls_mutations_blind_spots_missing_control():
    c = cj("P19_defect.json")
    assert len(c["controls"]) >= 25 and all(v is True for v in c["controls"].values())
    muts = c["mutations"]
    assert len(muts) == 8 and all(m["changes_outcome"] is True for m in muts.values())
    assert sum(m["outcome"].startswith("OBSTRUCTION") for m in muts.values()) == 7
    g = muts["naive_4D_D13_Gt_dropped"]
    assert g["outcome"].startswith("NONZERO, CANCELLABLE") and g["finite_counterterm"]["solvable"] is True
    assert int(g["finite_counterterm"]["rank"]) == 3
    blind = c["insensitive_variations"]
    assert set(blind) == {"drop_graph_D11", "drop_graph_D13", "flip_row_sign_Kc"}
    assert all(v["changes_outcome"] is False and v["why_blind"] for v in blind.values())
    m = c["missing_control"]["D11_removed_from_inventory"]
    assert m["inventory_ok"] is False and m["projected_defect_computed_if_removed"] == "not_earned"


def test_defect_flags_and_scope():
    c = cj("P19_defect.json")
    for k in QC.EARNABLE_P19:
        assert c[k] == "earned"
    assert c["bulk_symmetry_restored"] is False
    assert c["scope"].startswith("ch projection only")


# ================================================================ status (I1, I3)
def test_p19_release_status_and_flags():
    s = rs()
    assert s["revision"] == "p19" and s["publication"] == "accepted" and s["execution_pass"] is True
    for k in QC.EARNABLE_P19:
        assert s[k] == "earned", k
    assert s["quantum_inputs_evaluated"] == "earned"     # (p20: s is the p19 layer record)
    assert s["bulk_symmetry_restored"] is False and s["symmetry_restored"] is False
    assert s["O1_closure"] == "NOT_CLOSED" and s["XVI_P_registered"] is False and s["Route_B_discharged"] is F
  +> alse
    assert s["u_R_c_delta_added"] is False and s["XV_B_opened"] is False and s["XIV_J_opened"] is False
    assert s["evanescent_hh_counterterm_added"] is False
    assert s["insertion_status"] == "Frozen_negative_obstruction_preserved"
    assert s["XVI_M_sha256"].startswith("41aa1099") and s["XVI_M_pin_ok"] is True
    assert s["hard_stops"] == QC.HARD_STOPS_P19 and s["hard_stops_hold"] is True
    assert s["independent_rebuild_passed"] in ("pending", False)   # p20: the live p19 report is bound to the 
  +> p19 tree
    assert s["contract_identity"]["added"] == [] and s["contract_identity"]["changed_vs_p14r"] == ["code/p5_en
  +> try/dred.py"]
    assert "quantum_inputs_evaluated (p18 layer + recheck)" in s["publication_gated_on"]


def test_i3_milestone_wording():
    st = rs()["milestones"]["status"]
    assert st["P.5_calculation"].startswith("evaluated; 4D sector renormalized (MS-bar, declared domain); evan
  +> escent "
                                     "regulated (poles retained, not subtracted), decoupled from the ch slots"
  +> )
    assert "renormalized" in st["P.5_calculation"] and "evanescent regulated" in st["P.5_calculation"]


def test_p18_independent_rebuild_recorded_and_not_inherited():
    s = rs()
    rec = s["p18_independent_rebuild"]
    assert s["independent_rebuild_passed_p18"] is True
    assert rec["report_sha256"] == QC.P18_INDEPENDENT_REPORT_SHA256 and rec["pins_ok"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P18_SOURCE_TREE_SHA256
    assert rec["bound_to_source_zip_sha256"] == QC.P18_SOURCE_ZIP_SHA256 and rec["mismatches"] == 0
    import source_manifest as SM
    assert SM.tree_sha(ROOT) != QC.P18_SOURCE_TREE_SHA256


def test_change_log_vs_p18():
    cl = rs()["change_log_vs_p18"]
    assert cl["base_pinned_ok"] is True
    base = json.loads((ROOT / QC.P18_SOURCE_LIST).read_text())["files"]
    import source_manifest as SM
    cur = {r: hashlib.sha256((ROOT / r).read_bytes()).hexdigest() for r in SM.source_files(ROOT) if r != SM.RE
  +> FERENCE_FILE}
    changed = sorted(set(cur) ^ set(base) | {k for k in set(cur) & set(base) if cur[k] != base[k]} | {SM.REFER
  +> ENCE_FILE})
    assert sorted(cl["added"] + cl["removed"] + cl["modified"]) == changed
    assert [x for x in cl["contract_files_changed"] if not CR.registered_contract_change(x)] == []   # p22: re
  +> gistered
    assert sorted(x for x in cl["modified"] if x.startswith("tests/") and not __import__("contract_registry").
  +> p22_revised(x)) == sorted(   # p22 filter
        x for x in QC.DISCLOSED_TEST_REVISIONS_P19 if not __import__("contract_registry").p22_revised(x))
    for f in ("code/p5_calc/defect.py", "code/p5_calc/release_p19.py", "code/p5_calc/p19_conventions.py",
              "tests/test_p19.py"):
        assert f in cl["added"], f


def test_p18_calc_layer_byte_identical():
    for k, h in QC.P18_CALC_SHA256.items():   # p22: or the registered p22 revision of that layer file
        assert CR.layer_file_ok(k, hashlib.sha256((ROOT / k).read_bytes()).hexdigest(), h), k


def test_version_label_p19():
    import build as B
    assert QC.VERSION_LABEL == "XVI-P p19" and B.QC.VERSION_LABEL == f"XVI-P {B.QC.REVISION}"   # p20: current
  +>  label
    assert "certificates/P19_defect.json" in B.VALUE_BLOCKS


# ================================================================ p19 gate mutations (I1: fail closed)
def _copy():
    d = Path(tempfile.mkdtemp(prefix="p19gate_"))
    for sub in ("code", "certificates", "ledgers", "exports", "tools", "archival", "reproducibility", "provena
  +> nce", "tests"):
        if (ROOT / sub).exists():
            shutil.copytree(ROOT / sub, d / sub, ignore=shutil.ignore_patterns("__pycache__", "*.zip", "*.pdf"
  +> ))
    for f in ("README.md", "REBUILD_INSTRUCTIONS.md", "RELEASE_STATUS.json"):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, d / f)
    (d / "manuscript").mkdir()
    return d


def _edit_cert(d, name, fn):
    f = d / "certificates" / name
    c = json.loads(f.read_text())
    fn(c)
    f.write_text(json.dumps(c, indent=1))


def _p18_layer_q_not_earned(d):              # I1
    _edit_cert(d, "P18_release.json", lambda c: c.__setitem__("quantum_inputs_evaluated", "not_earned"))


def _inventory_hole_d13(d):                   # I1: in p18 this published with q not earned; p19 fails closed
    _edit_cert(d, "P15_D13.json", lambda c: c["D13_evaluated"].__setitem__("execution", False))


def _inventory_hole_d11(d):
    _edit_cert(d, "P18_D11.json", lambda c: c.__setitem__("D11_evaluated", False))


def _defect_not_computed(d):
    _edit_cert(d, "P19_defect.json", lambda c: c.__setitem__("projected_defect_computed", "not_earned"))


def _identity_without_computed(d):
    _edit_cert(d, "P19_defect.json", lambda c: c.__setitem__("projected_defect_computed", "not_earned"))
    _edit_cert(d, "P19_defect.json", lambda c: c.__setitem__("projected_identity_verified", "earned"))


def _defect_control_false(d):
    _edit_cert(d, "P19_defect.json", lambda c: c["controls"].__setitem__("E_transverse", False))


def _defect_mutation_silent(d):
    _edit_cert(d, "P19_defect.json", lambda c: c["mutations"]["flip_phase_D03"].__setitem__("changes_outcome",
  +>  False))


def _defect_mutation_removed(d):
    _edit_cert(d, "P19_defect.json", lambda c: c["mutations"].pop("wrong_projection_trace_operator_hh"))


def _missing_control_broken(d):
    _edit_cert(d, "P19_defect.json", lambda c: c["missing_control"]["D11_removed_from_inventory"].__setitem__(
        "changes_outcome", False))


def _bulk_claimed(d):
    _edit_cert(d, "P19_defect.json", lambda c: c.__setitem__("bulk_symmetry_restored", True))


def _assignment_dropped(d):
    _edit_cert(d, "P19_defect.json", lambda c: c["defect"].pop("c hat, h tilde"))


def _tamper_p18_layer(d):
    f = d / "code" / "p5_calc" / "d11.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _dred_code_change(d):
    f = d / "code" / "p5_entry" / "dred.py"
    f.write_text(f.read_text() + "\n_TAMPER = 1\n")


def _new_contract_file(d):
    (d / "code" / "p5_entry" / "evanescent_hh_counterterm.py").write_text("# undisclosed contract file\n")


def _tamper_p18_report(d):
    f = d / "archival" / "p18" / "reproducibility" / "independent_rebuild_report_p18.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


MUTS = [_p18_layer_q_not_earned, _inventory_hole_d13, _inventory_hole_d11, _defect_not_computed,
        _identity_without_computed, _defect_control_false, _defect_mutation_silent, _defect_mutation_removed,
        _missing_control_broken, _bulk_claimed, _assignment_dropped, _tamper_p18_layer, _dred_code_change,
        _new_contract_file, _tamper_p18_report]


def _run(d):
    return subprocess.run([sys.executable, "code/p5_calc/release_p19.py"], cwd=d, capture_output=True, text=Tr
  +> ue,
                          timeout=600)


@pytest.mark.parametrize("mut", MUTS, ids=lambda f: f.__name__)
def test_certificate_mutation_p19_gate_rejects(mut):
    d = _copy()
    try:
        mut(d)
        r = _run(d)
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d / "certificates" / "P19_release.json").exists()
        assert (d / "certificates" / "P19_release_rejected.json").exists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_p19_gate_accepts_unmodified_copy():
    d = _copy()
    try:
        r = _run(d)
        assert r.returncode == 0, r.stdout[-1500:]
        assert json.loads((d / "RELEASE_STATUS.json").read_text())["quantum_inputs_evaluated"] == "earned"
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ================================================================ honesty pass (user 07:12: a-d)
def test_a_why_zero_and_rests_on():
    c = cj("P19_defect.json")
    w = c["why_zero"]
    assert "each surviving ch row vanishes separately" in w and "no counterterm cancellation" in w
    assert "A_T1 = A_E1 = 0" in w and "tadpoles D14a-c vanish" in w and "transverse" in w
    r = " ".join(c["rests_on"])
    assert "4D components only" in r and "evanescent decoupling proofs" in r
    assert c["counterterm_solve"]["outcome"] == "ZERO"
    s = rs()
    assert "WHY ZERO" in s["claim_status"] and "RESTS ON" in s["claim_status"]


def test_b_flag_definitions_distinct_and_content_backed():
    c = cj("P19_defect.json")
    fd = c["flag_definitions"]
    assert set(fd) >= set(QC.EARNABLE_P19) | {"bulk_symmetry_restored"}
    # p20 (disclosed): restoration REDEFINED as full sigma_0 closure of the complete MS-bar S_ct (incl. c.cb)
    assert "REGULATED" in fd["projected_identity_verified"] and "COMPLETE" in fd["projected_restoration_verifi
  +> ed"]
    assert "NOT bulk symmetry" in fd["projected_restoration_verified"]
    assert fd["projected_identity_verified"] != fd["projected_restoration_verified"]
    assert c["renormalised_defect_zero"] is True and c["route_consistency_control_p19_criterion"]["holds"] is 
  +> True
    assert c["counterterm_solve"]["MSbar_counterterm_ch_image_zero"] is True
    s = rs()
    assert s["flag_definitions"] == fd and s["bulk_symmetry_restored"] is False and s["O1_closure"] == "NOT_CL
  +> OSED"
    sc = s["projected_restoration_scope"]
    assert sc.startswith("p20 definition: full sigma_0 closure") and "NOT bulk symmetry, NOT O.1" in sc
    assert "NOT bulk symmetry" in s["claim_status"] and "RETRACTED" in s["claim_status"]


def test_tex_escaping_of_results_table():
    import release_p19 as RP
    assert RP.tex("h.h#0 50% $x~{y}") == "\\texttt{h.h\\#0 50\\% \\$x\\textasciitilde{}\\{y\\}}"
    tab = (ROOT / "manuscript" / "body" / "P19-results-table.tex").read_text()
    import re
    assert not re.search(r"(?<!\\)#", tab)


def test_c_j1_disclosed_as_p14r_finding_contract_unchanged():
    c = cj("P19_defect.json")
    j = c["findings"]["J1_p14r_counterterm_domain_field"]
    assert j.startswith("FINDING ABOUT THE p14r CONTRACT (contract NOT modified)")
    p14 = cj("P14_counterterm_domain.json")                     # the released p14r certificate is untouched
    assert p14 and rs()["contract_identity"]["changed_vs_p14r"] == ["code/p5_entry/dred.py"]
    assert "J1" in rs()["claim_status"]


def test_d_k1_corrected_in_p20():
    """K1 (p20, disclosed revision; the p19 'closure fails / needs -1' conclusion is RETRACTED): the derived f
  +> actor +1
    closes the complete MS-bar counterterm once Sigma is converted to the route-G (c,cb) orientation (ratio -1
  +> )."""
    k = cj("P19_defect.json")["counterterm_solve"]["K1_ghost_closure_convention"]
    assert k["M_2iD_cK_to_cbc"] == [["0", "2"], ["-1", "0"], ["0", "-1"]]
    assert k["derived_equals_P15"] is True
    assert k["z_cb_derived_from_cK_pole_cbc_orientation"] == k["z_cb_P15_sigma_fit_cbc_orientation"] == ["-3/8
  +> ", "1/4"]
    assert k["relative_factor_derived"] == "1" and k["orientation_ratio_routeG_over_cbc"] == ["-1", "-1"]
    assert k["Sigma_pole_routeG_c_cb_coordinates"] == ["3/8", "-1/4"]
    assert k["full_closure_complete_S_ct"] == {"closed": True, "entries": 0, "sectors": []}
    assert k["full_closure_unconverted (p19 error)"]["sectors"] == ["c.b"]
    assert cj("P19_defect.json")["controls"]["ghost_equation_relation_reproduces_P15_sigma_pole"] is True
    cs = rs()["claim_status"]
    assert "RETRACTED" in cs and "selected by a scan" not in cs and "for which full closure fails" not in cs


def _restoration_without_content(d):        # p20: the content is full closure of the complete MS-bar S_ct
    _edit_cert(d, "P19_defect.json", lambda c: c["counterterm_solve"]["K1_ghost_closure_convention"][
        "full_closure_complete_S_ct"].__setitem__("closed", False))


def _k1_record_removed(d):
    _edit_cert(d, "P19_defect.json", lambda c: c["counterterm_solve"].pop("K1_ghost_closure_convention"))


def test_restoration_flag_withheld_without_content():
    d = _copy()
    try:
        _restoration_without_content(d)
        r = _run(d)
        if r.returncode == 0:      # may publish, but must NOT earn restoration
            assert json.loads((d / "RELEASE_STATUS.json").read_text())["projected_restoration_verified"] == "n
  +> ot_earned"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_k1_record_required():
    d = _copy()
    try:
        _k1_record_removed(d)
        assert _run(d).returncode == 1
    finally:
        shutil.rmtree(d, ignore_errors=True)
