# P19 CHECKPOINT (append-only)

## 2026-10-09T06:23:02Z start
- p19 approved from p18. p18 independent PASSED: reproducibility/independent_rebuild_report_p18.json sha 893f167ef7124d981c0569ca386035aed06e0dbb0c90a2362a6ceeafd1930cb2, tree bfab3b4b..., zip 7c7d5451..., same-box. Reviewer findings: I1 (release_p18 publication not gated on q), I2 (scan gaps), I3 (scope: P.5_calculation wording), I4-I7 informational.
- Step 1: archive p18 under archival/p18 (in progress).

## 2026-10-09T06:26:56Z archive done; science plan
- archival/p18 created: zip 7c7d5451 (copy), RELEASE_STATUS/MANIFEST/README/REBUILD_INSTRUCTIONS (p18), reference_values_p18 8a867f9e, author 13da1ba2, independent 893f167e, P18_* certs, P18_milestones, science PDF, p18_source_files.json 9b5ebcb0 (154 files; the tree sha recomputed equals bfab3b4b).
- Prototype /tmp/p19/proto_sigma.py (Route G, sigma0 on D): rank sigma0 on D = 6, so dim D cap ker sigma0 = 5; rank of P_ch sigma0 = 4. By sector: hh sigma0 rank 3 (ch 3); c.cb 2 (ch 0); c.K 3 (ch 1, only c.K#0 = T1); phi.phi 0.
- Structural facts (frozen certs): row K.c (D13) reaches ch only via T1 and E1, and A_T1 = A_E1 = 0 exactly in d (P15_D13, P16_E2). Row hh decouples (P18). Row one-point: D14a-c vanish.
- Next: code/p5_calc/defect.py with Route C (covariant, exact in d) + Route G (GE antibracket on D), counterterm solve, D cap ker sigma0, controls/mutations.

## 2026-10-09T06:53:24Z defect.py drafted (code/p5_calc/defect.py); runs in place
- Run 2 (/tmp/p19/defect_run2.log): outcome ZERO. Route C (both rows, all 7 assignments) is zero exactly in d, and the evanescent parts are zero. dim D cap ker sigma0 = 5; D cap Im = 3; cohomology 2. Quotient coordinates: the hh parts are zero (the hh pole is transverse, i.e. in Im sigma0); c.K pole (3/8, -1/4), L (-3/8, 1/4), local (2/3, -5/12).
- Bug found: _eqs treated the unknowns as polynomial generators, so the Route C image rank came out 0 (Route G gives 4); the outcome of naive_4D_D13 was misclassified because of it. Fixed by excluding the unknowns. Run 3 in progress (PID 1441784, log /tmp/p19/defect_run3.log).

## 2026-10-09T07:06:37Z defect run 4 results + Q(i) finding
- Run 4 (/tmp/p19/defect_run4.log): outcome ZERO; computed, identity and restoration all earned; all controls true; 8/8 mutations change the outcome (7 give a nonlocal OBSTRUCTION; naive_4D_D13 gives NONZERO but CANCELLABLE: a local residual -c.p p^2 (a.b p^2 - a.p b.p)/12, cancelled by finite h.h/c.K terms).
- FINDING J1: Route G over Q (re/im split, p14r convention) reproduces the p14r counts (Im 3, quotient 8, Xi rank 22), but those are field artefacts: odd-derivative densities carry an explicit i. Over Q(i) (physical; equal to Route C's rank): dim D cap Im = 6, dim D cap ker sigma0 = 6, cohomology 0, quotient 5; P_ch sigma0 rank 3 (Route C 3). The contract is not modified; the finding is reported.
- Closure probe added (the ghost self-energy relative factor). Run 5 in progress: PID 1446121, log /tmp/p19/defect_run5.log.

## 2026-10-09T07:10:42Z defect run 5 (PID 1446121, /tmp/p19/defect_run5.log): DONE 210.7 s; outcome ZERO; 25/25 controls; 8/8 mutations change outcome; closure probe: full closure only for ghost-self-energy relative factor -1 (1, I, -I fail) -- informational, not claimed. Test revisions test_p14/test_p18 applied (disclosed DISCLOSED_TEST_REVISIONS_P19); originals in /tmp/p19/orig.

## 2026-10-09T07:13:01Z RESUME after interruption (user 07:12: honesty pass a-d before freezing). State: tests/test_p19.py written (fast subset 36/39, 3 fixed); source_manifest.py + rebuild_from_source.py patched to p19; build.py NOT yet patched; no build running.

## 2026-10-09T07:14:06Z honesty pass (d): /tmp/p19/probe_ghost.py (<1 s): 2iD V[c.K#1]=-V[c.cb#0], 2iD V[c.K#2]=-V[c.cb#1], 2iD V[c.K#0]=2V[c.cb#1]; P15 ghost eq Sigma=+2iD[G] maps c.K pole to c.cb (-3/8,1/4) = P15 Sigma fit (consistent). sigma0-closed pairs need +1 => factor -1 NOT derived (selected by scan); full c.b closure NOT established, sign conflict ghost-eq vs S0 reported as finding K1. ch identity independent (c.cb has zero ch image).

## 2026-10-09T07:14:33Z defect run 6 STARTED PID 1453902 log /tmp/p19/defect_run6.log (honesty pass: why_zero, rests_on, flag_definitions, restoration = renormalised Delta_R=0 AND solve x=0, findings J1/K1, K1 derived factor +1, control ghost_equation_relation_reproduces_P15_sigma_pole). DO NOT restart. Pre-change copy /tmp/p19/defect_pre_honesty.py

## 2026-10-09T07:16:09Z release_p19 honesty edits (claim_status why-zero/rests-on/K1/J1, content re-check of the 3 flag definitions); science note manuscript/notes/P19_defect.tex + body include; build.py patched (/tmp/p19/patch_build.py); source_manifest + rebuild_from_source p19; README/REBUILD_INSTRUCTIONS p19; archival/p18/README.md written; I2 scan + poly-variable rule; placeholder reference_values_p19.json. Waiting defect run 6 (PID 1453902).

## 2026-10-09T07:18:23Z defect run 6 DONE (212.9 s): ZERO; 26/26 controls; flags earned (restoration content-backed); K1 derived +1, closure fails, -1 needed. release_p19 rc=0 (/tmp/p19/release_run2.log).

## 2026-10-09T07:18:26Z in-place pytest #1 started PID 1456797 log /tmp/p19/pytest_inplace1.log

## 2026-10-09T07:28:38Z release_p18 + release_p19 rerun in place (layer refresh); pytest #2 (no -x) PID 1459616 log /tmp/p19/pytest_inplace2.log

## 2026-10-09T07:32:49Z protected shas verified (2f85a566 7a43e8b0 19e8bf59 54325c1f 56d5887d 7f4f61df 7c7d5451; p18 indep report 893f167e). PRESYNC #1 STARTED PID 1461423: P14_SYNC_DIR=/tmp/p19_presync, log /tmp/p19_presync_build.log. DO NOT restart; wait for BUILD_RC.

## 2026-10-09T08:03:12Z PRESYNC #1 (PID 1461423) ENDED BUILD_RC=1: tests 247 passed (186/57/4); release_gate_p19 rc=0; pdflatex failed for XVI-P-science. Diagnosing.

## 2026-10-09T08:03:38Z FIX: release_p19.tex() did not escape # (quotient labels h.h#0) -> pdflatex fatal; now escapes # % $ ~ { }; standalone compile of note+table OK (5 pp). Honesty (user 08:03): projected_restoration_scope + claim_status: restoration scoped to projected ch identity (Delta_R=0, x=0), distinct (P_ch sigma0(S_ct)=0 independent check; S_ct has nonzero c.b image), K1 stated next to it (derived +1: full c.b closure FAILS). Kept earned. Note/README updated; tests added. PRESYNC #2 STARTED PID 1471529 log /tmp/p19_presync2_build.log. DO NOT restart.

## 2026-10-09T08:36:51Z PRESYNC #2 (PID 1471529) ENDED BUILD_RC=1: tests 248 passed; science OK; pdflatex failed for XVI-P-appendix. Diagnosing.

## 2026-10-09T08:37:01Z FIX: listing title "kappa^2" (raw ^) -> "kappa-squared"; all titles scanned for raw TeX specials (none). PDF-stage CHECK (resumed --from-stage pdf, sync /tmp/p19_pdftest; diagnostic only, not a release) PID 1481073 log /tmp/p19_pdftest.log

## 2026-10-09T08:37:41Z PDF-stage check PID 1481073 BUILD_RC=0 (readback pass incl P19_defect; zips built). PRESYNC #3 (from scratch) starting.
## 2026-10-09T08:37:41Z PRESYNC #3 STARTED PID 1481513 log /tmp/p19_presync3_build.log. DO NOT restart.

## 2026-10-09T09:06:26Z PRESYNC #3 (PID 1481513) BUILD_RC=0. SOURCE FROZEN. Starting author rebuild (/tmp/p19_author_rebuild.sh).
## 2026-10-09T09:06:29Z AUTHOR REBUILD STARTED PID 1490292 log /tmp/p19_author.log report /tmp/p19_author_report.json. DO NOT restart.
## 2026-10-09T09:19:50Z author: reference_values_p19.json written (tree w/o ref 4d4824ba); author src zip da924275 (164 files), tree fcf90354; clean-copy rebuild in progress.

## 2026-10-09T09:43:45Z AUTHOR REBUILD (PID 1490292) PASS: 320/320 equal, tree fcf90354, zip da924275; report installed reproducibility/author_rebuild_report_p19.json. FINAL BUILD STARTED (syncs /workspace) PID 1501335 log /tmp/p19_final_build.log. DO NOT restart.

## 2026-10-09T10:20:23Z FINAL BUILD (PID 1501335) BUILD_RC=0 (248 tests). /workspace synced 10:10:51. XVI-P.pdf 0c125f56 645pp; science 143a7eba 32pp; appendix c673d346 614pp; full 297c8c90; review-focus 0e2baa33; p19 source-only da924275. Protected shas unchanged; p18 indep 893f167e.
## 2026-10-09T10:20:26Z manifest LAST (10:10:48 after zips 10:10:44), contains all six deliverable hashes. p19 DONE.
