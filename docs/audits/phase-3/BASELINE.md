# Phase3稳定基线 0.3.0 · 受限工程验收

用户已明确 **ACCEPTED（RESTRICTED ENGINEERING SCOPE）**，授权PR #5合并及发布。普通merge已形成main `70086a74a632c73a2769ec24901ec47babfa8976`。本发布登记与附注标签phase3-baseline/v0.3.0原子推送main并核实同点后为 **RELEASED**；最终发布SHA由 `git rev-parse 'phase3-baseline^{}'` 解析，并在PR #5发布回执记录，避免文件自包含自身SHA。

| 追溯项 | 固定版本/证据 |
|---|---|
| 人工批准原话及范围 | publication/APPROVAL.json |
| 原main | f26255fc40a3080bfa883ad64938f60036a14759，旧标签不移动 |
| 获准PR #5头 | 2a3400c66ebf46b49cb1e9a99e8df5239dc0bfba |
| GPT Work G1 | 3861ef1637bc2b4c28725d7afc5f2e1f02242e80 PLAN PASS；U001仅设计，U002合成口径 |
| GPT Work独立G2 | 9ac5db069287a6e4a095e25ae8c3cc8fa229cded，TECHNICAL PASS WITH CONDITIONS，三缺陷CLOSED；g2-9ac5db0/ |
| 实际合并 | 70086a74a632c73a2769ec24901ec47babfa8976，双父保留且整tree与批准头相同；publication/MERGE_VERIFICATION.json |
| 合并前CI | run39730823159双OSsuccess；原独立raw ZIP核验保留9ac，publication/PREMERGE_CI.json明确证据范围 |
| 合并后本地干净SDK | aqrp-5d9c2b54-0b9f-4c4c-826b-c90e56192b12，578通过，0失败/错误/跳过；python3.13.16；真实wheel hash 0e5f14a20d6c54b4fc69cde01babf4bf567336e74de4f363036363e649394f01 |
| 追加开发方验证 | 原20/原四通过，原数学91通过；不是新独立审查，原脚本内旧标签另记实际执行身份 |
| 软件/依赖/数据/结果 | publication/BASELINE_FILES.json、sdk/environment.json、SDK_VERIFICATION.json及SDK_ARCHIVE.json |
| 不变源码bundle | 3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e，工程receipt仍TEST_ONLY/ENGINEERING_APPROVED/NONE |

## 批准范围与影响

26项原需求（23 MVP、3 Competition Ready）的工程实现、完整研究链路与证据在用户受限范围内验收。金融批准、真实隔离和正式独立Test明确延期，保持NOT VERIFIED；没有把本地工程测试写成真实隔离/正式研究批准。历史复现按已验证软件包、锁、旧因子Ref和声明投影结果重放验收，完整历史宿主字节复刻仍未验证且不属于当前验收必需范围。逐需求影响见publication/DEFERRED_CONDITIONS.json；原106目录及原独立报告不改。

正式ApprovedScores所需FACTOR-009/VALID-008的真实金融依赖仍未满足。用户另授权Phase4计划预审，可以设计明确SYNTHETIC/ENGINEERING_TEST_ONLY输入路径，但不能静默伪造金融批准或让正式入口绕过门禁。G1通过不等于P4实现/金融批准/用户验收。

本发布提交只增加证据/状态，src/tests/tools/workflow/构建/锁/扫描配置与已合并并实际运行SDK的版本字节一致。publication SDK是声明子集；完整本地选择ZIP含所有185项及选择清单，并列出每个Git省略文件hash，不冒充GitHub原ZIP。原独立证据及所有失败历史保留。

没有真实部署、账户/ACL/服务/调度变更或实盘。Phase4只从核实已发布main创建独立计划分支，交GPT Work固定SHA预审；用户未授权P4实际实现、合并/标签或P5。
