# 数学、合成经济与数值比较口径

P7不改变P3统计/拟合/OOS/HAC、P4整手目标及delta/风险、P5-D01–D10/C-P5-001事件总序/原子事务/资金桶/FIFO/费用口径，也不重写P6精确转换。全部复用已批准实现及独立正确答案；输入、适用条件和例外必须在各个Golden中明确。新适配只做单位恒等映射和规则声明，不暗中进行货币、税、交易日历或可用时间转换。

完整替换差异白名单预先固定：candidates中精确Momentum/Reversal Ref、候选hypothesis与factor_id、因子权重字典的对应键，以及由这些字段导致的params/ref/config/request hash和真实下游信号/订单/结果。两者的weights_percent=100、direction=+1、lookback=2、horizon=[1]、PIT快照/股票池、处理链、split/fit/评估截止、seed、组合/风险/费用/执行/初始账户不变。共同campaign在任何actor前预登记两变体且共享预算；不能变更方向/中性化/期限来追求“看起来不同”的订单。Ref/hash与实际制品必须核实，不用字符串factor_id替代精确Ref。

建议冻结两层完整替换协议：主层启用既有全部真实P3处理，走原中性化及统计/OOS，期望由不导入AQRP的独立参考和主审核对；透明层neutralize=false并保留SKIPPED血缘，清洗/zscore/IC/分层/OOS等仍真实执行，用于逐步手算信号和订单。透明层不取代主层。两层预登记后分别记录，不因运行结果修改口径；两个配置属于两项试验，不冒充独立的同一试验。

主层候选固定P6 24日/6证券全部19个决策（2024-01-04–2024-01-22）、horizon1、原split/fit/embargo和全部中性化流程。MAIN_REFERENCE_METHOD.md保存不导入AQRP的80位Decimal独立算法，MAIN_PIPELINE_CANDIDATES.json保存19截面的原始/清洗/标准化/OLS残差、next-open标签、IC/Rank IC及分层字面候选；实际执行记录另列。主层涵盖工程公开数据的train/validation/fixture-test分区，这个公开fixture的test字段**不是私有正式Test访问授权或正式Test执行**。

主层交易输入修订候选为initial_cash1000、**每决策fee_budget50**、沿原已批准LONG_SHORT配置取gross=net=0.5、等权long_k=short_k=1（short预算0），P3保持19研究点，P5按预冻结execution_sessions只执行隔日10点；这是现有允许经济配置与拟新增薄日程映射，不改T+1或放宽风险。原每日执行和fee100失败夹具完整保留。透明单决策层保持LONG_ONLY/top_k1/fee_budget10。每层内部两个因子各自配置完全一致，不能跨层宣称只改因子。

FINANCIAL_FEASIBILITY.md/FINANCIAL_REFERENCE_METHOD.md保存逐桶上下界和纯stdlib模型；两因子各7次换仓的全128顺序、9次最坏换仓全512顺序合计768条模型路径，明确覆盖10个required P4、每笔资金/手续费/预留、期末交收估值。两因子模型最终579现金/979权益、佣金15/滑点6；真实运行仍由后续G2核实，不能以有限模型代替产品验证。主审G1须独立核对全部假设、规则映射与设计参考，不再把简单可行性推导留作未知。

透明层设计候选固定P6 24日/6证券、2024-01-06单决策、SYN_U、lookback2、direction+1、neutralize=false。公开输入规则给i=4价格与i=2价格为[103,124,113,129,145,161]与[121,111,123,135,147,159]，Momentum精确值依次为[-18/121,13/111,-10/123,-2/45,-2/147,2/159]；Reversal逐项取反。5%/95%分位裁剪和zscore均不改变这组严格排序，Momentum top1为SYN_A:002，Reversal top1为SYN_A:001；不能把此排序未经独立OLS复算套用到neutralize=true主层。

该候选的工程执行sidecar明确原始开盘/估值100，lot1，初始现金1000，预留总费用预算10，无行动/外部流/借券，top_k1/long-only/equal，沿用原组合及撮合profile。P4可投预算990，floor(990/100)=9股；BUY滑点后成交价为ceil_tick(100×1.001)=100.10，成交金额900.90。原佣金为round_cent(max(1,900.90/1000))=1.00，滑点成本9×0.10=0.90，成交后现金1000−900.90−1=98.10，按原始估值100的市值900，权益998.10，净收益−1.90/1000=−0.0019。**1.90是费用加滑点的总拖累，不能误记成佣金1.90或把成交价写为100。** 两个因子分别买不同证券但现金/权益相同是正确结果；禁止要求收益一定不同。实际OPEN可用时间必须晚于决策，不能从此算术证明已实际成交或完整E2E通过。

这里的有限算术只属**开发方design candidates**，尚未导入产品/实际运行，不是GPT Work独立答案或P7测试通过。主层和多决策层的全部实际预期必须在实现前以独立参考/原Golden冻结并交GPT Work核对；不得从待测函数生成expected。任何候选与原profile不一致先修订提案/说明影响，不能修改已正确历史答案迁就实现。

数值比较：同一因子同一协议各actor的有效config及精确Ref完全相同；资金/价格/数量/桶/订单方向/状态/风险/known标志/原始十进制及有理数精确比较。研究float沿用原Golden更严阈值，通常abs<=1e-12、rel<=1e-10，null仅等于null、NaN/Infinity拒绝。原始字段不从图表或显示舍入反算。

运行独有UUID、UTC墙钟、绝对工程根仅在每条原始绑定已独立校验之后通过显式一一映射处理；其必然影响的清单/链hash先核原字节再映射比较。不忽略所有hash/错误/lineage，也不掩盖错snapshot、错父run、错时点或缺文件。跨因子比较不要求config_hash相同，要求唯一允许配置差异满足上述白名单，且其余经济字段逐项完全相同。

P6数字词法/4096位/4098字符及整数HALF_EVEN适配保持；旧P1–P5API量程与financial domain校验不放宽。现金桶对账同时核cash_set、U_free、U_short、S_set、short_value/已交收所得、冻结费用/名义/应付和实际available，正常、异常、取消/重放都从真实提交prefix重建，不能仅总现金相等。
