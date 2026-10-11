# 两通道公平输入对照：执行前资格协议

本轮新增对照准备旨在令后续真实任务比较可运行，不改变仍live的session99542。强PCHIP和直接稀疏任务是必要基线，不是新方法claim。当前正式19series最后模型和四验证gates还未得到；本轮只开发19series observed包输入检查和独立合成数值/梯度资格，不读GT/native参考/验证/确认，不训练MRI。

同一两通道3D U-Net、同参数数和共同权重，固定两个输入条件：
- dense-PCHIP：通道0由真实observed包生成PCHIP，使用观测mean/std归一化后原physical_mr映射；通道1为原native层可用性mask按同physical_mr映射的fractional availability。
- direct-observed：通道0在native真实观测层放入同一归一化观测值，未观测处0，再用同physical_mr映射；通道1与dense分支完全相同。它是已知插值核映射后的weighted observation numerator，非“未观测处已知背景”；mask显式区分无观测和观测值0。不除以availability，不生成伪造新测量，不称真实采集slice-profile。

所有输入只取已认证observed_rcz、observed_indices、native_shape、affine；重建函数没有native或GT参数。mask与normalized sparse field按原pixel-center lattice映射。两臂通道数/坐标/metadata/统计完全相同；PCHIP只使用observed，不向direct添加未观测GT或邻层真实像素。

资格：逐19开发series单次stream，检查原observed包SHA/角色、PCHIP native/physical SHA与已冻结输入一致、全部native观测值逐位保留、direct未观测值0、mask只标实际层、两个physical mask逐位一致、输入有限、mass在[0,1]。保存每输入SHA/shape/bytes，MRI输入0forward、不读标签、不保存完整输入体积。

增强：两路physical输入的灰度变换必须保持mask语义。positive scale s和shift t只改变observed强度，direct numerator变为`s*numerator+t*availability`；dense变为`s*dense+t*valid_grid`，padding外0。mask本身不做强度scale/shift，三轴flip同输入/标签同步。此新对照的padding增强规则与原sample_batch全patch shift不同，必须作为新的共同配方，不能替换原训练或混称一项因素。这条差别需在最终公平矩阵保留原one-channel-PCHIP参照。

模型：原TaskUNet3D第一Conv3d从1输入改为2输入；共同canonical权重取原seed20261007新随机模型，只扩展第一层，额外mask权重初始0。所有后续参数一致。两路均使用同一个两通道定义/权重，因此容量严格相同；额外16×27=432参数两臂都有。原单通道参考输出与扩展zero-mask权重的数值资格用独立合成16×32×32/batch2检查。不同Conv backend可能舍入，预固定allclose atol1e-5/rtol1e-5；不把两臂严格相同state_dict与跨通道backend输出bitwise等价混为一谈。

合成资格还验证两臂deep-supervision BCE+Dice均有限、encoder/decoder/ups/heads梯度非零及mask通道可收到梯度，2步checkpoint完整树连续vs恢复一致；仅合成数据，不能证明MRI拟合/泛化。后续MRI训练需要真实资源资格和原强任务gates通过，另立冻结训练budget/stream/最后权重规则，不由本次合成loss定预算。

资源：CPU4/interop1、float32、自身below-normal、无CUDA；墙钟600秒，RAM/磁盘各8GB余量，本轮保存<=25MB，MRI数组逐series释放。不运行新的MRI训练，不动任何用户终端进程。所有新文件仅innovation，不更改过去冻结文件。
