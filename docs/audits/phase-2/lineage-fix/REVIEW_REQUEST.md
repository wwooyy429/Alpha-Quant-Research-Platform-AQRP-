# 固定SHA修复复核指令（GPT Work / Gemini 按真实执行者署名）

仓库 https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- ，PR #3。先复制并冻结PR描述中的完整AQRP_FIXED_REVIEW_SHA，只审该版本。旧报告目标c70727c39182f81ee142730da9a9833a51581cd1，新实际执行业务708b83be1dd597395b41f2ff6e10702749175bbf；最终资料提交仅证据/状态，须核对源码/正式测试/工具/CI/构建/锁与业务一致。不能以旧报告PASS替代新修复复核。

重点：

1. WORK-P2-002：复跑原格式化JSON探针；合法缩进/键顺序/尾空白经统一canonical后，config_snapshot/content_hash/实际config.json及manifest一致。重复JSON对象键明确拒绝。逐项重算所有实际文件SHA256，不用JSON投影冒充文件字节。
2. WORK-P2-003：复跑config.params lookback2改1而保留旧hash/Signal的原探针，必须拒绝；按原FactorSpec/schema独立重算参数hash并同时核对config/每个Signal。真lookback1=0.1、2=0.21正控须通过；重复/缺键/未知/非法类型/越界及为旧Signal重贴新config hash均验证。不要更改正确答案或只改标签消除失败。
3. 原4探针脚本received/raw/test_work_p2_regressions.py及原两轮16项应原字节执行；25项新正式回归、完整干净wheel SDK417项、覆盖/参考/扫描及双OS证据核对，失败全保留。查验原失败与错误成功产物，不能用旧392绿色结论代替修复。
4. 新26模块bundle51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d实际重建，核对CODE_REVIEW_EVIDENCE、active CODE_BUNDLE/receipt和实际两处源码差异；只限ENGINEERING_APPROVED / TEST_ONLY / financial_approval NONE。P1修复与因子公式/Golden/锁不变。
5. 当前业务CI run39636161568/attempt1的两份原始ZIP见README完整ID/hash/大小；46项选择文件、实际wheel/.coverage、根清单、两套八表和query/因子run按原字节验证，CI临时merge父main+708b83b且tree与业务一致。最终头CI若另有run，单独分层记录，不把此ZIP冒充最终头产物。
6. 旧001按本次GPT Work报告接收为补充PASS；002/003由实际复核结果逐项裁定，不自动接受开发方关闭。报告原件/248项hash与245项归档、3项省略和失败均可追溯。分别写明真实操作者、Evidence Reviewed Only/实际执行/NOT VERIFIED，不补记Gemini本人运行或用户豁免。

请输出固定完整SHA、差异和证据清单、真实命令/退出码/环境/日志、问题逐项OPEN/CLOSED/NOT VERIFIED及剩余条件。无法实际运行应明确说明。用户Phase2验收、接受限制、合并/标签/发布及P3启动仍分别未授权；只复核，不合并、不打标签、不进入P3。
