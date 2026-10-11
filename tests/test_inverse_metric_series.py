#!/usr/bin/env python3
"""Acceptance tests for inverse-metric series (X-A / XI-A) BEFORE any O.2 hash."""
from __future__ import annotations
import sys
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code" / "classical"))
from inverse_metric_series import (  # noqa: E402
    inverse_series,
    product_qid_minus_one,
    negative_control_q11_series,
    expected_negative_control,
    ETA_SIG,
)


def fail(msg: str):
    raise SystemExit("INVERSE_METRIC_FAIL: " + msg)


def test_qid_identity_sparse():
    """q * q^{-1}_series = 1 + O(eps^5) on several sparse H."""
    eps = sp.symbols("eps")
    X = sp.symbols("x0:4")
    configs = []
    # constant diagonal
    H1 = sp.zeros(4)
    H1[1, 1] = sp.symbols("B")
    configs.append(("h11_const", H1))
    # function supports
    A = sp.Function("A")(*X)
    B = sp.Function("B")(*X)
    C = sp.Function("C")(*X)
    H2 = sp.zeros(4)
    H2[0, 0] = A
    configs.append(("h00", H2))
    H3 = sp.zeros(4)
    H3[0, 1] = C
    H3[1, 0] = C
    configs.append(("h01", H3))
    H4 = sp.zeros(4)
    H4[0, 0] = A
    H4[1, 1] = B
    configs.append(("h00_h11", H4))
    for name, H in configs:
        rem = product_qid_minus_one(H, eps, order=4)
        for i in range(4):
            for j in range(4):
                # residual through O(eps^4) must vanish (series removeO keeps through eps^4)
                if sp.simplify(rem[i, j]) != 0:
                    fail(f"{name}: (q qinv - I)[{i},{j}] = {rem[i, j]} nonzero through O(eps^4)")


def test_negative_control_diagonal():
    """h_11=B => q^{11} = -1 - eps B - eps^2 B^2 - eps^3 B^3 - eps^4 B^4 (NOT alternating)."""
    eps, B = sp.symbols("eps B")
    got = negative_control_q11_series(B, eps, order=4)
    exp = expected_negative_control(B, eps, order=4)
    if sp.simplify(got - exp) != 0:
        fail(f"negative control failed: got {got}, expected {exp}")
    # Explicitly forbid the buggy alternating pattern -1 -eps B + eps^2 B^2 - eps^3 B^3 + ...
    buggy = -1 - eps * B + eps**2 * B**2 - eps**3 * B**3 + eps**4 * B**4
    if sp.simplify(got - buggy) == 0:
        fail("got the BUG pattern (alternating higher signs)")


def test_XA_first_orders():
    """X-A: q^{mn} = eta^{mn} - kappa h^{mn} + kappa^2 (h^m_a h^{an} - k^{mn}) first corr minus, quadratic hh plus.
    At k=0: first correction minus raised h; quadratic plus (eta H eta H eta).
    """
    eps = sp.symbols("eps")
    H = sp.zeros(4)
    for i in range(4):
        for j in range(i, 4):
            H[i, j] = sp.symbols(f"H{i}{j}")
            H[j, i] = H[i, j]
    qinv = inverse_series(H, eps, order=2)
    eta = sp.diag(*ETA_SIG)
    h1 = eta * H * eta
    # coeff of eps^0
    for i in range(4):
        for j in range(4):
            c0 = sp.expand(qinv[i, j].coeff(eps, 0))
            if sp.simplify(c0 - eta[i, j]) != 0:
                fail(f"eps^0 mismatch at {i}{j}")
            c1 = sp.expand(qinv[i, j].coeff(eps, 1))
            if sp.simplify(c1 - (-h1[i, j])) != 0:
                fail(f"eps^1 must be -h_up (minus); got {c1} vs {-h1[i, j]}")
            c2 = sp.expand(qinv[i, j].coeff(eps, 2))
            h2 = sp.expand(h1 * eta * h1)
            if sp.simplify(c2 - h2[i, j]) != 0:
                fail(f"eps^2 must be + (h eta h); got {c2} vs {h2[i, j]}")


def main():
    test_qid_identity_sparse()
    test_negative_control_diagonal()
    test_XA_first_orders()
    print("test_inverse_metric_series: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
