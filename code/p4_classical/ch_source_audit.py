#!/usr/bin/env python3
"""p11 (e): mechanical ch dependency audit in TRANSFORMED variables + generated one-loop graph inventory.

Input: the transformed gauge-fixed action S_Psi(Phi, Phi*') = S_field + X(Phi, Phi*' - dPsi/dPhi)
(external antifields kept), built by source_action/gauge_fixing_map, plus the exported ell_2..ell_4.
Nothing below is typed by hand: every vertex pattern is read off S_Psi monomials.

ch pattern (exact): one c, one h; zero phi, cbar, b, antifields; ghost number 1; kappa^2; one loop; off-shell.
Projection of hbar^1 kappa^2 part of (S_Psi, Gamma_Psi) = sum_i (S_i, Gamma1^[2-i]) onto ch:
  summand 1 (A field):     dS_i/dA^R  *  dGamma1/dA*'^L      -> Gamma1 pattern P = ch - (M - A) + A*'
  summand 2 (A* antifield): dS_i/dA*'^R * dGamma1/dA^L        -> Gamma1 pattern P = ch - (M - A*') + A
for every monomial M of S_i.  P with a negative count => impossible.  Otherwise the one-loop graphs with
external pattern P at kappa^(2-i) are ENUMERATED from the S_Psi vertex inventory (cycles of vertices with
two internal legs each, lines h-h, c-cbar, phi-phi; b has no interaction vertex and is integrated out).
No graph => derived zero (with reason).  Surviving rows carry the generated graph names.

ENUMERATION LEMMA (p11; justifies max_len = 2).  (i) A connected one-loop graph is 1PI iff every internal line lies
on its unique cycle (a line off the cycle is a bridge); hence every vertex of a one-loop 1PI graph lies on the cycle
with exactly two internal legs, and all quadratic (kappa^0, two-field) terms are absorbed into propagators, so the
graph is a cycle of interaction vertices.  (ii) Every retained interaction vertex has coupling order kappa^n, n >= 1
(checked mechanically: the kappa^0 inventory contains only two-field monomials).  (iii) Hence a kappa^order
contribution with order <= 2 has at most `order` <= 2 vertices: max_len = 2 is exhaustive.  (iv) The auxiliary b
occurs only in kappa^0 two-field monomials (checked), so its Gaussian elimination produces only bilinear terms
(the de Donder kinetic term and source-bilinear terms) and no omitted interaction.  (v) Source-linear monomials
(exactly one quantum leg) cannot sit on a cycle (two internal legs needed); attached off the cycle they create a
bridge, i.e. a one-particle-reducible graph, so they cannot contribute extra 1PI coefficients.
Gamma_Psi <-> Gamma is the DEFINED classical pullback/interface along the antifield shift (gauge_fixing_map),
not an independently established quantum gauge-change theorem.
"""
from __future__ import annotations
import hashlib, itertools, json, os, sys, time
from collections import Counter
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "classical"))
from graded_jets import kappa_coeff, _KEY  # noqa: E402
from bv_model import KAPPA, Psi_density  # noqa: E402
from source_action import build_X_inv, scalar_density  # noqa: E402
from gauge_fixing_map import transformed_X  # noqa: E402
import planewave_exact as PW  # noqa: E402
import conventions as C  # noqa: E402
import certio  # noqa: E402

SPECIES = ["h", "c", "cb", "b", "phi", "K", "cs", "cbs", "bs", "phis"]
QUANTUM = {"h", "c", "cb", "b", "phi"}
ANTI = {"h": "K", "c": "cs", "cb": "cbs", "b": "bs", "phi": "phis"}
LINES = {("h", "h"), ("phi", "phi"), ("c", "cb"), ("cb", "c")}
GH = {"h": 0, "c": 1, "cb": -1, "b": 0, "phi": 0, "K": -1, "cs": -2, "cbs": 0, "bs": -1, "phis": -1}
CH = Counter({"c": 1, "h": 1})


