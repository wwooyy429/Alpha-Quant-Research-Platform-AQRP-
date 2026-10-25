<!-- Phase7 G2 repair candidate 001/002 -->
当前固定旧版本 ec6bfcedc0c424b6fa3e817c9a094385bd971d6f 的独立 G2 为 BLOCKED，001 Medium blocking、002 High 均 OPEN。0.7.0.dev2 仅为两项修复候选；原报告在 g2-ec6bfce/，范围、原始反例与开发验证分层见 repairs-g2-001-002/。新已提交完整40位SHA的完整SDK、双系统原包、真实浏览器及独立G2必须重新核实；不得沿用ec6通过数。开发自测不关闭发现，main/旧标签与全部延期和操作限制保持。以下原轮记录按时点保留。

# P7 开发方工程自查收据

本收据仅由开发方Codex在2026-10-25用户单独实施授权下签发，允许打包源码作为 TEST_ONLY 工程测试候选。不是GPT Work独立G2、金融批准、真实隔离验证、阶段验收或发布许可。精确包身份见 IMPLEMENTATION_IDENTITY.json 和包内 reviewed_code.json，真实执行固定SHA以PR #10唯一 AQRP_FIXED_REVIEW_SHA 及外部原始执行记录为准。

检查范围包括：experiments共同SQLite预算权威、全部受管研究入口、Task原子预留与R子运行claim、确定性trials outbox、legacy排他执行与恢复、冻结plan/CAS激活及陈旧会话拒绝；可选execution_sessions的完整P3研究与P5执行映射/所有权/完成屏障；competition离线身份适配、明确能力拒绝与同一服务调度；薄CLI/UI接线。未改P1/P3数学、P4风险或P5执行/账本算法。

原5016保护文件、原P6身份/checker、原审计/失败/独立答案/core和UI锁保持原字节。因子算法未改，语义版本保留1.2.1；整个包的 implementation_hash 因新控制模块而改变，完整FactorRef因此不同。旧P6 implementation_hash只能在其原wheel/锁环境加载，不能在新包伪装加载旧Ref。

安全边界仍为工程完整性控制：受信runner源文件及哈希、物理workspace/catalog/data、同库原子准入、不可变请求、终态manifest和claims/outbox相互核对；不宣称Python对象/SQLite替代OS权限隔离。WI-R2两项继续DEFERRED / NOT VERIFIED，正式入口失败关闭，金融批准NONE，无真实权限/部署/实盘操作。

开发方实际命令、失败、完整SDK、双OS原始ZIP和实际浏览器证据须分别按实际执行身份封存。此收据不能代替这些证据，也不能据自测关闭独立发现。

开发方在d9d020包上复现MIG-001：迁移接受了正常读取会拒绝的旧完成证明，继而允许新准入。原始失败、SQLite快照和中止SDK见self-review/MIG-001/EVIDENCE_INDEX.json，未改判通过。修订将正常读取的完整子运行验证提为共享函数供迁移调用，保留所有金融核对，并要求完成证明的规范字节、路径、轮次、配置和完整子证明一致。修复后的实际拒绝、回滚、健康迁移及完整新版本验证须另行记录；独立G2仍待审。

开发方另确认COMPAT-001：旧双OS CI及e610b9f实际安装包在缺失campaign_attempts记录时仍拒绝执行，但新增的激活验证先于原TaskState兼容边界运行，公开错误码从CAMPAIGN_ATTEMPT_HISTORY_INCOMPLETE变成ADMISSION_HISTORY_UNVERIFIED，导致未改动的原回归失败。原命令、stdout、JUnit及失败索引见self-review/COMPAT-001/EVIDENCE_INDEX.json。修订仅抽取原有严格原因匹配的异常转换并覆盖公开submit边界；所有权威验证、顺序、事务及原测试答案保留，其他历史损坏继续按原通用错误失败关闭。新版本仍须完整SDK、双OS及实际浏览器验证；原失败SDK不计为通过。


开发方COV-001：05fc498完整本地与双OS均1892项测试通过，但adapter/ledger/task_state/tasks四个原覆盖门槛未过，因此整体仍FAILED。原始官方ZIP、命令、覆盖和本地失败保留，不能以断言通过代替SDK通过。仅新增70项有实际拒绝/历史/恢复/无额外准入断言的测试；生产包6045a40、原测试、数学答案、覆盖阈值及锁未改。新增30/19/21项分别在实际安装包通过；同字节覆盖合并预测明确不是原生完整覆盖结果。后续固定新SHA必须重新执行完整SDK、双OS、原始ZIP及实际浏览器。处理与原失败见self-review/COV-001/，独立G2仍PENDING。


开发方SEC-001：6fc3e74双OS各1962断言、原覆盖门槛及十个非浏览器actor通过后，密钥扫描9条告警失败，完整SDK仍FAILED、实际浏览器未运行。两份公开合成配置前像独立复算覆盖全部9处；仅新增严格子配置，限定generic-api-key规则、完整对应哈希与7个确切路径，原.gitleaks.toml和secret_scan.py不改。实际继承及负例夹具失败均保留；原P1例外混合PAT在父/子同为0的既有局限明确记录，不能作为密钥检测通过。完整扫描提前，包含生成文件的全源集合/大小/哈希在测试后纯读取复核；只证明受信SDK端点字节一致，不是OS隔离。详self-review/SEC-001/。新完整40位固定版本仍须完整SDK、双OS原ZIP及真实浏览器，独立G2待审。

开发方HAR-001：e5e0b100680caa59706d7c3341988d9556b1f254 的完整SDK及双OS各1962项通过后，实际浏览器在取消重放收尾失败；complete-browser 原命令退出1，不能视为浏览器通过或G2就绪。服务按冻结G1 COMMON_BUDGET_ADMISSION_DESIGN 第3节、BUD-012/BUD-027 的明确契约返回 ADMISSION_IDEMPOTENCY_CONFLICT，e2e_smoke.py 取消分支却仍断言旧独立队列错误码。修订只纠正该精确断言，并新增实际受管零研究重放取消、原请求重试及换源拒绝的回归，直接执行收尾分支；原独立队列错误码、生产模块、金融算法、独立答案及预算规则不改。新增回归中的GUI证据接缝明确标为HEADLESS_UNIT_ONLY，不能代替真实浏览器。原实际失败COMMAND.json SHA256为44afe508ef46837f51270d9da902b06ed77c95fc61a12d18a4bb58c92a01be7f，stderr.log为5818ae184dbcd8f529158ac9914d1ad55f2558c88c2187f80bfdb5aff0aff899；原日志、实际GUI截图/下载、进程退出及未完成协议状态按原SHA另行封存。禁止修改冻结SDK断言后重判通过；新固定版本须重新完整执行SDK、双OS原始ZIP及全部实际浏览器协议。
