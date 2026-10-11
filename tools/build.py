#!/usr/bin/env python3
"""XVI-P p23 single active release (p23 = stage release on the O.1 direction: O.1 requirement, one-loop power
counting, P.6 entry inventory, poly-domain refusal; previously p22 (p22 = bigger fronts after p21, WITH a disclosed contract revision: EV-M2 (evanescent
matching statement), EV-CT (evanescent counterterms, sigma_0-closed, identity unchanged; P.5 status renormalized),
runtime d guard in code/p5_entry/dred.py (additive block, contract_registry), gate without prefix exemptions; stage
p22calc runs code/p5_calc/evanescent.py; after the p21 gate release_p21.py (now a LAYER gate writing
certificates/P21_release.json) the p22 gate code/p5_calc/release_p22.py runs).
Previous header (p21 = small release from p20: absolute D11 pin derived from 1/2 Tr ln under the
declared conventions; gate checks top-level pin status and re-checks lower layers; allow-list d-evaluation scan +
runtime opaque-d check; P19 note edit disclosed; no scope expansion; no contract revision; after the p20 gate
release_p20.py (now a LAYER gate writing certificates/P20_release.json; d11_pin.py and release_p20.py are disclosed
p21 revisions) the p21 gate code/p5_calc/release_p21.py runs).
Previous header (p20 = CORRECTION of p19 -- K1 orientation erratum, restoration redefined as full
sigma_0 closure of the one-loop kappa^2 MS-bar counterterm, full-closure mutation detector, D11 ratio pin, J1 wording,
scan patterns; no scope expansion; no contract revision), regenerated in dependency order (p20: after the p19 gate
(release_p19.py, now a LAYER gate writing certificates/P19_release.json; defect.py and release_p19.py are disclosed
p20 revisions), the D11 pin code/p5_calc/d11_pin.py and the p20 release gate code/p5_calc/release_p20.py, which
requires the p19 layer accepted, the K1 correction content, the retraction check, the D11 ratio pin, the pinned p19
independent record and the p20 hard stops; p19: defect.py + release_p19.py; p18: d11.py + release_p18.py; p17, p16,
p15 as before):

conventions -> boundary identity (C3) -> quartic (deterministic C1-C7) -> classical transformations / source action
-> gauge map -> ch audit -> graphs -> master verification  [the FROZEN p13 classical P.3/P.4 code, unchanged]
-> matter-loop gates (regenerate the inherited O5 records) -> P.5 entry contract (amplitude rules, counterterm
domain, quantum object, prescription + D11 matching; NO loop evaluation) -> contract gate code/p5_entry/release_p14.py
(classical acceptance AND p13 freeze AND all five P.5-entry flags AND contract hard stops) -> dossier (every link
resolved) -> p15 calculation (code/p5_calc: integral library, Batch A, D13) -> p15 release gate
code/p5_calc/release_p15.py (contract accepted AND contract byte-identity except the disclosed dred.py correction AND
library AND batchA_evaluated AND D13_evaluated AND p15 hard stops) -> p16 calculation (code/p5_calc: E2 evanescent
decoupling proof, Batch C D01/D03 via the covariant route) -> p16 release gate code/p5_calc/release_p16.py (p14r and
p15 gates accepted AND contract identity: only dred.py changed vs p14r (disclosed p15 F1 + p16 F3), no new contract
file AND p15 calc files byte-identical AND E2 proof AND batchC_evaluated AND p16 hard stops; a rejected release exits
nonzero and STOPS the build before any PDF/zip/sync) -> tests (baseline, certificate and
gate mutations, resumed builds; junit) -> PDFs (science, appendix, combined) + readback -> zips (review-focus, full,
SOURCE-ONLY XVI-P-p23-source-only.zip) -> external manifest LAST (PDFs never contain PDF hashes) -> sync to
$P14_SYNC_DIR (default /workspace; earlier source-only zips in /workspace are never written).

PUBLICATION GATE (since p12): before ANY pdf, zip or manifest/sync stage (also when resuming with --from-stage) the
contract gate release_p14.py, the dossier dossier_p14.py, the p15 gate release_p15.py, the p16 gate
release_p16.py, the p17 gate release_p17.py, the p18 gate release_p18.py, the p19 gate release_p19.py, the p20 gate release_p20.py, the p21 gate release_p21.py AND the p22 gate release_p22.py are re-invoked and the current
artifacts are checked (export hashes, residual-record invariants, cross-certificate agreement, dossier links,
listings == executed/written files, zips == current files, source-only zip == current source set).  If anything
fails, existing PDFs/zips/manifest are moved to stale/ with a REJECTED marker, PUBLICATION_REJECTED.txt is written,
nothing is synced, and the build exits nonzero.

p13/p14: the source set and the source-only zip are defined in tools/source_manifest.py; the clean-copy rebuild
contract is tools/rebuild_from_source.py (REBUILD_INSTRUCTIONS.md).  Generated-file cleaning NEVER touches the
p13 records reproducibility/reference_values.json, reproducibility/independent_rebuild_report.json,
reproducibility/author_rebuild_report.json or anything under archival/.

Usage: python3 tools/build.py [--from-cache] [--skip-tests] [--from-stage NAME]
"""
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys, time, unicodedata, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
MS = ROOT / "manuscript"
LST = MS / "listing_src"
DIST = ROOT / "dist"
TOP = Path(os.environ.get("P14_SYNC_DIR", "/workspace"))
STALE = ROOT / "stale"
PDF_STEMS = ("XVI-P-science", "XVI-P-appendix", "XVI-P")
SRC_ZIP = "XVI-P-p23-source-only.zip"
ZIPS = ("XVI-P-review-focus.zip", "XVI-P-full.zip", SRC_ZIP)
sys.path.insert(0, str(ROOT / "code" / "classical"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "code" / "p5_entry"))
import conventions as C  # noqa: E402   (frozen p13 classical conventions: pins only)
import p14_conventions as PC  # noqa: E402   (p14r CONTRACT constants: hard stops, flags, p13 pins)
sys.path.insert(0, str(ROOT / "code" / "p5_calc"))
import p15_conventions as Q15  # noqa: E402   (p15 layer constants: hard stops of the p15 gate)
import p23_conventions as QC  # noqa: E402   (revision/date/version label of THIS release)
import p22_conventions as Q22  # noqa: E402   (p22 layer)
import p21_conventions as Q21  # noqa: E402   (p21 layer: hard stops)
import p20_conventions as Q20  # noqa: E402   (p20 layer: hard stops)
import p19_conventions as Q19  # noqa: E402   (p19 layer: hard stops)
import p18_conventions as Q18  # noqa: E402   (p18 layer: hard stops)
import p17_conventions as Q17  # noqa: E402   (p17 layer: hard stops)
import p16_conventions as Q16  # noqa: E402   (p16 layer: hard stops)
import certio  # noqa: E402
import inherited  # noqa: E402
import source_manifest as SM  # noqa: E402
from manifest import file_line, verify, pdf_pages, sha  # noqa: E402

LOG = []


def step(name, cmd, timeout=3600):
    t0 = time.time()
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
    LOG.append({"stage": name, "cmd": " ".join(map(str, cmd)), "rc": r.returncode, "sec": round(time.time() - t0, 1)})
    print(f"[{name}] rc={r.returncode} {LOG[-1]['sec']}s", flush=True)
    if r.returncode != 0:
        print(r.stdout[-4000:], r.stderr[-4000:])
        raise SystemExit(f"stage {name} failed")
    return r


# ---------------- listings (ASCII-sanitised copies of CURRENT sources) ----------------
GREEK = {"α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "eps", "ζ": "zeta", "κ": "kappa", "λ": "lambda",
         "μ": "mu", "ν": "nu", "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau", "φ": "phi", "ξ": "xi", "ψ": "psi",
         "Ψ": "Psi", "Φ": "Phi", "Γ": "Gamma", "Π": "Pi", "∂": "d", "≤": "<=", "≥": ">=", "≠": "!=", "→": "->",
         "⇒": "=>", "∧": "AND", "∫": "int", "√": "sqrt", "²": "^2", "⁴": "^4", "₁": "_1", "≅": "~=", "∼": "~",
         "×": "x", "·": ".", "—": "--", "–": "-", "’": "'", "“": '"', "”": '"', "…": "...", "⟨": "<", "⟩": ">",
         "ℓ": "ell", "ℏ": "hbar", "□": "Box", "≡": "==", "∈": "in", "⊂": "subset", "∑": "sum"}


def ascii_clean(s: str) -> str:
    out = []
    for ch in s:
        if ord(ch) < 128:
            out.append(ch)
        elif ch in GREEK:
            out.append(GREEK[ch])
        else:
            out.append("<" + unicodedata.name(ch, "U+%04X" % ord(ch)).lower().replace(" ", "_") + ">")
    return "".join(out)


