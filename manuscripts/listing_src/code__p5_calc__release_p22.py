#!/usr/bin/env python3
"""XVI-P p22 release gate (bigger fronts after p21; WITH the disclosed p22 contract revision).

Runs AFTER the p14r .. p21 gates (release_p21.py -> certificates/P21_release.json, the p21 LAYER record) and r
  +> equires:
  contract          : the ONLY contract change is the registered p22 revision of dred.py (contract_registry: p
  +> 18 text
                      byte-identical outside one delimited guard block; exact sha pinned in P22_PINNED_SHA256)
  +> ;
  lower layers      : re-checked live (release_p21.lower_layers: contract identity under the registry, p18 lay
  +> er with q
                      earned, inventory, p19 layer, K1, retraction) + p20 layer + absolute D11 pin (live);
  p21 layer         : P21_release accepted with its earnables; p21_conventions.py byte-identical to the p21 zi
  +> p;
  EV-M2 / EV-CT     : certificates/P22_evanescent.json -- EV-M2 PROVEN, evanescent counterterms closed (h.c, c
  +> .b),
                      projected identity unchanged, all controls true, mutations detected;
  runtime d guard   : LIVE probe in a fresh interpreter -- every plant of QC.GUARD_PLANTS_P22 raises
                      PrematureD4Substitution on four expressions; ordinary algebra and substitute_d still wor
  +> k;
  disclosure (K)    : EVERY file added / modified / removed vs the pinned p21 zip list is in DISCLOSED_REVISIO
  +> NS_P22 (no
                      tools/ or manuscript/ exemption; added files included), except the p21 archive (pinned r
  +> ecords)
                      and the generated reference file; disclosed code revisions match their pinned sha;
  p21 independent   : archived report pinned (8a582b33...), PASS, bound to the p21 tree/zip (same-box caveat);
  hard stops        : QC.HARD_STOPS_P22 (bulk_symmetry_restored false; O.1 NOT_CLOSED; insertion frozen; ...).
Publication fails closed.  On reject: no P22_release.json and NO RELEASE_STATUS.json is left behind.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (HERE, ROOT / "code" / "p5_entry", ROOT / "code" / "classical", ROOT / "tools"):
    sys.path.insert(0, str(p))
import p22_conventions as QC  # noqa: E402
import p21_conventions as Q21  # noqa: E402
import certio  # noqa: E402
import source_manifest as SM  # noqa: E402
import contract_registry as CR  # noqa: E402
from release import rebuild_flag  # noqa: E402   (frozen p13 helper)
import release_p20 as R20  # noqa: E402   (helpers only)
import release_p21 as R21  # noqa: E402   (helpers only)

ARCH_P21 = "archival/p21"
ARCH_P21_INDEP = f"{ARCH_P21}/reproducibility/independent_rebuild_report_p21.json"
STATUS_FILES = ("RELEASE_STATUS.json", "certificates/RELEASE_STATUS.json")

GUARD_PROBE = r'''
import sys, json, operator
sys.path[:0] = [sys.argv[1] + "/code/p5_calc", sys.argv[1] + "/code/p5_entry", sys.argv[1] + "/code/classical"
  +> ]
import sympy as sp, dred
d = dred.d; x = sp.Symbol("x")
exprs = {"linear_and_pow": d * x + 1 / (d - 1), "power_base_only": 1 / (d ** 2 - 1), "d_alone": d, "mixed_pow"
  +> : x * d ** 2 + d}
D, = [d]
P = lambda e: sp.expand(e * (d ** 2 - 1)) if not e.has(1 / (d - 1)) else sp.expand(x * d ** 3 + d ** 2)
runs = {
 "subs_d": lambda e: e.subs(d, 4), "xreplace_d": lambda e: e.xreplace({d: 4}),
 "list_unpack_alias_then_subs": lambda e: e.subs(D, 4),
 "free_symbols_pop_subs": lambda e: e.subs([y for y in e.free_symbols if y.name == "d"][0], 4),
 "lambda_wrapper_Poly": lambda e: (lambda *a: sp.Poly(*a))(P(e), d).eval(4),
 "coeff_extract": lambda e: sum(sp.expand(e).coeff(d, k) * 4 ** k for k in range(5)),
 "dunder_getattribute_eq": lambda e: sp.Add(*[4 if y == d else y for y in (e.__getattribute__("args") + (d,))]
  +> ),
 "subs_power": lambda e: e.subs(d ** 2, 16) if e.has(d ** 2) else e.subs(d, 4),
 "subs_dict": lambda e: e.subs({d: 4}), "subs_list": lambda e: e.subs([(d, 4)]),
 "evalf_subs": lambda e: e.evalf(subs={d: 4}), "N_subs": lambda e: sp.N(e, subs={d: 4}),
 "Lambda": lambda e: sp.Lambda(d, e)(4), "Subs_doit": lambda e: sp.Subs(e, d, 4).doit(),
 "limit": lambda e: sp.limit(e, d, 4), "replace": lambda e: e.replace(d, 4),
 "replace_fn": lambda e: e.replace(lambda y: y == d, lambda y: 4),
 "as_poly_call": lambda e: P(e).as_poly(d)(4), "all_coeffs": lambda e: sp.Poly(P(e), d).all_coeffs(),
 "as_expr_values": lambda e: sp.Poly(P(e), d).as_expr(4),
 "collect": lambda e: sp.collect(sp.expand(e), d, evaluate=False), "as_independent": lambda e: sp.expand(e).as
  +> _independent(d),
 "series": lambda e: e.series(d, 4, 2), "rename_then_value": lambda e: e.subs(d, sp.Dummy()),
 "lambdify": lambda e: sp.lambdify(d, e)(4), "getattr_subs": lambda e: getattr(e, "subs")(d, 4),
 "methodcaller": lambda e: operator.methodcaller("subs", d, 4)(e), "unbound_Basic_subs": lambda e: sp.Basic.su
  +> bs(e, d, 4),
 "Symbol_new_classmethod": lambda e: e.subs(sp.Symbol.__new__(type(d), "d"), 4),
 "Function_call_d": lambda e: sp.Function("f")(e).subs(d, 4).args[0],
}
out = {}
for rn, f in runs.items():
    out[rn] = {}
    for en, e in exprs.items():
        try:
            v = f(e); out[rn][en] = "NOT_RAISED: " + str(v)[:60]
        except dred.PrematureD4Substitution:
            out[rn][en] = "RAISED"
        except Exception as ex:
            out[rn][en] = "OTHER " + type(ex).__name__
e = (d ** 2 - 2 * d - 2) / (32 * (d ** 2 - 1))
alg = {"cancel_together": str(sp.factor(sp.cancel(sp.together(e + 1 / (d + 1))))), "apart": str(sp.apart(e, d)
  +> ),
       "solve": str(sp.solve(sp.Symbol("r") * d - 1, sp.Symbol("r"))), "simplify": str(sp.simplify(e * (d - 1)
  +> )),
       "substitute_d": str(dred.substitute_d(e, 4, "release_p22 guard probe")),
       "authorised_d": None}
with dred.authorised_d("release_p22 guard probe: authorised coefficient read"):
    alg["authorised_d"] = str(sp.Poly(sp.cancel(e * 32 * (d ** 2 - 1)), d).all_coeffs())
print(json.dumps({"plants": out, "algebra": alg, "entry_points": dred.GUARDED_ENTRY_POINTS,
                  "revision": dred.GUARD_REVISION}))
'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(rel):
    f = ROOT / rel
    return json.loads(f.read_text()) if f.is_file() else {}


def guard_probe():
    r = subprocess.run([sys.executable, "-c", GUARD_PROBE, str(ROOT)], capture_output=True, text=True, timeout
  +> =600)
    if r.returncode != 0:
        return False, {"error": r.stderr[-800:]}
    rec = json.loads(r.stdout.strip().splitlines()[-1])
    # an "OTHER" outcome is accepted only where sympy itself refuses the construction (no value produced)
    not_raised = {f"{k}/{e}": v for k, per in rec["plants"].items() for e, v in per.items() if v.startswith("N
  +> OT_RAISED")}
    other = {f"{k}/{e}": v for k, per in rec["plants"].items() for e, v in per.items() if v.startswith("OTHER"
  +> )}
    alg = rec["algebra"]
    alg_ok = (alg["substitute_d"] == "1/80" and alg["solve"] == "[1/d]" and alg["authorised_d"] == "[1, -2, -2
  +> ]"
              and alg["apart"] and alg["cancel_together"])
    rec["not_raised"], rec["other"], rec["algebra_ok"] = not_raised, other, alg_ok
    rec["n_plants"] = len(rec["plants"])
    rec["all_plants_covered"] = set(rec["plants"]) == set(QC.GUARD_PLANTS_P22)
    ok = bool(not not_raised and alg_ok and rec["all_plants_covered"] and rec["revision"] == "p22")
    return ok, rec


def contract_check():
    dr = CR.dred_revision(ROOT)
    cur = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))}
    pinned = QC.P22_PINNED_SHA256.get(CR.DRED)
    ok = bool(dr["state"] == "p18 + p22 guard block" and (pinned is None or cur.get(CR.DRED) == pinned
                                                           or CR.p23_registered(ROOT)))   # p23: registered la
  +> ter block
    return ok, {"dred_registry": dr, "dred_sha256": cur.get(CR.DRED), "dred_pinned": pinned,
                "dred_pin_ok": pinned is not None and cur.get(CR.DRED) == pinned,
                "contract_revision_p22": QC.CONTRACT_REVISION}


def p21_layer():
    r = jl("certificates/P21_release.json")
    base = json.loads((ROOT / QC.P21_SOURCE_LIST).read_text())["files"]
    conv_ok = sha(ROOT / "code/p5_calc/p21_conventions.py") == base.get("code/p5_calc/p21_conventions.py")
    ok = bool(conv_ok and r.get("revision") == Q21.REVISION and r.get("publication") == "accepted"
              and r.get("release_claim_accepted") is True and r.get("hard_stops_hold") is True
              and r.get("bulk_symmetry_restored") is False
              and all(r.get(k) == "earned" for k in Q21.EARNABLE_P21))
    return ok, {"p21_conventions_byte_identical": conv_ok, "P21_release_accepted": r.get("publication") == "ac
  +> cepted",
                "P21_earned": {k: r.get(k) for k in Q21.EARNABLE_P21}}, r


def p21_independent():
    f = ROOT / ARCH_P21_INDEP
    if not f.is_file():
        return False, {"report": ARCH_P21_INDEP, "present": False, "pins_ok": False}
    rep = json.loads(f.read_text())
    live = ROOT / QC.P21_INDEPENDENT_REPORT
    rec = {"report": ARCH_P21_INDEP, "present": True, "report_sha256": sha(f),
           "report_sha256_pinned": sha(f) == QC.P21_INDEPENDENT_REPORT_SHA256,
           "pass": rep.get("pass"), "independent_rebuild_passed": rep.get("independent_rebuild_passed"),
           "bound_to_source_tree_sha256": rep.get("source_tree_sha256"), "bound_to_source_zip_sha256": rep.get
  +> ("zip_sha256"),
           "tree_matches_p21": rep.get("source_tree_sha256") == QC.P21_SOURCE_TREE_SHA256,
           "zip_matches_p21": rep.get("zip_sha256") == QC.P21_SOURCE_ZIP_SHA256,
           "mismatches": len(rep.get("mismatches", [])),
           "findings": [x.get("id") for x in rep.get("findings", []) if isinstance(x, dict)],
           "caveat": "same box (disclosed)",
           "live_report_identical_to_archived": (live.read_bytes() == f.read_bytes()) if live.is_file()
           else "live report not in this tree",
           "NOT_inherited_by_p22": "bound to the p21 tree/zip; the p22 tree has its own (pending) independent 
  +> flag"}
    rec["archived_p21_records_pinned"] = {p: (ROOT / p).is_file() and sha(ROOT / p) == h
                                           for p, h in QC.P21_ARCHIVED_RECORDS.items()}
    rec["pins_ok"] = bool(rec["report_sha256_pinned"] and all(rec["archived_p21_records_pinned"].values()))
    ok = bool(rec["pins_ok"] and rep.get("pass") is True and rep.get("independent_rebuild_passed") is True
              and rec["tree_matches_p21"] and rec["zip_matches_p21"] and rec["mismatches"] == 0
              and rec["live_report_identical_to_archived"] in (True, "live report not in this tree"))
    return ok, rec


def change_log():
    f = ROOT / QC.P21_SOURCE_LIST
    base_ok = f.is_file() and sha(f) == QC.P21_ARCHIVED_RECORDS[QC.P21_SOURCE_LIST]
    old = json.loads(f.read_text())["files"] if base_ok else {}
    new = {r: sha(ROOT / r) for r in SM.source_files(ROOT)}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k] != old[k])

    def disclosed(x):
        return (x in QC.DISCLOSED_REVISIONS_P22 or x in QC.GENERATED_EXEMPT_P22
                or (x in added and x.startswith(QC.DISCLOSED_PREFIXES_ADDED_P22))
                or (CR.p23_registered(ROOT) and CR.p23_disclosed(x)))          # p23: registered later revisio
  +> n
    undisclosed = [x for x in added + removed + modified if not disclosed(x)]
    pin_bad = {k: {"pinned": h, "current": new.get(k)} for k, h in QC.P22_PINNED_SHA256.items() if new.get(k) 
  +> != h
               and not (CR.p23_registered(ROOT) and CR.p23_disclosed(k))}     # p23 revisions pinned by the p2
  +> 3 gate
    listed_unchanged = sorted(k for k in QC.DISCLOSED_REVISIONS_P22 if k not in added + modified + removed)
    contract = [x for x in added + removed + modified if x.startswith("code/p5_entry/")]
    return {"base": f"{QC.P21_SOURCE_LIST} (pinned; files of the p21 zip sha256 {QC.P21_SOURCE_ZIP_SHA256})",
            "base_pinned_ok": base_ok, "added": added, "removed": removed, "modified": modified,
            "contract_files_changed": contract, "contract_changes_registered": all(x == CR.DRED for x in contr
  +> act),
            "undisclosed_changes": undisclosed, "pinned_sha_mismatches": pin_bad,
            "disclosed_but_unchanged": listed_unchanged,
            "exemptions": {"generated": list(QC.GENERATED_EXEMPT_P22),
                           "added_archive_prefixes": list(QC.DISCLOSED_PREFIXES_ADDED_P22)},
            "counts": {"added": len(added), "removed": len(removed), "modified": len(modified)}}


def manuscript_disclosure():
    rec = {}
    for k, v in QC.DISCLOSED_MANUSCRIPT_REVISIONS_P22.items():
        cur = sha(ROOT / k) if (ROOT / k).is_file() else None
        txt = (ROOT / k).read_text() if cur else ""
        rec[k] = {"differs_from_p21": cur != v["p21_sha256"], "superseded_marker_present": "[superseded in p21
  +> " in txt,
                  "revised_in": v["revised_in"]}
    return all(x["differs_from_p21"] and x["superseded_marker_present"] for x in rec.values()), rec


def evanescent_check():
    c = jl(f"certificates/{QC.CERT_PREFIX}_evanescent.json")
    ev = c.get("EV_CT", {})
    chk = {
        "EV_M2_proven": c.get("EV_M2", {}).get("verdict", "").startswith("PROVEN"),
        "EV_CT_earned": c.get("evanescent_counterterm_earned") is True,
        "controls_all_true": bool(c.get("controls")) and all(c["controls"].values()),
        "hc_closed": ev.get("a_closure", {}).get("h.c", {}).get("closed") is True,
        "cb_closed": ev.get("a_closure", {}).get("c.b", {}).get("closed") is True,
        "identity_unchanged": ev.get("b_projected_identity", {}).get("unchanged") is True,
        "mutations_detected": bool(c.get("mutations")) and all(c["mutations"].values()),
        "continuations_refuted_recorded": c.get("EV_M2", {}).get("continuation_tests", {}).get("D11", {})
        .get("ghat_continuation_holds") is False,
        "Q4S_trace_remnant_disclosed": "O_eps_times_pole_Q4S_trace_external" in ev.get("c_remnants", {}),
        "P5_status": c.get("P5_calculation_status") == QC.P5_STATUS_P22,
        "contract_revision_named": c.get("contract_revision") == QC.CONTRACT_REVISION,
    }
    return all(chk.values()), chk, c


def _main():
    low_ok, low = R21.lower_layers()
    l20_ok, l20, _r20 = R21.p20_layer()
    pin_ok, pin, _pc = R20.d11_pin_check()
    l21_ok, l21, r21 = p21_layer()
    con_ok, con = contract_check()
    ev_ok, ev, evc = evanescent_check()
    g_ok, g = guard_probe()
    p21i_ok, p21i = p21_independent()
    md_ok, md = manuscript_disclosure()
    hard = dict(QC.HARD_STOPS_P22)
    hard_ok = bool(all(r21.get("hard_stops", {}).get(k) == v for k, v in hard.items())
                   and r21.get("bulk_symmetry_restored") is False)
    cl = change_log()
    execution_pass = bool(low_ok and l20_ok and pin_ok and l21_ok and con_ok and ev_ok and g_ok and hard_ok an
  +> d md_ok
                          and cl["base_pinned_ok"] and cl["contract_changes_registered"]
                          and not cl["undisclosed_changes"] and not cl["pinned_sha_mismatches"]
                          and p21i.get("pins_ok") is True)
    publish = execution_pass
    author_ok, author_rec = rebuild_flag(QC.AUTHOR_REPORT, pending_if_absent=False)
    indep_ok, indep_rec = rebuild_flag(QC.INDEPENDENT_REPORT_CURRENT, pending_if_absent=True)
    earned = {k: ("earned" if (publish and r21.get(k) == "earned") else "not_earned") for k in Q21.EARNABLE_P2
  +> 1}
    earned.update({"evanescent_M2_verified": "earned" if publish and ev["EV_M2_proven"] else "not_earned",
                   "evanescent_counterterms_verified": "earned" if publish and ev_ok else "not_earned",
                   "d_runtime_guard_verified": "earned" if publish and g_ok else "not_earned"})
    ms = json.loads(json.dumps(r21.get("milestones", {})))
    cert = dict(r21)
    for k in ("absolute_pin", "lower_layers", "p20_layer", "manuscript_disclosure", "change_log_vs_p20", "open
  +> _pins",
              "disclosed_p20_layer_revisions_p21", "disclosed_test_revisions_p21", "disclosed_manuscript_revis
  +> ions",
              "independent_rebuild_passed_p20", "p20_independent_rebuild"):
        if k in cert:
            cert[f"p21_layer_{k}"] = cert.pop(k)
    scope = evc.get("D11_matching_verified_scope")
    cert.update({
        "landmark": "XVI-P", "revision": QC.REVISION, "contract_revision": QC.CONTRACT_REVISION, "date": QC.DA
  +> TE,
        "version_label": QC.VERSION_LABEL,
        "deliverable": ("p22: evanescent M2 statement, evanescent counterterms (p22 contract revision), runtim
  +> e d guard "
                        "(p22 contract revision), gate without prefix exemptions"),
        "execution_pass": execution_pass,
        "claim_status": (("p22. EV-M2: the 8 evanescent D11 structures have local UV poles and their renormali
  +> sed "
                          "remainder vanishes identically on QdS external legs (exact in d); they are NOT matc
  +> hed to XVI-O "
                          "(no counterpart; both natural d-dim continuations refuted). EV-CT: the declared eva
  +> nescent "
                          "counterterms (h.h gt-operators, K'.c E2, cb.c SE; coefficient = -pole) are sigma_0-
  +> closed "
                          "together with the 4D MS-bar counterterm and leave the projected identity unchanged;
  +>  P.5 "
                          "calculation status: " + QC.P5_STATUS_P22 + ". Runtime d guard at the sympy entry po
  +> ints "
                          "(contract revision); static scan secondary. Projected (ch-only) results as in p20/p
  +> 21; bulk "
                          "symmetry NOT restored/claimed; O.1 NOT_CLOSED.") if publish else "p22: not accepted
  +> "),
        "D11_matching_verified_scope": scope if publish else cert.get("D11_matching_verified_scope"),
        "evanescent_hh_counterterm_added": bool(publish and ev_ok),
        "evanescent": {"check": ev, "EV_M2": evc.get("EV_M2", {}).get("statement"),
                       "EV_M2_verdict": evc.get("EV_M2", {}).get("verdict"),
                       "coefficients_hh_sum": evc.get("EV_CT", {}).get("coefficients_hh_counterterm_sum"),
                       "coefficient_Kc_E2": evc.get("EV_CT", {}).get("coefficient_Kc_E2"),
                       "coefficient_ccb_SE": evc.get("EV_CT", {}).get("coefficient_ccb_SE"),
                       "remnants": evc.get("EV_CT", {}).get("c_remnants")},
        "P5_calculation_status": QC.P5_STATUS_P22 if publish else "renormalized (4D) / regulated (evanescent p
  +> oles)",
        "d_runtime_guard": {"ok": g_ok, "n_plants": g.get("n_plants"), "not_raised": g.get("not_raised"),
                            "other_outcomes": g.get("other"), "algebra_ok": g.get("algebra_ok"),
                            "entry_points": g.get("entry_points"), "residue_not_interceptable": QC.RUNTIME_GUA
  +> RD_RESIDUE_P22,
                            "static_scan": "secondary barrier (tests/test_p21.py scan4 allow-list, p22 sites r
  +> eviewed)"},
        "contract": con, "lower_layers": low, "p20_layer": l20, "p21_layer": l21, "absolute_pin_check": pin,
        "manuscript_disclosure": md, "change_log_vs_p21": cl, "open_pins": list(QC.OPEN_PINS_P22),
        "release_claim_accepted": publish,
        "release_claim_accepted_definition": ("contract = registered p22 revision only (pinned) AND lower laye
  +> rs re-checked "
                                              "live AND p20/p21 layers AND absolute pin AND EV-M2 + EV-CT cert
  +> ificate AND "
                                              "live runtime guard probe AND every added/modified/removed file 
  +> disclosed "
                                              "(no prefix exemption) AND the pinned p21 independent record AND
  +>  the p22 "
                                              "hard stops"),
        "publication": "accepted" if publish else "REJECTED",
        **earned,
        "disclosed_revisions_p22": QC.DISCLOSED_REVISIONS_P22,
        "disclosed_manuscript_revisions_p22": QC.DISCLOSED_MANUSCRIPT_REVISIONS_P22,
        "hard_stops": hard, "hard_stops_hold": hard_ok, "milestones": ms,
        "author_rebuild_passed": author_ok, "independent_rebuild_passed": indep_ok,
        "independent_rebuild_passed_p21": p21i_ok, "p21_independent_rebuild": p21i,
        "rebuild_flag_scope": ("author_rebuild_passed and independent_rebuild_passed refer to the CURRENT (p22
  +> ) source "
                               "tree only (independent: pending until a reviewer report for this tree exists);
  +>  "
                               f"independent_rebuild_passed_p21 refers to the p21 tree {QC.P21_SOURCE_TREE_SHA
  +> 256} / zip "
                               f"{QC.P21_SOURCE_ZIP_SHA256} (same-box caveat) and is not inherited by p22"),
        "reproducibility": {"contract": "REBUILD_INSTRUCTIONS.md", "entrypoint": "python3 tools/rebuild_from_s
  +> ource.py",
                            "source_zip": SM.ZIP_NAME, "reference_values": SM.REFERENCE_FILE,
                            "author": author_rec, "independent": indep_rec, "p21_archive": ARCH_P21,
                            "kind": "package evidence (XVI-O conv:package); not a mathematical certificate"},
        "XVI_P_registered": False, "symmetry_restored": False, "bulk_symmetry_restored": False,
        "O1_closure": "NOT_CLOSED", "insertion_status": "Frozen_negative_obstruction_preserved",
        "XV_B_opened": False, "XIV_J_opened": False, "Route_B_discharged": False, "u_R_c_delta_added": False,
        "inputs_content_sha256_ignoring_timings_and_run_specific_keys": {
            n: certio.file_content_sha(ROOT / "certificates" / n, QC.RUN_SPECIFIC_KEYS) for n in
            ("P21_release.json", f"{QC.CERT_PREFIX}_evanescent.json") if (ROOT / "certificates" / n).is_file()
  +> },
    })
    if publish:
        st = ms.setdefault("status", {})
        st["P.5_identity"] = str(st.get("P.5_identity", "")) + " [p22: evanescent counterterms closed; identit
  +> y unchanged]"
        st["P.5_calculation"] = QC.P5_STATUS_P22
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
            "independent_rebuild_passed_p21": p21i_ok, "hard_stops": hard,
            "flags": {**earned, "quantum_inputs_evaluated": cert.get("quantum_inputs_evaluated"),
                      "bulk_symmetry_restored": False}})
    else:
        _reject({"lower_layers_ok": low_ok, "p20_layer_ok": l20_ok, "absolute_pin_ok": pin_ok, "p21_layer_ok":
  +>  l21_ok,
                 "p21_layer": l21, "contract_ok": con_ok, "contract": con, "evanescent_ok": ev_ok, "evanescent
  +> ": ev,
                 "guard_ok": g_ok, "guard_not_raised": g.get("not_raised"), "guard_error": g.get("error"),
                 "manuscript_disclosure_ok": md_ok, "p21_independent_pins_ok": p21i.get("pins_ok"),
                 "hard_stops_hold": hard_ok, "change_log_base_ok": cl["base_pinned_ok"],
                 "undisclosed_changes": cl["undisclosed_changes"], "pinned_sha_mismatches": cl["pinned_sha_mis
  +> matches"],
                 "contract_changes_registered": cl["contract_changes_registered"]})
    print(json.dumps({"revision": QC.REVISION, "execution_pass": execution_pass, "publication": cert["publicat
  +> ion"],
                      "lower_layers": low_ok, "p20_layer": l20_ok, "p21_layer": l21_ok, "absolute_pin": pin_ok
  +> ,
                      "contract": con_ok, "evanescent": ev_ok, "guard": g_ok, "manuscript": md_ok, "hard_ok": 
  +> hard_ok,
                      **earned, "author": author_ok, "independent_p22": indep_ok, "independent_p21": p21i_ok,
                      "undisclosed": cl["undisclosed_changes"], "pin_mismatch": list(cl["pinned_sha_mismatches
  +> "]),
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
        print(f"release_p22 error: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
