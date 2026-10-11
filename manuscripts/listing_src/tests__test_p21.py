"""XVI-P p21 tests: absolute D11 pin (sign and magnitude derived from 1/2 Tr ln under the declared conventions
  +> );
gate fixes (top-level pin status, lower layers re-checked); ALLOW-LIST scan + runtime opaque-d check for the
d-evaluation contract (a check, NOT A PROOF); disclosure fixes; p21 gate fail-closed with no stale RELEASE_STA
  +> TUS."""
from __future__ import annotations
import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
for p in ("code/p5_calc", "code/p5_entry", "code/classical", "tools", "tests"):
    sys.path.insert(0, str(ROOT / p))
import p21_conventions as QC  # noqa: E402
import p23_conventions as QS  # noqa: E402   (p23: scan allow-lists incl. the reviewed p22/p23 guard sites)

CERT = ROOT / "certificates"
SCAN_DIRS = ("code/p5_calc", "code/p5_entry")


def cj(name):
    return json.loads((CERT / name).read_text())


def rs():
    return json.loads((CERT / "P21_release.json").read_text())      # p22: the p21 LAYER record


# ================================================================ A: absolute D11 pin
def test_absolute_pin_certificate():
    c = cj("P20_D11_pin.json")
    a = c["absolute_pin"]
    d = a["derivation_p21"]
    assert a["status"] == "PASS" and c["absolute_pin_status"] == a["status"] and c["D11_absolute_pin_verified"
  +> ] is True
    assert all(v is True for v in d["package_declarations_checked"].values()) and len(d["package_declarations_
  +> checked"]) == 8
    st = d["steps"]
    assert st["1_G_equals_Gamma2"] == "1" and st["2_wick_sign_s_W_from_N_eps_and_Ihat_pole"] == "1"
    assert st["3_i_S_M_over_S_E (must be -1)"] == "-1" and st["4_L_M_eff_over_L_E_eff"] == "-1"
    assert st["6_minkowski_quadratic_forms"]["C2"] == {"P2": "1/2", "P0s": "0"}
    assert st["6_minkowski_quadratic_forms"]["R2"] == {"P2": "0", "P0s": "3"}
    assert d["package_Gamma2_pole_per_kappa2_over_eps"] == {"spin2": "1/(3840*pi**2)", "spin0s": "1/(384*pi**2
  +> )"}
    assert d["heat_kernel_prediction_per_kappa2_over_eps"] == d["package_Gamma2_pole_per_kappa2_over_eps"]
    assert d["ratio_package_over_prediction"] == {"spin2": "1", "spin0s": "1"}
    assert d["convention_choices_external"].startswith("none")


def test_absolute_pin_live_and_mutations():
    import d11_pin as P
    import covariant as C
    eta = tuple(int(x) for x in C.ETA)
    p = (sp.Integer(2), sp.Rational(1, 3), sp.Integer(-1), sp.Integer(4))
    c2, c0 = -sp.I / 240, -sp.I / 24
    assert P.absolute_pin(c2, c0, eta, p)[1] is True
    assert P.absolute_pin(2 * c2, 2 * c0, eta, p)[1] is False          # x2
    assert P.absolute_pin(-c2, -c0, eta, p)[1] is False                # sign flip
    assert P.absolute_pin(sp.I * c2, sp.I * c0, eta, p)[1] is False    # phase error
    assert P.absolute_pin(c2, 2 * c0, eta, p)[1] is False              # spin-0 only
    # 2 x pole magnitude = kappa^2/(240 16 pi^2) (reviewer's magnitude): N_eps c2 = 1/(240 16 pi^2)
    assert sp.simplify(sp.I / (16 * sp.pi ** 2) * c2 - 1 / (240 * 16 * sp.pi ** 2)) == 0


def test_absolute_pin_minkowski_forms_match_euclidean():
    import d11_pin as P
    p = (sp.Integer(1), sp.Integer(2), sp.Integer(-3), sp.Rational(1, 2))
    fm = P.curvature_forms_eta(p, (1, -1, -1, -1))
    fe = P.curvature_forms(p)
    assert fm == fe


def test_absolute_pin_breaks_if_a_declared_convention_changes(monkeypatch):
    import d11_pin as P
    import conventions as CC
    import covariant as C
    eta = tuple(int(x) for x in C.ETA)
    p = (sp.Integer(2), sp.Rational(1, 3), sp.Integer(-1), sp.Integer(4))
    monkeypatch.setattr(CC, "METRIC_PARAMETRISATION", "g_{mu nu} = eta_{mu nu} + 2 kappa h_{mu nu}")
    assert P.absolute_pin(-sp.I / 240, -sp.I / 24, eta, p)[1] is False


# ================================================================ G: gate fixes
def test_p20_gate_checks_top_level_and_lower_layers():
    import release_p20 as R
    ok, chk, _ = R.d11_pin_check()
    assert ok and chk["top_level_absolute_status_consistent"] and chk["top_level_ratio_status_consistent"]
    ok19, l19, _ = R.p19_layer()
    assert ok19 and l19["lower_layers_rechecked_p21"]["P18_quantum_inputs_evaluated"] == "earned"


# ================================================================ S: allow-list scan (a check, NOT A PROOF)
def _fn_index(tree):
    fn = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for c in ast.walk(n):
                fn.setdefault(id(c), n.name)
    return fn


def _mentions_d(node, bare=False):
    """node is / contains the dimension: Name 'd' or attribute '.d' (dred.d, D.d); bare: node itself only."""
    def is_d(x):
        return (isinstance(x, ast.Name) and x.id == "d") or (isinstance(x, ast.Attribute) and x.attr == "d")
    return is_d(node) if bare else any(is_d(x) for x in ast.walk(node))


def scan4(path, root=ROOT):
    """ALLOW-LIST scan.  Refuses, except at reviewed sites: (a) ANY access to an expression-tree decomposer
    (QC.DECOMPOSE_ATTRS: .args, make_args, as_ordered_terms, as_coefficients_dict, ...), whatever is done with
  +>  the
    result afterwards (variable, map, sum, starred rebuild); (b) binding any sympy attribute other than the al
  +> lowed
    constants to a name (Q = sp.Poly), and any 'import sympy as X' / 'from sympy import Y as Z' alias; (c) a s
  +> ympy
    symbol constructor whose name is not a literal (starred, **kwargs, non-literal keyword, computed name);
    (d) p21 runtime finding: a value call (QC.VALUE_CALLS: subs, evalf, N, limit, Lambda, ...) whose arguments
  +>  mention
    d, and any binding of d to another name (D = dred.d) -- the runtime guard does NOT intercept subs when d o
  +> ccurs
    only as a power base, so subs on d is refused statically except at reviewed demonstration sites.
    Returns a list of violations (site keys)."""
    src = Path(path).read_text()
    tree = ast.parse(src)
    fn = _fn_index(tree)
    rel = Path(path).resolve().relative_to(root.resolve()).as_posix() if Path(path).is_absolute() or True else
  +>  path
    sympy_names = {"sp", "sympy"}
    out = []

    def key(n):
        return f"{rel}::{fn.get(id(n), '<module>')}::{ast.get_source_segment(src, n)}"

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] == "sympy" and a.asname not in (None, "sp"):
                    out.append(f"ALIAS {key(n)}")
        if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "sympy":
            for a in n.names:
                if a.asname is not None or a.name not in QC.SYMPY_ALIAS_ALLOWED:
                    out.append(f"ALIAS {key(n)}")
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            v = n.value
            if isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name) and v.value.id in sympy_names \
                    and v.attr not in QC.SYMPY_ALIAS_ALLOWED:
                out.append(f"ALIAS {key(n)}")
            if isinstance(v, ast.Name) and v.id in sympy_names:
                out.append(f"ALIAS {key(n)}")
        if isinstance(n, ast.Attribute) and n.attr in QC.DECOMPOSE_ATTRS:
            out.append(f"DECOMPOSE {key(n)}")
        if isinstance(n, ast.Name) and n.id in QC.DECOMPOSE_ATTRS and isinstance(n.ctx, ast.Load):
            out.append(f"DECOMPOSE {key(n)}")
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.NamedExpr)) and _mentions_d(n.value, bare=True):
            tg = getattr(n, "targets", None) or [n.target]
            if not all(isinstance(x, ast.Name) and x.id == "d" for x in tg):
                out.append(f"DALIAS {key(n)}")
        if isinstance(n, ast.Call):
            f = n.func
            fname = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if fname in QC.VALUE_CALLS and any(_mentions_d(a) for a in list(n.args) + [k.value for k in n.keyw
  +> ords]):
                out.append(f"DVALUE {key(n)}")
            is_maker = ((isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in symp
  +> y_names
                         and f.attr in QC.SYMBOL_MAKERS) or (isinstance(f, ast.Name) and f.id in QC.SYMBOL_MAK
  +> ERS))
            if is_maker:
                bad = any(isinstance(a, ast.Starred) for a in n.args) or any(k.arg is None for k in n.keywords
  +> )
                bad |= any(k.arg in ("name", "names") and not isinstance(k.value, ast.Constant) for k in n.key
  +> words)
                lit = [k.value for k in n.keywords if k.arg in ("name", "names")] + n.args[:1]
                for a in lit:
                    if isinstance(a, ast.Constant):
                        bad |= not isinstance(a.value, str) or "d" in a.value.replace(",", " ").split()
                    elif isinstance(a, ast.JoinedStr):
                        head = a.values[0] if a.values else None
                        bad |= not (isinstance(head, ast.Constant) and str(head.value) not in ("", "d"))
                    else:
                        bad = True
                if bad:
                    out.append(f"SYMBOL {key(n)}")
    return out