LISTINGS = [
    ("Release status / acceptance certificate (p23)", "certificates/P23_release.json"),
    ("Milestone ledger (p23)", "ledgers/P23_milestones.json"),
    ("Test results (p23)", "certificates/P23_test_results.json"),
    ("O.1 requirement, one-loop power counting, P.6 entry inventory (p23)", "certificates/P23_O1_scope.json"),
    ("p22 layer record (release gate p22, revised in p23)", "certificates/P22_release.json"),
    ("Evanescent components: EV-M2 statement and evanescent counterterms (p22)", "certificates/P22_evanescent.json"),
    ("p21 layer record (release gate p21, revised in p22)", "certificates/P21_release.json"),
    ("D11 pin: ratio (p20) and absolute sign and magnitude (derived in p21)", "certificates/P20_D11_pin.json"),
    ("p20 layer record (release gate p20, revised in p21)", "certificates/P20_release.json"),
    ("P.5 identity: projected ch-identity defect, counterterm solve, full closure (p19 layer, corrected in p20)", "certificates/P19_defect.json"),
    ("p19 layer record (release gate p19, revised in p20)", "certificates/P19_release.json"),
    ("Milestone ledger (p19 layer)", "ledgers/P19_milestones.json"),
    ("p18 layer record (release gate p18)", "certificates/P18_release.json"),
    ("Milestone ledger (p18 layer)", "ledgers/P18_milestones.json"),
    ("P.5 calculation: D11 matching premise M2 (discharge; p18)", "certificates/P18_D11_M2.json"),
    ("P.5 calculation: D11 evaluated under the declared prescription (p18)", "certificates/P18_D11.json"),
    ("P.5 calculation: full hh slot D01+D02+D03+D11+D12 vs the ch projection (p18)", "certificates/P18_hh_slot.json"),
    ("p17 layer record (release gate p17)", "certificates/P17_release.json"),
    ("Milestone ledger (p17 layer)", "ledgers/P17_milestones.json"),
    ("P.5 calculation: D01/D03 evanescent poles vs the ch-projected slot (decoupling proof; p17)", "certificates/P17_hh_slot.json"),
    ("p16 layer record (release gate p16)", "certificates/P16_release.json"),
    ("Milestone ledger (p16 layer)", "ledgers/P16_milestones.json"),
    ("P.5 calculation: E2 evanescent decoupling proof (D13; p16)", "certificates/P16_E2_evanescent.json"),
    ("P.5 calculation: Batch C certificate (D01, D03; p16)", "certificates/P16_batchC.json"),
    ("p15 layer release record (Batch A, D13; p15 gate)", "certificates/P15_release.json"),
    ("Milestone ledger (p15)", "ledgers/P15_milestones.json"),
    ("P.5 calculation: integral library certificate (p15)", "certificates/P15_integral_library.json"),
    ("P.5 calculation: Batch A certificate (D02, D12, D14a-c; p15)", "certificates/P15_batchA.json"),
    ("P.5 calculation: Batch B certificate (D13; p15)", "certificates/P15_D13.json"),
    ("p14r contract record (P.5 entry; contract gate)", "certificates/P14_release.json"),
    ("Closure release artifact of the p14r contract", "certificates/P14_closure_release.json"),
    ("P.5 entry dossier (machine-readable)", "certificates/P14_dossier.json"),
    ("Milestone ledger (p14)", "ledgers/P14_milestones.json"),
    ("P.5 entry: quantum object certificate", "certificates/P14_quantum_object.json"),
    ("P.5 entry: prescription and D11 matching certificate", "certificates/P14_prescription_D11_matching.json"),
    ("P.5 entry: counterterm domain certificate", "certificates/P14_counterterm_domain.json"),
    ("P.5 entry: amplitude rules certificate", "certificates/P14_amplitude_rules.json"),
    ("P.5 entry: operational DRED rules certificate (p14r rules; p15 R5 correction; p16 F3 hardening)", "certificates/P14_dred_rules.json"),
    ("Symbolic integrand D01 (p14r export; evaluated in p16)", "exports/P14_integrands/D01.json"),
    ("Symbolic integrand D03 (p14r export; evaluated in p16)", "exports/P14_integrands/D03.json"),
    ("Symbolic integrand D13 (p14r export; evaluated in p15)", "exports/P14_integrands/D13.json"),
    ("Symbolic integrand D14a (p14r export; evaluated in p15)", "exports/P14_integrands/D14a.json"),
    ("Symbolic integrand D14b (p14r export; evaluated in p15)", "exports/P14_integrands/D14b.json"),
    ("Symbolic integrand D14c (p14r export; evaluated in p15)", "exports/P14_integrands/D14c.json"),
    ("Symbolic integrand D02 (p14r export; evaluated in p15)", "exports/P14_integrands/D02.json"),
    ("Symbolic integrand D12 (p14r export; evaluated in p15)", "exports/P14_integrands/D12.json"),
    ("Boundary identity certificate (C3)", "certificates/P13_boundary_identity.json"),
    ("Quartic verification certificate", "certificates/P13_quartic_verified.json"),
    ("BRST derivation certificate", "certificates/P13_brst_derivation.json"),
    ("Source action certificate", "certificates/P13_source_action.json"),
    ("Gauge-fixing map certificate", "certificates/P13_gauge_fixing_map.json"),
    ("Master equation certificate", "certificates/P13_master_kappa2.json"),
    ("ch source audit certificate", "certificates/P13_ch_source_audit.json"),
    ("ch dependency rows ledger", "ledgers/P13_ch_dependency_rows.json"),
    ("Generated graph inventory", "ledgers/P13_graph_inventory.json"),
    ("V4\\_grav export", "exports/V4_grav.json"),
    ("ell4 conventions export", "exports/ell4_conventions.json"),
    ("Source: conventions.py", "code/classical/conventions.py"),
    ("Source: boundary\\_identity.py (C3)", "code/classical/boundary_identity.py"),
    ("Source: jetpoly.py", "code/classical/jetpoly.py"),
    ("Source: certio.py (certificate serialization + invariants)", "code/classical/certio.py"),
    ("Source: grav\\_noether.py", "code/classical/grav_noether.py"),
    ("Source: graded\\_jets.py", "code/classical/graded_jets.py"),
    ("Source: bv\\_model.py", "code/classical/bv_model.py"),
    ("Source: brst\\_from\\_geometry.py", "code/classical/brst_from_geometry.py"),
    ("Source: source\\_action.py", "code/classical/source_action.py"),
    ("Source: gauge\\_fixing\\_map.py", "code/classical/gauge_fixing_map.py"),
    ("Source: planewave\\_exact.py", "code/classical/planewave_exact.py"),
    ("Source: series\\_eval.py", "code/classical/series_eval.py"),
    ("Source: quartic.py", "code/classical/quartic.py"),
    ("Source: ell4\\_full\\_polynomial.py (builder library)", "code/classical/ell4_full_polynomial.py"),
    ("Source: inverse\\_metric\\_series.py", "code/classical/inverse_metric_series.py"),
    ("Source: master\\_kappa2.py", "code/classical/master_kappa2.py"),
    ("Source: ch\\_source\\_audit.py", "code/p4_classical/ch_source_audit.py"),
    ("Source: release.py (frozen p13 classical gate; forked verbatim by release\\_p14)", "code/classical/release.py"),
    ("Source: dossier.py (frozen p13 dossier library)", "code/classical/dossier.py"),
    ("Source: inherited.py (pinned inherited inputs)", "code/classical/inherited.py"),
    ("Source: tools/source\\_manifest.py (source set, source-only zip)", "tools/source_manifest.py"),
    ("Source: tools/rebuild\\_from\\_source.py (rebuild entrypoint)", "tools/rebuild_from_source.py"),
    ("REBUILD\\_INSTRUCTIONS.md", "REBUILD_INSTRUCTIONS.md"),
    ("Source: tools/build.py", "tools/build.py"),
    ("Source: tools/manifest.py", "tools/manifest.py"),
    ("Source: p14\\_conventions.py (P.5 entry contract constants)", "code/p5_entry/p14_conventions.py"),
    ("Source: freeze\\_p13.py (p13 freeze F1-F3)", "code/p5_entry/freeze_p13.py"),
    ("Source: amplitude\\_rules.py", "code/p5_entry/amplitude_rules.py"),
    ("Source: counterterm\\_domain.py", "code/p5_entry/counterterm_domain.py"),
    ("Source: quantum\\_object.py", "code/p5_entry/quantum_object.py"),
    ("Source: prescription\\_d11.py", "code/p5_entry/prescription_d11.py"),
    ("Source: dred.py (operational DRED rules, p14r; disclosed revisions: p15 structural R5 safeguard, p16 F3 hardening, p17 G2 guarded loader parse\\_d, p18 H3/H5 documentation only, p22 runtime d guard -- additive block)", "code/p5_entry/dred.py"),
    ("Source: hessian\\_route.py (W6 independent regeneration, p14r)", "code/p5_entry/hessian_route.py"),
    ("Source: release\\_p14.py (p14 release gate)", "code/p5_entry/release_p14.py"),
    ("Source: dossier\\_p14.py (P.5 entry dossier)", "code/p5_entry/dossier_p14.py"),
    ("Source: tests/test\\_p14.py", "tests/test_p14.py"),
    ("Source: p15\\_conventions.py (p15 constants, contract pins)", "code/p5_calc/p15_conventions.py"),
    ("Source: integrals.py (p15 integral library, S0)", "code/p5_calc/integrals.py"),
    ("Source: batchA.py (p15 Batch A)", "code/p5_calc/batchA.py"),
    ("Source: d13.py (p15 Batch B: D13)", "code/p5_calc/d13.py"),
    ("Source: release\\_p15.py (p15 release gate)", "code/p5_calc/release_p15.py"),
    ("Source: tests/test\\_p15.py", "tests/test_p15.py"),
    ("Source: p16\\_conventions.py (p16 constants, version label, pins)", "code/p5_calc/p16_conventions.py"),
    ("Source: covariant.py (p16 covariant route: exact covariant integrand, FP and PV loop routes)", "code/p5_calc/covariant.py"),
    ("Source: e2\\_evanescent.py (p16 E2 decoupling proof)", "code/p5_calc/e2_evanescent.py"),
    ("Source: batchC.py (p16 Batch C: D01, D03)", "code/p5_calc/batchC.py"),
    ("Source: release\\_p16.py (p16 release gate)", "code/p5_calc/release_p16.py"),
    ("Source: tests/test\\_p16.py", "tests/test_p16.py"),
    ("Source: p17\\_conventions.py (p17 constants, version label, pins, disclosures)", "code/p5_calc/p17_conventions.py"),
    ("Source: hh\\_slot.py (p17 D01/D03 evanescent poles vs the ch slot: proof, controls, mutations)", "code/p5_calc/hh_slot.py"),
    ("Source: release\\_p17.py (p17 release gate)", "code/p5_calc/release_p17.py"),
    ("Source: tests/test\\_p17.py", "tests/test_p17.py"),
    ("Source: p18\\_conventions.py (p18 constants, version label, pins, disclosures)", "code/p5_calc/p18_conventions.py"),
    ("Source: d11.py (p18 M2 discharge, D11 evaluation, full hh slot)", "code/p5_calc/d11.py"),
    ("Source: release\\_p18.py (p18 release gate)", "code/p5_calc/release_p18.py"),
    ("Source: tests/test\\_p18.py", "tests/test_p18.py"),
    ("Source: p19\\_conventions.py (p19 constants, version label, pins, disclosures)", "code/p5_calc/p19_conventions.py"),
    ("Source: defect.py (p19 layer, disclosed p20 revision: K1 orientation fix, full sigma-0 closure, restoration redefined)", "code/p5_calc/defect.py"),
    ("Source: release\\_p19.py (p19 layer gate, disclosed p20 revision)", "code/p5_calc/release_p19.py"),
    ("Source: tests/test\\_p19.py", "tests/test_p19.py"),
    ("Source: p20\\_conventions.py (p20 constants, version label, pins, disclosures)", "code/p5_calc/p20_conventions.py"),
    ("Source: d11\\_pin.py (p20 D11 pin; disclosed p21 revision: absolute pin derivation)", "code/p5_calc/d11_pin.py"),
    ("Source: release\\_p20.py (p20 layer gate, disclosed p21 revision)", "code/p5_calc/release_p20.py"),
    ("Source: tests/test\\_p20.py", "tests/test_p20.py"),
    ("Source: p21\\_conventions.py (p21 constants, version label, pins, disclosures, scan allow-list)", "code/p5_calc/p21_conventions.py"),
    ("Source: release\\_p21.py (p21 layer gate, disclosed p22 revision)", "code/p5_calc/release_p21.py"),
    ("Source: tests/test\\_p21.py", "tests/test_p21.py"),
    ("Source: p22\\_conventions.py (p22 constants, version label, disclosures, guard plants)", "code/p5_calc/p22_conventions.py"),
    ("Source: evanescent.py (p22 EV-M2 and evanescent counterterms)", "code/p5_calc/evanescent.py"),
    ("Source: contract\\_registry.py (p22 registry of the post-p18 contract revision)", "code/p5_calc/contract_registry.py"),
    ("Source: release\\_p22.py (p22 layer gate, disclosed p23 revision)", "code/p5_calc/release_p22.py"),
    ("Source: tests/test\\_p22.py", "tests/test_p22.py"),
    ("Source: p23\\_conventions.py (p23 constants, disclosures, pinned EV values, poly plants)", "code/p5_calc/p23_conventions.py"),
    ("Source: power\\_counting.py (p23 O.1 requirement, power counting, P.6 entry inventory)", "code/p5_calc/power_counting.py"),
    ("Source: release\\_p23.py (p23 release gate)", "code/p5_calc/release_p23.py"),
    ("Source: tests/test\\_p23.py", "tests/test_p23.py"),
]


WRAP = 110


def wrap_lines(txt: str) -> str:
    """Hard-wrap for verbatim listings; continuation lines are prefixed with '  +> ' (content unchanged)."""
    out = []
    for ln in txt.splitlines():
        while len(ln) > WRAP:
            out.append(ln[:WRAP])
            ln = "  +> " + ln[WRAP:]
        out.append(ln)
    return "\n".join(out) + "\n"


def make_listings():
    if LST.exists():
        shutil.rmtree(LST)
    LST.mkdir(parents=True)
    names = []
    for title, rel in LISTINGS:
        src = ROOT / rel
        dst = LST / (rel.replace("/", "__"))
        dst.write_text(wrap_lines(ascii_clean(src.read_text())))
        names.append((title, rel, dst.name))
    return names


def listing_marker(i, n):
    return f"[listing {i:02d}/{n:02d}]"


