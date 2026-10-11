#!/usr/bin/env python3
"""XVI-P single source of conventions (declared once, read by every builder; p13 adds the milestone definitions).

Nothing here is a result. Every sign that is a *result* (antifield-shift orientation,
odd left/right derivative signs, sigma_A in S_af, s2 per sector) is DERIVED in the
builders and compared against these declarations by the tests.
"""
from __future__ import annotations
from fractions import Fraction

REVISION = "p13"
DATE = "2026-10-08"
XVI_M_PIN = "41aa109935f40ddee3109de62c46329c189b5408007970cc90ed5611dc4739ea"

ETA = (1, -1, -1, -1)                 # eta = diag(+---)
A_GHOST = Fraction(1, 2)              # a = 1/2 (XVI-N)
INDEX = [(m, n) for m in range(4) for n in range(m, 4)]   # 10 independent h_{mn}, m<=n

# Metric parametrisation (declared; s2 is DERIVED from it, not assumed)
METRIC_PARAMETRISATION = "g_{mu nu} = eta_{mu nu} + kappa h_{mu nu}  (h lowered, affine in h)"
GHOST_SCALING = "xi^mu = kappa a c^mu  (geometric diffeo parameter; XVI-N: s h = (1/2) L_c(eta + kappa h))"

# XVI-N def:antibracket (frozen orientation; used verbatim by graded_jets.bracket)
ANTIBRACKET = ("(F,G) = sum_A int [ (d^R F/d Phi^A)(d^L G/d Phi*_A) "
               "- (d^R F/d Phi*_A)(d^L G/d Phi^A) ]")
GENERATOR_RULE = "s Phi^A = (S, Phi^A);  s Phi*_A = (S, Phi*_A)  (XVI-N: NOT (Phi*,S))"

# Field table: name -> (Grassmann parity, ghost number, conjugate antifield name)
FIELDS = {
    "h":   (0, 0, "K"),     # h_{mn}, m<=n ; K^{mn} its canonical conjugate
    "c":   (1, 1, "cs"),    # c^mu (upper)
    "cb":  (1, -1, "cbs"),  # cbar_mu (lower)
    "b":   (0, 0, "bs"),    # b_mu (lower)  Nakanishi-Lautrup
    "phi": (0, 0, "phis"),  # massless scalar
}
ANTIFIELDS = {v[2]: (1 - v[0], -1 - v[1], k) for k, v in FIELDS.items()}

# Off-diagonal multiplicity of the symmetric pairing int h*^{mu nu} X_{mu nu} (all 16 comps):
#   K^{mn} = w_{mn} h*^{mn},  w = 1 (m=n), 2 (m<n).  Canonical pair: (h_{mn}, K^{mn}), m<=n.
def w_mult(m, n):
    return 1 if m == n else 2

# Gauge fermion (declared, XVI-N): Psi = -i int cbar_mu (2 D^mu[h] - b^mu),
#   D^mu[h] = d_nu h^{mu nu} - (1/2) d^mu h^rho_rho   (linear de Donder)
PSI = "Psi = -i int cbar_mu (2 D^mu[h] - b^mu),  D^mu[h] = d_nu h^{mu nu} - (1/2) d^mu tr h"

# Actions (declared normalisations)
S_EH = "S_EH = -(2/kappa^2) int sqrt(-g) R ;  ell_k = -2 [eps^k] L_GammaGamma ; S_EH = sum_k kappa^(k-2) int ell_k (mod boundary)"

# Boundary identity (p11, CORRECTED orientation; proved generically in boundary_identity.py):
#   L_GG := sqrt(-g) g^{mn}(G^a_{mb} G^b_{na} - G^a_{mn} G^b_{ab}),
#   B^mu := sqrt(-g)(g^{mu nu} G^l_{nu l} - g^{l nu} G^mu_{l nu}),
#   Ricci convention of ell4_verify: R^r_{s m n} = d_m G^r_{n s} - d_n G^r_{m s} + G^r_{m l}G^l_{n s} - G^r_{n l}G^l_{m s},
#   R_{s n} = R^r_{s r n}, R = g^{s n} R_{s n}
#   =>  sqrt(-g) R - L_GG = - d_mu B^mu     (p09/p10 stated "+ d_mu B^mu": wrong; integrated action unaffected)
BOUNDARY_IDENTITY = "sqrt(-g) R - L_GG = - d_mu B^mu,  B^mu = sqrt(-g)(g^{mu nu} G^l_{nu l} - g^{l nu} G^mu_{l nu})"
L_GG = "L_GG = sqrt(-g) g^{mn}(G^a_{mb} G^b_{na} - G^a_{mn} G^b_{ab})"

