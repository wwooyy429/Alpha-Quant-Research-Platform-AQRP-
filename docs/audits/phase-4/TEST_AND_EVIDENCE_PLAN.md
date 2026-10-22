# Phase4测试与证据计划 · 未执行实现测试

G1先复算GOLDEN_REFERENCE的输入、分数合成/两腿/净总/换手/现金及整手后风险；独立参考仅stdlib Fraction/Decimal，不导入AQRP。开发方候选不算GPT Work独立认可；主审须自己复算并指出错误，不能用未来待测函数生成期望值。

实施后每项金融算术同时具备：预存独立答案；阈值等于/±容差内外、空/零/负/巨大/非法、lot与跨0边界；性质（资产/因子输入顺序置换不改结果、共同正比例缩放分数权不变、固定等权不随分数尺度变、long-short预算恒等、现金+signed市值=equity、取整后数量不增绝对风险但可能破坏净下界故重查、相同hash确定性、拒绝后无成功target/账本写入）；独立Fraction/Decimal矩阵和手算例核对。精度容差固定，不得迎合失败改正确答案。

时序/PIT：所有8类输入event/available/decision边界(前1us、相等、后1us)、不同时区同瞬间、混合决策、未来/过期/错误快照/币种/同证券不同市场/duplicate/null。账户必须包括非选中持仓及短仓。风险覆盖每条限额pre/post-round、缺暴露/借券/许可、停牌、受限现金/保证金、卖出跨0、旧空平仓、奇零股全平、所有失败诊断。正式审批与显式工程两条路径分别负测；真实ResearchValidated通过仍NOT VERIFIED，合成测试凭据不能提升为金融审批。

服务验证同内核/不依赖因子名、不可变输入、不同因子/配置选择真实改变结果、幂等与失败ledger。P4不强行完成P5组合回测替换，也不把研究替换测试重新命名为已实现组合E2E。CLI/网页一致属P6，不写网页或伪造结果。

回归先保留P0/P1/P2冻结资产及P3已审源/旧研究结果；计划轮源码/测试/工具/CI/锁/已封存审计不改，CI若运行仅P3的578回归。实施轮完整干净源码git archive→依赖hash安装→真实wheel安装→全部SDK；逐模块覆盖、边界性质、原始外置20/4、独立数学91和三扫描控制按适用变更运行，原日志含硬编码身份必须另记真实执行者，不冒充独立主审。

每次保存唯一run_id、UTC起止、原命令/exit、失败/JUnit/cov、Python3.13.16与OS/依赖清单、锁/code/tree/wheel/数据/配置及产物SHA256。双OS官方CI核对workflow/run/job/attempt/event/base/head/实际集成SHA与tree，下载官方原ZIP，对官方size/digest及内部逐文件manifest/JUnit/coverage/轮子源码/环境/复现文件独立核验；不重新压缩冒充原ZIP、不省略失败、复制子集必须逐项声明遗漏和原完整包位置。

未来新增portfolio/risk源码改变准入bundle时重新代码审查receipt，不复用P3 receipt伪称已审。完整旧Ref复现范围延续用户决定，仅软件包/依赖锁/精确Ref/结果重放；完整旧宿主NOT VERIFIED。所有审批/隔离/正式Test延期必须在G2报告单列，不以测试数量替代金融有效性。
