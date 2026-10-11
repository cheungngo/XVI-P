# archival/p14 -- the p14 release (superseded by the p14r repair)

p14 was released on 2026-10-08 (source-only zip `XVI-P-p14-source-only.zip`, sha256 7a43e8b0a374000d9ec565b64d
  +> d95d8deec5f3612512ed322307859e5e7a19ba,
source tree c8c6e044bc0a2a6cbf94276b6b125cd94c95d8496486be5221fc5b99d03158aa; author rebuild passed;
independent rebuild of p14: pending, never run). This directory keeps that release for provenance only. It is 
  +> NOT
p14r evidence and is not read by the p14r pipeline.

Contents: the p14 source-only zip, RELEASE_STATUS / RELEASE_MANIFEST / README / REBUILD_INSTRUCTIONS of p14, t
  +> he p14
reference values (`reference_values_p14.json`) and author rebuild report (`reproducibility/author_rebuild_repo
  +> rt_p14.json`),
the P14_* certificates and ledgers, the p14 P.5-entry code, tests, tools, notes, build records and the science
  +>  PDF.

Why p14 is superseded (narrow p14r repair; P.3/P.4 classical code unchanged, no loop evaluation):

1. The prescription was "DRED-type" in words only: no executable index rules, and it claimed that no evanescen
  +> t
   remainder arises. p14r makes DRED operational (code/p5_entry/dred.py, certificates/P14_dred_rules.json). Th
  +> e
   rules are g4 = ghat + gtilde with tr ghat = d and tr gtilde = 4-d; l and p in QdS; exported l_r lifted as l
  +> .e_(r);
   ghat-projected Gram/PV reduction; all contractions before the Laurent expansion with d symbolic; evanescent
   parts retained. The "none arise" claim is withdrawn.
2. The D11 M3 labels conflated the scalar-extension scaling degree (4) with the kernel bound (8). p14r states:
   kernel scaling degree at most eight; degree of divergence at most four; contact derivative order at most fo
  +> ur;
   sd(d^alpha delta) = 4 + |alpha|. M3 is now conditional on M2. Exactly degree four is an explicit normalizat
  +> ion
   condition N4; the order-0 and order-2 contacts are enumerated.
3. The counterterm quotient was called "essential counterterm directions". It is now "eight candidate directio
  +> ns
   modulo the computed exact equivalences, before imposing the relevant identity constraints". D cap ker sigma
  +> _0 has
   not been computed.
4. W5 regenerated only D14a-c, D11 and D13. p14r adds W6, an independent Hessian/Tr-log regeneration of D01, D
  +> 02,
   D03 and D12. The on-shell check is renamed "Ward contraction with two free on-shell graviton legs and an of
  +> f-shell
   gauge leg".
5. The p14 gate-mutation test copies lacked the frozen tests/ inputs, so every copy was unfrozen and P.5 mutat
  +> ions
   were rejected for the wrong reason. p14r copies all frozen inputs and adds an unmutated baseline that must 
  +> be
   accepted.
