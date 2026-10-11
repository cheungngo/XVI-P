# P18 checkpoint (append-only)
- 01:22 p17 final build had completed (BUILD_RC 0; /workspace synced 21:39; p17 zip 7f4f61df). p18 START. p17 independent report present (92542a22). Archived p17 -> archival/p17 (zip, README/REBUILD/MANIFEST/STATUS, science PDF, reference values, author+independent reports, P17 certs, ledger, p17_source_files.json). No running builds.
- 01:23 M2 analysis: plan = compare L-coefficient tensor of P^DR_D11 (4D components) with FT of (i k^2/4) RR K u^R (FT[u^R] log coeff = i pi^2 = -r, calibrated by DR scalar bubble and XVI-O residue). Probe D11 evaluation (batchC.evaluate_graph, read-only use) running bg: /tmp/p18/d11_probe.log
- 01:24 D11 probe: fit exact/unique, FP=PV routes agree exactly in d, exchange symmetric (3 s). M2 PROTOTYPE: L-coefficient of P^DR_D11 (4D comps) == -(i/4) RR(D2/60 + D0/18)(p) on ALL 100 pairs, exact incl. overall constant (/tmp/p18/m2_proto.py).
- 01:25 slot probe: p_m G_D11 = 0 exactly in d (all orbits incl. gt); slot value of D11 and of D01+D03+D11 = 0 on all 6 assignments (/tmp/p18/slot_probe.py).
- 01:26 wrote code/p5_calc/p18_conventions.py (draft; flags EARNABLE only via certificates).
- 01:28 wrote code/p5_calc/d11.py (M2 routes A+B, D11 record, full slot); K u = T (XVI-O all_256, derived alpha/beta) PASS in probe /tmp/p18/ku_check.log. Running: python3 code/p5_calc/d11.py > /tmp/p18/d11_run.log
- 01:33 d11.py run #1 EXIT 0: M2 DISCHARGED (4D comps; routes A+B, 6 mutations rejected); D11 evaluated (12 controls); full slot DECOUPLED (7 assignments; D11 transverse by itself); 4D poles: D11 = i(1/240 k1 - 1/120 k2), sum = i(41/80 k1 - 43/120 k2). inventory flag reader fixed (dict 'execution'); rerunning -> /tmp/p18/d11_run2.log
- 01:34 dred.py H3/H5 doc-only revision (AST-equal to p17 ignoring docstrings; p17 copy /tmp/p18/dred_p17.py). parse_d(srepr) raises verified.
- 01:35 wrote code/p5_calc/release_p18.py (gate: contract AST-pin for dred, p17 layer, M2/D11/slot certs, inventory recheck, earned flags only from certs).
- 01:35 wrote tests/test_p18.py (H1 scan + 15 plants, M2 covariant recheck, D11, slot, inventory, status, gate mutations).
- 01:36 disclosed test revisions applied: test_p14 (names p17->p18, P18 prefixes), test_p17 (rs()->P17_release.json, label, indep flag). originals in /tmp/p18/test_p1{4,7}_orig.py
- 01:37 patched tools/build.py (/tmp/p18/patch_build.py; p17 original /tmp/p18/build_p17.py), source_manifest (p18 zip/ref, archival/p17 globs), rebuild_from_source (p18), preamble H4 (upquote mechanism via textcomp).
- 01:37 docs: archival/p17/README.md, manuscript/notes/P18_D11.tex + body include (backslash fixed).
- 01:37 README p18 section + REBUILD_INSTRUCTIONS p18 (originals /tmp/p18/*_p17.md).
- 01:38 in-place gates: release_p17 rc0, release_p18 ACCEPTED (M2/D11/slot/inventory true, q earned). Running pytest p17+p18 -> /tmp/p18/pytest_p17_p18.log
- 01:38 placeholder reference_values_p18.json written; protected zips verified. PRESYNC BUILD #1 started (bg, PID 1337098): P14_SYNC_DIR=/tmp/p18_presync, log /tmp/p18_presync_build.log (do not restart; check BUILD_RC).
- 02:03 presync #1 progressing (see log); not restarted.
- 02:12 PRESYNC #1 BUILD_RC 1: test_p16::test_f4_value_block_readback_detects_a_changed_value failed on P18_hh_slot.json. DIAGNOSIS: test harness picks the first non-bool snippet (the long 'verdict', >110 chars) and mutates it by plain str.replace on the WRAPPED page -> no-op (snippet not verbatim in wrapped text). Readback itself is correct: a mutation inside the wrapped verdict is detected (pass False) -- verified. => stale test expectation: disclosed test revision of test_p16 (victim chosen among snippets verbatim in the page) + new test_p18 check of wrapped-value mutation. Also honesty pass (user 02:12): M2 scope qualifier, ledger-based inventory, M3 status/N4/degree-4 controls.
- 02:15 honesty pass done: M2 cert/RS carry D11_matching_verified_scope='4D components' + evanescent_components_matching=not_applicable_not_verified (gate requires); M3_status 'unconditional on the 4D components'; D11 controls exactly_degree_four + N4 (14 controls); inventory derived from P13_ch_dependency_rows surviving rows (3 rows, 9 graphs, statuses, no Missing) in d11.py and release_p18. test_p16 disclosed revision; test_p18 +wrapped readback test +scope mutation. d11 rerun OK; gates accepted; pytest p16+p17+p18 106 passed. README/note updated. Next: PRESYNC #2 full build from scratch.
- 02:16 PRESYNC #2 started (full, from scratch; PID 1349288): P14_SYNC_DIR=/tmp/p18_presync, log /tmp/p18_presync2_build.log. DO NOT restart; check BUILD_RC.

## 2026-10-09T02:56:41Z presync #2 result + fix
- PRESYNC #2 (PID 1349288) ended BUILD_RC 1: 2 failed, 179 passed (/tmp/p18_presync2_build.log): test_p18::test_inventory_and_quantum_inputs_flag and ::test_p18_release_status_and_flags; quantum_inputs_evaluated = not_earned.
- Diagnosis: a REAL ordering bug in new p18 code (code/p5_calc/d11.py main): inventory() was taken BEFORE certificates/P18_D11.json was written, so on a from-scratch build D11 had present=false and q_ok=false. In-place runs passed only because a stale P18_D11.json from an earlier run existed (a carried-over artefact, which is exactly what the fail-closed build is meant to catch). The gate's independent inventory_recheck withheld the flag because it requires the cert's "earned" (fail-closed, correct).
- Fix: d11.py now writes P18_D11.json first and then takes the inventory (pre-fix copy at /tmp/p18/d11_pre_orderfix.py). This is new p18 code, not contract code. Test: test_p18 now also asserts present is True for all 9 inputs.
- Verified fresh: moved the P18_D11/P18_hh_slot/P18_D11_M2 certs aside (/tmp/p18/aside) and reran d11.py: q=true, all 9 present; gate accepted with q earned; pytest p16+p17+p18: 106 passed.
- PRESYNC #3 started (full, from scratch; PID 1361759; log /tmp/p18_presync3_build.log). DO NOT restart; check BUILD_RC.

## 2026-10-09T03:28:48Z presync #3 PASS; source frozen; author rebuild
- PRESYNC #3 (PID 1361759) BUILD_RC 0: tests 181 passed (baseline 135, cert-mutation 42, resumed 4); release_gate_p18 accepted, quantum_inputs_evaluated earned. SOURCE FROZEN.
- AUTHOR REBUILD started: bash /tmp/p18_author_rebuild.sh (PID 1371190; log /tmp/p18_author.log; report /tmp/p18_author_report.json). DO NOT restart; wait for AUTHOR_REBUILD_DONE.

## 2026-10-09T04:11:18Z author rebuild #1 FAIL (criterion), fix, author rebuild #2
- AUTHOR REBUILD #1 (PID 1371190) pass=false. Every value matched: comparison_with_reference 290/290 equal, the full build rc 0, tests 181 passed, readback ok, manifest ok, source zip rebuilt identical. The ONLY failing step was release_accepted, because tools/rebuild_from_source.py still required the stale p17 criterion D11_evaluated is False (p18 earns True). This is a stale criterion, not an ordering or value problem. Kept as /tmp/p18_author_report_run1_FAIL.json and /tmp/p18_author_run1.log.
- Fix (disclosed in README p18 section): the criterion now requires D11_evaluated True, D11_matching_verified True with scope "4D components", quantum_inputs_evaluated earned and hh_full_row_decoupling_proven True. Pre-fix copy: /tmp/p18/rebuild_from_source_pre_fix.py. The README also discloses the d11.py ordering fix.
- After the fix: release_p18 gate rc 0; pytest p14+p16+p17+p18: 163 passed. Because the source changed, the reference was rewritten by the script and the author rebuild reruns from scratch in a clean copy (its full build includes all tests).
- AUTHOR REBUILD #2 started: PID 1384291; log /tmp/p18_author.log; report /tmp/p18_author_report.json. DO NOT restart.

## 2026-10-09T04:37:33Z author rebuild #2 PASS; final build
- AUTHOR REBUILD #2 (PID 1384291) pass=true. All 10 steps ok; 290/290 equal to the reference; 181 tests passed. Tree bfab3b4b318fc37f2fcca209d097d27a24955e3b3d8469f5a8ab2e904ace7094; zip 7c7d5451adb459092edc2606e1b3322909325000d47bab89c14b7f7a6d25c92f. Installed as reproducibility/author_rebuild_report_p18.json.
- FINAL BUILD started (syncs /workspace by default): PID 1391772; log /tmp/p18_final_build.log. DO NOT restart; check BUILD_RC.

## 2026-10-09T05:09:28Z FINAL BUILD PASS -- p18 RELEASED (on box)
- FINAL BUILD (PID 1391772) BUILD_RC 0; tests 181 passed (135/42/4); gate accepted; manifest 43 entries, failures [], no PDF hash inside the PDFs. RELEASE_MANIFEST_EXTERNAL.txt (sha 2ebbe605...) was written after all six deliverables. The /workspace synced copies are byte-identical to the in-tree copies and all appear in the manifest.
- Deliverables: XVI-P.pdf 16b252fd... (584 pp); XVI-P-science.pdf db0c526b... (29 pp); XVI-P-appendix.pdf 7a283009... (556 pp); XVI-P-full.zip a18bb4f1...; XVI-P-review-focus.zip 5b937bef...; XVI-P-p18-source-only.zip 7c7d5451... (= author rebuild #2 zip).
- Protected zips unchanged: 2f85a566, 7a43e8b0, 19e8bf59, 54325c1f, 56d5887d, 7f4f61df. p17 independent report 92542a22... unchanged and pinned.
- Flags: author_rebuild_passed True; independent_rebuild_passed (p18) pending; independent_rebuild_passed_p17 True.
