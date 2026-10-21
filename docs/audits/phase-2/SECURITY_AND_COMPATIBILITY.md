# Phase 2 准入与兼容风险专项

威胁模型：受信维护者通过仓库评审提交已审内置因子；运行配置可能非法。MVP阻断非法配置、未知版本/hash、不兼容接口和未审代码装载；不接受任意本地/网络插件来源。恶意维护者/获得进程同权限的Python代码、原生扩展或文件系统攻击不由dataclass、DataView或AST防御，任意不可信Python执行Unsupported，OS沙箱设计D-006仍未完成。

准入设计先核对可信host allowlist及代码bundle/review receipt再导入，所有失败都有错误/失败run；只读接口不传账户或网络能力，不等于操作系统剥夺文件/网络权限。禁止把测试中monkeypatch socket/open成功拦截个别调用称作沙箱证明；静态检查只能补充人工审查。内置源码和完整bundle核验、防导入副作用、审查记录真实性/来源是Gemini本轮重点。

CodeApproval(test environment)与金融审批隔离。仅P2软件契约验收不产生ResearchValidated/StrategyApproved；Registry的选择、回滚只在已有code-approved兼容版本中进行。对未知approval域或strategy模式失败，不能自动升级成交易授权。泛化P0 Approved术语如被认定语义变更，必须在改P0前提交用户批准，当前只是待审细化。

兼容：factor code exactref、factor API version、data/schema version、依赖锁/host bundle、参数schema及输出schema全部pin。旧配置不可热改，停用/回滚不抹旧版本/证据。无最新版本自动发现；不在导入模块时自注册或访问快照。P2加法接口可局限factors与security，不变更P1公共签名；若确需破坏data核心契约，另列变更与迁移/新旧版本回归，暂停依赖实施。

不新增外部数据服务、交易API、凭证存储、容器/微服务或第三方sandbox运行时；只有既有SYNTHETIC_V1。P1披露的独立执行/远端字节缺失继续保留；P2审查只能核对新固定SHA和新执行证据，不把旧审核PASS覆盖新代码。