def appendix_body(names):
    arch_notes = sorted((ROOT / "archival" / "p02_p09" / "notes").glob("*.tex"))
    lines = [r"\section{Appendix overview}",
             "All listings below are generated by \\texttt{tools/build.py} from exactly the source files executed and the "
             "certificate files written in this build (ASCII-sanitised copies in \\texttt{manuscript/listing\\_src}; "
             "the build verifies byte-identity after typesetting and again before zipping). Lists of scalars are printed "
             "on one line, so a page break cannot split them; page numbers are printed as ``" + QC.VERSION_LABEL + " | page N'' (one version variable, "
             "\\texttt{p22\\_conventions.VERSION\\_LABEL}, written to \\texttt{manuscript/version.tex}). "
             "The external manifest (with PDF/zip hashes) is written after the PDFs and is deliberately not reproduced "
             "inside any PDF.", ""]
    for i, (title, rel, fn) in enumerate(names, 1):
        lines += [f"\\section{{{title}}}",
                  f"\\noindent\\texttt{{{listing_marker(i, len(names))} {rel.replace('_', chr(92) + '_')}}}",
                  f"{{\\scriptsize\\verbatiminput{{listing_src/{fn}}}}}", ""]
    lines += [r"\section{Archival material (p22): evanescent M2/CT and runtime d guard, superseded by p23}",
              r"\scopebox{Archival.}{The p22 release (\texttt{archival/p22/}) is superseded by p23. Its independent "
              r"rebuild PASSED (same box; report 023e5b83\ldots), bound to tree 1bc6edff\ldots{} and zip "
              r"ade2fa5c\ldots; p23 records this as independent\_rebuild\_passed\_p22 and does not inherit it. "
              r"Findings (polynomial-algebra bypass of the d guard; EV values unchecked by the gate; title-line "
              r"qualifier) are addressed in p23.}"]
    lines += [r"\section{Archival material (p21): small release, superseded by p22}",
              r"\scopebox{Archival.}{The p21 release (\texttt{archival/p21/}) is superseded by p22. Its independent "
              r"rebuild PASSED (same box, fresh directory and venv; NOT a second machine), bound to the p21 tree "
              r"b835353f\ldots{} and zip a71d6b52\ldots; p22 records this as independent\_rebuild\_passed\_p21 and "
              r"does not inherit it. Its findings (gate prefix exemptions; eight scan misses and the power-base "
              r"subs hole of the d guard; stale OPEN text in the p20 section) are addressed in p22.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p21_README.md}}",
              r"\section{Archival material (p20): correction of p19, superseded by p21}",
              r"\scopebox{Archival.}{The p20 release (\texttt{archival/p20/}) is superseded by p21. Its independent "
              r"rebuild PASSED (same box, fresh directory and venv; NOT a second machine), bound to the p20 tree "
              r"2c0aa153\ldots{} and zip ca32ce01\ldots; p21 records this as independent\_rebuild\_passed\_p20 and "
              r"does not inherit it. Its findings (absolute D11 pin derivable; top-level pin status unchecked; eight "
              r"scan misses; P19 note edit not listed; misleading change-log key) are addressed in p21.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p20_README.md}}",
              r"\section{Archival material (p19): P.5 identity step, superseded by the p20 correction}",
              r"\scopebox{Archival.}{The p19 release (\texttt{archival/p19/}) is superseded by the p20 correction "
              r"release. Its independent rebuild PASSED with findings (same box, fresh directory and venv; NOT a second "
              r"machine), bound to the p19 tree fcf90354\ldots{} and zip da924275\ldots; p20 records this as "
              r"independent\_rebuild\_passed\_p19 and does not inherit it. Finding K1 (the p19 claim that full closure "
              r"fails with the derived factor) was an orientation bookkeeping error and is retracted (erratum in the "
              r"p20 note); all findings are addressed in p20.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p19_README.md}}",
              r"\section{Archival material (p18): M2 discharged, D11 evaluated, full hh slot, superseded by p19}",
              r"\scopebox{Archival.}{The p18 release (\texttt{archival/p18/}) is superseded as a release by p19; its "
              r"calculation code (d11, release\_p18) stays byte-identical and active as the p18 layer. Its "
              r"independent rebuild PASSED (same box, fresh directory and venv; NOT a second machine), bound to the p18 "
              r"tree bfab3b4b\ldots{} and zip 7c7d5451\ldots; p19 records this as independent\_rebuild\_passed\_p18 "
              r"and does not inherit it. Reviewer findings I1--I3 are addressed in p19 (I1 fail-closed gate, I2 "
              r"extended scan -- a pattern check, not a proof, I3 milestone wording); no contract revision.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p18_README.md}}",
              r"\section{Archival material (p17): D01/D03 evanescent poles vs the ch slot, superseded by p18}",
              r"\scopebox{Archival.}{The p17 release (\texttt{archival/p17/}) is superseded as a release by p18; its "
              r"calculation code (hh\_slot, release\_p17) stays byte-identical and active as the p17 layer. Its "
              r"independent rebuild PASSED (same box, fresh directory and venv; NOT a second machine), bound to the p17 "
              r"tree 2a5a6317\ldots{} and zip 7f4f61df\ldots; p18 records this as independent\_rebuild\_passed\_p17 "
              r"and does not inherit it. Reviewer findings H1--H5 are addressed in p18 (one disclosed dred.py revision, "
              r"documentation only).}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p17_README.md}}",
              r"\section{Archival material (p16): E2 decoupling proof and Batch C (D01, D03), superseded by p17}",
              r"\scopebox{Archival.}{The p16 release (\texttt{archival/p16/}) is superseded as a release by p17; its "
              r"calculation code (covariant route, Batch C, E2 proof, release\_p16) stays byte-identical and active as "
              r"the p16 layer. Its independent rebuild PASSED (same box, fresh directory and venv; NOT a second machine), "
              r"bound to the p16 tree 90b4a665\ldots{} and zip 56d5887d\ldots; p17 records this as "
              r"independent\_rebuild\_passed\_p16 and does not inherit it. Reviewer findings G1--G4 and G6 are addressed "
              r"in p17 (G2: one disclosed dred.py revision, the guarded loader parse\_d).}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p16_README.md}}",
              r"\section{Archival material (p15): first P.5 calculation (Batch A, D13), superseded by p16}",
              r"\scopebox{Archival.}{The p15 release (\texttt{archival/p15/}) is superseded as a release by p16; its "
              r"calculation code (integral library, Batch A, D13, release\_p15) stays byte-identical and active as the "
              r"p15 layer. Its independent rebuild PASSED (same box, fresh directory and venv; NOT a second machine), "
              r"bound to the p15 tree 79f53752\ldots{} and zip 54325c1f\ldots; p16 records this as "
              r"independent\_rebuild\_passed\_p15 and does not inherit it. Reviewer findings F3--F5 are addressed in "
              r"p16 (F3: one disclosed dred.py revision).}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p15_README.md}}",
              r"\section{Archival material (p14r): the P.5-entry contract release (contract active in p15, p16)}",
              r"\scopebox{Archival.}{The p14r release (\texttt{archival/p14r/}) is superseded as a release by p15; its "
              r"contract code stays active as the frozen contract on which p15 evaluates. Its independent rebuild "
              r"PASSED (same box, fresh directory and venv; NOT a second machine), bound to the p14r tree a64c0ae3\ldots "
              r"and zip 19e8bf59\ldots. ONE disclosed contract revision inside p15: the heuristic PrematureD4 guard of "
              r"dred.py (finding F1: a false positive and a false negative) is replaced by a structural safeguard; "
              r"released p14r values are unaffected (Pipeline.laurent was used only on toys).}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p14r_README.md}}",
              r"\section{Archival material (p14): superseded by the p14r repair}",
              r"\scopebox{Archival.}{The p14 release (\texttt{archival/p14/}) is superseded by p14r, a narrow repair: "
              r"p14 stated a DRED-type prescription without executable index rules and claimed that no evanescent "
              r"remainder arises (withdrawn); its M3 labels conflated the scalar-extension and kernel scaling degrees; "
              r"it called the counterterm quotient ``essential'' directions; its W5 regeneration did not cover D01, D02, "
              r"D03, D12; and its gate-mutation test copies lacked frozen inputs. P.3/P.4 code is unchanged.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p14_README.md}}",
              r"\section{Archival material (p13): frozen classical P.3/P.4 inputs}",
              r"\scopebox{Archival.}{The p13 release (\texttt{archival/p13/}) is superseded by p14 as a release but its "
              r"classical P.3/P.4 code is kept byte-identical and is the frozen P.5 input. The archive holds the p13 "
              r"source-only zip (tree 2b1baf33\ldots, zip 2f85a566\ldots), its reference values, its author rebuild "
              r"report and the independent rebuild report (passed; SAME box with a fresh venv and a source-only build, "
              r"NOT a second machine). The p14 freeze check re-verifies these pins on every release.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p13_README.md}}",
              r"\section{Archival material (p12): NOT p14 evidence}",
              r"\scopebox{Archival.}{The p12 release (\texttt{archival/p12/}) is superseded by p13, which adds no "
              r"mathematics. p12 used ``classical readiness'' without the milestone labels fixed in p13 (P.3, P.4 = "
              r"classical readiness, P.5 entry/calculation/identity), had no completion dossier, and had no source-only "
              r"rebuild contract or rebuild flags.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p12_README.md}}",
              r"\section{Archival material (p11): NOT p14 evidence}",
              r"\scopebox{Archival.}{The p11 release (\texttt{archival/p11/}) is superseded. Its certificate FILES were "
              r"internally consistent (all Noether residual counts zero), but its appendix typeset multi-line JSON arrays: "
              r"a page break inside \texttt{Q\_terms} placed the footer page number (12, 29) between array elements, so a "
              r"text extraction read [0,0,120,0] and [290,0,0,0]. p12 prints scalar arrays on one line, prefixes page "
              r"numbers, enforces the count/flag invariant before serialization and in the release gate, cross-checks the "
              r"quartic and master records, and gates every pdf/zip/sync stage.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p11_README.md}}",
              r"\section{Archival material (p10): NOT p14 evidence}",
              r"\scopebox{Archival.}{The p10 release (\texttt{archival/p10/}) is superseded and is not p14 evidence: its C3 "
              r"was vacuous and stated the wrong orientation $+\partial_\mu B^\mu$; it cited samples as proof; its master "
              r"certificate carried an unconditional pass; its multidegree lemma and polarization statement were imprecise. "
              r"Its note is preserved verbatim in \texttt{archival/p10/notes/} and is not typeset here.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_p10_README.md}}",
              r"\section{Archival material (p02--p09): NOT p14 evidence; superseded milestone wording}",
              r"\scopebox{Archival.}{Everything in this section is superseded material from revisions p02--p09, kept "
              r"for provenance only (\texttt{archival/p02\_p09/}). It is not read by the p14 pipeline and is not "
              r"acceptance evidence. HISTORY ONLY: its milestone wording (``P-next.N'', and the table row ``P4 coupled "
              r"one-loop restoration'' in \texttt{P\_scope.tex}) is superseded by the p13 definitions kept in p14 (P.4 = classical "
              r"readiness, NOT coupled one-loop restoration; see the milestone section of the science volume). The archived \texttt{ell4\_verify.py} and \texttt{ell4\_generator.py} state the "
              r"WRONG boundary orientation ($+\partial_\mu B^\mu$) and a vacuous C3; see "
              r"\texttt{P13\_boundary\_identity.json}.}",
              r"{\scriptsize\verbatiminput{listing_src/archival_README.md}}",
              r"\begingroup\let\section\subsection\let\subsection\subsubsection\let\subsubsection\paragraph"]
    for n in arch_notes:
        lines.append(f"\\input{{../archival/p02_p09/notes/{n.name}}}")
    lines.append(r"\endgroup")
    (LST / "archival_p21_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p21" / "README.md").read_text())))
    (LST / "archival_p20_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p20" / "README.md").read_text())))
    (LST / "archival_p19_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p19" / "README.md").read_text())))
    (LST / "archival_p18_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p18" / "README.md").read_text())))
    (LST / "archival_p17_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p17" / "README.md").read_text())))
    (LST / "archival_p16_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p16" / "README.md").read_text())))
    (LST / "archival_p15_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p15" / "README.md").read_text())))
    (LST / "archival_p14r_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p14r" / "README.md").read_text())))
    (LST / "archival_p14_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p14" / "README.md").read_text())))
    (LST / "archival_p13_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p13" / "README.md").read_text())))
    (LST / "archival_p12_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p12" / "README.md").read_text())))
    (LST / "archival_p11_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p11" / "README.md").read_text())))
    (LST / "archival_p10_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p10" / "README.md").read_text())))
    (LST / "archival_README.md").write_text(wrap_lines(ascii_clean((ROOT / "archival" / "p02_p09" / "README.md").read_text())))
    (MS / "body" / "XVI-P-appendix-body.tex").write_text("\n".join(lines) + "\n")


FRONT = {
    "XVI-P-science.tex": ("Landmark XVI-P --- Scientific manuscript\\\\\n\\large Science volume (p23: O.1 requirement recorded, one-loop power counting, P.6 entry inventory (kappa\\textsuperscript{3} three-point, not evaluated); P.5 calculation renormalized at one loop kappa\\textsuperscript{2} for the two-point functions with QdS external legs; bulk symmetry not claimed; O.1 NOT\\_CLOSED)",
                          "\\noindent\\textbf{Science volume.} Certificates and listings: \\texttt{XVI-P-appendix.pdf}; "
                          "combined: \\texttt{XVI-P.pdf}.\n\n\\tableofcontents\n\\newpage\n\\input{body/XVI-P-body.tex}"),
    "XVI-P-appendix.tex": ("Landmark XVI-P --- Appendix\\\\\n\\large Certificates, listings, archival section (p23)",
                           "\\tableofcontents\n\\newpage\n\\input{body/XVI-P-appendix-body.tex}"),
    "XVI-P.tex": ("Landmark XVI-P --- Combined release\\\\\n\\large (p23: O.1 requirement recorded, one-loop power counting, P.6 entry inventory (kappa\\textsuperscript{3} three-point, not evaluated); P.5 calculation renormalized at one loop kappa\\textsuperscript{2} for the two-point functions with QdS external legs; bulk symmetry not claimed; O.1 NOT\\_CLOSED)",
                  "\\tableofcontents\n\\newpage\n\\part{Science}\n\\input{body/XVI-P-body.tex}\n\\newpage\n"
                  "\\part{Appendix}\n\\input{body/XVI-P-appendix-body.tex}"),
}


def write_version():
    """F4 (p16): the footer label comes from ONE variable, the VERSION_LABEL of the current conventions (p23)."""
    assert re.fullmatch(r"XVI-P p\d+[a-z]?", QC.VERSION_LABEL) and QC.VERSION_LABEL.endswith(QC.REVISION)
    (MS / "version.tex").write_text("% generated by tools/build.py from code/p5_calc/p23_conventions.py VERSION_LABEL\n"
                                    "\\newcommand{\\XVIPversion}{" + QC.VERSION_LABEL + "}\n")


