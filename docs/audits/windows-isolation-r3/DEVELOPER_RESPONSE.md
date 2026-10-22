# Windows隔离R2两项OPEN：开发方修复候选，待固定版本复核

原审查业务9ac5db069287a6e4a095e25ae8c3cc8fa229cded、管理员尝试e6968f1c-3552-4a98-af61-98a5194dafea，原184检查183通过/1失败保持。WI-R2-001/002仍OPEN_PENDING_INDEPENDENT_RECHECK，整体Windows隔离NOT VERIFIED；不自判CLOSED。用户授权本轮修复，不授权部署、真实账户/ACL变更、正式Test、金融批准、main合并、标签或P5。

本分支从核实main 0a57dccb5618ba08cd3572d6d6b78fec963a3041独立修复，不改Phase4 PR6或其固定18439f3。Phase3受限发布和P4工程状态不变。修复包0.3.1.dev1仅开发候选；默认因子1.1.1区分新全bundle，原数学公式和旧1.1.0精确Ref保留。发布标签不动。P0–P3历史审计、数据契约、独立数学答案保持原字节。

## WI-R2-001：继承证明替代“所有对象都protected”的必要条件

原默认OperatorPolicy路径完全保留，不删除其protected检查。新增必须由可信operator在代码中显式构造的WindowsTreePolicy；root和四主体必须与OperatorPolicy绑定，不能来自研究请求任意JSON。未绑定新profile的旧正式授权封印拒绝。新门禁只读，不创建账户、不修改ACL、不重写已有对象。

WI-NTFS-CHAIN-1关闭ACL集合：trusted operator/SYSTEM/Administrators FullControl；evaluator仅Modify（readonly区域仅ReadAndExecute）；auditor仅ReadAndExecute；唯一OWNER RIGHTS ACE为Deny WRITE_DAC|WRITE_OWNER，防动态对象创建者凭owner默认权修改DACL。research与Users/Everyone、未知SID/通用rights/传播变体、额外显式ACE、缺少必要读取或拒绝规则均拒绝；不以“没有发现宽权限”替代有效权限证明。

root及显式继承/只读anchor必须operator拥有且protected。其他protected对象也必须operator拥有；只有显式允许继承anchor以下对象才能继承，子ACE必须全部IsInherited且逐项等于直接父目录投影（目录OI|CI、文件无继承flags、传播flags0）。输入readonly子树所有者也必须operator。逐级验证到可信anchor；并检查外部祖先owner及对非trusted主体的删除/改权权限，拒绝reparse/junction/hardlink和对象类型/集合/identity/ACL采集前后变化。ACL闭集合是保守证明，真实token正负探针仍必须执行，不覆盖管理员威胁或所有微观竞态。

旧42对象的ACL缺少此OWNER RIGHTS保护，故新候选仍拒绝原权限形状；绝不事后补ACL后改判旧失败。未来若经批准执行，必须新attempt、新目录、执行前完整门禁通过，再运行动态工程生命周期，再立即完整门禁；任何失败保留。新policy需要经过主审固定SHA审查，不能视为已经批准的实际部署。

## WI-R2-002：P1私有临时目录保留，发布从operator预建输入开始

src/aqrp/data/snapshot.py不修改；mkdtemp/rename继续保留P1创建者私有语义。新增publish_engineering_input只允许实际operator身份，目标必须已存在且列入经审定readonly anchor，并先通过完整权限门禁。源在sealed域外的operator私有准备目录中生成。复制九个已验证原始文件到全新目录（0777/default inheritance，继承已审定父DACL，绝不把P1私有目录rename入sealed域），核源/目标字节与完整成员集合，完整ACL再验后才写最终publication sidecar，再验一次。失败残留保留，不回填ACL/覆盖旧内容、不返回成功引用。

verify_engineering_input要求完整权限门禁、P1 manifest/八表验证、精确九成员及大小/SHA、operator身份/工程scope/sidecar原字节与inventory_hash一致；没有最终sidecar即拒绝。只读anchor预建、发布和审定必须在evaluator启动之前完成。profile创建由可信operator另行执行，本轮未执行或提供会自动改真实ACL的脚本。

tools/windows_access_probe.py提供经审查后分别在真实三主体下执行的只读探针：实际Windows SID/提升状态、固定config SHA、实际九输入/侧车/动态文件全部成员；每文件分别检查READ、WRITE_DATA、APPEND、WRITE_DAC、WRITE_OWNER、DELETE访问，所有拒绝必须ERROR_ACCESS_DENIED=5，缺文件/共享冲突不算成功。读者实际散列完整文件，不能拿canary替代。工具不写输入、不改ACL、不启用账户、不运行FINAL_TEST。operator提供的before/after完整对象清单和原始token/argv/退出码必须由主审交叉核对，不把role字符串或模型测试当真实主体。

九个旧不可读文件未接管、未读取、未恢复，其bd7ebd...旧manifest hash仍NOT VERIFIED。本轮另生成同公开经济参数100/110/121、100/150/200的新工程数据及九文件原字节ZIP、SOURCE和manifest，供独立读取/复算；新snapshot_id/hash明确不同，不冒充补回旧输入或真实auditor访问。工程输入新导出不是已部署发布物。

## 自测、旧证据与剩余验收

50个新增针对性测试涵盖ACL闭集/链、旧ACL继续拒绝、越权/owner rights、全成员/源变化/部分失败、真实P1文件复制、侧车后补/篡改、探针缺文件不冒充拒绝及当前身份原生只读捕获；其中模型adapter明确仅逻辑验证。完整SDK另见外置VALIDATION索引及PR。原并发单次访问、崩溃恢复/重复拒绝仍在既有测试中回归；新真实三主体下的这些运行及完整before/after门禁未执行。

实际只读捕获C:\\及C:\\AQRP-Sealed祖先发现系统盘根owner为TrustedInstaller；sc.exe showsid原生核对SID一致。该明确系统维护主体仅加入外部祖先trust集合，不适用于sealed根/输入owner及域内ACE，任意其他service SID仍拒绝；补独立反例测试。前一候选99cab98不包含此修正，其SDK/CI只能覆盖自己的固定SHA，最终以更新后的固定版本为准。新key_file也被显式绑定到tree policy，确保operator发布全域检查与evaluator Host门禁对同一私钥角色ACL一致，不会默认把它当auditor可读的普通文件。

初期test1的2失败来自测试把eval Modify ACL放到了可信外部祖先，门禁正确拒绝；已把祖先夹具改为只读，规则不放宽。test4的1失败为conda子进程PSModulePath选择到未能加载的外部Security模块；改为显式导入Windows自带$PSHOME模块，不绕过执行策略、不改变系统模块或权限。test5通过；原日志保留。早期lint多语句/后续E731诊断与修正保留可用原记录，不编造未保存的完整首轮lint。

**未闭环**：GPT Work固定SHA设计/实现复核；新profile的真实三主体全路径读取、拒写、拒改权，实际before/after门禁与并发/崩溃/重复回归；可信operator对真实输入发布及环境/入口hash的审定。三个旧账户维持禁用，本轮不重跑管理员脚本。正式Test、金融批准、完整历史宿主仍未验证；不能标VALID-004全项或完整Windows隔离通过。
