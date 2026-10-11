#!/usr/bin/env python3
"""XVI-P p23 (stage 1 of the O.1 direction): O.1 requirement record, exact one-loop power counting, the kappa^
  +> 2
identity decomposition (enlarge-rule check) and the P.6 ENTRY inventory (one-loop kappa^3 three-point graphs).

Exact, mechanical, from the frozen vertex inventory (feynman.vertices) -- no hand-written graph list:
  * every interaction vertex carries kappa^(legs-2) (sources/antifields count as legs)  =>  a one-loop 1PI gra
  +> ph with
    E external legs is exactly kappa^E (I = V at L = 1);  verified vertex by vertex AND graph by graph;
  * all one-loop 1PI graphs (cycles of interaction vertices, >= 3 legs, loop legs paired by the DECLARED propa
  +> gators
    h-h, phi-phi, c-cbar) are enumerated for E = 1, 2, 3 (topology level: species, vertices, loop lines; no sy
  +> mmetry
    factors, no amplitudes);
  * E = 2 must reproduce the frozen kappa^2 one-loop inventory exactly (D01..D06, D11, D12 + D13), E = 1 the
    one-point row;
  * the one-loop ST identity at kappa^2 is (S^(0), Gamma_1^(2)) + (S^(1), Gamma_1^(1)) (+ (S^(2), Gamma_1^(0))
  +>  = 0,
    Gamma_1^(0) is field independent): only E = 2 and E = 1 enter, so the O.1 enlarge rule ("the stated identi
  +> ty
    constrains n-point pieces at the same coupling order") is NOT triggered by one-loop three-point functions 
  +> at
    kappa^2 -- the kappa^2 three-point one-loop sector is EMPTY.  Three-point first appears at kappa^3 (P.6 en
  +> try).
This is package evidence (XVI-O conv:package), not a certificate of O.1.
"""
from __future__ import annotations
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in ("code/p5_entry", "code/classical", "code/p5_calc"):
    sys.path.insert(0, str(ROOT / p))
import feynman as F  # noqa: E402
import certio  # noqa: E402

CERT = ROOT / "certificates"
O_LEDGER = ROOT / "provenance" / "XVI-O" / "O_quantum_target.json"   # verbatim copy of XVI-O/ledgers/O_quantu
  +> m_target.json (sha pinned in p23_conventions; XVI-O untouched)
PROPAGATING = {frozenset(("h",)), frozenset(("phi",)), frozenset(("c", "cb"))}   # declared propagators (P14 G
  +> ate 0)