def write_fronts():
    write_version()
    for fn, (title, body) in FRONT.items():
        (MS / fn).write_text("\\documentclass{article}\n\\input{preamble.tex}\n\n"
                             f"\\title{{{title}}}\n\\author{{XVI-P {QC.REVISION}}}\n\\date{{{QC.DATE}}}\n\n"
                             "\\begin{document}\n\\maketitle\n" + body + "\n\\end{document}\n")


def build_pdfs():
    for stem in ("XVI-P-science", "XVI-P-appendix", "XVI-P"):
        for ext in (".aux", ".toc", ".out", ".log", ".pdf"):
            (MS / (stem + ext)).unlink(missing_ok=True)
        for _ in range(2):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", stem + ".tex"],
                               cwd=str(MS), capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                print(r.stdout[-3000:])
                raise SystemExit(f"pdflatex failed for {stem}")
        LOG.append({"stage": f"pdf {stem}", "pages": pdf_pages(MS / (stem + ".pdf"))})
        print(f"[pdf] {stem} pages={pdf_pages(MS / (stem + '.pdf'))}", flush=True)
    assert not any("MANIFEST" in p.name for p in LST.glob("*")), "manifest must not be listed in a PDF"


def assert_no_hash_in_pdfs():
    """After the manifest: no PDF/zip sha256 from the manifest occurs in the text of any PDF."""
    hashes = re.findall(r"sha256=([0-9a-f]{64})", (ROOT / "RELEASE_MANIFEST_EXTERNAL.txt").read_text())
    found = []
    for stem in ("XVI-P-science", "XVI-P-appendix", "XVI-P"):
        txt = subprocess.run(["pdftotext", str(MS / (stem + ".pdf")), "-"], capture_output=True, text=True).stdout
        txt = re.sub(r"\s+", "", txt)
        found += [f"{stem}:{h[:12]}" for h in hashes if h in txt]
    assert not found, found
    return True


def check_listings_current():
    for title, rel in LISTINGS:
        cur = wrap_lines(ascii_clean((ROOT / rel).read_text()))
        if (LST / rel.replace("/", "__")).read_text() != cur:
            raise SystemExit(f"listing stale: {rel}")


EXCL_DIRS = {"__pycache__", "dist", ".pytest_cache", "stale"}
EXCL_SUFFIX = {".aux", ".log", ".toc", ".out", ".pkl", ".pyc", ".zip"}  # no nested zips


