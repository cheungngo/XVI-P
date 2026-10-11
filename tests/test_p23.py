"""XVI-P p23 tests: O.1 requirement record, exact one-loop power counting / enlarge rule, P.6 entry inventory,
polynomial-domain refusal (p23 contract revision), EV value check, title qualifier, p23 gate (fail closed)."""
from __future__ import annotations
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
import p23_conventions as QC  # noqa: E402
import contract_registry as CR  # noqa: E402
import dred  # noqa: E402
import power_counting as PC  # noqa: E402

CERT = ROOT / "certificates"
d = dred.d
X, y = sp.Symbol("X"), sp.Symbol("y")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rs():
    return json.loads((ROOT / "RELEASE_STATUS.json").read_text())


def o1c():
    return json.loads((CERT / "P23_O1_scope.json").read_text())


# ================================================================ O.1 requirement
def test_o1_ledger_copy_pinned_and_read_only_source_recorded():
    assert sha(ROOT / QC.O1_LEDGER) == QC.O1_LEDGER_SHA256
    c = o1c()
    assert c["O1_source"]["sha256"] == QC.O1_LEDGER_SHA256 and c["O1_source"]["outcome"] == "NOT_CLOSED"
    assert c["O1_source"]["gate"] == "O.1" and len(c["O1_source"]["checklist"]) == 6


def test_o1_requirement_and_scope_honest():
    c = o1c()
    assert c["O1_closable_in_XVI_P"] is False
    sc = c["O1_items_scope"]
    assert sc["S_inv^{[2]} classical consistency (O.2)"]["scope"] == "OUT OF SCOPE"
    for w in ("VERIFIED", "O.2", "ell_4", "enlarged"):
        assert w in c["O1_requirement"]


# ================================================================ exact power counting (live recomputation)
def test_vertex_rule_and_kappa_equals_E_live():
    import feynman as F
    V = F.vertices()
    assert all(PC.vertex_power_ok(V).values())
    for E in (1, 2, 3):
        assert all(g["kappa_power"] == E for g in PC.one_loop_graphs(V, E))


def test_enumeration_reproduces_frozen_kappa2_inventory_live():
    import feynman as F
    fm = PC.frozen_match(PC.one_loop_graphs(F.vertices(), 2))
    assert fm["equal"] and fm["enumerated"] == fm["frozen"] == 9


def test_frozen_list_matches_inventory_records():
    f = CERT / "diagram_inventory.json"            # inherited (author tree); absent from the source-only tree
    if f.is_file():
        inv = json.loads(f.read_text())["diagrams"]
        loop = {x["id"] for x in inv if x.get("kappa_power") == 2 and x.get("hbar_power") == 1}
        assert loop == set(PC.FROZEN_E2) - {"D13_Kc_ghost_self_energy"}
    led = (ROOT / "ledgers" / "P13_graph_inventory.json").read_text()   # built in every tree
    for k in ("D01_hh_bubble_cubic", "D02_hh_tadpole_quartic", "D03_hh_ghost_loop", "D11_hh_scalar_loop",
              "D12_hh_scalar_tadpole"):
        assert k in PC.FROZEN_E2 and f'"{k}"' in led
    assert '"D13_Kc_ghost_graviton_loop"' in led
    assert sum(f'"D14{s}_h_onepoint_' in led for s in "abc") == QC.ONE_POINT_E1_GRAPHS


def test_enlarge_rule_not_triggered_and_P6_entry_counts():
    c = o1c()
    assert c["identity_at_kappa2"]["enlarge_rule_triggered"] is False
    assert len(c["graphs_E1"]) == QC.ONE_POINT_E1_GRAPHS
    p6 = c["P6_entry_kappa3_three_point"]
    assert p6["n_graphs"] == QC.P6_ENTRY_E3_GRAPHS and p6["by_external"] == QC.P6_ENTRY_E3_BY_EXTERNAL
    assert "NOT evaluated" in p6["status"]


def test_power_counting_mutations_detected():
    c = o1c()
    assert c["mutations_detected"] is True and all(c["mutations"].values()) and len(c["mutations"]) == 4


# ================================================================ polynomial-domain refusal (p23 contract revision)
num = lambda e: sp.numer(sp.together(e))  # noqa: E731
EXPRS = {"linear_and_pow": d * X + 1 / (d - 1), "power_base_only": 1 / (d ** 2 - 1), "d_alone": d,
         "mixed_pow": (d ** 2 - 2 * d - 2) / (32 * (d ** 2 - 1))}
