"""XVI-P p16 tests: F3 hardening of the opaque d, F4 version label + value-block readback, E2 decoupling proof,
Batch C (D01, D03), p16 status / hard stops / p15 independent record, F5 change log, p16 gate mutations."""
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
import p16_conventions as QC  # noqa: E402
import p15_conventions as Q15  # noqa: E402
import dred as DR  # noqa: E402

CERT = ROOT / "certificates"
L = sp.Symbol("L")


def cj(name):
    return json.loads((CERT / name).read_text())


def rs():
    """p17 disclosed test revision: the p16 LAYER record (the top-level RELEASE_STATUS.json is the p17 status)."""
    return json.loads((CERT / "P16_release.json").read_text())


# ================================================================ F3: the opaque d cannot be bypassed
@pytest.mark.parametrize("probe", ["replace", "lambdify", "match", "subs", "xreplace", "evalf", "limit"])
def test_f3_opaque_dimension_refuses_bypass(probe):
    d = DR.d
    e = (d - 4) / (d - 1) + d ** 2 + sp.Symbol("x")
    f = {"replace": lambda: e.replace(d, 4), "lambdify": lambda: sp.lambdify(d, e),
         "match": lambda: e.match(d), "subs": lambda: e.subs(d, 4),
         "xreplace": lambda: e.xreplace({d: 4}), "evalf": lambda: e.evalf(subs={d: 4}),
         "limit": lambda: sp.limit(e, d, 4)}[probe]
    with pytest.raises(DR.PrematureD4Substitution):
        f()


def test_f3_authorised_path_and_harmless_operations_still_work():
    d = DR.d
    e = (d - 4) / (d - 1) + d ** 2
    n0 = DR.D_PROVENANCE.get("test_p16: authorised", 0)
    assert DR.substitute_d(e, 4, "test_p16: authorised") == 16
    assert DR.D_PROVENANCE["test_p16: authorised"] == n0 + 1
    assert sp.factor(d ** 2 - 1).has(d) and str(e) and sp.latex(e) and sp.srepr(e)
    assert sp.series(1 / (d - 1), DR.eps).has(d)            # series in another symbol keeps d opaque
    x = sp.Symbol("x")
    assert (e + x).replace(x, 1).has(d) and (e + x).subs(x, 2).has(d)


def _forbidden_calls(path):
    """AST scan: lambdify/ufuncify/autowrap calls, any .eval( call, .replace(d, ...) with d as first argument."""
    tree = ast.parse(path.read_text())
    bad = []
    allowed = {"f3_hardening"}                  # release_p16's own probe of the guard

    def visit(node, fn=None):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = node.name
        if isinstance(node, ast.Call) and fn not in allowed:
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
            if name in ("lambdify", "ufuncify", "autowrap") or name == "eval" and isinstance(f, ast.Attribute):
                bad.append(f"{path.name}:{node.lineno}:{name}")
            if name == "replace" and isinstance(f, ast.Attribute) and node.args:
                a = node.args[0]
                if (isinstance(a, ast.Name) and a.id == "d") or (isinstance(a, ast.Attribute) and a.attr == "d"):
                    bad.append(f"{path.name}:{node.lineno}:replace(d)")
                if isinstance(a, ast.Lambda):        # callable-query replace: cannot be hooked by the guard
                    bad.append(f"{path.name}:{node.lineno}:replace(callable)")
        for ch in ast.iter_child_nodes(node):
            visit(ch, fn)
    visit(tree)
    return bad


def test_f3_static_scan_no_unguarded_value_paths():
    """Paths the guard cannot hook (Poly(expr, d).eval, compiled code) are excluded by a static scan of the package."""
    files = sorted((ROOT / "code" / "p5_calc").glob("*.py")) + sorted((ROOT / "code" / "p5_entry").glob("*.py"))
    bad = [b for f in files for b in _forbidden_calls(f)]
    assert not bad, bad


