#!/usr/bin/env python3
"""XVI-P p23 REBUILD ENTRYPOINT (the reproducibility contract; see REBUILD_INSTRUCTIONS.md).

Run from the root of an unpacked XVI-P-p23-source-only.zip (a tree containing SOURCE ONLY):

    python3 tools/rebuild_from_source.py [--inherited auto|workspace|vendored] [--report PATH]

It
  1. records the environment (Python, sympy, mpmath, pytest, pdfTeX, pdftotext) and compares it with the refer
  +> ence;
  2. refuses to run unless the tree is source-only: no generated certificates, exports, ledgers, listings, PDF
  +> s,
     zips, build/ or __pycache__ caches (tools/source_manifest.py defines the source set);
  3. verifies the inherited dependencies and pins: XVI-M (sha 41aa1099...739ea), the XVI-N grav_density.py rea
  +> d
     by C5/C6, the verbatim XVI-O (o70-sync) code and notes (provenance/XVI-O_o70_source_tree.json) and every
     inherited data input listed in reproducibility/inherited_data_pins.json;
  4. runs the full pipeline tools/build.py (fresh: no cache) with sync redirected INSIDE the copy
     (build/rebuild_sync) and every Python file access traced (tools/read_trace/sitecustomize.py);
     this regenerates the polynomial exports (ell2/ell3/ell4) and all residual records, the inherited O5
     matter-loop records, the P.5 entry contract (symbolic amplitude rules and integrands, counterterm domain,
     quantum object, prescription + D11 matching), the p15 calculation (integral library, Batch A, D13), the p
  +> 15
     release gate, the p16 calculation (E2 decoupling proof, Batch C D01/D03), the p16 release gate, the p17 c
  +> alculation (D01/D03
     evanescent poles vs the ch slot), the p17 release gate, the p18 calculation (M2 discharge, D11, full hh s
  +> lot)
     and the p18 release gate, the p19 calculation (projected ch-identity defect, counterterm solve, p20: full
     closure) and the p19 layer gate, the p20 D11 pin (p21: absolute pin derivation) and the p20 layer gate, t
  +> he p21 layer gate, the p22 evanescent
     calculation (EV-M2, EV-CT) and the p22 layer gate (incl. the live runtime d-guard probe), the p23 power c
  +> ounting / O.1 scope
     (power_counting.py) and the p23 release gate (live poly-refusal probe, EV value check), runs the baseline
  +> , certificate/gate-mutation
     and resumed-build tests, typesets the PDFs, zips and writes the manifest;
  5. checks: release accepted; test groups baseline / certificate_mutation / resumed_build all passed; the PDF
     readback equals the machine-readable residual records AND (p16, F4) the D13 / Batch A / Batch C / E2 / (p
  +> 17) hh-slot / (p18) M2, D11, full-slot value
     blocks, and every page footer carries the single version label; the external manifest verifies; the rebui
  +> lt
     source-only zip equals this tree; no file outside the tree was read except a pinned inherited input;
  6. compares with the author's reference values (reproducibility/reference_values_p23.json): export hashes, c
  +> ertificate
     content hashes ignoring wall-clock timings (and the run-specific reproducibility block), Q/W counts, flag
  +> s,
     milestone status and test counts, and writes a comparison report (default build/rebuild_report.json).
Exit code 0 iff every step passed and every compared value is equal.

Author mode (once, on the author's fully built tree): --write-reference writes reproducibility/reference_value
  +> s_p23.json.
(The p13 reproducibility/reference_values.json is NOT written or read by p14; its archived copy
archival/p13/reference_values_p13.json is pinned and read by the p13 freeze check F3.)
This is package evidence (XVI-O conv:package), not a mathematical certificate.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True          # the source-only check must not be defeated by our own caches
import json, os, platform, re, subprocess, tempfile, time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "code" / "classical"))
import source_manifest as SM  # noqa: E402
import certio  # noqa: E402
import inherited  # noqa: E402
import conventions as C  # noqa: E402   (frozen p13 classical conventions)
sys.path.insert(0, str(ROOT / "code" / "p5_entry"))
import p14_conventions as PC  # noqa: E402
sys.path.insert(0, str(ROOT / "code" / "p5_calc"))
import p15_conventions as Q15  # noqa: E402
import p23_conventions as QC  # noqa: E402
import p22_conventions as Q22  # noqa: E402
import p21_conventions as Q21  # noqa: E402
import p20_conventions as Q20  # noqa: E402
import p19_conventions as Q19  # noqa: E402
import p18_conventions as Q18  # noqa: E402
import p17_conventions as Q17  # noqa: E402
import p16_conventions as Q16  # noqa: E402

XVI_M_PIN = "41aa109935f40ddee3109de62c46329c189b5408007970cc90ed5611dc4739ea"
TRACE = ROOT / "build" / "rebuild_trace.log"
SYNC = ROOT / "build" / "rebuild_sync"
CERTS = ("P13_boundary_identity", "P13_quartic_verified", "P13_brst_derivation", "P13_source_action",
         "P13_gauge_fixing_map", "P13_ch_source_audit", "P13_master_kappa2", "P14_release", "P14_closure_relea
  +> se",
         "P14_dossier", "P14_quantum_object", "P14_prescription_D11_matching", "P14_counterterm_domain",
         "P14_amplitude_rules", "P14_dred_rules", "P15_integral_library", "P15_batchA", "P15_D13", "P15_releas
  +> e",
         "P16_E2_evanescent", "P16_batchC", "P16_release", "P17_hh_slot", "P17_release", "P18_D11_M2", "P18_D1
  +> 1", "P18_hh_slot", "P18_release",
         "P19_defect", "P19_release", "P20_D11_pin", "P20_release", "P21_release", "P22_evanescent", "P22_rele
  +> ase", "P23_O1_scope", "P23_release")
LEDGERS = ("P13_ch_dependency_rows", "P13_graph_inventory", "P14_milestones", "P15_milestones", "P16_milestone
  +> s", "P17_milestones", "P18_milestones", "P19_milestones", "P20_milestones", "P21_milestones", "P22_milest
  +> ones", "P23_milestones")
# p13 freeze inputs read by the p14 pipeline: pinned by sha256 in code/p5_entry/p14_conventions.py
PINNED_ARCHIVAL = (PC.P13_REFERENCE_FILE, PC.P13_INDEPENDENT_REPORT, PC.P13_FROZEN_LIST) + tuple(PC.P13_ARCHIV
  +> ED_RECORDS)
ARCHIVAL_PINS = {PC.P13_REFERENCE_FILE: PC.P13_REFERENCE_VALUES_SHA256, PC.P13_INDEPENDENT_REPORT: PC.P13_INDE
  +> PENDENT_REPORT_SHA256,
                 PC.P13_FROZEN_LIST: PC.P13_FROZEN_LIST_SHA256, **PC.P13_ARCHIVED_RECORDS,
                 "archival/p14r/reproducibility/independent_rebuild_report_p14r.json": Q15.P14R_INDEPENDENT_RE
  +> PORT_SHA256,
                 **Q15.P14R_ARCHIVED_RECORDS,
                 "archival/p15/reproducibility/independent_rebuild_report_p15.json": Q16.P15_INDEPENDENT_REPOR
  +> T_SHA256,
                 **Q16.P15_ARCHIVED_RECORDS, **Q17.P16_ARCHIVED_RECORDS, **Q18.P17_ARCHIVED_RECORDS,
                 **Q19.P18_ARCHIVED_RECORDS, **Q20.P19_ARCHIVED_RECORDS, **Q21.P20_ARCHIVED_RECORDS,
                 **Q22.P21_ARCHIVED_RECORDS, **QC.P22_ARCHIVED_RECORDS}
PINNED_ARCHIVAL = PINNED_ARCHIVAL + ("archival/p14r/reproducibility/independent_rebuild_report_p14r.json",
                                     *Q15.P14R_ARCHIVED_RECORDS,
                                     "archival/p15/reproducibility/independent_rebuild_report_p15.json",
                                     *Q16.P15_ARCHIVED_RECORDS, *Q17.P16_ARCHIVED_RECORDS, *Q18.P17_ARCHIVED_R
  +> ECORDS,
                                     *Q19.P18_ARCHIVED_RECORDS, *Q20.P19_ARCHIVED_RECORDS, *Q21.P20_ARCHIVED_R
  +> ECORDS,
                                     *Q22.P21_ARCHIVED_RECORDS, *QC.P22_ARCHIVED_RECORDS)
# run-specific keys (not mathematical content): the rebuild flags/records differ between the author tree (whic
  +> h holds
# the author's rebuild report) and any fresh copy.  Wall-clock 'seconds' are removed by certio.strip_volatile.
RUN_SPECIFIC = ("reproducibility", "author_rebuild_passed", "independent_rebuild_passed",
                "live_report_identical_to_archived",
                # p14 freeze records that depend on files which are (correctly) absent from a source-only copy
  +> :
                # the archived p13 zip and the reviewer's live p13 report in the author tree
                "live_report_present", "live_report_identical_to_archived", "archived_zip_sha256_ok",
                "list_equals_archived_zip")


def versions():
    import sympy, mpmath
    try:
        import pytest
        pv = pytest.__version__
    except Exception:  # noqa: BLE001
        pv = None

    def first(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
            return ((r.stdout or r.stderr).strip().splitlines() or [""])[0]
        except FileNotFoundError:
            return None
    return {"python": platform.python_version(), "sympy": sympy.__version__, "mpmath": mpmath.__version__,
            "pytest": pv, "pdftex": first(["pdflatex", "--version"]), "pdftotext": first(["pdftotext", "-v"]),
            "platform": platform.platform()}


# ---------------- reference values (identical code path for author and rebuild) ----------------
def jload(rel, root=ROOT):
    return json.loads((Path(root) / rel).read_text())


def reference_values(root=ROOT):
    root = Path(root)
    q = jload("certificates/P13_quartic_verified.json", root)
    m = jload("certificates/P13_master_kappa2.json", root)
    rs = jload("RELEASE_STATUS.json", root)
    tr = jload(f"certificates/{QC.CERT_PREFIX}_test_results.json", root)
    cl = rs["classical"]
    rec = lambda r: {k: r[k] for k in ("W_terms", "Q_terms", "Q_identically_zero", "s0_piece_alone_Q_terms")} 
  +>  # noqa: E731
    return {
        "source": {"tree_sha256_without_reference": SM.tree_sha_without_reference(root),
                   "n_source_files": len(SM.source_files(root))},
        "inherited_pins": {**{k: v["sha256"] for k, v in inherited.PINS.items()},
                           **{k: v["sha256"] for k, v in SM.inherited_data(root).items()},
                           "XVI-O_o70_source_tree": json.loads((root / SM.XVIO_TREE).read_text())["sha256"]},
        "exports": {**{f"ell{k}": {"file_sha256": SM.sha(root / "exports" / f"ell{k}_generating_polynomial.sre
  +> pr"),
                                   "polynomial_sha256": q[f"ell{k}_sha256"],
                                   "terms": q["terms_reproducibility"][str(k)]} for k in (2, 3, 4)},
                    "V4_grav.json": SM.sha(root / "exports" / "V4_grav.json"),
                    "ell4_conventions.json": SM.sha(root / "exports" / "ell4_conventions.json"),
                    "P14_vertex_tensors.json": SM.sha(root / "exports" / "P14_vertex_tensors.json"),
                    "P14_integrands": {f.name: SM.sha(f) for f in sorted((root / "exports" / "P14_integrands")
  +> .glob("*.json"))}},
        "certificate_content_sha256_ignoring_timings": {
            **{c: certio.file_content_sha(root / "certificates" / f"{c}.json", RUN_SPECIFIC) for c in CERTS},
            "RELEASE_STATUS": certio.file_content_sha(root / "RELEASE_STATUS.json", RUN_SPECIFIC),
            **{f"ledgers/{l_}": certio.file_content_sha(root / "ledgers" / f"{l_}.json", RUN_SPECIFIC) for l_ 
  +> in LEDGERS}},
        "residual_records": {
            "quartic_C7": {o: rec(q["controls"]["C7_noether_exact"][o]) for o in certio.ORDERS},
            "master_grav_af0": {o: rec(m["details"]["grav_af0_deterministic"][o]) for o in certio.ORDERS},
            "master_table": m["table_by_kappa_and_antifield_number"],
            "required_master_residuals": m["required_master_residuals"]},
        "p23": {k: rs[k] for k in ("O1", "power_counting", "P6_entry", "EV_values", "title_qualifier", "contra
  +> ct",
                                   "independent_rebuild_passed_p22", "O1_requirement_recorded",
                                   "one_loop_power_counting_verified", "P6_entry_inventory",
                                   "d_poly_domain_refusal_verified", "EV_values_verified")}
        | {"d_poly_domain_refusal": {k: rs["d_poly_domain_refusal"][k] for k in ("ok", "n_plants", "not_raised
  +> ",
                                                                                 "algebra_ok")},
           "change_log_vs_p22": {k: rs["change_log_vs_p22"][k] for k in ("added", "modified", "removed",
                                                                          "undisclosed_changes")}},
        "p22": {k: rs[k] for k in ("evanescent_M2_verified", "evanescent_counterterms_verified",
                                   "d_runtime_guard_verified", "evanescent", "P5_calculation_status",
                                   "D11_matching_verified_scope", "evanescent_hh_counterterm_added", "contract
  +> ",
                                   "p21_layer", "manuscript_disclosure", "open_pins", "independent_rebuild_pas
  +> sed_p21")}
        | {"lower_layers": {k: v for k, v in rs["lower_layers"].items() if k != "contract_detail"},
           "d_runtime_guard": {k: rs["d_runtime_guard"][k] for k in ("ok", "n_plants", "not_raised", "algebra_
  +> ok",
                                                                    "entry_points")},
           "change_log_vs_p21": {k: rs["change_log_vs_p21"][k] for k in ("added", "modified", "removed",
                                                                          "undisclosed_changes")}},
        "p21": {"D11_absolute_pin_verified": rs["D11_absolute_pin_verified"],
                "absolute_pin": rs["p21_layer_absolute_pin"],
                "lower_layers": {k: v for k, v in rs["p21_layer_lower_layers"].items() if k != "contract_detai
  +> l"},
                "p20_layer": rs["p21_layer_p20_layer"], "manuscript_disclosure": rs["p21_layer_manuscript_disc
  +> losure"],
                "open_pins": rs["p21_layer_open_pins"],
                # recomputed by the p21 gate on the CURRENT tree (not the p21 release log)
                "p21_gate_change_log_vs_p20_recomputed_on_current_tree": {
                    k: rs["p21_layer_change_log_vs_p20"][k] for k in ("added", "modified", "removed",
                                                                      "undisclosed_package_changes")},
                "independent_rebuild_passed_p20": rs["p21_layer_independent_rebuild_passed_p20"]},
        "p20": {"D11_ratio_pin_verified": rs["D11_ratio_pin_verified"], "D11_pin": rs["p20_layer_D11_pin"],
                "K1_correction": rs["p20_layer_K1_correction"], "retraction_check": rs["p20_layer_retraction_c
  +> heck"],
                "open_pins_p20_layer": rs["p20_layer_open_pins"],
                "full_closure_mutation_detector": rs["full_closure_mutation_detector"],
                # p20 reviewer: this log is RECOMPUTED by the p20 gate on the CURRENT tree (not the p20 releas
  +> e log)
                "p20_gate_change_log_vs_p19_recomputed_on_current_tree": {
                    k: rs["p20_layer_change_log_vs_p19"][k] for k in ("added", "modified", "removed")},
                "independent_rebuild_passed_p19": rs["p20_layer_independent_rebuild_passed_p19"]},
        "p19": {"projected_defect_computed": rs["projected_defect_computed"],
                "projected_identity_verified": rs["projected_identity_verified"],
                "projected_restoration_verified": rs["projected_restoration_verified"],
                "bulk_symmetry_restored": rs["bulk_symmetry_restored"],
                "counterterm_solve_outcome": rs["counterterm_solve"]["outcome"],
                "projected_defect_summary": rs["projected_defect_summary"],
                # p20 reviewer: renamed (was /p19/change_log_vs_p18, recomputed on the current tree); the p19
                # release log as released is frozen in archival/p19/reference_values_p19.json (pinned)
                "p19_gate_change_log_vs_p18_recomputed_on_current_tree": {
                    k: rs["p19_gate_change_log_vs_p18_recomputed_on_current_tree"][k] for k in ("added", "modi
  +> fied", "removed")},
                "change_log_vs_p18_as_released_p19": "archival/p19/reference_values_p19.json (sha256 pinned)",
                "independent_rebuild_passed_p18": rs["independent_rebuild_passed_p18"]},
        "p18": {"graphs": rs["graphs"], "D12_status": rs["D12_status"], "batchA_evaluated": rs["batchA_evaluat
  +> ed"],
                "D13_evaluated": rs["D13_evaluated"], "batchC_evaluated": rs["batchC_evaluated"],
                "E2_status": rs["E2_status"], "E2_decoupling_proven": rs["E2_decoupling_proven"],
                "D11_evaluated": rs["D11_evaluated"], "library_certified": rs["library_certified"],
                "contract_changed_files": rs["contract_identity"]["changed_vs_p14r"],
                "contract_files_added": rs["contract_identity"]["added"],
                "hh_evanescent_status": rs["hh_evanescent_status"],
                "hh_evanescent_decoupling_proven": rs["hh_evanescent_decoupling_proven"],
                "evanescent_hh_counterterm_added": rs["evanescent_hh_counterterm_added"],
                "D11_matching_verified": rs["D11_matching_verified"],
                "quantum_inputs_evaluated": rs["quantum_inputs_evaluated"],
                "hh_full_row_decoupling_proven": rs["hh_full_row_decoupling_proven"],
                "independent_rebuild_passed_p14r": rs["independent_rebuild_passed_p14r"],
                "independent_rebuild_passed_p15": rs["independent_rebuild_passed_p15"],
                "independent_rebuild_passed_p16": rs["independent_rebuild_passed_p16"],
                "independent_rebuild_passed_p17": rs["independent_rebuild_passed_p17"]},
        "release": {"release_claim_accepted": rs["release_claim_accepted"], "publication": rs["publication"],
                    "classical_readiness_for_ch_identity": cl["classical_readiness_for_ch_identity"],
                    "flags": cl["flags"], "milestones": rs["milestones"]["status"], "hard_stops": rs["hard_sto
  +> ps"],
                    "P5_entry_flags": rs["P5_entry_flags"], "P5_entry_earned": rs["P5_entry_earned"],
                    "P3_P4_frozen_as_P5_inputs": rs["P3_P4_frozen_as_P5_inputs"],
                    "D11_matching_verified": rs["D11_matching_verified"], "D12_status": rs["D12_status"]},
        "tests": tr.get("groups", {}),
    }


def flatten(d, p=""):
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            out.update(flatten(v, f"{p}/{k}"))
        return out
    return {p: d}


def compare(ref, cur):
    a, b = flatten(ref), flatten(cur)
    diffs = [{"key": k, "reference": a.get(k, "<absent>"), "rebuild": b.get(k, "<absent>")}
             for k in sorted(set(a) | set(b)) if a.get(k, "<absent>") != b.get(k, "<absent>")]
    return {"compared": len(set(a) | set(b)), "equal": len(set(a) | set(b)) - len(diffs), "differences": diffs
  +> }


# ---------------- trace analysis ----------------
SYSTEM_PREFIXES = ("/usr/", "/lib", "/etc/", "/proc/", "/dev/", "/sys/", "/opt/", "/var/lib/", "/run/")


def analyse_trace(source_before):
    if not TRACE.exists():
        return {"present": False, "unpinned_external_reads": ["<no trace>"]}
    reads, writes = set(), set()
    for ln in TRACE.read_text(errors="replace").splitlines():
        if len(ln) < 3:
            continue
        (writes if ln[0] == "W" else reads).add(ln[2:])
    root = str(ROOT) + "/"
    tmp = tempfile.gettempdir().rstrip("/") + "/"
    site = tuple(sorted({str(Path(p).resolve()) + "/" for p in sys.path if p and ("site-packages" in p or "dis
  +> t-packages" in p)}))
    pinned_ws = {v["workspace"] for v in inherited.PINS.values()}
    ext_pinned, ext_other, in_tree_inputs, unknown = set(), set(), set(), set()
    home = str(Path.home()) + "/"
    for r in reads:
        if r.startswith(root):
            rel = r[len(root):]
            if rel in source_before:
                in_tree_inputs.add(rel)
            elif r not in writes and not (ROOT / rel).exists() and "__pycache__" not in rel:
                unknown.add(rel)
            continue
        if r in pinned_ws:
            ext_pinned.add(r)
        elif r.startswith(SYSTEM_PREFIXES) or r.startswith(site) or "__pycache__" in r or r.endswith((".pyc",)
  +> ):
            continue
        elif r == tmp.rstrip("/") or r.startswith(tmp):
            continue                          # TemporaryDirectory / tempfile / pytest / this entrypoint's own
  +>  scratch
        elif r.startswith(home + ".") or r in ("/", ".") or r.startswith(str(TRACE)):
            continue
        elif "/" not in r and not Path(r).is_absolute():
            continue                          # relative basename from Path("subdir").exists() / mkdir (not a 
  +> file read)
        else:
            ext_other.add(r)
    data_inputs = sorted(x for x in in_tree_inputs if not x.endswith((".py", ".tex", ".md")))
    pins = SM.inherited_data(ROOT)
    unpinned_data = [x for x in data_inputs if x not in pins and not x.startswith("provenance/")
                     and x not in (SM.REFERENCE_FILE, SM.PINS_FILE) and x not in PINNED_ARCHIVAL]
    return {"present": True, "reads": len(reads), "writes": len(writes),
            "external_reads_pinned": sorted(ext_pinned), "unpinned_external_reads": sorted(ext_other),
            "in_tree_source_files_read": len(in_tree_inputs), "in_tree_data_inputs_read": data_inputs,
            "unpinned_in_tree_data_inputs": unpinned_data, "reads_of_unknown_files": sorted(unknown)[:50]}


# ---------------- main ----------------
def write_reference():
    rs = jload("RELEASE_STATUS.json")
    assert rs["release_claim_accepted"] and rs["publication"] == "accepted", "build the release first"
    ref = {"landmark": "XVI-P", "revision": QC.REVISION, "kind": "author reference values for the p21 rebuild 
  +> contract",
           "generated_from": "the author's full build of this source tree (tools/build.py)",
           "environment": versions(), "values": reference_values(ROOT)}
    (ROOT / SM.REFERENCE_FILE).write_text(json.dumps(ref, indent=1) + "\n")
    print(json.dumps({"written": SM.REFERENCE_FILE, "tree_sha256_without_reference":
                      ref["values"]["source"]["tree_sha256_without_reference"]}))
    return 0


def main():
    a = sys.argv[1:]
    if "--write-reference" in a:
        return write_reference()
    mode = a[a.index("--inherited") + 1] if "--inherited" in a else "auto"
    report_path = Path(a[a.index("--report") + 1]) if "--report" in a else ROOT / "build" / "rebuild_report.js
  +> on"
    t0 = time.time()
    steps, rep = {}, {"landmark": "XVI-P", "revision": QC.REVISION, "entrypoint": "tools/rebuild_from_source.p
  +> y",
                      "inherited_mode": mode, "kind": "package evidence (XVI-O conv:package); not a certificat
  +> e"}
    env = versions()
    ref = jload(SM.REFERENCE_FILE)
    rep["environment"] = env
    rep["environment_reference"] = ref.get("environment")
    rep["environment_matches_reference"] = {k: env.get(k) == ref.get("environment", {}).get(k)
                                            for k in ("python", "sympy", "mpmath", "pytest", "pdftex", "pdftot
  +> ext")}
    # 2. source only
    extra = SM.non_source_files(ROOT)
    steps["source_only_tree"] = {"ok": not extra, "non_source_files": extra[:40], "count": len(extra)}
    source_before = set(SM.source_files(ROOT))
    rep["source_tree_sha256"] = SM.tree_sha(ROOT)
    rep["source_tree_sha256_without_reference"] = SM.tree_sha_without_reference(ROOT)
    rep["n_source_files"] = len(source_before)
    with tempfile.TemporaryDirectory(prefix="p23src_") as td:
        z = SM.make_zip(Path(td) / SM.ZIP_NAME, ROOT)
    rep["source_zip_sha256"] = z["sha256"]
    if extra:
        rep.update({"pass": False, "steps": steps, "stopped": "tree is not source-only (generated artifacts or
  +>  caches present)"})
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(rep, indent=1) + "\n")
        print(json.dumps({"pass": False, "reason": rep["stopped"], "examples": extra[:10]}))
        return 1
    # 3. pins
    os.environ["XVIP_INHERITED"] = mode
    pins = inherited.verify_all(mode)
    data = SM.check_inherited_data(ROOT)
    xvio = SM.check_xvio_provenance(ROOT)
    arch = {p: (ROOT / p).is_file() and SM.sha(ROOT / p) == h for p, h in ARCHIVAL_PINS.items()}
    steps["inherited_pins"] = {"ok": all(v["ok"] and v["vendored_copy_matches_pin"] for v in pins.values())
                               and all(v["ok"] for v in data.values()) and all(v["ok"] for v in xvio.values())
                               and all(arch.values())
                               and C.XVI_M_PIN == XVI_M_PIN
                               and inherited.PINS["XVI-M.tex"]["sha256"] == XVI_M_PIN,
                               "external": pins, "inherited_data_files": len(data),
                               "inherited_data_failures": [k for k, v in data.items() if not v["ok"]],
                               "xvi_o_o70_files_verified": len(xvio),
                               "xvi_o_o70_failures": [k for k, v in xvio.items() if not v["ok"]],
                               "XVI_M_pin": XVI_M_PIN}
    # 4. full build (fresh, traced, sync inside the copy)
    (ROOT / "build").mkdir(exist_ok=True)
    TRACE.unlink(missing_ok=True)
    benv = dict(os.environ, P14_SYNC_DIR=str(SYNC), XVIP_INHERITED=mode, P13_MUTATIONS="", P14_MUTATIONS="",
                XVIP_TRACE_LOG=str(TRACE),
                PYTHONPATH=os.pathsep.join([str(ROOT / "tools" / "read_trace")] +
                                           ([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else []
  +> )))
    tb = time.time()
    with open(ROOT / "build" / "rebuild_build.log", "w") as lf:
        r = subprocess.run([PY, "tools/build.py"], cwd=str(ROOT), env=benv, stdout=lf, stderr=subprocess.STDOU
  +> T,
                           timeout=4 * 3600)
    steps["full_build"] = {"ok": r.returncode == 0, "rc": r.returncode, "seconds": round(time.time() - tb, 1),
                           "log": "build/rebuild_build.log"}
    if r.returncode == 0:
        import build as B                       # noqa: E402  (tools/build.py; import has no side effects)
        from manifest import verify             # noqa: E402
        rs = jload("RELEASE_STATUS.json")
        steps["release_accepted"] = {"ok": rs["release_claim_accepted"] is True and rs["publication"] == "acce
  +> pted"
                                     and rs["classical"]["classical_readiness_for_ch_identity"] is True
                                     and rs["P5_entry_earned"] is True and rs["P3_P4_frozen_as_P5_inputs"] is 
  +> True
                                     and rs.get("revision") == QC.REVISION and rs.get("batchA_evaluated") is T
  +> rue
                                     and rs.get("D13_evaluated") is True and rs.get("batchC_evaluated") is Tru
  +> e
                                     and rs.get("E2_decoupling_proven") is True and rs.get("D11_evaluated") is
  +>  True
                                     # p18 (disclosed): D11 is earned in p18; the p17 criterion "D11_evaluated
  +>  is False" was stale
                                     and rs.get("D11_matching_verified") is True
                                     # p22 (disclosed): the scope is widened by EV-M2 (evanescent components)
                                     and str(rs.get("D11_matching_verified_scope", "")).startswith(
                                         "4D components: M2 discharged")
                                     and rs.get("quantum_inputs_evaluated") == "earned"
                                     and rs.get("hh_full_row_decoupling_proven") is True
                                     and rs.get("hard_stops_hold") is True
                                     # p19: the projected-defect flags (P19 gate) and the bulk hard stop
                                     and rs.get("projected_defect_computed") == "earned"
                                     and rs.get("projected_identity_verified") == "earned"
                                     and rs.get("projected_restoration_verified") == "earned"
                                     and rs.get("bulk_symmetry_restored") is False
                                     # p20: the corrected restoration (full closure), D11 ratio pin, no retrac
  +> ted text
                                     and rs.get("D11_ratio_pin_verified") == "earned"
                                     and rs.get("p20_layer_K1_correction", {}).get("full_closure_complete_S_ct
  +> ") is True
                                     and rs.get("p20_layer_retraction_check", {}).get("hits") == {}
                                     # p21: absolute pin, lower layers re-checked live, every package change d
  +> isclosed
                                     and rs.get("D11_absolute_pin_verified") == "earned"
                                     and rs.get("lower_layers", {}).get("rechecked_live") is True
                                     # p22: evanescent M2 + counterterms, runtime guard, no undisclosed change
                                     and all(rs.get(k) == "earned" for k in Q22.EARNABLE_P22)
                                     and rs.get("P5_calculation_status") == Q22.P5_STATUS_P22
                                     # p23: O.1 scope / power counting / P.6 entry / poly refusal / EV values
                                     and all(rs.get(k) == "earned" for k in QC.EARNABLE_P23)
                                     and rs.get("O1_closure") == "NOT_CLOSED"
                                     and rs.get("change_log_vs_p22", {}).get("undisclosed_changes") == [],
                                     "milestones": rs["milestones"]["status"], "P5_entry_flags": rs["P5_entry_
  +> flags"]}
        groups = B.junit_groups()
        steps["tests"] = {"ok": set(groups) == {"baseline", "certificate_mutation", "resumed_build"} and
                          all(g["passed"] > 0 and g["failed"] == 0 and g["skipped"] == 0 for g in groups.value
  +> s()),
                          "groups": groups, "summary": (ROOT / "build" / "p14" / "pytest_summary.txt").read_te
  +> xt().strip()}
        rb = B.readback_compare(ROOT)
        steps["pdf_readback_vs_records"] = {"ok": rb["pass"], "records": rb["expected_records"],
                                            "appendix": rb["XVI-P-appendix"]["pass"], "combined": rb["XVI-P"][
  +> "pass"],
                                            "value_blocks": {st: {r: x["pass"] for r, x in rb[st]["value_block
  +> s"].items()}
                                                             for st in ("XVI-P-appendix", "XVI-P")},
                                            "footer": {st: rb[st]["footer"] for st in ("XVI-P-appendix", "XVI-
  +> P")}}
        v = verify(ROOT / "RELEASE_MANIFEST_EXTERNAL.txt", ROOT)
        synced = {f.name: SM.sha(f) for f in sorted(SYNC.glob("*"))} if SYNC.exists() else {}
        steps["external_manifest"] = {"ok": v["pass"] and len(synced) == 6, "entries": v["entries"],
                                      "failures": v["failures"], "synced_inside_copy": sorted(synced)}
        zp = ROOT / "dist" / SM.ZIP_NAME
        zbad = SM.zip_matches_tree(zp, ROOT)
        steps["source_only_zip_rebuilt"] = {"ok": not zbad and SM.sha(zp) == rep["source_zip_sha256"],
                                            "differences": zbad[:20]}
        tr = analyse_trace(source_before)
        steps["file_access_trace"] = {"ok": tr["present"] and not tr["unpinned_external_reads"]
                                      and not tr["unpinned_in_tree_data_inputs"], **tr}
        cur = reference_values(ROOT)
        cmp_ = compare(ref["values"], cur)
        steps["comparison_with_reference"] = {"ok": not cmp_["differences"], **cmp_}
        rep["rebuilt_values"] = cur
    rep["steps"] = steps
    rep["pass"] = all(s.get("ok") for s in steps.values()) and "comparison_with_reference" in steps
    rep["seconds"] = round(time.time() - t0, 1)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({"pass": rep["pass"], "steps": {k: v.get("ok") for k, v in steps.items()},
                      "report": str(report_path), "source_tree_sha256": rep["source_tree_sha256"],
                      "source_zip_sha256": rep["source_zip_sha256"]}, indent=1))
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
