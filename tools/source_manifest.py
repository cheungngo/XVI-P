#!/usr/bin/env python3
"""p14/p15/p16: the SOURCE set of XVI-P (single definition, used by the source-only zip, the rebuild entrypoint, the release
gate and the publication gate).

source = hand-written code/tools/tests, hand-written manuscript sources, provenance (pins + vendored inherited inputs),
         archival READMEs and archival notes typeset by the appendix, the reproducibility contract files, and the
         INHERITED DATA inputs listed (with sha256 pins) in reproducibility/inherited_data_pins.json.
Everything else in a built tree is generated (certificates P13_*/P14_*, RELEASE_STATUS, exports ell*/V4_grav/
ell4_conventions/P14_*, ledgers P13_*/P14_*, regenerated O5 matter-loop records, listings, appendix body, dossier and
summary tables, PDFs, zips, manifest, build/, caches; p15: certificates/ledgers P15_*, the P15 results table) and is
NOT in XVI-P-p15-source-only.zip.
p19: the p18 archive records are source as well (archival/p18/README.md, reference_values_p18.json, the p18 author
and independent rebuild reports and p18_source_files.json, the per-file base of the p19 change log).
p20: likewise the p19 archive records (archival/p19/README.md, reference_values_p19.json, the p19 author and
independent rebuild reports and p19_source_files.json, the per-file base of the p20 change log).
p21: likewise the p20 archive records (archival/p20/README.md, reference_values_p20.json, the p20 author and
independent rebuild reports and p20_source_files.json, the per-file base of the p21 change log).
p22: likewise the p21 archive records (archival/p21/README.md, reference_values_p21.json, the p21 author and
independent rebuild reports and p21_source_files.json, the per-file base of the p22 change log).
p18: the p17 archive records are source as well (archival/p17/README.md, reference_values_p17.json, the p17 author
and independent rebuild reports and p17_source_files.json, the per-file base of the p18 change log).
p17: the p16 archive records are source as well (archival/p16/README.md, reference_values_p16.json, the p16 author
and independent rebuild reports and p16_source_files.json, the per-file base of the p17 change log).
p16: the p15 archive records are source as well (archival/p15/README.md, reference_values_p15.json and the p15 author
and independent rebuild reports, byte-identical copies, pinned in p16_conventions.py); generated p16 outputs
(certificates/ledgers P16_*, the P16 results table) are NOT source.  The live reproducibility/*_p15.json files are NOT
p16 source and are never written by p16.
p15: the p14r archive records are source (archival/p14r/README.md, reference_values_p14r.json and the p14r author and
independent rebuild reports, byte-identical copies; the independent report is pinned in p15_conventions.py); the live
reproducibility/*_p14r.json files are NOT p15 source and are never written by p15.
p14: the p13 freeze inputs are source (archival/p13/reference_values_p13.json, archival/p13/frozen_p13_inputs.json,
archival/p13/reproducibility/*.json incl. the archived independent report); the reviewer's live
reproducibility/independent_rebuild_report.json and the p13 reproducibility/reference_values.json are NOT p14 source
(they are left untouched in the author tree; their archived copies are byte-identical).

Usage:  python3 tools/source_manifest.py [--list] [--tree-sha] [--zip OUT.zip] [--check-source-only]
"""
from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS_FILE = "reproducibility/inherited_data_pins.json"
REFERENCE_FILE = "reproducibility/reference_values_p23.json"
ZIP_NAME = "XVI-P-p23-source-only.zip"
ZIP_DATE = (2026, 10, 9, 0, 0, 0)

TOP_FILES = ("README.md", "REBUILD_INSTRUCTIONS.md")
GLOBS = ("code/**/*.py", "tools/**/*.py", "tests/**/*.py",
         "manuscript/preamble.tex", "manuscript/body/XVI-P-body.tex", "manuscript/notes/*.tex",
         "notes/*.tex", "provenance/**/*", "archival/*/README.md", "archival/p02_p09/notes/*.tex",
         "archival/p13/reference_values_p13.json", "archival/p13/frozen_p13_inputs.json",
         "archival/p13/reproducibility/independent_rebuild_report_p13.json",
         "archival/p13/reproducibility/author_rebuild_report_p13.json",
         "archival/p14r/reference_values_p14r.json",
         "archival/p14r/reproducibility/independent_rebuild_report_p14r.json",
         "archival/p14r/reproducibility/author_rebuild_report_p14r.json",
         "archival/p15/reference_values_p15.json",
         "archival/p15/reproducibility/independent_rebuild_report_p15.json",
         "archival/p15/reproducibility/author_rebuild_report_p15.json",
         "archival/p15/p15_source_files.json",
         "archival/p16/reference_values_p16.json",
         "archival/p16/reproducibility/independent_rebuild_report_p16.json",
         "archival/p16/reproducibility/author_rebuild_report_p16.json",
         "archival/p16/p16_source_files.json",
         "archival/p17/reference_values_p17.json",
         "archival/p17/reproducibility/independent_rebuild_report_p17.json",
         "archival/p17/reproducibility/author_rebuild_report_p17.json",
         "archival/p17/p17_source_files.json",
         "archival/p18/reference_values_p18.json",
         "archival/p18/reproducibility/independent_rebuild_report_p18.json",
         "archival/p18/reproducibility/author_rebuild_report_p18.json",
         "archival/p18/p18_source_files.json",
         "archival/p19/reference_values_p19.json",
         "archival/p19/reproducibility/independent_rebuild_report_p19.json",
         "archival/p19/reproducibility/author_rebuild_report_p19.json",
         "archival/p19/p19_source_files.json",
         "archival/p20/reference_values_p20.json",
         "archival/p20/reproducibility/independent_rebuild_report_p20.json",
         "archival/p20/reproducibility/author_rebuild_report_p20.json",
         "archival/p20/p20_source_files.json",
         "archival/p21/reference_values_p21.json",
         "archival/p21/reproducibility/independent_rebuild_report_p21.json",
         "archival/p21/reproducibility/author_rebuild_report_p21.json",
         "archival/p21/p21_source_files.json",
         "archival/p22/reference_values_p22.json",
         "archival/p22/reproducibility/independent_rebuild_report_p22.json",
         "archival/p22/reproducibility/author_rebuild_report_p22.json",
         "archival/p22/p22_source_files.json",
         "archival/p22/certificates/P22_evanescent.json",
         PINS_FILE, REFERENCE_FILE)
