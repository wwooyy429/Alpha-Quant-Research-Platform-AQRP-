# Gemini：Phase 2 集成已发布 0.1.1 修复后的固定版本复核

仓库：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-
PR：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/3

请先取得并记录PR描述中完整的 `AQRP_FIXED_REVIEW_SHA`；只审该固定提交，禁止改为漂移HEAD。如无法访问该提交，明确NOT VERIFIED并停止依赖该事实的裁定。执行资料业务提交为566f0ece4175fddb2703daab3b5b26ff0e4e245f，合并父947467b9d094905cab0af37ec5cc53f1d187e755、已发布main fb1ba4fd51202a303115e4449ee49db09ccc071c；最终资料提交须核对相对业务提交仅为审查证据/状态，src/tests/tools/CI/构建/锁相同。

本轮仅复核用户授权的P1补丁集成及P2注册/替换/API兼容。不要合并main、打标签、改审计原文、给出用户验收结论或进入Phase3；不要接真实账户/订单。需要外部执行或角色替代时明确范围和授权，不把此前P1指定代执行视为P2豁免。

1. 核对main的P1修复已保留历史集成，三处core/time.py、data/pit.py、data/quality.py与发布版逐字节相同，P2候选仍0.2.0，依赖锁和正确Golden未改。检查冲突处理未删除因子逻辑/回归或恢复已知缺陷；main与历史标签未移动。
2. 核对共享代码审查证据CODE_REVIEW_EVIDENCE.json及active ../CODE_REVIEW.md、../CODE_BUNDLE.json、src/aqrp/factors/reviewed_code.json。旧bundle cfabe293…更新为完整fc1b50110c02efbe4a53168c43d7fe4972e5ebab3edc3091aeaf58ac72a11fc7；不能只改hash，须复核实际源码/host调用边界。旧FactorRef不可静默升级。工程TEST_ONLY准入不等于金融批准、OS沙箱或Gemini独立批准。
3. 核对新完整wheel SDK、原始外置16项及新6项集成回归。每套392=旧254+P1修复132+本轮6；需求DATA-002、FACTOR-012、SEC-001的host时间精度/探索快照/共享代码漂移均须在compute前拒绝。数学公式、证券B、Volume历史均量和既有容差复核遵循独立答案，不用实现生成期望。
4. 核对CI run39631435026/attempt1两份原始ZIP：Windows12359171840，148498bytes，SHA256 a1320050f675f4522befd72ed774a57a5c8d8687bf7b46141c8e0ee7f62883fc；Ubuntu12359990804，148221bytes，SHA256 4ef8ba12586f6582d333f5c4bbb4b0a6d53458109b95bd287abe04787b1227e8。核对官方digest/大小、CRC/安全路径、完整清单、各46选择文件hash、原wheel和.coverage、两组各8表/查询及3个factor-run manifest。CI临时merge父main+业务566f0ec、tree与业务相同；不得以旧8183版ZIP证明当前版本。
5. 独立执行能力允许时，按CPython3.13.16标准GIL/x64运行tools/ci.py并提供原始命令、退出码、环境与日志、固定代码/数据/配置hash。仅阅读证据标Evidence Reviewed Only；未运行SDK明确NOT VERIFIED，不把开发方结果补记为Gemini执行。开发方在Windows回放Ubuntu产物不等于新Linux本地安装。
6. 核对CHECKER_CORRECTION.json、verify-first.py与首次失败日志：查询hash含存储root，原检查误以为迁移路径后hash不变；现以记录原root重算原查询hash，并独立回放数据/result hash。核对这只是校验方法修正，未改产品或金融答案，失败记录保留。
7. 对照../MATH_INCREMENTAL_RECONCILIATION.md及本目录REPORT_FACTS_AND_OPEN_GATES.md逐项确认旧十二项报告勘误和两项Low。特别核对PR真实标题/Phase0 BASELINE未改、FACTOR-011为P2替换/API兼容、Volatility为FACTOR-008 POST7 Deferred、真实源码core/security/__init__.py和factors/contracts.py、TEST_ONLY为用途而非state、available_at为合成decision_time，以及尚无原件的综合AST/math/hash工具。不要把报告写AGREE自动当事实已对齐。

输出固定完整SHA、审查范围/证据等级、新旧发现逐项处理（CLOSED/OPEN/NOT VERIFIED及依据）、实际执行清单、仍需补齐条件和最终建议。用户人工验收、合并发布和下一阶段授权分别保留；任何PASS只属于实际审查范围。

资料入口：本目录README.md、AUTHORIZATION.json、INTEGRATION_TOPOLOGY.json、CODE_REVIEW_EVIDENCE.json、EVIDENCE_INDEX.json、LOCAL_VERIFICATION.json、ci/*-verification.json、ci/*zip、sdk/、original16.*、FILE_MANIFEST.json；旧Gemini原件在../gemini/。
