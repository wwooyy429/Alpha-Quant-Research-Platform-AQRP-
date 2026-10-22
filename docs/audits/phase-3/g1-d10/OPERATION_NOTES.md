# 开发方归档过程记录

首次暂存区差异检查exit2：原报告/JSON含原生CRLF或重复CR，开发方raw stdout亦有Windows CRLF，被Git按行尾空白报告。没有业务测试失败，未执行commit/push。首次完整输出保留git-diff-initial.log，未删记录。

采用phase-3/.gitattributes中仅限g1-d10原始证据及supplemental_reference.log的行尾检查规则；不改变原件字节、不归一化、不关闭设计/业务代码的普通差异检查。最终重新执行暂存区检查并核manifest。该调整不是隐藏实际金融/数学或业务测试失败。

首次commit尝试exit128：当前副本未配置Git author identity（Author identity unknown），未产生提交。核实既有d10/f262/e50的开发方身份均为Codex <codex@localhost>，后续仅在单次commit参数中沿用该开发方身份，不写全局用户配置、不使用人类审批者身份。此为Git操作环境错误，不是项目测试失败。