PLANTS = {
    "rem": lambda e: sp.rem(num(e), d - 4, d), "resultant": lambda e: sp.resultant(num(e), d - 4, d),
    "compose": lambda e: sp.compose(num(e), 4, d), "div": lambda e: sp.div(num(e), d - 4, d),
    "prem": lambda e: sp.prem(num(e), d - 4, d),
    "Poly_shift_as_coeff_add": lambda e: sp.Poly(num(e), d).shift(-4).as_expr().as_coeff_add(),
    "Poly_rem_method": lambda e: sp.Poly(num(e), d).rem(sp.Poly(d - 4, d)),
    "Matrix_subs_rename": lambda e: sp.Matrix([e]).subs(d, y).subs(y, 4),
    "Matrix_xreplace_rename": lambda e: sp.Matrix([e]).xreplace({d: y}).subs(y, 4),
}


def test_poly_plant_list_matches_conventions():
    assert set(PLANTS) == set(QC.POLY_PLANTS_P23)


@pytest.mark.parametrize("expr", sorted(EXPRS))
@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_poly_refusal_every_plant_raises(plant, expr):
    with pytest.raises(dred.PrematureD4Substitution):
        PLANTS[plant](EXPRS[expr])


def test_poly_refusal_keeps_rational_algebra_and_authorised_path():
    e = EXPRS["mixed_pow"]
    assert sp.cancel(sp.apart(e, d) - e) == 0
    assert sp.cancel(sp.factor(sp.cancel(e + 1 / (d + 1))) - (d ** 2 + 30 * d - 34) / (32 * (d - 1) * (d + 1))) == 0
    assert dred.substitute_d(e, 4, "test_p23: authorised") == sp.Rational(1, 80)
    assert sp.rem(X ** 3 + 1, X - 1, X) == 2                     # d-free polynomial algebra unaffected


def test_contract_state_registered():
    r = CR.dred_revision(ROOT)
    assert r["ok"] and r["registered_blocks"] == ["p22 runtime d guard", "p23 polynomial-domain refusal"]
    assert CR.p22_block_unchanged(ROOT) and CR.p23_registered(ROOT)
    assert sha(ROOT / CR.DRED) == QC.P23_PINNED_SHA256.get(CR.DRED, sha(ROOT / CR.DRED))


# ================================================================ EV values, title qualifier, status
def test_ev_values_checked_against_pinned_and_archived():
    import release_p23 as R
    ok, rec = R.ev_values()
    assert ok and rec["archived_cert_pinned"]
    assert rec["values"]["calibration_rho_from_4D_pair"]["current"] == "1/2"
    assert rec["values"]["coefficient_Kc_E2"]["current"] == "-1/16"


def test_title_qualifier_readme_and_pdf_titles():
    first = (ROOT / "README.md").read_text().splitlines()[0]
    assert "two-point" in first and "QdS" in first
    assert (ROOT / "tools" / "build.py").read_text().count("for the two-point functions with QdS external legs") >= 2


def test_p23_release_status_and_flags():
    s = rs()
    assert s["revision"] == "p23" and s["publication"] == "accepted" and s["execution_pass"] is True
    for k in QC.EARNABLE_P23:
        assert s[k] == "earned", k
    assert s["bulk_symmetry_restored"] is False and s["symmetry_restored"] is False and s["O1_closure"] == "NOT_CLOSED"
    assert s["P6_entry"]["evaluated"] is False and s["three_point_defect"].startswith("not computed")
    assert s["O1"]["closable_in_XVI_P"] is False
    assert s["independent_rebuild_passed"] is not True and s["independent_rebuild_passed_p22"] is True
    assert s["hard_stops"] == QC.HARD_STOPS_P23 and s["hard_stops_hold"] is True


def test_disclosure_complete_exact_and_pinned():
    cl = rs()["change_log_vs_p22"]
    assert cl["undisclosed_changes"] == [] and cl["pinned_sha_mismatches"] == {}
    assert cl["disclosed_but_unpinned"] == [] and cl["disclosed_but_unchanged"] == []
    assert cl["registry_lists_match_disclosure"] is True


def test_version_label_p23():
    import build as B
    assert QC.VERSION_LABEL == "XVI-P p23" and B.QC.VERSION_LABEL == QC.VERSION_LABEL
    assert "certificates/P23_O1_scope.json" in B.VALUE_BLOCKS


