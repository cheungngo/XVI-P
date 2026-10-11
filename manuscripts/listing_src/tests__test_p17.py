"""XVI-P p17 tests: D01/D03 evanescent poles vs the ch-projected slot (proof, controls, mutations, transverse
coordinates), G1 extended static scan (with planted violations), G2 guarded loader parse_d, G3 wording, G4 cha
  +> nge log,
G6 phase convention, p17 status / hard stops / p16 independent record, p17 gate mutations."""
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
import p17_conventions as QC  # noqa: E402
import p16_conventions as Q16  # noqa: E402
import p15_conventions as Q15  # noqa: E402
import dred as DR  # noqa: E402

CERT = ROOT / "certificates"
PKG = ("code/p5_calc", "code/p5_entry")


def cj(name):
    return json.loads((CERT / name).read_text())


def rs():
    # p18: the p17 LAYER record (the top-level RELEASE_STATUS.json is the p18 status)
    return json.loads((CERT / "P17_release.json").read_text())


def P(text):
    """certificate string -> expression with the OPAQUE d (G2 loader); 'p.p' is the scalar p^2."""
    return DR.parse_d(text.replace("p.p", "pp"), {"I": sp.I})


# ================================================================ G1: extended static scan
FORBIDDEN_NAMES = {"eval", "exec", "parse_expr", "lambdify", "ufuncify", "autowrap"}
PROBE_FUNCTIONS = {"f3_hardening"}         # release_p16 / release_p17 guard probes (deliberate hazards, must 
  +> raise)


def scan(path, root=ROOT):
    """AST pattern scan for value paths the runtime guard cannot hook.  Returns (violations, parse_sites):
    violations: builtin eval/exec, parse_expr, lambdify/ufuncify/autowrap, any `.eval(` call, `.replace(` whos
  +> e first
    argument is not a string literal (d itself, a lambda or a NAMED function query), `.func(` expression-tree 
  +> rebuilds;
    parse_sites: every sympify / S call that does not pass locals with the key 'd' (must be on the reviewed li
  +> st)."""
    src = path.read_text()
    tree = ast.parse(src)
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.name
    bad, sites = [], []

    def visit(node, fn=None):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = node.name
        if isinstance(node, ast.Call) and fn not in PROBE_FUNCTIONS:
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
            if name in FORBIDDEN_NAMES:
                bad.append(f"{rel}:{node.lineno}:{name}")
            if name == "replace" and isinstance(f, ast.Attribute) and node.args:
                a = node.args[0]
                if not (isinstance(a, ast.Constant) and isinstance(a.value, str)):
                    bad.append(f"{rel}:{node.lineno}:replace(non-literal)")
            if name == "func" and isinstance(f, ast.Attribute):
                bad.append(f"{rel}:{node.lineno}:.func(rebuild)")
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
            if name in ("sympify", "S"):
                loc = {k.arg: k.value for k in node.keywords}.get("locals")
                has_d = isinstance(loc, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == "d" for k
  +>  in loc.keys)
                if not has_d:
                    sites.append(f"{rel}::{fn}::{ast.get_source_segment(src, node)}")
        for ch in ast.iter_child_nodes(node):
            visit(ch, fn)
    visit(tree)
    return bad, sites


def _pkg_files():
    return [f for d in PKG for f in sorted((ROOT / d).glob("*.py"))]


def test_g1_static_scan_package_clean():
    bad, sites = [], []
    for f in _pkg_files():
        b, s = scan(*CR.scan_view(f))   # p22: p18 contract core of the registered dred revision
        bad += b
        sites += s
    assert not bad, bad
    unreviewed = sorted(set(sites) - set(QC.PARSE_SITES_REVIEWED))
    assert not unreviewed, unreviewed                              # every parse site reviewed
    stale = sorted(set(QC.PARSE_SITES_REVIEWED) - set(sites))
    assert not stale, stale                                        # the reviewed list is exact (no stale entr
  +> y)


