# Windows R3 开发方处理意见：待独立关闭

原固定b3d9aef79396db948d326f5ce247131f96739d9d，GPT Work REQUEST CHANGES。WORK-WI-R3-001/002仍OPEN，原WI-R2-001/002不关闭，整体Windows隔离NOT VERIFIED。原报告/模型反例、407文件封存收件见RECEIVED.json及received/，不能把旧628通过当成修复证据。

## 001 · Medium：不完整枚举被误当完整

放弃会吞掉DirEntry.is_dir错误的os.walk，前后两次均改为严格scandir及entry.stat(follow_symlinks=False)，不调用有损is_dir分类；打开/迭代/条目stat错误均直接拒绝，链接/reparse和非普通对象不下降遍历；任何持续/暂时权限错误、消失或I/O错误立即ACL_ENUMERATION_FAILED，field保留JSON phase/path/errno/winerror/错误类型/原始message，异常cause保留。lstat采集错误另外以ACL_TREE_METADATA_FAILED结构化拒绝。原双次membership、identity/type/link、ACL再捕获与祖先/封闭ACE检查保留；目录类型使用已采集stat，不再靠可能吞异常的is_dir来生成验证映射。完整proof增加两次枚举完成标记、精确对象ID/类型、完整描述符和祖先。不是删除安全检查、接受同样不完整的子集。

## 002 · Medium：局部探针不能证明全覆盖

windows_access_probe.py新增三个强制模式：freeze（可信operator原生SID、非提权）、probe（三角色分别访问）、reconcile（operator再次实际全树采集并强制三份结果对账）。冻结清单绑定attempt UUID、before/after、root、四SID、policy binding、真实P1 snapshot、发布sidecar及完整两次门禁。实际九输入由verify_engineering_input核定，包含所有目录边界、动态文件和私钥；存文件大小/hash、目录直接成员、对象ID和完整ACL proof。权威原字节SHA单独提供，probe配置由freeze机械生成并另锁SHA。旧只有非空hash字段的配置明确拒绝；research只消费清单，不要求它遍历不可读私域。

before/after采用同一attempt/root/policy/snapshot，after必须带before原字节及SHA，记录新增/删除路径；九输入、sidecar和key不得改变。任意漏/多对象、漏目录、hash/type/成员或上下文不符均拒绝。目录检查LIST_DIRECTORY、ADD_FILE、ADD_SUBDIRECTORY、DELETE_CHILD、WRITE_DAC、WRITE_OWNER、DELETE；文件才读全字节。当前封闭MODIFY不含0x40，所以DELETE_CHILD各角色应拒绝，不与对象DELETE混同。key按既定profile：evaluator可读且不可写，auditor/research不可读，不扩大ACL。

每份role结果仅listed_checks_pass和inventory_binding_verified；coverage_verified及all_pass保持false、标PARTIAL_REQUIRES_OPERATOR_RECONCILIATION。reconcile不能接受调用方提供的旧“当前清单”，必须自己以真实operator再次调用完整freeze采集；逐项重算三个角色所有operation/mask/native ERROR_ACCESS_DENIED=5/文件hash/目录成员，不能只信pass标志。树变动、缺一个检查/角色、错阶段或SID均拒绝。reconcile的all_pass和coverage_verified只表示该phase清单对账，overall_windows_isolation仍NOT_VERIFIED；真实token声明及执行证据必须由主审独立核验。

## 验证与兼容

tests/research/test_windows_r3_recheck.py含真实os.walk注错前后两阶段、消失/I/O/元数据错误、漏动态/目录、清单hash/root/phase/role、目录类型/成员/删除子项、key特定期望、真实P1九文件与sidecar、before/after链、重采集漂移和不可变CLI输出。windows_model.py的ACL/token/open adapter明确MODEL_ONLY，期望权限表独立硬编码，不使用待测operations生成期望。SDK额外导出windows-probe-model原始清单/三结果/对账/截断拒绝，仅模型不是NTFS三主体证据。原并发单次、崩溃恢复、重复拒绝在完整SDK保留。

0.3.1.dev3，47模块；默认内置因子1.1.3只区分全bundle。P1 snapshot.py/私有mkdtemp/rename、P3经济与统计、106需求、旧发布和独立答案不改；旧失败/不可读九文件/旧hash缺口均保留，不用新导出替代。唯一新增业务模块变化为windows_acl.py（另外仅版本和admission默认身份）；工具/测试/证据按最小范围改变。
