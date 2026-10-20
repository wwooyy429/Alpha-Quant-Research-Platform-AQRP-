# 当前真实项目状态

2026-10-21（Asia/Shanghai）。Phase0 RELEASED；Phase1 AUDIT PASS AS REPORTED / REPORT ERRATA CLARIFICATION REQUIRED，用户阶段验收尚未发生。PR #2保持Draft，不合并、不打标签、不进入Phase2。

Phase0发布基线7de1d0e81385ae97f98ea673fe05dd726f0b577b；标签对象0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0。main仍502c6931dcfce50bee2f71a80524475fae6396bf。F-001/GOV-010已按原门禁报告CLOSED，原报告与获批内容未改。

用户已经授权Phase1合成数据/通用契约并批准CPython3.13.16，原话见audits/phase-1/AUTHORIZATION.json（初始时间点快照不覆盖）。Gemini对380d9f86467db874033a06a9e6487fd3998e205f的计划预审PASS，原件hash109ec7c92a3e5fd5329d1380abbf381a570bf2690d8f1536a478b96da54f2809；已原字节归档，报告勘误与处置单独记录。

14项P1代码已实现：规范标识/Decimal单位/UTC微秒/IANA日历/PIT修订/行动研究视图/历史池及状态/质量/不可变Parquet与DuckDB索引、环境锁/CI/扫描及测试。实际映射和资料见audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md。102项本地测试通过，门槛未放宽；真实双平台CI及失败历史以implementation/EVIDENCE_INDEX.json为准。旧计划SELF_CHECK/MANIFEST/COMMAND_LOG不作为业务测试证据。

已安装3.13.16标准GIL/x64，完整传递哈希锁和新venv验证；本地构建/venv/缓存/数据产物位于非同步路径。原Baidu工作区Git索引锁反复失败，删除被自动审批拒绝后，使用LOCALAPPDATA/AQRP/checkouts下独立克隆并校验全部复制文件，后续提交从该副本完成。原工作区未reset、未强推、未删除锁，可能保留旧HEAD和已暂存实现；不把它当最新已审版本，准确位置见CHECKOUT_TRANSFER.json。

规范目录106条/16组、canonical CSV hash20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1及P0核心契约保持原字节。F-P1-PRE-001/002/003及F-002/F-003有实现证据，正式关闭待Gemini核对。无真实市场可得性证明、无真实供应商/账户/订单。因子、研究、组合、风险、回测、UI/对应CLI仍Planned，高级扩展Deferred、真实执行Unsupported。

停止点：提交固定SHA实现复核资料，等待Gemini独立代码审查/修复复核及用户Phase1验收。本次不执行发布或下一阶段。

## 2026-10-21：Gemini实现报告接收与核对

已原字节归档Gemini对固定74bdb9216c585d27de91123605aff0266ca028cc的实现报告，SHA-256为54b1fde673a809e3af0f99e2148355813423d1348c0071cff2e38e8f42d035e7。原文PASS及“建议用户验收”如实登记；F-002/F-003/F-P1-PRE-001按审查方意见RESOLVED/CLOSED。F-P1-PRE-002/003没有明确关闭结论，不推定关闭。

开发方核实到8项勘误/范围澄清，详见audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md及IMPLEMENTATION_AUDIT_ERRATA.json：拆股名义量应1000而非500；数个实现/测试文件不存在；tests/golden仅夹具，pytest收集0项、exit5，不能当SDK独立运行证据。固定提交开发方另重跑102项测试和独立参考均通过，实际输出/命令保留；不冒充Gemini沙箱复现。Run#8为有效push运行39476816120，PR#9为39476825340，两者双平台均成功，不误判#8为无效。

当前没有据本报告确认的新业务代码缺陷需要改动；原金融公式、Golden答案/容差、源代码和测试保持原字节。本次只更新归档、勘误及审查/状态记录；报告PASS适用范围与执行证据仍须Gemini确认。远端完整artifact本地下载和跨OS结果hash直接比较的NOT VERIFIED不因报告未提及而消除。

状态不是ACCEPTED或RELEASED。待审查方确认数学/路径/执行证据勘误并明确剩余证据范围后，再判断正常人工验收材料是否齐备；用户验收、main合并/标签及Phase2启动仍各自另行授权。本次不合并、不打标签、不进入Phase2。
