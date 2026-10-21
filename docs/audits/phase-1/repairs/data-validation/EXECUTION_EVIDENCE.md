# Executed evidence for Phase 1 correction

Business commit: `cdb11cd913e965a43572ceb86efb0a39d1f618df` (parent `6ea8beeac3452738799e0b691535e981810d83f8`; implementation and initial archive in 6ea8bee; cdb11cd only preserves source coverage bytes). Base main: `f579b2c99e762085772de6e70ba1fa98792a7add`. New draft PR: https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/4.

## Actual developer execution

- Clean source archive, hash-locked dependency installation, built and installed `aqrp-0.1.1-py3-none-any.whl`: PASS. Runtime CPython 3.13.16 x64 standard GIL, launched from the already authorized Conda aqrp-p1; package installed in a new isolated venv. Run ID `aqrp-44857d53-7400-4119-87db-13b4f51b6ffc`. SDK wheel SHA256 `34a407a495e03e94b5b6bd61cf95e266e774580937c316ed22fe5355f779a386`. `execution/local-sdk/environment.json`, commands.log, actual wheel and runtime-probe.json retain origin/version evidence.
- Complete installed-wheel SDK: **148 passed**, zero failures/errors/skips. Module line/branch coverage gates, exact environment, independent rational/Decimal reference checks, persisted snapshot/query smoke, pinned secret scanner positive/negative controls: PASS. See commands.log and JUnit/coverage/scanner outputs. Command: Conda Python `tools/ci.py`, AQRP_RUN_ROOT outside source. This is Codex developer execution, not Gemini.
- Original unedited six review regressions against that installed new wheel: **6 passed** (prior developer replay: 4 failures / 2 passes). Full pytest log/JUnit and exit code retained at execution/original-six*. They are additional to the 148 SDK tests.
- Source-only pre/post tests remain separately labeled in developer-source-tests: 46 new semantic cases initially 19 failed/27 passed; after correction entire 148 passed. Frozen original answers and 50 protected files retain hashes; see CORE_PRESERVATION_CHECK.json.

## Remote execution and original ZIPs

PR workflow run **39612329694**, attempt 1, Windows and Ubuntu: success. https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39612329694. Original metadata at execution/github-metadata.json. Temporary checkout `ccf0e9f1861a83a6995be10149239737a85214ec` has parents base main + cdb11cd and tree `e0c4d288d16fc3e117fc5f0622f2783742120b6c`, equal to the business head tree; no merge to main performed.

| Artifact | Original ZIP bytes | SHA256 |
|---|---:|---|
| Windows 12351655951 | 83982 | 098ad1a3ecebfe8e71fee739d7b116fdd75631e4d8a5148e1c6a84a6887fae35 |
| Ubuntu 12350412606 | 83907 | 54e013322b660832d3707097513306fe6f7a0502d83c69800490e506916b236b |

Both original ZIP digests/sizes match GitHub metadata. CRC/path/duplicate/symlink checks pass. Exactly **23 selected files + upload-selection.json** per ZIP: all selected hashes match and no unexpected files. Root inventory: **12 uploaded / 12 verified**; two explicitly omitted tools are gitleaks(.exe) and pinned pip bootstrap. Raw .coverage and actual project wheel are present. Wheel digest matches the SDK receipt; all packaged Python module bytes match the fixed business commit. Each remote JUnit has 148 passed; coverage gates and empty scan findings verified. Eight Parquet table hashes and independent manifest digest verify; installed SDK query replay matches stored results. Windows/Ubuntu logical tables, results and configuration match after documented snapshot identifiers are excluded. See executable `execution/verify_repair_zips.py`, actual output/exit code and zip-verification.json. Downloaded ZIPs are original bytes, never repacked.

## Remaining conditions

WORK-P1-001/002/003 are implemented and developer/CI validated; **independent fixed-SHA review remains pending**. WORK-P1-005 new upload-policy verification is complete on the above run; old historical missing tool/coverage/wheel bytes are still NOT VERIFIED. WORK-P1-004 remains OPEN: no new Gemini SDK/ZIP execution is supplied here. Gemini should review the current fixed PR SHA and code-equivalence evidence; developer evidence cannot be attributed to Gemini. User acceptance of this corrective delivery and separate merge/release authorization are still required.

Phase 2 PR #3 remains on its separate branch, with inherited defects until a separately controlled integration and fresh validation. Factor approval bundle hashes cover shared code; incorporation will require reviewing/re-pinning hashes and rerunning Phase 2 tests/SDK. This task does not change PR #3 source or factor receipts. Existing Phase 1 ACCEPTED/RELEASED history and stable tags remain unchanged; correction itself is NOT ACCEPTED/NOT RELEASED. No Phase 3 development.

Subsequent evidence-only commits do not claim a new SDK run on their own SHA; PR metadata pins the final review SHA and the business SHA. Source/tests/tools/workflow/lock/Golden must compare equal to the business commit before reusing this evidence.
