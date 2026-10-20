# Phase1复现及证据

使用用户批准的标准GIL/x64 CPython3.13.16。从PR固定SHA检出干净工作区，不浮动使用分支head。设置AQRP_RUN_ROOT到非同步本地目录，再运行`python tools/ci.py`。解释器版本不符、工作区不干净或任何适用检查失败即停止。

该入口使用锁定pip26.2.1 wheel及预审公开SHA引导新venv，按requirements.lock进行require-hashes/only-binary安装及pip check；从git archive固定Commit的副本以no-deps/no-build-isolation/no-index构建本地wheel，记录实际wheel SHA，再离线安装。静态、测试和扫描也运行该固定副本，避免源目录并发编辑污染结果。

输出独立UUID运行目录，包含environment.json（Commit、dirty、Python、OS、runner ImageOS/ImageVersion、锁/wheel哈希、CI run/attempt）、commands.log、JUnit、分支覆盖率、秘密扫描脱敏日志、固定配置/真实合成快照/查询结果及哈希。完整成功才complete=true；失败保留日志，不删除失败证据。pytest缓存、Hypothesis数据库、bytecode、构建源副本、venv和数据产物均置于运行或本地缓存目录。

CI为Windows x64及Ubuntu24.04 x64，Python精确3.13.16，无依赖缓存命中要求，均全新venv；Actions固定完整SHA、contents:read、无持久凭证，PR使用pull_request。实际托管镜像版本按各次environment.json记录，不声称windows-latest/ubuntu标签不可变。上传原始失败/成功日志与数据证据；有效期30天，最终审查原始证据另归档本仓库implementation目录并核对hash。

计划生成锁的原命令保留在requirements.lock头部；全传递22包（Windows包含colorama标记）精确版本及所有允许发行hash。only-binary策略拒绝源码构建；重新解析锁是升级操作，不能在复现时自动重算。uv引导版本0.13.4已核对官方wheel哈希。精确安装器/签名/工具/依赖来源见ENVIRONMENT_PLAN、DEPENDENCY_CANDIDATES及implementation中的实际记录，前两者只是原候选快照。

本地源BaiduSyncdisk目录反复出现索引写入/锁故障；自动审批拒绝删除index.lock后，使用LOCALAPPDATA/AQRP/checkouts下独立克隆，逐文件复制并校验未提交实现。原目录未reset/强推/删除，详见implementation/CHECKOUT_TRANSFER.json；后续提交和验证均注明这个独立工作副本。它不等于自动更改用户项目的默认路径。

当前实现尚需Gemini对新固定SHA复核和用户阶段验收，不合并、不打标签、不进入Phase2。未运行/未附原始证据的项必须NOT VERIFIED；不得使用本地PASS代替双平台CI、用计划PASS代替代码审查。
