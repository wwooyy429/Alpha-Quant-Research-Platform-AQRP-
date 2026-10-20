# 当前真实项目状态

2026-10-21（Asia/Shanghai）。Phase0 RELEASED；Phase1 IMPLEMENTATION REVIEW REQUIRED，独立实现验收尚未完成。PR #2保持Draft，不合并、不打标签、不进入Phase2。

Phase0发布基线7de1d0e81385ae97f98ea673fe05dd726f0b577b；标签对象0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0。main仍502c6931dcfce50bee2f71a80524475fae6396bf。F-001/GOV-010已按原门禁报告CLOSED，原报告与获批内容未改。

用户已经授权Phase1合成数据/通用契约并批准CPython3.13.16，原话见audits/phase-1/AUTHORIZATION.json（初始时间点快照不覆盖）。Gemini对380d9f86467db874033a06a9e6487fd3998e205f的计划预审PASS，原件hash109ec7c92a3e5fd5329d1380abbf381a570bf2690d8f1536a478b96da54f2809；已原字节归档，报告勘误与处置单独记录。

14项P1代码已实现：规范标识/Decimal单位/UTC微秒/IANA日历/PIT修订/行动研究视图/历史池及状态/质量/不可变Parquet与DuckDB索引、环境锁/CI/扫描及测试。实际映射和资料见audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md。102项本地测试通过，门槛未放宽；真实双平台CI及失败历史以implementation/EVIDENCE_INDEX.json为准。旧计划SELF_CHECK/MANIFEST/COMMAND_LOG不作为业务测试证据。

已安装3.13.16标准GIL/x64，完整传递哈希锁和新venv验证；本地构建/venv/缓存/数据产物位于非同步路径。原Baidu工作区Git索引锁反复失败，删除被自动审批拒绝后，使用LOCALAPPDATA/AQRP/checkouts下独立克隆并校验全部复制文件，后续提交从该副本完成。原工作区未reset、未强推、未删除锁，可能保留旧HEAD和已暂存实现；不把它当最新已审版本，准确位置见CHECKOUT_TRANSFER.json。

规范目录106条/16组、canonical CSV hash20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1及P0核心契约保持原字节。F-P1-PRE-001/002/003及F-002/F-003有实现证据，正式关闭待Gemini核对。无真实市场可得性证明、无真实供应商/账户/订单。因子、研究、组合、风险、回测、UI/对应CLI仍Planned，高级扩展Deferred、真实执行Unsupported。

停止点：提交固定SHA实现复核资料，等待Gemini独立代码审查/修复复核及用户Phase1验收。本次不执行发布或下一阶段。
