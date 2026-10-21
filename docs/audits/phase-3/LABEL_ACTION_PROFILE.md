# SYNTHETIC_V1_LABEL_1：行动、持有及可用时间提案

对应WORK-P3-002、VALID-001/002/003、QA-004、INT-001。**新P3侧车标签profile待独立复算及用户经济假设确认**，不修改P1 `SYNTHETIC_V1`/8表或其total_return/action_view，不把下述研究权益算法作为P5账户账本。原15组Golden字节保持；旧4%仍只是有资格时的算术。

时间使用UTC微秒，日历为显式session表（候选例2026-01-05/06/07/08，open09:00Z、close16:00Z，无市场推定）。signal session t确认收盘之后；entry=next scheduled session open，exit=entry之后h个scheduled session open，h>=1。入场时持有0→1股，以RAW entry open计初始分母，不回填调整价格；无借券/手续费/税/红利再投。RAW价正有限且单位/币种相同，停牌/缺价/未支持退市给null+reason。仅支持明确合成拆股及现金红利，其他行动/未知资格/外币返回UNSUPPORTED，不声称符合真实市场规则。

同一有效时点顺序：①该时点全部拆股按action_id确定排序，更新已有股数；②确认该时点现金红利资格/应收；③若为entry则买1股；④若为exit则以RAW open卖出全部持有股数；⑤支付仅把已有应收转现金不改变净权益。入场无既有权益，因此action_time==entry不享受旧股拆股或红利；exit同刻仍持有到行动处理后，享受权益后退出。资格区间为 **(entry_time, exit_time]**；1微秒前/后按比较结果，而非日期模糊判断。record_date仅合成信息不作另一个持股判据；ex_date必须匹配effective_at日历日期；pay_date>=ex_date，无支付时点时只报告应收+已付合计credit，不猜日内支付顺序。支付晚于exit仍纳入有资格的应收。后续支付不重复记收益；未知税/违约/支付金额规则不支持。

P1 dividend_basis始终 `PER_OLD_SHARE`，本profile明确old share锚定到action所属session的前一scheduled close的股数单位；不改原字段为POST_SPLIT。`R_anchor_to_action`为该锚点之后到本行动（含同刻①拆股）的累计拆股倍数，`cash_per_current_share = cash_per_share_old / R_anchor_to_action`。已有n_current股确认credit=n_current*cash_per_current_share。同刻2:1拆股、旧单位红利2：1→2股，每现股1、总credit2。原15组postsplit1案例的独立转换是P1 cash_per_share_old=2。入场已在拆股后时初始1股仍通过同一锚点比率转换。每一close锚点重新计比率；已在先前session完成的拆股不可再除一次。沿用P1一个close区间内多个不同有效拆股时点不支持的边界，返回UNSUPPORTED_ACTION_CHAIN；不能把多次拆股错误相乘后声称通过原接口。所有依赖锚点/session及行动版本写血缘。

信息可用不等于经济有效时点：P1日bar的open虽标记09:00，整行event_time为16:00、available_at>=16:00；标签不能因exit open已发生就提前读取该行。每个label冻结evaluation_cutoff，对RAW bar/action/PIT sidecar先event/available双过滤再选可见revision，保留所有使用的revision/原字节hash。`label_available_at=max(all dependency event_time/available_at, action-coverage watermark available_at)`（synthetic计算延迟显式0；有延迟则另加），依赖包括entry/exit完整bar、所有相关anchor/calendar/行动、及覆盖声明。

保管者另签独立 `LabelCoverageRef`，声明actions_complete_through>=exit、as_of版本/修订与source身份；它不是向原8表加列。无coverage或晚到行动尚未可见时不能把“当前看不到”当没有行动，返回UNKNOWN_ACTION_COVERAGE/NOT_YET_AVAILABLE，收益/股数/credit及label_available_at均为null；不能从尚未可见的依赖反推未来发布时间。候选中oracle_only时点只供独立答案核对，不是当时API可返回信息。修订仅在新evaluation_cutoff可见时用新label_ref/new run；旧label/artifact不覆盖。历史拟合不能引用后来才可见的修订，即使label的价格终点在Train内。

输出分别记录：price holding闭区间[entry,exit]；entitlement开闭区间(entry,exit]；information closed interval **[signal_decision_time,label_available_at]**。purge使用information interval与heldout保护interval闭区间交集，接触也删除，比只看持有期更保守；embargo保持预注册session网格。跨期Train拟合须label_available_at<=fit_cutoff且signal/dependencies/fit rows在Train许可范围，未来1微秒拒绝；当日截面z/OLS只读当日decision可见score/exposure，不能借label可用条件放宽。

新增手工候选见supplemental_cases.json：entry/exit同刻拆股/分红、两端±1微秒、PER_OLD_SHARE转换、次日锚点重置、晚到/修订、付款晚于退出、bar直到close可见、label fit截止±1微秒以及purge闭接触。每例给股数、credit/应收+已付、收益及label_available_at；纯算术参考不冒充真实PIT实现测试。Formal Test中的完整原始行动和coverage只在隔离评估端，不能从研究侧读取未来行。

## e26补充：自包含可用时间候选v2

原supplemental_cases.json/脚本/log保持。新label_visibility_v2.json逐例显式给entry/exit/anchor/calendar、每个action的announcement_at=event_time、available_at、effective_at、原P1单位/修订以及coverage版本/event/available/complete_through/状态。所有时间在JSON，不在参考程序填默认；这是合成输入片段与侧车证据设计，不冒充已提交P1八表快照或真实签名。保管者签名状态PROPOSED_UNSIGNED，正式路径拒绝。新增边界覆盖最后水位后1微秒，原可用时间答案在补全前提下不改。经济口径仍待USER_DECISIONS中U-002明确确认。
