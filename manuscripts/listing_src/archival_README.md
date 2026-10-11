# ARCHIVAL -- XVI-P revisions p02-p09 (not active, not acceptance evidence for p10)

Moved here by the p10 release (2026-10-08). Nothing in this directory is read by the p10 pipeline
(`tools/build_p10.py`) or by the active tests (`tests/test_p10.py`, `tests/test_matter_loop_gates.py`,
`tests/test_inverse_metric_series.py`).

* `certificates/`, `ledgers/`, `notes/`, `code/`, `tests/` -- p02-p09 material (P1-P4, P9 series).
  The p09 `required_classical_BV_components_verified=false` / residual `complete_af_ghost_O_kappa2_on_D_h`
  is superseded by `certificates/P10_master_kappa2.json`.
* `tests/test_quantum_normalization.py` -- inherited XVI-O o70-sync package test; it pins
  `RELEASE_STATUS.revision == "o70-sync"` and already failed on the p09 tree (first check). The
  wrong-prescription and source-comparison controls it was cited for are exercised, and pass, in the
  active `tests/test_matter_loop_gates.py` (route-A/B prefactor mutations; Ww prescription-id mutations).
* `certs_pre_p09/`, `listings_p02_p07/`, `listing_src_snapshot_p09/`, `RELEASE_MANIFEST_p09.txt` -- earlier ar
  +> chives.
* `release_p09/` -- the p09 PDFs and zips formerly at the package root (superseded). The two p09 zips are kept
  +>  on
  disk here but are NOT nested into the p10 zips.
* `build_pre_p10/` -- pre-p10 build scratch (old listing copies, LaTeX logs, outputs, PDFs).
