# Phase2 WORK-P2-002/003 修复交审包

状态：开发方修复验证通过，等待新固定SHA复核；不是用户验收或发布。固定完整审查SHA锁定在PR #3描述的AQRP_FIXED_REVIEW_SHA；执行业务为708b83be1dd597395b41f2ff6e10702749175bbf，父c70727c39182f81ee142730da9a9833a51581cd1。末次证据提交须核对src/tests/tools/CI/构建/锁与业务一致。

报告与原始失败：received/raw/GPT-Work-Phase2-c70727c-Recheck.md、Codex-Phase2-c70727c-Repair-Tasks.md，原248项清单及245份短路径原件；RECEIPT_INDEX.json记录3项显式省略及完整hash。received/invalid-run/保留错误成功产物，probe-before.*为开发方对未修改旧wheel的2失败/2通过复现。报告真实执行者GPT Work，不能补记Gemini。

当前修复：只改factors/contracts.py、engine.py，规范化等价配置JSON、拒绝重复键、按既有schema重算参数并跨配置/Signal核对、实际文件字节hash入清单。新增25项正式回归；公式、Golden、依赖锁与已发布P1三处修复不改。代码bundle重新审查并更新为51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d，仅工程TEST_ONLY准入。

新SDK run aqrp-4b6de3af-e5df-4c88-959a-4ad1ac4915a9，CPython3.13.16，真实0.2.0 wheel，全套417通过；未编辑原16通过、原四探针4通过。CI run39636161568/attempt1双OS各417通过；Windows原始ZIP12360664392（149849bytes，6a8dd1e48258801fb24b4e464296ae27ca5269162f0487177b613ef96a50e015），Ubuntu12360544462（149662bytes，11371f0e8771eafcbe18a6b638f4f5318b6fc05d611d58875bd2b915c70679e3）。官方hash、内部46文件、根清单、wheel/.coverage、两组8表/查询与3因子产物核验通过。源数据原query_hash按记录root重算，迁移后比较结果hash，不混同路径相关身份。

入口：DEVELOPER_RESPONSE.md、CURRENT_DISPOSITION.json、CODE_REVIEW_EVIDENCE.json、EVIDENCE_INDEX.json、LOCAL_VERIFICATION.json、ci/*-verification.json与原始ZIP、sdk/、original16.*、original4.*、verify_evidence.py、FILE_MANIFEST.json。verify_evidence.py为实际执行副本，保留原本地路径；正式可复现安装入口仍是仓库tools/ci.py。

001接收为GPT Work补充PASS；002/003登记DEVELOPER FIX VERIFIED / RECHECK REQUIRED，不由开发方代关。旧报告事实勘误、Gemini本人执行限制和人工验收/合并/标签/发布/下一阶段授权分开保留；本轮不合并main、不打标签、不进入P3。
