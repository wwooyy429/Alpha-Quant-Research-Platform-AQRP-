# P7 工程集成使用与证据说明

仅使用已授权合成工程数据。金融批准NONE；真实Windows隔离WI-R2-001/002为DEFERRED / NOT VERIFIED；正式Test未运行且入口失败关闭；未知真实赛事/数据源需后续另行确定。本次没有部署、账户、ACL、服务或调度操作。

环境固定Python3.13.16、requirements.lock及对应OS的UI锁。完整验证从干净固定Git提交运行 `python tools/ci.py`，所有工件写到AQRP_RUN_ROOT外部新UUID目录；安装新wheel并检查完整RECORD，原P6 checker在原P6源码/wheel隔离环境执行。保留全部失败日志，不以重跑覆盖。

日常薄入口仍是aqrp-ui六页面、aqrp-tasks和原研究/回测CLI，均调用同一应用服务。engineering_pipeline可显式填写执行会话列表，留空保留全部研究会话；不能按结果临时挑选日期。网页显示可信股票池、原始配置及解析后的研究/执行来源。正式研究与交易许可不会因为工程Task成功而产生。

通用离线适配流程：先由adapter-spec/input-reference读取实际P1与规则身份；capabilities提交完整显式规则，缺失/未知外部条件被拒绝；adapter-freeze生成不可变receipt，再经adapter-submit调用原TaskService，result校验原核心终态。请以 `python -m aqrp.services.task_cli --help` 的实际命令参数为准，SDK对应competition.adapter模块；适配receipt不能授予金融批准。

集成协议由已冻结源码哈希的受信e2e_smoke运行器控制actor顺序。SDK、TaskCLI、AppTest和legacy共10单位完成后，状态必须仍为BROWSER_EVIDENCE_PENDING；真实浏览器在同一已冻结输入/代码/计划上完成剩余两次全链，另执行事前登记的风险夹具和主根零研究取消/重放。UI没有激活槽位的输入项，旧会话需按可信激活重新加载。CLI组件测试或截图本身不算完整浏览器证据，必须与真实Task、R/P4/B、终态清单和下载字节相互绑定。

最终交给GPT Work的是PR #10唯一AQRP_FIXED_REVIEW_SHA锁定的完整40位实现提交及实际证据索引。SDK命令complete只说明该SDK选集完成；整体真实浏览器/E2E由独立字段记录。开发方自查、CI、独立G2、用户验收和发布是不同状态。

通用适配CLI的具体顺序（W是已初始化的合成工程工作区，draft.json为原Task草案，rules.json为逐项审定的完整合成规则，输出文件必须尚不存在）：

```text
python -m aqrp.services.task_cli adapter-spec --workspace W --output spec.json
python -m aqrp.services.task_cli adapter-capabilities --workspace W --rules rules.json --output capabilities.json
python -m aqrp.services.task_cli adapter-freeze --workspace W --request draft.json --rules rules.json --output receipt.json
python -m aqrp.services.task_cli adapter-submit --workspace W --request receipt.json --rules rules.json --key unique-engineering-key --wait --output task-result.json
python -m aqrp.services.task_cli status --workspace W --task TASK_UUID
python -m aqrp.services.task_cli artifact --workspace W --task TASK_UUID --slot B --name result.json --output original-result.json
```

adapter-submit接受原冻结receipt并重新核验原始字节、当时defaults revision与原规则；后来的默认配置修改不会重写它。对冻结receipt使用execution-sessions覆盖明确拒绝。草案便利提交仍通过同一freeze/execute服务，不能绕过共同预算或可信actor计划。规则文件只能用于明确的合成工程口径，不能以spec的支持列表冒充尚未收到的真实赛事规则。

设计候选中的p7_engineering_protocol控制面最终实现于tools/e2e_smoke.py；身份冻结和PlanAuthority语义相同，最终逐文件清单明确锁定该名称。该工具的`--developer-fixture`只用于可追溯的开发脚手架诊断，不能生成固定版本完整协议收据或替代干净SDK。正式送审证据必须来自无该参数、dirty=false的固定提交运行。

受已批准BUD-024共同准入契约影响，旧P6的单项历史污染测试由手工追加无归属记录改为完整、合法登记并取消的历史试验，保留原污染、额度及损坏检测断言；后补无归属记录另设负例，要求失败关闭、原字节不变且不消耗新额度。原测试完整字节保留在p6-source-overrides/tests/ui/test_g2_cancel_proof_controls.py，并在原P6源码及wheel环境中另行实际执行；不得以新契约抹去旧结果。冻结的5016文件未因此改变。

旧TaskState原生WAL竞争测试同时验证全部连接关闭和恰好一次成功WAL建库，继续保留实际BUSY、持锁释放、单工作区及sentinel原值断言。P7增加只读遗留authority探测，因此连接总次数不再固定为一；旧完整测试文件同样封存并在原P6环境执行，生产安全探测和原超时策略保持。
