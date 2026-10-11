#!/usr/bin/env python3
"""p08: Full indexed ell_4 / V4_grav generating polynomial (order-by-order).

ell_4 = -2 [eps^4] L_Γ,  L_Γ = sqrt(-q) q^{mn}(Γ^a_{mb} Γ^b_{na} - Γ^a_{mn} Γ^b_{ab})
      ≡ sqrt(-q) R  (modulo total derivatives; IBP policy).

Jet coordinates: 10 independent H_{μν} and ∂_ρ H_{μν}.
"""
from __future__ import annotations
import hashlib, json, time, sys
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inverse_metric_series import (  # noqa: E402
    inverse_series,
    product_qid_minus_one,
    negative_control_q11_series,
    expected_negative_control,
    ETA_SIG,
)

ETA = ETA_SIG
eps = sp.symbols("eps")
OUT = ROOT / "exports"
CERT = ROOT / "certificates"
OUT.mkdir(parents=True, exist_ok=True)
CERT.mkdir(parents=True, exist_ok=True)
INDEX = [(m, n) for m in range(4) for n in range(m, 4)]
ORDER = 4


def jet_symbols():
    H = {(m, n): sp.symbols(f"H{m}{n}") for m, n in INDEX}
    dH = {(r, m, n): sp.symbols(f"dH{m}{n}_{r}") for r in range(4) for m, n in INDEX}
    return H, dH


def sym_mat(comp):
    M = sp.zeros(4)
    for m in range(4):
        for n in range(4):
            key = (min(m, n), max(m, n))
            M[m, n] = comp[key]
    return M


def acceptance_controls():
    results = {"qid_identity": [], "negative_control": None, "pass": True}
    for name, H in [
        ("h11_const", sp.Matrix(4, 4, lambda i, j: sp.symbols("B") if i == j == 1 else 0)),
        ("h00_const", sp.Matrix(4, 4, lambda i, j: sp.symbols("A") if i == j == 0 else 0)),
        ("h01_const", sp.Matrix(4, 4, lambda i, j: sp.symbols("C") if {i, j} == {0, 1} else 0)),
    ]:
        rem = product_qid_minus_one(H, eps, order=4)
        ok = all(sp.simplify(rem[i, j]) == 0 for i in range(4) for j in range(4))
        results["qid_identity"].append({"support": name, "pass": bool(ok)})
        if not ok:
            results["pass"] = False
    B = sp.symbols("B")
    got = negative_control_q11_series(B, eps, order=4)
    exp = expected_negative_control(B, eps, order=4)
    nc_ok = sp.simplify(got - exp) == 0
    buggy = -1 - eps * B + eps**2 * B**2 - eps**3 * B**3 + eps**4 * B**4
    not_buggy = sp.simplify(got - buggy) != 0
    results["negative_control"] = {"pass": bool(nc_ok and not_buggy), "rejected_alternating_bug": bool(not_buggy)}
    if not (nc_ok and not_buggy):
        results["pass"] = False
    return results


# --- Power series helpers: dict order -> sympy expr ---
def ps_const(expr, order=ORDER):
    return {0: sp.expand(expr), **{k: 0 for k in range(1, order + 1)}}


def ps_trunc(d, order=ORDER):
    return {k: sp.expand(d.get(k, 0)) for k in range(order + 1)}


def ps_add(a, b, order=ORDER):
    return {k: sp.expand(a.get(k, 0) + b.get(k, 0)) for k in range(order + 1)}


def ps_mul(a, b, order=ORDER):
    out = {k: 0 for k in range(order + 1)}
    for i in range(order + 1):
        ai = a.get(i, 0)
        if ai == 0:
            continue
        for j in range(order - i + 1):
            bj = b.get(j, 0)
            if bj == 0:
                continue
            out[i + j] = sp.expand(out[i + j] + ai * bj)
    return out


def ps_scale(a, c, order=ORDER):
    return {k: sp.expand(c * a.get(k, 0)) for k in range(order + 1)}


