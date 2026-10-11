# 共同投影 observed 输入控制：19 系列结果

新模块已在全部 19 个开发系列／11 个患者完成生产资格与精度明确的独立 v2 核验。它让 direct 和 dense-PCHIP 从同一份 float32 投影后锚点出发，用作后续输入因素对照；尚没有分割、动作收益或临床结果。

生产作业 109.092687s；原独立作业 14.533936s、真实失败；独立 v2 92.745478s。共加载 observed 包 42 次（19+4+19），唯一医学系列19。新模型数组、神经/GPU forward、训练更新0；计数不包含原训练，也不把 hash 字节读取当数组加载。

## 已核输入合同

- 原全部 observed 统计先归一化，再 bilinear 投影 r/c；两路取同一个只读锚点对象，分支后不重估统计。
- 原 local PCHIP 内部四锚点、首尾 linear fallback、tail 复制；direct 缺层 native z=0。共同 z-only map 和 padding。
- availability 由原二值 native mask 构造，两路共享；全部19与旧资格 SHA 逐位一致。强度增强不修改 mask，padding为0。
- 中间 rcz affine 使用面内 pixel-center map；最终和 padded zrc affine 与原 grid 在1e-12容差下一致。

## 保留的数值失败与修正范围

原 v1 独立核验在第4个已加载包失败，只有3系列完成。原因检查依赖已安装 ATen header；另建 v2 protocol、source、preregistration、attempt，不覆盖原记录。v2 在同一预定样点重现原失败，用显式 float32 坐标后通过；atol/rtol仍各3e-5。

v2 面内四角样点最大误差 7.56089214349e-07；完整 native z 的独立 NumPy Hermite/linear/tail 最大误差 9.53674316406e-07。同库全数组执行 SHA 重放通过。前者是抽样数值核验、后者覆盖全部中间 dense 体素；同库 hash 重放不能冒称独立数学证明。

按原 ideal float64 坐标的同一3e-5 abs/rel门槛，9/19系列存在失败样点，总30个；这些差异和失败点保留在 v2 JSON。新 direct 与原一次 trilinear direct 完整体积逐位相同 19/19，最大绝对差 0。未证明完整体积理想坐标误差界、float32可逆或严格信息等价。旧 direct absolute 任务失败没有因此被改写。

| 患者 | UID末12位 | 后端投影最大样点误差 | 完整Hermite最大误差 | 原ideal门槛失败样点 | 新/旧direct最大差 |
|---|---|---:|---:|---:|---:|
| VS-MC-RC-001 | 292568369177 | 3.78e-07 | 3.58e-07 | 0 | 0 |
| VS-MC-RC-001 | 625802103688 | 3.59e-07 | 2.38e-07 | 0 | 0 |
| VS-MC-RC-002 | 544325434833 | 6.78e-07 | 4.77e-07 | 0 | 0 |
| VS-MC-RC-002 | 277274474217 | 6.04e-07 | 4.77e-07 | 1 | 0 |
| VS-MC-RC-004 | 601978222649 | 5.76e-07 | 4.77e-07 | 1 | 0 |
| VS-MC-RC-005 | 372315290570 | 7.56e-07 | 9.54e-07 | 0 | 0 |
| VS-MC-RC-005 | 968159053837 | 5.92e-07 | 4.02e-07 | 0 | 0 |
| VS-MC-RC-006 | 528541337534 | 4.79e-07 | 7.15e-07 | 1 | 0 |
| VS-MC-RC-006 | 715824886367 | 6.16e-07 | 4.77e-07 | 5 | 0 |
| VS-MC-RC-006 | 234505955794 | 5.51e-07 | 4.77e-07 | 1 | 0 |
| VS-MC-RC-007 | 599138416018 | 4.88e-07 | 7.15e-07 | 1 | 0 |
| VS-MC-RC-009 | 159756197992 | 5.3e-07 | 8.34e-07 | 0 | 0 |
| VS-MC-RC-009 | 282909258398 | 6.88e-07 | 7.15e-07 | 0 | 0 |
| VS-MC-RC-010 | 282417647395 | 5.66e-07 | 4.77e-07 | 0 | 0 |
| VS-MC-RC-010 | 883323973905 | 6.24e-07 | 7.15e-07 | 4 | 0 |
| VS-MC-RC-010 | 314776200590 | 7.26e-07 | 4.28e-07 | 0 | 0 |
| VS-MC-RC-011 | 786790590874 | 3.95e-07 | 7.15e-07 | 7 | 0 |
| VS-MC-RC-012 | 133167917606 | 6.47e-07 | 7.75e-07 | 0 | 0 |
| VS-MC-RC-013 | 306821943207 | 4.29e-07 | 8.34e-07 | 9 | 0 |

## 证据与接续

- [原输入合同](COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md)、[精度v2合同](COMMON_PROJECTED_OBSERVED_INPUT_PRECISION_V2_PROTOCOL_2026-10-08.md)。
- [新模块](experiments/mc_rc_common_projected_observed_2026_10_08.py)、[19系列生产](experiments/common_projected_observed_qualification_2026_10_08/attempt01.json)、[原独立失败](experiments/common_projected_observed_independent_2026_10_08/attempt01.json)、[独立v2](experiments/common_projected_observed_independent_precision_v2_2026_10_08/attempt01.json)、[汇总](experiments/common_projected_observed_summary_2026_10_08.json)。

待原两臂完整预算、真实最后退出、原56FOV/6gates/strict完成后，将此控制加入同初始化、同容量、同训练监督和完整实测成本的任务因素矩阵；不提前训练、不以中间loss选择动作。

本控制变更投影和插值顺序，是输入解释对照，不称新恢复算法、原native锚点保持、理论风险证书或已发表claim。确认患者、已见验证及locked IXI仍关闭；goal active。
