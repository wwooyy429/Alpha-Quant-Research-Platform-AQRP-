# Round 2 fixed-SHA review instructions

Review PR #4 at its latest complete AQRP_FIXED_REVIEW_SHA from the PR body; never a moving branch. AQRP_BUSINESS_SHA identifies the exact new SDK/CI implementation commit; later evidence-only changes require explicit source/tests/tools/workflow/lock equivalence.

Start with RECONCILIATION.md, ARCHIVE_INDEX.json, raw GPT Work report/task list and preserved failures. Recheck 006–009 plus 001–003; do not apply released f579's failure counts to repaired head. Run the original 16 unedited review cases against the installed fixed-SHA wheel. Inspect all eight formal/unknown table gates, exploratory retention and all six official API rejections, forged formal-manifest revalidation, Windows path escape rejection/package-file invariance, int64 report conservation and exact two-fraction offset handling. Existing DST/naive/date/Golden tests must remain correct.

New EXECUTION_EVIDENCE and original Windows/Ubuntu ZIPs will record only actual runs. Verify run/attempt/head/temporary checkout topology, actual wheel/coverage, exact upload inventory, eight table hashes and query replay. Developer results must not be attributed to Gemini. WORK-P1-004 and historical missing-byte limitations remain explicit. No merge, tag, Phase 2 integration or Phase 3 is authorized by this report.
