# Phase 2 集成 0.1.1 修复审查包

用户明确授权集成已发布 main 后交审。本目录是新一轮集成资料，不覆盖旧 Gemini 报告/254项SDK/原始ZIP。

Phase2 原 head：947467b9d094905cab0af37ec5cc53f1d187e755。集成的已发布 main：fb1ba4fd51202a303115e4449ee49db09ccc071c（v0.1.1）。使用保留双父历史的 merge；包候选版本继续0.2.0，无新发布。

冲突处理：状态文档两侧原记录均保留并加最新权限；CI/runner保留Phase2名称、分支触发、factor数据/运行产物和实际wheel/.coverage上传；pyproject/包版本/安装测试保持0.2.0。三处共享代码精确等于main；因子Python实现、依赖锁及正确Golden未改。

CODE_REVIEW_EVIDENCE.json记录开发方对共享代码的实际准入审查、新旧bundle和三处hash；active CODE_BUNDLE.json及固定receipt同步更新。不能把修改hash当作Gemini批准：旧审查不覆盖新bundle，需对新固定SHA复核。SEC-001仍限受审内置工程测试，外部不可信插件/OS沙箱Unsupported。

新增tests/factors/test_p1_patch_integration.py共6项，分别在host阻断秒/offset超微秒、未知calendar/universe探索快照、共享time/PIT代码漂移；断言均不得进入因子compute。需求映射DATA-002、FACTOR-012、SEC-001；既有132项数据修复回归一并保留，全部原数学答案和容差不改。

新SDK、CI原始ZIP及清单按实际执行另行添加。旧报告十二项勘误/两项Low处理及报告事实冲突仍见../MATH_INCREMENTAL_RECONCILIATION.md，未宣称已全部闭环；Gemini完整SDK独立执行及新版本复核、用户验收、合并/发布仍待完成。用户对Phase1的指定代执行授权不能自动扩展为Phase2独立审查豁免。