# ================================================================ p23 gate mutations (fail closed; no stale status)
def _copy():
    d_ = Path(tempfile.mkdtemp(prefix="p23gate_"))
    shutil.copytree(ROOT, d_ / "XVI-P", ignore=shutil.ignore_patterns("__pycache__", "dist", "stale", "build"),
                    symlinks=True)
    return d_ / "XVI-P"


def _edit_json(d_, rel, fn):
    f = d_ / rel
    c = json.loads(f.read_text())
    fn(c)
    f.write_text(json.dumps(c, indent=1) + "\n")


def _rho_edited(d_):
    _edit_json(d_, "certificates/P22_evanescent.json",
               lambda c: c["EV_CT"]["a_closure"]["c.b"].__setitem__("calibration_rho_from_4D_pair", "1"))


def _E2_sign_flipped(d_):
    _edit_json(d_, "certificates/P22_evanescent.json", lambda c: c["EV_CT"].__setitem__("coefficient_Kc_E2", "1/16"))


def _poly_refusal_removed(d_):
    f = d_ / CR.DRED
    f.write_text(f.read_text().replace("\n_install_poly_refusal()\n", "\n"))


def _p22_block_edited(d_):
    f = d_ / CR.DRED
    f.write_text(f.read_text().replace('_deny(f"replace({query}, ...)")', '_deny(f"replace({query},...)")'))


def _o1_ledger_edited(d_):
    _edit_json(d_, QC.O1_LEDGER, lambda c: c["closure_check"].__setitem__("outcome", "CLOSED"))


def _p6_count_edited(d_):
    _edit_json(d_, "certificates/P23_O1_scope.json",
               lambda c: c["P6_entry_kappa3_three_point"].__setitem__("n_graphs", 14))


def _enlarge_flag_edited(d_):
    _edit_json(d_, "certificates/P23_O1_scope.json",
               lambda c: c["identity_at_kappa2"].__setitem__("enlarge_rule_triggered", True))


def _title_qualifier_removed(d_):
    f = d_ / "README.md"
    lines = f.read_text().splitlines(True)
    lines[0] = lines[0].replace("two-point", "2pt")
    f.write_text("".join(lines))


def _undisclosed_note(d_):
    f = d_ / "manuscript" / "notes" / "P18_D11.tex"
    f.write_text(f.read_text() + "\n% undisclosed\n")


def _pinned_tool_edited(d_):
    f = d_ / "tools" / "source_manifest.py"
    f.write_text(f.read_text() + "\n# undisclosed\n")


def _p22_independent_tampered(d_):
    f = d_ / "archival" / "p22" / "reproducibility" / "independent_rebuild_report_p22.json"
    f.write_text(f.read_text().replace('"pass": true', '"pass": false', 1))


MUTS = [_rho_edited, _E2_sign_flipped, _poly_refusal_removed, _p22_block_edited, _o1_ledger_edited, _p6_count_edited,
        _enlarge_flag_edited, _title_qualifier_removed, _undisclosed_note, _pinned_tool_edited,
        _p22_independent_tampered]


def _run(d_):
    return subprocess.run([sys.executable, "code/p5_calc/release_p23.py"], cwd=d_, capture_output=True, text=True,
                          timeout=1200)


@pytest.mark.parametrize("mut", MUTS, ids=lambda f: f.__name__)
def test_p23_gate_mutation_rejects_without_stale_status(mut):
    d_ = _copy()
    try:
        assert (d_ / "RELEASE_STATUS.json").exists()
        mut(d_)
        r = _run(d_)
        assert r.returncode == 1, r.stdout[-1500:]
        assert not (d_ / "certificates" / "P23_release.json").exists()
        assert (d_ / "certificates" / "P23_release_rejected.json").exists()
        assert not (d_ / "RELEASE_STATUS.json").exists() and not (d_ / "certificates" / "RELEASE_STATUS.json").exists()
    finally:
        shutil.rmtree(d_.parent, ignore_errors=True)


def test_p23_gate_accepts_unmodified_copy():
    d_ = _copy()
    try:
        r = _run(d_)
        assert r.returncode == 0, r.stdout[-1500:]
        s = json.loads((d_ / "RELEASE_STATUS.json").read_text())
        assert s["revision"] == "p23" and s["O1_closure"] == "NOT_CLOSED" and s["bulk_symmetry_restored"] is False
    finally:
        shutil.rmtree(d_.parent, ignore_errors=True)
