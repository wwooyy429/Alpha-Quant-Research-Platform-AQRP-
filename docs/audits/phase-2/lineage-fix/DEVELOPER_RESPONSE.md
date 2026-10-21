# GPT Work c70727c复核接收与开发方处理

报告目标c70727c39182f81ee142730da9a9833a51581cd1；真实来源GPT Work，不是Gemini。WORK-P2-001补充复核PASS；WORK-P2-002/003在该版本为Medium阻断，本轮开发方用未编辑四探针对上一正式wheel再次得到2失败/2通过，旧失败和错误成功产物均保留。

原清单248项大小/hash全部匹配，245项复制；仅3项大文件（固定源码ZIP、固定scanner/pip本地工具）按完整hash核对后显式不入库，原字节继续在原审核目录保留，不声称已上传。RECEIPT_INDEX.json记录原路径→短归档路径映射与省略；原清单/报告字节不改。两份最终头c707原始CI ZIP、SDK实际wheel/环境/日志/两套快照/三个因子产物、原四探针失败及16项通过记录现均可追溯；不是新修复版的通过证据。

| 问题 | 本轮处理 | 验证与状态 |
|---|---|---|
| WORK-P2-001 | 保留已发布P1三处源码、新准入绑定及6项host边界；不重开旧已修复问题 | GPT Work对c707补充PASS；本轮适用回归继续验证 |
| WORK-P2-002 | SignalBatch接受等价JSON时统一canonical不可变字节；重复JSON对象键拒绝，非法UTF8/非有限值结构化失败；write_run按实际落盘字节计算SHA256 | 格式化/键顺序/尾空白往返、batch内容hash与实际文件hash正向核对；原失败不删除。开发方已修复，待新固定SHA复核，不代审查者关闭 |
| WORK-P2-003 | 从config.spec重建既有FactorSpec/schema；config.params必须严格等于冻结投影（拒绝重复/缺键/未知/非法类型及范围），重算hash与config及每条Signal一致 | 真lookback1=0.1、lookback2=0.21独立手工比值正控；旧hash换参数及新hash重贴旧Signal均拒绝。开发方已修复，待复核 |

仅factors/contracts.py和engine.py两处Python实现改变；core/data及因子公式/输入/Git Golden/依赖锁/版本0.2.0不改。完整26模块bundle由fc1b501…更新为51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d，详见CODE_REVIEW_EVIDENCE.json及active ../CODE_REVIEW.md/../CODE_BUNDLE.json、随库receipt。实际开发方审查不等于Gemini独立批准或金融批准，仍ENGINEERING_APPROVED / TEST_ONLY / NONE。

25项正式回归位于tests/factors/test_config_integrity.py，追踪FACTOR-001/002/010、QA-002、ENV-002；原外置探针保持原字节供独立复跑，不改正确答案消除失败。开发源417项通过、覆盖率门槛通过；新完整安装SDK及双OS CI各417通过，未编辑原16/四探针分别16/4通过，两份原始ZIP的官方digest/大小、CRC/路径、46项内部hash、实际wheel/.coverage、两套八表及查询/三因子产物已实际核对通过，原件在sdk/与ci/。执行业务708b83b；最终审查资料提交仅改证据/状态，需对新固定SHA独立复核。本轮附件是审查资料，授权仍来自先前Phase2开发/修复范围，不新增main合并、标签发布、阶段验收或P3权限。

仍需新完整40位SHA复核、002/003由实际审查方裁定、旧报告事实/执行限制如实处理，以及用户Phase2人工验收和分别授权的合并发布。Gemini本人新的完整SDK仍NOT VERIFIED；本次GPT Work真实新SDK和ZIP复核证据单独登记，不相互替代。
