#!/usr/bin/env python3
"""p13: inherited (read-only) external inputs, each pinned by sha256.

Every file this package reads from OUTSIDE its own tree is listed here.  resolve(name) returns a path whose sha256
equals the pin, or raises.  Search order (XVIP_INHERITED = auto | workspace | vendored, default auto):
  workspace : the sibling landmark tree on the author's machine (e.g. /workspace/XVI-M.tex);
  vendored  : the byte-identical copy shipped inside this package under provenance/ (so a clean environment that has
              only XVI-P-source-only.zip can rebuild).
A pin mismatch is never tolerated in either location.  Certificates record only the logical name and the sha256,
never the absolute path, so certificate contents do not depend on where the rebuild runs.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PINS = {
    "XVI-M.tex": {
        "sha256": "41aa109935f40ddee3109de62c46329c189b5408007970cc90ed5611dc4739ea",
        "workspace": "/workspace/XVI-M.tex",
        "vendored": "provenance/XVI-M.tex",
        "used_for": "landmark pin (read-only; XVI-M supplies M.4 selected-graph data, not premises of P.3/P.4)",
    },
    "XVI-N-r10/code/prep/grav_density.py": {
        "sha256": "855ab9e2124acf66f4440b2f1745470acf137caf77dc7bd538d13b7c878ea8e0",
        "workspace": "/workspace/XVI-N-r10/code/prep/grav_density.py",
        "vendored": "provenance/inherited/XVI-N-r10/code/prep/grav_density.py",
        "used_for": "C5/C6 regression references: XII-C ell_3 (ell3_and_curvature) and XI-A Fierz-Pauli (FP_density)",
    },
}


class PinError(RuntimeError):
    pass


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def candidates(name, mode=None):
    mode = mode or os.environ.get("XVIP_INHERITED", "auto")
    pin = PINS[name]
    ws, vd = Path(pin["workspace"]), ROOT / pin["vendored"]
    return {"workspace": [ws], "vendored": [vd], "auto": [ws, vd]}[mode]


def resolve(name, mode=None):
    """Path of a pinned inherited input (sha256 verified)."""
    pin = PINS[name]
    tried = []
    for p in candidates(name, mode):
        if p.exists():
            h = sha(p)
            if h == pin["sha256"]:
                return p
            tried.append(f"{p}: sha256 {h} != pin")
        else:
            tried.append(f"{p}: absent")
    raise PinError(f"inherited input {name} not available with pinned sha256 {pin['sha256']}: " + "; ".join(tried))


def verify_all(mode=None):
    """{name: {pin, ok, location, sha256}} without absolute paths in the location field."""
    out = {}
    for name, pin in PINS.items():
        try:
            p = resolve(name, mode)
            loc = "vendored" if Path(p).resolve() == (ROOT / pin["vendored"]).resolve() else "workspace"
            out[name] = {"sha256": pin["sha256"], "ok": True, "location": loc}
        except PinError as exc:
            out[name] = {"sha256": pin["sha256"], "ok": False, "error": str(exc)}
    # the vendored copies themselves must also match (the source-only zip ships them)
    for name, pin in PINS.items():
        vd = ROOT / pin["vendored"]
        out[name]["vendored_copy_matches_pin"] = vd.exists() and sha(vd) == pin["sha256"]
    return out


if __name__ == "__main__":
    import json
    r = verify_all()
    print(json.dumps(r, indent=1))
    raise SystemExit(0 if all(v["ok"] and v["vendored_copy_matches_pin"] for v in r.values()) else 1)