def _package_violations():
    v = []
    for d in SCAN_DIRS:
        for f in sorted((ROOT / d).glob("*.py")):
            v += scan4(f)
    return v


def _unreviewed(viol):
    reviewed = {**{f"DECOMPOSE {k}": c for k, c in ((k, QS.DECOMPOSE_SITE_COUNTS.get(k, 1))
                                                     for k in QS.DECOMPOSE_SITES_REVIEWED)},
                **{f"SYMBOL {k}": 1 for k in QS.SYMBOL_SITES_REVIEWED},
                **{f"ALIAS {k}": 1 for k in QS.SYMPY_FROM_IMPORT_REVIEWED},
                **{f"DVALUE {k}": QS.DVALUE_SITE_COUNTS.get(k, 1) for k in QS.DVALUE_SITES_REVIEWED},
                **{f"DALIAS {k}": 1 for k in QS.DALIAS_SITES_REVIEWED}}
    cnt = Counter(viol)
    return {k: c for k, c in cnt.items() if reviewed.get(k) != c} | \
        {k: 0 for k in reviewed if k not in cnt}


def test_scan4_package_clean_against_allow_list():
    assert _unreviewed(_package_violations()) == {}


REVIEWER_PLANTS_P20 = {   # the 8 misses of test_p18.scan + test_p20.scan3 reported by the p20 independent reb
  +> uild
    "assign_alias_Poly": "import sympy as sp\nQ = sp.Poly\ndef f(e, d):\n    return Q(e, d).eval(4)\n",
    "map_over_args_rebuild": ("import sympy as sp\ndef f(e, d):\n"
                              "    return sp.Add(*map(lambda t: t.xreplace({}), e.args))\n"),
    "args_via_variable": "import sympy as sp\ndef f(e):\n    a = e.args\n    return sp.Add(*[t for t in a])\n"
  +> ,
    "ordered_terms_rebuild": "import sympy as sp\ndef f(e):\n    return sp.Add(*e.as_ordered_terms())\n",
    "builtin_sum_over_args": "def f(e):\n    return sum(t for t in e.args)\n",
    "symbol_starred_literal": "import sympy as sp\nd = sp.Symbol(*['d'])\n",
    "symbol_kwargs_dict": "import sympy as sp\nd = sp.Symbol(**{'name': chr(100)})\n",
    "make_args_rebuild": "import sympy as sp\ndef f(e):\n    return sp.Add(*[t for t in sp.Add.make_args(e)])\
  +> n",
}
EXTRA_PLANTS = {
    "from_import_alias": "from sympy import Poly as Q\n",
    "module_alias": "import sympy as S2\n",
    "module_rebind": "import sympy as sp\nX = sp\n",
    "func_rebuild": "def f(e):\n    return e.func(*e.args)\n",
    "coeff_dict": "def f(e):\n    return e.as_coefficients_dict()\n",
    "preorder": "from sympy import preorder_traversal\n",
    "symbol_computed": "import sympy as sp\nd = sp.Symbol(chr(100))\n",
    "symbol_kw_computed": "import sympy as sp\nd = sp.Symbol(name=chr(100))\n",
    "symbols_literal_d": "import sympy as sp\na, d = sp.symbols('a d')\n",
    "symbol_fstring_d": "import sympy as sp\nd = sp.Symbol(f'{chr(100)}')\n",
    "subs_d_power_base": "import dred\ndef f(e):\n    return e.subs(dred.d, 4)\n",
    "subs_d_dict": "from dred import d\ndef f(e):\n    return e.subs({d: 4})\n",
    "d_rebound": "import dred\nD = dred.d\n",
    "evalf_subs_d": "from dred import d\ndef f(e):\n    return e.evalf(subs={d: 4})\n",
    "walrus_alias": "import sympy as sp\nif (P := sp.Poly):\n    pass\n",
}


