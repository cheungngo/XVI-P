# archival/p16 -- the p16 release (E2 evanescent decoupling proof; Batch C D01, D03; superseded as a release b
  +> y p17)

p16 was released on 2026-10-08: source-only zip `XVI-P-p16-source-only.zip`, sha256
56d5887daa7a96dcc7cf2f70c6735e802125c9b19a33ac17a3ef975e330fef57, 608444 bytes, 134 files; source tree
90b4a6659cddd341436a59d285a56eb14bdd575bb56e69faf4ba75be4d7b549e (d02d30a8... without reference); reference va
  +> lues
reference_values_p16.json a1fda1e67a4a0033014f40b8bdac57b4daacfa507588e0765bb7139587b053d9; author rebuild pas
  +> sed
(272/272; report b4f9bcf3...).

INDEPENDENT REBUILD OF p16: PASSED (272/272 entrypoint values equal; 107 tests in a separate copy; own E2
decoupling derivation; own Batch C spot-check; determinism across PYTHONHASHSEED), report
`reproducibility/independent_rebuild_report_p16.json` (archived copy byte-identical, sha256
1a8861964afe7ae4d4b38aaae5381230d8cda82610c51ef2b7919ebd6e326843), bound to tree 90b4a665... / zip 56d5887d...
  +> .
SAME-BOX caveat: same machine as the author build (fresh directory, fresh venv, from the source-only zip), NOT
  +>  a
second machine.  p17 records independent_rebuild_passed_p16 = true; it is NOT inherited by the p17 tree.

Reviewer findings carried into p17: G1 (static scan narrower than the disclosure: named-function replace, stri
  +> ng
round-trips, eval(srepr), manual tree rebuilds; no package use) -> scan extended, wording corrected; G2 (sympi
  +> fy of a
stored string gives a plain Symbol('d')) -> guarded loader dred.parse_d + assert_opaque_d (disclosed contract
revision); G3 (docstring 'expr.match(d)' wording; Wild-pattern match not refused) -> wording corrected; G4 (ch
  +> ange
log omitted the added reference file) -> fixed; G5 (disclosed test_p15 relaxation) -> unchanged; G6 (overall i
phase of D01/D03 vs real D13) -> convention documented; G7 (hh-basis coordinates not recomputed) -> p17 recomp
  +> utes
the coordinates explicitly (certificates/P17_hh_slot.json).

Contents: the p16 source-only zip, RELEASE_STATUS / RELEASE_MANIFEST / README / REBUILD_INSTRUCTIONS of p16, t
  +> he
p16 reference values, the p16 author and independent rebuild reports, the P16_* certificates, the P16 mileston
  +> es
ledger, the p16 per-file source list (base of the p17 change log) and the science PDF.
