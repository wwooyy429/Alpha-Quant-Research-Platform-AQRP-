# Phase7 实现 G2 审查资料

开发方发现的MIG-001及原始反例见 `self-review/MIG-001/EVIDENCE_INDEX.json`。旧d9d020包和872c05b本地SDK不能据此视为完整通过；后者已因确认缺陷中止并封存。修订版需新包哈希和固定提交的完整验证，修复自测也不等于独立G2关闭。

五项受限工程实现依据用户明确接受的C-P7-001～004（含修订003）及单独授权，G1固定 `645049ae9b08710ed93189b80547d14c87d80584`。实施从归档提交 `8106bbe6fbb73b5b4336d42e4c27b3adb1cf6ff8` 继续PR #10。G1通过不等于实现通过；本资料与开发方自测均不替代GPT Work固定版本G2。

审查仓库：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- 。PR：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/10 。**请只审PR描述唯一 AQRP_FIXED_REVIEW_SHA 的完整40位实现提交**，先核对Git对象/包/日志/工件身份，不以漂移HEAD代替。后续证据归档提交若存在，须与已执行代码提交分列并核对差异范围。

| 内容 | 路径或证据 |
|---|---|
| 用户原话、G1和条件接受 | IMPLEMENTATION_AUTHORIZATION.json；g1-645049a原报告及处置 |
| 原始需求五项／原106目录 | REQUIREMENTS_SNAPSHOT、IMPLEMENTATION_TRACEABILITY；docs/requirements.csv |
| 新接口及兼容边界 | IMPLEMENTATION_CONTRACT、IMPLEMENTATION_MANUAL、原G1 COMPATIBILITY_IMPACT／EXECUTION_SELECTION／COMMON_BUDGET_ADMISSION_DESIGN |
| 新源码及精确变更集合 | IMPLEMENTATION_BASELINE_FILES、IMPLEMENTATION_ALLOWED_PATHS、IMPLEMENTATION_IDENTITY、包内reviewed_code.json；新checker同时核原5016保护文件 |
| 已审设计与独立答案原字节 | DESIGN_IDENTITY；MAIN_PIPELINE_CANDIDATES、FINANCIAL_FEASIBILITY_CANDIDATES、GOLDEN_CANDIDATES；原G1参考方法与失败记录 |
| 当前干净SDK | tools/ci.py真实执行目录的environment、commands原日志、junit、coverage、wheel/RECORD、upload-selection及所有工件；实际路径/哈希见PR外部封存索引 |
| 原P6来源及兼容 | P6_BASELINE_INPUTS及p6-source-overrides；tools/released_p6_smoke.py在原P6源码/原wheel/锁新venv运行未修改checker、原安装测试及四个旧Ref；reproduction/p6原始日志与RESULT |
| 主全链与适配器 | e2e/PROTOCOL、frozen-plan、requests、actors、原R/P4/B/账本／manifest、独立projection；competition能力矩阵及真实同核receipt |
| 双OS官方证据 | 实际run/attempt/job/head/artifact ID、原始ZIP/API digest/长度/CRC、精确成员和全子树哈希；所有失败attempt保留 |
| 真实浏览器 | 固定实现wheel本机loopback测试进程、AX/截图/逐步操作/真实下载、各Task ID、研究预算和源工件前后完整清单；不得用AppTest或CI代替 |

重点反证：12次取消之后旧入口仍须拒绝；legacy与Task争最后一单位；多假设全N原子；跨family/参数/输出不重置预算；活legacy排他和恢复；outbox反序发布、缺失/外来历史；旧key/会话/epoch不能领下一actor。核对主19研究／10执行全部真实P4完成屏障、篡改血缘及缺省同包raw兼容。适配器不可缺省未知规则或运行真实源，不得新增第二风控/撮合/账本。

主协议12研究单位在任何结果前冻结，实际顺序为SDK2、TaskCLI2、AppTest2、legacy双CLI2、透明答案SDK2、真实浏览器2。CI只执行前10并保留BROWSER_PENDING，SDK命令complete不是整体E2E或浏览器complete。独立原风险夹具1单位、主根queued取消0及数值重放0均另列，真实浏览器完成后才产生开发方完整协议收据；这些仍需GPT Work独立核验。

原G1的36候选／394抽象断言、19截面／768数学模型路径保持原结论，不写成P7产品测试。所有新通过数只从实际固定版本日志读取；原失败不覆盖。最终是否G2通过由GPT Work判断，用户阶段验收和发布仍未授予。

主干/P6基线保持 `d563347ad11e1f26e131dc06e343250282c05c33`，旧标签不移动。WI-R2-001/002持续DEFERRED / NOT VERIFIED；正式Test未运行且入口失败关闭，金融NONE、历史宿主受限边界保持。无合并、标签、真实权限变更、部署或实盘。
