# 变更记录

## 2026-10-20 · main初始化与Phase0发布门禁（未发布）

- 依据用户明确授权，创建空main初始化提交e87d0082a5e448e9550129a486ba965f13a155f8，保留既有开发历史；仅将该空提交接入开发分支以建立PR共同祖先，无强推、无设计合入main。
- 设置默认分支main并创建Phase0草稿PR#1；最终待审SHA由PR描述固定，不使用漂移分支头或旧锚点代替。
- 纳入Main Baseline Release Gate，新增BASELINE登记、发布前核验/phase0-baseline/main一致性规则。区分AUDIT PASSED、ACCEPTED、RELEASED；当前未审、未验收、未发布，P1 BLOCKED。
- 未创建稳定标签、未合并设计、未执行Phase1业务开发；初始化授权不代表Phase0通过。

## 2026-10-20 · V3.2 Phase 0 待审设计（未发布）

- 初始空仓库；保留V3.0原文，归档V3.1/V3.2来源，建立正式规范。
- 将阶段依赖、PIT数据、事件/订单/账本、样本外隔离、多重检验、四级需求、独立答案、环境/安全和六项专项审计纳入设计。
- 纳入GPT开发/Gemini独立审查/用户批准：计划预审→固定SHA+PR→修复复核→人工验收→授权发布→等待下一阶段。
- 建立双AI审查、ReviewPackage、A–F验收模板和缺陷闭环规则；禁止冒充Gemini报告或以CI替代独立审查。
- 创建编号需求/双向追踪与文档核查工具；当前不包含业务实现，不声称运行测试、环境锁定、Gemini审查或发布成功。
- 未决事项与影响分析见DECISIONS和 `audits/phase-0/CHANGE_IMPACT.md`。
