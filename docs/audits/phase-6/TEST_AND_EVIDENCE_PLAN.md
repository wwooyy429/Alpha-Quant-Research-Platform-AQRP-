# 实现后的测试与原始证据计划

G1当前无UI业务实现/安装/浏览器通过记录。已有1158只验证P5，不增加P6产品通过数。实施后必须同时完成以下层次，必要自测由Codex执行，独立固定SHA G2以GPT Work为主；不能以开发方或子代理冒充独立审查。

| 测试组 | 实际对象与独立期望 | 关键负例 |
|---|---|---|
| T6-DASH/FACTOR/CONFIG/SETTINGS | 真实目录、6页面交互、配置revision、精确Ref/权重与原始状态；literal夹具/独立JSON对照 | rerun重复提交、回滚改旧文件、撤销或伪造Ref、坏manifest计成功 |
| T6-RESEARCH/BT | 真实P1→P3→P4→P5服务与原始artifact绑定，IC/分层/OOS/风险/资金/订单/Fill/绩效展示 | 同一合法UUID错血缘、后补清单文件、无知财务状态旧余额回退、未来输入 |
| T6-PARITY/REPLACE | 同一canonical请求走原CLI/新任务CLI/SDK/实际Streamlit事件，Momentum→Reversal仅改Ref各跑完整链，独立投影/原金融答案 | 只对比截图、过宽忽略hash/lineage/null、改变core后假称同核 |
| T6-TASK/IDEMP/CRASH | 实际并发进程/持久化索引/原核心账本，10并发同key、崩溃前后、取消与成功竞态 | 同key异hash、提交后异常旧余额、预分配run映射丢失自动重复执行、伪终态、分task目录重置研究家族预算 |
| T6-ARTIFACT/REPLAY/SAFE | 真manifest/hash/目录边界、原始下载、历史声明重放、日志安全、无任意代码和私有路径 | path traversal/reparse/symlink逃逸、清单删项/目录枚举报错、HTML注入/敏感字段泄漏 |
| T6-FORMAL | 所有入口formal/FINAL_TEST安全拒绝，真实私有入口不调用 | 前端改布尔或候选Ref后仍执行、默默转工程模式 |

正确性须已知答案+边界+性质+独立参考。GOLDEN_CANDIDATES为预先指定设计答案；不得从待测UI/service函数生成期望。运行scope为工程数据，保留全部失败、取消、unknown和恢复证据，既有P1–P5 Golden及G2反例全部回归。

覆盖率：金融及关键安全/任务持久化路径保持既定核心行95%/分支90%或更严格现行门槛；一般服务行90%/分支85%；纯UI/CLI薄适配行80%/分支70%，关键流程必须100%有用例。不能把复杂状态/金融逻辑移到UI以套低门槛。门槛适配需明确文件分类和新固定SHA审查，不能直接降低现有模块要求。

完整SDK：新干净venv、Python3.13.16、core/扩展依赖哈希安装、wheel构建安装、lint/format/覆盖、全部旧回归/原20+4/数学91、P1八表/九文件及旧Ref重放、P3/P4/P5完整服务、P6六页面/AppTest/任务故障/三入口数值。双OS CI各跑同版本，保存run/attempt/job、完整退出码/通过失败跳过、原始ZIP/API digest/长度/CRC/精确成员清单、source/wheel/环境/数据/终态链；上传器复制的pytest current目录需全子树字节对账，不冒称原symlink或ACL身份。

AppTest用于页面状态和组件断言，真实浏览器另留本地工程启动的argv/地址绑定/进程身份/交互与截图、六页面/两因子/取消/失败/下载链日志。不得把AppTest或mock结果宣称真实浏览器验证；没有真实浏览器证据则该项NOT VERIFIED，阻断所需UI验收。任何未来本地工程启动都需先有实施授权，不涉及外网发布/管理员操作，本轮不启动。

每次run唯一UUID、不可变有效配置、代码40SHA/dirty、core bundle/两套锁/实际distribution+RECORD/interpreter/OS、数据manifest/sidecar、输入/输出工件、开始结束UTC、原始命令/stdout/stderr/报告/hash。固定G2版本用PR AQRP_FIXED_REVIEW_SHA，HEAD漂移单列，不继承旧PASS。保留扫描正/负控及所有原失败记录；真实Windows R2延期不因这些测试关闭。