def test_g1_static_scan_detects_planted_violations(tmp_path):
    f = tmp_path / "planted.py"
    f.write_text(
        "import sympy as sp\nfrom sympy.parsing.sympy_parser import parse_expr\nfrom dred import d\n"
        "def isd(x):\n    return x == d\n"
        "def g(e):\n"
        "    a = sp.Poly(e, d).eval(4)\n"                                  # 1 .eval
        "    b = e.replace(d, 4)\n"                                        # 2 replace(d)
        "    c = e.replace(lambda x: x == d, lambda x: 4)\n"              # 3 replace(lambda)
        "    k = e.replace(isd, lambda x: 4)\n"                            # 4 replace(named function)  [G1]
        "    m = sp.sympify(str(e)).subs(sp.Symbol('d'), 4)\n"            # site: string round-trip  [G1]
        "    n = eval(sp.srepr(e))\n"                                      # 5 eval(srepr)  [G1]
        "    o = parse_expr(str(e))\n"                                     # 6 parse_expr  [G1]
        "    q = e.func(*[x if x != d else 4 for x in e.args])\n"         # 7 tree rebuild  [G1]
        "    r = sp.lambdify(d, e)\n"                                      # 8 lambdify
        "    exec('z = 1')\n"                                              # 9 exec
        "    s = sp.S(str(e))\n"                                           # site: S of a string  [G1]
        "    t = sp.sympify(str(e), locals={'d': d})\n"                   # guarded: not a site
        "    return a, b, c, k, m, n, o, q, r, s, t\n")
    bad, sites = scan(f, tmp_path)
    assert len(bad) == 9, bad
    assert len(sites) == 2 and not set(sites) & set(QC.PARSE_SITES_REVIEWED), sites


def test_g1_prefactor_strings_parsed_without_d_are_d_free():
    """the reviewed prefactor parse sites parse export prefactor strings: none contains d."""
    for f in sorted((ROOT / "exports" / "P14_integrands").glob("*.json")):
        pre = json.loads(f.read_text())["prefactor"]
        e = sp.sympify(pre, locals={"kappa": sp.Symbol("kappa")})
        assert {s.name for s in e.free_symbols} <= {"kappa"}, (f.name, pre)


def test_g1_disclosure_wording_matches_scan_scope():
    txt = json.dumps(QC.DISCLOSED_CONTRACT_REVISIONS_P17)
    for w in ("ANY function query", "string round-trips", "srepr", "e.func(*args)", "Poly(..).eval",
              "pattern check, not a proof"):
        assert w in txt, w
    doc = DR.__doc__ or ""
    assert "Wild pattern" in doc and "NOT refuse" in doc                       # G3 wording corrected


# ================================================================ G2: guarded loader
def test_g2_parse_d_restores_opaque_d_and_guard():
    e = P("(d - 4)/(d - 1) + d**2")
    assert e.has(DR.d) and all(isinstance(s, DR.OpaqueDimension) for s in e.free_symbols if s.name == "d")
    with pytest.raises(DR.PrematureD4Substitution):
        e.subs(DR.d, 4)
    assert DR.substitute_d(e, 4, "test_p17: parse_d authorised path") == 16


def test_g2_plain_symbol_from_sympify_is_detected():
    plain = sp.sympify("(d - 4)/(d - 1)")                     # the G2 hazard
    assert plain.subs(sp.Symbol("d"), 4) == 0                  # a plain d is NOT guarded ...
    with pytest.raises(DR.PlainDimensionSymbol):
        DR.assert_opaque_d(plain)                              # ... and is detected
    with pytest.raises(DR.PlainDimensionSymbol):
        DR.parse_d("d + 1", {"d": sp.Symbol("d")})            # rebinding d in extra_locals refused
    assert DR.assert_opaque_d(DR.d + 1) == DR.d + 1


def test_g2_stored_certificate_strings_round_trip_through_parse_d():
    c = cj("P16_batchC.json")
    for g in QC.HH_SLOT_GRAPHS:
        for lab, v in c["graphs"][g]["result"].items():
            e = P(v["A_exact_d_times_MB"])
            DR.assert_opaque_d(e)
            assert e.has(DR.d) or e.is_number, (g, lab)


def test_g3_wild_pattern_not_refused_and_documented():
    w = sp.Wild("w")
    assert (DR.d + 1).match(DR.d + w) == {w: 1}               # substitutes no value for d; not refused (docum
  +> ented)
    with pytest.raises(DR.PrematureD4Substitution):
        (DR.d + 1).match(DR.d)