NEVER = ("__pycache__", ".pytest_cache")
NEVER_SUFFIX = (".pyc", ".pkl", ".aux", ".log", ".toc", ".out", ".pdf", ".zip")


def inherited_data(root=ROOT):
    f = Path(root) / PINS_FILE
    return json.loads(f.read_text())["files"] if f.exists() else {}


def source_files(root=ROOT):
    root = Path(root)
    out = set()
    for t in TOP_FILES:
        if (root / t).is_file():
            out.add(t)
    for g in GLOBS:
        for p in root.glob(g):
            if p.is_file():
                out.add(p.relative_to(root).as_posix())
    for rel in inherited_data(root):
        if (root / rel).is_file():
            out.add(rel)
    return sorted(r for r in out if not any(n in r.split("/") for n in NEVER) and not r.endswith(NEVER_SUFFIX))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree_sha(root=ROOT, exclude=()):
    """sha256 over the sorted 'relpath<TAB>sha256' lines of the source set (optionally excluding some paths)."""
    root = Path(root)
    lines = [f"{r}\t{sha(root / r)}" for r in source_files(root) if r not in exclude]
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def tree_sha_without_reference(root=ROOT):
    """Hash of everything except the reference-values file (which records this hash, so it cannot include itself)."""
    return tree_sha(root, exclude=(REFERENCE_FILE,))


def non_source_files(root=ROOT):
    """Files present in a tree that are not source (i.e. generated artifacts or caches)."""
    root = Path(root)
    src = set(source_files(root))
    extra = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            if rel not in src:
                extra.append(rel)
    return extra


def make_zip(out, root=ROOT):
    """Deterministic zip (sorted entries, fixed date and permissions) of the source set under XVI-P/."""
    root, out = Path(root), Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    files = source_files(root)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            info = zipfile.ZipInfo("XVI-P/" + rel, date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, (root / rel).read_bytes())
    return {"zip": out.name, "files": len(files), "bytes": out.stat().st_size, "sha256": sha(out)}


def zip_matches_tree(zp, root=ROOT):
    """[] if the zip holds exactly the current source set byte-for-byte; else a list of differences."""
    root = Path(root)
    bad = []
    try:
        zf = zipfile.ZipFile(zp)
    except (zipfile.BadZipFile, FileNotFoundError) as exc:
        return [f"{Path(zp).name}: {type(exc).__name__}"]
    with zf:
        names = {n.split("/", 1)[1]: n for n in zf.namelist()}
        src = set(source_files(root))
        bad += [f"missing_in_zip:{r}" for r in sorted(src - set(names))]
        bad += [f"not_source:{r}" for r in sorted(set(names) - src)]
        bad += [f"differs:{r}" for r in sorted(src & set(names)) if zf.read(names[r]) != (root / r).read_bytes()]
    return bad


XVIO_TREE = "provenance/XVI-O_o70_source_tree.json"


def check_xvio_provenance(root=ROOT):
    """The XVI-O (o70-sync) code and notes carried verbatim in this package (code/matter_loop/*.py, notes/*.tex)
    must match the sha256 list recorded in provenance/XVI-O_o70_source_tree.json."""
    root = Path(root)
    tree = json.loads((root / XVIO_TREE).read_text())
    out = {}
    for f in tree["files"]:
        p = root / f["path"]
        out[f["path"]] = {"pin": f["sha256"], "ok": p.is_file() and sha(p) == f["sha256"]}
    return out


def check_inherited_data(root=ROOT):
    """Every inherited data input is present and matches its sha256 pin."""
    root = Path(root)
    out = {}
    for rel, pin in inherited_data(root).items():
        p = root / rel
        out[rel] = {"pin": pin["sha256"], "present": p.is_file(),
                    "ok": p.is_file() and sha(p) == pin["sha256"]}
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--list" in a:
        print("\n".join(source_files()))
    if "--tree-sha" in a:
        print(json.dumps({"source_tree_sha256": tree_sha(), "without_reference": tree_sha_without_reference(),
                          "files": len(source_files())}))
    if "--check-source-only" in a:
        extra = non_source_files()
        print(json.dumps({"non_source_files": extra[:50], "count": len(extra)}))
        raise SystemExit(0 if not extra else 1)
    if "--zip" in a:
        print(json.dumps(make_zip(a[a.index("--zip") + 1])))
