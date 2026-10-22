# 开发方源审查 · 不是 GPT Work 独立 G2

0.4.1.dev1，53 Python 模块；默认内置因子身份 1.2.1 区分全 bundle，因子公式未改。reviewed_code.json 仅 TEST_ONLY、financial_approval NONE 的开发方固定准入收据，不是主审关闭、操作系统沙箱或金融批准。

变更限定 portfolio/contracts.py、research_input.py、service.py、risk/checks.py，包版本与 admission 默认身份；核精确算术、实际字节复核、父 ID 不可变锚点、失败终态及旧结果完整性重放。根工具切换到本轮独立 IDENTITY.json，原 IMPLEMENTATION_IDENTITY.json 保留。P1/P2/P3 数学、数据契约、原 P3 发布、锁、独立答案、原 P4 七冻结输入保持原字节；IDENTITY.json 列出相对审查树未改文件，FROZEN_INPUTS.json 独立核七输入。

临时回归的反例已先在旧真实 wheel 上失败：before.log 两失败，原 bundle3cac…，并未用新代码伪造旧失败。后续正式 SDK 必须清洁已提交树、新 venv、hash 依赖、真实 wheel、原宿主包归档和完整回归，双系统原始 ZIP 实际下载核验。依赖锁不升级。

