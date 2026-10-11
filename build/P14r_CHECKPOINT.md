# p14r repair checkpoint (t105u). P.3/P.4 code byte-identical; no loop evaluation.
Start: p14 tree c8c6e044..., p14 zip 7a43e8b0... (/workspace/XVI-P-p14-source-only.zip: never overwrite)
Protected: /workspace/XVI-P-source-only.zip 2f85a566, reproducibility/reference_values.json d8bf3d97,
  reproducibility/independent_rebuild_report.json 7ce496cc, /workspace/indep_rebuild_p13, /workspace/XVI-P-p14-source-only.zip 7a43e8b0
Steps:
 [x] 0 archive p14 -> archival/p14 (zip, status, manifest, reference, author report, certs, code, tests, tools, notes)
 [ ] 1 DRED index algebra module + tests (premature d=4, tr ghat=4 mutation)
 [ ] 2 D11 M3 labels + conditional + lower-degree contacts
 [ ] 3 counterterm wording
 [ ] 4 W5 wording, D01/D02/D03/D12 independent regeneration, Ward rename
 [ ] 5 isolated-copy baseline/gate tests
 [ ] 6 P.5 entry flag gating on DRED; revision p14r; docs/notes
 [ ] 7 build -> reference p14r -> author rebuild -> final build + sync
Design notes:
 - revision label 'p14r' (PC.REVISION); cert file names keep prefix P14_; new certs P14_dred_rules.json; zip XVI-P-p14r-source-only.zip;
   reference reproducibility/reference_values_p14r.json; author report reproducibility/author_rebuild_report_p14r.json
 - dred.py: Q4S = QdS (+) Q(4-d)S; ghat/gtilde/g4 contraction engine; l,p in QdS; exported l_r lifted as l.e_(r), e_(r) in Q4S;
   ghat_rs -> eta_rs - Gt_rs (evanescent); Gram/PV reduction with symbolic d; contractions before Laurent; PrematureD4 guard
 - hessian_route.py (W6): Gamma1 = (i/2) STr log S'' ; D01/D02/D03/D12 vs exported integrands; own ell_k monomial differentiation
 - W4 key onshell_3graviton_transversality_instance -> ward_contraction_two_free_onshell_graviton_legs_offshell_gauge_leg

## Step 1 DONE (dred.py + 5 tests)
- code/p5_entry/dred.py runs in ~35 s -> certificates/P14_dred_rules.json, dred_rules_verified=true.
- T1: finite a/8+b/4 (premature d=4 gives b/4, raises PrematureD4Substitution). T2: pre-Laurent J-4J/d = -(4-d)/d J,
  finite -a/2 (d-4)x pole. Mutations premature_d4 / trace_ghat_eq_4 (T1 b/4, T2 0, rules check fails) /
  contract_after_laurent (UncontractedObjects) all rejected. Known PV reductions pass.
- Lifts of all 9 exported graphs present; evanescent Gt parts in every graph (D02: 70/94 comps).
- tests/test_p14.py: test_dred_* (5) pass.

## Step 2 DONE (M3 + prescription)
- prescription_d11.py: PRESCRIPTION rewritten to operational DRED (lifting, order_of_operations, evanescent retained,
  'none arise' withdrawn); prescription checks add operational_DRED_rules_verified + evanescent_remainders_retained.
- M3: labels sd(u^R)=4, kernel sd bound 8, divergence 4, contact derivative order 4, sd(d^a delta)=4+|a|; exact wording;
  CONDITIONAL on M2; bounded contact space order0 (2, tr 0), order2 (4, tr 1), order4 (5, tr 2); N4 normalization
  condition excludes order0/2 explicitly (not by 'no other scale'). Cert regenerated; tests pass.

## Step 3 DONE (counterterm wording)
- counterterm_domain.py: key essential_by_sector_upper_bound -> candidate_directions_by_sector; reading "Eight candidate
  directions modulo the computed exact equivalences, before imposing the relevant identity constraints."; added
  cohomology_caveat + D_cap_ker_sigma0_computed=false; normalization condition 2 now cites N4. Cert regenerated (168 s).

## Step 4 IN PROGRESS (W5 wording, W4 rename, W6)
- hessian_route.py written: D01/D02/D03/D12 Tr-log route == exported integrands, all components, 0 mismatches (23 s).
- amplitude_rules.py: docstring W4/W5/W6; key ward_contraction_two_free_onshell_graviton_legs_offshell_gauge_leg;
  verify adds W6_hessian_route; main binds W6 to exports (w6_exports). Rerun started in bg -> /tmp/am.out
