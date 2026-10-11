# XVI-P p23: rebuild instructions (reproducibility contract)

p23 (stage release from p22; disclosed contract revision: polynomial-domain refusal block appended to dred.py): the
O.1 requirement record, the one-loop power counting and the P.6 entry inventory are in certificates/P23_O1_scope.json
(code/p5_calc/power_counting.py), and the gate is code/p5_calc/release_p23.py (live poly-refusal probe, EV value check).
The p23 change log is computed against archival/p22/p22_source_files.json. The source zip is
XVI-P-p23-source-only.zip, the reference is reproducibility/reference_values_p23.json, and the reports are
reproducibility/{author,independent}_rebuild_report_p23.json. The top-level RELEASE_STATUS.json is the p23 status
(certificates/P22_release.json is the p22 layer record). independent_rebuild_passed_p22 = true (archived report
023e5b83..., same box); the p23 independent rebuild is pending. The text below applies with p22 -> p23 where it names
the current release.


p22 (from p21; disclosed contract revision): EV-M2 proven, evanescent counterterms (EV-CT) earned with full closure and
the projected identity unchanged, P.5 calculation status renormalized (one loop, kappa^2, two-point functions,
QdS externals), and a runtime d guard in dred.py (delimited additive block, live probe of 30 forms x 4 expressions in
release_p22.py). The p22 change log is computed against archival/p21/p21_source_files.json (pinned in
code/p5_calc/p22_conventions.py) and every change must be disclosed (no tools/ or notes prefix exemption). The source
zip is XVI-P-p22-source-only.zip, the reference is reproducibility/reference_values_p22.json, the reports are
reproducibility/{author,independent}_rebuild_report_p22.json, and the top-level RELEASE_STATUS.json is the p22 status
(certificates/P21_release.json is the p21 layer record). independent_rebuild_passed_p21 = true (archived report
8a582b33..., same box); the p22 independent rebuild is pending. The p21 text below applies with p21 -> p22 where it
names the current release.


p21 (small release from p20): the absolute D11 pin is derived (sign and magnitude, from 1/2 Tr ln under the declared
conventions, equal to the heat-kernel a_2); the p20 gate checks the top-level pin status and re-checks the lower layers;
an allow-list scan and a runtime opaque-d check complement the pattern scans; the p20 edit of the P19 note is disclosed.
The p20 independent rebuild PASSED (report e8f358f9..., same box) and is recorded as independent_rebuild_passed_p20;
the p21 independent rebuild is pending.

This contract lets anyone check, from **source only**, that the XVI-P evidence (the frozen classical P.3/P.4
pipeline, the p14r P.5 entry contract, the p15 first P.5 calculation -- Batch A D02, D12, D14a-c and Batch B D13 --
the p16 second step -- the E2 decoupling proof and Batch C D01, D03 -- and the p17 third step -- the proof that the
D01/D03 evanescent poles decouple from the ch-projected slot as the sum D01 + D03 -- and the p18 fourth step -- the
discharge of the D11 matching premise M2, D11 evaluated, and the full hh slot D01 + D02 + D03 + D11 + D12 -- and the
p19 identity step -- the projected one-loop kappa^2 ch-identity defect assembled from every evaluated input, and the
counterterm solve -- and the p20 correction -- K1 orientation erratum, full sigma_0 closure of the one-loop kappa^2
MS-bar counterterm, the D11 ratio pin)
regenerates and matches the author's reference values. A passing rebuild is package evidence (XVI-O `conv:package`), **not** a
mathematical certificate. XVI-P stays unregistered.

## Flags