@pytest.mark.parametrize("name", sorted(REVIEWER_PLANTS_P20) + sorted(EXTRA_PLANTS))
def test_scan4_detects_plants(name, tmp_path):
    src = {**REVIEWER_PLANTS_P20, **EXTRA_PLANTS}[name]
    f = tmp_path / "plant.py"
    f.write_text(src)
    assert scan4(f, root=tmp_path), name


def test_scan4_reviewer_plants_were_missed_by_pattern_scans(tmp_path):
    """honesty control: the reviewer's misses really pass the older pattern scans (so the allow-list adds cove
  +> rage)."""
    import test_p20 as T20
    missed = 0
    for name, src in REVIEWER_PLANTS_P20.items():
        f = tmp_path / f"{name}.py"
        f.write_text(src)
        try:
            hits = [x for part in T20.scan3(f, root=tmp_path) for x in part]   # scan3 -> (list, list)
        except Exception:      # noqa: BLE001
            hits = ["error"]
        missed += not hits
    assert missed == len(REVIEWER_PLANTS_P20) == 8


def test_scan4_allows_benign_forms(tmp_path):
    f = tmp_path / "ok.py"
    f.write_text("import sympy as sp\nI = sp.I\nx = sp.Symbol('x')\ny = sp.Symbol(f'p{3}')\n"
                 "a, b = sp.symbols('a b')\ndef g(e):\n    return sp.expand(e * x)\n")
    assert scan4(f, root=tmp_path) == []


