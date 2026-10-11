# archival/p21 -- the p21 release (small release: D11 absolute pin, gate/scan/disclosure fixes; superseded by 
  +> p22)

p21 was released on 2026-10-09. Source-only zip `XVI-P-p21-source-only.zip`: sha256
a71d6b5203bc3914833db9fd13b9d186bef93d1ae3007b2e4c99fdfce11e0678, 183 files. Source tree
b835353ffe16a8ff159e2916fe3efdf2b9d89a4d512e80e9e6da587cecd0fe5e. Reference values reference_values_p21.json
96ae946b.... Author rebuild passed (report a5f886ad...).

INDEPENDENT REBUILD OF p21: PASSED, with findings (no mismatches). Report
`reproducibility/independent_rebuild_report_p21.json` (archived copy byte-identical, sha256
8a582b332cd242689c54b1f962dc88270b9592040c0ba432576a505f0e36a60d), bound to tree b835353f... / zip a71d6b52...
  +> .
SAME-BOX caveat: it ran on the same machine as the author build (fresh directory, fresh venv, from the source-
  +> only
zip), NOT on a second machine. p22 records independent_rebuild_passed_p21 = true; the p22 tree does NOT inheri
  +> t it.

Reviewer findings, addressed in p22 (which also carries the user-approved bigger fronts and a DISCLOSED contra
  +> ct revision):
- p21 gate disclosure prefix exemptions (low): tools/ and manuscript/ edits and added code files escaped the
  undisclosed-change check -> p22 gate: every changed/added/removed file must be listed (no prefix exemption f
  +> or
  tools/, notes or code; only generated reference values and the listed archival/p21 records are exempt).
- Scan misses (low; 8 forms) and the d-guard power-base hole (low) -> p22 contract revision: a runtime d guard
  +>  in
  code/p5_entry/dred.py (one delimited additive block; the p18 core is byte-identical) that intercepts subs/xr
  +> eplace/
  replace/evalf/Poly/coeff/collect/limit/Lambda/series/d==d from outside sympy; a live probe (30 forms x 4 exp
  +> ressions,
  incl. all reviewer forms and the power-base hole) must raise. The static allow-list scan stays as secondary.
- Stale 'Absolute pin: OPEN' text in the P20 section (info/low) -> inline [superseded in p21] marker.
- p20 gate standalone scope, absolute-pin step-1 hard-coding, reviewer rule note (info): no action needed.
