# 固定版本训练链：这次实际读到了什么

本轮只读获取和逐行核读 FastSurfer v2.3.0 的另外七个文件，固定 commit `550e84596b7adbc01bd0f2e93f1a127b1cb2df99`。defaults 240、loader 176、train 427、dataset 544、三个 YAML 各 74 行，共 1609 行；与前轮四文件 2361 行合计 11 文件、3970 行。获取真正 `1c2de9 exit0`，六个未截断读取返回分别为 `6a0da1 / 743fd0 / 86719c / 4b17de / 527dce / 59ab7b`。没有 import 或执行作者代码、没有读取其 HDF5、权重或本项目新的医学数组；不同论文正文新增数仍为 0。

## 由“存在这个类”推进到“发布配置实际连接它”

三个方向 YAML 的 DATA.AUG 均是 `[None, Gaussian]`，训练 batch 8、70 epochs、bilinear、top_left、BASE_RES=1.0，axial/coronal 79 类、sagittal 51 类。loader 46–61 进入普通分支，用 ZeroPad2D、ToTensor、AddGaussianNoise(mean=0,std=.1) 顺序组成 transforms，并用 MultiScaleDatasetVal 作为此训练数据集。dataset 506 和 516 得到 base_res/zoom，519–531 执行 transforms；此前已核 augmentation.py 343 对两轴加同一个高斯 delta。因此，在未被运行参数覆盖的三个发布配置中，内部尺度因子扰动有完整静态调用链；它不是图像强度 Gaussian noise，也不是通过改 GT 做这个尺度增强。

loader 62–153 的另一个可配置分支确有 TorchIO Scaling、Rotation、Translation、Elastic、image-only RAnisotropy、BiasField、RGamma，并可把 Gaussian 标志交给 MultiScaleDataset。但三个发布 YAML 不进入该分支。不能看到源码支持这些操作就声称发布默认训练同时使用所有操作；也不能把 TorchIO Compose 的字典值 .8 直接解释成每个操作独立 .8 概率，当前没有读取固定 TorchIO 版本实现。

MultiScaleDataset 266–275 的 scale noise 有 clamp(min=.1)，AddGaussianNoise 在所读普通分支没有这个 clamp；不能把一个分支的稳定性性质转给另一个。TorchIO 分支归一化是 img/img.max() 后 clamp，普通 ToTensor 分支是 /255 后 clamp；本项目 observed-shared z-score 仍须自己的强度合同。存在源码中的潜在角落问题不等于作者真实实验失败。

## 训练与模型选择的成本不能只按 YAML batch 数算

train.py 93、133–157：batch 非 16 时进入 subepoch；发布 batch8 会每两 batch 执行一次 optimizer.step，loss_total 每 batch backward，源码此处没有把 loss 除以 2。即使输入 batch 数相同，forward/backward 数与优化器更新数也不同，梯度量级不能当成标准平均累积未经核查地移植。本轮未读取 get_loss_func/get_optimizer/get_lr_scheduler 的文件，所以不推断完整实际优化配置或损失的所有缩放行为。

train.py 321 会用 loader 更新 NUM_STEPS，YAML 的 NUM_STEPS=10 不是训练只有十步的证据。run 388–427 每个 epoch train+val，同时周期 checkpoint 和按 miou 选 best。defaults 100–113 有 early-stopping 配置项，所读 run 没有根据它终止的分支；有配置名不等于执行了早停。运行入口如何合并 YAML/命令行参数、真实历史日志、训练 HDF5 身份及 patient split 均未取得。因此，只陈述该 commit 的静态发布配置与 Trainer 行为，不认定它是 2022 论文精确配方，也不宣称分折独立或复现成功。

## 对项目的决策

VINN 的内部 feature 尺度转换和 image-only resolution degradation 已有明确先例。给新基线加尺度扰动、拿 nominal scale 的倒数忽略实际整数尺寸修正，或把 feature 路径当成我们的 3D image roundtrip，均不能支撑创新 claim。

先用本项目真实上下文与完整几何资格把 ordinary augmentation 基线做好，再研究充分任务能力后的具体动作损害差。全 patch 支持资格可避免仅保留有效 loss mask 时的 InstanceNorm 全局污染问题，但只认证输入插值支持，不认证医学有效性、信息无损或模型性能提升。该基线候选政策和后续拒绝条件记录于 [准备协议](ORDINARY_WHOLE_PATCH_POLICY_PREPARATION.md)。

来源获取原文、字节 SHA、响应头见 [receipt](vinn_training_chain_attempt01/receipt.json)。取得源码与本次实际核读分别登记，历史 retrieval 中 actually_read=false 不覆盖。
