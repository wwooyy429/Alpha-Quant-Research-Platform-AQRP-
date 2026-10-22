# Phase4实际实现与边界

用户已授权按G1固定265af16的7项受限工程设计实现。代码版本0.4.0待G2；新包不是发布，旧main/标签不动，P4未用户验收、未合并或部署。

`PortfolioRequest.create(mapping)`冻结canonical字节，或直接传原始bytes以保留非法输入失败。`construct_engineering(request, ledger_root, code_commit)`是完整同步服务；ledger_root仅实验输出，不是交易账户账本。返回PortfolioResult原字节、独立副本read；成功有工程目标与不可执行调仓建议，拒绝无target。`build_candidate`只是未验证中间物；`check_target(candidate,request)`逐字节重构并执行完整pre/post。正式construct_approved按实际金融policy NONE返回APPROVAL_REQUIRED，没有skip或工程降级。

输入模式DECLARED_FIXTURE是显式合成声明与可验证内容hash，不是外部数据真实性/审批签名。RESEARCH_ARTIFACT另绑定实际P3成功终态manifest与单次stage原字节；bind_research将已预注册因子键投影到声明证券集/共同决策时刻，保留精确原Ref、参数及源日历，其他市场/账户夹具仍单独标明工程来源。随后prepare再次核原工件与投影，不接受后补/替换/改分后重新算envelope hash冒充原研究结果。不得将任何工程来源提升金融批准。

SYNTHETIC_PORTFOLIO_1当前唯一日历为SYNTHETIC_V1：当前session_index对应决策所在UTC日，信号与事件时刻一致并须落在当前UTC日；max_age=0，不隐式支持真实市场时区/过夜session。缺/错映射拒绝。真实市场profile、数据接入和经济规则另定；不是假装完成真实市场支持。

计算内部用精确Fraction，输入遵守34位有限Decimal及指数边界，输出独立34位ROUND_HALF_EVEN。数量/lot/借券整除无容差；风险比率1e-12、资金1e-8按原设计。非selected原仓仍进目标0/清仓建议；停牌有调仓拒绝。局部风险assess对delta0允许停牌原仓持有并照查全部敞口；组合构建不在选择失败后自动保留或冻结该仓，也不偷偷重新分配预算。完整风险和资金前后均检查，不能因取整减少gross而略过Beta/净/换手。

完整6组输入和预存答案在tests/portfolio/fixtures，先于产品实现冻结FROZEN_INPUTS.json。原G01–G20/R01–R17及所有独立报告不改。新增测试覆盖真实公开服务、原G1反例、部分/不动/全平/跨0、严格输入与PIT、各项风险、三资产/多因子、性质、不可变证据与旧P3工件输入，不创建订单或P5集成。旧578回归与新测试计数以实际SDK/JUnit为准，不预写通过数。

开发早期记录：首次格式/静态检查发现E701/E702，格式化后通过；新增研究输入测试曾有unused变量与编辑位置错误，静态检查发现并修正。初次完整新测试test2为194过/1失败：用例net_min1.1仍配net_max1导致正确返回CONFLICTING_LIMITS；修复该测试的上界为2以真正测试合法区间下限，不改独立数学expected或实现来迎合。失败test2.log/xml及后续日志保留；早期静态诊断只保存在会话工具输出，无单独完整原日志文件，不补造。正式SDK/CI均从干净已提交归档构建，原命令/退出/失败/工件完整保存。

新增代码由开发方完整工程准入审查并重算bundle/receipt，不能声称GPT Work已G2通过。保留真实隔离、正式Test、金融批准和完整旧宿主NOT VERIFIED；本阶段目标仅工程组合/风险。旧wheel/锁/原Ref/结果及现有重放证据保持，不宣称新完整宿主重建。
