#!/usr/bin/env python3
"""p11 (d): evaluate 2(S0,S2)+(S1,S1) (and the kappa^0, kappa^1 regressions) by antifield number,
in invariant AND transformed (gauge-fixed, external antifields retained) variables.

S = S_field + X,  X antifield-linear.  (S_field,S_field)=0 identically, so
  (S,S) = 2 (S_field, X) + (X, X),   2(S_field,X) = 2 int E_Phi(S_field) . sigma s Phi  (af 0)
* (X,X): exact graded-engine bracket (XVI-N orientation), split by kappa order, antifield number
  and bracket pair; divergence test by Euler operators (exact).
* 2(S_field,X), scalar sector: exact engine bracket + divergence test.
* 2(S_field,X), gravitational sector (p11, DETERMINISTIC): W_n = s0 ell_{n+2} + s1 ell_{n+1} built as exact
  jet polynomials from the EXPORTED ell_2, ell_3, ell_4 (sha-checked); W_n is c-linear, so W_n ~ c^mu E_{c^mu}(W_n)
  and W_n is a divergence iff E_{c^mu}(W_n) = 0 identically (grav_noether.py).  The s0-alone piece is reported to
  exhibit the mixed cancellation.  Plane-wave evaluation is retained as a sampled REGRESSION CONTROL only.
Multidegree lemma (corrected p11): with P_d the projection onto field multidegree d and E_u the Euler operator of
field u, E_u P_d = P_{d - e_u} E_u (E_u lowers the u-degree by one and preserves the others; total derivatives
preserve multidegree).  Hence if F = sum_d P_d F has E_u F = 0 for all u, then P_{d-e_u} E_u F = E_u P_d F = 0 for every
d and u, so every homogeneous component P_d F with |d| >= 1 has vanishing Euler derivatives and is a divergence
(no constant term occurs); conversely a sum of divergences is a divergence.  So a sum is a divergence iff each
multidegree component is.  Within one multidegree all contributions are summed before testing.
"""
from __future__ import annotations
import hashlib, json, random, sys, time
from fractions import Fraction as Fr
from pathlib import Path
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graded_jets import (GE, D, bracket, euler, comps, kappa_coeff, divergence_residual, PAIRS,  # noqa: E402
                         _KEY, set_parity)
from bv_model import KAPPA, A, s_map, Psi_density, hc  # noqa: E402
from source_action import build_X_inv, scalar_density  # noqa: E402
from gauge_fixing_map import transformed_X  # noqa: E402
import planewave_exact as PW  # noqa: E402
import conventions as C  # noqa: E402
import certio  # noqa: E402
import grav_noether as GN  # noqa: E402
import jetpoly as J  # noqa: E402
import os

ROOT = Path(__file__).resolve().parents[2]
AF_ODD = {"K", "bs", "phis"}
AF_EVEN = ("cs", "cbs")


def af_number_split(F):
    out = {}
    for k, v in F.t.items():
        n_odd = sum(1 for x in k if x[0] in AF_ODD)
        for term in sp.Add.make_args(sp.expand(v)):
            n = n_odd
            for s_, e in term.as_powers_dict().items():
                kk = _KEY.get(s_)
                if kk is not None and kk[0] in AF_EVEN:
                    n += int(e)
            out.setdefault(n, {})
            out[n][k] = out[n].get(k, 0) + term
    return {n: GE(t) for n, t in out.items()}


def kappa_parts(X, nmax=2):
    return {n: kappa_coeff(X, KAPPA, n) for n in range(nmax + 1)}


def bracket_pairs(F, G):
    return {f: bracket(F, G, pairs=[(f, fs)]) for f, fs in PAIRS}


def residual_summary(F):
    res = divergence_residual(F)
    return {"is_divergence": not res, "n_terms": len(F.t),
            "nonzero_euler_components": sorted(f"{f}{c}" for f, c in res)[:12]}


