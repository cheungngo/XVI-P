# P15 checkpoint (first P.5 calculation: Batch A = D02, D12, D14a-c; Batch B = D13)
Started 2026-10-08 ~12:00 UTC. Base: p14r release (tree a64c0ae3, zip 19e8bf59).
DO NOT TOUCH: /workspace/indep_rebuild_p14r, /workspace/XVI-P-p14r-source-only.zip, XVI-P-source-only.zip,
XVI-P-p14-source-only.zip, reproducibility/reference_values*.json (p13/p14r), reproducibility/independent_rebuild_report*.json.
t104u text not on box: spec taken from the p15 brief (sections 5A/5B as restated there).

## Design (step 0)
- contract code code/p5_entry/* stays BYTE-IDENTICAL (P14_* certs keep revision p14r = contract revision).
- new layer code/p5_calc/: p15_conventions, integrals (library), batchA, d13, release_p15 (runs AFTER release_p14,
  requires the contract gate accepted, writes P15_* certs and the top-level RELEASE_STATUS with revision p15).
- route 1 = frozen export (sha-pinned) -> frozen dred lift/reduce -> J via library (scaleless rule explicit);
  route 2 = regenerated integrand (own pw_vertex route) -> Feynman parameters, no scaleless rule.
- evanescent Gt: covariant fit with faithful realization Gt = (4-d) M (M sym, M.p = 0, tr M = 1).
## Step 1 DONE (integral library): code/p5_calc/{p15_conventions,integrals}.py; P15_integral_library.json library_certified=true (43 s): B0/A0 Laurent, exact-d numeric (B0 at d=2.6/3.3/3.7, T at d=0.7/1.5), frozen-dred tensor reduction + S0 == Feynman parameters (ranks 0-3, 4 realizations each), S0 Lambda-split, misuse guard.
- Step 2 DONE batchA.py: all 5 vanishing_under_declared_prescription (omega 2/4 only, no log members), IR-mass poles m^2/m^4, 124 s. Step 3 (d13.py) written; first run started bg -> /tmp/p15_d13.log
- 12:32 STEERING (parent): p14r independent rebuild PASSED (reproducibility/independent_rebuild_report_p14r.json; record
  independent_rebuild_passed_p14r=true bound to tree a64c0ae3/zip 19e8bf59, same-box caveat). Reviewer finding: the
  PrematureD4Substitution guard is heuristic (false positive on eta^{rs} int l_r l_s/(l^2-m^2) = J; false negative under
  premature_d4 on the same integral via eta_trace_Gt -> d J/4, finite error -m^4/2). Fix = disclosed p14r CONTRACT
  CORRECTION inside p15: structural/provenance safeguard (opaque d, substitution only inside laurent; numeric traces of
  ghat/gtilde forbidden), R5 docstring fixed, reviewer toys (eta-trace FP/FN, A0 +m^4/2, B0 -p^2/6) as regression tests.
  Released p14r values unaffected (laurent used only on toys).
- D13 first full run (69.8 s): routes agree exactly in d, fit exact, ghost equation OK; pole T2=3/16, T3=-1/4, E2=1/16
  (evanescent pole NONZERO); local T2=1/3, T3=-5/12, E2=1/6. FAILS: premature_d4 not rejected (my r5_guard was the same
  heuristic -> replace by structural guard); ghost self-energy pole c.cb-span fit false (investigate).
- 12:40 DONE contract correction in code/p5_entry/dred.py (OpaqueDimension d, substitute_d + D_PROVENANCE,
  NumericTraceForbidden, Rules(display_only), heuristic removed, R5 docstring corrected, reviewer_toys() in
  P14_dred_rules.json -> p15_contract_correction; all toys ok). tests/test_p14.py::test_dred_trace_ghat_eq_4_rejected
  revised (numeric trace now raises; display via display_only). p5_calc code switched to dred.substitute_d;
  d13 r5_guard removed; ghost self-energy fit fixed (upper rho index: structures x eta^{rho rho}; exact) and
  mapped onto p14r c.cb basis (sector_basis('cb','c',4), 2 dirs). Rerunning integrals, batchA, d13 in background.
- 12:55 D13 rerun OK (RC 0): all 11 controls true incl. ghost self-energy pole in p14r c.cb span (coords -3/8, 1/4;
  SE evanescent pole -1/8) and R5_structural_safeguard_active; premature_d4 now rejected structurally. D13 status
  'regulated' (4D sector 'renormalized'; E2 evanescent pole 1/16 recorded, no evanescent counterterm in p14r).
  batchA + integrals rerun OK with substitute_d. archival/p14r/ created (README, copies of p14r zip, reference,
  author+independent reports, P14_* certs incl. ORIGINAL p14r P14_dred_rules.json, ledgers, status, manifest, PDF).
  p15_conventions: P14R_CONTRACT_SHA256 pins, DISCLOSED_CONTRACT_CORRECTIONS (dred.py), test revision disclosure.
  code/p5_calc/release_p15.py written; release_p14 -> release_p15 both accept (changed contract files = [dred.py];
  independent_p14r true; D12_status vanishing_under_declared_prescription (derived)).
  NEXT: build.py/source_manifest/rebuild_from_source p15 layering, tests/test_p15.py + test_p14 revisions,
  manuscript note + README/REBUILD_INSTRUCTIONS, then full author build (background).
- 13:10 Release layering done: release_p15.py; build.py (stages p15calc + release15, gate re-invokes release_p14,
  dossier_p14, release_p15; listings/zips/manifest/GENERATED/clean for P15; P15_test_results.json); source_manifest
  (ZIP p15, reference_values_p15.json, archival/p14r records as source); rebuild_from_source (P15 certs/ledger, p15
  values, p14r archived report pinned); tests/test_p15.py (15 pass); test_p14 revised (contract record from
  certificates/P14_release.json; source-set/zip names p15); README p15 section; REBUILD_INSTRUCTIONS p15; manuscript
  note P15_first_calculation.tex (+ generated body/P15-results-table.tex).
- 13:11 Step 7 presync build started (bg): P14_SYNC_DIR=/tmp/p15_presync python3 tools/build.py > /tmp/p15_presync_build.log
  (expected: test_source_only_contract fails until preliminary reference_values_p15.json is written; then resume
  --from-stage release). Then: author rebuild script /tmp/p15_author_rebuild.sh -> install report -> final build.
- 13:27 status regenerated (release_p14, release_p15), preliminary reference written; build2 --from-stage release started (bg).
- 13:55 build2 presync PASS (BUILD_RC 0): tests 75/75 (baseline 54, cert-mutation 17, resumed 4); gates accepted
  before pdf/zip/manifest; PDFs 22/307/330; readback 6 records pass; source-only zip 122 files (synced to
  /tmp/p15_presync only). SOURCE FROZEN. Author rebuild started: /tmp/p15_author_rebuild.sh > /tmp/p15_author.log
- 14:10 author rebuild running (zip 190a85a9..., tree ae8cbd0f..., 122 files)
- 14:13 author rebuild #1 FAILED: file_access_trace, comparison_with_reference (tree ae8cbd0f, zip 190a85a9). Diagnosing.
- 14:20 DIAGNOSIS (author rebuild #1): (a) file_access_trace: 2 unpinned in-tree reads = archival/p14r/
  reference_values_p14r.json and archival/p14r/reproducibility/author_rebuild_report_p14r.json (read when the zips are
  written) -> PACKAGING (archived records without pin). (b) comparison 196/198: only P15_release and RELEASE_STATUS
  differ, and the ONLY differing field is inputs_content_sha256_ignoring_timings/P14_release.json, a hash of the
  contract record that included run-specific keys (independent_rebuild_passed False vs pending, reproducibility,
  freeze live-report sub-records) -> PACKAGING (run-specific fields in hashed content). All computed values equal:
  P15_integral_library, P15_batchA, P15_D13, P14_* content hashes identical between author tree and clean rebuild.
  FIX: P14R_ARCHIVED_RECORDS pins (p15_conventions; rebuild_from_source ARCHIVAL_PINS; release_p15 checks them);
  release_p15 hashes inputs with QC.RUN_SPECIFIC_KEYS excluded. Flag NOT carried over: redo presync+reference+rebuild.
- 14:22 presync build3 (--from-stage release15) started, log /tmp/p15_presync_build3.log
- 14:40 presync build3 PASS (75/75; PDFs 22/307/330; gates accepted). SOURCE FROZEN. Author rebuild #2 started (/tmp/p15_author.log).
- 15:10 author rebuild #2 running (zip 54325c1f..., tree 79f53752...)
- 15:31 author rebuild #2 PASS (10/10 steps incl file_access_trace, comparison_with_reference; 1279s; tree 79f53752, zip 54325c1f). Installed reproducibility/author_rebuild_report_p15.json. Starting final build.
- 15:33 pre-final protected sha check: all 8 unchanged (p13 2f85a566, p14 7a43e8b0, p14r 19e8bf59, ref d8bf3d97, indep 7ce496cc, indep_p14r 09cda7db, ref_p14r 9e817492, author_p14r 2f7def0c)
- 15:03 interrupted; final build PID 1108460 still running, waiting (not restarted)
- 15:07 final build progressing (past matter_loop_gates)
- 15:16 final build: p15 calc stages running/done
- 15:22 FINAL BUILD PASS (PID 1108460, not restarted): 21 stages rc=0, tests 75/75 (baseline 54, cert-mutation 17, resumed 4), gates accepted before pdf/zip/manifest, manifest 31 entries 0 failures, PDF readback pass.
  Synced to /workspace 15:16: XVI-P-p15-source-only.zip 54325c1f (122 files, 535086 B) == author report zip; tree 79f53752 == author report tree;
  XVI-P-science.pdf a77e7114 (22pp), XVI-P-appendix.pdf 0ed99bf3 (307pp), XVI-P.pdf ffd0ace1 (330pp), full.zip 983ffe63 (898 files), review-focus.zip ff57cca3 (114 files).
  reference_values_p15.json 0866adfe; author_rebuild_report_p15.json 1e729eba.
  RELEASE_STATUS: publication accepted, batchA_evaluated True, D13_evaluated True, author_rebuild_passed True, independent_rebuild_passed pending, independent_rebuild_passed_p14r True, hard_stops_hold True.
- 15:22 post-final protected shas: all 8 unchanged. p15 RELEASED. DONE.