def pat(c):
    return tuple(sorted((k, v) for k, v in Counter(c).items() if v))


def show(p):
    return "".join(f"{k}{'^'+str(v) if v > 1 else ''}." for k, v in p).rstrip(".") or "1"


# ---------------- vertex inventory of S_Psi ----------------
def monomial_patterns(F, nmax=2):
    out = {}
    for n in range(nmax + 1):
        Fn = kappa_coeff(F, KAPPA, n)
        pats = set()
        for key, coef in Fn.t.items():
            odd = Counter(k[0] for k in key)
            for term in sp.Add.make_args(sp.expand(coef)):
                cnt = Counter(odd)
                for s_, e in term.as_powers_dict().items():
                    kk = _KEY.get(s_)
                    if kk is not None:
                        cnt[kk[0]] += int(e)
                pats.add(pat(cnt))
        out[n] = sorted(pats)
    return out


def S_psi_inventory(mutate=None):
    X_inv = build_X_inv()
    X_psi = transformed_X(X_inv, Psi_density(), -1)
    inv = {n: set() for n in range(3)}
    src = {}
    for name, F in (("X_Psi (antifield + s Psi)", X_psi), ("scalar", scalar_density(2))):
        for n, ps in monomial_patterns(F).items():
            for p in ps:
                inv[n].add(p)
                src.setdefault(f"{n}|{show(p)}", set()).add(name)
    for k in (2, 3, 4):
        e, h = PW.load_ell(k)
        if e != 0:
            p = pat({"h": k})
            inv[k - 2].add(p)
            src.setdefault(f"{k-2}|{show(p)}", set()).add(f"ell_{k}")
    return {n: sorted(v) for n, v in inv.items()}, {k: sorted(v) for k, v in src.items()}


# ---------------- one-loop graph enumeration ----------------
def vertex_options(inv):
    """(kappa, pattern, internal pair (x,y), external pattern) for every vertex with >=2 quantum legs, kappa>=1."""
    opts = []
    for n, ps in inv.items():
        for p in ps:
            c = Counter(dict(p))
            q = [s for s in c if s in QUANTUM]
            if sum(c[s] for s in q) < 2:
                continue
            if n == 0:
                if sum(c.values()) <= 2:
                    continue  # kinetic / source-linear terms are propagators or external insertions
            for x in q:
                for y in q:
                    if x > y:
                        continue
                    cc = Counter(c)
                    cc[x] -= 1
                    if cc[y] <= 0:
                        continue
                    cc[y] -= 1
                    opts.append((n, p, (x, y), pat(cc)))
    return opts


def b_has_no_interaction(inv):
    return all(dict(p).get("b", 0) == 0 or n == 0 and sum(dict(p).values()) <= 2
               for n, ps in inv.items() for p in ps)


def enumerate_graphs(inv, P, order, max_len=2):
    """One-loop graphs with external pattern P at kappa^order (canonical signatures)."""
    opts = [o for o in vertex_options(inv) if 1 <= o[0] <= order]
    found = set()
    target = Counter(dict(P))
    for L in range(1, max_len + 1):
        for combo in itertools.combinations_with_replacement(range(len(opts)), L):
            vs = [opts[i] for i in combo]
            if sum(v[0] for v in vs) != order:
                continue
            ext = Counter()
            for v in vs:
                ext.update(dict(v[3]))
            if +ext != +target or any(ext[k] != target[k] for k in set(ext) | set(target)):
                continue
            # line matching: L=1 internal pair must be a line; L=2 pairs must match crosswise
            if L == 1:
                x, y = vs[0][2]
                ok = (x, y) in LINES
            else:
                (a1, b1), (a2, b2) = vs[0][2], vs[1][2]
                ok = ((a1, a2) in LINES and (b1, b2) in LINES) or ((a1, b2) in LINES and (b1, a2) in LINES)
            if ok:
                found.add(tuple(sorted((show(v[1]), f"{v[2][0]}{v[2][1]}", v[0]) for v in vs)))
    return sorted(found)


