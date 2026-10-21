# Round 2 receipt and reconciliation

The user's follow-up supplies a second GPT Work supplemental report and task list. They are untrusted source material, not new Gemini advice or acceptance. The prior human authorization to verify/archive/repair Phase 1 data defects through an independent PR continues to govern this corrective work. No new architecture, frozen financial answer, requirement, Phase 2 feature or publication authorization is inferred from the attachments.

## Target correction

The report reviews released main f579b2c99e762085772de6e70ba1fa98792a7add, not PR #4's corrected 3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f. Its 001–003 OPEN findings are valid against that old release; they do not reverse the six passing regressions at the new PR. Developer replay on the installed previous repair SDK gives **7 failed / 9 passed** across the unedited 16 review cases. The seven failing negative cases map to the four newly confirmed issues 006–009; the six first-round regressions and remaining three controls pass.

The original report's **11 failed / 5 passed** belongs to its fixed released-source execution; neither counts nor target are rewritten. Source-only and clean installed-wheel evidence are kept separate. This round's 86 new semantic cases initially have **33 failed / 53 passed** against previous repair source. The first implementation run had **1 failed / 233 passed** due to a simplified internal PIT reference record lacking quality_status; the compatibility fix retains records without that optional helper key while rejecting explicit UNKNOWN_AVAILABILITY. The preserved second run has **234 passed** with line/branch coverage gates passing. These are Codex developer executions, not Gemini.

Phase 0: report found no new blocker in its inspected design/release scope. Developer checked the archived Phase 0 ZIP's 69 manifest entries, all match. This does not certify Gemini's original execution, repeat its whole audit, or alter Phase 0 acceptance/tag. The 106-item/16-group classification is unchanged. Source reports and all 113 manifested original evidence files are byte-archived with the original manifest.

## Finding response

| ID | Requirements | Minimal handling | Current state |
|---|---|---|---|
| WORK-P1-006 High | DATA-002/006/009, QA-002 | All eight dataset tables reject explicit unknown flags or absent availability for formal PIT; normalization retains unknown quality even with missing observations; visible_rows adds a defensive flag check; existing sealed snapshot read validation rechecks all tables | Implemented, source tests pass; new SDK/CI/ZIP PASS at8902ba0; independent fixed-SHA review pending |
| WORK-P1-007 Medium | DATA-003/007, ENV-001, QA-002 | Validate portable IANA components before package resource lookup; reject drive/absolute/backslash/dot paths; all data still resolves only through locked tzdata | Implemented, namespace/external-file invariance and prior DST tests pass; new SDK/CI/ZIP PASS at8902ba0; independent review pending |
| WORK-P1-008 Medium | DATA-006, QA-002 | Integer upper bounds follow Arrow field bit width before table construction; structured code/field remain available from normalize, rejected row index/code from unchanged QualityReport | Implemented, overflow/negative/bool/string/fractional rejection, maximum int64 and mixed-batch conservation pass; independent review pending |
| WORK-P1-009 Medium | DATA-002/003, QA-002 | Inspect every fractional segment before parsing; explicit ISO calendar timestamp/offset grammar; exact offset microseconds, including offset seconds, reconstructed without truncation or minute/second overflow normalization | Implemented; two-fraction, zero-tail, signed offset and malformed offset tests pass; independent review pending |

No blanket exception swallow, empty-success workaround, synthetic availability replacement or Golden relaxation. Candidate version stays 0.1.1 within the unmerged corrective PR. Full source change is limited to core/time.py, data/quality.py, data/pit.py and semantic tests. Existing signatures/schemas/dependency lock remain fixed.

WORK-P1-001–003 remain implemented but awaiting independent review of the correction; 004's designated independent execution is still OPEN; 005's new policy is already developer-verified on original first-repair CI ZIPs, while historical missing bytes remain NOT VERIFIED. No report is modified or signed as Gemini. PR #3 remains technically blocked on incorporation/review/re-pin/revalidation; its source branch and receipts are untouched.

Latest execution: clean installed-wheel SDK234passed, original16reviewcases16passed, Windows/Ubuntu CI and both original ZIPs PASS. See EXECUTION_EVIDENCE.md. Developer verification is complete for this implementation SHA; independent review and acceptance remain pending.
