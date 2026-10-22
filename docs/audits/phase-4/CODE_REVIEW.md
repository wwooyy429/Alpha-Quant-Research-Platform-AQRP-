# P4开发方代码准入审查（TEST_ONLY，非GPT Work G2）

授权IMPLEMENTATION_AUTHORIZATION.json；G1固定265af16353d85ce8c2d229a7517809d707498da8。新增源码仅portfolio和risk，既有43模块保持原字节，__init__仅更新包版本0.4.0，admission仅将默认因子版本1.1.0递增为1.2.0以区分新完整bundle；旧精确Ref由旧wheel和原工件保留，不覆盖旧注册内容或改变因子公式。原P0–P3文档/失败/Golden/审计及依赖锁保持。每次源码修改或格式化后均重新核全量Python bundle，更新工程receipt；不沿用旧P3 bundle批准新代码，也不授金融批准。

- contracts：严格字段/类型及每层哈希、输入集合、共同PIT时点、signal session age、父快照/币种/市场、完整账户对账和显式风险配置。金额/数量必须有限十进制字符串；独立分数可有限float投影。拒绝系数超过34位或绝对十进制指数超过100的输入，避免精度/资源歧义；结果统一34位ROUND_HALF_EVEN，核心计算用精确Fraction，不受调用方Decimal context影响。冻结输入仅声明合成工程fixture，不是外部数据真实性证明。
- weights：共同有效交集、固定预注册因子系数、稳定排序、真实多空双腿及gross/net预算；不做P3再次拟合或最终Test选择；无效交集/非零预算空腿和重叠都明确处理，不默改K/风险阈值。
- construct：只产生UnvalidatedCandidate，绝对目标向零取整；只有理想数量精确等于原仓才不动，不因失败自动保留或拆单。候选与请求原字节绑定。
- risk：公开check_target重新构造候选并核请求哈希，不能相信caller passed；固定容差只用于对应风险/现金，lot/借券/数量精确。所有连续与取整后约束、目标及delta双lot、全平例外、可交易/可售/总借券/资金均逐项诊断；拒绝不能得成功target。
- service：先工程receipt验证，再唯一run_id/不可变请求配置/环境hash写实验ledger。成功/拒绝/非法输入/内部异常均保存终态证据；目标和建议明确不可执行，不写交易账本，不生成OrderEvent。公开正式入口依据实际package policy金融批准NONE拒绝APPROVAL_REQUIRED，不回退工程路径、不接受caller批准字符串。真正隔离与正式Test未部署。
- replay：读取已验证终态manifest中唯一result，验证同次原始字节；仅声明原结果完整性核验，不把它冒充新宿主或正式金融复现。
- research_input：只读取P3成功终态、唯一清单成员及同次字节，固定原run/工件/manifest hash、原证券/市场/币种/父数据、精确Ref/参数/stage/决策时点，重构分数投影。原P3日历ID留在绑定中，P4工程profile显式投影至UTC日的SYNTHETIC_V1当前session（max_age=0）；signal_time必须匹配事件时刻及该UTC日，不能仅伪造session_index冒充新分数。声明账户及市场风险夹具仍标SYNTHETIC，不冒充真实PIT源或金融批准。来源目录必须已存在，不创建来源记录，不运行因子代码。

现有registry只调用包内已审builtin；新portfolio/risk不导入任意因子或网络，无eval/exec、网页代码、真实凭据或交易API。receipt是包内工程准入记录，不是密码学签名或恶意Python沙箱。源文件变更后必须重新审完整bundle。完整代码hash及保留文件见IMPLEMENTATION_IDENTITY.json；最终自测与独立主审结论分别记录，不用本审查冒充G2。
