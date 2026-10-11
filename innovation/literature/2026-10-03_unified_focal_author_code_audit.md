# Unified Focal作者代码核对与CPU移植准备

论文XML明确链接 [作者仓库](https://github.com/mlyg/unified-focal-loss)。本轮按commit `411c9c5ce43b2ef847f0903d1b841512ad8d2eee`（2022-05-13）获取仓库/commit/tree响应及README、loss_functions.py；raw内容的Git blob SHA1与tree一致，同时保存SHA256。所读代码是该commit公开版本，不证明论文原实验精确版本相同。没有clone、安装、TensorFlow import或作者包执行。

实际读README全部、loss_functions.py全部源码（含identify_axis和各loss）；Figures/test.py只是一个换行，不算算法材料。获取时actual_source_read=false保留原状态，本报告和下面源码锚点另作阅读证明，不回写获取记录。原始文件第262行会抛IndentationError（第261行nested loss_function的docstring缩进不正确），未修改原字节。

| 源码锚点 | 已核语义 | 对当前准备的影响 |
|---|---|---|
| identify_axis、18–91的Dice/Tversky | spatial axes求和，保留batch/classes；`tp+delta*fn+(1-delta)*fp` | δ提高FN权重，与扁平正文Eq18系数顺序有出入；不根据正文猜类别 |
| 260–289 asymmetric_focal_loss | channel0背景、channel1前景；背景乘`(1-p_background)^gamma`和1−δ，前景CE乘δ、不加focal压制 | 移植必须明确channel顺序和softlabel语义 |
| 292–323 asymmetric_focal_tversky_loss | 背景1−TI，前景`(1-TI)*(1-TI)^(-gamma)`；两class与batch平均 | 等效前景指数1−γ；不是跨两个patch合并的前景Dice |
| 351–372 asym_unified_focal_loss | weight乘FT、1−weight乘CE；默认.5/.6/.5 | λ=.5时两种命名相同；非.5不能交换系数 |
| K.epsilon和clip | 作者委托backend的epsilon，并clip预测 | 本CPU合同显式选1e−7，不假称原训练运行时已核 |

新增 [单logit CPU移植](../experiments/unified_focal_binary_cpu_port.py)保留两class/per-image平均、δFN顺序、asymmetric项和显式epsilon；将(1−g,g)用于area softlabel是本项目适配，不能声称复现原one-hot训练。作者代码未原样执行，这也不是新loss创新。

[独立NumPy数值/梯度证明](../experiments/unified_focal_binary_cpu_port/attempt_01.json)核五个binary/soft/empty/full/extreme合成情形以及24个central finite differences；无MR、无network forward、无训练updates。[匹配FP/FN与输入域检查](../experiments/unified_focal_binary_cpu_port/output_bias_and_input_guards_attempt_01.json)另列，不把一个toy scenario的方向推广为真实召回改善。

下一能力实验才可使用移植。要共享初权重、patient/series/augmentation draws、相同预算/最后checkpoint与完整原生指标；模型容量、observed信息、采样与target resize都固定。当前冻结20k模型及验证失败结果不改变，确认患者仍不开。
