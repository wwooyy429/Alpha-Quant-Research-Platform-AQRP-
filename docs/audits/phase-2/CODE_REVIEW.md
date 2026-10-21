# Phase2 开发方代码测试准入审查

审查者：Codex开发方（非Gemini），用途TEST_ONLY；状态ENGINEERING_APPROVED，financial_approval=NONE。随库固定策略不是外部plugin自报审批，不等于独立代码审查、研究有效或策略执行批准。

已检查：固定内置ID与receipt/hash先于BuiltinFactor导入；未知路径/URL/callable无法注册；完整aqrp源码bundle及固定依赖锁纳入hash；同ID/version不覆盖；参数/上下文/输出冻结，run UUID阻止路径越界，P1 query每decision取数、host可见日历及拆股视图复用，三公式不持有账户/网络，静态guard按Python3 Call和危险导入检查。

已运行独立标准库AST解析和禁止导入/调用检查，未在准入前执行factor compute。原始代码版本见CODE_BUNDLE.json；receipt写入固定package-data reviewed_code.json。任何源码调整后都必须重新审查并更新bundle/receipt，不能仅改hash掩盖未审代码。

限制保留：同权限恶意维护者/Python反射/原生代码不由AST/只读对象阻止；无OS物理沙箱。外部不可信代码Unsupported，不能称SEC-001提供完整进程隔离。已审内置的单机受控测试范围获计划预审认可；此开发方记录仍须送Gemini固定实现SHA复核。

审查后进入本次开发/正式wheel测试，失败如实修复/重审，不生成虚假Gemini批准。bundle hash：cfabe293a88c21f8be68bf913f3001edd2562b70f7e8fcde88427c8ab85d43bc
