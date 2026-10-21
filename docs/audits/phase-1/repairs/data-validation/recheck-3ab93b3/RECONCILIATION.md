# Receipt of GPT Work fixed-3ab93b3 recheck

Report target: **3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f**. The supplied 39-character prefix resolves uniquely to this existing Git commit. Report target is the first correction; it explicitly excludes subsequent business8902ba00a818150bf00af8d051a3837bc79e6bfc and evidence head16083e151e3dadc11981c878f5aa90b7b09e9ac4. Report verdict is BLOCKING for that old target, not a regression verdict for the current correction.

## Evidence actually received and checked

Original report, task list, source ZIP, SDK root logs/environment/JUnit/coverage, actual newly built wheel, old failure logs, facts and ZIP validation receipts are supplied. All59 source-manifest entries match size/SHA256;57 are copied, two pinned tools (gitleaks.exe and pip bootstrap) are explicitly omitted from this repository receipt after their source hashes are verified. Their omission is new archival policy, not fabrication of historical CI bytes. Original manifest stays unchanged. Eight smoke Parquet files and their manifest are also copied and verified against their original snapshot manifest.

SDK receipt/JUnit confirms148/0/0/0, dirty=false, complete=true at3ab93b3, runaqrp-693e8864-c8ff-4369-86c3-defabf81dffd; external16 case JUnit confirms7failures/9passes and exit1. New review wheel SHA256d99d7ffc508db253c85459cea40a7b1a1813bea937f14e3f32df15dd56e9510d;17 Python module bytes match the fixed Git source and source ZIP. Original external test script hashes match. Referenced original CI ZIPs already archived in ../execution/ match the report digests and each exact23-file upload selection.

This intake performed static, receipt and byte checks only. It did not run another SDK/test suite or repeat query replay. The supplied GPT Work execution and the prior Codex/CI executions retain separate provenance. No Gemini full SDK/ZIP receipt is provided by this report.

## Version-scoped disposition

| ID | This GPT Work recheck at3ab93b3 | Current business8902ba0 / evidence16083e1 | Remaining gate |
|---|---|---|---|
|001 High|Supplemental recheck PASS: invalid field units rejected, legitimate conversion controls retained|Developer full234/16case evidence exists; no new code for this receipt|Independent review of current fixed SHA and human acceptance|
|002 High|Supplemental recheck PASS: ex-session and effective-time handling|Developer234/16pass; receipt does not retest later changes|Current fixed-SHA independent review|
|003 Medium|Supplemental recheck PASS: known OHLC inequalities with missing fields|Developer234/16pass|Current fixed-SHA independent review|
|004 Medium evidence|OPEN: designated Gemini execution missing|Unchanged; GPT Work execution cannot substitute|Gemini actual fixed-SHA execution or separate user decision|
|005 Medium evidence|New upload policy and actual old-business ZIP23/12 files, wheel/coverage/data/query verification CONFIRMED|Policy also developer-verified on round2 CI original ZIPs|Historical missing bytes remain NOT VERIFIED; no blanket historical closure|
|006 High|OPEN at3ab: four negative cases fail|Already implemented at8902ba0; developer234/16pass; no duplicate repair|Independent verification of newer fixed SHA|
|007 Medium|OPEN at3ab: external IANA path accepted|Already implemented at8902ba0; developer234/16pass|Independent verification of newer fixed SHA|
|008 Medium|OPEN at3ab: overflow bypasses row report|Already implemented at8902ba0; developer234/16pass|Independent verification of newer fixed SHA|
|009 Medium|OPEN at3ab: second fractional segment bypasses resolution gate|Already implemented at8902ba0; developer234/16pass|Independent verification of newer fixed SHA|

001–003 can now be recorded as **GPT Work supplemental recheck PASS at3ab93b3**. This is neither Gemini global closure nor Phase1 correction acceptance/release. 006–009 remain historically OPEN at3ab and are already fixed in later code; the old failures are not carried forward as proof of present failure. Current head is not certified by this recheck. No repeated code fix or test rerun is justified solely by receipt of an old-target report.

## Remaining release conditions and CI

Prior evidence16083e1 workflow39616587448, previously queued, is now confirmed API success on both Windows/Ubuntu; PRIOR_HEAD_CI.json records the response. This is metadata verification, not another raw-ZIP inspection. New receipt-only commit keeps source/tests/tools/workflow/build/lock/Golden equal to business8902ba0; final review SHA is pinned in PR #4 body.

Next independent review must use that complete new review SHA, with business8902ba0 as the code anchor, and inspect round2/REVIEW_PACKAGE.md and round2/EXECUTION_EVIDENCE.md (234 SDK tests,16 original cases and round2 original ZIPs). Do not ask the reviewer to rerun3ab when validating the newer correction.

Gemini/designated evidence, independent current-SHA review, user correction acceptance and separate merge/release authorization remain pending. Phase2 PR #3 still requires controlled incorporation, shared-code approval hash/receipt review and fresh Phase2 validation. main/Phase0+1 tags/Phase2 branch stay unchanged. No merge, tag, Phase3 or new business implementation in this intake.

## Windows checkout path correction

Receipt commit837983f triggered run39620003625: Ubuntu PASS; Windows Git checkout failed with Filename too long before SDK start, then always-upload had no run artifacts. Full decoded job log and API steps are retained in WINDOWS_CHECKOUT_FAILURE files. The original SDK run directory is relocated to sdk/ inside this receipt, with per-file before/after path and identical SHA256 in RECEIPT_INDEX.json. Original source manifest, report bytes and all financial/code assets remain unchanged. No workflow policy is changed or failed test suppressed.
