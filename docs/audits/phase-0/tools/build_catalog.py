"""Phase 0 文档编制工具；只生成需求与追踪文档，不实现业务能力。"""
from pathlib import Path
import csv
import io
import re

ROOT = Path(__file__).resolve().parents[4]
# id|source|tier|phase|module|definition|input|output|dependencies|acceptance|design
DATA = r"""
GOV-001|V3.0§1.1;V3.0§1.2;V3.0§1.3;V3.0§22;V3.1§5;V3.2§9|MVP|0|governance|只执行Phase0，质量顺序及长期平台目标，保留未修订原要求|V3.0–3.2|正式规范及授权范围|NONE|无业务实现且不启动P1，未实现如实标注|PROJECT_CHARTER.md
GOV-002|V3.0§14.1;V3.0§14.2;V3.2§2|MVP|0|governance|维护规定的12份正式文档及audits/golden/integration/e2e目录|原始指令|版本化文档与目录|GOV-001|全部真实文件存在，后续手册/部署阶段明确|PROJECT_CHARTER.md
GOV-003|V3.0§14.3;V3.0§14.4;V3.0§14.5;V3.1§8|MVP|0|governance|唯一需求ID、完整字段、双向追踪及需求覆盖/遗漏/重复/冲突审计|原文与设计|需求清单及追踪矩阵|GOV-001|每条有来源等级阶段依赖验收代码测试状态，原文节与实际文件均可反查|REQUIREMENTS.md
GOV-004|V3.0§15.1;V3.0§15.2;V3.0§15.3;V3.0§15.4;V3.0§15.5;V3.0§18;V3.1§1|MVP|0|governance|每阶段计划/范围/依赖/测试/审查/人工批准，合法状态与禁止越级|阶段授权及依赖|独立阶段计划|GOV-001|仅明确批准推进，验收与模块可用性一致|ROADMAP.md
GOV-005|V3.0§19;V3.2§4.7;V3.2§4.9|MVP|0|governance|每阶段A–F报告、停止等待、阶段验收不等于下阶段授权|阶段成果及证据|验收报告及授权记录|GOV-004|无用户记录不标ACCEPTED/RELEASED，无Gemini审查不申请正常通过|ACCEPTANCE.md
GOV-006|V3.0§17.1;V3.0§17.2;V3.0§17.3;V3.2§3;V3.2§4.8|MVP|0|governance|feature/fix/audit/main分工、PR、授权合并发布标签与可回滚|固定提交及批准|可追溯版本/回滚记录|GOV-005|无实际合并标签不称发布，不删历史掩盖错误|ACCEPTANCE.md
GOV-007|V3.0§21;V3.2§2|MVP|0|governance|跨对话先读规定文档及Git，GitHub与可信记录为事实源，冲突先报告|文档和实际Git|当前授权/稳定版核查|GOV-002|记录未提交与未同步状态，不凭记忆猜测|PROJECT_CHARTER.md
GOV-008|V3.0§16;V3.2§1;V3.2§4;V3.2§5;V3.2§7|MVP|0|governance|GPT开发、Gemini独立计划预审/固定SHA复审、15项ReviewPackage与审计模板|计划/指定SHA/原始证据|独立审查材料及报告|GOV-004|每阶段两次交接和修复复核明确，不用GPT自查代Gemini|ACCEPTANCE.md
GOV-009|V3.0§16;V3.0§20;V3.2§4.6;V3.2§6;V3.2§8|MVP|0|governance|缺陷严重度/复现/预期实际/修复SHA/独立复核，保留争议及原报告|审查发现|缺陷闭环及阻断判断|GOV-008|Critical/High未关闭禁止正常通过，Medium按金融安全判断|ACCEPTANCE.md
ARCH-001|V3.0§2.1;V3.0§2.3;V3.0§9|MVP|0|architecture|固定PythonCore/Streamlit/Registry/独立回测，13模块明确边界和依赖图|业务目标|模块架构及责任|GOV-001|插件不动资金、UI不撮合、报告不改持仓、回测不识别具体因子|ARCHITECTURE.md
ARCH-002|V3.0§2.2|MVP|0|architecture|优先技术栈及大型框架/微服务/后期库变更审批|技术要求|受控选型|ARCH-001|未批准不引入额外框架，静态类型/结构校验按风险评估|ARCHITECTURE.md
ARCH-003|V3.0§2.4;V3.1§2;V3.1§3|MVP|0|architecture|接口统一输入输出类型单位时间异常和SemVer，变更影响/兼容测试|各模块边界|版本化契约|ARCH-001|无隐式单位或静默不兼容升级|INTERFACES.md
DATA-001|V3.0§4.1;V3.0§4.3;V3.1§2|MVP|1|data|稳定security_id及市场/别名，OHLCV/amount标准化，原单位可追溯|标准化源记录|市场隔离日频数据|ARCH-003|同ticker不同市场不混，价格/股数/金额单位正确|DATA_CONTRACT.md
DATA-002|V3.0§4.2;V3.0§4.3;V3.1§2|MVP|1|data|UTC带时区event_time/available_at/decision_time及PIT修订查询|时间约束/历史版本|当时可见DataView|DATA-001|未来修订/晚到数据不进入过去决策，未知历史可用性阻断正式PIT|DATA_CONTRACT.md
DATA-003|V3.0§4.1;V3.0§4.4;V3.0§18|MVP|1|data|日历/交易session/本地日期/夏令时/半日休市及确定排序|版本化日历|跨市场一致时间映射|DATA-002|非交易日与边界正确，UTC日期不替代本地session|DATA_CONTRACT.md
DATA-004|V3.0§4.1;V3.0§4.4;V3.1§2|MVP|1|data|RAW和PIT复权视图、分红/拆股/行动数据不重复计收益|原价及行动|版本化复权视图|DATA-002|未来行动不回填历史，撮合永用RAW|DATA_CONTRACT.md
DATA-005|V3.0§4.1;V3.0§4.4;V3.1§2|MVP|1|data|历史股票池/停牌/退市及生效和可用双时间|成员及证券状态|Universe/StatusView|DATA-002|保留退市证券，禁止用当前股票池过滤历史|DATA_CONTRACT.md
DATA-006|V3.0§4.4;V3.1§2|MVP|1|data|缺失/重复/异常/零量/非法价格/错位/历史不足明确语义|原始记录|质量报告及隔离数据|DATA-001|不静默删大量记录、不缺失填零、不跨证券填充|DATA_CONTRACT.md
DATA-007|V3.0§4.3;V3.0§13;V3.1§2;V3.1§7|MVP|1|data|不可变数据快照、分片与manifest哈希、schema/日历/行动版本|Parquet与元数据|可验证snapshot_id|DATA-001|修改或损坏被识别，更正另建版本|DATA_CONTRACT.md
DATA-008|V3.0§18;V3.0§2.2|MVP|1|data|DuckDB/Parquet加载清洗及合成OHLCV基础|固定合成输入|可复现标准数据|DATA-001;DATA-007|干净环境加载并与独立数据答案一致，合成不冒充真实源|DATA_CONTRACT.md
DATA-009|V3.0§4.5;V3.0§11.2|MVP|1|data|未来数据变更/PIT修订/股票池时间测试，P2/P3扩展信号链|固定cutoff及变更集|不泄漏证据|DATA-002|历史可见投影不变，正向控制会变化；不只依赖mutation|DATA_CONTRACT.md
DATA-010|V3.0§4.1;V3.0§4.2;V3.0§3.4|Advanced Research|POST7|data|财务等扩展数据PIT公告/修订及字段契约|财报/其他数据|扩展DataView|DATA-002|财报期末不等于可用时点，单独审批|DATA_CONTRACT.md
DATA-011|V3.1§2|MVP|1|data|货币、最小单位、Decimal精度/scale及价格/成交量换算|源单位/profile|统一金融单位|DATA-001|跨币种未实现明确拒绝，金额不经float记账|DATA_CONTRACT.md
DATA-012|V3.0§4.4;V3.0§7.3|Competition Ready|3|data|PIT行业/市值/风险暴露数据接口及缺失语义|分类/暴露版本|研究风险可用暴露|DATA-002|不拿最新行业回填历史，缺失不视为0|DATA_CONTRACT.md
DATA-013|V3.0§4.1;V3.0§18;V3.1§5|Competition Ready|7|competition|真实比赛数据源映射、授权/规则和能力边界|用户选定源及比赛规范|来源明确的数据适配|DATA-008;INT-006|未知源/规则保持外部待决，不假称真实接入|DATA_CONTRACT.md
FACTOR-001|V3.0§3.1;V3.0§3.3|MVP|2|factors|统一Factor协议及12项元数据、参数schema、数据与API兼容声明|FactorSpec/DataView/Context|只读确定性信号|DATA-002;DATA-008|必填字段/窗口/频率/方向/可用时间完整、无账户或网络副作用|INTERFACES.md
FACTOR-002|V3.0§3.2|MVP|2|factors|信号时间/证券/ID版本/值、快照参数任务/可用时间/有效性及唯一键|计算输出|SignalBatch|FACTOR-001|重复幂等而冲突失败，血缘完整|INTERFACES.md
FACTOR-003|V3.0§2.1;V3.0§3.5;V3.1§1|MVP|2|factors|注册/resolve/兼容校验/停用/精确版本/回滚/参数校验|审查代码与精确FactorRef|固定Registry记录|FACTOR-001;SEC-001|同ID版本异内容拒绝，回滚只选已批准兼容版本|INTERFACES.md
FACTOR-004|V3.0§3.4;V3.0§18|MVP|2|factors|Momentum基础因子|L+1个有效session收盘|L期收益信号|FACTOR-002|121/100−1=.21且窗口不跨股票|INTERFACES.md
FACTOR-005|V3.0§3.4;V3.0§18|MVP|2|factors|Reversal基础因子|同Momentum输入|负L期收益|FACTOR-002|相同输入输出−.21，方向不重复反号|INTERFACES.md
FACTOR-006|V3.0§3.4;V3.0§18|MVP|2|factors|Volume基础因子|当日及前L日股数|相对历史均量信号|FACTOR-002|分母0/历史不足显式无效，手与股不混|INTERFACES.md
FACTOR-007|V3.0§3.4|Competition Ready|3|factors|Price-Volume基础因子与独立公式审批|价格和成交量|价量信号|FACTOR-003|公式预注册和独立答案，不以Volume冒充价量|INTERFACES.md
FACTOR-008|V3.0§3.4|Advanced Research|POST7|factors|波动率/流动性/基本面/更广截面/公式WorldQuant/ML扩展|已审批数据及模型|新候选因子|FACTOR-003;INT-004|每类新增独立需求/答案，不提前加框架|ROADMAP.md
FACTOR-009|V3.0§1.3;V3.0§3.5;V3.0§12.3;V3.0§18|MVP|3|factors|Candidate/Reviewed/ResearchValidated/StrategyApproved审批证据隔离|代码审查及研究标准/证据|审批记录|FACTOR-003;VALID-008|P3不凭空要求P5，策略批准待P5经济证据|RESEARCH_PROTOCOL.md
FACTOR-010|V3.0§3.5;V3.0§13|MVP|2|factors|配置选因子/参数/增删/停用/权重/版本/回滚，新运行pin不可热替换|不可变因子配置|新运行版本|FACTOR-003|旧运行不随registry变化；权重由P4消费，UI由P6提供|INTERFACES.md
FACTOR-011|V3.0§3.6;V3.1§1;V3.2§7|MVP|2|factors|P2注册替换和版本兼容测试|固定DataView/两个因子|API替换证据|FACTOR-004;FACTOR-005|只改FactorRef，不调用尚不存在研究/回测|TESTING.md
FACTOR-012|V3.0§3.3;V3.0§11.2;V3.1§7|MVP|2|factors|因子隔离/确定性/不修改资金持仓费用或其他代码|受审插件与只读数据|受限执行|FACTOR-001;SEC-001|未授权读取未来/网络/账户被拒，接口不冒充沙箱|ENVIRONMENT_AND_SECURITY.md
RESEARCH-001|V3.0§5.1;V3.0§12.1|MVP|3|research|批量Alpha计算/预处理/验证/报告/实验完整研究编排|因子股票池/区间/协议|完整研究产物|FACTOR-003|链路真实可运行，无占位模块伪装|INTERFACES.md
RESEARCH-002|V3.0§5.1|MVP|3|research|去极值/缺失处理/横截面排名/z标准化，顺序和拟合区间配置化|原始信号与处理链|清洗和标准化分数|RESEARCH-001|常数/极端/缺失/小样本有明确定义和答案|RESEARCH_PROTOCOL.md
RESEARCH-003|V3.0§5.1;V3.0§18|Competition Ready|3|research|行业和市值中性化基础|PIT行业/市值与分数|残差及诊断|RESEARCH-002;DATA-012|秩亏/暴露缺失处理明确，不复制原值冒充|RESEARCH_PROTOCOL.md
RESEARCH-004|V3.0§5.2|MVP|3|research|Delay/Delta/RollingMean/Std/Correlation/Sum/Min/Max|逐证券session序列|窗口算子输出|RESEARCH-001|端点/min_periods/ddof明示，独立测试每算子|RESEARCH_PROTOCOL.md
RESEARCH-005|V3.0§5.2|MVP|3|research|Rank/Ts_Rank/Conditional白名单算子|当前截面/窗口|秩及条件结果|RESEARCH-004|并列秩正确，条件不执行任意代码|RESEARCH_PROTOCOL.md
RESEARCH-006|V3.0§5.3|MVP|3|research|分别保存raw/clean/standardized/neutralized/final及报告stage|处理链结果|分阶段产物|RESEARCH-002|未启用stage标SKIPPED，不能混报|INTERFACES.md
RESEARCH-007|V3.0§5.1|MVP|3|research|因子相关/组合研究/冗余分析|同股票池及stage因子|相关与冗余报告|RESEARCH-006|对齐交集和缺失n，研究组合不动账户|RESEARCH_PROTOCOL.md
RESEARCH-008|V3.0§5.1;V3.0§13|MVP|3|research|缓存和参数实验，版本/时点/处理链缓存隔离|运行配置和数据hash|可追溯缓存/实验|EXP-001;RESEARCH-001|未来数据/参数改变不复用错误缓存，所有试验保留|ARCHITECTURE.md
RESEARCH-009|V3.1§1;V3.0§3.6|MVP|3|research|P3因子替换后完整研究可运行|固定研究配置及Momentum/Reversal|研究替换报告|RESEARCH-001;VALID-001|只改因子选择，报告/统计核心无需改动|TESTING.md
VALID-001|V3.0§6.1;V3.0§6.2;V3.0§10.2|MVP|3|validation|Pearson/Spearman/MeanIC/std/ICIR/正值比例/序列|有效截面分数与未来标签|统计指标及n/reason|RESEARCH-006|平均并列秩/ddof1/默认非年化正确，Golden对齐|RESEARCH_PROTOCOL.md
VALID-002|V3.0§6.1;V3.0§6.2|MVP|3|validation|分位组收益/单调/TMB、衰减/多期限/年度稳定|已注册期限和标签|分层衰减年度报告|VALID-001|标签起止可用/股票池/权重明确，不混期限|RESEARCH_PROTOCOL.md
VALID-003|V3.0§6.3;V3.1§4|MVP|3|validation|Train/Validation/Test及Walk-forward/Purge/Embargo|标签信息区间和split协议|无重叠污染评估|VALID-001|相交训练标签剔除、窗口留痕、不随机打散|RESEARCH_PROTOCOL.md
VALID-004|V3.0§6.4;V3.1§4|MVP|3|validation|开发期确定方向/参数/预处理/期限，最终Test封存与访问审计|预注册协议和访问身份|冻结配置及测试记录|VALID-003;EXP-002|反复Test调参被识别为污染，不能继续宣称独立|RESEARCH_PROTOCOL.md
VALID-005|V3.0§6.1;V3.0§6.5|MVP|3|validation|显著性/自相关/重叠期限稳健SE或预注册替代法|IC序列和依赖假设|SE/p/不确定性|VALID-001|不把ICIR当t值，假设不满足明确拒绝|RESEARCH_PROTOCOL.md
VALID-006|V3.0§6.4;V3.1§4|MVP|3|validation|记录全部候选/参数/淘汰/筛选/验证访问次数与重复试验|所有实验及family|搜索路径及overfit风险|EXP-002;VALID-004|不能只保留赢家或重命名Test，重复指纹可查|RESEARCH_PROTOCOL.md
VALID-007|V3.0§6.4;V3.1§4|MVP|3|validation|多重假设family及Holm/BY/BH适用性和校正记录|原始p及预注册m|校正p和风险说明|VALID-005;VALID-006|计入全部假设，依赖/自适应限制披露|RESEARCH_PROTOCOL.md
VALID-008|V3.0§6.5;V3.1§4|MVP|3|validation|批准前记录预定标准及实际验证，不以正IC批准|冻结标准/独立OOS证据|ResearchValidated提案|VALID-004;VALID-007|阈值未批准或证据不齐不可正式批准，交易适用待P5|RESEARCH_PROTOCOL.md
PORT-001|V3.0§7.1|MVP|4|portfolio|因子无关组合输入和目标权重/仓位/调仓建议及诊断|已批准分数/股票池/账户/权益/暴露|TargetPortfolio|FACTOR-009;VALID-008|不依赖具体因子名称，不修改账本|INTERFACES.md
PORT-002|V3.0§7.2;V3.0§3.4|MVP|4|portfolio|单/多因子组合、等权/分数权、LongOnly|分数和权重规则|合法目标及残余现金|PORT-001|零分/负分/整手余数有定义，权重守恒|INTERFACES.md
PORT-003|V3.0§7.2;V3.0§18|Competition Ready|4|portfolio|LongShort组合及gross/net分别控制|多空权限及分数|多空目标|PORT-001;RISK-003|不得用long-only冒充多空，P5另测真实模拟约束|INTERFACES.md
PORT-004|V3.0§7.2|Advanced Research|POST7|portfolio|优化算法扩展|批准的约束/优化方案|优化目标|PORT-001;INT-004|代价/兼容/迁移评审后另行授权|ROADMAP.md
RISK-001|V3.0§7.3|MVP|4|risk|单票/总敞口/净敞口/杠杆/换手限制|目标账户/配置|逐项风险诊断|PORT-001|等号/越界/冲突约束测试，不静默放宽|INTERFACES.md
RISK-002|V3.0§7.3|Competition Ready|4|risk|行业与Beta暴露限制|PIT暴露及目标|合规或拒绝|PORT-001;DATA-012|缺暴露不视为0，容差明确|INTERFACES.md
RISK-003|V3.0§7.3|Competition Ready|4|risk|可交易性/空头许可/借券/可售数量检查|市场profile/状态/账户|交易资格诊断|PORT-001;DATA-005|停牌/借券不足显式拒绝，P5提交撮合再检查|INTERFACES.md
RISK-004|V3.0§7.3;V3.0§11.2|MVP|4|risk|风险拒单及不可行组合显式错误，不可绕过|候选目标/订单|RiskDecision/reason|RISK-001|调用方不能强制忽略拒绝；实际订单接线P5测|INTERFACES.md
BT-001|V3.0§8.1;V3.1§3|MVP|5|backtest|独立Market/Signal/Decision/Order/Fill/Account/Valuation事件状态机|有序事件及causation|确定性事件流|PORT-001;RISK-004;DATA-002|P0契约在P5自动验证，逐笔Fill/账户原子配对|BACKTEST_CONTRACT.md
BT-002|V3.0§8.2;V3.1§3|MVP|5|backtest|收盘后信号、next session最早开盘，available/decision/submission/eligible/fill约束|可用数据及日历|合法可执行订单|BT-001|不可用前无订单，延迟错过开盘不得倒填|BACKTEST_CONTRACT.md
BT-003|V3.0§8.3|MVP|5|execution|创建/状态/成交/部分成交/拒绝/取消/到期与幂等|订单和执行切片|Fill/状态记录|BT-002;RISK-004|非法终态拒绝，累计数量守恒，重试不重复成交|BACKTEST_CONTRACT.md
BT-004|V3.0§8.2;V3.0§8.3|MVP|5|execution|费用/滑点/流动性/停牌与开盘可交易模型|批准profile和历史可见容量|现实假设模拟Fill|BT-003|无日终量泄漏，不能无条件全额理想成交|BACKTEST_CONTRACT.md
BT-005|V3.0§8.4;V3.0§10.3;V3.1§3|MVP|5|backtest|现金/持仓/成本/费用/现金流/已实现未实现/权益账本及原始重建|Fill/现金流/账户初态|Journal/AccountState|BT-003;DATA-011|799/210/1009独立核对，买卖部分成交边界性质均测|BACKTEST_CONTRACT.md
BT-006|V3.0§2.1;V3.0§8.4;V3.0§10.3|Competition Ready|5|backtest|行动/分红应收支付/拆股/交收/退市估值|行动/市场profile/持仓|资金和证券变动|BT-005;DATA-004;DATA-005|行动不双计，碎股/税务/停退市未知明确阻断|BACKTEST_CONTRACT.md
BT-007|V3.0§8.4;V3.0§10.3|Competition Ready|5|backtest|空头、融资/借券费、保证金与股息应付|已批准多空profile|多空账本和费用|BT-005;PORT-003;RISK-003|独立空头答案+边界/性质，缺规则Unsupported不假装通过|BACKTEST_CONTRACT.md
BT-008|V3.0§8.4;V3.0§8.5|MVP|5|performance|估值/权益/每日持仓现金/风险暴露/订单成交报告|账本及RAW marks|账户与策略报告|BT-005|权益独立对账，stale/缺估值明确披露|BACKTEST_CONTRACT.md
BT-009|V3.0§8.5|MVP|5|performance|累计/年化/波动/Sharpe/MDD/换手/费用/净收益/多空贡献|日权益收益/费用及约定|统一绩效指标|BT-008|A/ddof/rf/现金流/换手定义明确，费用不双扣|BACKTEST_CONTRACT.md
BT-010|V3.1§1;V3.0§3.6;V3.0§12.2|MVP|5|backtest|P5因子替换后完整组合/风险/撮合/账本流程|固定模拟配置及两因子|回测替换证据|BT-009;FACTOR-004;FACTOR-005|只改因子配置，核心hash未变，独立订单/资金答案正确|TESTING.md
UI-001|V3.0§9.1|MVP|6|ui|Dashboard状态/因子数/任务/最近研究回测/错误警告|应用服务结果|状态页面|BT-009;RESEARCH-001|真实任务状态，不伪造成功/数量|INTERFACES.md
UI-002|V3.0§9.2;V3.0§3.5|Competition Ready|6|ui|FactorLibrary列表详情/版本参数/选择状态/比较/增删配置权重回滚|Registry及请求配置|因子管理页面|FACTOR-010;UI-001|精确版本和审批可见，无网页任意Python执行|INTERFACES.md
UI-003|V3.0§9.3|MVP|6|ui|AlphaResearch选择股票池/因子/区间/期限，IC/Rank/ICIR/分层/衰减/OOS展示|ResearchRequest|研究页面|RESEARCH-009;UI-001|展示后端原始产物不私改统计，缺项明确|INTERFACES.md
UI-004|V3.0§9.4|MVP|6|ui|StrategyBacktest选批准因子/权重/仓位/风险/成本，收益回撤订单Fill持仓|BacktestRequest|回测页面|BT-010;UI-001|候选因子禁止策略调用，结果来自统一服务|INTERFACES.md
UI-005|V3.0§9.5|Competition Ready|6|ui|ExperimentManager查询/版本参数比较/数据版本/报告/复现|run_id及索引|实验页面|EXP-003;UI-001|历史不可覆盖，差异及不可复现原因展示|INTERFACES.md
UI-006|V3.0§9.6|Competition Ready|6|ui|Settings数据源/默认参数/费用/风险/依赖信息/日志|经校验设置|新配置及可见日志|UI-001;ENV-001|只影响新任务，不改已封存实验，敏感值不泄露|INTERFACES.md
UI-007|V3.0§9.7;V3.1§1|MVP|6|ui|CLI/服务/网页因子选择和研究/回测同配置同核一致|同canonical配置/数据/版本|一致性比对证据|UI-002;UI-003;UI-004|config_hash和数值相同，允许run_id/墙钟不同|TESTING.md
UI-008|V3.0§9;V3.0§18;V3.0§2.1|MVP|6|services|任务提交/状态/取消/错误日志/图表报告，算法不在页面重写|统一RunRequest|RunReceipt/TaskState/Artifact|UI-001;EXP-001|失败取消不标SUCCEEDED，幂等重试不重复任务|INTERFACES.md
EXP-001|V3.0§13;V3.1§7|MVP|3|experiments|唯一run_id和不可变配置，代码/数据/因子/参数/股票池/split/seed/环境/规则成本/时间/日志/失败|完整运行配置与血缘|append-only RunRecord|DATA-007;FACTOR-003|所有指定字段完整，封存后修改被拒，不覆盖历史|INTERFACES.md
EXP-002|V3.0§6.4;V3.0§13;V3.1§4|MVP|3|experiments|全部参数候选/淘汰与验证访问次数及重复指纹|每次研究调用|实验搜索ledger|EXP-001|失败实验留痕，赢家选择可反查|RESEARCH_PROTOCOL.md
EXP-003|V3.0§13;V3.0§9.5|MVP|3|experiments|版本差异比较/复现与不可复现原因|固定run与工件|差异报告或重放任务|EXP-001|缺hash/脏代码不冒充正式复现，旧结果不改写|INTERFACES.md
EXP-004|V3.1§4;V3.1§7|MVP|3|experiments|批准因子时预设标准/冻结时间/实际证据/审批者|ApprovalProposal与审核记录|可验证批准记录|VALID-008;EXP-001|候选变更必须新版本再验证，P5后才可策略批准|RESEARCH_PROTOCOL.md
ENV-001|V3.0§18;V3.1§7|MVP|1|environment|精确Python及直接传递依赖/哈希/平台环境固定|批准环境选型|锁文件及环境清单|GOV-004|P1干净安装可复现，升级经评审；P0不得称已锁定|ENVIRONMENT_AND_SECURITY.md
ENV-002|V3.0§11.4|MVP|1|environment|开始正式代码即建Actions安装/格式静态/单元集成回归/报告|固定依赖及适用测试|可信CI证据|ENV-001|关键失败阻断，外部PR无秘密/写权限执行|ENVIRONMENT_AND_SECURITY.md
ENV-003|V3.0§11.3|MVP|0|environment|风险分层覆盖率目标，不能代替数学答案|模块风险|覆盖率与案例门槛|ARCH-001|金融关键行95/分支90等目标明确并待批准|TESTING.md
SEC-001|V3.0§3.3;V3.0§9.2;V3.0§20;V3.1§7;V3.2§3|MVP|2|security|新因子审查后才入批准环境，隔离最小权限/不可信代码禁执行|代码hash/审查证据|允许列表与受限测试|ENV-001|Candidate不获账户/网络权限，AST检查不当安全边界|ENVIRONMENT_AND_SECURITY.md
SEC-002|V3.0§20;V3.1§7;V3.2§3|MVP|1|security|禁止提交真实密钥、凭证隔离与日志脱敏/提交CI扫描|源码配置日志|无秘密工件|ENV-001|扫描与人工核查，无真实交易凭证进入测试|ENVIRONMENT_AND_SECURITY.md
SEC-003|V3.0§20;V3.1§7;V3.1§5|Production Extensions|POST7|security|真实账户/真实订单及生产权限隔离|另行明确授权|未来真实执行能力|INT-004|当前Unsupported，不因比赛适配或研究自动开放|ENVIRONMENT_AND_SECURITY.md
SEC-004|V3.2§1;V3.2§3;V3.2§8|MVP|0|security|Gemini初始只读，独立测试分支/执行须授权，GPT保留原审计|用户权限和原报告|权限/审查记录|GOV-008|不代写或篡改Gemini结论，不代用户批准|ACCEPTANCE.md
QA-001|V3.0§10.1;V3.0§10.2;V3.0§10.3;V3.1§6|MVP|0|quality|Golden设计覆盖收益/因子/IC/Rank/ICIR/排名标准化/权重/费用账本/MDD/卖出部分空头分红异常|独立手算/参考|输入答案依据容差核验方案|ARCH-003|不调用待测函数生成答案，Gemini/人工核对状态明确|GOLDEN_DATASET.md
QA-002|V3.0§10.4;V3.0§11.1;V3.1§6|MVP|1|quality|单元/契约/集成/回归/E2E/泄漏/性质/必要性能测试按阶段实施|需求与独立预期|实际适用测试报告|QA-001;DATA-008|关键数学和资金同时有边界性质独立参考，未来测试仅Planned|TESTING.md
QA-003|V3.0§11.2;V3.1§3|MVP|5|quality|10项核心不变量及完整事件/资金独立对账自动测试|原始事件和独立答案|不变量与已知答案证据|BT-009;QA-002|费用守恒/合法状态/风险/无未来/复现/批准/同核逐项适用验证|TESTING.md
QA-004|V3.0§10.4;V3.1§6;V3.2§1|MVP|3|quality|Gemini独立建立/核对Golden，人工复算关键金融数学|输入公式及原始参考|核验者/日期/证据|QA-001;VALID-001|GPT手算不标独立审查完成，修答案走缺陷版本|GOLDEN_DATASET.md
QA-005|V3.1§8|MVP|0|quality|六项专项审计及原V3.0覆盖/架构评审|需求与契约|专项检查和架构报告|GOV-003;ARCH-003;QA-001|与追踪矩阵一致，未知/冲突明确列出|audits/phase-0/SPECIAL_AUDITS.md
QA-006|V3.2§5;V3.2§6|MVP|0|quality|ReviewPackage15项及真实命令/日志/CI/Golden/缺项证据|固定SHA和实际工件|可核实资料包|GOV-008|无实际证据不称通过，空字段和未来项如实标示|audits/phase-0/REVIEW_PACKAGE.md
QA-007|V3.0§16;V3.0§19;V3.2§4;V3.2§6|MVP|0|quality|独立审查适用范围与运行限制、阻断闭环后人工验收|Gemini报告/修复SHA|人工验收申请|GOV-008;GOV-009|CI不代Gemini，Gemini不代用户，未运行不报运行级审计|ACCEPTANCE.md
INT-001|V3.0§12.1;V3.1§1|MVP|3|integration|加载数据→股票池→因子→预处理→IC/分层/OOS→报告→实验|研究请求|完整研究运行|RESEARCH-009;VALID-003;EXP-001|P3真实研究E2E，数据/版本/失败全留痕|TESTING.md
INT-002|V3.0§12.2;V3.1§1|MVP|5|integration|批准因子→信号→组合→风险→订单→撮合→账户→净值→绩效|回测请求|完整策略运行|BT-010;INT-001|各步骤真实可执行，成本后证据才授策略批准|TESTING.md
INT-003|V3.0§12.3;V3.0§11.2|MVP|7|integration|Research/Strategy状态与版本隔离|候选变更与固定策略配置|互不污染证据|INT-002;UI-007|候选代码/参数修改不影响策略pin及历史实验|TESTING.md
INT-004|V3.0§12.4;V3.0§18|MVP|7|integration|全新环境源代码/锁依赖/数据/测试/CLI研究回测/网页执行数值比对/手册部署证据|已审查全模块及干净环境|部署及最终运行验收报告|INT-003;ENV-002|全部实际运行留日志，不以UI启动代完整部署|TESTING.md
INT-005|V3.0§3.6;V3.1§1;V3.2§7|MVP|7|integration|固定快照和组合回测配置Momentum→Reversal完整替换/全回归|固定SHA/数据/配置|全链兼容与正确性证据|INT-004;FACTOR-011;RESEARCH-009;BT-010;UI-007|仅改因子配置且核心不变，信号订单按独立预期变化|TESTING.md
INT-006|V3.0§1.2;V3.0§2.3;V3.0§18;V3.1§5|Competition Ready|7|competition|比赛执行/数据规则适配及通用模拟能力声明|正式比赛规则|适配器/规则测试/能力清单|INT-002|未知规则明确外部阻断，不声称具体比赛验收通过|INTERFACES.md
EXT-001|V3.0§18;V3.0§1.2|Advanced Research|POST7|extension|GPT候选生成/公式检查/批评估/去重/稳健筛选/排序/审批|独立新阶段授权|默认Candidate的候选池|INT-004;FACTOR-008|无代码审查自动测试OOS不得进入正式策略|ROADMAP.md
""".strip()