def _walk(base: Path):
    for p in sorted(base.rglob("*")):
        if p.is_dir() or any(part in EXCL_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.suffix in EXCL_SUFFIX or p.name in ("RELEASE_MANIFEST_EXTERNAL.txt", "PUBLICATION_REJECTED.txt"):
            continue
        if p.relative_to(ROOT).parts[:2] in (("build", "p10"), ("build", "p13"), ("build", "p14")) and p.suffix == ".log":
            continue
        yield p


def make_zips():
    DIST.mkdir(exist_ok=True)
    focus = ["README.md", "REBUILD_INSTRUCTIONS.md", "RELEASE_STATUS.json", "manuscript/XVI-P-science.pdf",
             "manuscript/XVI-P-appendix.pdf", "manuscript/XVI-P.pdf", "manuscript/notes/P16_E2_and_batchC.tex",
             "manuscript/body/P16-results-table.tex", "ledgers/P16_milestones.json", "tests/test_p16.py",
             "manuscript/notes/P17_hh_slot.tex", "manuscript/body/P17-results-table.tex", "ledgers/P17_milestones.json",
             "tests/test_p17.py", "manuscript/notes/P18_D11.tex", "manuscript/body/P18-results-table.tex",
             "ledgers/P18_milestones.json", "tests/test_p18.py", "manuscript/notes/P19_defect.tex",
             "manuscript/body/P19-results-table.tex", "ledgers/P19_milestones.json", "tests/test_p19.py",
             "manuscript/notes/P20_correction.tex", "certificates/P20_D11_pin.json", "ledgers/P20_milestones.json",
             "tests/test_p20.py", "manuscript/notes/P21_absolute_pin.tex", "ledgers/P21_milestones.json",
             "tests/test_p21.py", "manuscript/notes/P22_evanescent.tex", "ledgers/P22_milestones.json",
             "tests/test_p22.py", "certificates/P22_evanescent.json", "manuscript/notes/P23_O1_scope.tex",
             "ledgers/P23_milestones.json", "tests/test_p23.py", "certificates/P23_O1_scope.json",
             "archival/p22/README.md", "archival/p21/README.md",
             "archival/p21/reference_values_p21.json",
             "archival/p21/reproducibility/independent_rebuild_report_p21.json",
             "archival/p21/reproducibility/author_rebuild_report_p21.json", "archival/p20/README.md", "archival/p20/reference_values_p20.json",
             "archival/p20/reproducibility/independent_rebuild_report_p20.json",
             "archival/p20/reproducibility/author_rebuild_report_p20.json",
             "archival/p19/README.md", "archival/p19/reference_values_p19.json",
             "archival/p19/reproducibility/independent_rebuild_report_p19.json",
             "archival/p19/reproducibility/author_rebuild_report_p19.json",
             "archival/p18/README.md", "archival/p18/reference_values_p18.json",
             "archival/p18/reproducibility/independent_rebuild_report_p18.json",
             "archival/p18/reproducibility/author_rebuild_report_p18.json", "archival/p17/README.md",
             "archival/p17/reference_values_p17.json",
             "archival/p17/reproducibility/independent_rebuild_report_p17.json",
             "archival/p17/reproducibility/author_rebuild_report_p17.json", "archival/p16/README.md", "archival/p16/reference_values_p16.json",
             "archival/p16/reproducibility/independent_rebuild_report_p16.json",
             "archival/p16/reproducibility/author_rebuild_report_p16.json",
             "manuscript/preamble.tex", "manuscript/version.tex",
             "archival/p15/README.md", "archival/p15/reference_values_p15.json",
             "archival/p15/reproducibility/independent_rebuild_report_p15.json",
             "archival/p15/reproducibility/author_rebuild_report_p15.json",
             "manuscript/notes/P15_first_calculation.tex",
             "manuscript/body/P15-results-table.tex", "ledgers/P15_milestones.json", "tests/test_p15.py",
             "archival/p14r/README.md", "archival/p14r/reference_values_p14r.json",
             "archival/p14r/reproducibility/independent_rebuild_report_p14r.json",
             "archival/p14r/reproducibility/author_rebuild_report_p14r.json",
             "manuscript/notes/P14_P5_entry_contract.tex",
             "manuscript/notes/P14_frozen_classical_record.tex", "manuscript/body/P14-dossier-table.tex",
             "manuscript/body/P14-entry-summary.tex", "ledgers/P13_ch_dependency_rows.json",
             "ledgers/P13_graph_inventory.json", "ledgers/P14_milestones.json", "exports/V4_grav.json",
             "exports/ell4_generating_polynomial.srepr", "exports/ell3_generating_polynomial.srepr",
             "exports/ell2_generating_polynomial.srepr", "exports/ell4_conventions.json", "tools/build.py",
             "tools/manifest.py", "tools/source_manifest.py", "tools/rebuild_from_source.py", "tests/test_p14.py",
             "build/p14/test_results/e2e_mutations.json", "build/p14/pdf_readback.json", "build/p14/pdf_inputs.json",
             "build/p14/junit.xml", SM.REFERENCE_FILE, SM.PINS_FILE, "exports/P14_vertex_tensors.json",
             "archival/p13/README.md", "archival/p13/reference_values_p13.json", "archival/p13/frozen_p13_inputs.json",
             "archival/p13/reproducibility/independent_rebuild_report_p13.json",
             "archival/p13/reproducibility/author_rebuild_report_p13.json", "archival/p12/README.md", "archival/p11/README.md", "archival/p10/README.md",
             "code/p4_classical/ch_source_audit.py", "code/p5_entry/dred.py", "code/p5_entry/hessian_route.py",
             "certificates/P14_dred_rules.json", "archival/p14/README.md"]
    for opt in (QC.AUTHOR_REPORT, QC.INDEPENDENT_REPORT_CURRENT):
        if (ROOT / opt).exists():
            focus.append(opt)
    focus += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "certificates").glob("P1[3456]_*.json"))]
    focus += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "exports" / "P14_integrands").glob("*.json"))]
    focus += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "code" / "classical").glob("*.py"))]
    focus += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "code" / "p5_entry").glob("*.py"))]
    focus += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "code" / "p5_calc").glob("*.py"))]
    focus = [f for f in focus if (ROOT / f).exists()]
    out = {}
    for name, files in (("XVI-P-review-focus.zip", focus),
                        ("XVI-P-full.zip", [str(p.relative_to(ROOT)) for p in _walk(ROOT)])):
        zp = DIST / name
        zp.unlink(missing_ok=True)
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for rel in sorted(set(files)):
                info = zipfile.ZipInfo("XVI-P/" + rel, date_time=(2026, 10, 8, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, (ROOT / rel).read_bytes())
        out[name] = len(set(files))
        print(f"[zip] {name} files={out[name]} bytes={zp.stat().st_size}", flush=True)
    src = SM.make_zip(DIST / SRC_ZIP, ROOT)
    out[SRC_ZIP] = src["files"]
    print(f"[zip] {SRC_ZIP} files={src['files']} bytes={src['bytes']} (source only; tools/source_manifest.py)", flush=True)
    return out


MANIFEST_FILES = ("manuscript/XVI-P-science.pdf", "manuscript/XVI-P-appendix.pdf", "manuscript/XVI-P.pdf",
                  "dist/XVI-P-review-focus.zip", "dist/XVI-P-full.zip", f"dist/{SRC_ZIP}",
                  "RELEASE_STATUS.json", "certificates/P23_release.json", "ledgers/P23_milestones.json",
                  "certificates/P23_test_results.json", "certificates/P23_O1_scope.json",
                  "certificates/P22_release.json", "ledgers/P22_milestones.json", "certificates/P22_evanescent.json",
                  "certificates/P21_release.json", "ledgers/P21_milestones.json",
                  "certificates/P20_release.json", "ledgers/P20_milestones.json", "certificates/P20_D11_pin.json",
                  "certificates/P19_release.json", "ledgers/P19_milestones.json", "certificates/P19_defect.json",
                  "certificates/P18_release.json", "ledgers/P18_milestones.json",
                  "certificates/P18_D11_M2.json", "certificates/P18_D11.json", "certificates/P18_hh_slot.json",
                  "certificates/P17_release.json", "ledgers/P17_milestones.json", "certificates/P17_hh_slot.json",
                  "certificates/P16_release.json", "ledgers/P16_milestones.json",
                  "certificates/P16_E2_evanescent.json", "certificates/P16_batchC.json",
                  "certificates/P15_release.json", "ledgers/P15_milestones.json",
                  "certificates/P15_integral_library.json", "certificates/P15_batchA.json", "certificates/P15_D13.json",
                  "certificates/P14_release.json", "certificates/P14_closure_release.json",
                  "certificates/P14_dossier.json", "ledgers/P14_milestones.json",
                  "certificates/P14_quantum_object.json", "certificates/P14_prescription_D11_matching.json",
                  "certificates/P14_counterterm_domain.json", "certificates/P14_amplitude_rules.json",
                  "certificates/P14_dred_rules.json",
                  "exports/P14_vertex_tensors.json",
                  "exports/ell2_generating_polynomial.srepr", "exports/ell3_generating_polynomial.srepr",
                  "exports/ell4_generating_polynomial.srepr", "exports/V4_grav.json",
                  "REBUILD_INSTRUCTIONS.md", SM.REFERENCE_FILE,
                  "reproducibility/inherited_data_pins.json", QC.AUTHOR_REPORT)
# pinned p13 inputs: their sha256 are printed in the PDFs on purpose (p14_conventions listing), so they are NOT hash
# entries of this manifest (whose hashes must never occur inside a PDF); they are listed by path, verified by F1-F3.
PINNED_P13 = ("archival/p13/reference_values_p13.json", "archival/p13/frozen_p13_inputs.json",
              "archival/p13/XVI-P-source-only_p13.zip", "archival/p13/reproducibility/independent_rebuild_report_p13.json")


def write_manifest():
    rs = json.loads((ROOT / "RELEASE_STATUS.json").read_text())
    tr = json.loads((ROOT / "certificates" / f"{QC.CERT_PREFIX}_test_results.json").read_text())
    cl = rs["classical"]
    lines = [f"XVI-P RELEASE_MANIFEST_EXTERNAL -- revision {QC.REVISION} (contract {QC.CONTRACT_REVISION})",
             f"date: {QC.DATE}",
             f"XVI-M_sha256: {rs['XVI_M_sha256']}  pin_ok: {rs['XVI_M_pin_ok']}",
             f"execution_pass: {rs['execution_pass']}", f"claim_status: {rs['claim_status']}",
             f"release_claim_accepted: {rs['release_claim_accepted']}", f"publication: {rs['publication']}",
             f"scope: {rs['scope']}", ""]
    lines += [f"milestone {k}: {v}" for k, v in rs["milestones"]["status"].items()]
    lines += [f"library_certified: {rs['library_certified']}", f"batchA_evaluated: {rs['batchA_evaluated']}",
              f"D13_evaluated: {rs['D13_evaluated']}", f"batchC_evaluated: {rs['batchC_evaluated']}",
              f"E2_status: {rs['E2_status']}  (E2_decoupling_proven: {rs['E2_decoupling_proven']})",
              f"hh_evanescent_status: {rs['hh_evanescent_status']}  (hh_evanescent_decoupling_proven: "
              f"{rs['hh_evanescent_decoupling_proven']}; evanescent_hh_counterterm_added: "
              f"{rs['evanescent_hh_counterterm_added']})",
              f"hh_full_row_decoupling_proven: {rs['hh_full_row_decoupling_proven']}",
              f"D11_evaluated: {rs['D11_evaluated']}", f"D12_status: {rs['D12_status']}",
              f"D11_matching_verified_scope: {rs['D11_matching_verified_scope']}  (evanescent components: "
              f"{rs['D11_evanescent_components_matching']})",
              f"M3_status: {rs['M3_status']}",
              f"quantum_inputs_evaluated: {rs['quantum_inputs_evaluated']}  (inventory: "
              + "; ".join(f"{x['graph']} [{x['slot_row']}] {x['status']}" for x in rs['quantum_inputs_inventory']) + ")",
              f"projected_identity_verified: {rs['projected_identity_verified']}",
              f"projected_restoration_verified: {rs['projected_restoration_verified']}",
              f"projected_defect_computed: {rs['projected_defect_computed']}",
              f"bulk_symmetry_restored: {rs['bulk_symmetry_restored']}",
              f"counterterm_solve: {rs['counterterm_solve']['outcome']}  (rank P_ch sigma_0 "
              f"{rs['counterterm_solve']['rank_P_ch_sigma0_routeG']}; {rs['counterterm_solve']['solution']})",
              f"why_zero: {rs['why_zero']}",
              f"rests_on: {'; '.join(rs['rests_on'])}"]
    lines += [f"flag_definition {k}: {v}" for k, v in rs["flag_definitions"].items()]
    lines += [f"finding {k}: {v}" for k, v in rs["findings"].items()]
    lines += [f"graph {k}: {v.get('status')}" for k, v in rs["graphs"].items()]
    lines += [f"contract_revision_disclosed: {', '.join(rs['contract_identity']['changed_vs_p14r'])} "
              f"(p15: finding F1 of the p14r independent rebuild; p16: finding F3 of the p15 independent rebuild; "
              f"p17: findings G1-G3 of the p16 independent rebuild; p18: H3/H5 of the p17 independent rebuild "
              f"(documentation only); p19: none; p20: none; p21: none; p22: runtime d guard, one additive block (contract_registry); p23: polynomial-domain refusal, one appended block; "
              f"released values unaffected); new contract files: {rs['contract_identity']['added'] or 'none'}"]
    cl22 = rs["change_log_vs_p21"]
    lines += [f"change_log_vs_p21 {k}: {', '.join(cl22[k]) or 'none'}" for k in ("added", "modified", "removed")]
    ev = rs["evanescent"]
    lines += [f"EV_M2: {ev['EV_M2_verdict']}: {ev['EV_M2']}",
              f"D11_matching_verified_scope (p22): {rs['D11_matching_verified_scope']}",
              f"evanescent counterterm coefficients (hh sum): {ev['coefficients_hh_sum']}; K'.c E2: "
              f"{ev['coefficient_Kc_E2']}; cb.c SE: {ev['coefficient_ccb_SE']}",
              f"evanescent checks: {ev['check']}",
              f"Q4S trace remnant: {ev['remnants']['O_eps_times_pole_Q4S_trace_external']}",
              f"P5_calculation_status: {rs['P5_calculation_status']}",
              f"d_runtime_guard: ok {rs['d_runtime_guard']['ok']}; plants {rs['d_runtime_guard']['n_plants']}; "
              f"not raised {rs['d_runtime_guard']['not_raised']}; entry points {rs['d_runtime_guard']['entry_points']}",
              f"d_runtime_guard residue: {rs['d_runtime_guard']['residue_not_interceptable']}",
              f"evanescent_M2_verified: {rs['evanescent_M2_verified']}",
              f"evanescent_counterterms_verified: {rs['evanescent_counterterms_verified']}",
              f"d_runtime_guard_verified: {rs['d_runtime_guard_verified']}"]
    o1 = rs["O1"]
    lines += [f"O1_requirement (p23): {o1['requirement']}", f"O1_closable_in_XVI_P: {o1['closable_in_XVI_P']} ({o1['reason']})",
              f"power_counting (p23): vertex rule {rs['power_counting']['vertex_rule']}; one-loop kappa^E "
              f"{rs['power_counting']['kappa_equals_E']}; frozen E2 match {rs['power_counting']['frozen_E2_match']['equal']}; "
              f"enlarge rule triggered {rs['power_counting']['identity_at_kappa2']['enlarge_rule_triggered']}",
              f"P6_entry (p23): {rs['P6_entry']['n_graphs']} graphs {rs['P6_entry']['by_external']}; {rs['P6_entry']['status']}",
              f"d_poly_domain_refusal (p23): {rs['d_poly_domain_refusal']['ok']}; not raised {rs['d_poly_domain_refusal']['not_raised']}",
              f"EV_values (p23): {all(v['ok'] for v in rs['EV_values']['values'].values())}",
              f"title_qualifier (p23): {QC.TITLE_QUALIFIER}"]
    cl23 = rs["change_log_vs_p22"]
    lines += [f"change_log_vs_p22 {k}: {', '.join(cl23[k]) or 'none'}" for k in ("added", "modified", "removed")]
    lines += [f"erratum_p19 (p20 layer) {k}: {v}" for k, v in rs["p20_layer_erratum_p19"].items()]
    ap = rs["p21_layer_absolute_pin"]["absolute_pin"]
    lines += [f"D11_absolute_pin: status {ap['status']}; package Gamma2 pole per kappa^2/eps "
              f"{ap['derivation_p21']['package_Gamma2_pole_per_kappa2_over_eps']}; heat-kernel prediction "
              f"{ap['derivation_p21']['heat_kernel_prediction_per_kappa2_over_eps']}; external convention choices: "
              f"{ap['derivation_p21']['convention_choices_external']}",
              f"D11_ratio_pin_verified: {rs['D11_ratio_pin_verified']}",
              f"D11_absolute_pin_verified: {rs['D11_absolute_pin_verified']}", f"open_pins: {rs['open_pins']}",
              f"runtime_guard_limitation_p21 (CLOSED in p22): {Q21.RUNTIME_GUARD_LIMITATION_P21}"]
    p13i, p14ri, p15i = rs["p13_independent_rebuild"], rs["p14r_independent_rebuild"], rs["p15_independent_rebuild"]
    p16i, p17i, p18i = rs["p16_independent_rebuild"], rs["p17_independent_rebuild"], rs["p18_independent_rebuild"]
    lines += [f"P5_entry_earned: {rs['P5_entry_earned']}"]
    lines += [f"P5_entry_flag {k}: {v}" for k, v in rs["P5_entry_flags"].items()]
    lines += [f"P3_P4_frozen_as_P5_inputs: {rs['P3_P4_frozen_as_P5_inputs']}  (bound to p13 source tree "
              f"{p13i.get('bound_to_source_tree_sha256')})",
              f"independent_rebuild_passed_p13: {rs['independent_rebuild_passed_p13']}  caveat: {p13i.get('caveat')}",
              f"independent_rebuild_passed_p14r: {rs['independent_rebuild_passed_p14r']}  (bound to p14r tree "
              f"{p14ri.get('bound_to_source_tree_sha256')} / zip {p14ri.get('bound_to_source_zip_sha256')}; "
              f"caveat: {p14ri.get('caveat')})",
              f"independent_rebuild_passed_p15: {rs['independent_rebuild_passed_p15']}  (bound to p15 tree "
              f"{p15i.get('bound_to_source_tree_sha256')} / zip {p15i.get('bound_to_source_zip_sha256')}; "
              f"caveat: {p15i.get('caveat')})",
              f"independent_rebuild_passed_p16: {rs['independent_rebuild_passed_p16']}  (bound to p16 tree "
              f"{p16i.get('bound_to_source_tree_sha256')} / zip {p16i.get('bound_to_source_zip_sha256')}; "
              f"caveat: {p16i.get('caveat')})",
              f"independent_rebuild_passed_p17: {rs['independent_rebuild_passed_p17']}  (bound to p17 tree "
              f"{p17i.get('bound_to_source_tree_sha256')} / zip {p17i.get('bound_to_source_zip_sha256')}; "
              f"caveat: {p17i.get('caveat')})",
              f"independent_rebuild_passed_p18: {rs['independent_rebuild_passed_p18']}  (bound to p18 tree "
              f"{p18i.get('bound_to_source_tree_sha256')} / zip {p18i.get('bound_to_source_zip_sha256')}; "
              f"caveat: {p18i.get('caveat')})",
              f"independent_rebuild_passed_p19: {rs['p20_layer_independent_rebuild_passed_p19']}  (bound to p19 tree "
              f"{rs['p20_layer_p19_independent_rebuild'].get('bound_to_source_tree_sha256')} / zip "
              f"{rs['p20_layer_p19_independent_rebuild'].get('bound_to_source_zip_sha256')}; "
              f"caveat: {rs['p20_layer_p19_independent_rebuild'].get('caveat')})",
              f"independent_rebuild_passed_p20: {rs['p21_layer_independent_rebuild_passed_p20']}  (bound to p20 tree "
              f"{rs['p21_layer_p20_independent_rebuild'].get('bound_to_source_tree_sha256')} / zip "
              f"{rs['p21_layer_p20_independent_rebuild'].get('bound_to_source_zip_sha256')}; "
              f"caveat: {rs['p21_layer_p20_independent_rebuild'].get('caveat')})",
              f"independent_rebuild_passed_p21: {rs['independent_rebuild_passed_p21']}  (bound to p21 tree "
              f"{rs['p21_independent_rebuild'].get('bound_to_source_tree_sha256')} / zip "
              f"{rs['p21_independent_rebuild'].get('bound_to_source_zip_sha256')}; "
              f"caveat: {rs['p21_independent_rebuild'].get('caveat')})",
              f"{QC.REVISION} author_rebuild_passed: {rs['author_rebuild_passed']}",
              f"{QC.REVISION} independent_rebuild_passed: {rs['independent_rebuild_passed']}",
              f"D11_matching_verified: {rs['D11_matching_verified']}",
              f"source_tree_sha256: {SM.tree_sha(ROOT)}", ""]
    lines += [f"classical {k}: {v}" for k, v in cl["flags"].items()]
    lines += [f"classical_readiness_for_ch_identity: {cl['classical_readiness_for_ch_identity']}",
              f"required_master_residuals: {cl['required_master_residuals']}"]
    lines += [f"{k}: {v}" for k, v in rs["hard_stops"].items()]
    lines += [f"tests: {tr['summary']}", ""]
    lines += [f"pinned p13 input (pin in code/p5_entry/p14_conventions.py; verified by the freeze F1-F3): {rel}"
              f"  present={(ROOT / rel).exists()}" for rel in PINNED_P13]
    lines += ["", "Files (written after the PDFs and zips; no PDF contains any of these hashes):"]
    for rel in MANIFEST_FILES:
        if (ROOT / rel).exists():
            lines.append(file_line(ROOT, rel))
    man = ROOT / "RELEASE_MANIFEST_EXTERNAL.txt"
    man.write_text("\n".join(lines) + "\n")
    v = verify(man, ROOT)
    assert v["pass"], v
    v["no_pdf_hash_inside_pdfs"] = assert_no_hash_in_pdfs()
    return v


def sync_top():
    pairs = [(MS / "XVI-P-science.pdf", TOP / "XVI-P-science.pdf"), (MS / "XVI-P-appendix.pdf", TOP / "XVI-P-appendix.pdf"),
             (MS / "XVI-P.pdf", TOP / "XVI-P.pdf"), (DIST / "XVI-P-review-focus.zip", TOP / "XVI-P-review-focus.zip"),
             (DIST / "XVI-P-full.zip", TOP / "XVI-P-full.zip"), (DIST / SRC_ZIP, TOP / SRC_ZIP)]
    TOP.mkdir(parents=True, exist_ok=True)
    out = {}
    for s, d in pairs:
        shutil.copyfile(s, d)
        assert sha(s) == sha(d)
        out[d.name] = {"bytes": d.stat().st_size, "pages": pdf_pages(d) if d.suffix == ".pdf" else None, "sha256": sha(d)}
    return out


def collect_tests():
    d = ROOT / "build" / "p14" / "test_results"
    res = {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json"))} if d.exists() else {}
    junit = ROOT / "build" / "p14" / "pytest_summary.txt"
    summ = junit.read_text().strip() if junit.exists() else "not run"
    (ROOT / "certificates" / f"{QC.CERT_PREFIX}_test_results.json").write_text(certio.dumps(
        {"revision": QC.REVISION, "summary": summ, "groups": junit_groups(), "results": res}))
    return summ


def junit_groups(path=None):
    """Per-group outcomes from the pytest junit XML: baseline / certificate_mutation / resumed_build."""
    import xml.etree.ElementTree as ET
    path = Path(path) if path else ROOT / "build" / "p14" / "junit.xml"
    if not path.exists():
        return {}
    groups = {"baseline": {"passed": 0, "failed": 0, "skipped": 0},
              "certificate_mutation": {"passed": 0, "failed": 0, "skipped": 0},
              "resumed_build": {"passed": 0, "failed": 0, "skipped": 0}}
    for tc in ET.parse(path).getroot().iter("testcase"):
        n = tc.get("name", "")
        g = ("resumed_build" if n.startswith("test_resumed_stage_build_blocked") else
             "certificate_mutation" if n.startswith(("test_certificate_mutation", "test_e2e_", "test_stale_ell4_hash",
                                                          "test_p5_entry_gate_mutation", "test_amplitude_rules_and_mutations"))
             else "baseline")
        st = ("failed" if tc.find("failure") is not None or tc.find("error") is not None else
              "skipped" if tc.find("skipped") is not None else "passed")
        groups[g][st] += 1
    return groups


# ---------------- p12/p13/p14: fresh clean, publication gate, rejection, readback ----------------
GENERATED = (["RELEASE_STATUS.json", "RELEASE_MANIFEST_EXTERNAL.txt", "PUBLICATION_REJECTED.txt",
              "certificates/RELEASE_STATUS.json", "exports/V4_grav.json", "exports/ell4_conventions.json",
              "manuscript/body/P13-dossier-table.tex", "manuscript/body/P14-dossier-table.tex",
              "manuscript/body/P14-entry-summary.tex", "manuscript/body/XVI-P-appendix-body.tex",
              "exports/P14_vertex_tensors.json", "reproducibility/reference_values_p15.candidate.json",
              "reproducibility/reference_values_p16.candidate.json", "manuscript/body/P15-results-table.tex",
              "manuscript/body/P16-results-table.tex", "manuscript/version.tex",
              "reproducibility/reference_values_p17.candidate.json", "manuscript/body/P17-results-table.tex",
              "reproducibility/reference_values_p18.candidate.json", "manuscript/body/P18-results-table.tex",
              "reproducibility/reference_values_p19.candidate.json", "manuscript/body/P19-results-table.tex",
              "reproducibility/reference_values_p20.candidate.json",
              "reproducibility/reference_values_p21.candidate.json",
              "reproducibility/reference_values_p22.candidate.json",
              "reproducibility/reference_values_p23.candidate.json"]
             + [f"exports/ell{k}_generating_polynomial.srepr" for k in (2, 3, 4)]
             + [f"manuscript/{s}.pdf" for s in PDF_STEMS] + [f"dist/{z}" for z in ZIPS])


def clean_fresh():
    """Full build: remove every generated P13/P14 artifact first, so nothing shown or shipped can be a stale copy.
    (reproducibility/*rebuild_report*.json are records of rebuilds of the SOURCE and are kept; the p13
    reproducibility/reference_values.json and everything under archival/ are never touched.)"""
    for pat in ("certificates/P13_*.json", "ledgers/P13_*.json", "certificates/P14_*.json", "ledgers/P14_*.json",
                "certificates/P15_*.json", "ledgers/P15_*.json", "certificates/P16_*.json", "ledgers/P16_*.json",
                "certificates/P17_*.json", "ledgers/P17_*.json", "certificates/P18_*.json", "ledgers/P18_*.json",
                "certificates/P19_*.json", "ledgers/P19_*.json",
                "certificates/P20_*.json", "ledgers/P20_*.json",
                "certificates/P21_*.json", "ledgers/P21_*.json",
                "certificates/P22_*.json", "ledgers/P22_*.json",
                "certificates/P23_*.json", "ledgers/P23_*.json"):
        for f in ROOT.glob(pat):
            f.unlink()
    for rel in GENERATED:
        assert not rel.startswith(("archival/", "reproducibility/reference_values.json",
                                   "reproducibility/independent_rebuild_report"))
        (ROOT / rel).unlink(missing_ok=True)
    shutil.rmtree(ROOT / "exports" / "P14_integrands", ignore_errors=True)
    shutil.rmtree(ROOT / "build" / "p14", ignore_errors=True)
    shutil.rmtree(ROOT / "build" / "p13", ignore_errors=True)   # p13 build outputs: archived in archival/p13/build
    shutil.rmtree(LST, ignore_errors=True)
    shutil.rmtree(STALE, ignore_errors=True)
    (ROOT / "build" / "p14").mkdir(parents=True, exist_ok=True)
    LOG.append({"stage": "clean_fresh"})


def reject_artifacts(stage, reasons):
    """Rejected build: existing PDFs/zips/manifest cannot pass as accepted artifacts; nothing is synced."""
    STALE.mkdir(exist_ok=True)
    moved = []
    for rel in [f"manuscript/{s}.pdf" for s in PDF_STEMS] + [f"dist/{z}" for z in ZIPS] + ["RELEASE_MANIFEST_EXTERNAL.txt"]:
        f = ROOT / rel
        if f.exists():
            dst = STALE / ("REJECTED__" + rel.replace("/", "__"))
            shutil.move(str(f), str(dst))
            moved.append(str(dst.relative_to(ROOT)))
    msg = {"publication": "REJECTED", "stage": stage, "reasons": reasons, "moved_to_stale": moved,
           "synced_to_top": False, "revision": QC.REVISION}
    (STALE / "REJECTED.json").write_text(json.dumps(msg, indent=1) + "\n")
    (ROOT / "PUBLICATION_REJECTED.txt").write_text(json.dumps(msg, indent=1) + "\n")
    (ROOT / "build" / "p14").mkdir(parents=True, exist_ok=True)
    (ROOT / "build" / "p14" / "build_log.json").write_text(json.dumps({"log": LOG, "rejected": msg}, indent=1))
    print("[gate] PUBLICATION REJECTED", json.dumps(msg), flush=True)
    raise SystemExit(3)


def listed_files():
    return [rel for _, rel in LISTINGS]


def file_sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def zips_current():
    bad = []
    for z in ZIPS:
        zp = DIST / z
        if not zp.exists():
            bad.append(f"missing {z}")
            continue
        if z == SRC_ZIP:
            bad += [f"{z}:{b}" for b in SM.zip_matches_tree(zp, ROOT)]
            continue
        try:
            zf = zipfile.ZipFile(zp)
        except zipfile.BadZipFile:
            bad.append(f"{z}: not a valid zip")
            continue
        with zf:
            for n in zf.namelist():
                rel = n.split("/", 1)[1]
                if rel.startswith(("certificates/", "exports/", "ledgers/", "code/", "tools/", "tests/", "manuscript/",
                                   "reproducibility/")) or rel == "RELEASE_STATUS.json":
                    f = ROOT / rel
                    if not f.exists() or zf.read(n) != f.read_bytes():
                        bad.append(f"{z}:{rel}")
    return bad


def publication_gate(stage):
    """Re-invoke the release gate and the dossier and check current artifact consistency; reject (and stop) on any
    failure.  Fail closed: an exception inside the checks is itself a rejection."""
    try:
        reasons = _gate_reasons(stage)
    except Exception as exc:  # noqa: BLE001
        reasons = [f"gate evaluation error: {type(exc).__name__}: {exc}"]
    if reasons:
        reject_artifacts(stage, reasons)
    (ROOT / "PUBLICATION_REJECTED.txt").unlink(missing_ok=True)
    print(f"[gate] before {stage}: accepted", flush=True)
    return True


def _gate_reasons(stage):
    reasons = []
    r = subprocess.run([PY, "code/p5_entry/release_p14.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"gate_before_{stage}", "release_rc": r.returncode})
    if r.returncode != 0:
        reasons.append(f"release_p14.py exit {r.returncode}")
    try:
        rs = json.loads((ROOT / "certificates" / "P14_release.json").read_text())      # the p14r CONTRACT record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P14_release (contract record) unreadable: {exc}")
    cl = rs.get("classical", {})
    if not (rs.get("release_claim_accepted") is True and cl.get("classical_readiness_for_ch_identity") is True
            and cl.get("release_claim_accepted") is True and rs.get("publication") == "accepted"):
        reasons.append("release_claim_accepted/readiness not true")
    if not (rs.get("P5_entry_earned") is True and all(v is True for v in rs.get("P5_entry_flags", {}).values())
            and len(rs.get("P5_entry_flags", {})) == len(PC.P5_ENTRY_FLAGS)):
        reasons.append("P5 entry not earned (all five contract flags required)")
    if rs.get("P3_P4_frozen_as_P5_inputs") is not True:
        reasons.append("p13 freeze (P3_P4_frozen_as_P5_inputs) not true")
    for k, v in PC.HARD_STOPS.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    reasons += [f"failed_prerequisite:{x}" for x in cl.get("failed_prerequisites", [])]
    if not (ROOT / "certificates" / "P14_closure_release.json").exists():
        reasons.append("closure artifact absent")
    d = subprocess.run([PY, "code/p5_entry/dossier_p14.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
    LOG.append({"stage": f"dossier_before_{stage}", "rc": d.returncode})
    if d.returncode != 0:
        reasons.append(f"dossier links unresolved: {d.stdout.strip()[-400:]}")
    r15 = subprocess.run([PY, "code/p5_calc/release_p15.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"p15_gate_before_{stage}", "release_rc": r15.returncode})
    if r15.returncode != 0:
        reasons.append(f"release_p15.py exit {r15.returncode}")
    try:
        rs = json.loads((ROOT / "certificates" / "P15_release.json").read_text())       # the p15 LAYER record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P15_release (p15 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q15.REVISION and rs.get("publication") == "accepted"
            and rs.get("release_claim_accepted") is True and rs.get("batchA_evaluated") is True
            and rs.get("D13_evaluated") is True and rs.get("library_certified") is True
            and rs.get("hard_stops_hold") is True):
        reasons.append("p15 layer not accepted")
    for k, v in Q15.HARD_STOPS_P15.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p15 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r16 = subprocess.run([PY, "code/p5_calc/release_p16.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"p16_gate_before_{stage}", "release_rc": r16.returncode})
    if r16.returncode != 0:
        reasons.append(f"release_p16.py exit {r16.returncode}: {r16.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "certificates" / "P16_release.json").read_text())       # the p16 layer record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P16_release (p16 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q16.REVISION and rs.get("publication") == "accepted"
            and rs.get("release_claim_accepted") is True and rs.get("batchA_evaluated") is True
            and rs.get("D13_evaluated") is True and rs.get("batchC_evaluated") is True
            and rs.get("E2_decoupling_proven") is True and rs.get("library_certified") is True
            and rs.get("D11_evaluated") is False and rs.get("hard_stops_hold") is True):
        reasons.append("p16 release not accepted")
    for k, v in Q16.HARD_STOPS_P16.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p16 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r17 = subprocess.run([PY, "code/p5_calc/release_p17.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"p17_gate_before_{stage}", "release_rc": r17.returncode})
    if r17.returncode != 0:
        reasons.append(f"release_p17.py exit {r17.returncode}: {r17.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "certificates" / "P17_release.json").read_text())       # the p17 layer record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P17_release (p17 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q17.REVISION and rs.get("publication") == "accepted"
            and rs.get("release_claim_accepted") is True and rs.get("batchC_evaluated") is True
            and rs.get("E2_decoupling_proven") is True and rs.get("hh_evanescent_decoupling_proven") is True
            and rs.get("evanescent_hh_counterterm_added") is False
            and rs.get("D11_evaluated") is False and rs.get("hard_stops_hold") is True):
        reasons.append("p17 release not accepted")
    for k, v in Q17.HARD_STOPS_P17.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p17 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r18 = subprocess.run([PY, "code/p5_calc/release_p18.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"p18_gate_before_{stage}", "release_rc": r18.returncode})
    if r18.returncode != 0:
        reasons.append(f"release_p18.py exit {r18.returncode}: {r18.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "certificates" / "P18_release.json").read_text())       # the p18 layer record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P18_release (p18 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q18.REVISION and rs.get("publication") == "accepted"
            and rs.get("quantum_inputs_evaluated") == "earned"
            and rs.get("release_claim_accepted") is True and rs.get("D11_matching_verified") is True
            and rs.get("D11_evaluated") is True and rs.get("hh_full_row_decoupling_proven") is True
            and rs.get("evanescent_hh_counterterm_added") is False
            and rs.get("projected_identity_verified") == "not_earned"
            and rs.get("projected_restoration_verified") == "not_earned"
            and rs.get("bulk_symmetry_restored") is False and rs.get("hard_stops_hold") is True):
        reasons.append("p18 release not accepted")
    for k, v in Q18.HARD_STOPS_P18.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p18 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r19 = subprocess.run([PY, "code/p5_calc/release_p19.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"p19_gate_before_{stage}", "release_rc": r19.returncode})
    if r19.returncode != 0:
        reasons.append(f"release_p19.py exit {r19.returncode}: {r19.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "certificates" / "P19_release.json").read_text())       # the p19 layer record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P19_release (p19 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q19.REVISION and rs.get("publication") == "accepted"       # I1: fail closed
            and rs.get("release_claim_accepted") is True and rs.get("quantum_inputs_evaluated") == "earned"
            and rs.get("projected_defect_computed") == "earned"
            and rs.get("bulk_symmetry_restored") is False and rs.get("symmetry_restored") is False
            and rs.get("O1_closure") == "NOT_CLOSED" and rs.get("hard_stops_hold") is True
            and (rs.get("projected_restoration_verified") != "earned" or rs.get("projected_identity_verified") == "earned")):
        reasons.append("p19 release not accepted")
    for k, v in Q19.HARD_STOPS_P19.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p19 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r20 = subprocess.run([PY, "code/p5_calc/release_p20.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"p20_gate_before_{stage}", "release_rc": r20.returncode})
    if r20.returncode != 0:
        reasons.append(f"release_p20.py exit {r20.returncode}: {r20.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "certificates" / "P20_release.json").read_text())       # the p20 layer record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P20_release (p20 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q20.REVISION and rs.get("publication") == "accepted"
            and rs.get("release_claim_accepted") is True and rs.get("quantum_inputs_evaluated") == "earned"
            and rs.get("projected_defect_computed") == "earned"
            and rs.get("bulk_symmetry_restored") is False and rs.get("symmetry_restored") is False
            and rs.get("O1_closure") == "NOT_CLOSED" and rs.get("hard_stops_hold") is True
            and rs.get("retraction_check", {}).get("hits") == {}
            and (rs.get("projected_restoration_verified") != "earned" or rs.get("projected_identity_verified") == "earned")):
        reasons.append("p20 release not accepted")
    for k, v in Q20.HARD_STOPS_P20.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p20 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r21 = subprocess.run([PY, "code/p5_calc/release_p21.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    LOG.append({"stage": f"p21_gate_before_{stage}", "release_rc": r21.returncode})
    if r21.returncode != 0:
        reasons.append(f"release_p21.py exit {r21.returncode}: {r21.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "certificates" / "P21_release.json").read_text())       # the p21 layer record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P21_release (p21 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q21.REVISION and rs.get("publication") == "accepted"
            and rs.get("release_claim_accepted") is True and rs.get("quantum_inputs_evaluated") == "earned"
            and rs.get("D11_absolute_pin_verified") == "earned" and rs.get("bulk_symmetry_restored") is False
            and rs.get("symmetry_restored") is False and rs.get("O1_closure") == "NOT_CLOSED"
            and rs.get("hard_stops_hold") is True and rs.get("lower_layers", {}).get("rechecked_live") is True
            and rs.get("change_log_vs_p20", {}).get("undisclosed_package_changes") == []):
        reasons.append("p21 release not accepted")
    for k, v in Q21.HARD_STOPS_P21.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p21 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r22 = subprocess.run([PY, "code/p5_calc/release_p22.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=1800)
    LOG.append({"stage": f"p22_gate_before_{stage}", "release_rc": r22.returncode})
    if r22.returncode != 0:
        reasons.append(f"release_p22.py exit {r22.returncode}: {r22.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "certificates" / "P22_release.json").read_text())       # the p22 layer record
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"P22_release (p22 layer record) unreadable: {exc}")
    if not (rs.get("revision") == Q22.REVISION and rs.get("publication") == "accepted"
            and rs.get("release_claim_accepted") is True and rs.get("quantum_inputs_evaluated") == "earned"
            and all(rs.get(k) == "earned" for k in Q22.EARNABLE_P22) and rs.get("bulk_symmetry_restored") is False
            and rs.get("symmetry_restored") is False and rs.get("O1_closure") == "NOT_CLOSED"
            and rs.get("hard_stops_hold") is True and rs.get("change_log_vs_p21", {}).get("undisclosed_changes") == []):
        reasons.append("p22 release not accepted")
    for k, v in Q22.HARD_STOPS_P22.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p22 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    r23 = subprocess.run([PY, "code/p5_calc/release_p23.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=1800)
    LOG.append({"stage": f"p23_gate_before_{stage}", "release_rc": r23.returncode})
    if r23.returncode != 0:
        reasons.append(f"release_p23.py exit {r23.returncode}: {r23.stdout.strip()[-400:]}")
    try:
        rs = json.loads((ROOT / "RELEASE_STATUS.json").read_text())                     # the p23 status
    except Exception as exc:  # noqa: BLE001
        rs = {}
        reasons.append(f"RELEASE_STATUS unreadable: {exc}")
    if not (rs.get("revision") == QC.REVISION and rs.get("publication") == "accepted"
            and rs.get("release_claim_accepted") is True and all(rs.get(k) == "earned" for k in QC.EARNABLE_P23)
            and rs.get("bulk_symmetry_restored") is False and rs.get("symmetry_restored") is False
            and rs.get("O1_closure") == "NOT_CLOSED" and rs.get("hard_stops_hold") is True
            and rs.get("change_log_vs_p22", {}).get("undisclosed_changes") == []):
        reasons.append("p23 release not accepted")
    for k, v in QC.HARD_STOPS_P23.items():
        if rs.get("hard_stops", {}).get(k) != v:
            reasons.append(f"p23 hard stop violated: {k}={rs.get('hard_stops', {}).get(k)!r}")
    for c in ("P15_release.json", "P16_release.json", "P17_release.json", "P18_release.json", "P19_release.json",
              "P20_release.json", "P21_release.json", "P22_release.json", f"{QC.CERT_PREFIX}_release.json"):
        if not (ROOT / "certificates" / c).exists():
            reasons.append(f"release certificate absent: {c}")
    for f in sorted(list((ROOT / "certificates").glob("P[12][0-9]_*.json")) + list((ROOT / "ledgers").glob("P[12][0-9]_*.json"))):
        try:
            bad = certio.invariant_violations(json.loads(f.read_text()))
        except Exception as exc:  # noqa: BLE001
            bad = [f"unreadable: {exc}"]
        reasons += [f"{f.name}:{b}" for b in bad]
    if stage in ("zip", "manifest"):
        pi = ROOT / "build" / "p14" / "pdf_inputs.json"
        if not pi.exists():
            reasons.append("pdf_inputs.json absent (PDFs not built by this pipeline)")
        else:
            rec = json.loads(pi.read_text())
            for rel, h in rec["listed"].items():
                if not (ROOT / rel).exists() or file_sha(rel) != h:
                    reasons.append(f"appendix listing no longer equals file: {rel}")
            for st in PDF_STEMS:
                f = MS / (st + ".pdf")
                if not f.exists() or sha(f) != rec["pdfs"].get(st):
                    reasons.append(f"pdf missing or not the gated build output: {st}")
        rb = ROOT / "build" / "p14" / "pdf_readback.json"
        if not rb.exists() or not json.loads(rb.read_text()).get("pass"):
            reasons.append("pdf readback absent or failed")
    if stage == "manifest":
        reasons += [f"zip_not_current:{b}" for b in zips_current()[:20]]
        if rs.get("author_rebuild_passed") is True:     # the flag must refer to exactly the zip being published
            rep = json.loads((ROOT / QC.AUTHOR_REPORT).read_text())
            if (DIST / SRC_ZIP).exists() and rep.get("source_zip_sha256") != sha(DIST / SRC_ZIP):
                reasons.append("author_rebuild_passed refers to a different source-only zip")
    return reasons


def _text(pdf):
    return subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout


# F4 (p16): value blocks read back from the PDFs in addition to the residual records.  For each certificate below, the
# ordered list of `"key": value` snippets (exactly as serialized in the file) must occur IN ORDER inside that
# certificate's typeset listing slice, after footers ("<VERSION_LABEL> | page N") and wrap markers are stripped.
VALUE_BLOCKS = {
    "certificates/P15_D13.json": ("result", ("structure", "A_exact_d_times_MB", "UV_pole", "MSbar_finite",
                                             "nonlocal_coefficient_of_L", "local_polynomial")),
    "certificates/P15_batchA.json": ("graphs", ("graph", "kappa_order", "prefactor", "status", "finite_part")),
    "certificates/P16_batchC.json": ("graphs.*.result", ("evanescent", "A_exact_d_times_MB", "UV_pole", "MSbar_finite",
                                                         "nonlocal_coefficient_of_L", "local_polynomial")),
    "certificates/P16_E2_evanescent.json": ("", ("outcome", "E2_status", "D13_slot_contribution", "E2_decoupling_proven")),
    "certificates/P17_hh_slot.json": ("", ("verdict", "status", "surviving_evanescent_structures_in_slot",
                                           "decoupling_proven")),
    "certificates/P18_D11_M2.json": ("", ("verdict", "D11_matching_verified")),
    "certificates/P18_D11.json": ("result", ("evanescent", "A_exact_d_times_MB", "UV_pole", "MSbar_finite",
                                             "nonlocal_coefficient_of_L", "local_polynomial")),
    "certificates/P18_hh_slot.json": ("", ("verdict", "decoupling_proven_full_row", "surviving_evanescent_structures_in_slot",
                                           "D11_reopens_evanescent_question", "quantum_inputs_evaluated")),
    "certificates/P19_defect.json": ("", ("defect_zero_exact_in_d", "quotient_coordinates", "D_cap_ker_sigma0",
                                          "projected_defect_computed", "projected_identity_verified",
                                          "projected_restoration_verified", "bulk_symmetry_restored")),
    "certificates/P20_D11_pin.json": ("", ("c2_spin2", "c0_spin0s", "ratio_c0_over_c2", "ratio_pin_status",
                                           "absolute_pin_status", "D11_ratio_pin_verified",
                                           "D11_absolute_pin_verified")),
    "certificates/P22_evanescent.json": ("", ("evanescent_counterterm_earned", "EV_M2_status", "EV_CT_status")),
    "certificates/P23_O1_scope.json": ("", ("O1_closure_status", "P6_entry_n_graphs", "one_point_n_graphs",
                                                    "O1_closable_in_XVI_P")),
}
FOOTER_RE = re.compile(r"XVI-P p\d+[a-z]? \| page \d+")
FOOTER_LINE_RE = re.compile(r"^XVI-P p\d+[a-z]? \| page \d+$", re.M)     # a footer is a line of its own


def _snip(k, v):
    return json.dumps(k) + ": " + json.dumps(v)


def value_snippets(root, rel):
    """Ordered `"key": value` snippets of the value block of one certificate (file order)."""
    path, keys = VALUE_BLOCKS[rel]
    obj = json.loads((Path(root) / rel).read_text())
    nodes = [obj]
    for part in [x for x in path.split(".") if x]:
        nodes = [v for n in nodes for v in (n.values() if part == "*" else [n[part]])]
    out = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in keys and not isinstance(v, (dict, list)):
                    if not (isinstance(v, str) and (not v.isascii() or "'" in v or "`" in v)):
                        out.append(_snip(k, v))     # typographic-quote / non-ASCII values are not read back
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for n in nodes:
        walk(n)
    return out


def _squash(t):
    return re.sub(r"\s+", "", t.replace("+>", ""))


def readback_values(text, root, rel, slice_text):
    """True iff every snippet of rel occurs in order in slice_text (footers/wrap markers/whitespace removed)."""
    src = _squash((Path(root) / rel).read_text())
    snips = value_snippets(root, rel)
    missing_in_file = [x for x in snips if _squash(x) not in src]
    t = _squash(FOOTER_RE.sub(" ", slice_text))
    pos, miss = 0, []
    for x in snips:
        i = t.find(_squash(x), pos)
        if i < 0:
            miss.append(x)
        else:
            pos = i + len(_squash(x))
    return {"snippets": len(snips), "not_in_order_in_pdf": miss[:5], "n_missing": len(miss),
            "builder_error_not_in_file": missing_in_file[:5],
            "pass": bool(snips) and not miss and not missing_in_file}


def readback_compare(root=None):
    """Read the typeset residual records back from the appendix and combined PDFs and compare with the files
    (pure: no side effects; used by pdf_readback and by tools/rebuild_from_source.py)."""
    root = Path(root) if root else ROOT
    exp_q, exp_z = [], []
    for rel in listed_files():
        if rel.endswith(".json"):
            for _, rec in certio.residual_records(json.loads((root / rel).read_text())):
                exp_q.append(rec["Q_terms"])
                exp_z.append(bool(rec["Q_identically_zero"]))
    out = {"expected_records": len(exp_q), "expected_values": exp_q}
    ok = True
    n = len(LISTINGS)
    for st in ("XVI-P-appendix", "XVI-P"):
        raw = _text(root / "manuscript" / (st + ".pdf"))
        footers = FOOTER_LINE_RE.findall(raw)
        pages = pdf_pages(root / "manuscript" / (st + ".pdf"))
        foot = {"pages": pages, "footers": len(footers), "labels": sorted({f.rsplit(" | ", 1)[0] for f in footers}),
                "expected_label": QC.VERSION_LABEL}
        foot["pass"] = foot["footers"] == pages and foot["labels"] == [QC.VERSION_LABEL]
        t = re.sub(r"\s+", " ", raw)
        # scope: only the typeset certificate/ledger/export JSON listings (sliced by the listing markers)
        slices, pos, missing, vals = [], 0, [], {}
        for i, (_, rel) in enumerate(LISTINGS, 1):
            a = t.find(listing_marker(i, n), pos)
            if a < 0:
                missing.append(rel)
                continue
            b = t.find(listing_marker(i + 1, n), a) if i < n else t.find("Archival material", a)
            b = len(t) if b < 0 else b
            if rel.endswith(".json"):
                slices.append(t[a:b])
            if rel in VALUE_BLOCKS:
                vals[rel] = readback_values(t, root, rel, t[a:b])
            pos = a
        for rel in VALUE_BLOCKS:
            vals.setdefault(rel, {"pass": False, "reason": "listing not found"})
        t = " ".join(slices)
        got_q, bad = [], []
        for m in re.finditer(r'"Q_terms": ?\[([^\]]*)\]', t):
            body = m.group(1)
            if re.search(r"[A-Za-z_(]", body):
                continue          # source code, not a certificate value
            if not re.fullmatch(r" ?\d+(, ?\d+)* ?", body):
                bad.append(body)
                continue
            got_q.append([int(x) for x in body.split(",")])
        got_z = [x == "true" for x in re.findall(r'"Q_identically_zero": ?(true|false)', t)]
        res = {"Q_terms_equal": got_q == exp_q, "zero_flags_equal": got_z == exp_z, "malformed": bad,
               "read": len(got_q), "read_values": got_q, "missing_listing_markers": missing}
        res["value_blocks"] = vals
        res["footer"] = foot
        res["pass"] = (res["Q_terms_equal"] and res["zero_flags_equal"] and not bad and not missing
                       and all(v["pass"] for v in vals.values()) and foot["pass"])
        out[st] = res
        ok &= res["pass"]
    out["pass"] = ok
    return out


def pdf_readback():
    out = readback_compare()
    (ROOT / "build" / "p14" / "pdf_readback.json").write_text(json.dumps(out, indent=1) + "\n")
    print("[pdf readback]", json.dumps({k: ({"pass": v["pass"], "values": {r: x["pass"] for r, x in v.get("value_blocks", {}).items()},
                                             "footer": v.get("footer")} if isinstance(v, dict) else v) for k, v in out.items()
                                        if k != "expected_values"}), flush=True)
    if not out["pass"]:
        reject_artifacts("pdf_readback", [f"pdf readback mismatch: {out}"])
    return out


def record_pdf_inputs():
    rec = {"listed": {rel: file_sha(rel) for rel in listed_files()},
           "pdfs": {st: sha(MS / (st + ".pdf")) for st in PDF_STEMS}}
    (ROOT / "build" / "p14" / "pdf_inputs.json").write_text(json.dumps(rec, indent=1) + "\n")


def main():
    args = sys.argv[1:]
    t0 = time.time()
    assert inherited.sha(inherited.resolve("XVI-M.tex")) == C.XVI_M_PIN
    for sub in ("certificates", "exports", "ledgers", "dist", "manuscript/body", "build/p14"):   # absent in a source-only tree
        (ROOT / sub).mkdir(parents=True, exist_ok=True)
    stages = ["quartic", "brst", "source", "gauge", "ch", "master", "matterloop", "p5entry", "release", "dossier",
              "p15calc", "release15", "p16calc", "release16", "p17calc", "release17", "p18calc", "release18", "p19calc", "release19", "p20calc", "release20", "release21", "p22calc", "release22", "p23calc", "release23", "tests", "pdf", "zip",
              "manifest"]
    (ROOT / "build" / "p14").mkdir(parents=True, exist_ok=True)
    start = args[args.index("--from-stage") + 1] if "--from-stage" in args else "quartic"
    run = stages[stages.index(start):]
    if "quartic" in run:
        clean_fresh()
        step("conventions", [PY, "-c", "import sys; sys.path.insert(0,'code/classical'); import conventions as C; print(C.REVISION)"])
        step("inherited_pins", [PY, "code/classical/inherited.py"])
        step("boundary_identity_C3", [PY, "code/classical/boundary_identity.py"])
        step("quartic", [PY, "code/classical/quartic.py"] + (["build/p14/ell_cache.pkl"] if "--from-cache" in args else []))
    if "brst" in run:
        step("brst_transformations", [PY, "code/classical/brst_from_geometry.py"])
    if "source" in run:
        step("source_action", [PY, "code/classical/source_action.py"])
    if "gauge" in run:
        step("gauge_map", [PY, "code/classical/gauge_fixing_map.py"])
    if "ch" in run:
        step("ch_audit_and_graphs", [PY, "code/p4_classical/ch_source_audit.py"])
    if "master" in run:
        step("master", [PY, "code/classical/master_kappa2.py"])
    if "matterloop" in run:     # regenerates the inherited O5 matter-loop records read by the D11 matching note
        step("matter_loop_gates", [PY, "tests/test_matter_loop_gates.py"])
    if "p5entry" in run:        # P.5 entry contract: symbolic rules and definitions only, NO loop evaluation
        step("p5_amplitude_rules", [PY, "code/p5_entry/amplitude_rules.py"])
        step("p5_dred_rules", [PY, "code/p5_entry/dred.py"])          # p14r: operational DRED (reads the exports)
        step("p5_counterterm_domain", [PY, "code/p5_entry/counterterm_domain.py"])
        step("p5_quantum_object", [PY, "code/p5_entry/quantum_object.py"])
        step("p5_prescription_d11", [PY, "code/p5_entry/prescription_d11.py"])
    if "release" in run:
        r = subprocess.run([PY, "code/p5_entry/release_p14.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate", "rc": r.returncode})
        print(f"[release_gate] rc={r.returncode}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release", ["release_p14.py rejected publication", r.stdout[-2000:]])
    if "dossier" in run:
        r = subprocess.run([PY, "code/p5_entry/dossier_p14.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "dossier", "rc": r.returncode})
        print(f"[dossier] rc={r.returncode} {r.stdout.strip()}", flush=True)
        if r.returncode != 0:
            reject_artifacts("dossier", ["dossier links unresolved", r.stdout[-2000:]])
    if "p15calc" in run:        # p15: FIRST P.5 CALCULATION on the p14r contract (Batch A, Batch B = D13)
        step("p15_integral_library", [PY, "code/p5_calc/integrals.py"])
        step("p15_batchA", [PY, "code/p5_calc/batchA.py"])
        step("p15_D13", [PY, "code/p5_calc/d13.py"])
    if "release15" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p15.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p15", "rc": r.returncode})
        print(f"[release_gate_p15] rc={r.returncode}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release15", ["release_p15.py rejected publication", r.stdout[-2000:]])
    if "p16calc" in run:        # p16: E2 evanescent decoupling proof (D13 ch slot), Batch C (D01, D03; covariant route)
        step("p16_E2_evanescent", [PY, "code/p5_calc/e2_evanescent.py"])
        step("p16_batchC", [PY, "code/p5_calc/batchC.py"], timeout=5400)
    if "release16" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p16.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p16", "rc": r.returncode})
        print(f"[release_gate_p16] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release16", ["release_p16.py rejected publication", r.stdout[-2000:]])
    if "p17calc" in run:        # p17: D01/D03 evanescent poles vs the ch-projected slot (decoupling proof)
        step("p17_hh_slot", [PY, "code/p5_calc/hh_slot.py"], timeout=3600)
    if "release17" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p17.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p17", "rc": r.returncode})
        print(f"[release_gate_p17] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release17", ["release_p17.py rejected publication", r.stdout[-2000:]])
    if "p18calc" in run:        # p18: M2 discharge, D11 evaluation, full hh slot
        step("p18_d11", [PY, "code/p5_calc/d11.py"], timeout=3600)
    if "release18" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p18.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p18", "rc": r.returncode})
        print(f"[release_gate_p18] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release18", ["release_p18.py rejected publication", r.stdout[-2000:]])
    if "p19calc" in run:        # p19: projected ch-identity defect, Route C / Route G, counterterm solve
        step("p19_defect", [PY, "code/p5_calc/defect.py"], timeout=3600)
    if "release19" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p19.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p19", "rc": r.returncode})
        print(f"[release_gate_p19] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release19", ["release_p19.py rejected publication", r.stdout[-2000:]])
    if "p20calc" in run:        # p20: D11 normalisation pin (trace-anomaly spin-2 / spin-0 ratio)
        step("p20_d11_pin", [PY, "code/p5_calc/d11_pin.py"], timeout=1800)
    if "release20" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p20.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p20", "rc": r.returncode})
        print(f"[release_gate_p20] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release20", ["release_p20.py rejected publication", r.stdout[-2000:]])
    if "release21" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p21.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p21", "rc": r.returncode})
        print(f"[release_gate_p21] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release21", ["release_p21.py rejected publication", r.stdout[-2000:]])
    if "p22calc" in run:        # p22: EV-M2 and the evanescent counterterms
        step("p22_evanescent", [PY, "code/p5_calc/evanescent.py"], timeout=3600)
    if "release22" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p22.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p22", "rc": r.returncode})
        print(f"[release_gate_p22] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release22", ["release_p22.py rejected publication", r.stdout[-2000:]])
    if "p23calc" in run:        # p23: O.1 requirement, one-loop power counting, P.6 entry inventory
        step("p23_power_counting", [PY, "code/p5_calc/power_counting.py"], timeout=3600)
    if "release23" in run:
        r = subprocess.run([PY, "code/p5_calc/release_p23.py"], cwd=str(ROOT), capture_output=True, text=True)
        LOG.append({"stage": "release_gate_p23", "rc": r.returncode})
        print(f"[release_gate_p23] rc={r.returncode} {r.stdout.strip()[-600:]}", flush=True)
        if r.returncode != 0:
            reject_artifacts("release23", ["release_p23.py rejected publication", r.stdout[-2000:]])
    if "tests" in run and "--skip-tests" not in args:
        shutil.rmtree(ROOT / "build" / "p14" / "test_results", ignore_errors=True)
        r = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=build/p14/junit.xml",
                            "tests/test_p14.py", "tests/test_p15.py", "tests/test_p16.py", "tests/test_p17.py", "tests/test_p18.py", "tests/test_p19.py", "tests/test_p20.py",
                            "tests/test_p21.py", "tests/test_p22.py", "tests/test_p23.py", "tests/test_inverse_metric_series.py"],
                           cwd=str(ROOT), capture_output=True, text=True)
        (ROOT / "build" / "p14" / "pytest_summary.txt").write_text(r.stdout.strip().splitlines()[-1] + "\n")
        print("[tests]", r.stdout.strip().splitlines()[-1], json.dumps(junit_groups()), flush=True)
        if r.returncode != 0:
            print(r.stdout[-5000:])
            raise SystemExit("tests failed")
    collect_tests()
    if "pdf" in run:
        publication_gate("pdf")
        names = make_listings()
        appendix_body(names)
        write_fronts()
        build_pdfs()
        check_listings_current()
        record_pdf_inputs()
        pdf_readback()
    if "zip" in run:
        publication_gate("zip")
        (ROOT / "RELEASE_MANIFEST_EXTERNAL.txt").unlink(missing_ok=True)
        make_zips()
    if "manifest" in run:
        publication_gate("manifest")
        v = write_manifest()
        top = sync_top()
        shutil.rmtree(STALE, ignore_errors=True)
        print(json.dumps({"manifest": v, "top": top}, indent=1))
    (ROOT / "build" / "p14" / "build_log.json").write_text(json.dumps({"log": LOG, "sec": round(time.time() - t0, 1)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
