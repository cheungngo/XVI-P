"""XVI-P p22 tests: EV-M2 (evanescent matching statement), EV-CT (evanescent counterterms: closure, identity u
  +> nchanged,
remnants), the p22 runtime d guard (contract revision; every reviewer plant raises; the residue is disclosed),
  +>  the
gate without prefix exemptions (tools/, earlier-layer notes, added code files), the superseded-text marker, st
  +> atus."""
from __future__ import annotations
import hashlib
import json
import operator
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
for p in ("code/p5_calc", "code/p5_entry", "code/classical", "tools", "tests"):
    sys.path.insert(0, str(ROOT / p))
import p22_conventions as QC  # noqa: E402
import dred  # noqa: E402
import contract_registry as CR  # noqa: E402

CERT = ROOT / "certificates"
d = dred.d


def cj(name):
    return json.loads((CERT / name).read_text())


def rs():
    # p23 (disclosed): the p22 LAYER record (the top-level RELEASE_STATUS.json is the p23 status)
    return json.loads((ROOT / "certificates" / "P22_release.json").read_text())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ================================================================ EV-M2
def test_ev_m2_statement_and_scope():
    c = cj("P22_evanescent.json")
    m = c["EV_M2"]
    assert m["verdict"].startswith("PROVEN") and m["locality"] is True
    assert all(v == "0" for v in m["four_D_decoupling"].values()) and len(m["four_D_decoupling"]) >= 8 + 2
    ct = m["continuation_tests"]["D11"]
    assert ct["ghat_continuation_holds"] is False and ct["g4_kept_continuation_holds"] is False   # refuted, r
  +> ecorded
    assert ct["hatted_externals_agree_both"] is True
    assert "NOT matched to XVI-O" in c["D11_matching_verified_scope"]
    assert rs()["D11_matching_verified_scope"] == c["D11_matching_verified_scope"]
    assert "REFUTED" in m["candidates"]["match a d-dim continuation of the XVI-O kernel"]


def test_d11_evanescent_poles_are_the_stored_ones():
    c = cj("P22_evanescent.json")
    r = cj("P18_D11.json")["result"]
    ev = {k: v for k, v in r.items() if v["evanescent"]}
    assert len(ev) == 8
    co = c["EV_CT"]["coefficients_hh_counterterm_per_graph"]["D11"]
    for k, v in ev.items():
        assert sp.simplify(dred.parse_d(co[k], {"I": sp.I}) + dred.parse_d(v["UV_pole"], {"I": sp.I})) == 0, k


# ================================================================ EV-CT
def test_ev_ct_coefficients_closure_identity():
    c = cj("P22_evanescent.json")
    e = c["EV_CT"]
    assert e["coefficient_Kc_E2"] == "-1/16" and e["coefficient_ccb_SE"] == "1/8"
    assert e["coefficients_hh_counterterm_sum"]["g4_mn gt_rs (p.p)^2"] == "-7*I/120"
    a = e["a_closure"]
    assert a["h.c"]["closed"] is True and a["h.c"]["p_dot_T_ev_sum"] == {} and a["h.c"]["E_dot_E2"] == 0
    assert a["h.c"]["p_dot_T_ev_per_graph"]["D11"] == {} and a["h.c"]["p_dot_T_ev_per_graph"]["D01"] != {}
    assert a["c.b"]["closed"] is True and a["c.b"]["calibration_rho_from_4D_pair"] == "1/2"
    assert a["c.b"]["ghost_equation_exact_in_d_gt_sector"] is True and a["c.b"]["image_ev_pair"] == {}
    b = e["b_projected_identity"]
    assert b["unchanged"] is True and all(v == "0" for v in b["hh_slot_values_sum"].values())
    assert all(v == "0" for v in b["Kc_slot_values"].values())
    assert any(v != "0" for v in b["hh_slot_values_per_graph"]["D01"].values())     # only the SUM decouples
    assert all(c["mutations"].values()) and c["insensitive_variations"]["detected"] is False
    assert all(c["controls"].values()) and c["evanescent_counterterm_earned"] is True