def XX_by_order(X, label, nmax=2, per_pair=True):
    Xk = kappa_parts(X, nmax)
    out = {}
    for n in range(nmax + 1):
        pairs_total = {f: GE() for f, _ in PAIRS}
        for i in range(n + 1):
            j = n - i
            if Xk[i].is_zero() or Xk[j].is_zero():
                continue
            for f, v in bracket_pairs(Xk[i], Xk[j]).items():
                pairs_total[f] = pairs_total[f] + v
        tot = GE()
        for v in pairs_total.values():
            tot = tot + v
        split = af_number_split(tot)
        rec = {"total": residual_summary(tot), "by_antifield_number": {}}
        for af in sorted(set(split) | {0, 1, 2}):
            part = split.get(af, GE())
            prs = {}
            if per_pair:
                for f, v in pairs_total.items():
                    pv = af_number_split(v).get(af, GE())
                    if not pv.is_zero():
                        prs[f] = residual_summary(pv)
            rec["by_antifield_number"][af] = {"total": residual_summary(part), "per_bracket_pair": prs,
                                               "mixed_cancellation": (len(prs) > 1 and residual_summary(part)["is_divergence"]
                                                                       and any(not p["is_divergence"] for p in prs.values()))}
        out[n] = rec
    return out


def scalar_sector(X, nmax=2, mutate_a2=None):
    L = scalar_density(nmax, mutate_a2=mutate_a2)
    Lk = kappa_parts(L, nmax)
    Xk = kappa_parts(X, nmax)
    out = {}
    for n in range(nmax + 1):
        tot = GE()
        pieces = {}
        for i in range(n + 1):
            j = n - i
            if Lk[i].is_zero() or Xk[j].is_zero():
                continue
            b = bracket(Lk[i], Xk[j]).scale(2)
            pieces[f"2(L{i},X{j})"] = residual_summary(b)["is_divergence"]
            tot = tot + b
        out[n] = {"total": residual_summary(tot), "pieces_individually_divergence": pieces}
    return out


# ---------------- gravitational sector (exact plane waves) ----------------
def load_grav(mutate_ell4=None):
    data = {}
    for k in (2, 3, 4):
        expr, sha = PW.load_ell(k)
        cp = PW.compile_poly(expr)
        if k == 4 and mutate_ell4 is not None:
            cp = [(c * mutate_ell4 if i == 0 else c, f) for i, (c, f) in enumerate(cp)]
        data[k] = {"cp": cp, "sha": sha, "terms": len(cp)}
    return data


def grav_noether(data, n, rng, a=Fr(1, 2), s1_scale=Fr(1), transport=1, s1_sign=1):
    ev = {k: (lambda j, cp=data[k]["cp"]: PW.eval_poly(cp, j)) for k in data}
    nh = n + 1
    eps = [PW.rnd_sym(rng) for _ in range(nh)]
    ks = [PW.rnd_vec(rng) for _ in range(nh)]
    kc = PW.neg(PW.vadd(*ks))
    zeta = PW.rnd_vec(rng)
    W = [PW.tensor_jet(eps[i], ks[i]) for i in range(nh)]
    S0 = PW.tensor_jet(PW.s0_h_pol(zeta, kc, a), kc)
    Y = [PW.tensor_jet(PW.lie_c_h_pol(zeta, kc, eps[i], ks[i], a * s1_scale * s1_sign, transport=transport),
                       PW.vadd(kc, ks[i])) for i in range(nh)]
    piece_s0 = PW.polarize(ev[n + 2], W + [S0])
    piece_s1 = Fr(0)
    if n >= 1:
        for i in range(nh):
            others = [W[j] for j in range(nh) if j != i]
            piece_s1 += PW.polarize(ev[n + 1], others + [Y[i]])
    return piece_s0, piece_s1


def grav_sector(data, samples=10, seed=2026, **kw):
    out = {}
    for n in (0, 1, 2):
        rng = random.Random(seed + n)
        vals = []
        for _ in range(samples):
            p0, p1 = grav_noether(data, n, rng, **kw)
            vals.append((p0, p1))
        out[n] = {
            "samples": samples,
            "all_sums_exactly_zero": all(p0 + p1 == 0 for p0, p1 in vals),
            "s0_piece_nonzero_in_samples": sum(1 for p0, _ in vals if p0 != 0),
            "s1_piece_nonzero_in_samples": sum(1 for _, p1 in vals if p1 != 0),
            "max_abs_sum": str(max(abs(p0 + p1) for p0, p1 in vals)),
            "example_pieces": [str(vals[0][0]), str(vals[0][1])],
            "density": {0: "s0 ell2", 1: "s0 ell3 + s1 ell2", 2: "s0 ell4 + s1 ell3 (+ s2 ell2, s2=0 derived)"}[n],
        }
    return out


