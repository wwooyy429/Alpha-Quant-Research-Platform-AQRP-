# Fixed-SHA repair review package

Latest receipt: recheck-3ab93b3/RECONCILIATION.md records GPT Work supplemental PASS for001–003 at3ab93b3 and confirmation of005 new upload policy. Later006–009 fixes at8902ba0 are outside that report; current fixed-SHA independent review and004 remain pending. No new business changes or test executions in this receipt.

Latest round 2 corrective work: see round2/RECONCILIATION.md and round2/REVIEW_PACKAGE.md. The newly supplied report targets released f579, not repaired PR #4. Four additional confirmed implementation defects (WORK-P1-006–009) are being corrected within the previously authorized Phase 1 data-contract repair scope. Round 2 adds 86 semantic cases (234 total source tests passing); new clean SDK234tests, original16cases, dual-OS CI and original ZIP checks PASS at8902ba0; see round2/EXECUTION_EVIDENCE.md. Prior text below is first-round evidence at 3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f, not proof that the new defects are independently closed. Core contracts and Golden answers remain frozen.

Repository: https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-

New draft repair PR #4 pins AQRP_FIXED_REVIEW_SHA and AQRP_BUSINESS_SHA. Do not review a moving head. Compare to main f579b2c99e762085772de6e70ba1fa98792a7add. Read AUTHORIZATION, raw review-input reports, ARCHIVE_INDEX, DESIGN_AND_SCOPE, DEVELOPER_RESPONSE, TRACEABILITY and EXECUTION_EVIDENCE.

Independently rerun installed-wheel SDK and the six original review regressions; examine all 46 new semantic cases, especially market-local ex-date and partial missing OHLC. Verify the original new CI ZIPs against GitHub digest, exact upload-selection hashes, actual wheel/.coverage bytes and smoke manifests. Historical missing bytes and Gemini execution gaps remain explicit limitations. No developer test or GPT Work report is a substitute for Gemini fixed-SHA review or user acceptance. Do not merge/tag or start Phase 3.