def test_ev_ct_remnants_honest():
    r = cj("P22_evanescent.json")["EV_CT"]["c_remnants"]
    q = r["O_eps_times_pole_Q4S_trace_external"]
    assert q["finite_term_if_external_trace_mode_uses_g4"] == "7*I*p.p*(a^.b^*p.p - a^.p*b^.p)/60"
    assert "NONZERO" in q["status"] and "QdS" in q["status"]
    assert "not evaluated, not claimed" in r["where_O_eps_x_pole_would_enter"]


def test_ev_ct_c_b_closure_live():
    """live: the de Donder image of the E2 pole + rho x SE pole vanishes; rho from the 4D pair (T2, T3 vs S1, 
  +> S2)."""
    import evanescent as EV
    import e2_evanescent as E2M
    X4 = {"T2": sp.Rational(3, 16), "T3": sp.Rational(-1, 4)}
    Y4 = {"S1": sp.Rational(-3, 8), "S2": sp.Rational(1, 4)}
    rho = sp.Symbol("rho")
    img = EV.close([(c * X4[k], f) for k in X4 for c, f in EV.dhat([tuple(t) for t in E2M.STRUCT[k]], E2M.PPOW
  +> [k])]
                   + [(rho * c * Y4[k], f) for k in Y4 for c, f in EV.ytensor(k)])
    sol = sp.solve(list(img.values()), rho, dict=True)
    assert sol == [{rho: sp.Rational(1, 2)}]
    ev = EV.close([(c * sp.Rational(1, 16), f) for c, f in EV.dhat([tuple(t) for t in E2M.STRUCT["E2"]], 1)]
                  + [(sp.Rational(1, 2) * c * sp.Rational(-1, 8), f) for c, f in EV.ytensor("SE")])
    assert ev == {}
    bad = EV.close([(c * sp.Rational(1, 16), f) for c, f in EV.dhat([tuple(t) for t in E2M.STRUCT["E2"]], 1)])
    assert bad != {}


def test_p5_status_renormalized_scoped():
    s = rs()
    assert s["P5_calculation_status"] == QC.P5_STATUS_P22 and "QdS" in QC.P5_STATUS_P22
    assert s["evanescent_hh_counterterm_added"] is True
    assert s["milestones"]["status"]["P.5_calculation"] == QC.P5_STATUS_P22


# ================================================================ runtime d guard (contract revision)
X = sp.Symbol("x")
EXPRS = {"linear_and_pow": d * X + 1 / (d - 1), "power_base_only": 1 / (d ** 2 - 1), "d_alone": d,
         "mixed_pow": X * d ** 2 + d}


def _poly_input(e):
    return sp.cancel(e * (d ** 2 - 1) * (d - 1))


PLANTS = {
    "subs_d": lambda e: e.subs(d, 4), "xreplace_d": lambda e: e.xreplace({d: 4}),
    "list_unpack_alias_then_subs": lambda e: (lambda D: e.subs(D, 4))(*[d]),
    "free_symbols_pop_subs": lambda e: e.subs([y for y in e.free_symbols if y.name == "d"][0], 4),
    "lambda_wrapper_Poly": lambda e: (lambda *a: sp.Poly(*a))(_poly_input(e), d).eval(4),
    "coeff_extract": lambda e: sum(sp.expand(e).coeff(d, k) * 4 ** k for k in range(5)),
    "dunder_getattribute_eq": lambda e: sp.Add(*[4 if y == d else y for y in e.__getattribute__("args") + (d,)
  +> ]),
    "subs_power": lambda e: e.subs(d ** 2, 16), "subs_dict": lambda e: e.subs({d: 4}),
    "subs_list": lambda e: e.subs([(d, 4)]), "evalf_subs": lambda e: e.evalf(subs={d: 4}),
    "N_subs": lambda e: sp.N(e, subs={d: 4}), "Lambda": lambda e: sp.Lambda(d, e)(4),
    "Subs_doit": lambda e: sp.Subs(e, d, 4).doit(), "limit": lambda e: sp.limit(e, d, 4),
    "replace": lambda e: e.replace(d, 4), "replace_fn": lambda e: e.replace(lambda y: y == d, lambda y: 4),
    "as_poly_call": lambda e: _poly_input(e).as_poly(d)(4), "all_coeffs": lambda e: sp.Poly(_poly_input(e), d)
  +> .all_coeffs(),
    "as_expr_values": lambda e: sp.Poly(_poly_input(e), d).as_expr(4),
    "collect": lambda e: sp.collect(sp.expand(e), d, evaluate=False),
    "as_independent": lambda e: sp.expand(e).as_independent(d), "series": lambda e: e.series(d, 4, 2),
    "rename_then_value": lambda e: e.subs(d, sp.Dummy()), "lambdify": lambda e: sp.lambdify(d, e)(4),
    "getattr_subs": lambda e: getattr(e, "subs")(d, 4),
    "methodcaller": lambda e: operator.methodcaller("subs", d, 4)(e),
    "unbound_Basic_subs": lambda e: sp.Basic.subs(e, d, 4),
    "Symbol_new_classmethod": lambda e: e.subs(sp.Symbol.__new__(type(d), "d"), 4),
    "Function_call_d": lambda e: sp.Function("f")(e).subs(d, 4).args[0],
}


