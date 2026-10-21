# Phase 2 实现复核资料包

当前状态：IMPLEMENTATION REVIEW REQUIRED。Gemini只对4f8b0de01b5991ef172f52f6a81e64b855a32d68计划给出PLAN PASS；本次实现及证据尚待固定新SHA独立复核。用户未验收、未授权P2合并/标签/P3。

业务实现固定SHA：8183b3762b56c466b989d9062a720b5f0d31172a。后续文档/原始证据归档提交不改此版src/tests/tools/CI/依赖；最终复核头SHA由PR #3字段AQRP_FIXED_REVIEW_SHA给出，避免本文自引用。审查前读取该字段并固定下载，不审漂移分支。

## 核对顺序

1. gemini/PRE_REVIEW_INDEX.json及原报告（SHA256 5b6abe40bc78d088b40f19f883ddd0cfe551c52c6b625c8f6606c28a590aa35e）；PRE_REVIEW_RESPONSE.md逐项对照编号/方向/时序/数学勘误。原报告不改。报告提及的独立数学.py/.log尚未提供，不能补记已收到或独立复跑。
2. IMPLEMENTATION_TRACEABILITY.md与冻结106条/16组、10项P2 ID。计划拟文件名与实际文件名有差异，按实际测试函数追踪，不按误述新增Volatility/DAG。
3. FACTOR_SDK.md、FACTOR_IMPLEMENTATION_SPEC.md、SECURITY_AND_COMPATIBILITY.md；后两份是原4f计划设计，实施语义以正式契约及本次真实SDK交叉核对，若有冲突必须指出。
4. CODE_REVIEW.md、CODE_BUNDLE.json、src/aqrp/factors/reviewed_code.json；核验加载前拒绝未审代码、完整bundle、hash漂移、Python环境，以及批准只是TEST_ONLY。评估F-P2-PRE-001/002开发方关闭意见，独立决定是否认可。
5. implementation/EVIDENCE_INDEX.json、local-verification.json、local-archive-map.json、local/原始命令/JUnit/coverage/wheel/快照/因子产物。254 tests，0失败/错误/跳过；原P1 102项回归，新增P2 152项，P1测试仅AQRP包版本断言改0.2.0，不改金融期望。依赖锁未改。
6. implementation/ci/两份GitHub原始ZIP、api-artifacts.json、api-jobs.json、*-verification.json；可在无凭证环境复验原始字节/路径/CRC/清单/快照/运行hash/覆盖率门槛，或下载API原件交叉比对。
7. implementation/FINAL_CHECKS.json与FILE_MANIFEST.json：P0冻结资产、旧P1审计原件、Golden、canonical要求及main/tag只读核验；manifest排除自身，不替代Git身份。

## 已实际验证的范围

业务8183在干净树运行完整tools/ci.py，经Conda3.13.16启动新venv，hash锁安装、pip check、wheel构建/安装、ruff静态/格式、254测试、逐模块覆盖率、独立参考算式、P1数据smoke、P2三因子smoke、秘密扫描及正负控制全部通过。语句1171/1174（99.7445%），分支464/470（98.7234%）；coverage默认排除3行仅Protocol省略号声明，未排除可执行计算。开发过程中233/243测试通过后，曾在243项版本触发engine分支覆盖率不足；删除已被SignalBatch完整校验覆盖的重复不可达检查，新增真实类型负例等，未降低覆盖率门槛或删除正确失败答案，最终254项通过。中间日志保留development/。

CI run39590967220 attempt1，Ubuntu job119191513902、Windows job119191514330均success。CI checkout是GitHub临时合并6ff410928a34df1696fb1bf36072adb3e9312147，父提交f579b2c+8183，tree与8183完全一致，不把临时SHA冒充PR head。

| 原始ZIP | artifact ID | SHA256 |
|---|---|---|
| Ubuntu | 12342621298 | e816a54fc6d181904500adae860c21e12b255cb913af731c805855e0961b58da |
| Windows | 12342066424 | 6346c1fb51ab1dba310fa9d8f65a32be686c2ce9c58e96bccf74a8ec5df5dde3 |

两端各254项全通过；已下载原始压缩字节并与GitHub digest/size核对。包内安全路径/重复/CRC、upload-selection完整集合和每文件SHA、显式省略项、两快照各8表、3个运行manifest、wheel及coverage检查通过；两端与本地logical factor结果一致：.21、-.21、.6。运行随机标识/真实血缘及原始wheel压缩字节可不同，不假称全量hash跨OS相同。scanner与pip bootstrap字节未上传，inventory明确uploaded=false；项目wheel与.coverage本次已上传。local归档仅两文件重命名映射，未声称包括venv/cache/源副本/工具二进制。新P2证据不补记旧P1缺字节为已存在。

## 未闭环条件

- Gemini须对最终固定SHA审查实现、开发方勘误与证据，并决定是否接受两项Low的有限关闭；计划PASS不能覆盖实现。
- Gemini报告声称附带的数学原脚本/日志尚未收到。独立复核若执行新测试须附真实输入/命令/输出；不能以开发方运行代替独立执行。若无执行权限，明确NOT VERIFIED及剩余影响，由用户判断。
- Critical/High或影响金融/安全验收的Medium若发现须修复、新SHA、再复核。
- 用户阶段人工验收、另行main合并/标签授权、合并后范围/检查/基线核验，以及后续Phase3独立授权仍未取得。

只提交审查建议及证据，不推送、不合并、不打标签、不进入P3。main/phase1-baseline保持f579b2c99e762085772de6e70ba1fa98792a7add。
