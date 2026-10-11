# XVI-P — revision p23 (stage release on the O.1 direction: O.1 requirement recorded, one-loop power counting and enlarge-rule check, P.6 entry inventory (κ³ three-point, not evaluated), polynomial-domain refusal for d; P.5 renormalized at one loop κ² for the two-point functions with QdS external legs; bulk symmetry not claimed; O.1 NOT_CLOSED) — 2026-10-10

XVI-P is **unregistered**. The package is evidence in the sense of XVI-O `conv:package` (an archive, a listing and a
hash manifest are not a mathematical certificate). It is not a series certificate and does not update XVI-O, where
`prop:kappa2-master` stays Partial, `symmetry_restored` is false and O.1 is NOT_CLOSED.

## p23: stage release on the O.1 direction (honest partial)

p23 follows the p22 independent rebuild (PASS, no mismatches; report sha256 023e5b83…, bound to tree 1bc6edff… /
zip ade2fa5c…, same box). Disclosed contract revision: one delimited block is appended to `code/p5_entry/dred.py`
(polynomial-domain refusal for d). The p18 core and the p22 block are byte-identical (`contract_registry.p23_registered`).
New in p23: `code/p5_calc/{p23_conventions,power_counting,release_p23}.py`, `tests/test_p23.py`,
`certificates/P23_*`, `manuscript/notes/P23_O1_scope.tex`, `provenance/XVI-O/O_quantum_target.json` (a verbatim
read-only copy of the O.1 ledger, sha pinned) and `archival/p22/`.

**O.1 exact requirement.** From XVI-O `ledgers/O_quantum_target.json` (o70-sync), O.1 closes iff the one-loop κ²
bulk two-point sector on S_inv closes under a VERIFIED retained quantum identity. That needs O.2 (classical κ²
master including grav ℓ₄), O.4, O.5, O.6 and O.7 all earned, and the target must first be enlarged if the identity
constrains more legs at κ². In XVI-P scope: the inventory (O.4), graph evaluation (O.5), the projected identity and
counterterm solution (part of O.6/O.7) and the enlarge rule. Out of scope: O.2 and the bulk ST4b identity, which are
XVI-O/XVI-N items and stay untouched. **O.1 is therefore not closable inside XVI-P.**

**Power counting (exact).** Every vertex is κ^(legs−2), counting sources. So a one-loop graph with E legs is κ^E.
The one-loop identity at κ² is (S⁽⁰⁾,Γ₁⁽²⁾) + (S⁽¹⁾,Γ₁⁽¹⁾), which involves only E = 2 and E = 1. The mechanical
enumeration reproduces the frozen κ² inventory exactly (9/9) and the one-point row (3 graphs). **The enlarge rule
is not triggered:** there is no one-loop three-point sector at κ².

**P.6 entry.** Three-point first appears at κ³: 15 one-loop graphs (hhh 5, hφφ 4, c c̄ h 2, K c h 2, c c c* 1,
φ* c φ 1). This is an inventory at topology level only. Amplitude rules, the counterterm domain, evaluation, the
defect and closure are **not done**.

**Fixes (p22 review).**
- The opaque d now refuses the polynomial domain from outside sympy: rem/prem/div/resultant/compose/Poly.shift/
  Poly.rem and similar raise. Internal renames of d are admitted only to a Dummy, so Matrix.subs(d→y) raises.
  A live probe runs 9 forms × 4 expressions.
- The gate checks ρ = 1/2, the E2 coefficient −1/16, the SE coefficient +1/8 and the summed h·h coefficients against
  both the pinned values and the archived p22 certificate.
- The title line carries the two-point / QdS qualifier.

Flags: the p22 earnables are unchanged. New earned flags: O1_requirement_recorded, one_loop_power_counting_verified,
P6_entry_inventory, d_poly_domain_refusal_verified and EV_values_verified. independent_rebuild_passed_p22 = true
(same box); p23 independent pending. bulk_symmetry_restored = false; O.1 NOT_CLOSED.

## p22: evanescent components, evanescent counterterms, runtime d guard (disclosed contract revision)

p22 follows the p21 independent rebuild (PASS, no mismatches; report sha256 8a582b33…, bound to tree b835353f… /
zip a71d6b52…, same box). It carries ONE disclosed contract revision (`p22_conventions.CONTRACT_REVISION`):
evanescent counterterms admitted outside the p14r 4D domain, and a delimited additive runtime-guard block in
`code/p5_entry/dred.py` (p18 core byte-identical, registered in `code/p5_calc/contract_registry.py`). New in p22:
`code/p5_calc/{p22_conventions,evanescent,contract_registry,release_p22}.py`, `tests/test_p22.py`,
`certificates/P22_*`, `manuscript/notes/P22_evanescent.tex`, `archival/p21/`. Every other change is listed in
`DISCLOSED_REVISIONS_P22`.

**EV-M2: PROVEN (exact, opaque d).** The evanescent D11 (and D01/D03) poles are local evanescent operators. The
renormalised evanescent remainder vanishes identically on 4D external legs at every d. No matching to XVI-O is
asserted, because both natural d-dim continuations of the XVI-O kernel are refuted.
`D11_matching_verified_scope` = 4D components: M2 discharged; evanescent components: EV-M2 proven; NOT matched to XVI-O.

**EV-CT: earned.** The counterterm coefficients are −(pole) (per graph and summed, in `certificates/P22_evanescent.json`).
The K′.c E2 coefficient is −1/16 and the c̄Σ_SE c partner is +1/8.
- Full σ0 closure including the evanescent counterterms holds in h.c, c.b and c.cbs.
- The projected identity is unchanged: all slot values are 0.
- Finite remnants vanish on hatted legs. With Q4S external traces there is a finite 7i p²(â·b̂ p² − â·p b̂·p)/60, disclosed as a scheme choice.
- Six mutations are detected.

**P.5 calculation status: renormalized** (one loop, κ², two-point functions, external legs QdS).

**Runtime d guard.** 30 bypass forms × 4 expressions all raise `PrematureD4Substitution`. These include the reviewer's
p21 forms and the power-base hole. Ordinary algebra is unchanged. The residue (`is` tests, string round-trips,
Poly.rep) is disclosed and covered only by the static scan, which is kept as secondary.

**Gate.** No tools/ or notes prefix exemptions. Every changed, added or removed file must be disclosed.

Flags: evanescent_M2_verified, evanescent_counterterms_verified, d_runtime_guard_verified = earned;
independent_rebuild_passed_p21 = true (same box); independent_rebuild_passed (p22) = pending;
bulk_symmetry_restored = false; O.1 NOT_CLOSED.

## p21: small release from p20 (no scope expansion)

p21 follows the findings of the p20 independent rebuild (PASS, no mismatches; report sha256 e8f358f9…, bound to tree
2c0aa153… / zip ca32ce01…, same box, not a second machine). No contract revision. The disclosed p21 revisions of the
p20 layer are `d11_pin.py` and `release_p20.py` (`p20_conventions.py` byte-identical). New in p21:
`code/p5_calc/{p21_conventions,release_p21}.py`, `tests/test_p21.py`, `certificates/P21_*`,
`manuscript/notes/P21_absolute_pin.tex`, `archival/p20/`.