def test_plant_list_matches_conventions():
    assert set(PLANTS) == set(QC.GUARD_PLANTS_P22)


@pytest.mark.parametrize("expr", sorted(EXPRS))
@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_guard_every_plant_raises(plant, expr):
    with pytest.raises(dred.PrematureD4Substitution):
        PLANTS[plant](EXPRS[expr])


def test_guard_power_base_hole_closed():
    with pytest.raises(dred.PrematureD4Substitution):
        dred.parse_d("1/(d**2 - 1)").subs(dred.d, 4)            # p21 limitation, closed by the p22 contract r
  +> evision


def test_guard_ordinary_algebra_and_authorised_paths():
    e = (d ** 2 - 2 * d - 2) / (32 * (d ** 2 - 1))
    assert sp.factor(sp.cancel(sp.together(e + 1 / (d + 1)))) != 0
    assert sp.cancel(sp.apart(e, d) - (sp.Rational(1, 32) - 1 / (64 * (d + 1)) - 3 / (64 * (d - 1)))) == 0
    r = sp.Symbol("r")
    assert sp.solve(r * d - 1, r) == [1 / d]
    assert dred.substitute_d(e, 4, "test_p22") == sp.Rational(1, 80)
    with dred.authorised_d("test_p22: authorised coefficient read"):
        assert sp.Poly(sp.cancel(e * 32 * (d ** 2 - 1)), d).all_coeffs() == [1, -2, -2]
    assert "test_p22: authorised coefficient read" in dred.D_PROVENANCE
    with pytest.raises(dred.PrematureD4Substitution):                       # authorisation does not leak
        e.subs(d, 4)


def test_guard_symbol_new_and_plain_d_produce_no_value():
    plain = sp.Symbol.__new__(sp.Symbol, "d")
    assert plain != d and (d * X).subs(plain, 4) == d * X
    with pytest.raises(dred.PlainDimensionSymbol):
        dred.assert_opaque_d(plain + 1)


def test_guard_residue_disclosed_and_demonstrated():
    """the residue the guard cannot intercept is disclosed (and covered only by the secondary static scan)."""
    txt = QC.RUNTIME_GUARD_RESIDUE_P22
    for w in ("identity", "string round-trips", "Poly.rep", "static allow-list scan"):
        assert w in txt
    e = X * d ** 2 + d
    assert sp.Add(*[4 if y is d else y for y in e.args]).has(d)          # `is` test: d**2 survives ...
    assert sp.sympify(str(e).replace("d", "4")) == 16 * X + 4            # ... a string round-trip is NOT inte
  +> rcepted


def test_guard_entry_points_recorded_and_registry():
    for k in ("Basic.subs", "Basic.xreplace", "Atom.xreplace (bare d)", "Poly.eval", "Expr.coeff", "collect", 
  +> "limit",
              "Lambda(d, ...)", "OpaqueDimension.__eq__ (d == d)", "evalf/n(subs=...)"):
        assert k in dred.GUARDED_ENTRY_POINTS, k
    r = CR.dred_revision(ROOT)
    assert r["state"] == "p18 + p22 guard block" and r["p18_core_byte_identical"] is True
    assert sha(ROOT / CR.DRED) == QC.P22_PINNED_SHA256[CR.DRED] or CR.p23_registered(ROOT)   # p23 registered 
  +> block
    assert rs()["d_runtime_guard"]["ok"] is True and rs()["d_runtime_guard"]["not_raised"] == {}


