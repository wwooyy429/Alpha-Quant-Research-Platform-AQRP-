# Phase4 Golden独立算术候选（G01–G20）

只用手算/有理数及stdlib参考校对；未调用AQRP组合函数（尚未实现），不是P4实现通过，也不是主审结论。可运行golden_reference.py获得开发方20组算术核对日志。所有权重/比率按1e-12绝对容差，数量/权限精确，金额1e-8；候选输入均明确为合成，同一决策、CCY、PIT且默认其余限额不触发。

| 编号 | 独立输入/推导 | 预期 |
|---|---|---|
| G01 | 单因子[3,1]，score权3/(3+1) | A=3/4,B=1/4 |
| G02 | 先定向分数A=[2,4],B=[4,2]；a=[3,1]，除4 | S_A=5/2,S_B=7/2；score权5/12,7/12 |
| G03 | A/B/C同分；K2；完整ID A<B<C | 选A/B，等权1/2,1/2；ties=true |
| G04 | TopK分数[-1,-2]；score权 | NO_POSITIVE_SCORE，现金1；禁止cash则INFEASIBLE |
| G05 | 同[-1,-2]；equal权 | A/B各1/2；规则不同结果显式 |
| G06 | F1有A/B，F2有B/C，a=[1,1]，B分数[2,4] | 交集B，S_B=3，权重1；A/C剔除不补0 |
| G07 | G=1,N=0，两腿各一资产 | long1/2,short-1/2；gross1,net0 |
| G08 | G=6/5,N=1/5，两腿各一 | long7/10,short-1/2；gross6/5,net1/5 |
| G09 | S=[3,1,-1,-3]；mean0；G=1,N=0 | 权重[3/8,1/8,-1/8,-3/8] |
| G10 | E1000；A/B各1/2；p=[30,40],lot10 | q*=[50/3,25/2]→q=[10,10]；w=[3/10,2/5]；cash300 |
| G11 | E1000，w=[1/2,-1/2]，p=[30,40],lot10 | q=[10,-10]；net=-1/10,gross7/10,cash1100；short冻结400+margin400→free300 |
| G12 | targetA=3/4；abs cap=7/10 | 超1/20，REJECT，不截断为cap |
| G13 | current=[1/2,1/2]→target=[3/4,1/4] | gross-turnover1/2，half1/4；cap2/5则拒绝 |
| G14 | net低界0，连续net0；G11整手后net=-1/10 | pre通过，post拒绝，不宣称取整天然安全 |
| G15 | 同行业w=[3/4,-1/4] | sector_net1/2，sector_gross1；gross_cap9/10拒绝 |
| G16 | w=[3/4,1/4],beta=[6/5,4/5] | Beta=11/10；upper1触发；缺任一Beta不得填0 |
| G17 | current10,target-5,sellable10,borrow_total5,short_permission=true | long_sale10、target_short5，均可；sellable9或borrow4分别拒绝 |
| G18 | current-4,target-6,borrow_total5 | 新增2但总short6>5，拒绝 |
| G19 | E1000，qnotional=[500,-500] | cash1000，short500+margin500=1000，free0；G08短500/long700则cash800/free-200拒绝 |
| G20 | 上界cap=3/4、tol=1e-12 | value=cap和cap+5e-13可；cap+2e-12拒绝；容差不作用于整数借券 |

非算术负例不能靠此脚本宣称实现通过：未来时点、假审批、停牌调仓、混合币种、旧结果篡改、独有旧持仓、缺暴露/borrow、奇零股全平、空腿/重叠、NaN和重复。它们在TEST_AND_EVIDENCE_PLAN逐项要求真实实现测试。G09均值是工程预注册变换而非开发/最终Test数据拟合；不得对正式Test选择参数。