| flag | meaning | set by |
|---|---|---|
| `author_rebuild_passed` | `reproducibility/author_rebuild_report_p21.json` passed **and** was produced from exactly the current source tree (`source_tree_sha256` equal) | `code/p5_calc/release_p21.py` |
| `independent_rebuild_passed` | `pending` until `reproducibility/independent_rebuild_report_p21.json` exists; then the same rule | a separate clean environment (not the author) |
| `independent_rebuild_passed_p20` | the archived p20 independent report (`archival/p20/reproducibility/independent_rebuild_report_p20.json`, sha256 `e8f358f9…` pinned) passed and is bound to the p20 tree `2c0aa153…` / zip `ca32ce01…` (same box) | `code/p5_calc/release_p21.py` |
| `independent_rebuild_passed_p19` | the archived p19 independent report (`archival/p19/reproducibility/independent_rebuild_report_p19.json`, sha256 `1b01f1d8…` pinned) passed and is bound to the p19 tree `fcf90354…` / zip `da924275…` | `code/p5_calc/release_p20.py` |
| `independent_rebuild_passed_p18` | the archived p18 independent report (`archival/p18/reproducibility/independent_rebuild_report_p18.json`, sha256 `893f167e…` pinned) passed and is bound to the p18 tree `bfab3b4b…` / zip `7c7d5451…` | `code/p5_calc/release_p19.py` |
| `independent_rebuild_passed_p17` | the archived p17 independent report (`archival/p17/reproducibility/independent_rebuild_report_p17.json`, sha256 `92542a22…` pinned) passed and is bound to the p17 tree `2a5a6317…` / zip `7f4f61df…` | `code/p5_calc/release_p18.py` |
| `independent_rebuild_passed_p16` | the archived p16 independent report (`archival/p16/reproducibility/independent_rebuild_report_p16.json`, sha256 `1a886196…` pinned) passed and is bound to the p16 tree `90b4a665…` / zip `56d5887d…` | `code/p5_calc/release_p17.py` |
| `independent_rebuild_passed_p15` | the archived p15 independent report (`archival/p15/reproducibility/independent_rebuild_report_p15.json`, sha256 `6bc760c2…` pinned) passed and is bound to the p15 tree `79f53752…` / zip `54325c1f…` | `code/p5_calc/release_p16.py` |
| `independent_rebuild_passed_p14r` | the archived p14r independent report (`archival/p14r/reproducibility/independent_rebuild_report_p14r.json`, sha256 pinned) passed and is bound to the p14r tree `a64c0ae3…` / zip `19e8bf59…` | `code/p5_calc/release_p15.py` |

None of these flags enters `release_claim_accepted`. (The integrity of the pinned archived records does: a tampered
archive rejects publication.)

**p19 independent rebuild (bound to the p19 tree).** PASSED with findings (SAME-BOX caveat: same machine, fresh
directory and venv, from the source-only zip; not a second machine). It is not inherited by p20. Its findings (K1:
the p19 full-closure statement was an orientation bookkeeping error, now retracted; quotient orientation; restoration
flag not independent; blind spots; J1 wording; scan gaps; stale RELEASE_STATUS on a standalone reject) are addressed
in the p20 correction release, with no contract revision.

**p18 independent rebuild (bound to the p18 tree).** PASSED (SAME-BOX caveat: same machine, fresh directory and
venv, from the source-only zip; not a second machine). It is not inherited by p19. Its findings I1 (publication not
gated on quantum_inputs_evaluated), I2 (remaining static-scan pattern gaps) and I3 (milestone wording) are addressed
in p19 with no contract revision.

**p17 independent rebuild (bound to the p17 tree).** PASSED (SAME-BOX caveat: same machine, fresh directory and
venv, from the source-only zip; not a second machine). It is not inherited by p18. Its findings H1 (static-scan
pattern gaps), H2 (c hat / h tilde assignment), H3 (stale comments), H4 (curly quotes in listings) and H5 (parse_d of
srepr raises, undocumented) are addressed in p18; the dred.py change of p18 is documentation only (its AST without
docstrings is pinned equal to p17).

**p16 independent rebuild (bound to the p16 tree).** PASSED (272/272 values equal, 0 mismatches; SAME-BOX caveat:
same machine, fresh directory and venv, from the source-only zip; not a second machine). It is not inherited by p17.
Its findings G1 (static-scan scope), G2 (plain `Symbol('d')` from re-parsed strings), G3 (guard wording), G4 (change
log omitted the new reference file) and G6 (phase convention) are addressed in p17. The fix for G2 (the guarded
loader `dred.parse_d`) is the one disclosed contract revision of p17 (`dred.py`).

