# Phase 1 已发布基线登记

**人工验收：ACCEPTED；发布：RELEASED。** 生效依据为本登记所在提交与 `phase1-baseline` 同时发布到远端 main 并经核验；仅生成本地文件不构成发布。

日期：2026-10-21（Asia/Shanghai）。用户分别明确“phase 1验收已完成”和“请开始合并并打标签”，原话、SHA绑定及权限范围见 publication/APPROVAL.json。未授权 Phase 2。

| 项目 | 固定版本 / 核对入口 |
|---|---|
| 仓库 / 主干 | https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- / main |
| 稳定标签 | phase1-baseline（附注标签，发布后不移动） |
| 最终基线 Commit | 解析 `git rev-parse 'phase1-baseline^{}'`；发布完整 SHA 与附注对象同时记入 PR #2 发布回执，避免在提交文件内自包含自身 SHA |
| 用户验收对应交付 | 71cc044d5f4e2079426049c0f7c6f747fee01692 |
| 获准合并 PR #2 head | 18d51fbecc4a1526f2ab75d34874a0b25d00f6c1，相对验收交付仅增加人工验收/状态记录 |
| 实际合并 Commit | 9b843b17ccf362cf5b7a5351269559a627c55b32，双父保留历史，完整 tree 与 PR head 一致 |
| 业务固定 Commit | 74bdb9216c585d27de91123605aff0266ca028cc |
| 原 main / Phase 1 起点 | 502c6931dcfce50bee2f71a80524475fae6396bf |
| 合并前 CI | Run39581713605，Windows/Ubuntu全部适用检查成功 |
| 合并后完整 SDK | aqrp-04427a93-6375-4f62-9719-45b05084a7ad，代码 9b843b17ccf362cf5b7a5351269559a627c55b32，102测试/0失败/0错误/0跳过、覆盖率/参考数学/smoke/秘密扫描与正负控制通过 |
| 合并与测试证据 | publication/MERGE_VERIFICATION.json、publication/sdk/ |
| 数据/代码/环境文件版本 | publication/BASELINE_FILES.json、publication/sdk/environment.json；锁hash 86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb |
| Gemini 原始审查 | gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json、gemini/SDK_HASH_INCREMENTAL_INDEX.json；原报告不改 |
| 人工验收证据 | acceptance/ACCEPTANCE.json；当前授权以 publication/APPROVAL.json 为准 |

最终发布登记提交仅维护文档和可核对的证据，不修改源代码、测试、CI、依赖锁、Golden或Phase0的50份冻结资产。版本清单与最终提交由 publication/MANIFEST.json、Git对象及远端main/tag相互核实；新清单不替换旧固定版本快照。

保留边界：本机SDK、原始ZIP可用字节/八表/跨平台/SDK回放由开发方实际执行，不改写成Gemini独立运行。Gemini全量SDK/原始ZIP执行证据仍不完整；旧远端ZIP每平台3项根清单文件及项目wheel原字节仍缺失。用户已验收并另行授权本次合并/标签，但未逐项描述豁免；不伪造豁免原话。Gemini尚未执行本次最终main独立Gate，不声称已执行。

Phase0 `phase0-baseline` 仍指向7de1d0e81385ae97f98ea673fe05dd726f0b577b，不移动。Phase1发布不代表Phase2获准启动；下一阶段必须从核实main基线创建独立分支并取得用户另行授权。