GRAPH_NAMES = {
    # (external pattern, kappa, signature) -> name ; unknown signature => TBD (acceptance fails)
    (("h^2", 2), (("h^3", "hh", 1), ("h^3", "hh", 1))): "D01_hh_bubble_cubic",
    (("h^2", 2), (("h^4", "hh", 2),)): "D02_hh_tadpole_quartic",
    (("h^2", 2), (("c.cb.h", "ccb", 1), ("c.cb.h", "ccb", 1))): "D03_hh_ghost_loop",
    (("h^2", 2), (("h.phi^2", "phiphi", 1), ("h.phi^2", "phiphi", 1))): "D11_hh_scalar_loop",
    (("h^2", 2), (("h^2.phi^2", "phiphi", 2),)): "D12_hh_scalar_tadpole",
    (("K.c", 2), (("K.c.h", "ch", 1), ("c.cb.h", "cbh", 1))): "D13_Kc_ghost_graviton_loop",
    (("h", 1), (("h^3", "hh", 1),)): "D14a_h_onepoint_grav_tadpole",
    (("h", 1), (("c.cb.h", "ccb", 1),)): "D14b_h_onepoint_ghost_tadpole",
    (("h", 1), (("h.phi^2", "phiphi", 1),)): "D14c_h_onepoint_scalar_tadpole",
}
GRAPH_STATUS = {
    "D01_hh_bubble_cubic": "listed_unevaluated",
    "D02_hh_tadpole_quartic": "vertex_available_quantum_unevaluated",
    "D03_hh_ghost_loop": "listed_unevaluated",
    "D11_hh_scalar_loop": "Constructed_kernel_under_prescription (inherited O5; not re-evaluated)",
    "D12_hh_scalar_tadpole": "Missing (D12_quantum_evaluated=false)",
    "D13_Kc_ghost_graviton_loop": "listed_unevaluated (generated from S_Psi; h* c row; coefficient not evaluated)",
    "D14a_h_onepoint_grav_tadpole": "listed_unevaluated; order-kappa one-point slot, DISTINCT from D12",
    "D14b_h_onepoint_ghost_tadpole": "listed_unevaluated; order-kappa one-point slot, DISTINCT from D12",
    "D14c_h_onepoint_scalar_tadpole": "listed_unevaluated; order-kappa one-point slot, DISTINCT from D12",
}


def show_sig(sig):
    return tuple((a, b, c) for a, b, c in sig)


def name_graph(P, order, sig):
    return GRAPH_NAMES.get(((show(P), order), tuple(sig)))


def audit(inv, drop_rows=()):
    rows, graphs, tbd = [], {}, []
    for i in range(3):
        for M in inv[i]:
            m = Counter(dict(M))
            for A in QUANTUM:
                for summand, X, Y in ((1, A, ANTI[A]), (2, ANTI[A], A)):
                    if m[X] == 0:
                        continue
                    R = Counter(m)
                    R[X] -= 1
                    Pc = Counter(CH)
                    Pc.subtract(R)          # what Gamma1 must supply besides the differentiated leg Y
                    if any(v < 0 for v in Pc.values()):
                        continue            # pattern impossible (S-monomial remainder exceeds ch)
                    Pc[Y] += 1
                    P = pat(Pc)
                    gs = enumerate_graphs(inv, P, 2 - i)
                    names = []
                    for g in gs:
                        nm = name_graph(P, 2 - i, g)
                        if nm is None:
                            tbd.append({"P": show(P), "order": 2 - i, "sig": g})
                            nm = "TBD"
                        names.append(nm)
                        graphs[nm] = {"external": show(P), "kappa": 2 - i, "signature": g,
                                      "status": GRAPH_STATUS.get(nm, "TBD")}
                    rid = f"(S{i},Gamma1^[{2-i}]) s{summand} {X}:{show(M)}"
                    if rid in drop_rows:
                        continue
                    if gs:
                        why = "surviving: one-loop graphs exist; coefficient not evaluated in this release"
                    elif dict(P).keys() & {"cbs", "bs"}:
                        why = ("derived zero: Gamma1 cannot depend on " + ",".join(sorted(dict(P).keys() & {'cbs', 'bs'}))
                               + " (no S_Psi vertex carries it with two quantum legs)")
                    else:
                        why = "derived zero: no one-loop graph with this external pattern at this order"
                    rows.append({"id": rid, "bracket": f"(S{i}, Gamma1^[{2-i}])", "summand": summand,
                                 "S_monomial": show(M), "differentiated": X, "Gamma1_pattern": show(P),
                                 "Gamma1_order": f"kappa^{2-i}", "graphs": sorted(set(names)),
                                 "status": "surviving_unevaluated" if gs else "derived_zero", "reason": why})
    return rows, graphs, tbd