The top-level `RELEASE_STATUS.json` is the p21 status. The layer records are `certificates/P20_release.json`, `certificates/P19_release.json`,
`certificates/P18_release.json`,
`certificates/P17_release.json`,
`certificates/P16_release.json` and `certificates/P15_release.json`.

**p15 independent rebuild (bound to the p15 tree).** PASSED (0 mismatches; SAME-BOX caveat: same machine, fresh
directory and venv, from the source-only zip; not a second machine). It is not inherited by p16. Its findings F3
(opaque-d bypass via `replace`/`lambdify`), F4 (stale footer label; readback scope) and F5 (non-contract change log)
are addressed in p16; F3 is the one disclosed contract revision of p16 (`dred.py`).

**p14r independent rebuild (bound to the p14r tree).** PASSED: 143/143 compared values equal, 60 tests, reviewer toy
checks OK. SAME-BOX caveat: it ran on the same machine as the author build (fresh directory and venv, from the
source-only zip), not on a second machine. It is not inherited by p15: the p15 tree has its own pending flag. Its
finding F1 (the heuristic PrematureD4 guard of `dred.py`) is repaired in p15 as a disclosed contract revision.

The p14r contract record is `certificates/P14_release.json`.

**p13 freeze (separate, bound to the p13 tree).** `P3_P4_frozen_as_P5_inputs` is true because the independent
rebuild of **p13** passed (source tree `2b1baf33…`, zip `2f85a566…`; archived report
`archival/p13/reproducibility/independent_rebuild_report_p13.json`, pinned by sha256), the 54 frozen classical files
are byte-identical and the classical values equal the archived p13 reference values. Caveat: that rebuild ran on the
same box (shared kernel, TeX Live, poppler) in a fresh venv from the source-only zip; it was not on a second machine.
The p13 flag is not inherited by later changes: each tree has its own independent flag.

## Environment used by the author

| component | version |
|---|---|
| Python | 3.13.5 |
| sympy | 1.14.0 |
| mpmath | 1.3.0 |
| pytest | 9.1.1 |
| pdfTeX | 3.141592653-2.6-1.40.26 (TeX Live 2025/dev/Debian) |
| poppler (`pdftotext`, `pdfinfo`) | 25.03.0 |

LaTeX packages used: lmodern, amsmath/amssymb/amsthm, booktabs, hyperref, bookmark, geometry, longtable,
listings, xcolor, graphicx, verbatim, fancyhdr. No other Python packages are needed. Other versions may work. The
report records the versions found and compares them with the reference. A different sympy version may change the
`srepr` text of the exports, and therefore the export **file** hashes, without changing the polynomials. The
polynomial hashes are compared separately.

## Steps

```
unzip XVI-P-p23-source-only.zip         # creates XVI-P/ (source only: no certificates, exports, PDFs, caches)
cd XVI-P
python3 tools/rebuild_from_source.py --inherited vendored --report build/rebuild_report.json
```

The command exits 0 if and only if every step passed and every compared value is equal. It takes about 30–45 minutes
on one machine. The full pipeline uses about 2.5 minutes for the quartic, about 1 minute for the master, about
1.5 minutes for the matter-loop gates, about 7 minutes for the P.5 entry stages (amplitude rules incl. the W6
Hessian route ≈ 3, operational DRED ≈ 0.5, counterterm domain ≈ 3), about 4 minutes for the p15 calculation
(integral library ≈ 0.75, Batch A ≈ 2, D13 ≈ 1.2), about 4 minutes for the p16 calculation (E2 ≈ 0.1, Batch C ≈ 3.5),
about 1 minute for the p17 calculation (hh slot), about 2 minutes for the p18 calculation (M2, D11, full slot), about 5 minutes for the p19 calculation (projected defect, full closure), a few seconds for the p20 D11 pin (p21: with the absolute pin derivation) and several minutes for the tests.

