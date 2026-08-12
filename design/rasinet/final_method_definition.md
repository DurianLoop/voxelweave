# 最终方法定义

## 推荐部署定义

最终推荐方法仍为预先指定的 target-to-committee disagreement：对目标插值器 `m`，committee `C_m` 必须排除 `m`；在真正生成的切片上计算 `median_b |yhat_m - yhat_b|`，用目标预测的 1% foreground mask 限定支持域，再用体素均值形成 examination-level score。高分仅表示较高的估计重建风险并进入优先复核，不是概率或临床保证。

## 固定成员

在共同多倍率实验中，可用模型为 I3Net、HAT、SwinIR、ArSSR、CycleINR、Pix2PixGAN、SMamba-UNet、ACVTT、ResSRDiff、ResUNet、SAINT、linear 和 cubic。最终 baseline 使用原始 frozen-primary 成员集合；目标模型每次从集合中删除。额外模型只参加开发期候选搜索，不因宁夏结果被加入最终方法。

## 为什么没有采用开发集最优方案

development high-fidelity committee 将平均 nAURC 从 0.089 降到 0.040，但在冻结 NingXia 验证上从 0.070 恶化到 0.116。该结果说明 committee selection 本身可能过拟合 cohort。低成本方案验证均值为 0.080，接近 baseline，但 paired bootstrap 未建立优势。因此推荐稳健的预设 baseline，并把广泛搜索作为 transfer-failure 分析，而不是事后宣称算法升级。

## 可识别边界

若 `yhat_b = y + c + epsilon_b`，target-to-member difference 消去共享误差 `c`。因此该分数能感知模型特有偏离，却无法识别全部成员共同的结构删除、过度平滑、预处理错误或偏置。跨倍率逐体素一致性也因现有输出深度和 generated-slice support 不同而不可直接计算；未进行未经验证的重采样。