def build():
    fields = ['id','source','tier','phase','module','definition','input','output','dependencies','acceptance','design','priority','planned_code','planned_test','capability_status','design_status']
    rows = []
    for line in DATA.splitlines():
        parts = line.split('|')
        assert len(parts) == 11, line
        r = dict(zip(fields[:11], parts))
        r['priority'] = 'P2' if r['phase'] == 'POST7' else 'P0' if r['module'] in {'governance','architecture','security','quality'} else 'P1'
        locations = {'environment': 'pyproject.toml;requirements.lock;.github/workflows/ci.yml',
                     'quality': 'tests/（对应模块）',
                     'security': 'src/aqrp/core/security/',
                     'integration': 'src/aqrp/services/;tests/integration/;tests/e2e/',
                     'extension': '后续单独批准的扩展模块（尚未选型）'}
        r['planned_code'] = 'docs/' + r['design'] if r['phase'] == '0' else locations.get(r['module'], 'src/aqrp/' + r['module'] + '/')
        r['planned_test'] = 'docs/audits/phase-0/' if r['phase'] == '0' else 'tests/' + r['module'] + '/test_' + r['id'].lower().replace('-','_') + '.py'
        r['capability_status'] = 'Unsupported' if r['id'] == 'SEC-003' else 'Deferred' if r['phase'] == 'POST7' else 'Planned'
        r['design_status'] = 'DRAFT_PRESENT'
        rows.append(r)
    ids = {r['id'] for r in rows}
    assert len(ids) == len(rows)
    for r in rows:
        for dep in r['dependencies'].split(';'):
            assert dep == 'NONE' or dep in ids, (r['id'], dep)
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    (ROOT/'docs/requirements.csv').write_text(out.getvalue(), encoding='utf-8', newline='\n')
    md = ['# 正式需求清单 V3.2（待审）', '', f'共 {len(rows)} 条编号需求，规范源表为 `requirements.csv`；本文件由同目录审计编制工具生成。每条均保留输入、输出、来源、优先级、模块、阶段、等级、依赖、验收、设计及未来代码/测试位置。', '',
          '设计状态 DRAFT_PRESENT 只指设计已编写；能力状态 Planned/Deferred/Unsupported 均表示尚未实现。所有未来代码/测试路径是规划位置，不是现有文件。Phase 0 治理/设计实际文件由交付清单核实，执行强制控制仍未实施。', '',
          '等级：MVP / Competition Ready / Advanced Research / Production Extensions。优先级 P0 为不可降级治理或关键质量要求，P1 为指定阶段功能，P2 为后续扩展；不能因等级或优先级擅自延期原V3.0必须项。POST7 仅可在核心P7后另行授权。', '',
          '通过标准均为待审提案；实际数值的业务门槛待 DECISIONS 批准。批准状态变更须附证据而不能直接改表。来源 `§18` 为原文阶段计划，V3.2 `§4.x` 为对应Step。', '']
    for r in rows:
        md += [f"## {r['id']} · {r['definition']}", '',
          f"- 来源：{r['source']}；等级：{r['tier']}；阶段：{r['phase']}；优先级：{r['priority']}；模块：{r['module']}。",
          f"- 输入：{r['input']}。输出：{r['output']}。依赖：{r['dependencies']}。",
          f"- 验收：{r['acceptance']}。",
          f"- 设计：[契约/方案]({r['design']})；拟代码：`{r['planned_code']}`；拟测试：`{r['planned_test']}`。",
          f"- 能力状态：{r['capability_status']}；设计状态：{r['design_status']}；实际实现/测试证据：尚无（P0文档证据另见审查包）。", '']
    (ROOT/'docs/REQUIREMENTS.md').write_text('\n'.join(md), encoding='utf-8', newline='\n')
    trace = ['# 双向需求追踪矩阵（待审）', '', '源要求→需求ID→设计/未来实现→分阶段测试；实际实现后须把规划路径替换/补充为真实文件、测试ID、Commit及证据。空缺不能当已实现。需求的完整输入输出/验收定义见 REQUIREMENTS 和 requirements.csv。', '',
      '| ID | 来源 | 等级/阶段 | 前提需求 | 设计 | 未来代码 / 测试 | 状态 |', '|---|---|---|---|---|---|---|']
    for r in rows:
        trace.append(f"| {r['id']} | {r['source']} | {r['tier']} / {r['phase']} | {r['dependencies']} | [{r['design']}]({r['design']}) | `{r['planned_code']}` / `{r['planned_test']}` | {r['capability_status']}，设计待审 |")
    src = {}
    for r in rows:
        for s in r['source'].split(';'):
            src.setdefault(s,[]).append(r['id'])
    trace += ['', '## 来源反查索引', '', '分组需求的 definition 明列子能力；本索引是节覆盖证据，不能单凭“节已映射”证明语义无遗漏，仍须 Gemini 对原文逐项审读。V3.1专项要求全部保留在契约和审计。', '', '| 原文条款 | 需求ID |','|---|---|']
    trace += [f"| {s} | {', '.join(v)} |" for s,v in sorted(src.items())]
    trace += ['', '## 实际文件反向追踪', '', '| 已创建文件类别 | 授权需求 |', '|---|---|',
      '| AGENTS、README、章程、进度、决策、变更 | GOV-001–009 |',
      '| REQUIREMENTS、requirements.csv、TRACEABILITY、编制工具 | GOV-003 |',
      '| ARCHITECTURE、INTERFACES、DATA_CONTRACT、BACKTEST_CONTRACT | ARCH-001–003，DATA-001–013，FACTOR-001–012，PORT-001–004，RISK-001–004，BT-001–010 |',
      '| RESEARCH_PROTOCOL、GOLDEN_DATASET | RESEARCH-001–009，VALID-001–008，QA-001–004 |',
      '| ROADMAP、ACCEPTANCE、TESTING、ENVIRONMENT_AND_SECURITY | GOV-004–009，ENV-001–003，SEC-001–004，QA-001–007 |',
      '| docs/sources、audits/phase-0与templates、文档核查工具/证据 | GOV-003，GOV-008，QA-005–007 |',
      '| tests/golden、integration、e2e说明 | GOV-002，QA-001–002，INT-001–005 |',
      '| .gitignore | SEC-002（辅助措施，非已完成秘密扫描） |',
      '| .gitattributes | DATA-007，EXP-001（固定字节避免检出换行转换破坏hash） |', '',
      'P0文件的精确列表/hash以审查包 MANIFEST.json 为准。源文件、作者工具和自查不是独立审计；任何新增业务模块必须有已批准需求，当前不存在业务实现。']
    (ROOT/'docs/TRACEABILITY.md').write_text('\n'.join(trace)+'\n', encoding='utf-8', newline='\n')
    return rows

if __name__ == '__main__':
    print(f'Generated {len(build())} requirements and traceability records.')
