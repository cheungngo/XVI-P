#!/usr/bin/env python3
"""p12: certificate serialization + residual-record invariants (shared by every certificate writer and the rel
  +> ease gate).

Why (p12 root cause): the p11 appendix typeset multi-line JSON arrays; a page break inside a Q_terms array
put the footer page number ("12", "29") between two array elements, and a plain text extraction of the PDF rea
  +> d
the kappa0 quartic counts as 0,0,120,0 and the kappa1 master counts as 290,0,0,0.  The certificate files thems
  +> elves were correct.  p12 therefore
  * writes every list of scalars on ONE line (cannot be split by a page break),
  * enforces, before serialization, the invariant  Q_identically_zero == all(n == 0 for n in Q_terms)
    on every residual record (any dict carrying both keys), and
  * provides the acceptance and cross-certificate checks used by quartic.py, master_kappa2.py and release.py.
"""
from __future__ import annotations
import json
from pathlib import Path

ORDERS = ("kappa0", "kappa1", "kappa2")
REC_KEYS = ("W_terms", "Q_terms", "Q_identically_zero", "s0_piece_alone_Q_terms")


class CertificateInvariantError(AssertionError):
    pass


def _scalar(x):
    return x is None or isinstance(x, (bool, int, float, str))


def _enc(o, ind, step=2):
    pad, pad2 = " " * ind, " " * (ind + step)
    if isinstance(o, dict):
        if not o:
            return "{}"
        items = [f"{pad2}{json.dumps(str(k))}: {_enc(v, ind + step)}" for k, v in o.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(o, (list, tuple)):
        if not o:
            return "[]"
        if all(_scalar(x) for x in o):
            return "[" + ", ".join(json.dumps(x) for x in o) + "]"
        return "[\n" + ",\n".join(pad2 + _enc(x, ind + step) for x in o) + "\n" + pad + "]"
    if _scalar(o):
        return json.dumps(o)
    return json.dumps(str(o))


def residual_records(obj, path=""):
    """Yield (path, record) for every dict carrying both Q_terms and Q_identically_zero."""
    if isinstance(obj, dict):
        if "Q_terms" in obj and "Q_identically_zero" in obj:
            yield path, obj
        for k, v in obj.items():
            yield from residual_records(v, f"{path}/{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from residual_records(v, f"{path}[{i}]")


def invariant_violations(obj):
    bad = []
    for p, r in residual_records(obj):
        counts = r["Q_terms"]
        if not (isinstance(counts, list) and all(isinstance(n, int) and n >= 0 for n in counts)):
            bad.append(f"{p}: Q_terms not a list of nonnegative ints: {counts!r}")
        elif bool(r["Q_identically_zero"]) != all(n == 0 for n in counts):
            bad.append(f"{p}: Q_identically_zero={r['Q_identically_zero']} but Q_terms={counts}")
    return bad


def dumps(obj):
    bad = invariant_violations(obj)
    if bad:
        raise CertificateInvariantError("; ".join(bad))
    return _enc(obj, 0) + "\n"


def write(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(dumps(obj))


def accepted_orders(block):
    """Acceptance: Q_terms == [0,0,0,0] AND Q_identically_zero at every order kappa0..kappa2."""
    out = {}
    for o in ORDERS:
        r = block.get(o, {})
        out[o] = r.get("Q_terms") == [0, 0, 0, 0] and r.get("Q_identically_zero") is True
    return out


def cross_check(q_block, q_params, m_block, m_params):
    """Same export hashes + transformation parameters must give identical residual records."""
    same_inputs = q_params == m_params
    diffs = []
    if same_inputs:
        for o in ORDERS:
            for k in REC_KEYS:
                a, b = q_block.get(o, {}).get(k), m_block.get(o, {}).get(k)
                if a != b:
                    diffs.append(f"{o}.{k}: quartic={a} master={b}")
    return {"same_inputs": same_inputs, "differences": diffs, "agree": same_inputs and not diffs,
            "quartic_parameters": q_params, "master_parameters": m_params}


# ---------------- p13: content hashes that ignore wall-clock timings (reproducibility comparison) -----------
  +> -----
VOLATILE_KEYS = frozenset({"seconds"})          # wall-clock timings: the only run-dependent values in a certi
  +> ficate


def strip_volatile(obj, extra=()):
    drop = VOLATILE_KEYS | frozenset(extra)
    if isinstance(obj, dict):
        return {k: strip_volatile(v, extra) for k, v in obj.items() if k not in drop}
    if isinstance(obj, (list, tuple)):
        return [strip_volatile(v, extra) for v in obj]
    return obj


def content_sha(obj, extra=()):
    """sha256 of the canonical JSON (sorted keys, compact) after removing timing keys (and `extra` keys)."""
    import hashlib
    txt = json.dumps(strip_volatile(obj, extra), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(txt.encode()).hexdigest()


def file_content_sha(path, extra=()):
    return content_sha(json.loads(Path(path).read_text()), extra)
