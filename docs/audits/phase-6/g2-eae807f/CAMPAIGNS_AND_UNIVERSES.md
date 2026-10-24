# 受限工程使用方式及边界

三个可信合成池：SYN_U（SYN_A六股）、SYN_CORE4（001–004）、SYN_TAIL4（003–006）。原P1合成跨市场条目和历史成员有效区间/可用时间不删改；P3按市场及每次决策的P1历史成员筛选，P5输入按每个行情时点查询同一成员契约。目录的快照、成员表及各池历史哈希随请求冻结。此处无真实源、上传路径或自由Python执行入口。

SDK先调用`TaskService.register_campaign("study", [draft1, draft2])`，冻结完整候选变体和多重检验集合；随后在请求中指定`campaign_id="study"`与`universe_id`。CLI使用`aqrp-tasks campaign-register --workspace <root> --campaign study --request variants.json`，其中文件为候选draft的JSON列表；`campaigns`只读列举。网页Experiment Manager提供同一注册表单，研究和回测表单都能选择已登记计划与股票池。

未显式选择计划时，首次freeze只建立一次`engineering-default`：冻结当时的lookback、方向、预处理、决策区间；声明当前因子组合与四个单因子、首次预测期限/[1]/[1,2]及三个可信池的有限笛卡尔积（去重）。其完整definitions与候选集合可读且不可事后扩充。之后编辑未登记的参数会明确拒绝，需要预先列出新计划；不能自动按新配置hash领新family。正式研究应使用显式登记；默认first-use只是工程便利，不能据此声称正式预注册或正式Test。

每个工程workspace的相同数据身份共享固定12个candidate×horizon预算单位。Task提交时原子预留，失败/取消保留且不退，幂等重试复用原记录。多预测期限和多因子按实际假设数量计数。新计划不能重置预算；注册记录冻结此前试验/Task访问历史，跨计划访问在后续统计中标为污染。未执行的已声明假设保留在Holm分母中。显式改名、失败或取消均不能制造新的干净配额。原P3已执行trial继续保存且与拥有它的Task预留不重复计数；拒绝于Task边界的尝试保留原请求及拒绝记录，不伪造已执行P3 trial。

预算/完整性边界是工程workspace及同数据身份；这不是跨机器、防人为删除整个工作区、真实OS隔离或金融批准。dev2目录与原审查运行只读保留，不迁移、重新归类或覆盖其失败证据；dev3新目录用catalog/2。测试创建不同故障工作区时须披露它们是工程反例控制，不能以此主张研究样本独立。

取消不是财务证书：每个已启动P5或重放必须重新核验实际事务目录、初始锚、完整提交链、物理成员及完整金融projection；任一未知/损坏都以FAILED / COMMITTED_STATE_UNVERIFIED收尾，并保留取消意图和原始子运行。已成功取消后再损坏仅在公开读取时呈现INTEGRITY_ERROR，不改写原终态。正式入口仍失败关闭，Windows R2两项DEFERRED / NOT VERIFIED。
