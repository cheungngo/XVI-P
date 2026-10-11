# archival/p15 -- the p15 release (first P.5 calculation; superseded as a release by p16)

p15 was released on 2026-10-08: source-only zip `XVI-P-p15-source-only.zip`, sha256
54325c1ff6c079e0389f96d9c0875524c73f6a706e079fd1734c1b1701c707d3, 535086 bytes, 122 files; source tree
79f5375272d6e7327721572ae7eeff59d6bf69d2eb13d353204d38ce9c1dc84f (fce59770... without reference); reference va
  +> lues
reference_values_p15.json 0866adfe0f9dc281053b84dcabbe751a8a7425f522d37839373b4d373415cda8; author rebuild pas
  +> sed
(report 1e729eba...); 75 tests.

INDEPENDENT REBUILD OF p15: PASSED (198/198 entrypoint values equal, 75 tests, own D13 spot-check, own Batch A
omega analysis, own p14r toys under the corrected dred), report `reproducibility/independent_rebuild_report_p1
  +> 5.json`
(archived copy byte-identical, sha256 6bc760c24f48d61fe066dde62cbe5b41daa7e4eafc347f8fd72e1a84fcab4713), bound
  +>  to
tree 79f53752... / zip 54325c1f.... SAME-BOX caveat: same machine as the author build (fresh directory, fresh
venv, from the source-only zip), NOT a second machine. p16 records independent_rebuild_passed_p15 = true; it i
  +> s NOT
inherited by the p16 tree.

Reviewer findings carried into p16: F3 (expr.replace / lambdify bypass of OpaqueDimension; no package use) ->
hardened in p16; F4 (stale footer 'XVI-P p14'; entrypoint PDF readback covered only the 6 classical records) -
  +> >
fixed in p16; F5 (non-contract file changes) -> p16 change log lists all; F6 (D13 spot-check started from the
exported integrand) -> scope note; F7 (E2 evanescent pole, no p14r evanescent counterterm) -> addressed in p16
  +> .

Contents: the p15 source-only zip, RELEASE_STATUS / RELEASE_MANIFEST / README / REBUILD_INSTRUCTIONS of p15, t
  +> he
p15 reference values, the p15 author and independent rebuild reports, the P15_* certificates, P14_dred_rules.j
  +> son
as released in p15 (with the p15 dred correction), the P15 milestones ledger, build records and the science PD
  +> F.
