# 修复数据版 I3Net：full 前核验（2026-09-24）

**已就绪，尚未启动 full。** 当前只交付 `full.ps1 -Seed 3407`，完整300轮。机器可读记录为 `final_verification.json`。

## 检查结果

官方模型源副本与已有上游核验记录逐文件SHA匹配。完整模型23,205,197参数；4真实锚点→13位置及中央三层5:8映射正确，观测位置在AMP输出dtype下精确复制。target和cond替换为NaN不改变预测；模型只使用anchors。

checkpoint组数0/1/2/8的输出逐位一致，梯度最大差0；全部梯度有限。学习率起点3e−6、warmup峰值3e−4、300轮终点3e−5均核验。配置 `epochs=min_epochs=300`，完整预算内不启用早停。

真实256²两轮smoke使用16个train区间、一个val区间，microbatch8×累积2、checkpoint2/8。另一次运行在epoch1提交后中断，再恢复到epoch2；模型、优化器、scaler、Python/NumPy/Torch/CUDA RNG及验证均值与连续训练逐项一致，模型最大差0。这是实际恢复后继续优化的检查，不只是加载checkpoint。详见 `resume_equivalence.json`。

best重新加载后独立复算8指标，最大差0。smoke仅有两个优化器更新，指标不作模型质量、收敛或SOTA依据。正式PowerShell入口已执行 `-Preflight`，确认为1356train/69val、原修复manifest和当前源码哈希，未创建full目录。正式训练每轮85次更新，总25,500次。

## 显存和效率

真实训练峰值 **18.7550GiB allocated /19.6934GiB reserved**，allocated十进制约20.14GB，适合24GB显卡。没有无关分配来占满显存。与已测的旧I3Net参照相同执行方案。

完整 forward（四锚点输入、生成13位置、返回中央三缺失层），AMP、10warmup/30repetitions：中位 **10.28995ms/缺失切片**，峰值0.225783GiB；当前权重是smoke best，full完成后将对最终best重测。部分Conv/Linear为906.985GFLOPs/三切片区间，排除DCT矩阵乘等，不能称总FLOPs。与PAST的输出计算合同不同，报告中保留原始scope，不将两份contract伪装成完全相同。

## 研究决策与冻结状态

小波主干full的全部val指标已独立复算，效应量不足，停止。新双锚点机制容量失败，正式入口已实际调用preflight并确认因 `capacity failed or stale` 拒绝；源哈希匹配，实际失败原因是capacity=false，不是过期检查。未产生该模型full输出目录。

本I3Net包解决旧参照的两项限制：修复数据和执行完整预设调度。它不作为新PAST模型晋级，也不将两个改变相对旧I3Net的差值作单变量归因。修复PAST control和旧小波full源/权重哈希仍通过核验，旧包和论文测试表不变。

完成后以相同修复数据的PAST control作患者配对、质量/效率和末段收敛分析，无论结果高低都保留。不同历史初始化、目标函数和累计预算的限制仍存在；不作SOTA承诺，不开放test/IXI/NingXia，不直接启动其它seeds。

[完整运行指令](../docs/运行指令.md)
