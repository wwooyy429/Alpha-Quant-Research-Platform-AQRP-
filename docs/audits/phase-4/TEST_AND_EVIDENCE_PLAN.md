# Phase4测试与证据计划 · 未执行实现测试

G1先复算GOLDEN_REFERENCE的输入、分数合成/两腿/净总/换手/现金及整手后风险；独立参考仅stdlib Fraction/Decimal，不导入AQRP。开发方候选不算GPT Work独立认可；主审须自己复算并指出错误，不能用未来待测函数生成期望值。

实施后每项金融算术同时具备：预存独立答案；阈值等于/±容差内外、空/零/负/巨大/非法、lot与跨0边界；性质（资产/因子输入顺序置换不改结果、共同正比例缩放分数权不变、固定等权不随分数尺度变、long-short预算恒等、现金+signed市值=equity、固定正价格、固定正权益及固定行业映射下，向零取整或精确不动仅保证每票绝对目标数量/绝对目标名义金额、gross和行业gross不增；不推论Beta绝对值、net/行业net、turnover、现金或许可单调，所有约束均前后重查、相同hash确定性、拒绝后无成功target/账本写入）；独立Fraction/Decimal矩阵和手算例核对。精度容差固定，不得迎合失败改正确答案。

时序/PIT：所有8类输入event/available/decision边界(前1us、相等、后1us)、不同时区同瞬间、混合决策、未来/过期/错误快照/币种/同证券不同市场/duplicate/null。账户必须包括非选中持仓及短仓。风险覆盖每条限额pre/post-round、缺暴露/借券/许可、停牌、受限现金/保证金、卖出跨0、旧空平仓、原奇零股不动/部分增减/全平true或false/正负仓/跨0、目标与delta各自lot门禁、所有失败诊断。正式审批与显式工程两条路径分别负测；真实ResearchValidated通过仍NOT VERIFIED，合成测试凭据不能提升为金融审批。

服务验证同内核/不依赖因子名、不可变输入、不同因子/配置选择真实改变结果、幂等与失败ledger。P4不强行完成P5组合回测替换，也不把研究替换测试重新命名为已实现组合E2E。CLI/网页一致属P6，不写网页或伪造结果。

回归先保留P0/P1/P2冻结资产及P3已审源/旧研究结果；计划轮源码/测试/工具/CI/锁/已封存审计不改，CI若运行仅P3的578回归。实施轮完整干净源码git archive→依赖hash安装→真实wheel安装→全部SDK；逐模块覆盖、边界性质、原始外置20/4、独立数学91和三扫描控制按适用变更运行，原日志含硬编码身份必须另记真实执行者，不冒充独立主审。

每次保存唯一run_id、UTC起止、原命令/exit、失败/JUnit/cov、Python3.13.16与OS/依赖清单、锁/code/tree/wheel/数据/配置及产物SHA256。双OS官方CI核对workflow/run/job/attempt/event/base/head/实际集成SHA与tree，下载官方原ZIP，对官方size/digest及内部逐文件manifest/JUnit/coverage/轮子源码/环境/复现文件独立核验；不重新压缩冒充原ZIP、不省略失败、复制子集必须逐项声明遗漏和原完整包位置。

未来新增portfolio/risk源码改变准入bundle时重新代码审查receipt，不复用P3 receipt伪称已审。完整旧Ref复现范围延续用户决定，仅软件包/依赖锁/精确Ref/结果重放；完整旧宿主NOT VERIFIED。所有审批/隔离/正式Test延期必须在G2报告单列，不以测试数量替代金融有效性。


## G1两项发现的新增冻结用例与性质边界

原G01–G20答案/脚本保持原字节。新增ROUNDING_REFERENCE.md与rounding_reference.py的R01–R17属独立设计算术和规则候选，不导入AQRP或提前实现产品。R01重现X01的target10/90、delta -5/+90：新设计必须DELTA_LOT_MISMATCH拒绝。R02–R13/R17冻结部分增减/不动/全平开关/正负原仓/跨0和外部非整手目标；全平只免lot，仍须实际可交易/资金/可售等检查，不能拿数量局部通过当完整PortfolioResult成功。

R14重现X03：E1000、w=(.5,-.5)、p=(60,50)、lot10、Beta1同业，q'=(0,-10)，abs Beta与abs行业net从0升到.5；Beta和行业net区间[-.1,.1]应pre通过/post拒绝。R15重现X04：已有A10/B0、cash400，同价/lot等权目标，gross-turnover .6→1.1，cap.8应pre通过/post拒绝；已有原仓整手，不依赖001。R16只校验收窄的绝对目标数量/名义金额/gross/行业gross不增以及合成资金恒等式，不宣称全部风险单调。

后续真正实现必须以这些独立预存答案核对实际内核与共同service，含篡改target/delta/风险flag及不合法建议不能成功返回；所有失败原样留存。开发方本次候选校对不关闭G1发现，须新固定SHA交GPT Work复核。
