#!/usr/bin/env python3
"""External manifest writer/verifier (written LAST; PDFs never embed their own hashes).

Machine-checkable lines:  FILE <relpath> pages=<n|-> bytes=<n> sha256=<hex>
verify(): recompute bytes + sha256 of every FILE line; any mismatch (stale hash) => fail.
"""
from __future__ import annotations
import hashlib, re, subprocess, sys
from pathlib import Path

LINE = re.compile(r"^FILE (\S+) pages=(\S+) bytes=(\d+) sha256=([0-9a-f]{64})$")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pdf_pages(p: Path):
    try:
        out = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        return int(m.group(1)) if m else None
    except FileNotFoundError:
        return None


def file_line(root: Path, rel: str) -> str:
    p = root / rel
    pages = pdf_pages(p) if p.suffix == ".pdf" else None
    return f"FILE {rel} pages={pages if pages is not None else '-'} bytes={p.stat().st_size} sha256={sha(p)}"


def verify(manifest: Path, root: Path) -> dict:
    bad, n = [], 0
    for ln in manifest.read_text().splitlines():
        m = LINE.match(ln.strip())
        if not m:
            continue
        n += 1
        rel, _, b, h = m.groups()
        p = root / rel
        if not p.exists():
            bad.append(f"missing {rel}")
        elif p.stat().st_size != int(b) or sha(p) != h:
            bad.append(f"stale {rel}")
    return {"entries": n, "failures": bad, "pass": n > 0 and not bad}


if __name__ == "__main__":
    r = verify(Path(sys.argv[1]), Path(sys.argv[2]))
    print(r)
    raise SystemExit(0 if r["pass"] else 1)
