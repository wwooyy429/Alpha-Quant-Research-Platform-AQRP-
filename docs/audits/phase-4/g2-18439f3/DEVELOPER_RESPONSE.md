# P4 G2 开发方处理意见：待独立复核

原审查 SHA：`18439f31536295aea42e57e566d07cce345a35cf`。主审 GPT Work 原判 BLOCKED / REQUEST CHANGES，001 High、002 Medium 仍 OPEN；本文件只登记修复，不替代主审关闭结论。

## WORK-P4-G2-001 · High

根因：Fraction 精确检查后，统一 Decimal34 投影再次舍入有限小数；数量、delta、现金可能不再是已检查值。修复：有限小数使用整数分解分母的精确十进制表示，不受调用方 Decimal context 影响；非终止展示比率继续固定 34 位 HALF_EVEN。输入仍保持原 34 位有效系数、指数绝对值至 100 的域；合法输入计算出的输出可更长，不将输入域静默扩大。单独输出解析器限制规范十进制串及长度 2048。

成功前重建原精确目标并从真正序列化字节解析数量、delta、现金，严格相等核对、资金恒等式、pre/post 全风险约束、target/risk 内容哈希、上下文及全部建议；落盘后再次读取 result.json 并记录 published-byte-audit.json 与其 SHA。返回字节去掉附加 manifest 后必须等于落盘原字节。中途不一致不得成功返回；落盘后失败保留原字节和 publication-failure，终态 FAILED，禁止成功重放。旧结果完整性重放不等于重新批准旧结果金融正确性。

独立整数答案：E=10^n、p=1、lot=3（n=3/34/35/40），q=E−1、cash=1；p=.01、lot=.03、E=10^35，q=10^37−.01、cash=.0001；E=10^100、p=10^-100、lot=7，q=10^200−2、cash=2e−100；极小资金为 0 仓位。空头双腿 E=10^35、lot=3，各腿 |q|=(E−4)/2，cash=E，restricted=margin=|q|，free=4。答案由整数/有理公式给出，不调用待测函数生成期望。

## WORK-P4-G2-002 · Medium

根因：原绑定只交叉核 data hash，P1 manifest 的数据摘要不承诺 snapshot_id，导致一致改写请求 ID 仍被接受。修复以原 P3 成功终态 manifest 内 engine.json 原字节为父 ID 权威：核其 config 原始 UTF-8/哈希、嵌套内容摘要及信号 ID，要求所有记录同一 snapshot_id+manifest_hash。上下文、所有 envelope 和 source_snapshot 必须与该不可变锚点一致，再调用 P1 verify_snapshot 验证真实 manifest 和八表文件及表内 ID，附加实际 manifest 原字节 SHA。

bind_research 新增显式 source_snapshot=SnapshotRef。默认仅解析已有 SDK 归档约定的同级 inputs/dataset/<真实父ID>，无 fixture 替代或缺文件降级；自定义存储须显式给 Ref，绑定的绝对路径不被当成数据身份。新增 snapshot 与 snapshot_manifest_sha256 是新 P4 请求必需字段，旧不足绑定的草稿请求明确拒绝，已有原字节结果仍可完整性重放。原 P3 引擎、manifest、九个工程文件保持字节不变。

## 验证与保留

tests/portfolio/test_g2_published_integrity.py 覆盖两原反例、数值边界、小数/负数量、Decimal context、输入域、序列化/磁盘/返回篡改、合法 UUID 一致篡改、跨 hash、缺绑定/文件、显式真实 Ref、manifest ID/表篡改及引擎内部配置。旧 P4 答案及七冻结文件不改。received/ 与 development-history/ 保存原失败，不改判历史。

代码/测试修复属于已授权 P4 范围，不包含 Windows 隔离 PR #7、ACL、账户、服务或调度变更。只有工程数据；正式 Test/金融批准及真实隔离仍未验证。

