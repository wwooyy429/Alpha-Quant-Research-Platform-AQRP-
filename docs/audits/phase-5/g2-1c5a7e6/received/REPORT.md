# AQRP Phase5 G2 — 003原始执行背书修复独立复核

完整固定审查SHA：`1c5a7e62cace7c3e66b7cc7f12fd564cb0013654`；前轮：`bf5e5a89209f2dd24042cd806626f832b531de52`。实际执行者：GPT Work补充审核员（本审查会话）；2026-10-23，Asia/Shanghai。

**G2 PASS — RESTRICTED ENGINEERING SCOPE（既定十二项受限工程范围）。WORK-P5-G2-003 High：CLOSED — FIX VERIFIED；001/002保持CLOSED，无新增阻断发现。用户Phase5阶段验收仍待决定。** 这个结论仅适用于本完整SHA及下述已执行/可证明范围，不是部署、正式Test、金融批准、发布或P6许可。

PR #8起止及封存前均读取head/描述AQRP_FIXED_REVIEW_SHA锁，均为本SHA；detached检出且工作树干净，没有审漂移HEAD或修改仓库业务/测试文件。main、phase4-baseline、v0.4.0保持`32ea5d6b75c84c07017d87377eeabd2f78207c5c`，全部旧标签起止相同。

## 003关闭依据：代码、原反例与适用边界

前轮003原因为已交收SHORT cashlot.amount与同一post_state中lot.price可以同步99.9→98.9相互自证，原始Fill1股@99.9及Journal不变，却在失败/取消公开known=true、S_set98.9、available798.9。正确C_set997.8、S_set99.9、A797.9；前轮报告/反例保持原字节，不能被本轮关闭追溯改写。

本轮逐行审核`ledger.verify_execution_backing`（142行起）、`transactions.verified_snapshot`（125行起）、`services.projection`（75行起）及正常/异常/取消/重放调用点：

1. 来源为writer锁内恢复并验证完整哈希链的durable prefix；重建读取records的真实children/payload，不从被核post_state的lot、缓存Fill或价格生成expected。实际Fill按证券重建FIFO开平、跨零、原始gross所得及未平限制；SPLIT调整股数/单位成本，MarketConfirmed重建mark，DELIST按原行动现金回收，SETTLEMENT处理真实到期及已完成session。随后比较lot、cashlot、复制Fill/回收、数量、成本、mark/估值调整和交收元数据。缺失/矛盾来源拒绝认证。
2. `cash_structure`现在明确只表示内部结构检查，`execution_backing`才表示已核原始执行/FIFO/交收。私有projection未提供records（None）时拒绝；真实服务提供本run已验证的磁盘前缀，不信任调用方自报来源。合法尚未提交事务的初态可以有零条commit，不能与缺失来源混为一谈。
3. initial_cash、other_restriction按当前从现金开始的工程profile为不变输入；verified_snapshot从initial.json核对最终状态及每一个已提交prefix的这两个字段。曾改动后又恢复最终值也被拒绝，不能让post_state自行设置Journal的初始资金基数或固定Z。
4. 正常输出、失败、取消、数值重放均使用完整projection：逐桶/RP/Journal、来源背书、经济恒等式和归因。成功及重放重新读取durable prefix，缓存与磁盘不一致明确拒绝。无法证明的异常/取消统一FAILED、COMMITTED_STATE_UNVERIFIED、known=false，不公开last_committed_account或可信财务快照。原commit和第一异常原因保持。

**原最小公共服务反例已由本审查方实际重跑，3/3通过：** 未损坏同边界正控保持FAILED但known=true、S_set99.9/A797.9；成对字段损坏ContractError与KeyboardInterrupt两种路径均FAILED、UNVERIFIED_COMMITTED_STATE、known=false，没有last_committed_account，正常私有gate及完整projection也拒绝同一损坏状态。实际提交链、终态manifest成员hash、原始commit字节及公开result getter均独立核验。没有再认证或公开798.9。捕获故障后的FAILED是正确的合成负控，不是产品测试失败。