def test_guard_not_in_block_is_unregistered(tmp_path):
    (tmp_path / "code/p5_entry").mkdir(parents=True)
    t = (ROOT / CR.DRED).read_text()
    (tmp_path / CR.DRED).write_text(t.replace('ETA = (1, -1, -1, -1)', 'ETA = (1, 1, 1, 1)'))
    assert CR.dred_revision(tmp_path)["state"] == "unregistered"
    t = t[:t.index(CR.BEGIN23)] if CR.BEGIN23 in t else t          # p23: strip the registered p23 block too
    (tmp_path / CR.DRED).write_text(t[:t.index(CR.BEGIN)] + t[t.index(CR.END) + len(CR.END):])
    assert CR.dred_revision(tmp_path)["state"] == "p18"


# ================================================================ T: science text
def test_p20_absolute_open_passage_marked_superseded():
    txt = (ROOT / "manuscript/notes/P20_correction.tex").read_text()
    i = txt.index("Absolute pin: OPEN")
    assert "[superseded in p21" in txt[i:i + 200]
    assert sha(ROOT / "manuscript/notes/P20_correction.tex") != \
        QC.DISCLOSED_MANUSCRIPT_REVISIONS_P22["manuscript/notes/P20_correction.tex"]["p21_sha256"]


# ================================================================ status
def test_p22_release_status_and_flags():
    s = rs()
    assert s["revision"] == "p22" and s["publication"] == "accepted" and s["execution_pass"] is True
    for k in QC.EARNABLE_P22:
        assert s[k] == "earned", k
    assert s["bulk_symmetry_restored"] is False and s["symmetry_restored"] is False and s["O1_closure"] == "NO
  +> T_CLOSED"
    assert s["insertion_status"] == "Frozen_negative_obstruction_preserved"
    assert s["hard_stops"] == QC.HARD_STOPS_P22 and s["hard_stops_hold"] is True
    # p23: the p22 LAYER gate evaluates the "current" independent flag against the p23 tree -> never True here
    assert s["independent_rebuild_passed"] is not True and s["independent_rebuild_passed_p21"] is True
    assert s["change_log_vs_p21"]["undisclosed_changes"] == [] and s["change_log_vs_p21"]["pinned_sha_mismatch
  +> es"] == {}
    assert s["contract_revision"] == QC.CONTRACT_REVISION and "DISCLOSED p22 contract revision" in QC.CONTRACT
  +> _REVISION


def test_p21_independent_recorded_and_not_inherited():
    rec = rs()["p21_independent_rebuild"]
    assert rec["report_sha256"] == QC.P21_INDEPENDENT_REPORT_SHA256 and rec["pins_ok"] is True
    assert rec["bound_to_source_tree_sha256"] == QC.P21_SOURCE_TREE_SHA256 and rec["tree_matches_p21"] is True
    assert rec["bound_to_source_zip_sha256"] == QC.P21_SOURCE_ZIP_SHA256 and rec["mismatches"] == 0
    import source_manifest as SM
    assert SM.tree_sha(ROOT) != QC.P21_SOURCE_TREE_SHA256


def test_disclosure_complete_and_exact():
    cl = rs()["change_log_vs_p21"]
    changed = set(cl["added"]) | set(cl["modified"]) | set(cl["removed"])
    listed = set(QC.DISCLOSED_REVISIONS_P22)
    assert cl["disclosed_but_unchanged"] == [] and listed <= changed
    for x in changed - listed:
        assert (x in QC.GENERATED_EXEMPT_P22 or (x in cl["added"] and x.startswith(QC.DISCLOSED_PREFIXES_ADDED
  +> _P22))
                or CR.p23_disclosed(x)), x                    # p23: registered later revisions (pinned by the
  +>  p23 gate)
    assert cl["contract_files_changed"] == ["code/p5_entry/dred.py"] and cl["contract_changes_registered"] is 
  +> True
    assert set(CR.P22_REVISED_FILES) <= listed


def test_version_label_p22():
    import build as B
    assert QC.VERSION_LABEL == "XVI-P p22" and B.QC.VERSION_LABEL == f"XVI-P {B.QC.REVISION}"   # p23: current
  +>  label


# ================================================================ p22 gate mutations (fail closed; no stale s
  +> tatus)
def _copy():
    import test_p21 as T21
    return T21._copy()


