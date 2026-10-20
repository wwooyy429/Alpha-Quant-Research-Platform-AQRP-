# Phase1独立答案候选、边界与性质清单

状态：**REVIEW REQUIRED，开发方手工参考，不是已独立签署/已运行的测试结果**。所有输入及答案应在Gemini预审核对后以版本化fixture封存；实现不得调用自身生成期望值。这里使用小型合成记录，不需要真实数据许可。

## 已知答案候选

| case_id / 需求 | 固定输入与独立计算依据 | 明确预期 / 容差 |
|---|---|---|
| P1-ID / DATA-001 | 两证券SYN_A:001与SYN_B:001，symbol同为DUP，分别价100和200 | 以security_id/market精确隔离，各1行；精确 |
| P1-ALIAS / DATA-001/002 | 某ID从OLD换为NEW，生效Jan3 00:00Z；新别名修订available Jan3 01:00Z | Jan3 00:30不可预知NEW，按当时可见版本处理；01:00可见NEW；不创建另一个证券ID |
| P1-PIT / DATA-002 | 同日bar event Jan2 16:00Z；rev1 available16:05Z close100；rev2 availableJan3 10:00Z close101 | Jan2 16:04:59.999999无行；16:05有100；Jan3 09:59:59.999999为100；10:00为101；精确 |
| P1-UNKNOWN / DATA-002 | event已知但available_at未知，ingested_at在后来，快照标EXPLORATORY_ONLY | 正式query拒绝，不能用抓取时间伪造历史可用性 |
| P1-TIME / DATA-002/003 | timestamp输入2024-01-02、naive 2024-01-02T16:00:00 | 两者均拒绝作为event/available/as_of；合法session_date=2024-01-02仍接受 |
| P1-MICRO / DATA-002 | 可用时点16:05:00.000001Z，cutoff16:05:00.000000Z及.000001Z | 前者不可见，后者可见；1微秒精确。输入非零纳秒尾数拒绝 |
| P1-DST / DATA-003 | 合成NY日历：2024-03-08 09:30−05:00，03-11 09:30−04:00 | UTC分别14:30与13:30；仅测试IANA转换，非真实市场日历认证 |
| P1-LOCALDATE / DATA-003 | 合成Asia/Shanghai session结束2024-04-02 00:30+08:00 | UTC=2024-04-01 16:30Z，本地session_date仍04-02；精确 |
| P1-SESSION / DATA-003 | 显式session表仅Jan2/Jan3，Jan3半日close12:00Z，Jan4为假日 | Jan4 bar拒绝，Jan3 event必须为12:00Z；不自动补齐Jan4 |
| P1-SPLIT / DATA-004 | 可见并生效2:1拆股，前RAW close100/volume10，后close50/volume20 | RAW不变；拆股研究视图前50/20、后50/20；总回报0；Decimal精确 |
| P1-FUTUREACTION / DATA-004 | 上述拆股在旧cutoff后才可用或生效 | 旧cutoff的价格仍100、量10，不因未来行动改成50/20 |
| P1-DIV / DATA-004 | 前close100，ex-session close98，现金分红每旧股2，s=1 | RAW价收益98/100−1=−.02；毛总回报(98+2)/100−1=0，不再叠加2；abs1e-12 |
| P1-UNIVERSE / DATA-005 | U含A/B；B退市生效Jan4 00:00Z，退出修订availableJan3 18:00Z | Jan3 17:00仍A/B；Jan4 00:00只A，security_master及历史数据仍保留B；区间半开 |
| P1-LATESTATUS / DATA-005 | B停牌生效Jan3 00:00Z，状态修订availableJan3 10:00Z | 09:59查询不读取后来才知道的状态；10:00起返回可见停牌，不靠缺bar推断 |
| P1-QUALITY / DATA-006 | 6输入行：2有效(其中1零量)、1与首行完全相同重复、1合法null观测、1负价、1 high<close | valid2、duplicate1、missing1、rejected2，合计6；零量不被标缺失，null不变0；非法行使严格发布失败 |
| P1-DUPCONFLICT / DATA-006 | 同物理键、相同可用时点，close100与101两行 | 冲突隔离并阻断发布，不按先后顺序选101 |
| P1-UNIT / DATA-011 | 源成交量3手、每手100股，源amount1.25千测试币 | 300 share、1250.00测试币；保留原始单位，Decimal精确 |
| P1-DECIMAL / DATA-011 | 源文本0.10及0.20；另有超出profile可承载scale或混币输入 | .10+.20=.30精确；溢出/不支持币种显式拒绝，不先转float再修补 |
| P1-ROUNDTRIP / DATA-008 | timestamp_us、Decimal128、date、null的小表写入Parquet，经Arrow/DuckDB读出 | 类型、值、精度、null、排序与固定源行一致；整数/Decimal/us/date精确 |
| P1-HASH / DATA-007 | 已封存分片改1字节、manifest路径../outside、已有snapshot重复发布 | 分别拒绝篡改、越界与覆盖；不能自动重新算hash掩盖损坏 |
| P1-RET / QA-002，G-RET | 无行动、RAW close100→110；110/100−1 | 0.10，abs1e-12/rel1e-10；分母0或负值拒绝，缺值返回明确缺失 |

上述日期均为合成示例；实际fixture将完整填齐schema必需字段，表中的简写不作为不完整输入的免检理由。最小golden行必须记录profile/schema、单位、完整UTC时间、所有revision和source lineage、答案公式/中间量、核对者/版本与输入/答案hash。

## 边界、性质及独立参考要求

- 时间：cutoff前1us/等于/后1us、跨UTC日期、无时区/非法时区、DST重复/不存在本地时刻、微秒溢出；入口JSON/Arrow/Pandas/DuckDB路径一致。
- PIT：随机打乱源行、分片和证券顺序不改变排序后的可见投影；同一输入重复查询幂等；未知可用性及晚到修订不读取未来。显式参考实现从小表逐行筛可见修订，不调用待测query/排序/helper。
- future mutation：另建未来价格/晚到修订/成员/行动的新快照，固定cutoff的值投影及投影hash一致；修改cutoff前已可见合法close应改变结果，作为非恒定正向控制。完整snapshot_id可变化，不将其误判成泄漏。
- 单位：精确转换及可逆条件、scale/precision边界、超大金额、零/负量拒绝、混币拒绝。独立Decimal或有理数参考不得共享业务转换函数。
- 行动：RAW不随研究视图修改；拆股price×share在单位转换上守恒；现金分红只计一次；future/unknown行动不会回填；这只是研究数据处理，不是P5账本守恒测试通过。
- 质量：互斥行分类计数守恒，完全重复幂等，冲突/非法输入发布失败；无跨证券填充，无null→0。
- 快照：发布同一内容的幂等/冲突规则明确，更正用新版本；无路径逃逸；checksum不匹配必失败；索引重建与缓存失效不改变正确可见数据。
- 安全：固定版本秘密扫描器正例/负例，正例仅使用测试中临时生成的公开假凭证模式，不提交真实或可用凭证；脱敏测试不得把原敏感值写入原始日志。合成源与测试不访问真实账户或供应商。
- 环境：实际检查sys.version_info=(3,13,16)、锁文件完整及哈希安装；Windows/Linux分别保存日志/镜像身份；不将能下载wheel视为安装已通过。

预审时请Gemini独立核对上述数值、时区及错误语义并给出通过/修订意见。后续实现阶段由pytest/Hypothesis执行已签署fixture及独立reference；目前没有业务测试通过记录。
