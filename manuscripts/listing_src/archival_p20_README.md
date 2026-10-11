# archival/p20 -- the p20 release (CORRECTION of p19: K1 orientation erratum, restoration redefined, D11 ratio
  +>  pin; superseded by p21)

p20 was released on 2026-10-09. Source-only zip `XVI-P-p20-source-only.zip`: sha256
ca32ce018933f12d1a623217d6a98d647817360dd12211e2e9469cf850a63bb2, 174 files. Source tree
2c0aa1533b5a64d65f9169cc510ea3f0761c9471f9601cdec6973a2aa8d45700. Reference values reference_values_p20.json
4877f5de.... Author rebuild passed (422/422; report 686e2c9c...).

INDEPENDENT REBUILD OF p20: PASSED, with findings (no mismatches). Report
`reproducibility/independent_rebuild_report_p20.json` (archived copy byte-identical, sha256
e8f358f9c4f13c76693968211b49e04d546a0bb3a4c0ab4b1a0e485f62595389), bound to tree 2c0aa153... / zip ca32ce01...
  +> .
SAME-BOX caveat: it ran on the same machine as the author build (fresh directory, fresh venv, from the source-
  +> only
zip), NOT on a second machine. p21 records independent_rebuild_passed_p20 = true; the p21 tree does NOT inheri
  +> t it.

Reviewer findings, addressed in p21 (a small release, no scope expansion):
- D11 absolute pin left OPEN but derivable (low): p21 derives the sign AND magnitude of the D11 pole from 1/2 
  +> Tr ln
  under the package's declared conventions (G = Gamma^(2) from Gate 0 + G6; Wick direction from N_eps = i/(16 
  +> pi^2)
  and the +1/eps bubble pole; g = eta + kappa h; eta = (+,-,-,-)): Gamma^(2)|_pole = kappa^2/(16 pi^2 eps)
  [p^4 P2/240 + p^4 P0s/24], equal to the heat-kernel a_2 = C^2/120 + R^2/72 exactly. No external convention c
  +> hoice;
  external inputs are mathematics only (a_2 coefficients, heat-kernel pole formula). x2 and sign flip detected
  +> .
- Scan misses (low): eight forms passed the pattern scans; p21 adds an allow-list scan and a runtime opaque-d 
  +> check.
- Gate: top-level absolute_pin_status unchecked (low) -> checked against the nested status in p21.
- p20 gate trusted the P19 layer record (info) -> p21 re-checks the p18 layer (q earned) and the inventory liv
  +> e.
- P19 note edit not in DISCLOSED_* (info) -> listed in p21_conventions.DISCLOSED_MANUSCRIPT_REVISIONS.
- /p19/change_log_vs_p18 recomputed on the current tree (info/low) -> renamed in p21.
- p19 quotient finding withdrawn by the reviewer; restoration scope wording confirmed (info).