def test_f3_static_scan_detects_a_planted_violation(tmp_path):
    f = tmp_path / "planted.py"
    f.write_text("import sympy as sp\nfrom dred import d\ndef g(e):\n    return sp.Poly(e, d).eval(4), e.replace(d, 4), "
                 "sp.lambdify(d, e), e.replace(lambda x: x == d, lambda x: 4)\n")
    assert len(_forbidden_calls(f)) == 4


def test_f3_documented_limitation_callable_replace_is_not_hookable():
    """Honest record: a callable-query replace bypasses the runtime guard (no hook exists); it is excluded by the
    static scan above, and the limitation is disclosed in p16_conventions.DISCLOSED_CONTRACT_REVISIONS_P16."""
    d = DR.d
    with pytest.raises(DR.PrematureD4Substitution):    # p22 (disclosed test revision): the d == d hook of the p22 runtime
        (d ** 2).replace(lambda x: x == d, lambda x: sp.Integer(4))          # guard now intercepts this form
    assert "callable query" in json.dumps(QC.DISCLOSED_CONTRACT_REVISIONS_P16)


def test_f3_contract_revision_disclosed():
    rev = QC.DISCLOSED_CONTRACT_REVISIONS_P16
    assert list(rev) == ["code/p5_entry/dred.py"] and "F3" in json.dumps(rev)
    cur = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    assert sorted(k for k, h in Q15.P14R_CONTRACT_SHA256.items() if cur.get(k) != h) == ["code/p5_entry/dred.py"]
    assert set(cur) == set(Q15.P14R_CONTRACT_SHA256)                                   # no new contract file
    assert cur["code/p5_entry/dred.py"] != QC.P15_DRED_SHA256                          # the p16 revision is real
    for k, h in QC.P15_CALC_SHA256.items():                                             # p15 layer byte-identical
        assert hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == h, k


# ================================================================ F4: version label and value-block readback
def test_f4_footer_from_single_version_variable():
    pre = (ROOT / "manuscript" / "preamble.tex").read_text()
    assert "\\XVIPversion" in pre and "\\input{version.tex}" in pre
    code_lines = [ln for ln in pre.splitlines() if not ln.lstrip().startswith("%")]
    assert not any("XVI-P p1" in ln for ln in code_lines)                           # no literal label left
    import build as B
    src = (ROOT / "tools" / "build.py").read_text()
    assert "XVI-P p15 |" not in src and "XVI-P p14 |" not in src
    assert QC.VERSION_LABEL == f"XVI-P {QC.REVISION}"
    assert B.QC.VERSION_LABEL == f"XVI-P {B.QC.REVISION}"        # p17 disclosed revision: the CURRENT label (p17)


