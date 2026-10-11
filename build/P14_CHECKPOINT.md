# p14 release checkpoint (resume notes; outside the tree so it never enters zips)
Protected (never touch): /workspace/XVI-P-source-only.zip (2f85a566), XVI-P/reproducibility/reference_values.json (d8bf3d97),
  XVI-P/reproducibility/independent_rebuild_report.json (7ce496cc), /workspace/indep_rebuild_p13/
Sequence:
 [x] code/p5_entry, tests/test_p14.py, notes, body, tools (build/source_manifest/rebuild_from_source), README, REBUILD, archival/p13/README
 [x] build1 (presync /tmp/p14_presync): pipeline OK, 5 test bugs -> fixed in tests/test_p14.py
 [x] preliminary reference_values_p14.json written (to be rewritten after a passing build)
 [x] build2: tests 51/51 pass; manifest failed (archival p13 pins in PDFs) -> PINNED_P13 lines fix; release_p14 adds independent_rebuild_passed_p13 + rebuild_flag_scope
 [x] build3: PASS (51 tests, gates, manifest; synced to /tmp/p14_presync only)
 [x] reference rewritten (08:5x); FROZEN SOURCE: tree 8c4eeaaa55d377df..., zip 1675379fef003b93... -- DO NOT EDIT SOURCE until final release
 [~] author clean-copy rebuild (RUNNING): /tmp/p14_author_rebuild.sh > /tmp/p14_author.log (writes reference, zip, unzip, rebuild -> /tmp/p14_author_report.json)
 [ ] install report -> reproducibility/author_rebuild_report_p14.json
 [ ] final build with sync to /workspace (log /tmp/p14_build_final.log); verify protected shas
 [x] author rebuild #1 (tree 8c4eeaaa): FAIL -- (a) trace: 2 archived p13 records unpinned; (b) amplitude_rules W4 'kappa2_seconds' timing leaked into content hash
     -> fixed: amplitude_rules res["seconds"]; PC.P13_ARCHIVED_RECORDS pinned + verified in rebuild step 3
 [x] build4: tests+gates pass; manifest collision a60230a3 (inherited_data_pins_p13 pin == live pins file) -> removed from source set + pins
 [x] build5: PASS
 [ ] then: /tmp/p14_author_rebuild.sh > /tmp/p14_author2.log ; install report ; final full build with sync
 [x] author rebuild #2 PASS (tree c8c6e044, zip 7a43e8b0; 142/142; trace clean) -> installed reproducibility/author_rebuild_report_p14.json
 [i] 09:3x resumed after interruption; author rebuild #2 PID 988994 still running (not restarted)
 [x] FINAL full gated build PASS (10:04): 51 tests, gates pdf/zip/manifest accepted, readback pass, manifest 24 entries verified, synced 6 files to /workspace
 [x] RELEASED p14: tree c8c6e044bc0a2a6cbf94276b6b125cd94c95d8496486be5221fc5b99d03158aa,
     /workspace/XVI-P-p14-source-only.zip sha 7a43e8b0a374000d9ec565b64dd95d8deec5f3612512ed322307859e5e7a19ba (== author report)
     protected files verified unchanged (p13 zip 2f85a566, reference_values.json d8bf3d97, independent report 7ce496cc)
 DONE. Nothing pending except the p14 independent rebuild (pending; reviewer's choice).
