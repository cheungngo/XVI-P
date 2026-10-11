# archival/p18 -- the p18 release (M2 discharged, D11 evaluated, full hh slot; superseded as a release by p19)

p18 was released on 2026-10-09. Source-only zip `XVI-P-p18-source-only.zip`: sha256
7c7d5451adb459092edc2606e1b3322909325000d47bab89c14b7f7a6d25c92f, 753894 bytes, 154 files. Source tree
bfab3b4b318fc37f2fcca209d097d27a24955e3b3d8469f5a8ab2e904ace7094 (52976da5... without reference). Reference va
  +> lues
reference_values_p18.json 8a867f9e.... Author rebuild passed (290/290; report 13da1ba2...).

INDEPENDENT REBUILD OF p18: PASSED. Report `reproducibility/independent_rebuild_report_p18.json` (archived cop
  +> y
byte-identical, sha256 893f167ef7124d981c0569ca386035aed06e0dbb0c90a2362a6ceeafd1930cb2), bound to tree bfab3b
  +> 4b... /
zip 7c7d5451.... SAME-BOX caveat: it ran on the same machine as the author build (fresh directory, fresh venv,
  +>  from
the source-only zip), NOT on a second machine. p19 records independent_rebuild_passed_p18 = true; the p19 tree
  +>  does
NOT inherit it.

Reviewer findings carried into p19:
- I1: release_p18.py published without gating on quantum_inputs_evaluated. Now release_p19.py and the build's
  publication gate fail closed: publication requires the p18 layer's quantum_inputs_evaluated == 'earned', the
  inventory recheck and projected_defect_computed. Gate mutations are in tests/test_p19.py.
- I2: static-scan pattern gaps. The tests/test_p19.py scan now flags: a Poly or as_poly result held in a varia
  +> ble
  and then called; collect(evaluate=False); Add/Mul/Pow(*x.args) rebuilds; eval/exec aliases; vars()/globals()
  +> /
  locals() subscripts; operator.attrgetter/methodcaller; Symbol/symbols/var with a run-time name that could be
  +>  'd'.
  Every Poly .terms()/.coeffs()/.monoms() site is on a reviewed list. This is still a pattern check, not a pro
  +> of.
- I3: milestone wording. P.5_calculation status now reads "evaluated; 4D sector renormalized (MS-bar, declared
  domain); evanescent regulated (poles retained, not subtracted), decoupled from the ch slots".
- I4-I7: informational; unchanged.

Bug fixes disclosed in p18 (d11.py inventory ordering; the stale rebuild criterion) are verified by the review
  +> er.

Contents:
- the p18 source-only zip;
- RELEASE_STATUS, RELEASE_MANIFEST, README and REBUILD_INSTRUCTIONS of p18;
- the p18 reference values;
- the p18 author and independent rebuild reports;
- the P18_* certificates and the P18 milestones ledger;
- the p18 per-file source list (p18_source_files.json, the base of the p19 change log);
- the p18 science PDF.
