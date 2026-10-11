#!/usr/bin/env python3
"""p13: P.3 / P.4 completion dossier (authoritative; NOT a release-history retelling).

Each row links one claim to its executable evidence: file, function, certificate key(s) and test.  dossier.py 
  +> RESOLVES
every link mechanically on the current tree:
  * the function exists in the file (AST),
  * the certificate key exists and holds the expected value,
  * the test exists in the test file (AST; pass/fail is recorded separately in P13_test_results.json),
and writes
  certificates/P13_dossier.json          (machine-readable; all_links_resolved must be true for publication)
  manuscript/body/P13-dossier-table.tex  (the typeset table, generated from the same rows)
Milestone definitions come from conventions.MILESTONES; milestone status from RELEASE_STATUS.json.
The three quantum input slots are NAMED DEPENDENCIES (rows of the ch audit), never evaluated coefficients.
"""
from __future__ import annotations
import ast, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import conventions as C  # noqa: E402
import certio  # noqa: E402

T = "tests/test_p13.py"
QA, BI, BR, SA = ("certificates/P13_quartic_verified.json", "certificates/P13_boundary_identity.json",
                  "certificates/P13_brst_derivation.json", "certificates/P13_source_action.json")
GF, MS, CH, RS = ("certificates/P13_gauge_fixing_map.json", "certificates/P13_master_kappa2.json",
                  "certificates/P13_ch_source_audit.json", "RELEASE_STATUS.json")
GI = "ledgers/P13_graph_inventory.json"
F_CH, F_Q, F_GN = "code/p4_classical/ch_source_audit.py", "code/classical/quartic.py", "code/classical/grav_no
  +> ether.py"
F_BI, F_BR, F_SA = "code/classical/boundary_identity.py", "code/classical/brst_from_geometry.py", "code/classi
  +> cal/source_action.py"
F_GF, F_MS, F_RL = "code/classical/gauge_fixing_map.py", "code/classical/master_kappa2.py", "code/classical/re
  +> lease.py"
F_CI, F_BD = "code/classical/certio.py", "tools/build.py"
ALL_TRUE, NONEMPTY = "ALL_TRUE", "NONEMPTY"


def R(rid, claim, file, funcs, checks, tests):
    return {"id": rid, "claim": claim, "file": file, "functions": list(funcs),
            "checks": [{"source": s, "key": k, "expect": e} for s, k, e in checks], "tests": list(tests)}