def _edit(d_, name, fn):
    f = d_ / "certificates" / name
    c = json.loads(f.read_text())
    fn(c)
    f.write_text(json.dumps(c, indent=1))


def _tools_change(d_):                      # reviewer: tools/ was exempt in p21
    f = d_ / "tools" / "manifest.py"            # p23: a tools file NOT revised in p23 (revised ones are pinne
  +> d by the p23 gate)
    f.write_text(f.read_text() + "\n# undisclosed\n")


def _earlier_note_change(d_):               # reviewer: earlier-layer notes were exempt in p21
    f = d_ / "manuscript" / "notes" / "P18_D11.tex"
    f.write_text(f.read_text() + "\n% undisclosed\n")


def _added_code_file(d_):                   # reviewer: added files were not disclosure-checked in p21
    (d_ / "code" / "p5_calc" / "zz_extra.py").write_text("x = 1\n")


def _dred_guard_removed(d_):
    f = d_ / CR.DRED
    t = f.read_text()
    f.write_text(t[:t.index(CR.BEGIN)] + t[t.index(CR.END) + len(CR.END):])


def _dred_core_changed(d_):
    f = d_ / CR.DRED
    f.write_text(f.read_text().replace('ETA = (1, -1, -1, -1)', 'ETA = (1, -1, -1, -1)  # edit'))


def _guard_weakened(d_):                    # in-block edit: subs guard disabled -> sha pin AND live probe fai
  +> l
    f = d_ / CR.DRED
    src = f.read_text()
    old = '_check_rule(_pairs_of_subs(args, kwargs), "subs", 4)'
    assert old in src
    f.write_text(src.replace(old, 'None'))


def _ev_cb_open(d_):
    _edit(d_, "P22_evanescent.json", lambda c: c["EV_CT"]["a_closure"]["c.b"].__setitem__("closed", False))


def _ev_identity_changed(d_):
    _edit(d_, "P22_evanescent.json", lambda c: c["EV_CT"]["b_projected_identity"].__setitem__("unchanged", Fal
  +> se))


def _ev_m2_not_proven(d_):
    _edit(d_, "P22_evanescent.json", lambda c: c["EV_M2"].__setitem__("verdict", "NOT ESTABLISHED"))


def _superseded_marker_removed(d_):
    f = d_ / "manuscript" / "notes" / "P20_correction.tex"
    f.write_text(f.read_text().replace("[superseded in p21", "[note"))


def _p21_layer_rejected(d_):
    _edit(d_, "P21_release.json", lambda c: c.__setitem__("publication", "REJECTED"))


def _tamper_p21_report(d_):
    f = d_ / "archival" / "p21" / "reproducibility" / "independent_rebuild_report_p21.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


MUTS = [_tools_change, _earlier_note_change, _added_code_file, _dred_guard_removed, _dred_core_changed,
        _guard_weakened, _ev_cb_open, _ev_identity_changed, _ev_m2_not_proven, _superseded_marker_removed,
        _p21_layer_rejected, _tamper_p21_report]


def _run(d_):
    return subprocess.run([sys.executable, "code/p5_calc/release_p22.py"], cwd=d_, capture_output=True, text=T
  +> rue,
                          timeout=900)


@pytest.mark.parametrize("mut", MUTS, ids=lambda f: f.__name__)
def test_p22_gate_mutation_rejects_without_stale_status(mut):
    d_ = _copy()
    try:
        assert (d_ / "RELEASE_STATUS.json").exists()
        mut(d_)
        r = _run(d_)
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d_ / "certificates" / "P22_release.json").exists()
        assert (d_ / "certificates" / "P22_release_rejected.json").exists()
        assert not (d_ / "RELEASE_STATUS.json").exists() and not (d_ / "certificates" / "RELEASE_STATUS.json")
  +> .exists()
    finally:
        shutil.rmtree(d_, ignore_errors=True)


def test_p22_gate_accepts_unmodified_copy():
    d_ = _copy()
    try:
        r = _run(d_)
        assert r.returncode == 0, r.stdout[-1500:]
        s = json.loads((d_ / "RELEASE_STATUS.json").read_text())
        assert s["revision"] == "p22" and s["evanescent_counterterms_verified"] == "earned"
        assert s["d_runtime_guard_verified"] == "earned" and s["bulk_symmetry_restored"] is False
    finally:
        shutil.rmtree(d_, ignore_errors=True)
