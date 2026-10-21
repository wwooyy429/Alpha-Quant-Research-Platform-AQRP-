# 数学补充件开发方执行记录

本目录是Codex开发方静态阅读/实际复跑/独立正确公式核对，非Gemini新执行或完整SDK。原始用户文件位于../gemini/math-supplement/，原件不改；checks.json记录真实参数、环境、输出hash和返回码。

developer-replay.stdout.log/stderr.log为原脚本-I -S隔离路径执行的真实输出。返回0且与所供日志统一换行后相符，但Volume缺-1，证券B不从输入推导，没有hash/ZIP/SDK验证，所以不能用返回0证明正式因子通过。

check_supplement_executed.py是实际核对源，保留当时绝对路径和干净入站79c91e4前置条件；如需复验，在独立副本适配路径，不覆盖原证据。标准库Fraction另核正式G-P2-A/B，未调用因子函数生成期望值。

新FILE_MANIFEST只覆盖本轮可交付文件并排除自身，旧manifest为对应历史快照。未获人工验收或合并/标签/P3授权。
