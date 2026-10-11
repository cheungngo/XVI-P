# ARCHIVAL -- XVI-P revision p13 (superseded as a release by p14; its classical P.3/P.4 code is the FROZEN P.5
  +>  input)

Snapshot of the p13 release (2026-10-08). p14 keeps the classical P.3/P.4 code byte-identical to this snapshot
  +>  and
re-checks the freeze on every release (`code/p5_entry/freeze_p13.py`: F1 independent report, F2 frozen files,
F3 classical values).

Pins (also in `code/p5_entry/p14_conventions.py`):
* p13 source tree sha256 `2b1baf335468944aa800c05eaa8b0b4df67ee893491079fcc944eb8fb0e69a70`
* p13 source-only zip sha256 `2f85a566c49689dea329df9fe3ea213eb6495759d4e95546495e245e7fdf3266`
  (`XVI-P-source-only_p13.zip`, a byte copy of `/workspace/XVI-P-source-only.zip`; zips are never source, so t
  +> his
  copy is not in the p14 source-only zip)
* p13 reference values sha256 `d8bf3d97457913dbd1fa03a2e801630005aeca601b93ebb53307fb30e1bc4095`
  (`reference_values_p13.json`, a byte copy of the p13 `reproducibility/reference_values.json`)
* independent rebuild report sha256 `7ce496cc446f2ef1948de6aaf034b09e9dcab0b9878cd6ae6015cda63a6515e4`
  (`reproducibility/independent_rebuild_report_p13.json`, a byte copy of the reviewer's
  `reproducibility/independent_rebuild_report.json`)
* frozen file list `frozen_p13_inputs.json` (54 classical files with their p13 sha256)

Independent rebuild of p13: PASSED (112/112 reference values matched, 77 values recomputed independently, no
mismatches, hand spot check of the conformal boundary identity). CAVEAT: it ran on the SAME box (shared kernel
  +> ,
TeX Live, poppler) in a fresh venv from the source-only zip; it was NOT run on a second machine. The resulting
  +>  flag
`independent_rebuild_passed = true` is bound to the p13 tree above and is not inherited by p14 changes.

Contents:
* `README_p13.md`, `REBUILD_INSTRUCTIONS_p13.md`, `RELEASE_MANIFEST_p13.txt`, `RELEASE_STATUS_p13.json`;
* `XVI-P-source-only_p13.zip`, `reference_values_p13.json`, `frozen_p13_inputs.json`;
* `reproducibility/`: author and independent rebuild reports and the inherited data pins of p13;
* `build/`, `certificates/`, `ledgers/`, `code/`, `tools/`, `tests/`, `manuscript/`: the p13 build outputs, re
  +> lease
  code, tools, tests and notes as released (superseded by the p14 versions; not read by the p14 pipeline).

Only `reference_values_p13.json`, `frozen_p13_inputs.json` and the independent report are read by the p14 pipe
  +> line,
each verified against its pinned sha256 before use.
