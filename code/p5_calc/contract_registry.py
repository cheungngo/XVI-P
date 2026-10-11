#!/usr/bin/env python3
"""XVI-P p22: registry of DISCLOSED contract revisions after p18 (consulted by the p19, p20, p21 layer gates and the p22
gate).  The only post-p18 contract revision is p22's runtime d guard: code/p5_entry/dred.py = the p18 dred.py with ONE
delimited block inserted (markers below).  dred_revision() strips the block and requires the remainder to be byte-identical
to the p18 release (P18_DRED_SHA256): the p18 contract text is untouched, the revision is purely additive.  The p22 gate
additionally pins the exact sha of the revised file (p22_conventions.P22_DRED_SHA256)."""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRED = "code/p5_entry/dred.py"
P18_DRED_SHA256 = "14c11a512c1609c9f9a7829dcb68e71a94c8ac3d38497e2dcac110a1b8d5e81c"
BEGIN = ("\n\n# ======================================================================================= "
         "p22 CONTRACT REVISION: runtime d guard\n")
END = "# ======================================================================================= end p22 runtime d guard\n"
BEGIN23 = ("\n\n# ======================================================================================= "
           "p23 CONTRACT REVISION: polynomial-domain refusal\n")
END23 = "# ======================================================================================= end p23 polynomial-domain refusal\n"
P22_BLOCK_SHA256 = "9d2bbe3e77030115d0c302da3895e1b4615fe8c0aa8ba9a5b5dbf02b640482ad"   # the p22 block as released


def p22_block_unchanged(root=ROOT):
    t = (Path(root) / DRED).read_text()
    if t.count(BEGIN) != 1 or t.count(END) != 1:
        return False
    return hashlib.sha256(t[t.index(BEGIN):t.index(END) + len(END)].encode()).hexdigest() == P22_BLOCK_SHA256


def p23_registered(root=ROOT):
    """the p23 contract state: p18 core byte-identical, p22 block byte-identical to its release, p23 block present."""
    r = dred_revision(root)
    return bool(r["ok"] and "p23 polynomial-domain refusal" in r.get("registered_blocks", []) and p22_block_unchanged(root))


REVISED_CONTRACT_FILES = {DRED: "p22 contract revision: runtime d guard (additive block)"}


def dred_revision(root=ROOT):
    raw = (Path(root) / DRED).read_bytes()
    cur = hashlib.sha256(raw).hexdigest()
    if cur == P18_DRED_SHA256:
        return {"state": "p18", "ok": True, "sha256": cur}
    t = raw.decode()
    blocks = ["p22 runtime d guard"]
    if t.count(BEGIN23) == 1 and t.count(END23) == 1 and t.index(BEGIN23) < t.index(END23) and t.endswith(END23):
        t = t[:t.index(BEGIN23)]                 # p23 block appended at the end of the file (after the p22 END)
        blocks.append("p23 polynomial-domain refusal")
    elif t.count(BEGIN23) or t.count(END23):
        return {"state": "unregistered", "ok": False, "sha256": cur}
    if t.count(BEGIN) != 1 or t.count(END) != 1 or t.index(BEGIN) > t.index(END):
        return {"state": "unregistered", "ok": False, "sha256": cur}
    core = t[:t.index(BEGIN)] + t[t.index(END) + len(END):]
    ok = hashlib.sha256(core.encode()).hexdigest() == P18_DRED_SHA256
    # compatibility key: "p18 + p22 guard block" = p18 core byte-identical + the p22 block + any LATER registered
    # block listed in registered_blocks (p23: polynomial-domain refusal)
    return {"state": "p18 + p22 guard block" if ok else "unregistered", "ok": ok, "sha256": cur,
            "p18_core_byte_identical": ok, "registered_blocks": blocks if ok else []}


def scan_view(path, root=ROOT):
    """Older-layer static scans (p17..p20 tests) review the p18 CONTRACT text: for the registered revised dred.py they
    are handed the p18 core (block stripped, byte-identical to the p18 release) in a temporary mirror root.  The p22
    guard block itself is covered by the p22 runtime probe and the p21 allow-list scan (scan4, p22 allow-lists)."""
    import tempfile
    path, root = Path(path), Path(root)
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return path, root
    if rel != DRED or dred_revision(root)["state"] != "p18 + p22 guard block":
        return path, root
    t = path.read_text()
    if BEGIN23 in t:
        t = t[:t.index(BEGIN23)]
    core = t[:t.index(BEGIN)] + t[t.index(END) + len(END):]
    tmp = Path(tempfile.mkdtemp(prefix="p22scanview_"))
    (tmp / DRED).parent.mkdir(parents=True)
    (tmp / DRED).write_text(core)
    return tmp / DRED, tmp


def registered_contract_change(rel, root=ROOT):
    """True iff `rel` is a contract file whose change is a registered (disclosed) revision in its current state."""
    return rel == DRED and dred_revision(root)["state"] == "p18 + p22 guard block"


# p18-layer gate revised in p22 (pinned byte-identically by release_p19.p18_layer): exact sha of the revised file
LAYER_FILE_REVISIONS_P22 = {"code/p5_calc/release_p18.py": "f2e8743b4902b4304679c68b994dfc9c6df4a0b769827eb2693a72495a4e9c5b"}


def layer_file_ok(rel, cur_sha, pinned_sha):
    return cur_sha == pinned_sha or LAYER_FILE_REVISIONS_P22.get(rel) == cur_sha


# files revised in p22 (disclosed; listed in p22_conventions.DISCLOSED_REVISIONS_P22 with reasons and pinned there by sha);
# the earlier-layer change logs (release_p21 vs the p20 zip) treat exactly these as disclosed
P22_REVISED_FILES = (
    "code/p5_entry/dred.py", "code/p5_calc/release_p18.py", "code/p5_calc/release_p19.py",
    "code/p5_calc/release_p20.py", "code/p5_calc/release_p21.py",
    "tests/test_p14.py", "tests/test_p16.py", "tests/test_p17.py", "tests/test_p18.py", "tests/test_p19.py",
    "tests/test_p20.py", "tests/test_p21.py",
)


# p23 (disclosed in p23_conventions.DISCLOSED_REVISIONS_P23, exact shas pinned by the p23 gate): files changed or added
# in p23 -- earlier layer gates/tests accept them as later registered revisions
P23_REVISED_FILES = (
    "code/p5_entry/dred.py", "code/p5_calc/contract_registry.py", "code/p5_calc/release_p21.py",
    "code/p5_calc/release_p22.py",
    "tests/test_p14.py", "tests/test_p21.py", "tests/test_p22.py",
    "tools/build.py", "tools/source_manifest.py", "tools/rebuild_from_source.py",
    "README.md", "REBUILD_INSTRUCTIONS.md", "manuscript/body/XVI-P-body.tex",
)
P23_ADDED_FILES = ("code/p5_calc/power_counting.py", "code/p5_calc/p23_conventions.py", "code/p5_calc/release_p23.py",
                   "tests/test_p23.py", "manuscript/notes/P23_O1_scope.tex")
P23_ADDED_PREFIXES = ("archival/p22/", "provenance/XVI-O/")


P23_GENERATED = ("reproducibility/reference_values_p23.json",)   # generated reference (exempt in the p23 gate)


def p23_disclosed(rel):
    return (rel in P23_REVISED_FILES or rel in P23_ADDED_FILES or rel in P23_GENERATED
            or rel.startswith(P23_ADDED_PREFIXES))


def p22_revised(rel):
    """revised by a LATER registered release (p22, or p23)."""
    return rel in P22_REVISED_FILES or p23_disclosed(rel)