def test_g_contract_revision_disclosed_and_layers_identical():
    rev = QC.DISCLOSED_CONTRACT_REVISIONS_P17
    assert list(rev) == ["code/p5_entry/dred.py"] and "G2" in json.dumps(rev)
    cur = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    assert sorted(k for k, h in Q15.P14R_CONTRACT_SHA256.items() if cur.get(k) != h) == ["code/p5_entry/dred.p
  +> y"]
    assert set(cur) == set(Q15.P14R_CONTRACT_SHA256)                                   # no new contract file
    assert cur["code/p5_entry/dred.py"] != QC.P16_DRED_SHA256                          # the p17 revision is r
  +> eal
    for k, h in {**Q16.P15_CALC_SHA256, **QC.P16_CALC_SHA256}.items():                 # p15 + p16 layers iden
  +> tical
        assert hashlib.sha256((ROOT / k).read_bytes()).hexdigest() == h, k


def test_p14_p15_p16_certificate_values_unchanged_vs_p16_reference():
    """the p17 dred.py revision only ADDS functions: every P13/P14/P15/P16 certificate content hash (timings a
  +> nd
    run-specific keys ignored; the layer release records excluded) equals the archived p16 author reference.""
  +> "
    import certio
    ref = json.loads((ROOT / "archival" / "p16" / "reference_values_p16.json").read_text())["values"]
    ch = ref["certificate_content_sha256_ignoring_timings"]
    diff = []
    for name, h in ch.items():
        if name.startswith(("P13_", "P14_", "P15_", "P16_")) and name not in ("P15_release", "P16_release"):
            if certio.file_content_sha(CERT / f"{name}.json", QC.RUN_SPECIFIC_KEYS) != h:
                diff.append(name)
    assert not diff, diff


# ================================================================ priority 1: hh evanescent poles vs the ch s
  +> lot
def test_hh_slot_verdict_controls_and_mutations():
    c = cj("P17_hh_slot.json")
    assert c["revision"] == "p17" and c["decoupling_proven"] is True
    assert c["status"] == "decoupled_from_ch_slot_proven_as_sum" and c["verdict"].startswith("DECOUPLED (proof
  +> )")
    assert c["surviving_evanescent_structures_in_slot"] == []
    assert len(c["controls"]) >= 17 and all(v is True for v in c["controls"].values())
    assert sorted(c["mutations"]) == sorted(("M1_wrong_relative_sign_D03", "M2_D03_times_2_symmetry_factor",
                                             "M3_D03_evanescent_dropped_naive_4D", "M4_trace_operator_in_place
  +> _of_s_h"))
    assert all(v["accepted_as_rejection"] is True for v in c["mutations"].values())
    assert c["quantum_inputs_evaluated"] == "not_earned" and "NOT evaluated" in c["D11"]


def test_hh_slot_row_and_operator():
    c = cj("P17_hh_slot.json")
    assert list(c["rows_with_D01_D03"]) == [QC.SLOT_ROW]
    led = json.loads((ROOT / "ledgers" / "P13_ch_dependency_rows.json").read_text())["rows"]
    rows = [r["id"] for r in led if any(g.split("_")[0] in ("D01", "D03") for g in r["graphs"])]
    assert rows == [QC.SLOT_ROW]                                  # independent reading of the ledger
    op = c["operator_s_h"]
    assert op["exact"] and op["unique"] and op["covariant"] == [["I/2", [["g4", "m", "v"], ["p", "n"]]]]


def test_hh_slot_cancellation_independent_of_hh_slot_code():
    """p_m G for D01 and D03 as recorded by the (byte-identical) p16 Batch C code: their sum vanishes exactly 
  +> in d,
    structure by structure (4D and evanescent); each is nonzero."""
    c = cj("P16_batchC.json")["graphs"]
    a, b = c["D01"]["longitudinal_projection_p_m_G"], c["D03"]["longitudinal_projection_p_m_G"]
    keys = set(a) | set(b)
    assert any(k.startswith("t_") for k in keys)                 # evanescent structures present
    for k in keys:
        s = sp.cancel(P(a.get(k, "0")) + P(b.get(k, "0")))
        assert s == 0, k
    assert any(sp.cancel(P(v)) != 0 for v in a.values()) and any(sp.cancel(P(v)) != 0 for v in b.values())


def test_hh_slot_transverse_coordinates_exact():
    fd = cj("P17_hh_slot.json")["four_D_poles"]
    assert fd["basis_dimension"] == 5 and fd["basis_rank"] == 5 and fd["dim_pair_symmetric_4D_structures"] == 
  +> 5
    assert fd["span_is_all_4D_structures"] is True                # automatic (disclosed as such)
    assert fd["longitudinal_constraint_rank"] == 3 and fd["transverse_subspace_dimension"] == 2
    k1, k2 = [[sp.Rational(x) for x in v] for v in fd["transverse_basis_in_p14r_coordinates"]]
    z = {g: [sp.sympify(x, locals={"I": sp.I}) for x in fd["graphs"][g]["coordinates_p14r_basis"]]
         for g in ("D01", "D03", "D01+D03")}
    I = sp.I
    assert z["D01"] == [-27 * I / 160, -71 * I / 240, 19 * I / 60, 11 * I / 20, -13 * I / 30]
    assert z["D03"] == [7 * I / 96, I / 24, -I / 8, -I / 24, I / 12]
    assert [sp.simplify(x + y) for x, y in zip(z["D01"], z["D03"])] == z["D01+D03"]
    al, be = sp.symbols("al be")
    sol = sp.solve([al * u + be * v - w for u, v, w in zip(k1, k2, z["D01+D03"])], [al, be], dict=True)
    assert sol == [{al: 61 * I / 120, be: -7 * I / 20}]           # the summed pole lies in the transverse ker
  +> nel
    for g in ("D01", "D03"):
        assert not sp.solve([al * u + be * v - w for u, v, w in zip(k1, k2, z[g])], [al, be], dict=True)
        assert fd["graphs"][g]["transverse"] is False
    assert fd["graphs"]["D01+D03"]["transverse"] is True


def test_hh_slot_evanescent_poles_recorded_not_dropped():
    ev = cj("P17_hh_slot.json")["evanescent_poles_D01_plus_D03_in_hh_green_function"]
    assert len(ev) == 8 and all(v != "0" for v in ev.values()) and all("gt_" in k for k in ev)


def test_g6_phase_convention_documented():
    c = cj("P17_hh_slot.json")
    assert "overall I" in c["phase_convention_G6"] and "real" in c["phase_convention_G6"]
    assert "D13" in QC.PHASE_CONVENTION_G6 and rs()["phase_convention_G6"] == QC.PHASE_CONVENTION_G6


# ================================================================ status, hard stops, change log
def test_p17_release_status_and_hard_stops():
    s = rs()
    assert s["revision"] == "p17" and s["publication"] == "accepted" and s["release_claim_accepted"] is True
    assert s["hh_evanescent_decoupling_proven"] is True and s["evanescent_hh_counterterm_added"] is False
    assert s["contract_identity"]["added"] == [] and s["contract_identity"]["changed_vs_p14r"] == ["code/p5_en
  +> try/dred.py"]
    assert s["batchC_evaluated"] is True and s["E2_decoupling_proven"] is True
    assert s["D11_evaluated"] is False and s["graphs"]["D11"]["status"] == "unevaluated"
    assert s["D11_matching_verified"] is False and s["quantum_inputs_evaluated"] == "not_earned"
    assert s["hard_stops"] == QC.HARD_STOPS_P17 and s["hard_stops_hold"] is True
    assert s["O1_closure"] == "NOT_CLOSED" and s["symmetry_restored"] is False and s["bulk_symmetry_restored"]
  +>  is False
    assert s["XVI_P_registered"] is False and s["Route_B_discharged"] is False and s["u_R_c_delta_added"] is F
  +> alse
    assert s["XV_B_opened"] is False and s["XIV_J_opened"] is False
    assert s["insertion_status"] == "Frozen_negative_obstruction_preserved"
    assert s["XVI_M_sha256"].startswith("41aa1099") and s["XVI_M_pin_ok"] is True
    assert s["milestones"]["status"]["P.5_identity"] == "open"
    assert s["independent_rebuild_passed"] in ("pending", False)   # p18: the live p17 report is bound to the 
  +> p17 tree
    assert s["contract_identity"]["guard_probes"]["all_refused"] is True
    assert s["contract_identity"]["guard_probes"]["G2_ok"] is True


def test_p16_independent_rebuild_recorded_and_not_inherited():
    s = rs()
    rec = s["p16_independent_rebuild"]
    assert s["independent_rebuild_passed_p16"] is True
    assert rec["report_sha256"] == QC.P16_INDEPENDENT_REPORT_SHA256 and rec["report_sha256_pinned"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P16_SOURCE_TREE_SHA256
    assert rec["bound_to_source_zip_sha256"] == QC.P16_SOURCE_ZIP_SHA256
    assert "SAME-BOX" in rec["caveat"] and rec["mismatches"] == 0
    assert all(rec["archived_p16_records_pinned"].values())
    import source_manifest as SM
    assert SM.tree_sha(ROOT) != QC.P16_SOURCE_TREE_SHA256


def test_g4_change_log_lists_every_changed_file_incl_reference():
    s = rs()
    cl = s["change_log_vs_p16"]
    assert cl["base_pinned_ok"] is True
    base = json.loads((ROOT / QC.P16_SOURCE_LIST).read_text())["files"]
    import source_manifest as SM
    cur = {r: hashlib.sha256((ROOT / r).read_bytes()).hexdigest() for r in SM.source_files(ROOT) if r != SM.RE
  +> FERENCE_FILE}
    changed = sorted(set(cur) ^ set(base) | {k for k in set(cur) & set(base) if cur[k] != base[k]} | {SM.REFER
  +> ENCE_FILE})
    assert sorted(cl["added"] + cl["removed"] + cl["modified"]) == changed
    assert SM.REFERENCE_FILE in cl["added"]                                        # G4
    assert cl["contract_files_changed"] == ["code/p5_entry/dred.py"]
    assert sorted(x for x in cl["modified"] if x.startswith("tests/") and not __import__("contract_registry").
  +> p22_revised(x)) == sorted(   # p22 filter
        x for x in QC.DISCLOSED_TEST_REVISIONS_P17 if not __import__("contract_registry").p22_revised(x))


def test_version_label_p17():
    import build as B
    assert QC.VERSION_LABEL == "XVI-P p17" and B.QC.VERSION_LABEL == f"XVI-P {B.QC.REVISION}"   # p18: current
  +>  label
    assert "certificates/P17_hh_slot.json" in B.VALUE_BLOCKS


# ================================================================ p17 gate mutations (copy of the built packa
  +> ge)
def _copy():
    d = Path(tempfile.mkdtemp(prefix="p17gate_"))
    for sub in ("code", "certificates", "ledgers", "exports", "tools", "archival", "reproducibility", "provena
  +> nce", "tests"):
        if (ROOT / sub).exists():
            shutil.copytree(ROOT / sub, d / sub, ignore=shutil.ignore_patterns("__pycache__"))
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


def _tamper_hh_control(d):
    _edit_cert(d, "P17_hh_slot.json", lambda c: c["controls"].__setitem__("H3_p_dot_G_sum_zero_exact_in_d", Fa
  +> lse))


def _surviving_structure(d):
    _edit_cert(d, "P17_hh_slot.json", lambda c: c.__setitem__("surviving_evanescent_structures_in_slot",
                                                               ["gt_rs p_m p_n (p.p)^1"]))


def _tamper_p16_layer(d):
    f = d / "code" / "p5_calc" / "batchC.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _tamper_contract(d):
    f = d / "code" / "p5_entry" / "counterterm_domain.py"
    f.write_text(f.read_text() + "\n# tampered\n")


def _new_contract_file(d):
    (d / "code" / "p5_entry" / "evanescent_hh_counterterm.py").write_text("# undisclosed contract file\n")


def _tamper_p16_report(d):
    f = d / "archival" / "p16" / "reproducibility" / "independent_rebuild_report_p16.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


def _hard_stop(d):
    _edit_cert(d, "P17_hh_slot.json", lambda c: c.__setitem__("quantum_inputs_evaluated", "earned"))


@pytest.mark.parametrize("mut", [_tamper_hh_control, _surviving_structure, _tamper_p16_layer, _tamper_contract
  +> ,
                                 _new_contract_file, _tamper_p16_report, _hard_stop], ids=lambda f: f.__name__
  +> )
def test_certificate_mutation_p17_gate_rejects(mut):
    d = _copy()
    try:
        mut(d)
        r = subprocess.run([sys.executable, "code/p5_calc/release_p17.py"], cwd=d, capture_output=True, text=T
  +> rue,
                           timeout=600)
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d / "certificates" / "P17_release.json").exists()
        assert (d / "certificates" / "P17_release_rejected.json").exists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_p17_gate_accepts_unmodified_copy():
    d = _copy()
    try:
        r = subprocess.run([sys.executable, "code/p5_calc/release_p17.py"], cwd=d, capture_output=True, text=T
  +> rue,
                           timeout=600)
        assert r.returncode == 0, r.stdout[-1500:]
    finally:
        shutil.rmtree(d, ignore_errors=True)
