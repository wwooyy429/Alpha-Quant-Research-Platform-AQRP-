# 数量lot与取整性质：G1增量独立答案候选

本文件及rounding_reference.py只做设计规则/算术候选核对，不是AQRP实现或独立主审。原G01–G20及golden_reference.py不变。用有理数Fraction固定输入和预存答案，不导入AQRP，不用未来待测函数生成expected。数量整除无容差；风险比率仍1e-12，资金1e-8 CCY。本轮两项发现保持OPEN待复核。

## 数量门禁矩阵（lot均10）

下表的target是取整/保持后的候选，q_current+delta=target精确成立。这里只判定局部数量门禁；即使局部允许，资金、许可、可售、可交易、暴露等仍须全部通过，不能将本表写为PortfolioResult成功。R03/R13目标与连续理想数量精确等于原仓，才走UNCHANGED_HOLDING；不能对本来要调仓但失败的请求自动保留旧仓。

| 案例 | current → target | delta | full-close flag | 数量结论及独立依据 |
|---|---|---|---|---|
| R01 / X01 | A15/B0 → A10/B90，E1000、p均10、cash850、score1/9 | -5/+90 | true | 两目标整手仍拒绝：-5/10非整数，A非全平；DELTA_LOT_MISMATCH |
| R02 | 15 → 20 | +5 | true | 部分增加不整手，拒绝；不允许部分奇零股 |
| R03 / X02 | 15 → 15（q*=15） | 0 | false | 保持原奇零股，无交易建议；不需要全平开关 |
| R04 | 15 → 0 | -15 | true | 仅数量例外允许：完整原long一次全卖；其他检查不豁免 |
| R05 | 15 → 0 | -15 | false | 无全平例外，DELTA_LOT_MISMATCH |
| R06 | -15 → 0 | +15 | true | 仅数量例外允许：完整原short一次买回；资金/可交易等仍查 |
| R07 | -15 → 0 | +15 | false | 无全平例外，DELTA_LOT_MISMATCH |
| R08 | 15 → -10 | -25 | true | 跨0后有新仓，不是全平例外；拒绝，不能自动拆成-15/-10 |
| R09 | -15 → 10 | +25 | true | 反向跨0同样拒绝，不能自动拆单 |
| R10 | 10 → 20 | +10 | false | 普通目标与delta均整手，局部允许 |
| R11 | -15 → -10 | +5 | true | 部分平空不整手，拒绝 |
| R12 | -15 → -20 | -5 | true | 部分加空不整手，拒绝 |
| R13 | -15 → -15（q*=-15） | 0 | false | 原short奇零股不动，无交易建议，仍纳入全部风险 |
| R17 | 外部候选10 → 15 | +5 | true | 非零变化目标本身非整手，先TARGET_LOT_MISMATCH；也不能用外部risk_passed绕过 |

R01完整算术：target weights=(.1,.9)，gross=net=Beta=行业净=行业gross=1；turnover=(5*10+90*10)/1000=.95；cash/free_cash=0，其他默认约束可通过。新设计必须在P4数量门禁拒绝，不把不可执行标签或P5再查当替代。

后续实现还须验证普通整手全平在flag=false仍可、整手原仓跨0的delta整手时仅数量允许、lot非法/零/负/非有限、数量精确整除不借用ratio容差、停牌奇零股不动及全平被可交易性拒绝、全平仍受sellable/资金影响。这些是未来实际接口测试，当前没有产品运行结果。

## R14 / X03：绝对Beta及行业净暴露可增加

E=1000、连续w=(1/2,-1/2)、p=(60,50)、lot=(10,10)、Beta=(1,1)、同一行业、原持仓0。

- q*=(25/3,-10)，向零取整q'=(0,-10)，delta也为(0,-10)，数量整手。
- w'=(0,-1/2)；gross：1→1/2；Beta及行业net：0→-1/2，绝对值：0→1/2。
- Beta与行业net均采用[-1/10,1/10]时，pre通过/post拒绝。不能因gross降低而略过signed区间。
- cash：1000→1500；post短卖冻结500、额外保证金500、非short限制/费用0，自由资金500。资金足够不消除暴露超限。

## R15 / X04：相对原仓换手可增加

E1000、current=(10,0)、cash400、p=(60,50)、lot=(10,10)、LongOnly等权w=(1/2,1/2)。

- 连续q*=(25/3,10)，delta*=(-5/3,10)，turnover=(100+500)/1000=3/5，half=3/10。
- 取整q'=(0,10)，delta=(-10,10)，turnover=(600+500)/1000=11/10，half=11/20。
- turnover cap=4/5：pre通过/post拒绝。原仓与调仓都是整手，不依赖001。post现金500、无短仓，资金不能替代换手限制。

## R16：成立的性质及资金恒等式

固定正价格p、固定正权益E、固定行业映射，q'对q*向零取整或精确保持原仓：各|q'|<=|q*|，各|q'*p/E|<=|q**p/E|，gross及逐行业gross不增。只是这些非负绝对项的和不增；不推广到signed净额、Beta绝对值、换手、现金或权限。

当前无融资合成规则中，total_cash'=E-long_notional+short_notional；冻结short_notional并额外要求short_notional保证金，故free_cash=E-long_notional-short_notional-R-fee=E*(1-gross)-R-fee。R=0、fee=0时gross=1自由资金0，gross=6/5自由资金-200；cap1.5不能覆盖资金门禁。此推论没有改原经济参数。
