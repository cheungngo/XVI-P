#!/usr/bin/env python3
"""XVI-P p23 release gate (stage release on the O.1 direction; WITH the disclosed p23 contract revision).
Runs AFTER the p14r .. p22 gates (release_p22.py -> certificates/P22_release.json, the p22 LAYER record) and r
  +> equires:
  contract        : dred.py = p18 core byte-identical + the p22 block byte-identical to its release + the regi
  +> stered p23
                    block (contract_registry.p23_registered); exact sha pinned in P23_PINNED_SHA256;
  p22 layer       : P22_release accepted with all p22 earnables; p22_conventions.py byte-identical to the p22 
  +> zip; the p22
                    contract check, runtime guard probe and EV certificate check re-run LIVE (release_p22 help
  +> ers);
  EV values       : rho, the K'.c E2 and cb.c SE coefficients and the summed h.h counterterm coefficients in
                    certificates/P22_evanescent.json equal BOTH the pinned values (p23_conventions.EV_EXPECTED
  +> ) and the
                    archived p22 certificate (sha pinned)  -- reviewer p22: flags alone were checked;
  poly refusal    : LIVE probe in a fresh interpreter: every POLY_PLANTS_P23 form (reviewer p22: rem / resulta
  +> nt /
                    compose / div / prem / Poly.shift+as_coeff_add / Poly.rem / Matrix.subs and xreplace renam
  +> es) raises
                    PrematureD4Substitution on four expressions; rational-function algebra unchanged;
  O.1 scope       : certificates/P23_O1_scope.json -- the O.1 ledger copy matches its pinned sha; vertex rule
                    kappa^(legs-2); one-loop kappa^E; enumerated E=2 == frozen inventory; enlarge rule not tri
  +> ggered at
                    kappa^2; O1_closable_in_XVI_P false; P.6 entry counts as pinned; mutations detected;
  title qualifier : README title line carries the two-point / QdS qualifier (reviewer p22);
  disclosure      : every added/modified/removed file vs the pinned p22 zip list disclosed; disclosed files sh
  +> a-pinned;
  p22 independent : archived report pinned (023e5b83...), PASS, bound to the p22 tree/zip (same-box caveat);
  hard stops      : bulk_symmetry_restored false; O.1 NOT_CLOSED; insertion frozen; ...
Publication fails closed.  On reject: no P23_release.json and NO RELEASE_STATUS.json is left behind.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys  # noqa: E401
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p23_conventions as QC  # noqa: E402
import p22_conventions as Q22  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
import contract_registry as CR  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)
import release_p22 as R22  # noqa: E402   (helpers only)

ARCH_P22 = "archival/p22"
ARCH_P22_INDEP = f"{ARCH_P22}/reproducibility/independent_rebuild_report_p22.json"
STATUS_FILES = ("RELEASE_STATUS.json", "certificates/RELEASE_STATUS.json")
POLY_PROBE = r'''
import sys, json
sys.path[:0] = [sys.argv[1] + "/code/p5_entry"]
import sympy as sp, dred
d = dred.d; X = sp.Symbol("X"); y = sp.Symbol("y")
num = lambda e: sp.numer(sp.together(e))
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
out = {}
for k, f in PLANTS.items():
    out[k] = {}
    for n, e in EXPRS.items():
        try:
            f(e); out[k][n] = "NOT_RAISED"
        except dred.PrematureD4Substitution:
            out[k][n] = "RAISED"
        except Exception as x:
            out[k][n] = "OTHER:" + type(x).__name__
e = EXPRS["mixed_pow"]
alg = {"cancel_factor": str(sp.factor(sp.cancel(e + 1 / (d + 1)))), "apart": str(sp.apart(e, d)),
       "together": str(sp.together(e)), "authorised_value": str(dred.substitute_d(e, 4, "p23 probe: authorised
  +> "))}
print(json.dumps({"plants": out, "algebra": alg}))
'''
ALGEBRA_EXPECTED = {"cancel_factor": "(d**2 + 30*d - 34)/(32*(d - 1)*(d + 1))",
                    "apart": "1/32 - 1/(64*(d + 1)) - 3/(64*(d - 1))", "authorised_value": "1/80"}   # (16-8-2
  +> )/(32*15)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def poly_probe():
    p = subprocess.run([sys.executable, "-c", POLY_PROBE, str(ROOT)], capture_output=True, text=True, timeout=
  +> 600)
    try:
        r = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        return False, {"error": (p.stderr or p.stdout)[-1500:]}
    not_raised = {k: [n for n, v in r["plants"][k].items() if v != "RAISED"] for k in r["plants"]}
    not_raised = {k: v for k, v in not_raised.items() if v}
    alg_ok = all(r["algebra"].get(k) == v for k, v in ALGEBRA_EXPECTED.items())
    rec = {"plants": r["plants"], "not_raised": not_raised, "algebra": r["algebra"], "algebra_ok": alg_ok,
           "n_plants": len(r["plants"]), "all_plants_covered": set(r["plants"]) == set(QC.POLY_PLANTS_P23)}
    return bool(not not_raised and alg_ok and rec["all_plants_covered"]), rec


def contract_check():
    dr = CR.dred_revision(ROOT)
    cur = sha(ROOT / CR.DRED)
    pinned = QC.P23_PINNED_SHA256.get(CR.DRED)
    rec = {"dred_registry": dr, "p22_block_unchanged": CR.p22_block_unchanged(ROOT), "p23_registered":
           CR.p23_registered(ROOT), "dred_sha256": cur, "dred_pinned": pinned, "contract_revision_p23": QC.CON
  +> TRACT_REVISION,
           "other_contract_files_changed": [p.relative_to(ROOT).as_posix() for p in (ROOT / "code" / "p5_entry
  +> ").glob("*.py")
                                            if p.name != "dred.py" and p.relative_to(ROOT).as_posix() in
                                            jl(QC.P22_SOURCE_LIST).get("files", {}) and
                                            sha(p) != jl(QC.P22_SOURCE_LIST)["files"][p.relative_to(ROOT).as_p
  +> osix()]]}
    ok = bool(rec["p23_registered"] and (pinned is None or cur == pinned) and not rec["other_contract_files_ch
  +> anged"])
    return ok, rec


def p22_layer():
    r22 = jl("certificates/P22_release.json")
    base = jl(QC.P22_SOURCE_LIST).get("files", {})
    conv_same = base.get("code/p5_calc/p22_conventions.py") == sha(ROOT / "code/p5_calc/p22_conventions.py")
    con_ok, con = R22.contract_check()
    g_ok, g = R22.guard_probe()
    ev_ok, ev, _ = R22.evanescent_check()
    earned = {k: r22.get(k) == "earned" for k in Q22.EARNABLE_P22}
    rec = {"publication": r22.get("publication"), "earned": earned, "p22_conventions_byte_identical": conv_sam
  +> e,
           "live_contract_check": con_ok, "live_guard_probe": g_ok, "guard_not_raised": g.get("not_raised"),
           "live_evanescent_check": ev_ok, "hard_stops_hold": r22.get("hard_stops_hold"),
           "bulk_symmetry_restored": r22.get("bulk_symmetry_restored"), "O1_closure": r22.get("O1_closure")}
    ok = bool(r22.get("publication") == "accepted" and all(earned.values()) and conv_same and con_ok and g_ok 
  +> and ev_ok
              and r22.get("hard_stops_hold") is True and r22.get("bulk_symmetry_restored") is False
              and r22.get("O1_closure") == "NOT_CLOSED")
    return ok, rec, r22


def ev_values():
    cur = jl("certificates/P22_evanescent.json").get("EV_CT", {})
    arch_f = ROOT / ARCH_P22 / "certificates" / "P22_evanescent.json"
    arch_ok = arch_f.is_file() and sha(arch_f) == QC.P22_ARCHIVED_RECORDS[f"{ARCH_P22}/certificates/P22_evanes
  +> cent.json"]
    arch = json.loads(arch_f.read_text()).get("EV_CT", {}) if arch_ok else {}

    def get(c, k):
        if k == "calibration_rho_from_4D_pair":
            return c.get("a_closure", {}).get("c.b", {}).get(k)
        return c.get(k)
    rec = {}
    for k, v in QC.EV_EXPECTED.items():
        rec[k] = {"expected": v, "current": get(cur, k), "archived_p22": get(arch, k),
                  "ok": get(cur, k) == v and get(arch, k) == v}
    return bool(arch_ok and all(x["ok"] for x in rec.values())), {"archived_cert_pinned": arch_ok, "values": r
  +> ec}


def o1_scope():
    c = jl(f"certificates/{QC.CERT_PREFIX}_O1_scope.json")
    led = ROOT / QC.O1_LEDGER
    led_ok = led.is_file() and sha(led) == QC.O1_LEDGER_SHA256
    p6 = c.get("P6_entry_kappa3_three_point", {})
    rec = {"present": bool(c), "ledger_sha_pinned": led_ok,
           "cert_ledger_sha": c.get("O1_source", {}).get("sha256") == QC.O1_LEDGER_SHA256,
           "ledger_outcome_NOT_CLOSED": c.get("O1_source", {}).get("outcome") == "NOT_CLOSED",
           "vertex_rule_holds": c.get("vertex_rule_holds") is True,
           "one_loop_kappa_equals_E": c.get("one_loop_kappa_equals_E") is True,
           "frozen_E2_match": c.get("frozen_E2_match", {}).get("equal") is True,
           "enlarge_rule_not_triggered": c.get("identity_at_kappa2", {}).get("enlarge_rule_triggered") is Fals
  +> e,
           "O1_not_closable_in_XVI_P": c.get("O1_closable_in_XVI_P") is False,
           "E1_count": len(c.get("graphs_E1", [])) == QC.ONE_POINT_E1_GRAPHS,
           "E3_count": p6.get("n_graphs") == QC.P6_ENTRY_E3_GRAPHS,
           "E3_by_external": p6.get("by_external") == QC.P6_ENTRY_E3_BY_EXTERNAL,
           "mutations_detected": c.get("mutations_detected") is True, "pass": c.get("pass") is True}
    return bool(all(rec.values())), rec, c


def title_qualifier():
    first = (ROOT / "README.md").read_text().splitlines()[0]
    pdf_titles = (ROOT / "tools" / "build.py").read_text().count("for the two-point functions with QdS externa
  +> l legs")
    ok = "two-point" in first and "QdS" in first and pdf_titles >= 2          # README title + science/combine
  +> d PDF titles
    return ok, {"title_line": first, "pdf_title_lines_with_qualifier": pdf_titles, "required": QC.TITLE_QUALIF
  +> IER}


def p22_independent():
    f = ROOT / ARCH_P22_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P22_INDEP, "present": False, "pins_ok": False}
    rep = json.loads(f.read_text())
    rec = {"report": ARCH_P22_INDEP, "report_sha256_pinned": sha(f) == QC.P22_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "tree_matches_p22": rep.get("source_tree_sha256") == QC.P22_SOURCE_TREE_SHA256,
           "zip_matches_p22": rep.get("zip_sha256") == QC.P22_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])),
           "findings": [x.get("id") for x in rep.get("findings", []) if isinstance(x, dict)],
           "caveat": "same box (disclosed)",
           "NOT_inherited_by_p23": "bound to the p22 tree/zip; the p23 tree has its own (pending) independent 
  +> flag"}
    rec["archived_p22_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P22_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p22_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p22"] and rec["zip_matches_p22"] and rec["mismatches"] == 0)
    return ok, rec


def change_log():
    f = ROOT / QC.P22_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P22_ARCHIVED_RECORDS[QC.P22_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT)}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])

    def disclosed(x):
        return (x in QC.DISCLOSED_REVISIONS_P23 or x in QC.GENERATED_EXEMPT_P23
                or (x in added and x.startswith(QC.DISCLOSED_PREFIXES_ADDED_P23)))
    undisclosed = [x for x in added + removed + modified if not disclosed(x)]
    pin_bad = {k: {"pinned": h, "current": new.get(k)} for k, h in QC.P23_PINNED_SHA256.items() if new.get(k) 
  +> != h}
    unpinned = sorted(k for k in QC.DISCLOSED_REVISIONS_P23 if k not in QC.P23_PINNED_SHA256
                      and k not in ("code/p5_calc/p23_conventions.py", "README.md", "REBUILD_INSTRUCTIONS.md")
  +> )
    listed_unchanged = sorted(k for k in QC.DISCLOSED_REVISIONS_P23 if k not in added + modified + removed)
    registry_consistent = sorted(set(CR.P23_REVISED_FILES) | set(CR.P23_ADDED_FILES)) == sorted(
        k for k in QC.DISCLOSED_REVISIONS_P23 if not k.startswith(CR.P23_ADDED_PREFIXES))
    return {"base": f"{QC.P22_SOURCE_LIST} (pinned; files of the p22 zip sha256 {QC.P22_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok, "added": added, "removed": removed, "modified": modified,
            "undisclosed_changes": undisclosed, "pinned_sha_mismatches": pin_bad, "disclosed_but_unpinned": un
  +> pinned,
            "disclosed_but_unchanged": listed_unchanged, "registry_lists_match_disclosure": registry_consisten
  +> t,
            "counts": {"added": len(added), "removed": len(removed), "modified": len(modified)}}


def _main():
    con_ok, con = contract_check()
    l22_ok, l22, r22 = p22_layer()
    ev_ok, ev = ev_values()
    pp_ok, pp = poly_probe()
    o1_ok, o1, o1c = o1_scope()
    tq_ok, tq = title_qualifier()
    p22i_ok, p22i = p22_independent()
    hard = dict(QC.HARD_STOPS_P23)
    hard_ok = bool(all(r22.get("hard_stops", {}).get(k) == v for k, v in hard.items())
                   and r22.get("bulk_symmetry_restored") is False)
    cl = change_log()
    execution_pass = bool(con_ok and l22_ok and ev_ok and pp_ok and o1_ok and tq_ok and hard_ok
                          and cl["base_pinned_ok"] and not cl["undisclosed_changes"] and not cl["pinned_sha_mi
  +> smatches"]
                          and not cl["disclosed_but_unpinned"] and not cl["disclosed_but_unchanged"]
                          and cl["registry_lists_match_disclosure"] and p22i.get("pins_ok") is True)
    publish = execution_pass
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    earned = {k: ("earned" if (publish and r22.get(k) == "earned") else "not_earned") for k in Q22.EARNABLE_P2
  +> 2}
    earned.update({"O1_requirement_recorded": "earned" if publish and o1["ledger_sha_pinned"] else "not_earned
  +> ",
                   "one_loop_power_counting_verified": "earned" if publish and o1_ok else "not_earned",
                   "P6_entry_inventory": "earned" if publish and o1["E3_count"] and o1["E3_by_external"] else 
  +> "not_earned",
                   "d_poly_domain_refusal_verified": "earned" if publish and pp_ok else "not_earned",
                   "EV_values_verified": "earned" if publish and ev_ok else "not_earned"})
    ms = json.loads(json.dumps(r22.get("milestones", {})))
    cert = dict(r22)            # the p22 record carried forward (lower-layer keys), p23 keys added / overwrit
  +> ten below
    p6 = o1c.get("P6_entry_kappa3_three_point", {})
    cert.update({
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DA
  +> TE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": ("p23 (stage release on the O.1 direction): O.1 exact requirement and scope; one-loop p
  +> ower "
                        "counting and enlarge-rule check; P.6 ENTRY inventory (kappa^3 three-point, topology l
  +> evel, NOT "
                        "evaluated); polynomial-domain refusal for d (p23 contract revision); EV value check; 
  +> title "
                        "qualifier"),
        "execution_pass": execution_pass,
        "claim_status": (("p23. O.1 requires the one-loop kappa^2 bulk two-point sector on S_inv to close unde
  +> r a VERIFIED "
                          "retained identity with O.2 (classical kappa^2 master incl. grav ell_4), O.4, O.5, O
  +> .6, O.7 all "
                          "earned. Exact power counting: every vertex is kappa^(legs-2), so one-loop graphs ar
  +> e kappa^E; "
                          "the kappa^2 identity involves only E=2 and E=1, the enumeration reproduces the froz
  +> en kappa^2 "
                          "inventory exactly, and the enlarge rule is NOT triggered (no one-loop three-point s
  +> ector at "
                          "kappa^2). Three-point first appears at kappa^3: P.6 ENTRY inventory = 15 one-loop g
  +> raphs, NOT "
                          "evaluated. O.1 is not closable inside XVI-P (O.2 and the bulk ST4b identity are XVI
  +> -O/XVI-N "
                          "items, untouched). " + QC.TITLE_QUALIFIER + ". Bulk symmetry NOT restored/claimed; 
  +> O.1 "
                          "NOT_CLOSED.") if publish else "p23: not accepted"),
        "O1": {"requirement": o1c.get("O1_requirement"), "items_scope": o1c.get("O1_items_scope"),
               "closable_in_XVI_P": False, "reason": o1c.get("O1_closable_reason"), "ledger": QC.O1_LEDGER,
               "ledger_sha256": QC.O1_LEDGER_SHA256},
        "power_counting": {"vertex_rule": o1c.get("vertex_rule_holds"), "kappa_equals_E": o1c.get("one_loop_ka
  +> ppa_equals_E"),
                           "identity_at_kappa2": o1c.get("identity_at_kappa2"), "frozen_E2_match": o1c.get("fr
  +> ozen_E2_match")},
        "P6_entry": {"sector": "one loop, kappa^3, three-point (incl. antifield K,c,h and cs,c,c / phis,c,phi)
  +> ",
                     "n_graphs": p6.get("n_graphs"), "by_external": p6.get("by_external"),
                     "status": "inventory only (topology level); amplitude rules, counterterm domain, evaluati
  +> on, "
                               "defect and closure NOT done", "evaluated": False},
        "three_point_defect": "not computed (no graph evaluated)",
        "P5_calculation_status": QC.P5_STATUS_P23, "title_qualifier": tq,
        "d_poly_domain_refusal": {"ok": pp_ok, **{k: pp.get(k) for k in ("n_plants", "not_raised", "algebra", 
  +> "algebra_ok")}},
        "EV_values": ev, "contract": con, "p22_layer": l22, "o1_scope_check": o1, "change_log_vs_p22": cl,
        "open_pins": list(QC.OPEN_PINS_P23), "release_claim_accepted": publish,
        "publication": "accepted" if publish else "REJECTED",
        **earned,
        "disclosed_revisions_p23": QC.DISCLOSED_REVISIONS_P23,
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": ms,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p22": p22i_ok, "p22_independent_rebuild": p22i,
        "rebuild_flag_scope": ("author/independent flags refer to the CURRENT (p23) tree only (independent: pe
  +> nding until "
                               f"a reviewer report exists); independent_rebuild_passed_p22 refers to the p22 t
  +> ree "
                               f"{QC.P22_SOURCE_TREE_SHA256} / zip {QC.P22_SOURCE_ZIP_SHA256} (same-box caveat
  +> ), not "
                               "inherited"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_s
  +> ource.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p22_archive": ARCH_P22,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "symmetry_restored": False, "bulk_symmetry_restored": False,
        "O1_closure": "NOT_CLOSED", "insertion_status": "Frozen_negative_obstruction_preserved",
        "XV_B_opened": False, "XIV_J_opened": False, "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
            ("P22_release.json", f"{QC.CERT_PREFIX}_O1_scope.json") if (ROOT / "certificates" / n).is_file()},
    })
    if publish:
        st = ms.setdefault("status", {})
        st["P.6_entry"] = "inventory (one loop kappa^3 three-point, 15 graphs, topology level); not evaluated"
        st["O.1"] = "NOT_CLOSED (requirement recorded; not closable inside XVI-P)"
    cdir = ROOT / "certificates"
    if publish:
        txt = certio.dumps(cert)
        for s_ in STATUS_FILES:
            (ROOT / s_).write_text(txt)
        (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").unlink(missing_ok=True)
        (cdir / f"{QC.CERT_PREFIX}_release.json").write_text(txt)
        certio.write(ROOT / "ledgers" / f"{QC.CERT_PREFIX}_milestones.json", {
            "landmark": "XVI-P", "revision": QC.REVISION, "ledger": "milestones (authoritative definitions + s
  +> tatus)",
            **ms, "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
            "independent_rebuild_passed_p22": p22i_ok, "hard_stops": hard,
            "flags": {**earned, "quantum_inputs_evaluated": cert.get("quantum_inputs_evaluated"),
                      "bulk_symmetry_restored": False}})
    else:
        _reject({"contract_ok": con_ok, "contract": con, "p22_layer_ok": l22_ok, "p22_layer": l22, "EV_values_
  +> ok": ev_ok,
                 "EV_values": ev, "poly_probe_ok": pp_ok, "poly_not_raised": pp.get("not_raised"),
                 "poly_error": pp.get("error"), "O1_scope_ok": o1_ok, "O1_scope": o1, "title_qualifier_ok": tq
  +> _ok,
                 "p22_independent_pins_ok": p22i.get("pins_ok"), "hard_stops_hold": hard_ok,
                 "change_log_base_ok": cl["base_pinned_ok"], "undisclosed_changes": cl["undisclosed_changes"],
                 "pinned_sha_mismatches": cl["pinned_sha_mismatches"], "disclosed_but_unpinned": cl["disclosed
  +> _but_unpinned"],
                 "disclosed_but_unchanged": cl["disclosed_but_unchanged"],
                 "registry_lists_match_disclosure": cl["registry_lists_match_disclosure"]})
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publicat
  +> ion"],
                      "contract": con_ok, "p22_layer": l22_ok, "EV_values": ev_ok, "poly_probe": pp_ok, "O1_sc
  +> ope": o1_ok,
                      "title": tq_ok, "hard_ok": hard_ok, **earned, "author": author_ok, "independent_p23": in
  +> dep_ok,
                      "independent_p22": p22i_ok, "undisclosed": cl["undisclosed_changes"],
                      "pin_mismatch": list(cl["pinned_sha_mismatches"]), "unpinned": cl["disclosed_but_unpinne
  +> d"],
                      "unchanged": cl["disclosed_but_unchanged"], "registry_match": cl["registry_lists_match_d
  +> isclosure"],
                      "change_log_counts": cl["counts"]}, indent=1))
    return 0 if publish else 1


def _reject(detail):
    cdir = ROOT / "certificates"
    (cdir / f"{QC.CERT_PREFIX}_release.json").unlink(missing_ok=True)
    for s_ in STATUS_FILES:                      # a reject must not leave a stale RELEASE_STATUS.json
        (ROOT / s_).unlink(missing_ok=True)
    (cdir / f"{QC.CERT_PREFIX}_release_rejected.json").write_text(json.dumps(
        {"landmark": "XVI-P", "revision": QC.REVISION, "publication": "REJECTED", **detail}, indent=1, default
  +> =str) + "\n")


def main():
    try:
        return _main()
    except Exception as exc:  # noqa: BLE001   fail closed
        _reject({"error": f"{type(exc).__name__}: {exc}"})
        print(f"release_p23 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
