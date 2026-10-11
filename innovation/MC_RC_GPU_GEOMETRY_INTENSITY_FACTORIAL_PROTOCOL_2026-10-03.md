# 下一能力阶段：GPU上完整几何×强度四臂

无增强CPU20k已完成20000draw/40000patch认证；新GPU37完整条件/111plane实现核验完整通过，但四验证gate全部失败。开发full Dice .686214、四验证 .068768，4/9series TP0。这个结果不能用来推断SR机制；需继续任务能力开发。

原CPU“全增强/无增强”只作历史描述。为避免训练设备混杂，这次**四臂都在同GPU从头训练**：none、both、geometry_only、intensity_only，固定此顺序，各20000更新，总80000；不复用任何已训练CPU权重、不只报最优臂。单seed，四验证已用，仍不是患者科学确认。

沿用981602参数/seed20261004、BCE+local Dice+.5global、AdamW wd=.0001、cosine .001→.0001/19999、最后checkpoint/.5、11开发19series。四臂初权重必须等于已认证a146c0c4...；每次重置同patient/series随机流、旧z/patch primitive及源像素支撑，关闭因素保留原随机流，不能变为coverage采样。scale/shift只作用输入；D4同时作用图像/标签，几何关时用原patch逆映射。

所有MRI训练输入仍为已认证observed-only raw PCHIP/observed_shared与physical .5mm/±2±1/0mm上下文；没有完整隐藏MR。原生完整标签只用于开发监督。逐更新核patient/series/z/native patch与冻结CPU20k的primitive SHA；none/both实际输入SHA逐项对应旧新/旧aug SHA，两个partial臂保存全20k输入SHA。多患者新stream不能以608预检冒充独立认证，后续另做全80000输入重建核验。

CUDA仅用已授权GPUadapter，CPU保留context/resize/grid_sample与监督/loss；分支边界的CPU/GPUcopy保留autograd，模型和AdamW权重在GPU。float32，无AMP/TF32，cuDNN deterministic=True/benchmark=False。每步非有限loss或梯度停止保留失败；首臂首10真实updates核global/local梯度可回传、保存平均运行时，总80000投影≤3600秒作资源门槛，不按loss早停。不将CPU/GPU初权重相同误称训练轨迹或最后权重相同。

资源守卫沿单线程/below-normal、15GB磁盘/8GB内存、GPU allocator10%/peak≤2.5GB、循环free≥4GB。四臂顺序训练，全部训练结束和源核验通过前验证模型前向0；不与另一新训练/评价并行，不枚举或操作用户终端训练，不改根环境/locked IXI test。新目录<150MB。任何失败保留原attempt，不重启已完成/运行任务。

训练完成后需**新评价器和新独立核验入口**：四臂各同37完整条件，共148；各首中末，共444plane。同原患者聚合、四域计数/full-affine边界、空/undefined、固定四验证能力gate，完整逐臂报告。当前只有训练运行器和两个partial输入接口，148/444评价/训练全80000独立verifier尚需实现，不提供虚构已完成结果。原无增强GPU37结果不会被覆盖。

这是一项任务能力/增强因素开发，不是重建创新。若仍无法建立强能力，应转向充分架构/监督/分辨率与原生能力参照；不在弱评价器上训练observable修正。强能力后才native/6×5公平矩阵、同observed信息直接任务/分辨率随机化、具体缺层残余修正；最终方法/端点冻结后八确认及第二独立训练任务网络。
