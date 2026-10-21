# GPT Work 补充审核 — 第二轮修复任务

固定Phase1目标：`f579b2c99e762085772de6e70ba1fa98792a7add`。

## F. 给Codex的增量修复任务及复核条件

由用户转交；没有向任何开发聊天发消息。修复建议不构成需求/架构变更批准或用户验收。

| ID | 最小修改范围 | 必须保留 | 验证要求 |
|---|---|---|---|
| 006（High，优先） | 正式数据集与查询准入统一检查UNKNOWN_AVAILABILITY，不只看时间戳为空 | exploratory原件保存、不得伪填available_at或改标VALID | 四表未知标记+缺时间+exploratory/正式SDK入口的负例及已知正例 |
| 007（Medium） | iana键解析/资源范围检查，封堵Windows绝对/反斜杠路径 | 锁定tzdata、合法IANA及DST规则 | Windows外部文件拒绝；合法IANA固定快照不受包外文件变化影响 |
| 008（Medium） | schema整数上界校验及逐行错误归类 | int64持久类型、QualityReport计数守恒 | 上溢/下溢/bool/字符串拒绝；最大合法int64通过；不得用空成功结果代替 |
| 009（Medium） | 完整timestamp/offset语法与无损精度校验 | UTC微秒、合法offset、合法零尾数、date与naive拒绝 | 双小数纳秒拒绝、正常微秒正例、DST/跨UTC日期回归 |
| 001–003 | 沿用上一轮最小单位/行动日期/部分OHLC修复 | 正确Golden/容差、RAW、ex-session和合法null | 本轮旧4个失败断言应全部转为满足原契约，5项正控保持通过 |
| 004–005 | 补充独立执行与新CI原始wheel等证据；保留旧缺项 | Gemini原件、历史日志/ZIP、用户原话 | 不用本地新原件补造旧CI或代签Gemini；新SHA证据归属清楚 |

Phase0：目前不建议为“整理旧状态”重写已发布基线或原报告。本轮新反例指向Phase1实现不完整遵守既定契约，先修实现；若需要修改核心契约，应另列影响/批准，不以改文档或Golden消除失败。

请开发者提供**修复后的新完整40位SHA**，关联父SHA、每个问题ID、最小diff、测试命令/解释器/退出码/完整失败与成功日志、Windows/Linux run/attempt/head/checkout、wheel/锁/快照/数据hash。关键修复在新SHA复核；不得移动稳定标签、直接合并main或自动启动后续阶段。若原工作正处于Phase2，应明确修复的Phase1回归范围，不能将本清单当作额外Phase2功能授权。

**本轮最终结论：Phase0已检查范围未发现新增阻断问题；Phase1发现阻断问题。仅为GPT Work补充审核，不代表Gemini关卡通过、用户接受执行限制、用户验收或任何新增发布授权。**

报告时间：2026-10-21T21:43:37.961119+08:00（Asia/Shanghai）。