**额外15组实际公共服务/磁盘控制全部通过：** 两种捕获类型下的未损坏正控、成对字段+伪改post_state Fill复制件、归因池、初始资金与现金同步增加、固定Z减少；成功返回缓存与磁盘不一致；磁盘lot成对损坏；原成功run数值重放缓存/磁盘差异；两个锚点曾改后恢复。已知失败正控仍公开正确已提交账户，真实来源不一致则未知；原文件与首因保留，getter/manifest绑定正确。

另外新写独立上下文控制，使用**真实落盘TransactionStore提交前缀**，没有复用开发测试工厂或从生产account生成expected。独立Fraction模型/预先字面值核对多entry FIFO、两方向跨零、未交收/已交收cover、拆股、普通/零价公司回收、合法负available margin loss；六方向非负恒总额桶错分、R/P等幅抵消、来源缺失/重复/复制件变化、归因池及交收/lot损坏负控。共266条核对记录，**266 PASS / 0 MISMATCH**，含1228个金融标量比较。低层夹具是真实持久化来源/财务证明单元控制，不冒称完整撮合风险或OS权限测试；公共服务反例和完整SDK另行覆盖实际编排。

旧41组direct-state原脚本及40PASS/1MISMATCH原结果保留。新接口要求durable来源，本轮明确用上述上下文控制替代无来源调用，不能把“缺上下文被拒绝”算成所有财务负控通过。原最小脚本仅为私有gate检查补充实际重读的verified prefix并捕获其拒绝；请求、原始成对损坏、正确797.9/99.9和known预期未改，适配记录及最终脚本hash均封存。

因此关闭**同一WORK-P5-G2-003**；没有重编号、删除旧反例、改正确expected或弱化金融门禁。该证明是工程金融一致性证明；不能对拥有全部历史文件写权限的人提供密码学授权，也不是原生权限隔离。

## 十二项需求、接口与阶段依赖覆盖

106条canonical目录及P5十二项（10MVP/2Competition Ready）不变。3444冻结文件、12份G1设计/答案逐字节匹配原版本；七项既定包装例外按原清单检查。无P4金融源码、四因子算法或依赖锁修改。已接受G1及用户设计/实施授权保持，未加入P6业务或部署范围。

| ID | 本轮覆盖与适用结论 |
|---|---|
| BT-001 | 原子事务、六组BEFORE/AFTER×三捕获异常、真实子进程退出后原run恢复及重复终态拒绝通过；已知前缀财务认证现有原始来源/锚点证明 |
| BT-002 | 完整SDK的PIT、标签/信号可得性、严格未来执行与历史量可见性回归通过，事件次序未改 |
| BT-003 | 订单/成交状态、部分成交、DAY/GTC、撤单/到期/幂等及容量回归通过 |
| BT-004 | 执行价/滑点/tick/最小费/预算/限价/ADV边界，原生产探针及完整SDK通过 |
| BT-005 | 三现金桶、R/P、费用/成本/Journal逐项核对；原SHORT来源与不可变资金锚点、本轮独立正反例通过 |
| BT-006 | 拆股、分红、退市/回收及来源映射；低层模型的普通/零价回收、SDK实际生命周期回归通过 |
| BT-007 | 多空FIFO、所得限制、T+1/cover、借费/应付和margin loss；原错误认证反例及本轮模型/服务控制通过 |
| BT-008 | 账户/持仓/敞口/Journal/归因、成功与失败输出、实际落盘/返回/getter/manifest绑定通过 |
| BT-009 | 绩效/TWR/ddof1/年化/FIFO片段/费用一次性；独立字面数学与原始数值复算通过，金融批准仍NONE |
| BT-010 | 新SDK与官方双OS均执行P1九输入→P3→P4→P5两因子链、替换和数值重放 |
| QA-003 | 新完整1158与全部既定覆盖门槛通过；独立反例/模型/数学及原始证据核验通过，无未关闭阻断 |
| INT-002 | 真实已安装wheel、薄CLI同服务、原Ref/返回字节/重放/恢复及正式入口拒绝通过，未执行真实正式Test |

