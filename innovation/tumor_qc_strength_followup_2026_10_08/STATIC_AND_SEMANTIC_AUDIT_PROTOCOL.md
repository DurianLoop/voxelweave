# 非医学CPU审计的事前范围

不执行/import作者代码，也不假装复现其网络。已实际读固定commit e9ddc2418c72cc1c20b69bd3074b7f96b8b5f408的README、utils、dataloading、main全文。作者losses.py在公开根清单中未见，指标生成CSV和完整pipeline未核实；本轮不推断论文结果错误。

用标准库AST和inspect.Signature审计两个RegDataLoaderV1调用的参数绑定、README示例arch与argparse选择、局部单scalar/单二值SEM接口；只查读取的文件，不宣称全repo缺少其他实现。另以标准库穷举四解剖标签（background/edema/core/enhancing）之间16个有序GT/query组合，检查WT/TC/ET嵌套区域的XOR错误是否仍嵌套，以及Appendix D可视化式重新解码是否等价；只解释标签代数和可视化，不能把它当患者性能。

同时穷举二值query/GT四组合，独立检查E=P XOR GT、FP=E AND P、FN=E AND NOT P，说明VS单二值任务可合法从误差和query恢复方向，signed error输出本身不作创新。所有检查写详细receipt，source SHA、真实工具退出和失败保留。

本阶段CPU1/below-normal、<=120秒、无CUDA、无医学/GT/model数组/前向，目录全部<=5MB、磁盘/RAM各8GB储备。没有对当前训练分支评分或修改。理论/AST资格不称可发表claim，当前医学能力门槛和未见确认边界保持。