**Absolute D11 pin (p20: OPEN) — derived, PASS.** The sign and magnitude of the D11 UV pole follow from ½Tr ln of
the minimal scalar loop under the package's declared conventions (all checked verbatim in `d11_pin.absolute_pin`):
- G = Γ^(2) (amplitude rules iΓ₁ = ∫pref·N/∏(q²+i0) and G6 Ĝ = −i·pref/κ²·∫N/(D1D2));
- Wick direction from N_eps = iS_eps/(16π²) and the certified bubble pole +1/ε, so iS_M = −S_E and L_M = −L_E;
- g = η + κh, η = (+,−,−,−), S_φ = ½∫√−g g^{μν}∂φ∂φ (ξ = 0);
- heat kernel L_E,div = −a₂/(32π²ε), a₂ = C²/120 + R²/72; Minkowski forms C² → ½p⁴hP2h, R² → 3p⁴hP0h.

Result: Γ^(2)|pole = κ²/(16π²ε)·[p⁴P2/240 + p⁴P0s/24], equal to the package pole κ²N_eps Ĝ/ε (c2 = −i/240,
c0 = −i/24) exactly, ratio 1 for both spins. No convention choice is external; the external inputs are mathematics only
(the a₂ coefficients and the heat-kernel pole formula). ×2 and sign flip keep the 10:1 ratio and are detected by the
absolute pin; drop D11 and a structure swap are detected by the ratio pin. Flag `D11_absolute_pin_verified`: earned.

**Gate.** The top-level `absolute_pin_status` / `ratio_pin_status` must equal the nested statuses. Run standalone,
`release_p20.py` re-checks the p18 layer (quantum_inputs_evaluated earned) and the graph inventory instead of trusting
the P19 layer record. `release_p21.py` re-checks every lower layer live and requires every package change vs the p20
zip to be a disclosed revision.

**Scan (allow-list; a check, not a proof).** `tests/test_p21.py::scan4` complements the enumerated pattern scans
with an allow-list. Refused everywhere except at reviewed sites (listed with reasons in `p21_conventions.py`):
- any expression-tree decomposition (`.args`, `.func`, `make_args`, `as_ordered_terms`, `as_coefficients_dict`, …);
- any sympy callable alias (`Q = sp.Poly`, `import sympy as X`, `from sympy import Y as Z`);
- symbol constructors with non-literal names (`Symbol(*['d'])`, `Symbol(**{...})`, computed names);
- value calls (`subs`, `evalf`, `N`, `limit`, `Lambda`, …) mentioning d, and rebinding of d.

All eight reviewer misses are caught. The test verifies that they were missed by the older pattern scans.