`--inherited` selects where the pinned external inputs come from:
* `vendored`: only the copies shipped in `provenance/` (recommended for a clean environment);
* `workspace`: the sibling landmark trees, e.g. `/workspace/XVI-M.tex`;
* `auto`: workspace if present, otherwise vendored.

Every location is sha256-verified, and a mismatch fails the rebuild.

## What the entrypoint does

1. Records the environment (table above) and compares it with `reproducibility/reference_values_p23.json`.
2. Refuses to run unless the tree is source-only (`tools/source_manifest.py` defines the source set). No generated
   certificate, export, ledger, listing, PDF, zip, `build/` or `__pycache__` may be present.
3. Verifies inherited dependencies and pins:
   * XVI-M `41aa109935f40ddee3109de62c46329c189b5408007970cc90ed5611dc4739ea`;
   * XVI-N-r10 `code/prep/grav_density.py`, read by C5/C6 (pin in `code/classical/inherited.py`);
   * the verbatim XVI-O o70-sync code and notes (`code/matter_loop/*.py`, `notes/*.tex`) against
     `provenance/XVI-O_o70_source_tree.json`;
   * the inherited data input `ledgers/quantum_factor_ledger.json` (`reproducibility/inherited_data_pins.json`);
   * the p13 freeze inputs under `archival/p13/` (pinned in `code/p5_entry/p14_conventions.py`);
   * the archived p14r independent report (pinned in `code/p5_calc/p15_conventions.py`);
   * the archived p15 records: independent and author reports, reference values and the per-file source list
     `archival/p15/p15_source_files.json` (pinned in `code/p5_calc/p16_conventions.py`);
   * the archived p16 records: independent and author reports, reference values and the per-file source list
     `archival/p16/p16_source_files.json` (pinned in `code/p5_calc/p17_conventions.py`);
   * the archived p17 records: independent and author reports, reference values and the per-file source list
     `archival/p17/p17_source_files.json` (pinned in `code/p5_calc/p18_conventions.py`);
   * the archived p18 records: independent and author reports, reference values and the per-file source list
     `archival/p18/p18_source_files.json` (pinned in `code/p5_calc/p19_conventions.py`), and the p20 change log is
     computed against `archival/p19/p19_source_files.json` (pinned in `code/p5_calc/p20_conventions.py`); the p21 change log is computed against `archival/p20/p20_source_files.json` (pinned in `code/p5_calc/p21_conventions.py`).
4. Runs `tools/build.py` from a fresh state, with no cache and sync redirected to `build/rebuild_sync`, so nothing is
   written outside the copy except the tests' temporary directories. Every Python file access is traced
   (`tools/read_trace/sitecustomize.py`). The build regenerates the ℓ2/ℓ3/ℓ4 exports and all residual records, the O5
   matter-loop records and the P.5 entry certificates (including the operational DRED rules and the W6 Hessian-route
   regeneration) and symbolic integrands, then the p15 calculation (`code/p5_calc`: integral library, Batch A, D13)
   and the p15 release gate, then the p16 calculation (`e2_evanescent.py`, `batchC.py`) and the p16 release gate
   `release_p16.py`, then the p17 calculation (`hh_slot.py`) and the p17 release gate `release_p17.py`, then the p18
   calculation (`d11.py`) and the p18 release gate `release_p18.py`, then the p19 calculation (`defect.py`), the
   p19 layer gate `release_p19.py`, the p20 D11 pin (`d11_pin.py`), the p20 layer gate `release_p20.py` and the p21 release gate `release_p21.py`. It runs
   the baseline, certificate/gate-mutation and resumed-build tests, typesets the PDFs, reads them back, builds the zips
   (including the source-only zip), and writes the external manifest.
