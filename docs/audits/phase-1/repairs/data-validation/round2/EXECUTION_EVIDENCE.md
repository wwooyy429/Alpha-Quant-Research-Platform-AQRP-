# Round 2 actual execution evidence

Business SHA **8902ba00a818150bf00af8d051a3837bc79e6bfc**, parent **3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f**. Candidate remains 0.1.1 in PR #4. Code scope: core/time.py, data/quality.py, data/pit.py; 86 new semantic tests supplement 148 prior tests. No dependency/schema/signature/Golden/core-design change.

## Clean installed-wheel SDK

Executor **Codex developer**, not Gemini. CPython 3.13.16/x64/GIL, existing approved Conda launcher; new isolated clean venv, hash-locked install and project wheel built from the committed Git archive. Run ID `aqrp-b86f8693-15fb-4c3b-b0ba-c92193d3ab62`; dirty=false, complete=true. Exact commands/output are in execution/local-sdk/commands.log, environment.json and the outer console/exit files. Runtime-probe.json confirms the installed site-packages origin. Wheel SHA256 **93325fa3accd551b90f1087726ab4db01f7cd54e96e8e83f611e426f579302f6**; actual wheel and raw coverage are archived.

**234 passed, zero failures/errors/skips**. Ruff, module line/branch coverage gates, rational/Decimal reference checks, eight-table persisted snapshot/query smoke, pinned scanner positive/negative controls and clean source scan PASS. Original unedited review cases (10 second-round + 6 first-round), run separately against that installed SDK: **16 passed**, see original-sixteen.log/JUnit/exit. They are additional to the 234 SDK tests.

Source-only failures are preserved in developer-source-tests: initial installed previous SDK replay 7failed/9passed; new86 cases before changes 33failed/53passed; first implementation234 run 1failed/233passed (simplified internal PIT record compatibility), final source run234passed. The report's original released-source11failed/5passed remains unchanged in review-input. No developer replay is attributed to the report author or Gemini.

## New remote CI and original ZIP bytes

Workflow **39615639480**, attempt1: Windows/Ubuntu both success, each **234/0/0/0** in JUnit. https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39615639480

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Ubuntu 12351654578 | 86007 | c64d081898ded2009cccb4295f35f0a0449ac1c058de380cc77fc55f72465cc4 |
| Windows 12351629581 | 86167 | 1a2369adea3c4b502d06a9374e3304d008f6ab2cc599f110ea60237e3ae604fe |

Both original, unrepacked ZIPs match GitHub metadata size/digest. Each has exactly23 selected files plus upload-selection.json; all hashes match, no unlisted files. Twelve uploaded root inventory files all match; two tools (pinned gitleaks and pip bootstrap) are explicitly omitted. Raw .coverage is present. Each actual installed project wheel matches its environment receipt; packaged Python module bytes match the business commit. Root CRC/path/duplicate/symlink checks, coverage gates, empty scan findings, eight Parquet hashes, independent manifest digest and installed SDK query replay pass. Windows/Ubuntu logical table data, smoke results and config match after documented snapshot identifiers are excluded. All commands and checks are in execution/verify_repair_zips.py, zip-verification.log/exit/json and github-metadata.json.

Actual PR temporary checkout **60c2fbbc3269dc619ba928be883338a0c7986a09** has parents stable main f579b2c99e762085772de6e70ba1fa98792a7add and business8902ba0; its full tree equals the business tree. This is GitHub's test merge object, not a merge into main. Final evidence-only SHA must compare equal for source/tests/tools/workflow/build/lock/Golden to reuse this execution evidence.

## Remaining gates

WORK-P1-001–003 and006–009 are implemented and developer/CI validated; **fixed-SHA independent review is still pending**, not CLOSED by developer assertion. WORK-P1-004 Gemini full SDK/ZIP execution remains OPEN unless the user separately decides on its limitation. WORK-P1-005 new upload behavior is verified on both current original ZIPs; historical missing bytes remain NOT VERIFIED. Phase0's checked scope has no new reported blocker, but original execution provenance limits remain.

User acceptance of this corrective delivery and distinct merge/release authorization are absent. Phase2 PR #3 remains technically blocked on controlled incorporation, independent review, re-pinning shared-code approval hashes and fresh Phase2 SDK/CI. No main/tag/Phase2 source update and no Phase3 development.
