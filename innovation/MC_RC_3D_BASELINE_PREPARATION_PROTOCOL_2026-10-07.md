# 3D 任务基线候选：输入和执行资格预检

定位：标准 3D U-Net 候选，尚不称“已充分适配的强基线”，不称 nnU-Net 复现或新方法。原能力门槛不变。更大 z 物理上下文、标准监督和完整 FOV 推断都是既有做法。两篇本次取得全文 arXiv:1809.10486 与 arXiv:2404.09556 明确提示配置/尺度/预算可能造成假创新；正式方法对照不能用较弱旧网络作唯一基线。

输入参照：真实完整 native MR 只通过新的参照 loader；稀疏 raw PCHIP 只从旧 observed-only package 构造，不读取隐藏 MR 像素。两种均使用同 observed 全体 mean/std，标签只在输入构造后读取用于训练监督/最后评分。完整 native 是信息上限参照，不能用作稀疏方法的部署输入。只允许原开发/已见验证，确认关闭。

物理网格：沿原 DICOM RCZ 基向量，将三轴重采样到名义 0.5mm；target shape=round(native_n*actual_spacing/0.5)，最小 1。实现按 align_corners=False 的像素中心，实际 spacing=actual_spacing*n/target_n，显式记录由取整造成的差异和完整 affine；不是将新的 grid 假装成严格 .5mm 或正交 RAS。MR trilinear，二值 GT nearest-exact；GT 重采样必须保留各系列非零前景，native scoring 必须映回原 RCZ 网格。体积不足 patch 时对称 constant-zero padding，只记录并在推断后裁掉。

候选网络：输入 1 channel、四级 3D U-Net，channels 16/32/64/128，两次 3x3x3 conv、InstanceNorm affine、LeakyReLU .01，2x2x2 maxpool，transpose-conv decoder、skip concatenation，三个 decoder heads，深监督 CE+foreground Dice 权重 4/7、2/7、1/7。patch zrc=64x128x128、batch 2，实际名义上下文 32x64x64mm（小体积含 padding）。患者均匀，再患者内系列均匀；batch 第一 patch 强制 foreground，第二 patch uniform；所有随机选择可重放。训练增强共同采用三轴 mirroring 和强度 scale[.9,1.1]/shift[-.1,.1]。先检查配方/梯度/实际拟合；正式训练预算和 schedule 待真实 GPU 测量后另冻，不自动沿用旧20k或突破旧失败预算。

推断：整个已 padding 图像的三轴滑窗，patch半宽 stride，末端补齐；固定正 Gaussian 权重平均 sigmoid probabilities，全部 voxel coverage>0；裁掉 padding，再 trilinear 概率映回原 RCZ，阈值 .5；无 GT ROI、无预测/GT connected component 筛选，无 TTA。仅 forward 的批次上限2。实际 checkpoint 的全 FOV能力尚待 GPU 实验验证，CPU synthetic constant-network coverage check 不能代替病灶评价。

资源：沿本阶段 <=250MB 新存储/8GB disk reserve/8GB RAM/1 CPU thread/自身 below-normal 合同；不保存完整 native/physical 体积，只有 hashes/records/checkpoint。GPU 只 query device totals，不查询 PID；free>=4GB 才允许初始化并开始，allocator <=10%，自身 peak reserved<=2.5GB，运行期间 free>=4GB，每100更新检查。当前首次 query 2026-10-07 GPU free1394MiB/utilization94%，不符合启动条件，不执行 GPU 更新。冻结架构不表示架构能在此显存合同下训练；须真实测量，失败记录保留。

本预检成功条件：全部28系列的两输入、真实前景和 affine映射均通过；独立 NumPy 坐标/插值/覆盖核验；CPU 最小实形3D前向反向能给全部encoder/decoder/head非零有限梯度；GPU预检只有真实运行才计数。若候选显存/速度/拟合失败，保留失败、另立新配置，不称通过。
