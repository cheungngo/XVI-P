# archival/p17 -- the p17 release (D01/D03 evanescent poles vs the ch slot; superseded as a release by p18)

p17 was released on 2026-10-08: source-only zip `XVI-P-p17-source-only.zip`, sha256
7f4f61df9ce9c6483d76fa7b7b024591d6abfbae80ddc3dc0bee387245d25416, 678669 bytes, 144 files; source tree
2a5a6317f7322db910c26fb257e589b28aa017df740879194e0ac2eb505ddd92 (8a6658a8... without reference); reference va
  +> lues
reference_values_p17.json d4345c282aee89676ee7d0b077fd8fc94ebd8735cd78499550b2666a0b9103b1; author rebuild pas
  +> sed
(282/282; report bd7d8bae...).

INDEPENDENT REBUILD OF p17: PASSED, report `reproducibility/independent_rebuild_report_p17.json` (archived cop
  +> y
byte-identical, sha256 92542a2215c24b984e2220f69ac52698d6b09dbb6b860402bbc367d970c176eb), bound to tree 2a5a63
  +> 17... /
zip 7f4f61df.... SAME-BOX caveat: same machine as the author build (fresh directory, fresh venv, from the sour
  +> ce-only
zip), NOT a second machine.  p18 records independent_rebuild_passed_p17 = true; it is NOT inherited by the p18
  +>  tree.

Reviewer findings carried into p18: H1 (static-scan pattern gaps: Poly(e, d)(4), as_poly(d)(4), Horner via
all_coeffs, type(x)(*args) / x.__class__(*args), getattr indirection, aliased sympify import, sympify locals w
  +> ith a
plain Symbol('d') value, plain Symbol('d') creation; no package use) -> the tests/test_p18.py scan flags all o
  +> f them
(planted violations detected), still a pattern check, not a proof; H2 (assignment table omitted c hat / h tild
  +> e) ->
seventh assignment added (P18_hh_slot.json; the reviewer's value X_D01 = p.p^2 a~.b~ c^.p/16 = -X_D03 is repro
  +> duced);
H3 (stale comments: dred.py matches comment; PARSE_SITES_REVIEWED header) -> corrected (dred.py: documentation
  +> -only
revision, AST unchanged); H4 (curly apostrophes in typeset listings) -> straight quotes in verbatim listings
(preamble, upquote mechanism via textcomp); H5 (parse_d(srepr(e)) raises, undocumented) -> documented (fails
closed); H6 (scope: D11 unevaluated) -> p18 discharges M2 and evaluates D11.

Contents: the p17 source-only zip, RELEASE_STATUS / RELEASE_MANIFEST / README / REBUILD_INSTRUCTIONS of p17, t
  +> he
p17 reference values, the p17 author and independent rebuild reports, the P17_* certificates, the P17 mileston
  +> es
ledger, the p17 per-file source list (base of the p18 change log) and the science PDF.
