# 共同投影观测输入：执行前合同

本阶段把上一轮的[共同投影控制准备](PROJECTION_AND_SELFSUPERVISED_ACTION_PREPARATION_2026-10-08.md)落实到全部 19 个开发系列、11 个患者。先冻结本协议和新源码，再读取实际 observed NPZ；原两通道模块、原资格结果、原 native-PCHIP 和一通道参照均不覆盖。此控制用于后续判断输入投影与插值顺序的贡献，尚不测分割收益。

1. 只读 `mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json` 指定且认证的开发 observed 包。归一化使用全部实际 observed 强度的原 mean/population std，std=0 时 divisor=1。先 float64 归一化、cast float32，再逐 observed plane 用 Torch bilinear、align_corners=False 投影至原 physical grid 的目标 r/c。共享锚点保持 float32、只读，两分支只取得这一份共享锚点、索引、geometry 和同一统计记录；不重新计算投影后统计。
2. direct 分支把共享锚点写入 native z=0,4,…，其余 z=0；dense 分支调用原 local 四-anchor PCHIP 实现：首尾间隔 linear fallback，内部 PCHIP，last observed 后复制末 anchor。此处 PCHIP 作用于共同归一化/投影后的值；它与原 raw-native-PCHIP 后归一化的流程是不同输入控制。两分支仅沿 z 做 align_corners=False 插值，随后按原合同 padding=0。
3. availability 从原 native 二值 observed mask 经原三维 trilinear/padding 生成一次，两路共享同一个数组；其 SHA 必须与原 19 系列资格逐位相同。它在重采样后可以是 fractional。valid_grid 在未 padding 区=1，其余=0。沿用原 augment_pair：dense 的 shift 乘 valid_grid，direct 的 shift 乘 availability；mask 不做强度变换，所有 padding=0。
4. 面内投影的中间 affine = 原 native rcz affine × pixel-center map，其中 r/c scale=native size/target size，translation=scale/2−0.5，z 不变。z 投影与 padding 后 affine 必须与原 physical/padded zrc affine 一致。此控制不声称保持原 native anchor 强度，也不替代原 SR 输出约束。
5. 生产核验逐系列核 input/source/statistics SHA、索引、native z anchors/zero/tail、同 availability、finite/range、padding、augmentation、geometry。每系列用固定 SEED=20261008、purpose=810/index 的 512 个随机 physical 坐标，加每 anchor 临近 3 个 z × 面内 corner/center 三点；面内每 anchor 512 个固定样点及 corner/center。抽样 explicit pixel-center bilinear、z interpolation 的数值门槛 atol=rtol=3e-5，遵循原独立输入资格的量级。抽样数值核验不冒称验证每个体素的数学误差。
6. 第二作业重新打开同 19 包，独立归一化/读取索引，使用 Torch 重放整个共享锚点和两路 physical SHA（这是执行重放，共享库而非独立数学证明）。另用独立 NumPy float64 的显式 bilinear 样点、harmonic PCHIP slopes/Hermite 全 native z、首尾 linear/tail、显式 z map 样点核数学实现；全中间 dense 数组 atol=rtol=3e-5。不导入生产分支函数、原 SciPy reconstruct 或旧 direct 模块。geometry/mask 索引独立重建。另核新/旧 direct 数学同式的预定样点；完整新/旧 direct float32 差异仅作数值诊断，不据此事后改容差或宣布逐位等价。
7. 生产/独立各限 1200 s，自身 CUDA 不可见，CPU1/interop1、BLAS1、below-normal，RAM/disk 各保留 8 GB；新增本阶段文件及绑定各不超 20 MB。逐系列释放；仅保存 JSON/hash/抽样摘要，不保存完整医学体积、神经模型或 checkpoint。本阶段预期 observed 包加载 19+19 次，新增神经/GPU forward 和训练更新 0。记录真实退出、失败和已读包数；失败 attempt/version 保留，修复另存。
8. 不读 native MR/GT/validation/8 确认患者/locked IXI；严格 NPZ 白名单和读取审计。训练 live session 99542 继续原合同，不重启、不迁移、不枚举/控制其他 PID、不委派。只有原两臂各19998且真实 final exit=0/冻结，才原56FOV、全部6 gates、独立 strict；本控制不抢先启动正式训练。

数值资格不构成 MRI 效益、理论风险保证、float32 可逆性或临床证据。相同共享 source 也不推出最终两种编码严格信息等价。后续必须在同初始化/容量/训练监督/合法观测/完整成本下比较任务收益；8 确认只在方法和选择规则冻结后打开。fresh calibration 只约束正式风险保证。
