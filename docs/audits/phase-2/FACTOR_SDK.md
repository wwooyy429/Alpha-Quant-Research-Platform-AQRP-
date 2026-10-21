# Phase 2 Factor SDK（0.2.0）

适用：CPython3.13.16标准GIL/x64、固定requirements.lock、仅合成数据工程测试。安装精确版本构建的wheel；现有Conda aqrp-p1若仍装0.1.0不代表已安装本SDK。完整验证由该环境启动tools/ci.py，内部新建干净venv并安装0.2.0 wheel。本次真实命令及安装路径见implementation/local/commands.log、environment.json和driver.log。

## 正式调用

已取得P1 SnapshotRef后，先用固定受审内置构造spec并注册；不接受外部module/path/URL/factory。

```python
from datetime import date
from aqrp.core.contracts import QuerySpec
from aqrp.factors import FactorEngine, FactorRegistry, builtin_spec, write_run

registry = FactorRegistry()
spec = builtin_spec("momentum")
registry.register(
    spec.implementation_version, spec,
    actor="developer", reason="reviewed builtin engineering test",
    evidence=spec.review_ref,
)
request = QuerySpec(
    ("SYN_A:001",), "SYN_A", "SYN_A_CAL",
    (date(2024, 1, 2), date(2024, 1, 4)),
    ("close", "volume"), "split_adjusted",
)
batch = FactorEngine(registry).run(
    spec.ref, request, "2024-01-04T12:05:00Z", snapshot_ref,
    parameters={"lookback": 2}, mode="test",
)
run_path = write_run(batch, output_root, registry)
```

示例依赖与tools/factor_smoke.py相同的三日合成快照。可调用的完整造数/发布/三因子示例即该文件；工程回放命令为 `python tools/factor_smoke.py <新建的输出目录>`，须先安装本版SDK及锁定依赖。不是CLI产品或UI功能。SDK写新UUID运行目录，已有目录拒绝覆盖；调用者传入run_id/computation_id必须标准UUID。异常可通过engine.write_failure持久化FAILED，runner不会吞异常伪造成功，调用方负责捕获并保存失败receipt。

## 语义与限制

- Protocol是compute(view,context)。三内置momentum/reversal/volume，版本1.0.0；spec.ref包含exact版本与完整代码bundle hash。默认lookback20，1..252严格整数，bool/未知参数/非有限数拒绝。区间仅支持>=x.y.z,<u.v.w；不接受latest/prerelease/build。
- 价格/量均复用P1 split_adjusted。每证券目标日及之前连续L个可见session；Momentum=P[t]/P[t-L]-1；Reversal为其负值；Volume=V[t]/mean(V[t-L:t])-1，分母不含当期。历史均量0无效，当期0而历史均量正得-1。
- host在每个decision_time调用P1 query并核验快照/日历/字段；不用未来cutoff批量回算过去。available_at保守取decision_time；logical_compute_delay=0仅是明确合成假设。缺历史/缺目标/缺口/坏quality输出null+invalid_reason，schema/hash/上下文错误抛ContractError。
- 运行固定精确ref与不可变配置。deactivate禁止新resolve，旧pin仍可算；emergency=True显式阻断旧pin；rollback只选择已登记兼容且获工程准入的旧ref，保留事件。requested_weight只接受有限Decimal元数据，不加权或生成组合。
- Registry在单进程内append-only记录，events随每次write_run落盘；未实现跨进程持久目录服务。配置、signals、events分别hash，manifest保留runtime和全量/逻辑hash。逻辑hash排除随机run/computation/snapshot标识，用于跨OS值比较；全量hash保留真实血缘，不能强行相等。
- ENGINEERING_APPROVED / TEST_ONLY / financial_approval=NONE。receipt由受信随库策略保存，开发方审查不等于Gemini独立批准，也不是密码学签名。bundle覆盖全部aqrp源码和锁身份；receipt自身不递归hash，Git固定版本与审查证据提供追踪。
- 静态AST是辅助lint，不是OS沙箱。同权限恶意维护者、反射和原生扩展不在其防护声明内；外部不可信插件、研究/策略/真实订单模式Unsupported。未新增真实源、金融研究、组合、回测或网页。
