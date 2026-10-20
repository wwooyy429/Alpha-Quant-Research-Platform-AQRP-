# Phase1实现审查包

状态：实现已提交功能分支，等待Gemini对新的固定SHA独立复核；本文件及测试由开发方提供。用户已授权开发，尚未验收Phase1，禁止合并main、打标签或进入Phase2。PR固定审查SHA以PR #2的AQRP_FIXED_REVIEW_SHA及交接回执为准；380d9f8计划PASS不能覆盖实现。

1. **目标**：合成数据与通用契约；14项P1需求完整映射在IMPLEMENTATION_TRACEABILITY.md。真实源、真实交易、P2–7不在范围。
2. **仓库/PR**：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/2 ，feature/phase-1-data-system，保持Draft。
3. **基线**：从已核实main502c6931dcfce50bee2f71a80524475fae6396bf；P0已RELEASED、phase0-baseline固定7de1d0e81385ae97f98ea673fe05dd726f0b577b。未修改main/标签或P0核心数据/事件/接口/需求/独立原件。
4. **实际交付**：src/aqrp/core与data、明确八表Arrow schema、严格质量、单位与时间、PIT/股票池/别名/状态/行动研究视图、不可变Parquet及DuckDB可重建索引；冻结Golden输入/答案；精确Python及全传递哈希锁、固定SHA Actions、秘密扫描和适用自动化测试。
5. **未实现**：真实供应商/市场profile、因子Registry/信号、统计研究/OOS/实验平台、组合/风险、回测撮合账本、网页、研究/回测CLI（Planned/Unsupported按既定阶段）。没有用模拟数据宣称真实接入。
6. **范围和文件证据**：implementation/PROJECT_MANIFEST.json为当前文件清单，不含自身；implementation/CORE_PRESERVATION.json核对P0冻结文件；Git diff核对实际变化。旧计划MANIFEST/SELF_CHECK原样保留。
7. **接口**：DATA_SDK.md与预审DATA_IMPLEMENTATION_SPEC对照；批准DATA_CONTRACT/INTERFACES未改。timestamp规范UTC，保留源IANA/date；Decimal128(28,8)；冻结对象和独立DataView，不暴露SQL/连接。
8. **环境**：CPython3.13.16标准GIL/x64；完整22包跨平台标记及hash在requirements.lock。REPRODUCE.md说明干净安装/离线wheel；真实环境及run/attempt/ImageVersion/锁/wheelhash在每次原始environment.json。
9. **测试**：102项pytest（含Hypothesis性质、固定常量/Fraction/Decimal独立参考、契约、集成、泄漏mutation+正向控制）。逐模块行/分支门槛由tools/check_coverage.py强制，无排除业务模块或降低阈值。原始JUnit/coverage/log见implementation证据索引，开发方执行与Gemini报告分别标记。
10. **CI**：Windows和Ubuntu24.04干净安装矩阵。5e3ea46双平台85测试PASS为历史证据；后续75c3139的102测试及覆盖率通过，但扫描校验清单误报导致整轮FAIL。修复后必须在新SHA重新取得全部通过，最终结果见implementation/EVIDENCE_INDEX.json；不能沿用历史PASS。
11. **Golden**：tests/golden包含固定完整schema输入/答案及SHA/计算依据；来源为实现前380d9f8的手工GOLDEN_REFERENCE及Gemini预审。原G-RET100→110=.10保留，新增100→105=.05；abs1e-12/rel1e-10不改。tools/independent_reference.py只使用标准库，不调用待测SDK，不冒充Gemini独立执行。
12. **发现处理**：DEVELOPER_RESPONSE.md保持原预审勘误/处理记录；IMPLEMENTATION_FINDINGS.md给出当前实现处置和证据，Gemini最终关闭仍待复核。无真实凭证。扫描误报仅一份固定历史清单的完整行/完整hash+路径精确白名单，配置与核验理由供独立审查。
13. **复现**：固定SHA干净检出，精确解释器运行python tools/ci.py；包由固定Git archive离线构建安装，测试/扫描也运行同一副本。真实smoke封存配置、快照、结果及run_id/hash；缓存和venv均不写源码同步目录。
14. **审查重点**：先可见后修订/区间、晚到状态/换码/退市、日期/微秒/DST、RAW与行动时序、质量守恒、文件路径/完整hash/同字节解码、数据副本隔离、跨平台类型/时区/锁与真实CI证据。请独立运行并报告实际权限/环境/命令、目标SHA及NOT VERIFIED，不因旧计划PASS跳过代码检查。
15. **验收前条件**：最终固定SHA全部适用CI与原始证据齐备；Gemini独立实现审查、勘误和阻断问题关闭；用户明确Phase1验收。后续main合并/标签/Phase2各需另行授权。本次不申请自动验收，也不执行发布。

具体边界：仅SYNTHETIC_V1；不证明供应商历史可得性；日历非交易所认证；日频间隔多个不同生效时点拆股明确拒绝，不猜测中间状态；索引每次重建，无持久性能缓存；无规模SLA。源Baidu工作区保留未提交副本和旧HEAD，实际继续工作副本在CHECKOUT_TRANSFER.json，未重置或清理其Git锁。


最终执行更新：修复提交b6c369974052a00d4cc57388d5a2eb3708a6e114在本地干净安装及GitHub PR run39475976555（Windows/Ubuntu）全部PASS。本地102项及覆盖率/扫描/数据smoke原始产物已归档；两端decoded job logs已归档。GitHub完整artifact存在且API给出digest，但连接器向blob输出主机传输失败，远端完整JUnit/coverage/environment/快照未在本地取得或独立核验hash，跨OS smoke hash逐字比较NOT VERIFIED；需Gemini从Actions取得，不掩盖此证据限制。后续归档提交仅增加文档/证据，不外推Gemini计划PASS为代码PASS。