5. Checks:
   * the p16 layer is accepted (batchA_evaluated, D13_evaluated, batchC_evaluated, E2 decoupling proven,
     D11 NOT evaluated, p16 hard stops), the p17 release is accepted (hh-slot decoupling proven, no evanescent h·h
     counterterm, D11 NOT evaluated in the p17 layer, p17 hard stops), the p18 release is accepted (M2 discharged, D11
     evaluated, full-row slot decoupling, projected identity/restoration NOT earned in the p18 layer, p18 hard stops),
     the p19 release is accepted (quantum_inputs_evaluated earned -- I1, projected_defect_computed,
     projected_identity_verified and projected_restoration_verified earned, bulk_symmetry_restored false, p19 hard
     stops), the p20 release is accepted (restoration on the p20 definition = full sigma_0 closure of the complete
     MS-bar counterterm, K1 correction content, no retracted p19 text, D11_ratio_pin_verified earned, absolute D11
     pin derived and PASS since p21, p20 hard stops), the p21 release is accepted (absolute D11 pin earned, lower layers re-checked live, every package change vs the p20 zip disclosed, p21 hard stops), P.5 entry is earned and the p13 freeze holds;
   * the test groups `baseline`, `certificate_mutation` and `resumed_build` all pass (junit);
   * the PDF readback equals the machine-readable residual records and (p16, F4) the D13, Batch A, Batch C and E2
     value blocks (p17) the hh-slot value block and (p18) the M2, D11 and full-slot value blocks and (p19) the defect value block and (p20) the D11 pin value block, and every page footer carries the
     version label `XVI-P p21`;
   * the external manifest verifies, and all six synced files exist;
   * the rebuilt source-only zip equals the tree;
   * no file outside the tree was read, except a pinned input.
6. Compares with the reference values:
   * ℓ2/ℓ3/ℓ4 export file hashes, polynomial hashes and term counts;
   * `V4_grav.json`, `ell4_conventions.json`, `P14_vertex_tensors.json` and every `exports/P14_integrands/*.json`;
   * content hashes of every P13 classical, P14, P15 and P16 certificate (including `P14_dred_rules`,
     `P15_integral_library`, `P15_batchA`, `P15_D13`, `P15_release`, `P16_E2_evanescent`, `P16_batchC`,
     `P16_release`, `P17_hh_slot`, `P17_release`, `P18_D11_M2`, `P18_D11`, `P18_hh_slot`, `P18_release`, `P19_defect`, `P19_release`, `P20_D11_pin`, `P20_release`) and ledger, and of `RELEASE_STATUS`;
   * the graph statuses, D12 status, the flags, the list of changed contract files, the p19 change log vs p18 and the p19 defect summary and flags, the p20 change log vs p19 (recomputed on the current tree; renamed in p21), the p21 change log vs p20, the absolute D11 pin, the K1 correction, the
     retraction check, the D11 pin and the open pins;
   * W/Q counts of the quartic C7 and master gravitational records at kappa^0, kappa^1, kappa^2;
   * the master table, classical flags, P.5 entry flags, freeze, milestone status, hard stops and test counts.

   The report goes to `--report` (default `build/rebuild_report.json`).

**Ignored in the comparison:** wall-clock timings (`seconds`), the run-specific reproducibility block (the two flags
and the report records), and four freeze sub-records that depend on files correctly absent from a source-only copy
(`archived_zip_sha256_ok`, `list_equals_archived_zip`, `live_report_present`, `live_report_identical_to_archived`;
the last also for the p14r, p15, p16, p17 and p18 records). The author tree holds the author's report, the archived p13 zip and the
reviewers' live p13/p14r reports, and a fresh copy
does not, so these legitimately differ. PDF and zip bytes are not compared because they embed the timings through the listed certificates. Their
content is checked through the readback and the manifest instead.

## Recording a rebuild

* **Author:** copy the passing report to `reproducibility/author_rebuild_report_p19.json` in the author tree, then run
  `python3 tools/build.py`.
* **Independent (separate clean environment):** return the passing report. It is stored as
  `reproducibility/independent_rebuild_report_p19.json`. `release_p19.py` sets `independent_rebuild_passed = true`
  only if the report passed and its `source_tree_sha256` equals the source tree being released.