FROZEN_E2 = {   # frozen kappa^2 one-loop inventory (diagram_inventory.json D01..D12 + P15_D13), species level
    "D01_hh_bubble_cubic": ("h,h", ("V3_grav", "V3_grav")), "D02_hh_tadpole_quartic": ("h,h", ("V4_grav",)),
    "D03_hh_ghost_loop": ("h,h", ("V_cb_c_h", "V_cb_c_h")), "D04_phiphi_bubble": ("phi,phi", ("V_h_phi_phi", "
  +> V_h_phi_phi")),
    "D05a_phiphi_grav_tadpole": ("phi,phi", ("V_hh_phi_phi",)), "D06_cc_ghost_two_point": ("c,cb", ("V_cb_c_h"
  +> , "V_cb_c_h")),
    "D11_hh_scalar_loop": ("h,h", ("V_h_phi_phi", "V_h_phi_phi")), "D12_hh_scalar_tadpole": ("h,h", ("V_hh_phi
  +> _phi",)),
    "D13_Kc_ghost_self_energy": ("K,c", ("V_K_c_h", "V_cb_c_h")),
}


def pair_ok(a, b):
    return frozenset((a, b)) in PROPAGATING


def interaction_vertices(V):
    return {k: v for k, v in V.items() if len(v.legs) >= 3}


def vertex_power_ok(V):
    return {k: (v.kappa_power == len(v.legs) - 2) for k, v in V.items()}


def _vstates(V):
    """(vertex, in_species, out_species, external multiset) for every choice of two distinct loop legs."""
    out = []
    for name, v in V.items():
        L = list(v.legs)
        seen = set()
        for i in range(len(L)):
            for j in range(len(L)):
                if i == j:
                    continue
                ext = tuple(sorted(L[k] for k in range(len(L)) if k not in (i, j)))
                key = (name, L[i], L[j], ext)
                if key not in seen:
                    seen.add(key)
                    out.append(key)
    return out


def _canon(cyc):
    n = len(cyc)
    forms = []
    for seq in (cyc, [(v, o, i, e) for (v, i, o, e) in reversed(cyc)]):
        for r in range(n):
            forms.append(tuple(seq[r:] + seq[:r]))
    return min(forms)


def one_loop_graphs(V, E):
    """all one-loop 1PI graphs with exactly E external legs (interaction vertices only)."""
    Vi = interaction_vertices(V)
    states = _vstates(Vi)
    found = {}

    def ext_of(s):
        return len(s[3])

    def rec(cyc, e):
        if e > E:
            return
        last = cyc[-1]
        if e == E and pair_ok(last[2], cyc[0][1]):
            c = _canon(list(cyc))
            found[c] = c
        if e == E:
            return
        for s in states:
            if ext_of(s) >= 1 and pair_ok(last[2], s[1]):
                rec(cyc + [s], e + ext_of(s))

    for s in states:
        if ext_of(s) >= 1 or E == 0:
            rec([s], ext_of(s))
    out = []
    for c in sorted(found):
        kp = sum(Vi[v].kappa_power for (v, _, _, _) in c)
        ext = sorted(x for (_, _, _, e) in c for x in e)
        out.append({"vertices": [v for (v, _, _, _) in c],
                    "loop_lines": [f"{c[k][2]}-{c[(k + 1) % len(c)][1]}" for k in range(len(c))],
                    "external": ",".join(ext), "kappa_power": kp, "V": len(c), "I": len(c), "L": 1,
                    "kappa_equals_E": kp == E})
    return out


def frozen_match(g2):
    have = Counter((g["external"], tuple(sorted(g["vertices"]))) for g in g2)
    want = Counter((ex, tuple(sorted(vs))) for ex, vs in FROZEN_E2.values())
    return {"enumerated": sum(have.values()), "frozen": sum(want.values()),
            "missing_from_enumeration": sorted(map(str, (want - have).elements())),
            "not_in_frozen_inventory": sorted(map(str, (have - want).elements())),
            "equal": have == want}


def run(V):
    g = {E: one_loop_graphs(V, E) for E in (1, 2, 3)}
    return g


def main():
    t0 = time.time()
    raw = O_LEDGER.read_bytes()
    oled = json.loads(raw)
    V = F.vertices()
    vp = vertex_power_ok(V)
    g = run(V)
    fm = frozen_match(g[2])
    e1 = sorted((x["external"], tuple(sorted(x["vertices"]))) for x in g[1])
    e3_species = Counter(x["external"] for x in g[3])
    # mutations (must be detected)
    muts = {}

    class _VT:
        def __init__(self, legs, kp):
            self.legs, self.kappa_power = legs, kp
    m1 = {k: _VT(v.legs, v.kappa_power) for k, v in V.items()}
    m1["V3_grav"] = _VT(V["V3_grav"].legs, 2)
    muts["V3_grav_kappa_power_+1"] = not all(vertex_power_ok(m1).values())
    m2 = {k: _VT(v.legs, v.kappa_power) for k, v in V.items() if k != "V_cb_c_h"}
    muts["drop_V_cb_c_h"] = not frozen_match(one_loop_graphs(m2, 2))["equal"]
    m3 = {k: _VT(v.legs, v.kappa_power) for k, v in V.items() if k != "V_hh_phi_phi"}
    muts["drop_V_hh_phi_phi"] = not frozen_match(one_loop_graphs(m3, 2))["equal"]
    PROPAGATING.add(frozenset(("c", "h")))
    muts["spurious_c_h_propagator"] = not frozen_match(one_loop_graphs(V, 2))["equal"]
    PROPAGATING.discard(frozenset(("c", "h")))
    in_scope = {
        "State retained quantum identity (O.6)": ("PARTLY in XVI-P", "projected ch identity at one loop kappa^
  +> 2 stated "
                                                  "and verified (P19/P20), incl. evanescent CTs (P22); the BUL
  +> K "
                                                  "retained identity (ST4b functional) is XVI-O's statement, n
  +> ot changed"),
        "List amplitudes constrained by identity (O.4)": ("IN XVI-P (this record)", "one-loop kappa^2: exactly
  +>  the E=2 "
                                                          "two-point and E=1 one-point graphs; enumeration rep
  +> roduces "
                                                          "the frozen inventory; completeness at topology leve
  +> l only"),
        "S_inv^{[2]} classical consistency (O.2)": ("OUT OF SCOPE", "classical kappa^2 master 2(S0,S2)+(S1,S1)
  +> : grav ell_4 "
                                                    "Incomplete in XVI-O/XVI-N; XVI-A..O untouched -> O.1 cann
  +> ot "
                                                    "close inside XVI-P"),
        "Evaluate inventory graphs (O.5)": ("IN XVI-P", "all E=2 kappa^2 graphs evaluated (P15..P18, D12 Missi
  +> ng never "
                                            "zero per P14 -> see open items)"),
        "Demonstrate identity remainder cancellation / CT solution (O.6/O.7)": (
            "PARTLY in XVI-P", "projected: closure + restoration earned (P20, P22); bulk ST4a/ST4b split: XVI-
  +> O"),
        "Enlarge target if identity requires more legs/orders (O.1)": (
            "IN XVI-P (this record)", "NOT triggered at kappa^2 at one loop (three-point one-loop sector empty
  +>  at "
            "kappa^2); next order kappa^3 three-point = P.6 entry"),
    }
    out = {
        "landmark": "XVI-P", "revision": "p23",
        "deliverable": "p23 stage 1: O.1 exact requirement, one-loop power counting, enlarge-rule check, P.6 e
  +> ntry inventory",
        "O1_source": {"file": O_LEDGER.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(raw).hexdigest()
  +> , "read_only": True,
                      "gate": oled.get("gate"), "target": oled.get("proposed_target"),
                      "closure_question": oled["closure_check"]["question"],
                      "outcome": oled["closure_check"]["outcome"],
                      "checklist": oled["closure_check"]["checklist"],
                      "enlarge_rules": oled["closure_check"]["enlarge_rules"]},
        "O1_requirement": ("O.1 closes iff the one-loop kappa^2 bulk two-point sector on S_inv closes under a 
  +> VERIFIED "
                           "retained quantum identity: every checklist item (O.2 classical kappa^2 master Cons
  +> tructed incl. "
                           "grav ell_4; O.4 inventory; O.5 all graphs evaluated; O.6 identity verified; O.7 re
  +> mainder "
                           "cancellation / CT solution) earned, and the target enlarged first if the identity 
  +> constrains "
                           "more legs/orders at kappa^2."),
        "O1_items_scope": {k: {"scope": a, "evidence": b} for k, (a, b) in in_scope.items()},
        "O1_closable_in_XVI_P": False, "O1_closure_status": "NOT_CLOSED",
        "P6_entry_n_graphs": len(g[3]), "one_point_n_graphs": len(g[1]),
        "O1_closable_reason": "O.2 (classical kappa^2 master, grav ell_4 Incomplete) and the bulk ST4b identit
  +> y are owned "
                              "by XVI-O/XVI-N, which stay untouched",
        "vertex_kappa_power_equals_legs_minus_2": vp, "vertex_rule_holds": all(vp.values()),
        "one_loop_kappa_equals_E": all(x["kappa_equals_E"] for E in g for x in g[E]),
        "identity_at_kappa2": {"terms": ["(S^(0), Gamma_1^(2))  [E=2]", "(S^(1), Gamma_1^(1))  [E=1]",
                                         "(S^(2), Gamma_1^(0)) = 0  [field independent]"],
                               "orders_entering": ["E=2 two-point (hh, phiphi, c.cb, K.c)", "E=1 one-point"],
                               "three_point_one_loop_at_kappa2": "EMPTY (kappa^E with E=3 is kappa^3)",
                               "enlarge_rule_triggered": False},
        "graphs_E1": [{"external": a, "vertices": list(b)} for a, b in e1],
        "graphs_E2": g[2], "frozen_E2_match": fm,
        "P6_entry_kappa3_three_point": {"n_graphs": len(g[3]), "by_external": dict(sorted(e3_species.items()))
  +> ,
                                        "graphs": g[3],
                                        "status": "inventory only (topology level). NOT evaluated: amplitude r
  +> ules, "
                                                  "counterterm domain and evaluation are the next release"},
        "mutations": muts, "mutations_detected": all(muts.values()),
        "seconds": round(time.time() - t0, 2),
    }
    out["pass"] = bool(out["vertex_rule_holds"] and out["one_loop_kappa_equals_E"] and fm["equal"]
                       and out["mutations_detected"] and not out["identity_at_kappa2"]["enlarge_rule_triggered
  +> "])
    certio.write_json(CERT / "P23_O1_scope.json", out) if hasattr(certio, "write_json") else \
        (CERT / "P23_O1_scope.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"pass": out["pass"], "frozen_E2_match": fm, "E1": len(g[1]), "E2": len(g[2]), "E3": len(
  +> g[3]),
                      "E3_by_external": out["P6_entry_kappa3_three_point"]["by_external"], "mutations": muts},
  +>  indent=1))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
