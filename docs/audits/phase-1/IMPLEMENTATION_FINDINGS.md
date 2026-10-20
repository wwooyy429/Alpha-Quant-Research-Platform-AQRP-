# Phase1发现处置及剩余关卡

开发方处理，不等于Gemini签署关闭。原报告和勘误见DEVELOPER_RESPONSE.md及gemini/PRE_REVIEW_EVIDENCE_INDEX.json。最终固定SHA及真实CI结果由implementation/EVIDENCE_INDEX.json和PR描述对应。

| Finding | 已采取措施 | 关闭条件 / 当前责任 |
|---|---|---|
| F-P1-PRE-001 Medium | 固定3.13.16；完整22包哈希锁、禁止源码构建；新venv/no-index项目wheel、Windows/Linux真实CI | 以最终修复SHA的双平台全通过原始证据供Gemini核实，不能用候选JSON或旧SHA替代 |
| F-P1-PRE-002 Low | venv/cache/构建/产物均在非同步本地路径；索引锁故障后独立非同步克隆并逐文件核对，未重置原目录 | CHECKOUT_TRANSFER与实际环境路径；原同步工作区和其待提交改动仍保留，不冒称用户默认工作区已迁移或历史F-004全局关闭 |
| F-P1-PRE-003 Low | tzdata==2026.5两平台精确依赖；ZoneInfo.from_file仅读包内规则；DST歧义/不存在/时区日期/UTC存储全链测试 | 实际双平台测试及独立实现复核；未采用宽松>=或系统时区数据库 |
| F-002 / QA-001,ENV-001 | 已有真实Actions流水线，旧5e3ea46全通过；新75c3139扫描误报使该轮FAIL，全部保留 | 最终新SHA干净安装+静态+全测试+覆盖率+扫描+产物均PASS，Gemini复核后可建议关闭 |
| F-003 / DATA-002,005 | 统一timestamp/PIT、纯日期/naive/纳秒负例、迟到状态/退市/成员/别名、不可变日历/快照、mutation及正向控制 | 开发方102测试通过不替代独立复核；未知真实源available_at仍是外部限制 |

实际实施缺陷/失败均保留：首轮workflow引用runner上下文位置错误（2710a61，CI39472516191未启动jobs）；本地基础正例凭证使用字母顺序命中扫描器内置stopword，改为固定随机假模式后正负控制通过；日志解码添加UTF-8；本地测试编写语法/缺口夹具错误在实现测试中修正，原日志保留；75c3139的秘密扫描把CHECKOUT_TRANSFER中secret_scan.py的SHA和历史artifacts.json里secret-scan.log的SHA误判generic-api-key。

误报处理：新校验清单使用{path,sha256}记录，保留原历史artifacts.json字节；.gitleaks.toml仅允许该固定历史原件路径和精确完整SHA所在完整JSON行，已独立重算为实际脱敏日志hash。其他路径/其他hash/任意真实密钥不在例外中。扫描结果用--redact=100及JSON报告；无需、也没有宽泛忽略fixture或关闭默认规则。Gemini应重点核对这一唯一例外。

仍需：最终固定SHA双平台证据全部PASS、Gemini实现审查与缺陷复核、用户Phase1验收。main合并/打标签/Phase2另需明确授权。此处不宣称Phase1 ACCEPTED或RELEASED。
