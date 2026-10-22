GPT Work Windows R3复核：固定b3d9aef79396db948d326f5ce247131f96739d9d，候选REQUEST CHANGES；整体隔离仍NOT VERIFIED，原WI-R2-001/002暂不完全关闭。独立短路径干净SDK及双OS原ZIP各628通过，新九文件原字节/Parquet/四因子21/100、-21/100、3/5、3/50、旧66文件和三Ref、原R2证据均核验通过，三个账户仍禁用。以下反例为明确模型适配器测试，不是实际三主体越权。

请修复WORK-WI-R3-001（Medium）：windows_acl.py:142/157的两次os.walk没有onerror；真实os.walk在子目录scandir被注入PermissionError后，两次都跳过后代，verify仍从3对象退化到2对象并返回成功。请对前/后枚举错误立即fail closed、保留路径及原始错误，补独立阶段的拒绝/消失/I/O错误及完整正例；保留原identity/link/ACL变化检查，不能接受相同但不完整的子集。

请补齐WORK-WI-R3-002（Medium，验收工具覆盖缺口）：windows_access_probe.py仅核9输入、sidecar和非空inventory_hash，没有强制权威清单对账。after清单删掉一个实际存在的动态文件、保留原完整清单hash，三模拟角色仍all_pass。目录也统一read_bytes而失败，未覆盖FILE_DELETE_CHILD(0x40)。可在探针或独立强制编排阶段完成修复：绑定attempt/phase/root和before/after完整清单，核hash及集合完整；漏文件/漏目录/错误hash拒绝；区分局部检查通过与覆盖已证明。目录按类型做列举/创建子项/删除子项/改权等访问，文件才散列字节；私钥等对象要有角色特定期望或另行必需探针。若采用人工对账，交付可重复命令、原清单和强制验收条件，不能只写文字承诺。

原operator预建复制方案及P1私有临时目录语义保持；新九文件不是恢复旧不可读文件。修复后提交新40位固定SHA、变更清单、适用回归/SDK/双OS原ZIP及原始日志供GPT Work复核，不能自行关闭发现。本次不授权启用账户、设置真实ACL或重跑管理员脚本；不运行正式Test、不授金融批准、不合并、不打标签、不部署、不实盘、不进入P5。完整原报告/复现脚本/结果见同目录REPORT.md与封存包。
