# archival/p19 -- the p19 release (P.5 identity step: projected one-loop kappa^2 ch-identity defect; supersede
  +> d by the p20 correction)

p19 was released on 2026-10-09. Source-only zip `XVI-P-p19-source-only.zip`: sha256
da9242752d2e3753d8b2ce7fbb21e7cdb28487cc7966c2ca52d1ef1376658875, 839598 bytes, 164 files. Source tree
fcf90354d746e244fa2839048118bd8d64b1859ffd3825c0bfa3e1138ee88f36. Reference values reference_values_p19.json
08f10fa8.... Author rebuild passed (320/320; report 5f0715f3...).

INDEPENDENT REBUILD OF p19: PASSED, with findings. Report `reproducibility/independent_rebuild_report_p19.json
  +> `
(archived copy byte-identical, sha256 1b01f1d8e509afedcfd73d91685806205c56e7fe57a500b3a0bf008dd2811f45), bound
  +>  to
tree fcf90354... / zip da924275.... SAME-BOX caveat: it ran on the same machine as the author build (fresh dir
  +> ectory,
fresh venv, from the source-only zip), NOT on a second machine. p20 records independent_rebuild_passed_p19 = t
  +> rue; the
p20 tree does NOT inherit it.

Reviewer findings, all corrected in p20 (a correction release, no scope expansion):
- K1 (medium): the p19 claim "full sigma_0 closure of the MS-bar counterterm fails with the derived factor +1,
  +>  needs -1,
  unresolved" was WRONG. It was a Grassmann-orientation bookkeeping error: the P15 Sigma coordinates are (cb,c
  +> ), the
  route-G slots (c,cb). Corrected: the derived +1 closes the complete counterterm in h.c, c.b and c.cbs; Sigma
  +>  is
  (+3/8, -1/4) in (c,cb) coordinates. The p19 text is retracted (erratum in manuscript/notes/P20_correction.te
  +> x).
- Quotient c.cb orientation (low): clarified in p20; all coordinates are now stated in route-G labels.
- Restoration flag not independent (low/medium): REDEFINED in p20 as full sigma_0 closure of the complete MS-b
  +> ar
  S_ct, including c.cb. The p19 criterion is kept as a route-consistency control.
- Mutation criterion / blind spots (low): the p20 full-closure detector catches drop D13 and flip K.c. The p20
  +>  D11
  ratio pin (trace anomaly, spin-0 : spin-2 = 10 : 1) catches drop D11; the absolute pin stays OPEN.
- J1 wording (info): the Q(i) counts are the real dimensions under a compatible real structure.
- I2 scan misses (low): seven patterns added (still a pattern check, not a proof).
- Gate stale RELEASE_STATUS (low): a standalone reject now removes RELEASE_STATUS.json.

Contents:
- the p19 source-only zip;
- RELEASE_STATUS, RELEASE_MANIFEST, README and REBUILD_INSTRUCTIONS of p19, and the p19 science PDF;
- the p19 reference values and the p19 author and independent rebuild reports;
- the P19_* certificates as released, with the P19 milestones ledger;
- p19_source_files.json, the base of the p20 change log.

The archived P19_* certificates carry the retracted K1 text as released. The active p19 layer files in the p20
  +>  tree
are corrected.
