# P3-REPRO-ARTIFACT-1：精确旧制品的独立环境重放

对应WORK-P3-004、FACTOR-007、RESEARCH-008、EXP-003、INT-001。选择**独立旧wheel+原锁的独立解释器子进程**，不在新0.3候选环境中伪装旧Ref，不把旧receipt搬给新bundle。全部身份核验在执行前，未知或未审制品绝不因reproduce请求而安装/执行。

已保管的锚点：docs/audits/phase-2/publication/VALIDATION.json及FILE_MANIFEST.json。发布wheel SHA256 `70b43271ee142b18d5d9d306d452936f8409322fda5e676431f24eb150871c9d`，版本0.2.0，原code bb6076f87f616a98feb98287d661830b102ad015，稳定main f26255fc40a3080bfa883ad64938f60036a14759仅发布元数据；code bundle `51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d`，requirements.lock `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`。发布目录正式保管原wheel；实施时按manifest path定位及逐字节核验，不重打包假称原wheel。

EnvironmentArchiveRef必须含CPython3.13.16 standard GIL/x64及解释器安装包hash/OS架构、22锁包各原wheel/hash、AQRP原wheel、原receipt/FactorRef原字节、源archive/tree、数据全snapshot/manifest、请求/config字节与numeric projection schema。既有锁包hash允许的不同OS wheel是不同environment_ref，不能跨OS声称完整环境原字节相等。保管在hash寻址只读artifact store（Test环境在私有域）。可从批准可信来源补取与**原登记hash完全相同**的依赖；没有hash或解释器/系统身份不足则REPRODUCTION_ENVIRONMENT_UNAVAILABLE/NOT VERIFIED，不猜替代版本。

部署/调用：先核code/data/config/receipt/hash与批准状态，再验证只读受管独立venv，环境只安装原wheel和原22锁包（离线wheelhouse，require-hashes，无P3 AQRP覆盖）。以该venv的绝对python路径、隔离模式 `-I`、无user-site/PYTHONPATH/PYTHONSTARTUP、清理继承环境/凭据及独立cwd/temp启动固定已审重放入口；入口从已安装包读旧精确Ref，不把新P3对象pickle进旧环境。传预审过versioned JSON输入、size限额及结构校验；拒绝自定义命令/脚本/任意路径/依赖。旧环境内重新compute bundle/verify admission后才算因子。进程/环境分离用于制品兼容，不等于不可信插件安全沙箱；仅已审可信wheel。旧Data API factor_context使用只读受限投影；正式Test重放仍由私有evaluator且不能归还预算。

| 请求身份 | 路由 | API/三公式与允许结果 |
|---|---|---|
| 原0.2.0 Momentum/Reversal/Volume精确Ref及旧receipt | 原0.2.0环境 | 保留其原Factor API/schema/三公式/metadata/receipt，按原声明范围验证 |
| 同三名称但P3新bundle/新Ref | P3候选环境 | 内容身份必不同，必须完整bundle新审；原兼容DTO/公式用回归证明 |
| Price-Volume新Ref | P3候选环境 | 显式扩展close+volume/API范围，新receipt；不回写到原receipt |
| 旧Ref请求当前新环境直接resolve | 拒绝或显式指示reproduce路由 | 不原地替换hash/扩大原API兼容范围 |
| 原wheel/锁/receipt/data缺失、hash篡改或旧env不可构建 | 明确NOT_REPRODUCIBLE，附分类原因 | 无自动升级/下载latest/返回缓存成功 |

新增P3代码后完整bundle任何变化都走全量代码重审；新的0.3工程准入不授金融/策略批准。对原API有破坏时先列major变更、迁移、用户批准，不以加法口号跳过兼容检查。

重放三层比较：①归档输入/wheel/receipt/config文件hash**必须原字节相同**，绝不对JSON往返序列化再hash当相同；②逻辑结果投影：原decision/security/session/数值validity+reason、snapshot manifest内容、factor精确Ref、params/单位/可用时点及config逻辑身份一致，numeric abs1e-12/rel1e-10（原有特殊容差保留），null/标识精确；③允许变化项仅事前声明的run_id、请求UUID/墙钟、绝对路径及路径相关query/run_artifact身份。所有变化另存映射和原/新原始manifest，不能重写原hash或任意忽略不一致。环境不同/未声明字段差异只能DECLARED_PROJECTION_MATCH或NOT_REPRODUCIBLE，不能宣称全字节同一运行。报告比较模块只读这些产物。

验收：原三Ref各在原0.2环境真实重放，完整原manifest字节核对；P3新三Ref/PriceVolume各在新env运行；负例涵盖未知API、新bundle配旧receipt、缺wheel/锁/原依赖、篡改/JSON非canonical原件、不同OS与路径投影、失败与权限域。当前是具体设计，**这些新P3路由尚未实现/执行**；既有P2发布417/16/4不可替代未来路由测试。