CHAINS = [
    ("P.3", "projection -> dependency rows -> graphs", [
        R("P3.1", "ch output projection fixed (c^1 h^1, ghost number 1, kappa^2, one loop, transformed variabl
  +> es)",
          F_CH, ["main"], [(CH, "/ch_projection_defined", True), (CH, "/ch_pattern/ghost_number", 1)],
          ["test_ch_rows_and_quantum_input_slots"]),
        R("P3.2", "vertex inventory generated from S_Psi (not copied)", F_CH, ["S_psi_inventory", "vertex_opti
  +> ons"],
          [(CH, "/vertex_inventory", NONEMPTY), (CH, "/checks/b_has_no_interaction_vertex", True)],
          ["test_ch_rows_and_quantum_input_slots"]),
        R("P3.3", "dependency rows exhaustive: regenerated rows equal the published rows", F_CH,
          ["audit", "regenerate_and_compare"],
          [(CH, "/checks/regenerated_rows_match_published", True), (CH, "/regeneration/complete", True)],
          ["test_e2e_dropped_hstar_c_row"]),
        R("P3.4", "6 rows: 3 surviving, 3 derived zero (S2, cbar*, b* rows)", F_CH, ["audit"],
          [(CH, "/rows_total", 6), (CH, "/rows_surviving", 3), (CH, "/rows_derived_zero", 3)],
          ["test_ch_rows_and_quantum_input_slots"]),
        R("P3.5", "enumeration lemma (justifies max_len = 2) checked mechanically", F_CH, ["enumeration_lemma"
  +> ],
          [(CH, "/enumeration_lemma/holds", True)], ["test_enumeration_lemma"]),
        R("P3.6", "graph topologies generated and named; no unnamed graph", F_CH, ["enumerate_graphs", "name_g
  +> raph"],
          [(GI, "/names_TBD", []), (GI, "/graphs", NONEMPTY), (CH, "/checks/names_TBD_empty", True)],
          ["test_ch_rows_and_quantum_input_slots"]),
        R("P3.7", "P.3 flags", F_RL, ["_main"],
          [(RS, "/flags/ch_projection_defined", True), (RS, "/flags/ch_dependency_inventory_complete", True)],
          ["test_milestones_consistent"]),
    ]),
    ("P.4", "classical coefficient -> export -> verification", [
        R("P4.A1", "C3 boundary identity sqrt(-g)R - L_GG = -d_mu B^mu on generic jets", F_BI, ["generic_jet_p
  +> roof"],
          [(BI, "/C3_proved", True)], ["test_C3_boundary_identity_generic_and_conformal"]),
        R("P4.A2", "ell_2, ell_3, ell_4 built and exported; export hash == quartic cert == master input", F_Q,
          ["build_and_export"], [(RS, "/hash_consistency/consistent", True), (QA, "/ell4_sha256", NONEMPTY)],
          ["test_stale_ell4_hash_blocks_master"]),
        R("P4.A3", "C1 inverse, C2 det/trace-log (10 symbolic components)", F_Q, ["inverse_control", "det_trac
  +> elog_generic"],
          [(QA, "/acceptance_controls_deterministic/C1", True), (QA, "/acceptance_controls_deterministic/C2", 
  +> True)],
          ["test_quartic_acceptance_all_deterministic"]),
        R("P4.A4", "C4 export == independent evaluator (exact polynomial identity)", F_Q, ["export_identity"],
          [(QA, "/acceptance_controls_deterministic/C4", True)], ["test_quartic_acceptance_all_deterministic"]
  +> ),
        R("P4.A5", "C5/C6 ell_3 = XII-C, ell_2 = XI-A Fierz-Pauli modulo divergences (pinned XVI-N grav_densit
  +> y)", F_Q,
          ["regression_deterministic", "xvin_symbolic"],
          [(QA, "/acceptance_controls_deterministic/C5", True), (QA, "/acceptance_controls_deterministic/C6", 
  +> True)],
          ["test_quartic_acceptance_all_deterministic"]),
        R("P4.A6", "C7 gravitational Noether identities on the exports, kappa^0..kappa^2", F_GN, ["noether"],
          [(QA, "/controls/C7_accepted_orders", ALL_TRUE)], ["test_grav_noether_exact_and_mutation"]),
        R("P4.A7", "quartic mutations rejected; quartic flag", F_Q, ["main"],
          [(QA, "/mutations_all_rejected", True), (RS, "/flags/quartic_generator_verified", True)],
          ["test_e2e_corrupted_ell4_coefficient"]),
    ]),
    ("P.4", "transformations -> source terms", [
        R("P4.B1", "ghost law derived from s^2 = 0 (unique lambda = 1)", F_BR, ["solve_ghost_law"],
          [(BR, "/ghost_law_derivation/lam_solutions", ["1"])], ["test_brst_and_source_terms_derived"]),
        R("P4.B2", "s_2 derived zero in every sector; s nilpotent at all orders", F_BR, ["per_sector_expansion
  +> ", "nilpotency"],
          [(BR, "/s2_per_sector", "ALL_EQ:derived_zero"), (BR, "/nilpotency_exact_all_orders", True)],
          ["test_brst_and_source_terms_derived"]),
        R("P4.B3", "sigma_A derived from the generator rule (unique); antifield-linear, no kappa^2 X terms", F
  +> _SA,
          ["derive_sigma", "build_X_inv"],
          [(SA, "/sigma_unique", True), (SA, "/X_kappa2_terms", 0), (SA, "/antifield_linear", True)],
          ["test_brst_and_source_terms_derived", "test_e2e_flipped_odd_sign", "test_e2e_omitted_cstar_term"]),
    ]),
    ("P.4", "gauge map -> Hessians -> source convention", [
        R("P4.C1", "antifield shift orientation derived (eps = -1); S_Psi = S + s Psi mod d", F_GF, ["build", 
  +> "shift_map"],
          [(GF, "/derived_eps", -1), (GF, "/S_Psi_equals_S_plus_sPsi_mod_d", True)], ["test_e2e_altered_gauge_
  +> shift"]),
        R("P4.C2", "canonicity of the map on all 299 (anti)field pairs", F_GF, ["canonicity"],
          [(GF, "/canonicity/pass", True), (GF, "/canonicity/pairs_tested", 299)],
          ["test_gauge_hessian_generic_and_full_canonicity"]),
        R("P4.C3", "graviton Hessian at generic symbolic k: Schur complement k^2 P, propagator (k^2 P)^-1", F_
  +> GF,
          ["hessian_check"],
          [(GF, "/propagators/graviton/schur_equals_k2P", True), (GF, "/propagators/graviton/propagator_hh_equ
  +> als_inv_k2P", True)],
          ["test_gauge_hessian_generic_and_full_canonicity"]),
        R("P4.C4", "ghost (i cbar Box c) and scalar (-Box) kinetic terms; propagators match transformed Hessia
  +> ns", F_GF,
          ["ghost_kinetic_check"],
          [(GF, "/propagators/ghost/match", True), (GF, "/propagators/scalar/match", True),
           (GF, "/propagators_match_transformed_Hessians", True)], ["test_gauge_hessian_generic_and_full_canon
  +> icity"]),
        R("P4.C5", "source convention Gamma_Psi(Phi,Phi*') := Gamma(Phi, Phi*' - dPsi/dPhi): classical pullbac
  +> k, NOT a quantum theorem",
          F_GF, ["build"],
          [(GF, "/source_identity_relation_defined", True),
           (GF, "/source_identity_relation/status", "CONTAINS:NOT an independently established quantum")],
          ["test_gauge_hessian_generic_and_full_canonicity"]),
        R("P4.C6", "gauge-map flag", F_RL, ["_main"], [(RS, "/flags/gauge_fixing_map_constructed", True)],
          ["test_milestones_consistent"]),
    ]),
    ("P.4", "master component -> residual record -> acceptance gate", [
        *[R(f"P4.D{n + 1}", f"master equation at kappa^{n}: every antifield-number component; grav af0 record;
  +>  gate",
            F_MS, ["run", "XX_by_order", "grav_deterministic"],
            [(MS, f"/table_by_kappa_and_antifield_number/kappa{n}", ALL_TRUE),
             (MS, f"/details/grav_af0_deterministic/kappa{n}/Q_terms", [0, 0, 0, 0]),
             (MS, f"/details/grav_af0_deterministic/kappa{n}/Q_identically_zero", True),
             (RS, f"/residual_records/master_grav_per_order/kappa{n}/accepted", True)],
            ["test_residual_records_regenerated_and_agree"]) for n in (0, 1, 2)],
        R("P4.D4", "no required master residual; no unconditional pass field", F_MS, ["master_residuals"],
          [(MS, "/required_master_residuals", [])], ["test_master_no_unconditional_pass_and_deterministic"]),
        R("P4.D5", "count/flag invariant on every record; quartic and master records agree", F_CI,
          ["invariant_violations", "cross_check"],
          [(RS, "/deterministic_prerequisites/residual_record_invariants_all_certificates", True),
           (RS, "/residual_records/cross_certificate/agree", True)],
          ["test_certificate_mutation_rejects_publication", "test_certio_rejects_inconsistent_record_before_se
  +> rialization"]),
        R("P4.D6", "acceptance gate: release_claim_accepted and classical readiness (P.4)", F_RL, ["_main"],
          [(RS, "/release_claim_accepted", True), (RS, "/classical_readiness_for_ch_identity", True),
           (RS, "/flags/required_classical_BV_components_verified", True)],
          ["test_release_accepted_and_hard_stops"]),
        R("P4.D7", "publication gate re-invoked before every pdf/zip/manifest stage, also on resumed builds", 
  +> F_BD,
          ["publication_gate", "pdf_readback"], [], ["test_resumed_stage_build_blocked"]),
    ]),
]


def ptr(obj, key):
    cur = obj
    for part in [p for p in key.split("/") if p != ""]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def matches(val, exp):
    if exp == ALL_TRUE:
        return isinstance(val, dict) and bool(val) and all(v is True for v in val.values())
    if exp == NONEMPTY:
        return bool(val)
    if isinstance(exp, str) and exp.startswith("ALL_EQ:"):
        return isinstance(val, dict) and bool(val) and all(v == exp[7:] for v in val.values())
    if isinstance(exp, str) and exp.startswith("CONTAINS:"):
        return isinstance(val, str) and exp[9:] in val
    return val == exp and type(val) is type(exp)


def defs(rel):
    return {n.name for n in ast.walk(ast.parse((ROOT / rel).read_text())) if isinstance(n, ast.FunctionDef)}


def short(v, n=48):
    s = json.dumps(v)
    return s if len(s) <= n else s[:n - 3] + "..."


def resolve_row(row, cache):
    out = dict(row)
    fdefs = defs(row["file"]) if (ROOT / row["file"]).exists() else set()
    out["functions_found"] = {f: f in fdefs for f in row["functions"]}
    tdefs = cache.setdefault(T, defs(T))
    out["tests_found"] = {t: t in tdefs for t in row["tests"]}
    res = []
    for c in row["checks"]:
        try:
            doc = cache.setdefault(c["source"], json.loads((ROOT / c["source"]).read_text()))
            val = ptr(doc, c["key"])
            ok = matches(val, c["expect"])
            res.append({**c, "value": short(val), "ok": ok})
        except Exception as exc:  # noqa: BLE001
            res.append({**c, "value": f"UNRESOLVED ({type(exc).__name__})", "ok": False})
    out["checks"] = res
    out["resolved"] = all(out["functions_found"].values()) and all(out["tests_found"].values()) and \
        all(c["ok"] for c in res)
    return out


def slots(cache):
    ch = cache.setdefault(CH, json.loads((ROOT / CH).read_text()))
    gi = cache.setdefault(GI, json.loads((ROOT / GI).read_text()))
    rows = {r["id"]: r for r in ch["surviving_rows"]}
    out = []
    for s in C.QUANTUM_INPUT_SLOTS:
        r = rows.get(s["row"], {})
        graphs = r.get("graphs", [])
        ok = (r.get("Gamma1_pattern") == s["Gamma1_pattern"] and r.get("status") == "surviving_unevaluated"
              and [g.split("_")[0] for g in graphs] == s["graphs"] and all(g in gi["graphs"] for g in graphs))
        out.append({**s, "graph_names": graphs, "status": "named dependency; NOT an evaluated coefficient",
                    "graph_status": {g: gi["graphs"].get(g, {}).get("status") for g in graphs},
                    "evidence": {"file": F_CH, "function": "audit", "certificate": CH,
                                 "key": f"/surviving_rows/{list(rows).index(s['row']) if s['row'] in rows else
  +>  '?'}",
                                 "test": "test_ch_rows_and_quantum_input_slots"},
                    "resolved": ok})
    return out


def build():
    cache = {}
    rs = json.loads((ROOT / RS).read_text())
    chains = [{"milestone": m, "chain": name, "rows": [resolve_row(r, cache) for r in rows]} for m, name, rows
  +>  in CHAINS]
    sl = slots(cache)
    resolved = all(r["resolved"] for ch in chains for r in ch["rows"]) and all(s["resolved"] for s in sl)
    d = {
        "landmark": "XVI-P", "revision": C.REVISION, "document": "P.3/P.4 completion dossier",
        "status_of_this_document": ("package evidence for XVI-P (unregistered; XVI-O conv:package): an archive
  +> , a listing "
                                    "and a manifest are not a series certificate. Does not update XVI-O "
                                    "(prop:kappa2-master stays Partial there; symmetry_restored false; O.1 NOT
  +> _CLOSED)."),
        "milestone_definitions": C.MILESTONES, "milestone_status": rs.get("milestones", {}),
        "chains": chains, "quantum_input_slots": sl,
        "hard_stops": rs.get("hard_stops", {}),
        "reproducibility": {k: rs.get(k) for k in ("author_rebuild_passed", "independent_rebuild_passed")},
        "P3_P4_frozen_as_P5_inputs": rs.get("milestones", {}).get("P3_P4_frozen_as_P5_inputs"),
        "all_links_resolved": resolved,
        "n_rows": sum(len(ch["rows"]) for ch in chains), "n_slots": len(sl),
    }
    return d


# ---------------- LaTeX ----------------
def tex(s):
    rep = {"\\": r"\textbackslash{}", "_": r"\_", "^": r"\^{}", "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%"
  +> ,
           "#": r"\#", "$": r"\$", "~": r"\~{}", "<": r"\textless{}", ">": r"\textgreater{}"}
    return "".join(rep.get(ch, ch) for ch in str(s))


def brk(s):
    """escaped text with permitted line breaks after '/', '_' and '.' (long certificate keys in narrow columns
  +> )"""
    return tex(s).replace("/", r"/\allowbreak{}").replace(r"\_", r"\_\allowbreak{}").replace(".", r".\allowbre
  +> ak{}")


def disp(v):
    try:
        x = json.loads(v)
        return x[:16] + "..." if isinstance(x, str) and len(x) > 24 else short(x, 34)
    except Exception:  # noqa: BLE001            (already truncated by short())
        return v if len(v) <= 34 else v[:18] + "..."


def table(d):
    L = [r"{\scriptsize\setlength{\tabcolsep}{2.5pt}",
         r"\begin{longtable}{@{}p{0.9cm}p{4.1cm}p{3.5cm}p{5.0cm}p{3.0cm}@{}}",
         r"\toprule id & claim & file :: function & certificate key = value & test \\ \midrule \endhead"]
    for ch in d["chains"]:
        L.append(r"\multicolumn{5}{@{}l}{\textbf{" + tex(ch["milestone"]) + ": " + tex(ch["chain"]) + r"}} \\"
  +> )
        for r in ch["rows"]:
            fn = r"\texttt{" + brk(r["file"].split("/")[-1]) + "} :: " + ", ".join(
                r"\texttt{" + brk(f) + "}" for f in r["functions"])
            ks = r"\newline ".join(r"\texttt{" + brk(c["source"].split("/")[-1].replace("P13_", "").replace(".
  +> json", "")
                                                     + c["key"]) + "} = " + (r"\emph{all entries true}" if c["
  +> expect"] == ALL_TRUE and c["ok"] else brk(disp(c["value"])))
                                   for c in r["checks"]) or "(build-time gate)"
            ts = r"\newline ".join(r"\texttt{" + brk(t.replace("test_", "")) + "}" for t in r["tests"])
            L.append(f"{tex(r['id'])} & {tex(r['claim'])} & {fn} & {ks} & {ts} \\\\")
        L.append(r"\midrule")
    L.append(r"\multicolumn{5}{@{}l}{\textbf{Quantum input slots (named dependencies, NOT evaluated coefficien
  +> ts)}} \\")
    for s in d["quantum_input_slots"]:
        L.append(f"slot & {tex(s['slot'])} ($\\Gamma_1$ pattern \\texttt{{{tex(s['Gamma1_pattern'])}}}) & "
                 r"\texttt{ch\_source\_audit.py} :: \texttt{audit} & \texttt{ch\_source\_audit" + brk(s["evide
  +> nce"]["key"])
                 + "} = " + tex(", ".join(s["graphs"])) + r" & \texttt{" + brk("ch_rows_and_quantum_input_slot
  +> s") + r"} \\")
    rp = d["reproducibility"]
    L.append(r"\midrule \multicolumn{5}{@{}p{16.5cm}@{}}{\textbf{Reproducibility flags (package evidence, read
  +>  from "
             r"RELEASE\_STATUS at build time):} \texttt{author\_rebuild\_passed} = " + tex(json.dumps(rp.get("
  +> author_rebuild_passed")))
             + r"; \texttt{independent\_rebuild\_passed} = " + tex(json.dumps(rp.get("independent_rebuild_pass
  +> ed")))
             + r"; \texttt{P3\_P4\_frozen\_as\_P5\_inputs} = " + tex(json.dumps(d.get("P3_P4_frozen_as_P5_inpu
  +> ts"))) + r".} \\")
    L += [r"\bottomrule", r"\end{longtable}}"]
    return "\n".join(L) + "\n"


def main():
    d = build()
    certio.write(ROOT / "certificates" / "P13_dossier.json", d)
    (ROOT / "manuscript" / "body").mkdir(parents=True, exist_ok=True)
    (ROOT / "manuscript" / "body" / "P13-dossier-table.tex").write_text(table(d))
    bad = [r["id"] for ch in d["chains"] for r in ch["rows"] if not r["resolved"]] + \
          [s["slot"] for s in d["quantum_input_slots"] if not s["resolved"]]
    print(json.dumps({"all_links_resolved": d["all_links_resolved"], "rows": d["n_rows"], "slots": d["n_slots"
  +> ],
                      "unresolved": bad}))
    return 0 if d["all_links_resolved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