- amplitude_rules rerun OK (162 s): W1-W6 pass, W6_exports all_agree, all 5 mutations rejected (W6 also catches
  tadpole factor/D02, ghost sign/D03, offdiag/D01, omit transport/D03). dossier_p14.py rows P5E.2b (DRED), P5E.5b (W6).
## Step 4 DONE.

## Step 5 DONE (code; validated only after presync build)
- tests: COPY_SUBS from frozen list (+tests); GATE_MUTS + baseline_unmutated + dred_mutation_not_rejected;
  test_isolated_copy_contains_frozen_inputs, test_isolated_copy_baseline_accepted; P.5-only => freeze TRUE + named flag
  false; classical => freeze false.

## Step 6 IN PROGRESS
- REVISION p14r; AUTHOR_REPORT/INDEPENDENT_REPORT_CURRENT in p14_conventions; release gate recomputes DRED + W6.
- source_manifest ZIP p14r + reference_values_p14r.json; build.py (SRC_ZIP, dred stage, LISTINGS, MANIFEST_FILES,
  focus, titles, archival p14 section); rebuild_from_source CERTS + P14_dred_rules; README, REBUILD_INSTRUCTIONS.
- archival/p14/README.md written; live reproducibility/{reference_values_p14,author_rebuild_report_p14}.json removed
  (identical archived copies in archival/p14).
- TODO: manuscript note P14_P5_entry_contract.tex.
- note P14_P5_entry_contract.tex rewritten (scope p14r, sec:p14r-dred R1-R6 + tests, M3 conditional/N4, CT wording,
  W4/W5/W6, isolated-copy tests, repro p14r). P5_ENTRY_QUALIFICATION added (conventions, RELEASE_STATUS, closure).
- F1/F2 OK (54 files unchanged); protected shas OK (2f85a566, 7a43e8b0, d8bf3d97, 7ce496cc).
## Step 6 DONE.

## Step 7: presync build started (bg): P14_SYNC_DIR=/tmp/p14r_presync python3 tools/build.py > /tmp/p14r_presync_build.log
- build1 presync: pipeline OK, release accepted, dossier 42/42; tests 59/60 (source_only_contract needs reference) -> preliminary reference_values_p14r.json written; resume --from-stage release (log /tmp/p14r_presync_build2.log)
- build2 presync (--from-stage release): PASS, 60/60 tests (baseline 39, cert-mutation 17, resumed 4), gates OK,
  synced to /tmp/p14r_presync only. Isolated-copy results as specified (baseline accepted freeze T; P5-only freeze T +
  named flag F; classical freeze F). PDFs 20/246/267 pages. Protected shas OK.
- SOURCE FROZEN from here. Author rebuild started: /tmp/p14r_author_rebuild.sh > /tmp/p14r_author.log
  (rewrites reference, zips, clean copy /tmp/p14r_author_rebuild, report /tmp/p14r_author_report.json)
- NEXT: install report -> reproducibility/author_rebuild_report_p14r.json; final build (sync /workspace) log
  /tmp/p14r_build_final.log; verify protected shas.
- 11:35 resumed after interruption; author rebuild still running (tests stage), waiting
- AUTHOR REBUILD DONE: pass=true, all 10 steps true, 1027 s; tree a64c0ae3..., zip 19e8bf59... (111 files).
- Step 8: report installed -> reproducibility/author_rebuild_report_p14r.json (not source; tree sha unchanged).
- Step 9: final build started (bg, sync /workspace): python3 tools/build.py > /tmp/p14r_build_final.log (11:38)
- 11:53 final build: pipeline+release gate+dossier OK, now in tests stage
- Step 9 DONE (12:00): final build BUILD_RC=0, synced to /workspace. Pipeline rc=0 all stages; dossier 42/42;
  tests 60/60 (baseline 39, cert-mutation 17, resumed 4); gates accepted before pdf/zip/manifest; PDFs 20/247/267;
  readback 6 records pass; manifest 25 entries, 0 failures, manifest written last.
  XVI-P-p14r-source-only.zip 19e8bf59... == author report zip sha; tree a64c0ae3... == author report tree sha.
  RELEASE_STATUS: p14r, publication accepted, P5_entry_earned T (5/5 flags), author_rebuild_passed T,
  independent_rebuild_passed pending (p14r), independent_rebuild_passed_p13 T (p13-bound, same-box caveat), freeze T.
- Step 10 DONE: protected shas verified unchanged: p13 zip 2f85a566, p14 zip 7a43e8b0, p13 reference_values d8bf3d97,
  p13 independent report 7ce496cc.
## p14r COMPLETE (pending only: independent rebuild of p14r tree).
