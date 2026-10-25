# P7包准入、CI与原始工件接线设计 · G1候选

关联INT-004/005、ENV-001/002/003、QA-001/002/003/004/006/007及C-P7-004。此刻仅设计；不改R内任何工具/工作流/代码，不把原P6静态校验成功当P7实现证据。

## 已核实的旧守门与不兼容原因

真实 `tools/check_phase6_package.py` 读取P6 IMPLEMENTATION_AUTHORIZATION，固定已审G1 SHA e71和三条件；将P6 IMPLEMENTATION_IDENTITY整份bundle_manifest/current_files/preserved_files与当前包逐字节比较，核106项/8项P6及5MVP/锁文件，并明确禁止src/aqrp/competition与broker。它通过P6身份隐式固定83模块和该版current文件；P7新增competition/服务接线/新bundle或更新当前治理文档后，不能期待这个旧检查器在P7树上继续成功。

真实 `tools/ci.py` 在新venv、锁安装、wheel安装、ruff之后首先调用旧P6包checker，然后执行原重放、全部pytest/覆盖门槛、所有P1–P6参考/smoke、secret scan及上传选择清单。当前选集仅有dataset/factor/research/portfolio/backtest/ui等旧子树，workflow也没有e2e/competition子树；若只写新P7输出不同时改选择器与上传配置，原包会漏证据，即使命令退出0也不能算完整。

**旧checker原字节保留，不能删除其禁止competition检查或把旧83改成任意数量让新包通过。** 它在P6固定发布源码目录、原P6安装wheel和原锁环境中执行，ROOT指向该旧源码，保存旧环境/源码/模块来源/输出。P7树使用新阶段准入，不伪称旧checker证明新包；P6旧业务pytest/正确答案仍在当前P7 SDK完整回归。

## 拟增check_phase7_package.py

新checker先验证模式、可信基线、实际Git源码/安装包/授权和不可变目录，再检查具体差异；不从“存在competition目录”推断已获实现授权。两种明确模式有不同成功含义：

1. **PLAN_DOCUMENTS**：只允许G1资料/审查归档/治理文档及明确列出的文档校验/CI接线文件；src、业务测试、依赖锁及已审金融答案与P6发布基线完全相同，bundle仍为P6已核身份，competition/broker业务目录仍不存在。不要求实施授权，但必须有用户G1计划授权。该模式可用于实际计划PR的文档CI，全部已运行测试数只记P6回归。若本轮实际计划PR不增工具而仍使用旧checker，须明确逐字段解决旧identity/current文档绑定，不能未经说明刷新或覆盖原P6冻结身份；推荐独立新计划包检查而不改旧checker。
2. **IMPLEMENTATION**：必须存在P7独立G1固定40SHA、主审通过记录、阻断设计关闭/用户条件接受及**单独实现授权**；正式Test/金融批准/部署/真实ACL许可仍为否。验证P7 5项/3MVP/2CR及106总目录完全匹配原快照，并核原G1设计身份、全部独立正确答案及参考原字节。

实现模式的具体身份文件提案：P7 BASELINE_INPUTS记录实际P6发布SHA/tree/tag及其文件大小/hash；P7 DESIGN_IDENTITY记录经G1通过的设计/答案/范围hash；P7 IMPLEMENTATION_IDENTITY记录新bundle清单/包版本、旧不变集合、逐文件允许变化与新增文件集合（全部精确路径）及各文件实际大小/hash，自身排除以防循环。固定实现SHA由Git/PR锁及外部seal证明，不能自嵌无法闭合的commit值。

检查规则：

- **旧5016保护文件**、P6全部正确Golden/独立参考/审计原文/失败证据和历史包/锁/旧Ref不可整体豁免。原P6身份快照与checker原字节不改；若某计划接线路径意外属于原保护集合，须单独列冲突并重新审核，不通过扩展通配白名单解除保护。
- P6发布树的其他文件也默认不可变，只允许COMPATIBILITY_IMPACT及下表明确的少数服务/薄UI/工具/版本元数据/治理文件变化。实际Git差异集合必须与批准的changed/addition/deletion清单精确相等；不能只检查被主动列入的文件而忽略额外文件、目录或删项。原核心金融/统计/数据/因子算法不在例外集合。
- 新当前包的bundle必须由**全部实际包内.py文件**重新计算，文件集合与P7身份/源码Git清单/安装wheel的逐成员hash完全一致，不沿用83常数、不漏新competition模块、不信插件自报hash。reviewed_code收据须对应新bundle和受限ENGINEERING_APPROVED/TEST_ONLY/financial_NONE；旧P6 Ref不能在新bundle伪装可加载。
- 允许src/aqrp/competition下的明确薄适配文件；仍禁止另起broker、第二backtest、真实provider、任意代码执行或POST7模块。P5引擎/执行代码继续禁止依赖具体因子/Streamlit，不能为适配改变架构方向。
- core/UI locks及Python3.13.16原样固定；UI三处锁副本、wheelhash、实际distribution+RECORD一致。任何新依赖不在本设计授权内，需另行评估/批准。
- 金融/时间/Task关键覆盖继续原95/90，其余现行门槛不降低；新competition至少按现行默认90/85，不为了称薄适配直接降到80/70。若需重分类须显式G1/新固定SHA审核，不移动金融逻辑套低门槛。
- 输出包含checker自身hash、模式、P6基线/设计身份、新bundle/源码与wheel身份、需求计数、保护/变化/新增计数和实际差异摘要；成功只表示开发方包准入，不能写独立G2/验收/金融通过。

