# 四分支 pilot 的固定最终评价

须先获取 session80513 真正退出并保存来源绑定的 ACTUAL_PILOT_EXIT.json；四分支均完成 99 更新、journal/cp/source SHA 均核对后才运行。只评已见四名验证患者/9 series，每个分支完整 native FOV，总36次生产与36次独立functional FOV。不读确认患者或 locked IXI；本阶段不重新评分开发19 series，不能据此宣称全28医学资格或充分适配。

CPU4/interop1/below-normal，禁止CUDA初始化；V4最终概率 float64映射后转float32，严格概率误差≤3e-6、float64坐标≤3e-12、二值差异0。每分支先完成两个与GT无关的完整推断后才读GT。packbits无损保存/跨reader重读，计数/患者先均值独立比较；不能挑病例或改 .5 阈值。模型训练过程中不评分本验证集，完成后只用固定最后权重。

评价保持原六门槛：full Dice≥.70、missing Dice≥.65、full recall≥.70、absRVE≤.50、四患者full/missing均正Dice、无series零TP。报告所有四分支与每输入的 strong-minus-basic，以及原父模型比较。失败如实保存，短pilot成功亦不证明充分适配或创新。此已见验证集只用探索，四人样本不能当独立确认。纵向方向差异仅事后辅助，不做临床增长判断。

wall3600秒，本目录含训练与评价≤40MB，磁盘/RAM各十进制8GB储备，启动时确认未来新增存储可容纳。最终评价同入口两实现不是第三次跨进程独立重跑；日后正式资格须按完整冻结合同再验证。
