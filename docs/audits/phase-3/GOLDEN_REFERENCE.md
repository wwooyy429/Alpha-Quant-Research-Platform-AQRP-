# Phase3手工Golden候选（REVIEW REQUIRED）

golden_cases.json在业务实现前手工给定原始常量、预期和公式；reference_arithmetic.py只用标准库独立复算，不导入AQRP/NumPy，不从未来待测函数生成预期。开发方执行不等于QA-004 Gemini独立核验；所有答案仍REVIEW REQUIRED。保留已发布P0/P1/P2正确Golden原字节，若勘误须新版本及独立批准。

关键候选：P0 Pearson .19/sqrt(.0452)（完整值以Decimal高精度公式为准，不能把摘要六位当精确常量）；Spearman .9、tie sqrt(3)/2、ICIR2、z的ddof1；PriceVolume .1*.6=.06，不是L2 Momentum .21乘.6；滚动/neutralize/group/HAC/Holm/BY/label/purge也有手工案例。每项输入/期望在JSON，不把参考脚本输出反写答案。

float最终数值abs1e-12/rel1e-10，P0旧近似文本只按原abs1e-8比对；Decimal/Fraction/时点/hash/状态精确比较。HAC小向量仅核算公式，不声称小样本可产生正式推断或作为金融门槛。正式Test/审批等状态案例由独立测试计划补齐，不用数值脚本宣称实现了访问控制。

## G1修订新增候选

原15组/75断言获GPT Work补充独立算术核对，原JSON/脚本/log字节不变；不是Gemini QA-004全项批准。supplemental_cases.json另列28组手工输入/预期，supplemental_reference.log为开发方标准库122断言（全部通过），未来业务/OS权限/正式统计准入均未执行。新候选待独立复算，不能倒填成旧d10已审；旧公式/容差未改。
