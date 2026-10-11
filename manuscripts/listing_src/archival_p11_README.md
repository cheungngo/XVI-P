# ARCHIVAL -- XVI-P revision p11 (superseded by p12; not p12 acceptance evidence)

Snapshot of the p11 active release (2026-10-08): code, tools, tests (`test_p11.py`), certificates `P11_*`, led
  +> gers
`P11_*`, the science note `P11_classical_closure.tex`, the generated manuscript bodies, `RELEASE_STATUS_p11.js
  +> on`,
`RELEASE_MANIFEST_p11.txt` and `build/` (test results).

Why it was superseded (critique t103u) -- root cause of the "contradictory certificates":
* The certificate FILES were internally consistent and agreed with each other. Every gravitational Noether rec
  +> ord had
  `Q_terms = [0, 0, 0, 0]` and `Q_identically_zero = true` at kappa0, kappa1 and kappa2, in both
  `P11_quartic_verified.json` and `P11_master_kappa2.json`. Both records come from `grav_noether.noether`, whe
  +> re the
  count and the flag derive from the same normalised dicts.
* The p11 APPENDIX printed these arrays over several lines (`json.dumps(indent=2)`). In two places a page brea
  +> k fell
  inside an array:
  - quartic kappa0, after the 2nd element, footer "12";
  - master kappa1, right after "[", footer "29".
  A plain text extraction of the PDF then reads `0, 0, 12 0, 0` -> [0,0,120,0] and `29 0, 0, 0, 0` -> [290,0,0
  +> ,0].
  The listings were byte-identical to the files executed and written in that build (`check_listings_current`).
  The defect was a presentation one, not stale snapshots, a different code path, or zero-valued dict keys:
  `jetpoly` drops zero coefficients in every operation.
* Missing safeguards that p12 adds:
  - no count/flag invariant before serialization or in the release gate;
  - no cross-certificate check;
  - `--from-stage pdf|zip|manifest` bypassed `release.py`;
  - no readback of the typeset values;
  - bare page numbers.
