# Phase 2 稳定基线 0.2.0

人工验收 **ACCEPTED**。本登记与新附注标签 `phase2-baseline`、`v0.2.0` 原子推送至远端main、确认三者同点后为 **RELEASED**；本地生成文件不构成发布。最终发布SHA解析 `git rev-parse 'phase2-baseline^{}'`，完整值与标签对象记PR #3发布回执，避免文件自包含自身SHA。

| 项目 | 固定版本 / 证据 |
|---|---|
| 用户明确原话 | 验收通过，请合并打标签后进入phase 3开发 |
| 批准范围 / 原话 | publication/APPROVAL.json，Phase2验收/合并/标签及Phase3启动；P3仍走计划预审 |
| 原main | fb1ba4fd51202a303115e4449ee49db09ccc071c，保留v0.1.1/旧阶段标签 |
| 获准PR #3头 | e50cd75bf461b6ba02856591d5ef968c622da609 |
| 补充审查SHA | c8362953f555606795b6804cdfe28ff690c2364d，GPT Work技术PASS、001–003补充CLOSED |
| 业务修复SHA | 708b83be1dd597395b41f2ff6e10702749175bbf |
| 实际main合并 | bb6076f87f616a98feb98287d661830b102ad015，双父原main+批准头，tree完全相同；publication/MERGE_VERIFICATION.json |
| 合并前CI | run39642052818/39642046066，Windows/Ubuntu均success；publication/PREMERGE_CI.json |
| 合并后SDK | aqrp-aa4741d8-294c-45eb-8a11-838267e1cdca，干净归档构建并安装0.2.0真实wheel，417通过、0失败/错误/跳过 |
| 外置原始回归 | 未修改原16项16通过，原四探针4通过；publication/original16.*与original4.* |
| 完整环境/文件/数据hash | publication/sdk/environment.json、BASELINE_FILES.json、FILE_MANIFEST.json |
| 代码准入bundle | 51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d，工程TEST_ONLY/NONE |
| 独立审查来源 | gemini/保留原Gemini计划/实现/数学审查；recheck-c836/为GPT Work最终补充复核原件 |

当前26模块Factor Registry与三内置及已修复数据/配置/PIT边界组成已验收范围。417项适用测试、逐模块覆盖、独立参考、数据/因子smoke及秘密扫描正负控制通过。发布登记提交仅证据/状态，源码/正式测试/工具/CI/构建/锁/Golden/receipt与已合并树相同；所有旧失败、报告及原始数据保留。

不把用户明确验收改写为Gemini本人新执行或逐项历史证据豁免。GPT Work补充复核是真实来源；Gemini新完整SDK、旧P1未上传字节、旧综合工具原件等NOT VERIFIED事实保留。用户本次明确批准交付并授权发布/启动，按最新决定执行，不能再沿用旧待验收/未授权阻止已授权动作。OS恶意插件沙箱/真实数据/账户/订单未开放。

Phase3必须从已核实本main基线新建独立分支，先提交26项规范范围的研究/验证计划、接口、Golden候选与预审资料，Gemini计划预审及阻断问题闭环前不写P3业务实现。Phase4–7与P3合并/发布仍须另行授权。
