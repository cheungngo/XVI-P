# P20 CHECKPOINT (append-only)

## 2026-10-09T11:12:02Z p20 START (user 11:11): correction release from p19. p19 final build had completed (BUILD_RC 0). No running builds.
## 2026-10-09T11:12:33Z ARCHIVED p19 -> archival/p19 (zip da924275, README/REBUILD/MANIFEST/STATUS, science pdf, reference 08f10fa8, author 5f0715f3, independent 1b01f1d8, P19 certs, ledger, p19_source_files.json 01b34cc8 (164 files)).
- 2026-10-09T11:14:40Z defect.py p20 run1 launched PID=1536444 log=/tmp/p20/defect_run1.log (do not restart)
- 2026-10-09T11:15:59Z d11_pin.py run: ratio pin PASS (c2=-I/240, c0=-I/24), absolute OPEN; certificates/P20_D11_pin.json
- 2026-10-09T11:19:45Z defect run1 (PID 1536444) finished 266s: K1 orientation -1,-1; Sigma(c,cb)=(3/8,-1/4); full S_ct closed; detector drop D13/flip Kc detected, drop D11 blind; restoration earned (p20 def)
- 2026-10-09T11:21:19Z written: d11_pin.py, p20_conventions.py, release_p20.py, release_p19 rev, P20 note, P19 note/README corrections, archival/p19/README.md
- 2026-10-09T11:23:47Z defect.py run2 (final code) PID=1543794 log=/tmp/p20/defect_run2.log (do not restart)
- 2026-10-09T11:24:14Z d11_pin run3 (parse_d) rc=0; scan tests 39 passed
- 2026-10-09T11:28:22Z defect run2 PID 1543794 done 254.6s
- 2026-10-09T11:28:30Z in-place releases p15..p20 rc=0 (p20 accepted); pytest p18/p19/p20 PID=1545844 log=/tmp/p20/pytest_inplace1.log
- 2026-10-09T11:34:38Z in-place pytest p18/p19/p20: 158 passed
- 2026-10-09T11:34:40Z PRESYNC #1 launched PID=1548015 (P14_SYNC_DIR=/tmp/p20_presync) log=/tmp/p20/presync1.log -- DO NOT restart; wait for BUILD_RC
- 2026-10-09T12:02:11Z resumed after interruption: PRESYNC #1 PID 1548015 still running (tests stage); not restarted
- 2026-10-09T12:12:15Z PRESYNC #1 ended BUILD_RC=1 (tests failed); diagnosing
- 2026-10-09T12:12:32Z fix: P20_D11_pin top-level scalar summary + VALUE_BLOCKS keys (test_p16 f4 readback needed a verbatim snippet). PRESYNC #2 PID=1559694 log=/tmp/p20/presync2.log -- DO NOT restart
- 2026-10-09T12:51:51Z PRESYNC #2 BUILD_RC=0 (tests 293 passed; pages 33/662/696). Source frozen.
- 2026-10-09T12:51:54Z AUTHOR REBUILD PID=1570601 log=/tmp/p20_author.log report=/tmp/p20_author_report.json -- DO NOT restart
- 2026-10-09T12:52:24Z resumed: AUTHOR REBUILD PID 1570601 running (zip ca32ce01, tree 2c0aa153); not restarted
- 2026-10-09T13:31:31Z AUTHOR REBUILD done SCRIPT_RC=0 pass=true 422/422; report installed reproducibility/author_rebuild_report_p20.json
- 2026-10-09T13:31:33Z FINAL BUILD (sync /workspace) PID=1582004 log=/tmp/p20/final.log -- DO NOT restart
- 2026-10-09T13:42:37Z resumed: FINAL BUILD PID 1582004 running; not restarted
- 2026-10-09T14:14:31Z FINAL BUILD PID 1582004 BUILD_RC=0 (293 tests; 33/662/696 pages); source zip ca32ce01 = author zip; manifest verify 49/49; 16 protected zip copies intact; p19 indep report 1b01f1d8 intact. p20 DONE.