def regenerate_and_compare(published_rows, inv):
    rows, _, _ = audit(inv)
    want = {r["id"] for r in rows}
    have = {r["id"] for r in published_rows}
    return {"missing_from_published": sorted(want - have), "extra_in_published": sorted(have - want),
            "complete": want == have}


def enumeration_lemma(inv):
    opts = vertex_options(inv)
    k0_multi = [show(p) for p in inv[0] if sum(dict(p).values()) > 2]
    min_k = min(o[0] for o in opts if o[0] >= 1)
    b_pats = [(n, show(p)) for n, ps in inv.items() for p in ps if dict(p).get("b", 0)]
    return {
        "statement": __doc__.split("ENUMERATION LEMMA")[1].split("Gamma_Psi <->")[0].strip(),
        "mechanical_checks": {
            "kappa0_monomials_all_two_field": not k0_multi, "kappa0_multi_field_monomials": k0_multi,
            "min_interaction_vertex_order": min_k, "all_interaction_vertices_kappa_ge_1": min_k >= 1,
            "max_vertices_at_kappa2": 2 // min_k, "max_len_used": 2, "max_len_exhaustive": 2 // min_k <= 2,
            "b_monomials": b_pats, "b_only_in_kappa0_bilinears": b_has_no_interaction(inv),
            "source_linear_excluded_reason": "vertex_options requires >= 2 quantum legs; one-leg insertions are bridges (1PR)",
        },
        "holds": (not k0_multi) and min_k >= 1 and b_has_no_interaction(inv),
        "interface": ("Gamma_Psi(Phi,Phi*') := Gamma(Phi, Phi*' - dPsi/dPhi) is a defined classical pullback/interface, "
                      "not an independently established quantum gauge-change theorem"),
    }


def env_drop_rows(inv):
    muts = [m for m in os.environ.get("P13_MUTATIONS", "").split(",") if m]
    if "drop_hstar_c_row" not in muts:
        return ()
    rows, _, _ = audit(inv)
    return tuple(r["id"] for r in rows if r["status"] == "surviving_unevaluated" and r["differentiated"] == "h"
                 and r["Gamma1_pattern"] == "K.c")