# Polarisation convention (p11, ONE convention everywhere):
#   V4[h1,h2,h3,h4] := [t1 t2 t3 t4] ell_4(sum_i t_i h_i) = D^4 ell_4(0)[h1,h2,h3,h4]   (UNnormalised 4th variation)
#   normalised symmetric form = V4 / 4!  (not used for vertices).
#   Feynman vertex (from e^{iS}, S2 = int ell_4 at order kappa^2): i kappa^2 V4 (no 1/4!: the 1/4! of
#   S2 = (1/4!) D^4 S2[h,h,h,h] is cancelled by the 4! Wick assignments of external legs).
#   D02 (quartic tadpole, two legs contracted with the graviton propagator): graph symmetry factor 1/2 enters at
#   GRAPH level only.  D02 is not evaluated.
POLARIZATION = ("V4[h1..h4] = [t1 t2 t3 t4] ell_4(sum t_i h_i) = D^4 ell_4(0)[h1..h4] (unnormalised); "
                "normalised symmetric form = V4/4!; Feynman vertex i kappa^2 V4; D02 graph symmetry factor 1/2")
CERT_PREFIX = "P13"
S_SCALAR = ("S_phi = (1/2) int sqrt(-g) g^{mu nu} d_mu phi d_nu phi (m=0);  "
            "sqrt(-g) g^{mu nu} = eta + kappa a1 + kappa^2 a2 (XI-A a1,a2; O2_scalar_action_authoritative)")

BASELINE = "S_inv (unprepared, sigma_eps == 1, no insertion I_t); prepared S_D keeps (S_D,S_D) != 0 (XVI-N prop:broken-square)"

BOUNDARY_POLICY = ("Integrated identities modulo total derivatives only for the integrated action "
                   "(the sign/orientation of a discarded divergence never affects the integrated equivalence) "
                   "under compact-support (or periodic plane-wave momentum-conserving) boundary data. "
                   "No divergence is discarded after multiplication by a non-constant switch or test.")

HARD_STOPS = {
    "quantum_inputs_evaluated": "not_earned",
    "projected_identity_verified": "not_earned",
    "D02_quantum_evaluated": False,
    "D12_quantum_evaluated": False,
    "D12_status": "Missing",
    "symmetry_restored": False,
    "O1_closure": "NOT_CLOSED",
    "insertion_status": "Frozen_negative_obstruction_preserved",
    "XV_B_opened": False,
    "Route_B_discharged": False,
    "P5_opened": False,
    "loop_evaluations_performed": False,
    "u_R_c_delta_added": False,
}

NOT_PREMISES = ["En01-A", "En01-B", "En01-C", "Em01 family", "Em02-B", "Em02-D",
                "En02-A", "En02-B", "VII-E", "VIII-B"]

# ---------------------------------------------------------------------------------------------------------------
# p13: AUTHORITATIVE milestone definitions (used verbatim by the manuscript, RELEASE_STATUS, the milestone ledger and
# the completion dossier).  Older wording ("P-next.N", "P4 = coupled one-loop restoration", "P.3--P.5 out of scope")
# is history only: archival/p02_p09/notes/P_scope.tex and archival/p12/.  P.4 is classical readiness, NOT coupled
# one-loop restoration.
MILESTONES = {
    "P.3": "fixed output projection + exhaustive coefficient dependencies + graph topology inventory "
           "(complete for the declared ch target)",
    "P.4": "required classical action, transformations, source terms, gauge map and master verification "
           "(classical readiness earned); P.4 means classical readiness, NOT coupled one-loop restoration",
    "P.5_entry": "quantum prescription, amplitude rules and counterterm domain fixed",
    "P.5_calculation": "coefficients evaluated and renormalized",
    "P.5_identity": "projected defect computed and, if possible, cancelled",
}
MILESTONE_ORDER = ("P.3", "P.4", "P.5_entry", "P.5_calculation", "P.5_identity")
MILESTONE_HISTORY = ("archival/p02_p09/notes/P_scope.tex (p06-p08 'P-next.N' labels; its table row 'P4 coupled one-loop "
                     "restoration' is SUPERSEDED: P.4 = classical readiness); archival/p12/ (p12 used 'classical "
                     "readiness' without milestone labels)")

# p13: the three quantum input slots of the projected identity: NAMED DEPENDENCIES, not evaluated coefficients.
# Row ids are the surviving rows of certificates/P13_ch_source_audit.json (checked by dossier.py).
QUANTUM_INPUT_SLOTS = [
    {"slot": "hh at kappa^2", "Gamma1_pattern": "h^2", "row": "(S0,Gamma1^[2]) s2 K:K.c",
     "graphs": ["D01", "D02", "D03", "D11", "D12"]},
    {"slot": "K'c at kappa^2", "Gamma1_pattern": "K.c", "row": "(S0,Gamma1^[2]) s1 h:h^2", "graphs": ["D13"]},
    {"slot": "h one-point at kappa", "Gamma1_pattern": "h", "row": "(S1,Gamma1^[1]) s2 K:K.c.h",
     "graphs": ["D14a", "D14b", "D14c"]},
]
