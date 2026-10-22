# 后续真实覆盖执行契约 · 本轮禁止执行部署/角色命令

以下是可重复的验收接口，供独立审查，只有另获用户具体执行授权、可信operator事先审定完整部署/权限后才执行。本轮未启用账户或更改真实ACL。所有配置、清单、结果、stdout/stderr、argv/退出码、实际SID/token、UTC起止、环境和代码哈希分别封存，失败永存，不覆盖旧attempt。

## 可信配置与边界

operator-before.json必须是operator审定的UTF-8 JSON：policy包含root、owner/evaluator/research/auditor真实SID、inherited_roots、readonly_roots、key_file，严格沿用closed ACL；snapshot包含实际已operator发布的root/snapshot_id/manifest_hash；attempt_id为新UUID，phase为before。after配置只有phase改after，其余身份/根/源不漂移。配置原字节SHA由可信渠道预先锁定。policy/key/input/source必须是此次工程实际文件，不能canary替代。此工具不会建立或修复ACL。

封存输出目录必须在sealed root外、operator控制、路径事先审定，不能为research可写。配置/清单对有需求的角色只读，实际数据无需开放给research。下列参数名以本次审定的绝对路径及64位SHA替换；不得使用漂移配置。python必须为已固定wheel的3.13.16标准GIL x64运行时，TOOL为固定SHA下tools/windows_access_probe.py。

## 必经命令（此处仅说明，不执行）

1. operator：`python -I TOOL operator-before.json --sha256 CONFIG_SHA --mode freeze --output before-inventory.json --probe-config-output before-probe.json`。两输出不可覆盖，打印各自真实SHA；失败保留部分输出，不修复后重用为成功。
2. 分别以research/evaluator/auditor真实非提权token：`python -I TOOL before-probe.json --sha256 PROBE_CONFIG_SHA --role ROLE --inventory before-inventory.json --inventory-sha256 INVENTORY_SHA`。原始stdout分别存research/evaluator/auditor-before.json，完整stderr/退出和进程身份另存。退出0仅局部探针完成，输出coverage_verified=false/all_pass=false，不是隔离通过。
3. operator：`python -I TOOL before-probe.json --sha256 PROBE_CONFIG_SHA --mode reconcile --inventory before-inventory.json --inventory-sha256 INVENTORY_SHA --results research-before.json evaluator-before.json auditor-before.json`。此命令自己重新完整门禁/文件采集，不能提供旧current清单顶替。缺项/错位/native错误非5/任何漂移必须拒绝；输出phase coverage_verified=true仍非整体隔离。
4. 在另行授权范围运行工程并发单次、崩溃恢复及重复拒绝，每一实际动态产物保留；不得运行正式Test或修改经济/金融批准。任何失败均保存原环境、状态与日志。
5. operator：以after配置执行freeze，额外 `--before before-inventory.json --before-sha256 BEFORE_SHA`；生成after-inventory.json/after-probe.json，录全新增/删除路径，输入/sidecar/key不变。再分别三角色执行after probe，operator执行after reconcile同样加before参数。不得运行后补ACL再改原失败。
6. 独立审查必须核两phase完整proof/所有目录与文件/九输入与sidecar、key期望、三角色真实token/进程身份及全部生命周期回归，才能建议关闭对应发现。phase清单的hash/结果是审查证据，不是密码学主体认证或自动系统验收；不能仅信JSON中的native声明或开发方模型。

目录分别申请LIST_DIRECTORY=1、ADD_FILE=2、ADD_SUBDIRECTORY=4、DELETE_CHILD=0x40、WRITE_DAC=0x40000、WRITE_OWNER=0x80000、DELETE=0x10000，并对可读角色实际列举直接成员。当前MODIFY不含0x40，所有三角色此位应拒绝；DELETE对象自身和DELETE_CHILD不同。文件才做全字节hash；key仅evaluator可读、不可写，auditor/research应native错误5拒绝，operator生成权威字节hash。禁止把不存在/共享冲突/目录read_bytes错误当权限拒绝。