001与002分别在35f93d6首次独立关闭，并在bf5e5a8保持。本轮原短桶反例PASS、三边界一致、扩展20/20及原生产20/20通过（含原001六边界、真实os._exit进程原run恢复、坏链/注入PermissionError/总额差/桶错分、原002十种方向/开平腿/费用/收益控制）。六组原始commit/transactions/committed-trace/failed-state/返回hash绑定另核通过。没有将注入PermissionError冒称真实ACL验证。

## 本审查方实际执行与数学范围

- 干净SDK：`E:\WORK\AQRP-runs\gpt-p5-1c5a7e6-20261023\aqrp-87d64547-3922-4678-b3a4-a5cf51d4da00`。新venv、原哈希锁安装、构建并安装0.5.0.dev5 wheel，69模块源码及reviewed_code逐字节绑定固定Git；**1158 passed / 0 failures / 0 errors / 0 skipped**。所有既定行/分支门槛通过，完整SDK进程退出0且environment.complete=true；不是只运行选中的新测试。
- 实际环境：CPython3.13.16、标准GIL、64位AMD64、`Windows-11-10.0.26300-SP0`；Python可执行文件SHA256 `31fe10b4ed82a2f960af0ef9931f46a4b84ff286f8b6ffd9dee098cf4f10f17f`。完整版本/解释器路径、OS、安装/wheel/依赖、UTC记录见ENVIRONMENT及SDK原环境/命令日志。
- 原锁SHA256 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`，69模块bundle `68d723fd865a59ad843d0be096e841d1e56005907bb8783037a784c8159eda3e`。没有猜测新依赖版本或声称未安装依赖已验证。
- 原20+4、91项数学参考、三扫描控制、旧Ref/66发布文件/三个原run重放及P1八表+manifest/P3/P4/P5两因子烟雾/数值重放，实际在本次完整SDK执行，原stdout/commands.log保留。
- 本审查方标准库独立复算原25组/70项、补充25组/209项及6组2349设计模型场景通过，不导入AQRP或开发方checker生成expected。它们是数学/模型核对，不能加进1158或冒称额外pytest产品数。
- 从本轮独立SDK、开发方本地SDK及官方两OS的实际原始Fill/Market/Settlement和Journal，另行标准库重建两因子共240提交、**7904精确比较**通过，含分桶/RP、原子交收、原始execution_backing计数/限制、80位Decimal年化/Sharpe核对。此oracle仅覆盖这些实际恒价long开仓SDK样例，short/FIFO/actions另由独立模型、公共服务和SDK覆盖；不泛称全部历史宿主证明。开发方1026/因子独立参考如实另列开发执行，不冒称本审查方执行。

主命令均通过`run_capture.py`保存argv/cwd/起止UTC/退出码及原始stdout/stderr：固定clone/fetch/detach；标准Python的`run_sdk.py`→`tools/ci.py`；新venv运行五份原探针、`independent_backing_controls.py`和`public_backing_fault_controls.py`；标准Python运行scope/CI/SDK/原件/失败保留核验、两份独立数学和原始数值重建。全部`*.command.json`/`*.stdout.log`/`*.stderr.log`封存。脚本退出码与内部PASS/MISMATCH均检查，没有只凭退出0认定金融通过。

## 官方双系统CI及证据真实性

新从GitHub连接器读取run39920156761的两job及artifacts：completed/success，head为本固定SHA。实际CI执行临时merge `db8c9776007dc2e13a0ebd0aa2e6d7045d7a301f`，parents恰为P4基线+固定head，整树`9fa5f3739643214c81bbf4b2f081a46e0032bf7c`等于固定Git；未误说main已合并。

| 官方原始ZIP | pytest | 字节 | SHA256（匹配新API digest） |
|---|---:|---:|---|
| phase5-ubuntu-24.04-1 | 1158 | 167627051 | `2d368d5e582c6531d1b696a39b29515799d74d850a209ef95910f66f66ebe8ae` |
| phase5-windows-latest-1 | 1158 | 126386328 | `4e8dd9de86800bf040c57334e44766e81b195a1afc09a1707d8a6352e7c58d43` |

收到的官方原始ZIP字节与新API身份/大小/digest独立比对，CRC/精确成员集合/全部选中hash、69模块wheel/锁/环境、JUnit/覆盖、P5实际终态链/manifest/事务文件/返回绑定均通过。两包各3795个pytest current上传副本、198组，独立逐完整子树对应selected数字目录；未把原selection说成全部ZIP，也未冒称未上传的原symlink目标或ACL已验证。本轮检查官方原始字节，没有再声称本审查方亲自在远程Ubuntu/Windows主机执行或重新下载这些ZIP。

开发Evidence.zip：480918821字节，SHA256 `cc590bb40b9fbdbde24c2582f69008a0f23107f9118143323387a3ab227cfcf9`。10048声明文件+manifest、共10049成员，CRC/集合/全部大小hash通过；Fixed-Source.zip全部4528跟踪文件逐字节等于本轮固定Git。前轮589653932字节独立封存SHA256 `2b7b547a3e8b80e28d72160efb65aa485999af487febba442c88b579d788cc29`重新核CRC/176项hash；本版本接收137原件与旧zip或其外部自排除原收据/封存日志逐字节一致，PRE_REPAIR_IDENTITY等于旧Git。旧错误余额/认证和BLOCKED结论保持历史。

原7失败/3通过、纠正KeyboardInterrupt原因假设后4失败/6通过、扩展1失败/300通过、旧候选1152通过后的4个锚点失败日志均实际核有保留。旧d7b7eaa官方原ZIP外部仍可读，按保留receipt核大小/hash/CRC；仅为旧档案保存核对，未冒称重新执行或新读取该旧run API。旧1152成功不当作本候选1158成功。命名lint/收到原件空白失败保留；仅三个收到文件有局部尾空白例外，root/冻结规则及原字节不改。本轮未运行会重写历史报告的Phase0-only脚本。

封存后发布辅助脚本的实际执行sidecar及勘误另核hash：原包内的未执行草稿保留，原外置勘误明确未纳入原manifest；本审查方将其作为独立sidecar收入本次封存，不伪称旧包已覆盖。没有改变本固定源码/SDK/官方原包。核验结果见ORIGINAL_AUDIT_PRESERVATION及RETAINED_FAILURE_VERIFICATION。

## 未验证及待用户决定

WI-R2-001/002与真实Windows三主体隔离保持**DEFERRED / NOT VERIFIED**，延期至最终集成完整SHA的真实验证另行授权。本轮无账户启用、真实ACL/服务/调度修改。正式最终Test未运行；SDK中的正式入口拒绝单元/烟雾控制只证明APPROVAL_REQUIRED，未访问真实正式Test。金融批准NONE；完整历史宿主NOT VERIFIED，只保留已接受的软件包/锁/旧Ref/结果重放范围。

上述既有延期不因本轮G2技术通过自动关闭，也没有被拿来推迟003；003是在当前工程范围实际修复验证后关闭。本轮没有新增待批准的经济口径、依赖或部署选择。**待用户单独决定Phase5受限工程阶段验收；合并、基线/标签发布和P6启动须分别取得明确授权。** 本审查未合并、打标签、部署、实盘、运行真实正式Test、授金融批准或进入P6。

完整报告/发现处置、实际命令/成功失败原始日志、独立SDK选择工件和反例/上下文原件在本次独立EVIDENCE.zip封存；大小/SHA256/manifest与精确成员核验见独立RECEIPT.json。字节封存不是数字签名、用户验收或发布许可。