def test_scan_wording_honest():
    txt = (ROOT / "README.md").read_text()
    assert "allow-list" in txt and "not a proof" in txt


# ---------------------------------------------------------------- runtime opaque-d check
def test_runtime_stored_exact_d_amplitudes_carry_opaque_d_and_reproduce_poles():
    """RUNTIME check: every stored exact-d D11 amplitude re-parses (parse_d) with the OPAQUE d (type check), c
  +> annot be
    evaluated at d = 4 by xreplace/replace/lambdify (subs: limitation recorded below), and reproduces its stor
  +> ed UV pole only via the authorised
    substitute_d path (integrals.laurent)."""
    import dred
    import integrals as IL
    res = cj("P18_D11.json")["result"]
    n = 0
    for k, v in res.items():
        A = dred.parse_d(str(v["A_exact_d_times_MB"]), {"I": sp.I})
        dsyms = [s for s in A.free_symbols if s.name == "d"]
        assert all(isinstance(s, dred.OpaqueDimension) for s in dsyms), k
        if dsyms:
            for bad in (lambda e: e.xreplace({dred.d: 4}),          # subs: see the recorded limitation below
                        lambda e: e.replace(dred.d, 4), lambda e: sp.lambdify(dred.d, e)(4)):
                with pytest.raises(dred.PrematureD4Substitution):
                    bad(A)
        pole = IL.laurent(A * IL.master_exact(), 0)[-1]
        assert sp.simplify(pole - dred.parse_d(str(v["UV_pole"]), {"I": sp.I})) == 0, k
        n += 1
    assert n >= 5