def test_f4_value_block_readback_detects_a_changed_value():
    import build as B
    for rel in B.VALUE_BLOCKS:
        if not (ROOT / rel).exists():
            pytest.skip(f"{rel} not built")
        txt = B.wrap_lines(B.ascii_clean((ROOT / rel).read_text()))
        page = txt[: len(txt) // 2] + "\n" + QC.VERSION_LABEL + " | page 7\n" + txt[len(txt) // 2:]   # a page break mid-block
        ok = B.readback_values(page, ROOT, rel, page)
        assert ok["pass"] and ok["snippets"] > 0, (rel, ok)
        snips = B.value_snippets(ROOT, rel)
        victim = next(s for s in snips if (s in page) and                # p18 disclosed revision: a snippet that is
                      ('"' in s.split(": ", 1)[1] or s.split(": ", 1)[1] not in ("true", "false")))   # verbatim (unwrapped)
        k, v = victim.split(": ", 1)
        bad_page = page.replace(victim, k + ": " + json.dumps("MUTATED"), 1)
        assert bad_page != page and B.readback_values(bad_page, ROOT, rel, bad_page)["pass"] is False, rel


# ================================================================ E2: decoupling from the ch-projected slot
def test_E2_decoupling_proof_certificate():
    c = cj("P16_E2_evanescent.json")
    assert c["revision"] == "p16" and c["E2_decoupling_proven"] is True
    assert all(v is True for v in c["controls"].values()) and len(c["controls"]) >= 9
    for k in ("L1_E_transverse", "L2_E2_longitudinal", "L3_E2_slot_zero_all_externals", "L4_slot_map_nontrivial",
              "E_covariant_form_exact", "E_covariant_form_unique", "D13_A_T1_and_A_E1_zero"):
        assert c["controls"][k] is True, k
    assert c["D13_slot_contribution"] and all(v == "0" for v in c["D13_slot_contribution"].values())
    assert c["E2_status"] == "decoupled_from_ch_slot_proven" and c["outcome"].startswith("DECOUPLED")
    assert sorted(c["mutations"]) == ["M1_gauge_fixed_operator_qq2P", "M2_E1_in_place_of_E2", "M3_wrong_index_slot"]
    for k, v in c["mutations"].items():
        assert v["E2_slot_nonzero"] is True and v["rejected"] is True and v["accepted_as_rejection"] is True, k


def test_E2_consistent_with_p15_D13_values():
    r = cj("P15_D13.json")["result"]
    d = DR.d
    a = sp.sympify(r["E2"]["A_exact_d_times_MB"], locals={"d": d})
    assert sp.cancel(a - sp.Rational(3, 16) / (d - 1)) == 0
    assert DR.substitute_d(a, 4, "test_p16: E2 pole") == sp.Rational(1, 16)
    assert r["T1"]["A_exact_d_times_MB"] == "0" and r["E1"]["A_exact_d_times_MB"] == "0"


def test_E2_status_in_release_no_counterterm():
    s = rs()
    assert s["E2_decoupling_proven"] is True and s["E2_status"] == cj("P16_E2_evanescent.json")["E2_status"]
    assert s["contract_identity"]["evanescent_counterterm_added"] is False and s["contract_identity"]["added"] == []


def test_p14_p15_certificate_values_unchanged_vs_p15_reference():
    """F3 changed dred.py: every P14/P15 certificate content hash (timings and run-specific keys ignored) equals the
    archived p15 author reference values."""
    import certio
    ref = json.loads((ROOT / "archival" / "p15" / "reference_values_p15.json").read_text())["values"]
    ch = ref["certificate_content_sha256_ignoring_timings"]
    run_specific = ("reproducibility", "author_rebuild_passed", "independent_rebuild_passed",
                    "live_report_identical_to_archived", "live_report_present", "archived_zip_sha256_ok",
                    "list_equals_archived_zip")
    diff = []
    for name, h in ch.items():
        if name.startswith(("P14_", "P15_", "P13_")) and name not in ("P15_release",):
            f = CERT / f"{name}.json"
            if certio.file_content_sha(f, run_specific) != h:
                diff.append(name)
    assert not diff, diff


# ================================================================ Batch C
def _laurent(A):
    """independent Laurent expansion of A(d) * MB, MB = 1/eps + 2 - L, d = 4 - 2 eps (authorised substitution)."""
    eps = sp.Symbol("eps_t")
    e = DR.substitute_d(A, 4 - 2 * eps, "test_p16: independent Laurent check")
    ser = sp.series(e * (1 / eps + 2 - L), eps, 0, 1).removeO()
    return sp.simplify(ser.coeff(eps, -1)), sp.expand(ser.coeff(eps, 0))


def test_batchC_values_independent_laurent_check():
    c = cj("P16_batchC.json")
    d = DR.d
    for g in QC.BATCH_C:
        res = c["graphs"][g]["result"]
        assert len(res) == {"D01": 14, "D03": 12}[g]
        for lab, v in res.items():
            A = sp.sympify(v["A_exact_d_times_MB"], locals={"d": d, "I": sp.I})
            pole, fin = _laurent(A)
            assert sp.simplify(pole - sp.sympify(v["UV_pole"])) == 0, (g, lab)
            assert sp.simplify(fin - sp.sympify(v["MSbar_finite"], locals={"L": L})) == 0, (g, lab)
            assert sp.simplify(sp.sympify(v["nonlocal_coefficient_of_L"]) + pole) == 0
            assert v["evanescent"] == ("gt_" in lab)


def test_batchC_controls_status_and_scope():
    c = cj("P16_batchC.json")
    assert c["batchC_evaluated"]["execution"] is True and all(c["controls"].values())
    for g in QC.BATCH_C:
        G = c["graphs"][g]
        assert G["evaluated"] is True and all(G["controls"].values()) and len(G["controls"]) >= 10
        assert G["status"] == "regulated"                       # evanescent poles nonzero, retained (R6)
        assert G["evanescent_pole_nonzero"] is True and G["UV_pole_in_p14r_hh_basis"]
        assert G["regeneration"]["agree"] is True
    assert "NOT evaluated" in c["D11"] and "NOT quantum_inputs_evaluated" in c["batchC_evaluated"]["scope"]
    assert c["finding_C1_component_route"]["contract_change"] is False


def test_batchC_reference_values():
    c = cj("P16_batchC.json")["graphs"]
    I = sp.I
    d = DR.d
    want = {("D03", "g4_mn g4_rs (p.p)^2"): I * (d + 3) / (16 * (d - 1)),
            ("D03", "p_m p_n p_r p_s"): I * (d - 2) / (4 * (d - 1)),
            ("D01", "g4_mn g4_rs (p.p)^2"): -I * (2 * d ** 2 + 10 * d + 9) / (16 * (d - 1) * (d + 1)),
            ("D01", "p_m p_n p_r p_s"): -I * (13 * d ** 2 + 2 * d - 8) / (16 * (d - 1) * (d + 1)),
            ("D01", "gt_mn gt_rs (p.p)^2"): -I / (16 * (d - 1) * (d + 1))}
    for (g, lab), v in want.items():
        got = sp.sympify(c[g]["result"][lab]["A_exact_d_times_MB"], locals={"d": d, "I": I})
        assert sp.cancel(got - v) == 0, (g, lab)


def test_certificate_mutation_p16_batchC_mutations_rejected():
    m = cj("P16_batchC.json")["mutations"]
    assert len(m) == 7 and all(v["accepted_as_rejection"] is True for v in m.values())


# ================================================================ status, hard stops, rebuild flags, change log
def test_p16_release_status_and_hard_stops():
    s = rs()
    assert s["revision"] == "p16" and s["publication"] == "accepted" and s["release_claim_accepted"] is True
    assert s["batchC_evaluated"] is True and s["D01_evaluated"] is True and s["D03_evaluated"] is True
    assert s["D11_evaluated"] is False and s["graphs"]["D11"]["status"] == "unevaluated"
    assert s["D11_matching_verified"] is False and s["quantum_inputs_evaluated"] == "not_earned"
    assert s["hard_stops"] == QC.HARD_STOPS_P16 and s["hard_stops_hold"] is True
    assert s["O1_closure"] == "NOT_CLOSED" and s["symmetry_restored"] is False and s["bulk_symmetry_restored"] is False
    assert s["XVI_P_registered"] is False and s["Route_B_discharged"] is False and s["u_R_c_delta_added"] is False
    assert s["XV_B_opened"] is False and s["XIV_J_opened"] is False
    assert s["insertion_status"] == "Frozen_negative_obstruction_preserved"
    assert s["XVI_M_sha256"].startswith("41aa1099") and s["XVI_M_pin_ok"] is True
    assert s["milestones"]["status"]["P.5_identity"] == "open"
    for g in QC.BATCH_C:
        assert s["graphs"][g]["status"] == "regulated"
    assert s["independent_rebuild_passed"] in ("pending", False)   # p17 revision: bound to the p16 tree (layer record)


def test_p15_independent_rebuild_recorded_and_not_inherited():
    s = rs()
    rec = s["p15_independent_rebuild"]
    assert s["independent_rebuild_passed_p15"] is True
    assert rec["report_sha256"] == QC.P15_INDEPENDENT_REPORT_SHA256 and rec["report_sha256_pinned"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P15_SOURCE_TREE_SHA256
    assert rec["bound_to_source_zip_sha256"] == QC.P15_SOURCE_ZIP_SHA256
    assert "SAME-BOX" in rec["caveat"] and rec["mismatches"] == 0
    assert all(rec["archived_p15_records_pinned"].values())
    import source_manifest as SM
    assert SM.tree_sha(ROOT) != QC.P15_SOURCE_TREE_SHA256


def test_f5_change_log_lists_every_changed_file():
    s = rs()
    cl = s["change_log_vs_p15"]
    assert cl["base_pinned_ok"] is True
    base = json.loads((ROOT / QC.P15_SOURCE_LIST).read_text())["files"]
    import source_manifest as SM
    cur = {r: hashlib.sha256((ROOT / r).read_bytes()).hexdigest() for r in SM.source_files(ROOT) if r != SM.REFERENCE_FILE}
    changed = sorted(set(cur) ^ set(base) | {k for k in set(cur) & set(base) if cur[k] != base[k]})
    assert sorted(cl["added"] + cl["removed"] + cl["modified"]) == changed
    assert cl["contract_files_changed"] == ["code/p5_entry/dred.py"]
    tests_changed = sorted(x for x in cl["modified"] if x.startswith("tests/") and not __import__("contract_registry").p22_revised(x))   # p22 filter
    assert tests_changed == sorted(x for x in QC.DISCLOSED_TEST_REVISIONS_P16 if not __import__("contract_registry").p22_revised(x))


# ================================================================ p16 gate mutations (copy of the built package)
def _copy():
    d = Path(tempfile.mkdtemp(prefix="p16gate_"))
    for sub in ("code", "certificates", "ledgers", "exports", "tools", "archival", "reproducibility", "provenance", "tests"):
        if (ROOT / sub).exists():
            shutil.copytree(ROOT / sub, d / sub, ignore=shutil.ignore_patterns("__pycache__"))
    for f in ("README.md", "REBUILD_INSTRUCTIONS.md", "RELEASE_STATUS.json"):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, d / f)
    (d / "manuscript").mkdir()
    shutil.copy(ROOT / "manuscript" / "preamble.tex", d / "manuscript" / "preamble.tex")
    return d


def _tamper_batchC(d):
    f = d / "certificates" / "P16_batchC.json"
    c = json.loads(f.read_text())
    c["graphs"]["D03"]["controls"]["route_FP_equals_route_PV_exact_in_d"] = False
    f.write_text(json.dumps(c, indent=1))


def _tamper_E2(d):
    f = d / "certificates" / "P16_E2_evanescent.json"
    c = json.loads(f.read_text())
    c["controls"]["L3_E2_slot_zero_all_externals"] = False
    f.write_text(json.dumps(c, indent=1))


def _tamper_p15_layer(d):
    f = d / "code" / "p5_calc" / "d13.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _tamper_contract(d):
    f = d / "code" / "p5_entry" / "counterterm_domain.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _tamper_p15_report(d):
    f = d / "archival" / "p15" / "reproducibility" / "independent_rebuild_report_p15.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


def _hard_stop(d):
    f = d / "certificates" / "P16_batchC.json"
    c = json.loads(f.read_text())
    c["quantum_inputs_evaluated"] = "earned"
    f.write_text(json.dumps(c, indent=1))


@pytest.mark.parametrize("mut", [_tamper_batchC, _tamper_E2, _tamper_p15_layer, _tamper_contract, _tamper_p15_report,
                                 _hard_stop], ids=lambda f: f.__name__)
def test_certificate_mutation_p16_gate_rejects(mut):
    d = _copy()
    try:
        mut(d)
        r = subprocess.run([sys.executable, "code/p5_calc/release_p16.py"], cwd=d, capture_output=True, text=True,
                           timeout=600)
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d / "certificates" / "P16_release.json").exists()
        assert (d / "certificates" / "P16_release_rejected.json").exists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_p16_gate_accepts_unmodified_copy():
    d = _copy()
    try:
        r = subprocess.run([sys.executable, "code/p5_calc/release_p16.py"], cwd=d, capture_output=True, text=True,
                           timeout=600)
        assert r.returncode == 0, r.stdout[-1500:]
    finally:
        shutil.rmtree(d, ignore_errors=True)
