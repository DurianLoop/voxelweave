# 来源更正：模型库掩膜与成员身份

2026-09-09。本页明确纠正 Plan 13 审计中两处过强／错误的解释；不改变旧数值，不覆盖 Plan 13 报告原文。

## 1. `target_0.01` 的 target 是目标模型，不是真值

实际来源为 `design/rasinet/nested_precompute.py` 的 `case_job`：

```python
target_masks = {**masks, "target_0.01": threshold_mask(outputs[target], indices)}
```

Plan 11 使用该表的 `intensity_mean__target_0.01`，然后在 registry 候选成员之间取中位数。它是目标模型**预测**的 1% 掩膜；不是 `gt` 的掩膜。真值只用于下游 fidelity/benefit 端点。Plan 13 将这一分支与 Plan 9/11 的 GT-mask 机制实验混为一谈，结论错误，应撤回该分支的“评分掩膜访问目标真值”指控。

独立选取两队列按病例名排序第一例，对 I3Net/HAT 目标与七个其他候选成员的三种 mask 重新读取原始预测计算，共 84 项，最大绝对差为 `1.4210854715202004e-14`。同时验证预测 mask 与 GT mask 确实不同。见 [原始复算](outputs/bank_mask_raw_reproduction.csv) 和 [输入哈希](outputs/bank_mask_manifest.json)。

此更正不适用于 Plan 9/11 的五架构 shared/disjoint 实验：它们的掩膜确实直接由目标图像生成，相关部署边界仍然存在。也不意味着历史模型训练和图像预处理完全不存在其他目标信息依赖。

## 2. Linear/Cubic 是候选成员，但没有作为 bank-score 的被评估目标

`design/rasinet/model_bank_registry.csv` 显示两个解析插值器均为 `candidate_bank_member=True`。模型库包含六个神经候选和两个解析候选；`nested_precompute.TARGETS` 是 11 个神经目标。因此 bank 分数只有 11 个被评估目标，而 Anchor-CV/adjacent MAE 覆盖 13 个重建模型。

旧稿“解析插值器不在 candidate bank，所以缺失”的解释不正确。正确表述是：预计算合同没有生成以解析插值器为 target 的 bank-score 行。结构性缺失仍需保留，不填零，不改变原始分母。

## 3. fastMRI 划分与几何范围

独立复算得到 train 112 series /111 patients、val 24/24、test 24/24。一个患者跨 train/val，但 test 与两者患者集合均无交叉。该 train/val 交叉可能影响历史 checkpoint 选择，不能宣称训练/验证全面无泄漏；也不能把它错说成 test 患者泄漏。

对论文历史 test-24 逐例读取原始 DICOM，核对首／中／末像素与现有 NIfTI 顺序、方向一致性、物理位置单调性。24/24 通过。原 NIfTI 对角 affine 不保留完整患者方向；同数组位置的配对可追溯到相同 DICOM 平面，但不能把合成 affine 单独称作完整物理几何验证。见 [逐例几何](outputs/fastmri_test24_geometry.json) 和 [划分复核](outputs/fastmri_split_audit.json)。本轮未改任何原始图像、split 或其他工程的训练协议。