def test_runtime_guard_subs_limitation_recorded():
    """p21 finding (disclosed, contract unchanged): expr.subs(d, v) is NOT intercepted when d occurs only as a
  +>  power
    base (sympy's Pow substitution does not call the symbol's _subs).  The package has no such value path (sta
  +> tic
    rule (d) of scan4); the released premature-d4 demonstrations used components that DO raise."""
    import dred
    A = dred.parse_d("1/(d**2 - 1)")
    with pytest.raises(dred.PrematureD4Substitution):         # p22: the p21 limitation is CLOSED by the runti
  +> me guard
        A.subs(dred.d, 4)
    with pytest.raises(dred.PrematureD4Substitution):
        dred.parse_d("1/(d - 1)").subs(dred.d, 4)
    assert "power base" in QC.RUNTIME_GUARD_LIMITATION_P21
    for f, path in (("P18_D11.json", ("mutations", "premature_d4")), ("P16_batchC.json", ("mutations", "premat
  +> ure_d4"))):
        x = cj(f)
        for p in path:
            x = x[p]
        assert x["rejected"] is True, f


# ================================================================ D: disclosure
def test_p19_note_edit_disclosed():
    md = QC.DISCLOSED_MANUSCRIPT_REVISIONS["manuscript/notes/P19_defect.tex"]
    cur = hashlib.sha256((ROOT / "manuscript/notes/P19_defect.tex").read_bytes()).hexdigest()
    assert cur == md["p20_sha256"] != md["p19_sha256"] and md["revised_in"] == "p20"
    assert rs()["manuscript_disclosure"]["manuscript/notes/P19_defect.tex"]["current_equals_disclosed_p20"] is
  +>  True


def test_change_log_key_renamed():
    s = rs()
    assert "p19_layer_change_log_vs_p18" not in s and "p19_gate_change_log_vs_p18_recomputed_on_current_tree" 
  +> in s
    src = (ROOT / "tools" / "rebuild_from_source.py").read_text()       # the reference-value generator
    assert '"change_log_vs_p18":' not in src and '"change_log_vs_p19":' not in src
    assert '"p19_gate_change_log_vs_p18_recomputed_on_current_tree"' in src
    assert '"p20_gate_change_log_vs_p19_recomputed_on_current_tree"' in src


# ================================================================ status
def test_p21_release_status_and_flags():
    s = rs()
    assert s["revision"] == "p21" and s["publication"] == "accepted" and s["execution_pass"] is True
    for k in QC.EARNABLE_P21:
        assert s[k] == "earned", k
    assert s["bulk_symmetry_restored"] is False and s["symmetry_restored"] is False and s["O1_closure"] == "NO
  +> T_CLOSED"
    assert s["hard_stops"] == QC.HARD_STOPS_P21 and s["hard_stops_hold"] is True
    assert s["independent_rebuild_passed"] is not True and s["independent_rebuild_passed_p20"] is True   # p22
  +>  tree
    assert s["open_pins"] == list(QC.OPEN_PINS_P21) and s["lower_layers"]["rechecked_live"] is True
    assert s["change_log_vs_p20"]["undisclosed_package_changes"] == []


def test_p20_independent_recorded_and_not_inherited():
    rec = rs()["p20_independent_rebuild"]
    assert rec["report_sha256"] == QC.P20_INDEPENDENT_REPORT_SHA256 and rec["pins_ok"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P20_SOURCE_TREE_SHA256
    assert rec["bound_to_source_zip_sha256"] == QC.P20_SOURCE_ZIP_SHA256 and rec["mismatches"] == 0
    import source_manifest as SM
    assert SM.tree_sha(ROOT) != QC.P20_SOURCE_TREE_SHA256


def test_layers_and_disclosed_revisions():
    assert hashlib.sha256((ROOT / "code/p5_calc/p20_conventions.py").read_bytes()).hexdigest() == QC.P20_CONVE
  +> NTIONS_SHA256
    for k, h in QC.P20_RELEASED_SHA256.items():
        assert hashlib.sha256((ROOT / k).read_bytes()).hexdigest() != h and k in QC.DISCLOSED_P20_LAYER_REVISI
  +> ONS_P21


def test_change_log_vs_p20():
    cl = rs()["change_log_vs_p20"]
    import contract_registry as CR                                # p22: the p22 revised files are disclosed t
  +> here
    assert cl["base_pinned_ok"] is True and cl["contract_files_changed"] == []
    assert sorted(x for x in cl["modified"] if x.startswith("tests/") and x not in CR.P22_REVISED_FILES) == \
        sorted(x for x in QC.DISCLOSED_TEST_REVISIONS_P21 if x not in CR.P22_REVISED_FILES)
    import contract_registry as CR                                # p22: the p22 revised files are disclosed t
  +> here
    assert sorted(x for x in cl["modified"] if x.startswith("code/") and x not in CR.P22_REVISED_FILES) == \
        sorted(x for x in QC.DISCLOSED_P20_LAYER_REVISIONS_P21 if x not in CR.P22_REVISED_FILES)
    for f in ("code/p5_calc/p21_conventions.py", "code/p5_calc/release_p21.py", "tests/test_p21.py"):
        assert f in cl["added"], f


def test_version_label_p21():
    import build as B
    assert QC.VERSION_LABEL == "XVI-P p21" and B.QC.VERSION_LABEL == f"XVI-P {B.QC.REVISION}"   # p22: current
  +>  label


# ================================================================ p21 gate mutations (fail closed; no stale s
  +> tatus)
def _copy():
    import test_p20 as T20
    d = T20._copy()
    import source_manifest as SM
    for rel in SM.source_files(ROOT):          # the p21 gate checks the change log of the whole source tree
        if not (d / rel).exists():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / rel, d / rel)
    return d


def _edit(d, name, fn):
    f = d / "certificates" / name
    c = json.loads(f.read_text())
    fn(c)
    f.write_text(json.dumps(c, indent=1))


def _abs_fail(d):
    _edit(d, "P20_D11_pin.json", lambda c: c["absolute_pin"].__setitem__("status", "FAIL"))


def _abs_top_level_inconsistent(d):
    _edit(d, "P20_D11_pin.json", lambda c: c.__setitem__("absolute_pin_status", "OPEN"))


def _abs_x2_undetected(d):
    _edit(d, "P20_D11_pin.json", lambda c: c["mutations"]["D11_normalisation_x2"].__setitem__(
        "detected_by_absolute_pin", False))


def _p18_q_not_earned(d):
    _edit(d, "P18_release.json", lambda c: c.__setitem__("quantum_inputs_evaluated", "not_earned"))


def _p20_layer_rejected(d):
    _edit(d, "P20_release.json", lambda c: c.__setitem__("publication", "REJECTED"))


def _p20_conventions_changed(d):
    f = d / "code" / "p5_calc" / "p20_conventions.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _undisclosed_code_change(d):
    f = d / "code" / "p5_calc" / "hh_slot.py"
    f.write_text(f.read_text() + "\n# undisclosed\n")


def _tamper_p20_report(d):
    f = d / "archival" / "p20" / "reproducibility" / "independent_rebuild_report_p20.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


def _p19_note_changed(d):
    f = d / "manuscript" / "notes" / "P19_defect.tex"
    f.write_text(f.read_text() + "\n% edit\n")


def _k1_closure_broken(d):
    _edit(d, "P19_defect.json", lambda c: c["counterterm_solve"]["K1_ghost_closure_convention"][
        "full_closure_complete_S_ct"].__setitem__("closed", False))


MUTS = [_abs_fail, _abs_top_level_inconsistent, _abs_x2_undetected, _p18_q_not_earned, _p20_layer_rejected,
        _p20_conventions_changed, _undisclosed_code_change, _tamper_p20_report, _p19_note_changed, _k1_closure
  +> _broken]


def _run(d, script="code/p5_calc/release_p21.py"):
    return subprocess.run([sys.executable, script], cwd=d, capture_output=True, text=True, timeout=600)


@pytest.mark.parametrize("mut", MUTS, ids=lambda f: f.__name__)
def test_certificate_mutation_p21_gate_rejects_without_stale_status(mut):
    d = _copy()
    try:
        assert (d / "RELEASE_STATUS.json").exists()
        mut(d)
        r = _run(d)
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d / "certificates" / "P21_release.json").exists()
        assert (d / "certificates" / "P21_release_rejected.json").exists()
        assert not (d / "RELEASE_STATUS.json").exists() and not (d / "certificates" / "RELEASE_STATUS.json").e
  +> xists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_p21_gate_accepts_unmodified_copy():
    d = _copy()
    try:
        r = _run(d)
        assert r.returncode == 0, r.stdout[-1500:]
        s = json.loads((d / "RELEASE_STATUS.json").read_text())
        assert s["revision"] == "p21" and s["D11_absolute_pin_verified"] == "earned"
        assert s["bulk_symmetry_restored"] is False
    finally:
        shutil.rmtree(d, ignore_errors=True)
