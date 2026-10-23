# 数值呈现与同核比较口径

全部收益/IC/ICIR/检验/组合/资金/成本/绩效仍由既有内核产生，本阶段不定义新的金融经济或统计口径。沿用P3已审推断/OOS、P4约束、P5-D01–D10/C-P5-001等。UI不得重新拟合、从展示数值重算权重/账本、按显著性过滤掉失败实验，或将null填0。

输入：权重/金额/价格/数量以schema规定精确字符串或整数传递。百分数字段仅在共享请求builder按十进制精确除100（12.50%→0.125），不使用二进制float，不自动把不合格总权重归一化。有效配置包含defaults revision与实际展开的值、精确Ref、数据/sidecar hash、seed和既有经济profile；UI隐藏默认值同样冻结。canonical JSON使用与核心一致的UTF-8/sorted keys/无NaN规则；原始对象不同键序等价，数组顺序及字符串精度契约不得任意忽略。

原始输出不经展示舍入回写。资金/数量字符串及big-int在表格、tooltip和原JSON下载保持精确；展示金额可用Decimal HALF_EVEN到2位，百分比可到4位，标明只影响视图。图表只取已验证原始series，不另算回撤或收益。JS浮点不能安全表示的超大/极小/非有限点必须给精度警告和精确表/下载；不把舍入图点/缺失值冒充原数值或再次作为订单输入。渲染数据须保留每个点对应的原始索引和值。

比较三入口时，输入canonical config_hash应完全相同。金融精确字段（含P5 rational/decimal字符串、数量、现金桶、订单/Fill/费用/风险、方向/状态/known标志）完全相等；研究float沿用P3已有数值容差，默认abs<=1e-12、rel<=1e-10且不得放宽既有更严Golden标准。null只等于null，0/false/空串不是null，NaN/Infinity不能进入canonical。图表payload中的精确source值与原表一一相等，渲染像素不是数值真值。

允许差异必须预先枚举：各次生成run_id/task_id、recorded_at/墙钟、工作目录绝对定位以及由这些字段必然引出的非金融事件/manifest hash链；这些字段在各自链内仍必须独立验证，不可通配忽略所有hash、lineage或error。快照ID、数据/sidecar内容hash、真实父run映射的语义绑定、FactorRef、config_hash、状态、原因、预测可用时间、源code/bundle/lock必须一致或在不同run映射表中逐项证明；不得把合法但错误UUID当可忽略元数据。比较器在生产函数之外独立读取原工件做声明投影，不比较生产函数自身生成的预期值。

Golden候选只验证呈现/请求/任务契约，不是P6产品测试。独立主审应扩展未知财务状态、边界大整数、同key竞争、伪造来源、缺清单项及相同错误输入三入口一致拒绝等反例。
