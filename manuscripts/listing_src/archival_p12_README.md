# ARCHIVAL -- XVI-P revision p12 (superseded by p13; not p13 acceptance evidence)

Snapshot of the p12 active release (2026-10-08). It contains:
* code, tools and tests (`test_p12.py`);
* certificates `P12_*` and ledgers `P12_*`;
* the science note `manuscript/notes/P12_classical_closure.tex`, the generated manuscript bodies and the pream
  +> ble;
* `RELEASE_STATUS_p12.json`, `RELEASE_MANIFEST_p12.txt` and `README_p12.md`;
* `build/` (test results, PDF readback, PDF inputs, build log).

p12 was the evidence-reconciliation release (critique t103u). Its mathematics is unchanged in p13.

Why it was superseded (plan t104u):
* **Milestones were not defined.** p12 spoke of "classical readiness" without milestone labels. Older notes us
  +> ed
  "P-next.N", and a p08 table row in which "P4" meant coupled one-loop restoration. p13 fixes the definitions:
  P.3 = projection + dependencies + graph inventory; P.4 = classical readiness, NOT coupled one-loop restorati
  +> on;
  P.5 entry / calculation / identity.
* **No completion dossier.** p12 described its evidence as a release history. p13 adds one table in which ever
  +> y
  claim is linked to its file, function, certificate key and test, and the links are resolved mechanically
  (`certificates/P13_dossier.json`).
* **No reproducibility contract.** p12 had no source-only rebuild entrypoint, no reference values, no
  `author_rebuild_passed` / `independent_rebuild_passed` flags, and no source-only zip. Its builders read
  `/workspace/XVI-M.tex` and `/workspace/XVI-N-r10/code/prep/grav_density.py` by absolute path, and one certif
  +> icate
  recorded that absolute path. p13 resolves these through sha256 pins, with vendored copies.

The p12 certificates are internally consistent: every residual record is `[0,0,0,0]`/`true`, and the quartic
and master records agree. They are not p13 evidence because p13 regenerates everything from source.
