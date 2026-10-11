# archival/p14r -- the p14r release (P.5-entry contract repair; superseded as a release by p15)

p14r was released on 2026-10-08 (source-only zip `XVI-P-p14r-source-only.zip`, sha256
19e8bf599daf102d8e23382544e6c6991ea307b2c3f31a0a97ad66d0b8a3dba3, 468541 bytes, 111 files; source tree
a64c0ae365980fa6b077f991df4316347527613075e87f17fecfe422db6e3894; author rebuild passed; 60 tests).

INDEPENDENT REBUILD OF p14r: PASSED (143/143 compared values equal, 60 tests, reviewer toy checks OK), report
`reproducibility/independent_rebuild_report_p14r.json` (archived copy, byte-identical to the reviewer's file, 
  +> sha256
09cda7db0d1f8e1cf7409212e4ee88ef60f21975e1367472f2c3ed45f1f7004b), bound to the p14r tree a64c0ae3... and zip
19e8bf59... SAME-BOX caveat: the reviewer ran on the same machine as the author build (fresh directory, fresh 
  +> venv,
from the source-only zip), NOT on a second machine. p15 records this as independent_rebuild_passed_p14r = true
  +> ;
it is NOT inherited by the p15 tree (p15 has its own, pending, independent flag).

Contents: the p14r source-only zip, RELEASE_STATUS / RELEASE_MANIFEST / README / REBUILD_INSTRUCTIONS of p14r,
  +>  the
p14r reference values, the p14r author and independent rebuild reports, the P14_* certificates and ledgers as
released in p14r (P14_dred_rules.json is the p14r version, before the p15 correction), build records and the
science PDF. The p14r contract (code/p5_entry/*) remains ACTIVE in p15 as the frozen contract on which p15
evaluates; this directory is provenance for the p14r release itself.

Why p14r is superseded as a release (p15 = first P.5 calculation):

1. p15 evaluates Batch A (D02, D12, D14a, D14b, D14c) and Batch B (D13) under the frozen p14r prescription.
2. ONE disclosed contract revision inside p15 (finding F1 of the p14r independent rebuild): the p14r
   PrematureD4Substitution guard in code/p5_entry/dred.py was a heuristic on the shape of the expression befor
  +> e the
   Laurent expansion. It gave a FALSE POSITIVE on eta^{rs} int l_r l_s/(l^2-m^2) = J (a correct d-free result)
  +>  and a
   FALSE NEGATIVE under the package's own premature_d4 mutation on the same integral (eta_trace_Gt reintroduce
  +> s d
   via tr gtilde = 4-d, giving d J/4 and a finite error -m^4/2). The R5 docstring claim that premature d = 4 "
  +> is
   detected" did not hold in general. p15 replaces it by a structural, provenance-based safeguard (opaque d;
   substitution only through dred.substitute_d; numeric traces of ghat/gtilde refused) and adds the reviewer's
   toys as regression tests. Rules R1-R6 are unchanged. Released p14r values are unaffected: in p14r
   Pipeline.laurent was applied only to the toy placeholders; no loop integral was evaluated.
3. Every other p14r contract file is byte-identical in p15 (checked by release_p15 against pinned sha256).