def main(drop_rows=(), write=True):
    t0 = time.time()
    inv, src = S_psi_inventory()
    drop_rows = tuple(drop_rows) + env_drop_rows(inv)
    rows, graphs, tbd = audit(inv, drop_rows=drop_rows)
    lemma = enumeration_lemma(inv)
    surviving = [r for r in rows if r["status"] == "surviving_unevaluated"]
    hstar_c = [r for r in surviving if r["differentiated"] == "h" and r["Gamma1_pattern"] == "K.c"]
    onept = [r for r in surviving if r["Gamma1_pattern"] == "h"]
    cmp = regenerate_and_compare(rows, inv)
    phi_rows = [r for r in rows if "phi" in r["differentiated"]]
    k2_ghost_vertex = any(dict(p).get("c", 0) and dict(p).get("cb", 0) for p in inv[2])
    checks = {
        "names_TBD_empty": not tbd,
        "regenerated_rows_match_published": cmp["complete"],
        "hstar_c_row_present": bool(hstar_c),
        "onepoint_slot_distinct_from_D12": bool(onept) and all("D12_hh_scalar_tadpole" not in r["graphs"] for r in onept),
        "b_has_no_interaction_vertex": b_has_no_interaction(inv),
        "no_kappa2_ghost_vertex": not k2_ghost_vertex,
        "cbar_star_rows_derived_zero": all(r["status"] == "derived_zero" for r in rows if "cbs" in r["Gamma1_pattern"]),
        "b_star_rows_derived_zero": all(r["status"] == "derived_zero" for r in rows if "bs" in r["Gamma1_pattern"]),
        "S2_rows_derived_zero": all(r["status"] == "derived_zero" for r in rows if r["bracket"].startswith("(S2")),
        "enumeration_lemma_holds": lemma["holds"],
    }
    complete = all(checks.values())
    cert = {
        "revision": C.REVISION, "gate": "ch_projection_defined / ch_dependency_inventory_complete",
        "variables": "transformed (Phi, Phi*'), S_Psi with external antifields; Psi = " + C.PSI,
        "ch_pattern": {"c": 1, "h": 1, "phi": 0, "cbar": 0, "b": 0, "antifields": 0, "ghost_number": 1,
                       "coupling": "kappa^2", "loop": "one", "domain": "off-shell, compact smooth smearings"},
        "method": __doc__.strip().splitlines()[0],
        "vertex_inventory": {f"kappa{n}": [show(p) for p in ps] for n, ps in inv.items()},
        "vertex_sources": src,
        "rows_total": len(rows), "rows_surviving": len(surviving),
        "rows_derived_zero": len(rows) - len(surviving),
        "surviving_rows": surviving,
        "hstar_c_row": hstar_c,
        "onepoint_kappa_slot": onept,
        "phi_rows": {"count": len(phi_rows), "all_derived_zero_or_impossible": all(r["status"] == "derived_zero" for r in phi_rows),
                     "parity_argument": "phi -> -phi is a symmetry of S_Psi (phi appears in even powers in every non-antifield "
                                        "monomial and phis.phi pairs); ch is phi-even"},
        "checks": checks, "enumeration_lemma": lemma, "dropped_rows_mutation": list(drop_rows),
        "regeneration": cmp,
        "names_TBD": tbd,
        "ch_projection_defined": True,
        "ch_dependency_inventory_complete": complete,
        "values": ("no surviving coefficient is evaluated in this release (no loop evaluated here); D11 carries an "
                   "inherited O5 kernel constructed under prescription, not re-evaluated in this release"),
        "execution_pass": True, "claim_status": "earned" if complete else "Partial",
        "scope": "pattern-level dependency inventory of the projected kappa^2 one-loop source identity; not evaluation",
        "seconds": round(time.time() - t0, 1),
    }
    gl = {"revision": C.REVISION, "generated_from": "S_Psi vertex inventory (ch_source_audit.enumerate_graphs)",
          "graphs": graphs, "names_TBD": [t for t in tbd],
          "D02_quantum_evaluated": False, "D12_quantum_evaluated": False, "D12_status": "Missing",
          "no_loop_evaluated": True}
    rl = {"revision": C.REVISION, "rows": rows}
    if write:
        (ROOT / "certificates" / "P13_ch_source_audit.json").write_text(certio.dumps(cert))
        (ROOT / "ledgers" / "P13_ch_dependency_rows.json").write_text(certio.dumps(rl))
        (ROOT / "ledgers" / "P13_graph_inventory.json").write_text(certio.dumps(gl))
    return cert, rows, graphs


if __name__ == "__main__":
    cert, rows, graphs = main()
    print(json.dumps({"complete": cert["ch_dependency_inventory_complete"], "checks": cert["checks"],
                      "rows": cert["rows_total"], "surviving": [(r["id"], r["Gamma1_pattern"], r["graphs"]) for r in cert["surviving_rows"]],
                      "graphs": list(graphs), "inv": cert["vertex_inventory"], "TBD": cert["names_TBD"], "sec": cert["seconds"]}, indent=1, default=str))