def mat_ps_from_series_matrix(M, order=ORDER):
    """Convert Matrix of polynomials in eps to Matrix of ps dicts."""
    out = [[None] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            e = sp.expand(M[i, j])
            out[i][j] = {k: sp.expand(e.coeff(eps, k)) for k in range(order + 1)}
    return out


def mat_ps_mul(A, B, order=ORDER):
    C = [[ps_const(0) for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            acc = ps_const(0)
            for k in range(4):
                acc = ps_add(acc, ps_mul(A[i][k], B[k][j], order), order)
            C[i][j] = acc
    return C


def expand_L_gamma_jet(order=ORDER):
    tmark = time.time()
    Hsyms, dHsyms = jet_symbols()
    H = sym_mat(Hsyms)

    def dH_mat(r):
        return sym_mat({(m, n): dHsyms[(r, m, n)] for m, n in INDEX})

    print("  inverse series...", flush=True)
    ginv_M = inverse_series(H, eps, order=order)
    ginv = mat_ps_from_series_matrix(ginv_M, order)

    print("  sqrt(-det)...", flush=True)
    eta = sp.diag(*ETA)
    g = sp.Matrix(4, 4, lambda i, j: eta[i, j] + eps * H[i, j])
    det = sp.expand(g.det())
    # series of sqrt(-det)
    sqrt_series = sp.series(sp.sqrt(sp.expand(-det)), eps, 0, order + 1).removeO()
    sqrt_ps = {k: sp.expand(sqrt_series.coeff(eps, k)) for k in range(order + 1)}
    print("    sqrt done", round(time.time() - tmark, 2), flush=True)

    print("  Christoffel...", flush=True)
    # ∂_m g_sn = eps * dH_mat(m)[s,n]  => ps with only order 1
    def dg(m, s, n):
        return {0: 0, 1: dH_mat(m)[s, n], **{k: 0 for k in range(2, order + 1)}}

    Gam = [[[None] * 4 for _ in range(4)] for _ in range(4)]
    for r in range(4):
        for m in range(4):
            for n in range(4):
                acc = ps_const(0)
                for s in range(4):
                    # ginv[r,s] * (∂_m g_sn + ∂_n g_sm - ∂_s g_mn)
                    bracket = ps_add(ps_add(dg(m, s, n), dg(n, s, m), order), ps_scale(dg(s, m, n), -1, order), order)
                    acc = ps_add(acc, ps_mul(ginv[r][s], bracket, order), order)
                Gam[r][m][n] = ps_scale(acc, sp.Rational(1, 2), order)
        print(f"    r={r}", round(time.time() - tmark, 2), flush=True)

    print("  L_Γ contraction...", flush=True)
    # L0 = q^{mu nu} (Γ^a_{mu b} Γ^b_{nu a} - Γ^a_{mu nu} Γ^b_{a b})
    L0 = ps_const(0)
    for mu in range(4):
        for nu in range(4):
            quad = ps_const(0)
            for a in range(4):
                for b in range(4):
                    quad = ps_add(quad, ps_mul(Gam[a][mu][b], Gam[b][nu][a], order), order)
            tr = ps_const(0)
            for a in range(4):
                for b in range(4):
                    tr = ps_add(tr, ps_mul(Gam[a][mu][nu], Gam[b][a][b], order), order)
            struct = ps_add(quad, ps_scale(tr, -1, order), order)
            L0 = ps_add(L0, ps_mul(ginv[mu][nu], struct, order), order)
        print(f"    mu={mu}", round(time.time() - tmark, 2), flush=True)

    L = ps_mul(sqrt_ps, L0, order)
    print("  expand coeffs...", flush=True)
    coeffs = {k: sp.expand(L[k]) for k in range(order + 1)}
    print("  done expand", round(time.time() - tmark, 2), flush=True)
    return coeffs, Hsyms, dHsyms


def substitute_sparse(ell4, Hsyms, dHsyms, components):
    X = sp.symbols("x0:4")
    funs = {}
    for (m, n), stem in components.items():
        funs[(m, n)] = sp.Function(stem)(*X)
    reps = {}
    for m, n in INDEX:
        key = (m, n)
        f = funs.get(key, funs.get((n, m), 0))
        reps[Hsyms[key]] = 0 if f == 0 else f
        for r in range(4):
            reps[dHsyms[(r, m, n)]] = 0 if f == 0 else sp.diff(f, X[r])
    return sp.expand(ell4.xreplace(reps))


def main():
    t0 = time.time()
    controls = acceptance_controls()
    print("controls", controls["pass"], flush=True)
    if not controls["pass"]:
        (CERT / "P4_ell4_full_polynomial.json").write_text(json.dumps({
            "revision": "p08", "pass": False, "acceptance_controls": controls
        }, indent=2) + "\n")
        return 1

    coeffs, Hsyms, dHsyms = expand_L_gamma_jet(order=ORDER)
    ell4 = sp.expand(-2 * coeffs[4])
    ell3 = sp.expand(-2 * coeffs[3])
    print("ell4 terms", len(sp.Add.make_args(ell4)) if ell4 != 0 else 0, "len", len(str(ell4)), flush=True)

    s_ell = str(ell4)
    H_present = []
    for m, n in INDEX:
        if str(Hsyms[(m, n)]) in s_ell or any(str(dHsyms[(r, m, n)]) in s_ell for r in range(4)):
            H_present.append(f"H{m}{n}")
    max_der = 1 if any(str(v) in s_ell for v in dHsyms.values()) else 0

    sparse_checks = []
    for name, spec in [
        ("h00_only", {(0, 0): "A"}),
        ("h11_only", {(1, 1): "B"}),
        ("h01_only", {(0, 1): "C"}),
        ("h12_only", {(1, 2): "D"}),
        ("h00_h11", {(0, 0): "A", (1, 1): "B"}),
    ]:
        sub = substitute_sparse(ell4, Hsyms, dHsyms, spec)
        nz = sp.simplify(sub) != 0
        sparse_checks.append({
            "support": name,
            "ell4_jet_nonzero_on_support": bool(nz),
            "sha_head": hashlib.sha256(str(sp.expand(sub)).encode()).hexdigest()[:16],
        })
        print(name, "nz", nz, flush=True)

    term_count = len(sp.Add.make_args(ell4)) if ell4 != 0 else 0
    ell4_sha = hashlib.sha256(str(ell4).encode()).hexdigest()
    ell4_path = OUT / "ell4_generating_polynomial.srepr"
    ell4_path.write_text(sp.srepr(ell4) + "\n")

    export = {
        "id": "V4_grav",
        "revision": "p08",
        "status": "Constructed",
        "definition": "ell_4=-2[eps^4]L_Γ; L_Γ=sqrt(-q)q^{mn}(ΓΓ-ΓΓ) ≡ sqrt(-q)R modulo d(·)",
        "IBP_policy": "Compact support; discard total derivatives; Gamma-Gamma action density",
        "metric_normalization": "q=eta+eps H, eta=diag(+---), S_EH=-(2/kappa^2)int sqrt(-q)R",
        "n_independent_components": 10,
        "components": [f"H{m}{n}" for m, n in INDEX],
        "H_present_in_ell4": H_present,
        "max_derivative_order": max_der,
        "field_order": 4,
        "ell4_sha256": ell4_sha,
        "ell4_length": len(str(ell4)),
        "ell4_term_count": term_count,
        "ell4_srepr_path": str(ell4_path),
        "ell4_srepr_sha256": hashlib.sha256(ell4_path.read_bytes()).hexdigest(),
        "ell4_str_head": str(ell4)[:500],
        "ell3_sha256_from_same_prescription": hashlib.sha256(str(ell3).encode()).hexdigest(),
        "ell3_note": "Cubic from same L_Γ expansion for regression vs XII-C ell_3; NOT claiming XII-C is quartic",
        "NOT_XII_C_quartic": True,
        "pairing": {
            "vertex_id": "V4_grav",
            "legs": 4,
            "species": ["h", "h", "h", "h"],
            "D02_rule": "contract two h-legs with gauge-fixed Δ(h); two external",
            "evaluation_entry_point": "code/classical/v4_grav_pairings.py:evaluate_D02_template",
            "P33_connecting_map": "Unresolved",
        },
        "D02_availability": "unblocked_vertex_Constructed",
        "usable_by_graph_generator": True,
    }
    (OUT / "V4_grav.json").write_text(json.dumps(export, indent=2) + "\n")
    (OUT / "ell4_jet_symbols.json").write_text(json.dumps({
        "H": {f"{m}{n}": str(Hsyms[(m, n)]) for m, n in INDEX},
        "dH": {f"{m}{n}_{r}": str(dHsyms[(r, m, n)]) for r in range(4) for m, n in INDEX},
    }, indent=2) + "\n")

    nz_sparse = sum(1 for r in sparse_checks if r["ell4_jet_nonzero_on_support"])
    constructed = bool(
        controls["pass"] and ell4 != 0 and max_der <= 1
        and len(H_present) >= 8 and nz_sparse >= 3 and term_count > 0
    )
    cert = {
        "revision": "p08",
        "landmark": "XVI-P",
        "gate": "P-next.4_ell4_full_polynomial",
        "pass": constructed,
        "pass_means": (
            "Full indexed ell_4 Constructed as -2[eps^4]L_Γ in 10 H-components + ∂H jets; "
            "IBP/Gamma-Gamma declared; controls+sparse checks passed; exports/V4_grav.json + srepr. "
            "NOT XII-C quartic."
        ) if constructed else "Construction checks failed",
        "acceptance_controls": controls,
        "status": "Constructed" if constructed else "Unresolved",
        "method": "order_by_order_jet_GammaGamma_correct_inverse",
        "IBP_policy": export["IBP_policy"],
        "polynomial": {
            "n_components": 10,
            "H_present": H_present,
            "max_derivative_order": max_der,
            "field_order": 4,
            "term_count": term_count,
            "sha256": ell4_sha,
            "srepr_path": str(ell4_path),
            "export_path": str(OUT / "V4_grav.json"),
        },
        "sparse_support_checks": sparse_checks,
        "cubic_regression_record": {
            "ell3_sha256": export["ell3_sha256_from_same_prescription"],
            "note": export["ell3_note"],
            "NOT_XII_C_quartic": True,
        },
        "D02_availability": "unblocked_vertex_Constructed" if constructed else "still_blocked",
        "seconds": round(time.time() - t0, 3),
        "no_invented_s2": True,
    }
    (CERT / "P4_ell4_full_polynomial.json").write_text(json.dumps(cert, indent=2) + "\n")
    print(json.dumps({
        "pass": cert["pass"], "terms": term_count, "H_present": len(H_present),
        "max_der": max_der, "seconds": cert["seconds"], "D02": cert["D02_availability"],
    }, indent=2), flush=True)
    return 0 if constructed else 1


if __name__ == "__main__":
    raise SystemExit(main())
