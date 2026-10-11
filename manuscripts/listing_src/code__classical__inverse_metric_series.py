#!/usr/bin/env python3
"""Shared weak-field inverse-metric series (X-A / XI-A controls).

For q = eta + eps H (lowered indices), with Minkowski eta = diag(+1,-1,-1,-1)
so eta^{-1} = eta and eta^2 = I:

  q^{-1} = eta - eps (eta H eta) + eps^2 (eta H eta H eta)
         - eps^3 (eta H eta H eta H eta) + eps^4 (...) + O(eps^5)

Equivalently with h1 = eta*H*eta:
  h2 = h1 * eta * h1
  h3 = h2 * eta * h1
  h4 = h3 * eta * h1

WRONG (o57-v4 bug): h2 = h1*h1 (matrix product of two raised tensors without eta).
"""
from __future__ import annotations
import sympy as sp

ETA_SIG = (1, -1, -1, -1)


def eta_matrix():
    return sp.diag(*ETA_SIG)


def inverse_series(H: sp.Matrix, eps, order: int = 4) -> sp.Matrix:
    """Return q^{-1} series truncated through eps^order (inclusive)."""
    eta = eta_matrix()
    h1 = sp.expand(eta * H * eta)
    powers = [h1]
    for _ in range(2, order + 1):
        powers.append(sp.expand(powers[-1] * eta * h1))
    ginv = eta
    sign = -1
    for k in range(1, order + 1):
        ginv = ginv + sign * (eps**k) * powers[k - 1]
        sign = -sign
    return sp.Matrix(4, 4, lambda i, j: sp.expand(ginv[i, j]))


def q_matrix(H: sp.Matrix, eps) -> sp.Matrix:
    eta = eta_matrix()
    return sp.Matrix(4, 4, lambda i, j: sp.expand(eta[i, j] + eps * H[i, j]))


def product_qid_minus_one(H: sp.Matrix, eps, order: int = 4) -> sp.Matrix:
    """Return q * q^{-1}_series - I, coefficients through eps^order should vanish."""
    q = q_matrix(H, eps)
    qinv = inverse_series(H, eps, order=order)
    prod = sp.expand(q * qinv)
    I = sp.eye(4)
    return sp.Matrix(4, 4, lambda i, j: sp.series(prod[i, j] - I[i, j], eps, 0, order + 1).removeO())


def negative_control_q11_series(B, eps, order: int = 4):
    """For H with only H_11=B: q^{11} = -1 - eps B - eps^2 B^2 - ... (all minus)."""
    H = sp.zeros(4)
    H[1, 1] = B
    qinv = inverse_series(H, eps, order=order)
    return sp.series(qinv[1, 1], eps, 0, order + 1).removeO()


def expected_negative_control(B, eps, order: int = 4):
    s = -1
    for k in range(1, order + 1):
        s = s - (eps**k) * (B**k)
    return sp.expand(s)