## 明确允许的阶段工具/包装接线路径

| 路径候选 | 允许变化与约束 |
|---|---|
| 新tools/check_phase7_package.py及其独立测试 | 上述分模式准入、全量集合/字节校验、负控；旧check_phase6_package.py原字节保留 |
| tools/ci.py | 改为调用正确P7 checker模式；保留原full pytest/旧参考/原smoke/安装/ruff/覆盖/扫描；实现后在旧smoke之后新增明确P7 e2e/competition/reference命令与输出，不捕获失败继续标complete |
| 新tools/e2e_smoke.py、tools/e2e_reference.py、tools/competition_smoke.py（最终名在实施清单冻结） | 原服务真实19研究/10执行/同核与通用适配运行、独立原字节/数值参考，输出位于RUN/e2e与RUN/competition；不新增核心算法 |
| tools/ui_smoke.py、tools/ui_reference.py | 若扩展P7多时钟/旧CLI/新Task/UI对照须保留原同核/来源校验及旧actor；新增字段逐项证明，不通配忽略hash/lineage。旧原件作为P6源码/制品留存 |
| .github/workflows/ci.yml | 阶段/工件名改phase7，新增e2e/competition原工件路径，保留固定Actions commit、两OS/CPython3.13.16/read-only permissions/persist-credentials:false/fail-fast:false/if:always失败证据/hidden/error缺工件/retention；不加秘密、部署或写权限 |
| tests/environment/test_installation.py及受审身份包装字段 | 仅新包版本/安装身份适配，原安装真实性/非editable/RECORD/环境条件不删除；旧P6测试在旧包环境按原字节执行 |
| docs/audits/phase-7/{BASELINE_INPUTS,DESIGN_IDENTITY,IMPLEMENTATION_IDENTITY,...}.json | 新阶段来源/授权/设计与实际包身份，不重写P6原身份或旧答案 |

服务接线、薄UI/CLI和包版本范围仍按COMPATIBILITY_IMPACT；新增路径最终必须逐文件冻结，不把src/aqrp/services/**或tools/**作为无限授权。新checker不能只验证自己的可变清单而跳过独立原G1、P6基线与Git差异核对。

## CI原始ZIP及exact-member审计

tools/ci.py的upload-selection必须增加RUN/e2e/**和RUN/competition/**；workflow必须对应增加`${{ runner.temp }}/aqrp-evidence/*/e2e/**/*`和`${{ runner.temp }}/aqrp-evidence/*/competition/**/*`。选择器与上传声明从同一已冻结清单逐项核对，不能只改一边。每个P7真实输入、canonical请求、来源绑定、阶段工件/终态manifest、P4/P5原事务、独立比较与失败/拒绝/恢复日志都应在明确的选集里，缺必需项阻断complete。源码Git archive若未上传必须外置封存并明确，不宣称官方ZIP含源码。

environment.json在所有新命令、旧回归和必要证据选集校验完成之前保持complete=false。Junit统计使用实际运行数；旧P6 1567不是P7预定通过数。将源码/版本/OS/machine/installed modules/locks/UI wheels/原历史包环境全部绑定同一head_sha；新的P7 package gate成功不是独立审核。

官方ZIP仍按API artifact ID/run/attempt/job/head/平台、长度/官方digest/实际SHA256/CRC/精确成员逐项核验。所有upload-selection条目必须存在且hash相同；原文件、选择器自身、已解释的pytest-current复制别名子树须做**完整精确成员集合对账**，不接受大概数量或只读根manifest。新e2e/competition目录及失败子树也必须参与whole-subtree对账；清单外/缺失/重复路径、解包别名/越界、错误run/源码SHA一律拒绝。

保留原失败attempt及官方ZIP；同SHA重试不覆盖旧包，不以某OS成功抵消另一OS失败。真实浏览器仍是单独本机工程证据，不把AppTest或CI自动化输出称为真实浏览器；115MB开发模型路径保持外部，它的hash索引只是有限模型身份，不是CI产品工件或P7实现通过证明。
