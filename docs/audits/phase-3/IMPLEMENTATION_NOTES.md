# Phase 3 实现与验证边界

当前实施依据：固定 `3861ef1637bc2b4c28725d7afc5f2e1f02242e80` 的G1 PLAN PASS及用户明确确认U-001/U-002。本次授权不含实际账户/ACL/服务/调度部署，不含合并、标签、P4。G1原设计文件中的旧BLOCKED/待确认/Planned段落为当时状态；本轮实际映射以 IMPLEMENTATION_TRACEABILITY.md 为准，旧审计原文不修改。

当前实现为0.3.0候选。P1八表、SYNTHETIC_V1、Python3.13.16 standard GIL/x64及原22包锁保持；原已锁packaging26.3明确列为运行依赖，未升级或引入新包。研究服务验证实际安装版本；干净SDK另验证原wheel及包锁hash。所有正式测试仍须从干净Git归档构建、安装wheel执行。

`ResearchRequest`保存不可变canonical配置字节。`research()`/薄CLI共用服务。`research.synthetic.synthetic_research()`只生成公开合成输入，不产生期望答案；测试答案来自G1冻结数值和独立公式。单测内G1 SHA字符串只测试40位身份字段，不是该旧提交已含新源码的声明；真实SDK的research smoke使用environment.json中的实际执行提交。

主要API：data.exposures 的 publish_exposures/exposures_as_of；research.numerics的各算子、pipeline/compose；validation的make_labels、purged_train/walk_forward、hac/adjust_pvalues、propose/record_decision；experiments.ExperimentLedger及reproduce_current/archive_environment/replay_original/replay_published_runs；services.research.research/evaluate_sealed和aqrp-research CLI。

参数候选在config.candidates中分别声明精确Ref、参数、方向和不同score key。`hypotheses(config)`按全部候选（包括研究合成）×全部horizons生成family槽位；例如momentum::h=1。配置必须先存全family及每槽位定义hash，再计算。改变参数、方向、期限、stage/fit、币种/股票池/数据、方法/阈值、权限或seed均改变定义/缓存键。重复验证、失败及超预算尝试留痕，不能改名后伪称无重复。描述性工程p_approx与正式p分开；没有独立模型/正式协议不得以近似值凑齐正式family。

五阶段工件与原始FactorEngine config字节/signals完整保留；可重新计算content_hash。命中缓存会引用原计算origin_run_id与原始UUID/路径身份，不伪造新计算。当前重现比较原始manifest/hash保持不变，在明确数值投影上比较，允许的UUID/请求/路径/重复历史变化逐项声明。原0.2发布目录固定manifest锚点下66文件先逐字节核对，再在原wheel+原锁独立环境重放真实3份原运行；原始工件不经JSON往返重写。跨OS原wheel相同不代表解释器安装器或宿主字节相同，未保管的安装器身份不声称已验证。

coverage侧车区分独立每日水位和同一水位修订：先在evaluation_cutoff内取每coverage_id最新唯一修订，再选择最早足够覆盖退出的水位；后续独立日期不推迟已知历史标签，后来的同一水位修订仍形成新label版本。G1片段至P1完整快照的测试适配显式使用已批准P1“calendar.event=open”规则，源片段的先期日程元数据并非P1逐日记录；不补造行动/价格/可用时间答案。

Walk-forward采用保守的ALL_PRIOR_HELDOUT_PROTECTED：本窗及先前held-out信息闭区间与后续embargo均受保护，重叠评价观测只记一次。fit_cutoff不得晚于本窗开始，最终Test不可进入任一训练窗口。DEVELOPMENT时间上限严格早于Test起点；工程公开合成演示可运行全链与公开合成Test，但始终不是独立Test。

正式路径须由可信保管者构造OperatorPolicy、封存候选/协议/代码/数据/部署及方法证据。evaluate_sealed执行前核身份、授权和私有路径；统一control索引保存真实holdout身份，预留即消耗；成功/失败都只给开发端CONSUMED回执，详细结果留私有域。人工ResearchValidated签封必须匹配不可变proposal和验证证据。**代码/公开合成链路已实现；实际多主体部署和真实权限正负控制未获本轮授权，因此NOT DEPLOYED / NOT VERIFIED，正式Test未执行，金融批准=NONE。** 不能把单测模拟或Hosted CI普通账户当成真实隔离证据。

本轮不提前实现P4组合/风险、P5交易撮合/账本、P6网页或P7全链。上述阶段的Planned状态不影响本轮26项的实现范围；必须能力没有用占位输出替代。P3独立实现审核、上述实际环境证据、正式协议/金融批准与用户阶段验收仍分别记录，未经授权不合并或发布。