def grav_deterministic(mutations=()):
    ell, sha = GN.load_export_polys()
    if "corrupt_ell4" in mutations:
        e4 = dict(ell[4])
        k0 = sorted(e4)[len(e4) // 2]
        e4[k0] *= Fr(7, 5)
        ell[4] = e4
    tr = 0 if "drop_s1_transport" in mutations else 1
    return GN.noether(ell, transport=tr), sha, GN.parameters(sha, transport=tr)


def run(mutations=(), samples=3):
    t0 = time.time()
    muts = set(mutations)
    sigma = {"h": 1, "c": -1, "cb": -1, "phi": 1}
    if "flip_sigma_c" in muts:
        sigma["c"] = 1
    drop = ("c",) if "drop_cstar" in muts else ()
    X_inv = build_X_inv(sigma=sigma, drop=drop)
    Psi = Psi_density()
    X_psi = transformed_X(X_inv, Psi, -1, mutate="halve_offdiag_h" if "alter_gf_shift" in muts else None)
    if "flip_odd_derivative_sign" in muts:
        set_parity("c", 0)   # treat the ghost as even: odd left/right derivative signs lost
    try:
        inv = XX_by_order(X_inv, "invariant")
        trf = XX_by_order(X_psi, "transformed")
        sc = scalar_sector(X_inv, mutate_a2=Fr(1, 3) if "corrupt_a2" in muts else None)
    finally:
        set_parity("c", 1)
    gdet, gsha, gparams = grav_deterministic(muts)
    data = load_grav(mutate_ell4=Fr(7, 5) if "corrupt_ell4" in muts else None)
    grav = grav_sector(data, samples=samples,
                       transport=0 if "drop_s1_transport" in muts else 1)

    def ok_order(d, n):
        return all(v["total"]["is_divergence"] for v in d[n]["by_antifield_number"].values())

    residuals = []
    for n in (0, 1, 2):
        for name, d in (("invariant", inv), ("transformed", trf)):
            for af, v in d[n]["by_antifield_number"].items():
                if not v["total"]["is_divergence"]:
                    residuals.append(f"{name}_kappa{n}_af{af}:{','.join(v['total']['nonzero_euler_components'][:4])}")
        if not sc[n]["total"]["is_divergence"]:
            residuals.append(f"scalar_noether_kappa{n}_af0")
        if not (gdet[f"kappa{n}"]["Q_identically_zero"] and gdet[f"kappa{n}"]["Q_terms"] == [0, 0, 0, 0]):
            residuals.append(f"grav_noether_kappa{n}_af0:Q_terms={gdet[f'kappa{n}']['Q_terms']}")
    k2_res = [r for r in residuals if "kappa2" in r]
    return {
        "invariant_variables": inv, "transformed_variables": trf,
        "scalar_af0": sc, "grav_af0_deterministic": gdet, "grav_af0_parameters": gparams,
        "grav_af0_accepted_orders": certio.accepted_orders(gdet),
        "grav_af0_planewave_regression_control_NOT_acceptance": grav,
        "grav_inputs": {k: {"sha256": data[k]["sha"], "terms": data[k]["terms"]} for k in data},
        "residuals_all_orders": residuals, "residuals_kappa2": k2_res,
        "seconds": round(time.time() - t0, 2), "mutations": sorted(muts),
    }


def master_residuals(r, sha_ok):
    """Explicit list: every non-divergent component at any order, plus an ell4 provenance failure."""
    res = list(r["residuals_all_orders"])
    if not sha_ok:
        res.append("ell4_sha256_mismatch_vs_P13_quartic_verified")
    return res


def env_mutations():
    return tuple(m for m in os.environ.get("P13_MUTATIONS", "").split(",") if m)


def main(samples=3):
    muts = env_mutations()
    r = run(mutations=muts, samples=samples)
    q = json.loads((ROOT / "certificates" / "P13_quartic_verified.json").read_text()) \
        if (ROOT / "certificates" / "P13_quartic_verified.json").exists() else {}
    sha_ok = (q.get("ell4_sha256") == r["grav_inputs"][4]["sha256"]
              and q.get("ell3_sha256") == r["grav_inputs"][3]["sha256"]
              and q.get("ell2_sha256") == r["grav_inputs"][2]["sha256"])
    quartic_ok = bool(q.get("quartic_generator_verified"))
    prereq = [] if quartic_ok else ["prerequisite_failed:P13_quartic_verified.quartic_generator_verified"]
    verified = (not r["residuals_all_orders"]) and sha_ok and quartic_ok
    af_table = {}
    for n in (0, 1, 2):
        af_table[f"kappa{n}"] = {
            "af0_grav_Noether": r["grav_af0_deterministic"][f"kappa{n}"]["Q_identically_zero"],
            "af0_scalar_Noether": r["scalar_af0"][n]["total"]["is_divergence"],
            "af0_ghost_gf_transformed": r["transformed_variables"][n]["by_antifield_number"][0]["total"]["is_divergence"],
            "af1_invariant": r["invariant_variables"][n]["by_antifield_number"][1]["total"]["is_divergence"],
            "af1_transformed": r["transformed_variables"][n]["by_antifield_number"][1]["total"]["is_divergence"],
            "af2_invariant": r["invariant_variables"][n]["by_antifield_number"][2]["total"]["is_divergence"],
            "af2_transformed": r["transformed_variables"][n]["by_antifield_number"][2]["total"]["is_divergence"],
        }
    cert = {
        "revision": C.REVISION, "gate": "required_classical_BV_components_verified",
        "equation": "(S,S) at kappa^2: 2(S0,S2)+(S1,S1) = 0  [plus regressions (S0,S0)=0, 2(S0,S1)=0]",
        "bracket": C.ANTIBRACKET, "baseline": C.BASELINE,
        "identification_with_exports": {
            "ell2_ell3_ell4": r["grav_inputs"],
            "ell2_ell3_ell4_sha_match_P13_quartic_verified": sha_ok,
            "quartic_generator_verified": quartic_ok,
            "scalar_a1_a2": "re-derived and identified in P13_source_action (B = sqrt(-g) g^{-1})",
            "s_images": "P13_brst_derivation (s2 derived zero)"},
        "table_by_kappa_and_antifield_number": af_table,
        "details": r,
        "required_master_residuals": master_residuals(r, sha_ok) + prereq,
        "required_classical_BV_components_verified": verified,
        "evidence_kind": {
            "engine_parts": "exact symbolic (graded jets; Euler-operator divergence test)",
            "grav_af0": ("DETERMINISTIC exact polynomial identity: E_{c^mu}(s0 ell_{n+2} + s1 ell_{n+1}) = 0 for n = 0,1,2 "
                         "on the exported polynomials (grav_noether.py); structural reason: sqrt(-g)R is a scalar density, "
                         "s(sqrt(-g)R) = d(xi sqrt(-g)R), and L_GG = sqrt(-g)R + d_mu B^mu (P13_boundary_identity: "
                         "sqrt(-g)R - L_GG = -d_mu B^mu), with s d_mu B^mu = d_mu s B^mu"),
            "grav_af0_planewave": (f"REGRESSION CONTROL only: exact rational plane-wave evaluation at "
                                   f"{r['grav_af0_planewave_regression_control_NOT_acceptance'][2]['samples']} points per order; not cited as proof"),
        },
        "transformed_variables_note": ("(S_Psi,S_Psi) = 2(S_field,X_Psi) + (X_Psi,X_Psi); X is antifield-linear, so "
            "dX_Psi/dPhi*' = dX/dPhi* and 2(S_field,X_Psi) = 2(S_field,X) (af 0, shared Noether table); "
            "the s Psi field-only part has no antifields and brackets only through (X_Psi,X_Psi)."),
        "mixed_cancellations": {f"kappa{n}_af{af}_{name}": sorted(v["per_bracket_pair"])
                                for name, d in (("invariant", r["invariant_variables"]), ("transformed", r["transformed_variables"]))
                                for n in (0, 1, 2) for af, v in d[n]["by_antifield_number"].items() if v["mixed_cancellation"]},
        "execution_pass": True,
        "claim_status": "verified" if verified else "Partial",
        "mutations_from_env": list(muts),
        "scope": ("classical BV master equation of the S_inv extended action (grav ell_2..ell_4 + massless scalar + "
                  "minimal ghosts + nonminimal (cbar,b)) through O(kappa^2), in invariant and Psi-transformed variables "
                  "with external antifields; NOT the prepared S_D (broken square kept), NOT the insertion, NOT quantum."),
        "note_on_pass": "p11: no unconditional 'pass' field; execution_pass (ran), claim_status and scope are separate.",
    }
    (ROOT / "certificates" / "P13_master_kappa2.json").write_text(certio.dumps(cert))
    print(json.dumps({"verified": verified, "residuals": cert["required_master_residuals"], "table": af_table,
                      "sec": r["seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
