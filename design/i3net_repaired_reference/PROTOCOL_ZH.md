# I3Net 修复数据、完整调度参照：计算前协议（2026-09-24）

## 为何此时补强参照

PAST 小波主干 full 相对修复 control 仅 +0.017549 dB，未达 +0.10，停止。新的双锚点对应路径通过机制检查，但冻结旧主干的96步容量 MSE 仅下降0.9208%，未达5%，停止且不进入 validation/full。这些结果不支持继续付出该模型 full 成本。

当前旧官方 I3Net 本地参照在100轮早停，best epoch32，25.172132 dB；最后学习率2.4495e−4，原300轮cosine应到3e−5，低学习率阶段尚未执行。它还使用旧混合序列数据，无法与当前修复control形成同数据比较。现有优势不足以作SOTA依据。

本包补齐一个**更充分训练的官方架构参照**，不是PAST-Net新模型，也不是对PAST做续训/学习率微调。修复数据与完整训练预算同时更新，因此不将相对旧I3Net的变化归因于单一变量。此前旧分支的停止结论与原始文件保持不变。

## 固定模型与数据

直接复制已核验的官方 I3Net 64通道、16 I2Block、3 CrossViewBlock 原样vendor与reference源码。源文件 SHA 与旧 `source_check.json` 核验，不因结果换成代理或缩小模型。不改变官方模型的4真实锚点→13位置；仅监督与评估中央5:8三个缺失层。不是官方全窗口/IXI协议复现。

使用 `pastnet_series_integrity/manifests/fastmri_repaired.json`，113series/111train患者、1356train区间、23val患者/69val区间。observed-only归一化、256²、无clamp、相同边界重复/有效mask合同。原validation样本、聚合与8项指标完全保持。模型只读anchors，不读target、physical、cond。

## 唯一预设预算方案

seed3407，从与官方相同规则的随机初始化开始，不加载旧I3Net或G086权重。**固定完整300轮，不早停**；不搜索学习率、warmup、loss或宽度。Adam lr3e−4、betas(.9,.999)、eps1e−8、无weight decay、中央原生L1、无EMA、clip1、AMP scale4096，均保持旧I3Net参照。

原15轮warmup由3e−6升至3e−4，其后cosine到3e−5。有效batch16，microbatch8×累积2，重计算前2/8组，目标24GB卡约20GB实测使用。训练使用同样的独立epoch sampler。相对旧参照，只取消100轮起的早停（min_epochs=300），完整执行原先声明的调度；此处不是从旧last续训。

完整300轮包含25,500次更新（每轮85）。仅validation PSNR保存best。以完整预算作为本地参照，不声称官方1500轮协议或最优超参数，也不能仅凭固定轮数声称收敛。

## 前置检查、终止与结果解释

源文件一致、4→13/中央三层映射、观测位置复制、target隔离、checkpoint梯度/输出一致、学习率起/峰/末端，256²真实两轮smoke，提交epoch1后恢复至epoch2与连续运行的模型/优化器状态一致，独立8指标复算，正式PowerShell preflight。源码、训练/数据合同、best/last SHA全部冻结核验；非有限梯度或指标直接报错，不跳病例。

预算到300停止，不因分数追加训练；若最后30轮best增长>.03dB，标记预算受限、收敛未证实，并报告末段曲线。增长小也不是严格最优收敛证明。该参照无架构晋级门槛，低于/高于PAST都如实保留，不能挑选弱baseline。

完成后与同seed修复PAST control（25.567453dB）逐患者配对，10,000次bootstrap、困难四分位、全部质量/尾部与效率指标。显式报告 **PAST继承G086，而I3Net随机初始化；loss和累计预算不同**，因此为描述性本地参照，不是受控架构因果消融或SOTA证明。I3Net还生成完整13位置，效率统计须保留此输出合同。

不运行development test、IXI/NingXia，不据此直接修改旧论文test主表，不启动其它seeds。最终新模型仍须匹配三seeds、锁定后外部验证及可信强基线比较。
