# Phase4 G1 e40ddd0开发方处理意见

2026-10-22 当前Phase4 G1：GPT Work对固定265af16353d85ce8c2d229a7517809d707498da8判PLAN PASS（受限工程设计），001 High/002 Medium均CLOSED_DESIGN，无新增阻断。原17候选独立复算、64项证据检查通过；仅设计数学，不是P4实现。原件与接收/关闭在docs/audits/phase-4/g1-265af16/。实际P4实施仍待用户单独授权，未阶段验收/合并/标签/部署/实盘/P5；Phase3受限发布与延期不变。以下旧BLOCKED/OPEN按原轮历史保留。

GPT Work固定e40ddd0009cc30664c3a0fe0b74c4a497a541d77结论 **PLAN BLOCKED**。001 High、002 Medium继续**OPEN**；本轮为设计修订候选，不自行CLOSED或PLAN PASS，不启动P4实现。

## P4-G1-001 · 目标整手不保证调仓整手

接受反例X01及原奇零股不动冲突。采用原合成profile权限内的最小拒绝修订：仍对绝对目标向零取整，不改为增量格点量化，不增加部分奇零股交易权限、不自动拆成先平后开。q*精确等于当前原仓时保持原数量，允许原奇零股不动且不产生建议；其余按原目标取整。成功前分别校验有变化非零目标的lot与所有非零delta的lot；只有目标0且原完整仓一次全平、allow_full_close_odd_lot=true时豁免delta的整手。此例外仅免lot，不免可交易性/可售/借券/资金及全部风险。

X01目标10/90与delta -5/+90在新设计应明确DELTA_LOT_MISMATCH拒绝，无成功target。补已有奇零股部分增/减、不动、全平开关、正负仓、跨0和外部篡改非整手目标的冻结答案，详ROUNDING_REFERENCE。无需新增用户权限；若未来拟允许部分奇零股、交易增量格点或改经济规则，须另行设计批准。

## P4-G1-002 · 取整风险单调性质过宽

接受X03/X04。删除“不增绝对风险”泛称，只声明固定正价格、固定正权益和固定行业映射下：每票绝对目标数量、绝对目标名义金额、gross及行业gross不增。signed/absolute Beta、net/行业net、turnover、现金/保证金/自由资金及许可不具通用单调性，保留每一项前后复核，不仅检查净下界。

X03预存Beta及行业net 0→-0.5、abs 0→0.5，[-0.1,0.1]先过后拒；X04预存全额turnover 0.6→1.1，cap0.8先过后拒。原G01–G20答案和参考脚本原字节不动，新增独立stdlib有理数候选，不调用任何AQRP业务函数，也不将设计脚本校对当作产品测试通过。

## 主审其他意见及证据范围

显式补入原合成资金假设推论free_cash=E*(1-gross)-nonshort_restriction-fee_reserve。因此gross/leverage cap1.5并不意味着无融资profile资金允许gross>1；G08预算算术不改，G19依旧拒绝，不为通过案例更改保证金。

完整65项原成员及原manifest/receipt/ZIP原字节归档g1-e40ddd0，保留attempt-1主审辅助环境失败，不倒写旧报告。主审本轮官方双OS CI成功，但仅核API/日志/tree/上传digest文本，未下两份原ZIP、未重数578。本轮开发接收/设计自查同样不声称新独立SDK或P4实现通过。Phase3受限发布不撤回，延期仍NOT VERIFIED，无合并、标签、部署或P5。
