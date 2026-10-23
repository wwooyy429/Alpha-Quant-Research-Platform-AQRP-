# Phase5 包版本及基线兼容影响

当前0.5.0.dev3增补：[003处理](g2-35f93d6/DEVELOPER_RESPONSE.md)、[输出/恢复元数据](g2-35f93d6/OUTPUT_CONTRACT_ERRATA.md)、[独立复核入口](g2-35f93d6/REVIEW_PACKAGE.md)。固定35f93d6原001/002已独立关闭，新003 High仍OPEN，整体BLOCKED；以下旧状态/旧候选说明保留历史，不代替本轮固定版本验证。


当前0.5.0.dev2修复勘误以[g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md](g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md)及[修复复核入口](g2-bfdcf30/REVIEW_PACKAGE.md)为准：原bfdcf30独立G2为BLOCKED，两项仍待新固定版本独立确认；以下原实施说明及正确经济口径保留，不把旧PENDING或正常SDK通过改称G2通过。


用户已单独授权十二项工程实现。候选包版本0.5.0.dev1，新增backtest/execution/performance及薄服务/CLI，不是已发布版本。依赖锁、Python3.13.16、既有因子实现、P1/P3/P4金融源码/API/测试答案及冻结P0文件保持。历史main/phase4-baseline/v0.4.0保留32ea5d6b75c84c07017d87377eeabd2f78207c5c；旧标签不移动。

G1的FROZEN_INPUTS.json记录的是实施前131项字节身份，原件不重写。本阶段必须改变下列七个包装/验证文件，实际旧/新SHA由IMPLEMENTATION_IDENTITY.json逐项记录，其余124项仍严格核对。P4原3440项保留清单中仅三个对应CI/覆盖工具文件有明确升级；其余3437项原字节严格核对。若出现额外改动，checker失败；不能用重生成预期表掩盖金融源码差异。

| 文件 | 必要变化 |
|---|---|
| pyproject.toml | 0.5.0.dev1与aqrp-backtest薄入口，不新增/升级依赖 |
| src/aqrp/__init__.py | 与已安装候选版本一致 |
| tests/environment/test_installation.py | 仅改版本身份断言；金融答案/容差不动 |
| src/aqrp/factors/reviewed_code.json | 新完整host源码包Hash及开发方工程审查记录；不是独立G2或金融批准 |
| tools/ci.py | 新P5检查、真实回测smoke/标准库参考及原始失败工件采集；既有SDK/旧Ref/原20+四/91与其他smoke保留 |
| tools/check_coverage.py | 新增P5关键模块95%行/90%分支门槛，原门槛不降低、不加排除 |
| .github/workflows/ci.yml | Phase5双OS命名和回测/失败目录原始工件；固定action版本不改 |

旧tools/check_phase4_package.py原字节保留，它针对P4明确禁止backtest包且绑定当时53模块Hash，不能作为P5当前包的身份判定。新tools/check_phase5_package.py继承原保护清单并逐项落实上述明确变化、新包身份、全十二项需求、十二份G1设计身份及无broker/UI的边界。旧P4严格检查已在实施前通过，原日志保留；这不是删除金融检查、降低门槛或改旧答案。

因子Ref的implementation_hash按既定协议绑定整个软件包，新host包增加模块后Ref的bundle Hash随之改变。四个内置因子源码和算法未改；旧Ref仍要求精确旧软件包执行，沿用既有原wheel/锁/重放环境，不把新实现静默绑定旧Ref。P5还实际消费受信原P3终态信号，绑定其旧Ref/参数/阶段/P1父身份，不以名称重新算旧因子。完整历史OS宿主仍未验证。

本轮不集成独立PR7的Windows候选6207450，原WI-R2两项维持延期。工程hash收据是包内准入和开发方自查身份，不能改称GPT Work G2 PASS、真实三主体隔离、金融批准或真实Test许可。