Runtime check: the stored exact-d D11 amplitudes re-parse with the opaque d (type check) and reproduce their poles
only through `substitute_d`. It found a **limitation**: `expr.subs(d, v)` is not intercepted when d occurs only as a
power base (sympy's Pow substitution). The contract is unchanged in p21; no package value path uses it; the static
rule refuses it; the released premature-d4 demonstrations used components that raise. This is recorded as an open
issue for a future contract revision.

**Disclosure.** The p20 edit of `manuscript/notes/P19_defect.tex` is listed in
`p21_conventions.DISCLOSED_MANUSCRIPT_REVISIONS`. The reference keys `/p19/change_log_vs_p18` and
`/p20/change_log_vs_p19`, which were recomputed on the current tree, are renamed `…_recomputed_on_current_tree`. The
logs as released stay in the pinned archives.

**Status.** independent_rebuild_passed_p20 = true (same box; bound to the p20 tree, not inherited). The p21
independent rebuild is pending. Projected (ch-only) results as in p20; bulk_symmetry_restored false; O.1 NOT_CLOSED.

## p20: correction release of p19 (no scope expansion)

p20 corrects p19 from the findings of the p19 independent rebuild (PASS with findings; report sha256 1b01f1d8…,
bound to tree fcf90354… / zip da924275…, same box). No contract revision; the p14r contract and the p15–p18 layers
are byte-identical. The disclosed p20 revisions of the p19 layer are `defect.py` and `release_p19.py`. New in p20:
`code/p5_calc/{d11_pin,p20_conventions,release_p20}.py`, `certificates/P20_*`, `manuscript/notes/P20_correction.tex`.

**Erratum K1 (p19 text retracted).** p19 said that full σ0 closure of the MS-bar counterterm fails with the derived
ghost-equation factor +1 and needs −1 (unresolved). That was a Grassmann-orientation bookkeeping error:
- the route-G densities are built in the order (c,cb), but the P15 Σ coordinates are (cb,c)-oriented;
- V[c.cb#k] = −V[(cb,c)#k], and the measured ratio is −1, −1.

Corrected:
- Σ pole in (c,cb) coordinates: (+3/8, −1/4); local part (2/3, −5/12).
- The derived factor is +1, and the **complete** MS-bar counterterm (h.h + c.K + c.cb) is σ0-closed in every ghost +1
  sector (h.c, c.b, c.cbs).
- Without the c.cb term, or with Σ unconverted, there are 88 entries in c.b.
- Tree controls: V_S0[cb,c] = 2iD V_S0[K,c], and σ0(S0_Kc + S0_cbc) = 0.
- Quotient of the full data including Σ: 0.

**Restoration redefined.** `projected_restoration_verified` now means full σ0 closure of the complete one-loop κ²
MS-bar S_ct (including c.cb, Σ held fixed). Scope: that counterterm only, not bulk symmetry and not O.1.
- Status: **earned**.
- The p19 criterion (P_ch σ0(S_ct) = 0, x = 0) follows from the identity plus locality. It is kept only as a labelled
  route-consistency control, and it holds.

**Blind spots.**
- The full-closure mutation detector:
  - detects drop D13 and flip K.c (c.b, 88 entries);
  - detects drop D01, drop D03, flip D03 and D03 ×2 (h.c, 280 entries);
  - detects the p19 orientation error.
  - Drop D11 stays blind: D11 is transverse, so it is closed by itself.
- **D11 pin** (`certificates/P20_D11_pin.json`): spin projection of the 4D D11 UV pole gives c2 = −I/240 and
  c0 = −I/24, so spin-0 : spin-2 = 10 : 1.
  - Derived from P18_D11, with the package orbit convention and transversality checked.
  - The C² and R² quadratic forms are derived here (C² → ½P2, R² → 3P0s, Gauss–Bonnet → 0).
  - This equals the minimal-scalar a2 prediction (1/120)C² + (1/72)R², i.e. 1/240 : 1/24. The literature source
    (Birrell–Davies §6.2; 't Hooft–Veltman 1974) is external.
  - **Ratio pin: PASS.** It detects drop D11.
  - **Absolute pin: OPEN in p20 [superseded in p21: derived, PASS].** The magnitudes agree up to a common factor −I, but the map Ĝ → a2 is not derived. An
    overall ×2 is caught only by this open pin and by M2.

**J1 wording.** The Q(i) counts are the real dimensions under a compatible real structure.

**Scan.** Still a pattern check, not a proof. Added patterns:
- Add(*listcomp over e.args);
- aliased Poly import;
- Poly.__call__;
- as_coefficients_dict;
- functools.reduce rebuild;
- Symbol(name=…);
- explicit-constructor rebuild.

A standalone release-gate reject now leaves no stale RELEASE_STATUS.json.

**Rebuild flags.**
- independent_rebuild_passed_p19 = true (tree fcf90354… / zip da924275…; same box).
- The p20 independent rebuild is pending.

**Hard stops:** bulk_symmetry_restored = false regardless; O.1 NOT_CLOSED; XVI-P unregistered.

## p19: the projected one-loop κ² ch-identity defect (`code/p5_calc/defect.py`, `certificates/P19_defect.json`)

p19 keeps the p14r contract and the p15–p18 calculation layers byte-identical: `release_p19.py` checks them against
pinned sha256, and p19 makes no contract revision.

**Defect.** Δ = P_ch[(S_Ψ, Γ_Ψ)]_{ħκ²} is assembled from every evaluated input:
- hh row: D01 + D02 + D03 + D11 + D12;
- K.c row: D13;
- one-point row: D14a–c.

It is computed exactly in d (pole, coefficient of L, MS-bar local part) for seven external assignments.

**Result: Δ = 0 in every part and every assignment.**
- **Why zero:** each row vanishes separately in the projected slot. No counterterm cancellation and no cancellation
  between rows is involved.
  - hh row: full-row transverse decoupling. D01 and D03 are each nonzero and cancel in the slot; D11 is transverse by
    itself; D02 = D12 = 0.
  - K.c row: D13 reaches the slot only via T1/E1, and A_T1 = A_E1 = 0 exactly in d.
  - One-point row: the tadpoles vanish.
- **Rests on:** M2 / the D11 matching on the 4D components only, and the evanescent decoupling proofs (E2, hh
  evanescent / full row).
- **Evanescent parts:** assembled explicitly; they are zero. The evanescent poles are regulated and not subtracted.

**Counterterm domain** (Route G over Q(i); Route C covariant):
- rank σ0|D = 5, dim D∩ker σ0 = 6 = dim D∩Im σ0, cohomology 0, quotient 5;
- rank P_ch σ0 = 3 (both routes).
- Quotient coordinates of the h.h + c.K Γ1 data (without Σ; route-G (c,cb) labels): pole (0, 0, 0, −3/8, 1/4),
  L (0, 0, 0, 3/8, −1/4), local (0, 0, 0, −2/3, 5/12). This is −[Σ]: Σ itself has (+3/8, −1/4), and the data including Σ
  have quotient 0 (p20).
- **Solve:** x = 0 (ZERO; no residual).

**Flags** (definitions in `flag_definitions`; the gate re-checks each from the certificate content):
- `projected_defect_computed`: earned.
- `projected_identity_verified`: earned. Δ = 0 for the *regulated* Γ1.
- `projected_restoration_verified`: earned. **Redefined in p20** as full σ0 closure of the complete MS-bar counterterm
  (see p20 above). The p19 definition, renormalised Δ_R = 0 with x = 0, is now a route-consistency control.
- `bulk_symmetry_restored`: false (hard stop). O.1 stays NOT_CLOSED.

**K1: corrected in p20; the p19 text is retracted** (orientation erratum above).

**J1 (finding about the p14r contract; contract not modified).** The p14r counterterm-domain counts are artefacts of
a re/im split over Q:

| | Im | quotient | D∩ker | P_ch σ0 rank |
|---|---|---|---|---|
| p14r, over Q (split) | 3 | 8 | 5 | 4 |
| over Q(i) | 6 | 5 | 6 | 3 |

The Q(i) counts are the real dimensions under a compatible real structure (wording corrected in p20). p19 reproduces both
sets of counts.

**Controls and mutations.** All controls are true. Eight mutations change the outcome:
- drop D01; drop D03; flip the D03 phase; double D03; wrong hh projection; wrong K.c projection; naive 4D D03 →
  OBSTRUCTION;
- D13 with Gt dropped → CANCELLABLE.

Recorded blind spots of the projected identity: drop D11, drop D13, flip the K.c row sign. In p20, the full-closure
detector covers drop D13 and flip K.c, and the D11 ratio pin covers drop D11.

**p18 reviewer findings.**
- I1: publication fails closed. It requires the p18 layer's quantum_inputs_evaluated, the inventory recheck and
  projected_defect_computed; the gate mutations are in `tests/test_p19.py`.
- I2: extended scan, still a pattern check, not a proof; reviewed Poly coefficient sites.
- I3: P.5_calculation status reads "evaluated; 4D sector renormalized (MS-bar, declared domain); evanescent regulated
  (poles retained, not subtracted), decoupled from the ch slots".

**Rebuild flags.**
- independent_rebuild_passed_p18 = true (bound to tree bfab3b4b… / zip 7c7d5451…; same-box).
- The p19 independent rebuild is pending.

## p18 (layer): M2, D11 and the full hh slot (`code/p5_calc/d11.py`, `certificates/P18_*.json`)

* p18 build-process fixes (disclosed; caught by fail-closed from-scratch builds): (i) `code/p5_calc/d11.py` took the
  input inventory before writing `P18_D11.json` (a stale copy masked this in place; presync #2 failed, q not earned) --
  now written first; (ii) `tools/rebuild_from_source.py` still required the p17 criterion `D11_evaluated is False`
  (author rebuild #1: all 290 values equal, only `release_accepted` failed) -- now requires D11_evaluated,
  D11_matching_verified (scope "4D components"), quantum_inputs_evaluated earned and the full hh-row decoupling.

p18 keeps the p14r contract and the p15/p16/p17 calculation layers. Their files are byte-identical, and
`release_p18.py` checks them against pinned sha256. p18 adds the following.

* **M2 (the D11 matching premise): DISCHARGED on the 4D components** (`P18_D11_M2.json`).
  * *Route B (exact).* The nonlocal (log) part of P^DR at d → 4 is −(iκ²/16π²) L Σ_s A_s(4) S_s(p). The XVI-O
    side is (iκ²/4) R R K̂(p) · c_FT log(−p²−i0), with P̂_mn = p_m p_n − η_mn p².
    * Their equality, X_AB = −(i/4) R_A R_B (D̂2/60 + D̂0/18), holds exactly on all 100 component pairs.
    * The difference therefore has a polynomial Fourier transform and is supported at {0}. That is M2, and it is
      μ-independent on U.
  * *c_FT, calibrated twice.* (a) From the library DR bubble (FT[D_F²] = −N_ε MB, D_F² = A²u), independently of
    XVI-O. (b) As −r, with the XVI-O residue r = −iπ². Both give c_FT = iπ².
  * *Route A (structural).* M1 is re-run (100/100). The frozen XVI-O code, imported read-only, re-derives α = A²/60
    and β = A²/18 and verifies K u = T on all 256 components.
  * *Controls and mutations.* D11 is transverse exactly in d. Six mutations are each rejected: α↔β, off-diagonal
    weight 1, flipped FT sign, doubled symmetry factor, D01 in place of D11, and β = 0.
  * *Cited analytic inputs.* The Fourier transform of (Q−i0)^ζ (Gel'fand–Shilov), and the fact that a polynomial
    in p is the transform of a distribution supported at 0. Route A also uses XVI-O lem:BV_rules_on_U.
  * *Scope.* The 8 evanescent (g̃) structures of D11 have nonzero log coefficients. They are ε-scalar components
    outside M2's 4D statement.
  * *M3 consequence.* L_match is supported at 0 and lies in the 2-dimensional transverse h·h subspace (transverse,
    homogeneous of degree four). Its coordinates need the XVI-O finite constant of u^R and are not computed. Per M4
    it is booked on the P side; u^R_μ is unmodified and there is no cδ.
* **D11 evaluated** (`P18_D11.json`) under the declared prescription: operational DRED (d opaque), MS-bar, Feynman
  +i0, N4, M3 bounds 4/8/4.
  * There are 14 structures, 6 of them 4D. The fit is exact and unique; the FP and PV routes agree exactly in d; the
    result is exchange symmetric; the log coefficient equals minus the pole.
  * Premature d = 4 is refused and would shift the local parts. Four mutations are rejected.
  * 4D poles: p_m p_n p_r p_s −i/60; g_mn p_r p_s and g_rs p_m p_n i/80; g_mn g_rs −i/80; g_mr p_n p_s i/480;
    g_mr g_ns −i/480.
  * In p14r coordinates the 4D pole is i(−1/160, −1/480, 1/80, 1/240, −1/120) = i(1/240 k1 − 1/120 k2), which is
    transverse.
* **Full hh slot, row (S0, Γ1^[2]) s2 K:K·c, with D01 + D02 + D03 + D11 + D12: DECOUPLED (proof).**
  * p_m G_D11 = 0 identically in d, for both the 4D and the evanescent parts. D11 therefore decouples by itself;
    D01 and D03 decouple only as a sum.
  * X = 0 for all seven external assignments. This includes c hat / h tilde (H2), where X_D01 = −X_D03 =
    p⁴ ã·b̃ ĉ·p/16, as the reviewer found.
  * No evanescent structure survives: **D11 does not reopen the evanescent question**, and there is no contract
    revision.
  * The summed 4D pole is i(41/80 k1 − 43/120 k2), which is transverse.
  * Caveat: D11 phase and symmetry-factor mutations are invisible to the slot. They are tested by M2 instead.
  * The summed evanescent poles of the hh Green function (8 structures) are nonzero but transverse. Renormalising
    that Green function itself is outside the projection and not claimed.
* **Flags.**
  * `D11_matching_verified` = true, with **`D11_matching_verified_scope` = "4D components"**, and
    `D11_evaluated` = true.
    * The evanescent components are the 8 g̃-carrying structures: components with an index pair in DRED's
      ε-scalar (4−d) directions.
    * Their matching status is `not_applicable_not_verified`: XVI-O is strictly 4D and has no counterpart.
    * They are retained (R6) and drop out of the ch slot.
  * M3 is now **unconditional on the 4D components**: L_match is supported at {0}, within the 4/8/4 bounds.
  * The prescription was applied as stated, and both points are checked per structure:
    * exactly degree four: every structure has total momentum degree 4;
    * N4: the order-0/2 contacts it excludes do not arise (massless), so it removes nothing here.
  * `quantum_inputs_evaluated` = earned. The required inputs are every graph of the three surviving ch rows of
    the frozen ledger:
    * hh (S0,Γ1^[2]) s2 K:K·c: D01 regulated, D02 vanishing, D03 regulated, D11 renormalized-4D/regulated, D12
      vanishing;
    * K·c (S0,Γ1^[2]) s1 h:h²: D13 evaluated;
    * one-point (S1,Γ1^[1]) s2 K:K·c·h: D14a, D14b and D14c vanishing.

    None is Missing or unevaluated. The gate re-reads every status from its own certificate.
  * Not earned: `projected_defect_computed`, `projected_identity_verified` and `projected_restoration_verified`.
  * Unchanged: `symmetry_restored` = `bulk_symmetry_restored` = false; O.1 NOT_CLOSED; the insertion stays frozen;
    XV-B and XIV-J are unopened; Route B is not discharged.
  * `independent_rebuild_passed_p17` = true: report 92542a22…, tree 2a5a6317… / zip 7f4f61df…, same-box caveat,
    not inherited. `independent_rebuild_passed` (p18) is pending.
* **Review fixes (p17 independent rebuild).**
  * **H1.** The scan (`tests/test_p18.py`) also flags Poly(e, d)(4), as_poly(d)(4), all_coeffs (Horner),
    type(x)(…) and __class__(…) rebuilds, getattr indirection, aliased sympify imports and assignments, sympify
    locals whose 'd' is not the opaque d, and plain Symbol('d')/symbols('d'). Planted violations are detected. It is
    a pattern check, not a proof.
  * **H2.** The seventh assignment is added.
  * **H3.** Stale comments are corrected: dred.py, and the PARSE_SITES_REVIEWED header, which now distinguishes
    stored d-free strings.
  * **H4.** Verbatim listings use straight quotes (the upquote mechanism via textcomp).
  * **H5.** `parse_d(srepr(e))` raises PlainDimensionSymbol; this is now documented.
  * The dred.py change is the one disclosed contract revision of p18 and is documentation only: its AST without
    docstrings is pinned equal to p17.

## p17: the hh evanescent poles and the ch slot (`code/p5_calc/hh_slot.py`, `certificates/P17_hh_slot.json`)

p17 keeps the p14r contract and the p15 and p16 calculation layers. The p15/p16 files are byte-identical, and
`release_p17.py` checks them against pinned sha256. p17 adds the following.

* **Where the hh self-energy enters.** D01 and D03 enter exactly one ch-dependency row (computed from
  `ledgers/P13_ch_dependency_rows.json`): (S0, Γ1^[2]) s2 K:K·c, with Γ1 pattern h². The row also holds D02 and
  D12 (both 0) and D11 (not evaluated). The slot is X = ∫ (s h)_(mn) G^{(mn)(rs)} h_(rs), where s h is read off the
  K·c monomial of S0. Its exact, unique covariant form is (s h)_{(mn)ν} = (i/2)(η_{mν} p_n + η_{nν} p_m), which is
  **longitudinal**.
* **Verdict: DECOUPLED (proof), as the sum D01 + D03, not graph by graph.**
  * p_m (G_D01 + G_D03)^{(mn)(rs)} = 0 identically in d. This holds for the 4D part and the evanescent part
    separately; every g̃ structure cancels, e.g. g̃_rs p_n: −i p⁴/(8(d−1)) + i p⁴/(8(d−1)).
  * Hence X_{D01+D03} = 0 for all six external assignments, and with D02 = D12 = 0 no evanescent structure
    survives in the slot.
  * Controls: X_D01 and X_D03 are each nonzero, including their evanescent parts.
  * Mutations rejected: wrong relative sign of D03, D03 doubled, D03 evanescent part dropped, and the trace operator
    in place of s h.
  * At one loop the projection is linear in Γ1, so there is no evanescent × evanescent product.
* **No contract revision for the slot.** No evanescent h·h counterterm is added, and the counterterm quotient is
  unchanged. The summed evanescent poles of the hh Green function are nonzero (8 structures, recorded) but transverse.
  Renormalizing the hh Green function itself would need evanescent h·h counterterms; this is outside the projection
  and not claimed.
* **4D poles: coordinates and constraint.** Span membership in the five p14r h·h directions is automatic (they span
  all five pair-symmetric 4D structures). The sharper, non-automatic statement is transversality:
  * the longitudinal map has rank 3 on the coordinates, so the transverse subspace is 2-dimensional, with
    k1 = (1/2, −1/2, −1, 1, 0) and k2 = (1, 0, −2, 0, 1);
  * z_D01 = i(−27/160, −71/240, 19/60, 11/20, −13/30) and z_D03 = i(7/96, 1/24, −1/8, −1/24, 1/12) are not
    transverse;
  * their sum z = i(−23/240, −61/240, 23/120, 61/120, −7/20) = i(61/120 k1 − 7/20 k2) is transverse.
* **Phase convention (G6).** G = κ² N_ε Ĝ, N_ε = iS_ε/16π².
  * D01 and D03 have real export prefactors (κ²/2, −κ²), so A(d) carries an overall i.
  * D13 (prefactor iκ²) is real.
  * Since s h = i(…), X_hh is real like the D13 slot.
  * The D01/D03 relative phase is tested by the cancellation (mutation M1). The D13-vs-hh relative phase is not
    tested, since both contributions vanish.
* **Review fixes (p16 independent rebuild):**
  * **G2.** This is the one disclosed contract revision of p17, in `dred.py`. The guarded loader
    `dred.parse_d(text)` parses 'd' as the opaque d, and `dred.assert_opaque_d(expr)` with `PlainDimensionSymbol`
    detects a plain `Symbol('d')`. Only functions are added; P13–P16 certificate values equal the p16 reference.
  * **G1/G3.** The wording is corrected (what the runtime guard refuses; a Wild-pattern match is not refused). The
    static AST scan (`tests/test_p17.py`) now also flags:
    * replace with any non-literal query (named function or lambda);
    * builtin eval/exec, parse_expr, `.func(*args)` rebuilds;
    * every sympify/S call without guarded locals, unless it is on the reviewed list
      `p17_conventions.PARSE_SITES_REVIEWED` (24 sites: the loader itself, sympy objects, or d-free prefactor strings).
    It is a pattern check, not a proof. Planted violations are detected.
  * **G4.** The change log vs p16 lists the p17 reference-values file as added.
* **Flags.** `independent_rebuild_passed_p16` = true: archived report 1a886196…, bound to tree 90b4a665… / zip
  56d5887d…, same-box caveat, not inherited. `independent_rebuild_passed` (p17) is pending. The following are
  unchanged: `D11_evaluated` = false, `quantum_inputs_evaluated` = not_earned, O.1 NOT_CLOSED,
  `symmetry_restored` = `bulk_symmetry_restored` = false.

## p16: E2 analysis and Batch C (`code/p5_calc/`, `certificates/P16_*.json`, `RELEASE_STATUS.json`)

p16 keeps the p14r contract and the p15 calculation layer. The p15 calculation files are byte-identical, and
`release_p16.py` checks them against pinned sha256. p16 adds the following.

* **E2 (D13 evanescent pole 1/16, A_E2 = 3/(16(d−1))): DECOUPLED from the ch-projected slot. This is a proof**
  (`P16_E2_evanescent.json`, `code/p5_calc/e2_evanescent.py`). D13 enters the ch projection only through the row
  (S0, Γ1^[2]) s1 h:h², X = ∫ G_{(mn)ν} c^ν E^{(mn)(rs)} h_(rs), where E is the h² operator of S0 (linearized EH; exact
  covariant form, unique fit).
  * L1: E is transverse, p_m E = 0. Only g4·p = p is used; there is no trace, so this is exact in d.
  * L2: E2 is longitudinal in (mn).
  * L3: E2·E = 0 identically, for every external assignment (Q4S, QdS, mixed). It is exactly 0, not O(ε).
  * L4 (control): T1 and E1 give nonzero slot values, and A_T1 = A_E1 = 0, so D13's ch-slot contribution is 0.
  * Mutations rejected: the gauge-fixed operator q²P in place of E, E1 in place of E2, and a wrong index slot.
  * Consequence: no evanescent counterterm and no contract change for E2. The E2 pole remains a UV pole of the
    ε-scalar K′·c component (R6, retained), which is relevant only outside the ch projection and is not claimed. D13
    stays `regulated`.
* **Batch C: D01 and D03 evaluated** (`P16_batchC.json`, `code/p5_calc/batchC.py`, `covariant.py`).
  * **Finding C1.** The p14r per-component lift gives Gt-quadratic component sums for rank-4 numerators (D03: 10 of 100
    components). There, the linear realization Gt = (4−d)M is not faithful.
  * **Covariant route.** Batch C therefore uses a covariant route with the same rules R1–R6 and no contract change:
    1. the exact covariant numerator is fitted from the frozen export and verified on 100 of 100 components;
    2. the lift η → g4 is made;
    3. two loop routes are used, Feynman parameters and `dred.reduce_tensor` + J + S0, and they agree exactly in d;
    4. then ĝ = g4 − g̃ on the free indices.
  * **Controls.** D13 is reproduced exactly. The integrands are regenerated from S_Ψ and equal the export (100/100
    for both graphs). The 4D poles lie in the span of the five p14r h·h directions. Seven mutations are rejected.
  * **Status.** Both graphs are `regulated`: the 4D sector is renormalized, but the evanescent (g̃) poles are nonzero
    and retained, and no evanescent h·h counterterm is declared.
  * **Values.** These are in the generated table `manuscript/body/P16-results-table.tex` and in the science volume.
  * **D11 is NOT evaluated** (M2 undischarged). `D11_matching_verified` = false, and `quantum_inputs_evaluated` is
    not earned. The hh slot is incomplete.
* **Review fixes (p15 independent rebuild):**
  * **F3.** This is the one disclosed contract revision of p16, in `code/p5_entry/dred.py`. The opaque d now refuses
    `replace(d, ·)`, pattern matching and the lambdify/code-printer paths. Paths that cannot be hooked
    (callable-query replace, `Poly.eval`, string round trips) are excluded by a static AST scan. P13–P15 certificate
    values equal the p15 reference values.
  * **F4.** The footer label comes from one variable (`p16_conventions.VERSION_LABEL` → `manuscript/version.tex`).
    The PDF readback covers the D13, Batch A, Batch C and E2 value blocks and checks every footer.
  * **F5.** All changed files (contract and non-contract) relative to the p15 zip are listed in
    `RELEASE_STATUS.json` → `change_log_vs_p15`, with the base pinned in `archival/p15/p15_source_files.json`.
    The disclosed test revisions are `tests/test_p14.py` and `tests/test_p15.py`, described in
    `p16_conventions.DISCLOSED_TEST_REVISIONS_P16`.
* **Rebuild flags.**
  * `independent_rebuild_passed_p15` = true is bound to the p15 tree 79f53752… and zip 54325c1f… (report 6bc760c2…,
    pinned). It carries a same-box caveat and is not inherited by p16.
  * `independent_rebuild_passed` (p16) is pending.
  * `author_rebuild_passed` refers to the p16 tree only.
* **Unchanged hard stops.** XVI-M pin 41aa1099…; insertion frozen; O.1 NOT_CLOSED;
  `symmetry_restored`/`bulk_symmetry_restored` false; no Missing → zero by convention; XVI-P unregistered; no cδ in
  u^R_μ; XVI-N massless obstruction respected; XV-B and XIV-J unopened; Route B not discharged.

The top-level `RELEASE_STATUS.json` is the p16 status. The p15 layer record is `certificates/P15_release.json`, and the
p15 release is archived in `archival/p15/`.

## p15 (layer active in p16; released as p15, archived in `archival/p15/`): first P.5 calculation (`code/p5_calc/`, `certificates/P15_*.json`)

The graphs are evaluated under the p14r prescription: DRED R1–R6 with ĝ/g̃ algebra, contractions before the Laurent
expansion, d symbolic and evanescent parts retained; Feynman +i0; MS-bar with N_ε = iS_ε/(16π²).

* **Library** (`P15_integral_library.json`): A0, B0 and tensor reduction in ĝ. It is checked against Feynman
  parameters exactly in d, and numerically at d = 2.6, 3.3, 3.7.
* **Scaleless rule S0** is stated explicitly: ∫dᵈl (l²)ᵏ/(l²)^ν := 0, with a UV/IR reading. ω = 0 is a
  1/ε_UV − 1/ε_IR cancellation; for ω ≠ 0 neither side has a pole at d = 4. Applying S0 to an integral with a scale
  raises an error. Missing is never replaced by zero by convention.
* **Batch A** (D02, D12, D14a, D14b, D14c): all five are *vanishing_under_declared_prescription*. They have no UV pole,
  a zero finite part, and need no p14r counterterm. Every member is a pure power divergence (ω = 2, 4), so the DR
  zero is **not** a 1/ε_UV − 1/ε_IR cancellation.
  * With an IR-regulator mass, the poles go as κ²m⁴hh and κ²m²p²hh (contacts excluded by N4), or κm⁴h (the κ¹
    basis is empty). They vanish as m → 0.
  * Two routes are compared: the frozen dred lift + S0, and an independent symmetric integration.
  * D12 (κ² hh) is kept separate from the order-κ one-point slot.
  * D12_status moves from Missing to *vanishing_under_declared_prescription*. This is **derived**, not imported
    from XVI-O.
* **Batch B, D13** (κ² K′·c, V[K′_(mn)(−p), c^ν(p)] = κ² N_ε Ĝ, Ĝ = Σ Aᵢ(d) Tᵢ·B0):

  | structure | A(d) | UV pole | MS-bar finite part |
  |---|---|---|---|
  | T1 = η_mn p_ν p² | 0 | 0 | 0 |
  | T2 = (η_mν p_n + η_nν p_m) p² | (4d−7)/(16(d−1)) | 3/16 | 1/3 − (3/16) L |
  | T3 = p_m p_n p_ν | 3(2−d)/(8(d−1)) | −1/4 | −5/12 + (1/4) L |
  | E1 = G̃_mn p_ν p² (evanescent) | 0 | 0 | 0 |
  | E2 = (G̃_mν p_n + G̃_nν p_m) p² (evanescent) | 3/(16(d−1)) | 1/16 | 1/6 − (1/16) L |

  Here L = log(−p²/μ² − i0).
  * The 4D pole is local and lies in the span of the three p14r c·K′ directions, with coordinates (0, 3/8, −1/4).
  * The (d−4)×pole terms shift the local part (T2 by −1/24, T3 by +1/12). Setting d = 4 first gives a different
    finite part.
  * The **evanescent pole (E2) is nonzero**. The p14r contract declares no evanescent counterterm, so D13's status
    is *regulated*: its 4D sector is renormalized, and the evanescent pole is recorded but not absorbed (an open
    contract item).
  * Controls:
    * the frozen export with the dred Pipeline equals the regenerated integrand with Feynman parameters, exactly
      in d;
    * the exact covariant fit holds;
    * the ghost equation holds: 2i D^ρ[G] equals the evaluated ghost self-energy, whose pole is in the p14r c·c̄
      span at (−3/8, 1/4);
    * the structural R5 safeguard is active.
  * Five mutations each change the result and are rejected: wrong ghost-loop sign, premature d = 4, dropped
    evanescent part, wrong symmetry factor, and wrong K′/c ordering.
* **Not evaluated:** D01, D03 (Batch C) and D11 (M2). No slot of the identity is complete.
  * quantum_inputs_evaluated, projected_defect_computed, projected_identity_verified and
    projected_restoration_verified remain **not earned**.
  * bulk_symmetry_restored is false and O.1 is NOT_CLOSED.
  * The insertion stays frozen, XV-B/XIV-J stay closed, and Route B is not discharged.
* **Flags:**
  * `batchA_evaluated` and `D13_evaluated` each have execution, claim and scope parts.
  * `independent_rebuild_passed_p14r = true` is bound to the p14r tree a64c0ae3… and zip 19e8bf59…. Same-box
    caveat: it ran on the same machine, not a second one.
  * `independent_rebuild_passed` (p15) is pending.

### Disclosed p14r contract revision (inside p15)

This revision addresses finding F1 of the p14r independent rebuild.

**What was wrong.** The p14r `PrematureD4Substitution` guard in `code/p5_entry/dred.py` was a heuristic. On
η^{rs}∫l_r l_s/(l²−m²) = J it had two failures:
* a **false positive**: it rejected the correct, d-free result;
* a **false negative**: under the premature_d4 mutation, eta_trace_Gt reintroduces d through tr g̃ = 4 − d. The
  result is dJ/4, with a finite error of −m⁴/2, and the guard did not catch it.

**What p15 changes.**
* The guard is replaced by a **structural, provenance-based safeguard**. d is an opaque symbol: subs/xreplace of d
  raise unless they come from `dred.substitute_d`, which records every authorised use.
* Numeric traces of ĝ/g̃ are refused.
* The R5 docstring is corrected.
* The reviewer's η-trace toy and the A0 (+m⁴/2) and B0 (−p²/6) mixing toys are regression tests
  (`tests/test_p15.py`).

Rules R1–R6 are unchanged. Every other p14r contract file is byte-identical, and `release_p15.py` checks this
against pinned sha256. **Released p14r values are unaffected**: p14r applied `Pipeline.laurent` only to toy
placeholders.

In p15 the top-level `RELEASE_STATUS.json` was the p15 status (in p16 it is the p16 status; the p15 layer record is `certificates/P15_release.json`). The p14r contract record is `certificates/P14_release.json`.
The p14r release itself is archived in `archival/p14r/`.

## p14r contract (active in p15; released as p14r, archived in `archival/p14r/`)

p14 opened **P.5 entry only**. It fixed the quantum object, one prescription, the D11 matching note, the counterterm
domain and executable (symbolic) amplitude rules. No loop integral is evaluated; the Batch A/B/C integrals belong to
p15+.

## p14r repair (P.3/P.4 code byte-identical; no loop evaluation; p14 archived in `archival/p14/`)

1. **Operational DRED** (`code/p5_entry/dred.py`, `certificates/P14_dred_rules.json`):
   * metric rule: g⁽⁴⁾ = ĝ + g̃ with tr ĝ = d and tr g̃ = 4 − d;
   * the loop momentum l **and** the external momenta p lie in the d-dimensional space (p·g̃ = 0);
   * the exported lower components are lifted as l_r = l·e₍ᵣ₎, and the vertex tensors with η → g⁽⁴⁾;
   * Gram/PV reduction with ĝ projections, ĝ_rs = η_rs − G̃_rs;
   * **all contractions happen before the Laurent expansion**, with d kept symbolic through the MS-bar subtraction and
     finite-part extraction.
   Evanescent remainders **do** arise; the p14 statement that none arise is withdrawn. Two toy checks use generic
   J = a/ε + b + cε:
   * T1 has finite part a/8 + b/4; premature d = 4 would give b/4 and is caught;
   * T2 = −(4−d)/d·J has finite part −a/2.
   The mutations premature d = 4, tr ĝ = 4 and expand-before-contract are all rejected. Siegel; Stöckinger
   hep-ph/0503129; Signer–Stöckinger arXiv:0807.4424 are cited as background only.
2. **D11 M3** is conditional on M2. The scalar extension has scaling degree 4. *Kernel scaling degree at most eight;
   degree of divergence at most four; hence the local ambiguity has derivative order at most four*
   (sd(∂^αδ) = 4 + |α|). The bounded contact space has order 0: 2 (μ⁴), order 2: 4 (μ²), order 4: 5 (transverse 2).
   Exactly degree four is the explicit normalization condition N4; it is not implied by "no other scale".
3. **Counterterm wording.** *Eight candidate directions modulo the computed exact equivalences, before imposing the
   relevant identity constraints.* This is not a cohomological classification: D ∩ ker σ₀ has not been computed.
4. **Coverage.**
   * W5 regenerates only D14a–c, D11 and D13.
   * The new W6 (`code/p5_entry/hessian_route.py`) regenerates D01, D02, D03 and D12 from the Tr-log expansion of the
     field-dependent Hessian of S_Ψ, with its own (h,b) inverse. It matches the exported integrands exactly.
   * The renamed check is a "Ward contraction with two free on-shell graviton legs and an off-shell gauge leg". The
     generic symbolic off-shell Ward identities remain the primary evidence.
5. **Isolated-copy gate tests.** The copies now contain every frozen input.
   * The unmutated copy is accepted, with the freeze true.
   * P.5-only mutations keep the freeze TRUE, turn the named contract flag false, and are rejected.
   * Classical mutations make the freeze false and are rejected.

## Milestones (authoritative; `RELEASE_STATUS.milestones`, `ledgers/P14_milestones.json`)

| milestone | definition | status |
|---|---|---|
| P.3 | fixed output projection + exhaustive coefficient dependencies + graph topology inventory (complete for the declared `ch` target) | complete (frozen P.5 input) |
| P.4 | required classical action, transformations, source terms, gauge map and master verification (classical readiness earned). **P.4 means classical readiness, NOT coupled one-loop restoration.** | earned (frozen P.5 input) |
| P.5 entry | quantum object, prescription, D11 matching definition, counterterm domain and amplitude rules fixed | earned iff all five contract flags hold **and** P.3/P.4 are frozen |
| P.5 calculation | coefficients evaluated and renormalized | open (p15+) |
| P.5 identity | projected defect computed and, if possible, cancelled | open |

**P.5 entry rule.** `P5_entry_earned = quantum_action_defined ∧ quantum_prescription_defined ∧ D11_matching_defined ∧
counterterm_domain_defined ∧ amplitude_rules_verified ∧ P3_P4_frozen_as_P5_inputs`.

Older milestone wording is history only (`archival/p02_p09/notes/P_scope.tex`, `archival/p12/`, `archival/p13/`).

## Freeze of P.3/P.4 (dependency of P.5 entry)

`P3_P4_frozen_as_P5_inputs = F1 ∧ F2 ∧ F3` (`code/p5_entry/freeze_p13.py`), re-checked on every release:
* **F1**: the independent rebuild of **p13** passed (112/112 reference values, 77 independent comparisons, no
  mismatches). The archived report `archival/p13/reproducibility/independent_rebuild_report_p13.json` is pinned by
  sha256 and bound to the p13 source tree `2b1baf33…` and zip `2f85a566…`.
  **Caveat:** that rebuild ran on the **same box** (shared kernel, TeX Live, poppler) in a fresh venv from the
  source-only zip; it was **not on a second machine**.
* **F2**: the 54 frozen classical P.3/P.4 files are byte-identical to the p13 tree (`archival/p13/frozen_p13_inputs.json`).
* **F3**: the regenerated classical values equal the archived p13 reference values.

The p13 flag is bound to the p13 tree. The p14r tree has its own `independent_rebuild_passed`, which stays `pending`.

## P.5 entry contract (`manuscript/notes/P14_P5_entry_contract.tex`)

| flag | certificate | content |
|---|---|---|
| `quantum_action_defined` | `certificates/P14_quantum_object.json` | S_Ψ, Γ_Ψ in transformed variables; integrated fields; **b retained** (elimination computed but not used); external antifields; 1PI and normalization conventions; κ/loop bookkeeping; classical pullback kept separate |
| `quantum_prescription_defined` | `certificates/P14_prescription_D11_matching.json` + `certificates/P14_dred_rules.json` | `P14_DRED_MSbar_FeynmanI0`: operational dimensional reduction (rules R1–R6, executable, tested), MS-bar, Feynman `+i0` on every propagator; re-earned in p14r only with `dred_rules_verified` |
| `D11_matching_defined` | same | M0–M7 against the frozen XVI-O D11 (S_inv baseline, frozen u^R_μ without cδ, M3 conditional on M2 with normalization condition N4, residue −iπ² only after constructive holomorphy). **`D11_matching_verified = false`.** |
| `counterterm_domain_defined` | `certificates/P14_counterterm_domain.json` | local ghost-number-0, one loop, κ¹: 0 structures; κ²: explicit basis of 11 (h.h 5, c.c̄ 2, c.K′ 3, φ.φ 1); eight candidate directions modulo the computed exact equivalences, before imposing the relevant identity constraints (D ∩ ker σ₀ not computed); order-bounded EFT constraint list (XIV-J and XV-B not opened) |
| `amplitude_rules_verified` | `certificates/P14_amplitude_rules.json` | vertices, propagators, routing, multiplicities, symmetry factors, Grassmann signs, i-factors; symbolic integrands for D01–D03, D12, D13 (priority), D14a–c (`exports/P14_integrands/`); D11 reference only; controls W1–W6 (W5: D14a–c, D11, D13; W6 Hessian route: D01, D02, D03, D12); Ward/Bose controls; mutations rejected |

Hard stops (all enforced by the release gate):
- `quantum_inputs_evaluated`, `projected_defect_computed`, `projected_identity_verified`, `projected_restoration_verified`: not earned;
- `bulk_symmetry_restored = symmetry_restored = false`; D12 **Missing** (never zero); D02/D12 not evaluated;
- O.1 NOT_CLOSED; insertion frozen; XV-B and XIV-J not opened; Route B not discharged; no cδ on u^R;
- P.5 calculation and P.5 identity not opened; no loop evaluated;
- projected vs bulk kept distinct (XVI-N `lem:field-only`; the XVI-O kernel Ward is not functional ST4b);
- XVI-A … XVI-O not edited; XVI-M pin `41aa109935f40ddee3109de62c46329c189b5408007970cc90ed5611dc4739ea`.

## Dossier

`certificates/P14_dossier.json` and `manuscript/body/P14-dossier-table.tex`: the five classical chains (marked as
frozen P.3/P.4 inputs) and the P.5 entry chain (quantum object → prescription/D11 matching → counterterm domain →
amplitude rules → gate). Every link is resolved by `code/p5_entry/dossier_p14.py`; publication requires
`all_links_resolved = true`. The three quantum input slots (`hh` at κ², `K'c` at κ², `h` one-point at κ) are named
dependencies, not evaluated coefficients.

## Reproducibility contract (`REBUILD_INSTRUCTIONS.md`)

* Entrypoint: `python3 tools/rebuild_from_source.py [--inherited auto|workspace|vendored] [--report PATH]`, run from
  an unpacked `XVI-P-p14r-source-only.zip`.
* Reference values: `reproducibility/reference_values_p14r.json`.
* Inherited data pins: `reproducibility/inherited_data_pins.json`.
* Source set: `tools/source_manifest.py`.
* Flags in `RELEASE_STATUS.json`: `author_rebuild_passed` (bound to the current source tree hash through
  `reproducibility/author_rebuild_report_p14r.json`) and `independent_rebuild_passed` (`pending` until
  `reproducibility/independent_rebuild_report_p14r.json` is supplied).
* The p13 records `reproducibility/reference_values.json`, `reproducibility/author_rebuild_report.json` and
  `reproducibility/independent_rebuild_report.json` are left untouched in the author tree; they are not p14r source.

## Build (dependency order)

`python3 tools/build.py` runs the following stages:
1. fresh clean of every generated P13/P14 artifact (never the p13 reproducibility records or `archival/`);
2. conventions and inherited pins;
3. the frozen classical pipeline: C3, quartic, BRST, source action, gauge map, ch audit and graphs, master;
4. matter-loop gates (`tests/test_matter_loop_gates.py`, regenerating the inherited O5 records);
5. P.5 entry: `amplitude_rules.py` (with W6 `hessian_route.py`), `dred.py`, `counterterm_domain.py`, `quantum_object.py`, `prescription_d11.py`;
6. release gate `code/p5_entry/release_p14.py`;
7. dossier `code/p5_entry/dossier_p14.py`;
8. tests (baseline, certificate and gate mutations, resumed builds; junit);
9. [gate] PDFs and readback;
10. [gate] zips (review-focus, full, **source-only** `XVI-P-p14r-source-only.zip`);
11. [gate] external manifest (last);
12. sync of 6 files to `$P14_SYNC_DIR` (default `/workspace`): three PDFs, review-focus zip, full zip, p14r source-only zip.
    The p13 `/workspace/XVI-P-source-only.zip` and the p14 `/workspace/XVI-P-p14-source-only.zip` are never written.

| stage | builder | output |
|---|---|---|
| classical (frozen) | `code/classical/*.py`, `code/p4_classical/ch_source_audit.py` | `certificates/P13_*.json`, `ledgers/P13_ch_dependency_rows.json`, `ledgers/P13_graph_inventory.json`, `exports/ell{2,3,4}_*.srepr`, `exports/V4_grav.json`, `exports/ell4_conventions.json` |
| amplitude rules | `code/p5_entry/amplitude_rules.py` | `certificates/P14_amplitude_rules.json`, `exports/P14_vertex_tensors.json`, `exports/P14_integrands/*.json` |
| operational DRED | `code/p5_entry/dred.py` | `certificates/P14_dred_rules.json` |
| counterterm domain | `code/p5_entry/counterterm_domain.py` | `certificates/P14_counterterm_domain.json` |
| quantum object | `code/p5_entry/quantum_object.py` | `certificates/P14_quantum_object.json` |
| prescription + D11 | `code/p5_entry/prescription_d11.py` | `certificates/P14_prescription_D11_matching.json` |
| release gate | `code/p5_entry/release_p14.py` | `RELEASE_STATUS.json`, `ledgers/P14_milestones.json`; if accepted `certificates/P14_release.json`, `certificates/P14_closure_release.json`; else `certificates/P14_release_rejected.json` + exit 1 |
| dossier | `code/p5_entry/dossier_p14.py` | `certificates/P14_dossier.json`, `manuscript/body/P14-dossier-table.tex`, `manuscript/body/P14-entry-summary.tex` |
| tests | `tests/test_p14.py`, `tests/test_inverse_metric_series.py` | `certificates/P14_test_results.json`, `build/p14/junit.xml`, `build/p14/test_results/*.json` |

Mutation hooks for the end-to-end tests are read from `P13_MUTATIONS` (classical) and `P14_MUTATIONS` (P.5 entry);
both are empty in a normal build.

Archives (only the pinned p13 freeze inputs are read by the p14r pipeline):
* `archival/p14/`: the p14 release (superseded by p14r), with its source-only zip, reference values and author rebuild report;
* `archival/p13/`: p13 release, including its source-only zip, reference values and author/independent rebuild reports;
* `archival/p12/`, `archival/p11/`, `archival/p10/`;
* `archival/p02_p09/`: includes the legacy `ell4_verify.py` and `ell4_generator.py`, which state the wrong orientation,
  and the superseded milestone wording.
