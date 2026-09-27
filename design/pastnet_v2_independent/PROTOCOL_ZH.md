# 独立 correspondence-only 实验（geometry 未晋级后的新协议）

在本分支任何full运行前登记。原geometry累加链停止，不改其门槛、不改其gate、不将本分支视为geometry晋级。

## 已有判定

control best epoch49、64轮早停，validation PSNR25.562011。geometry best epoch42、57轮早停，25.564138，配对增益+.002126 dB，95% CI[-.000229,+.005716]，13/23胜。虽其他均值质量与成本指标不退，但效应、区间、win count未过门槛。geometry判定见 `../pastnet_v2/results/gate_geometry.json`。

这只否定当前独立物理FiLM在本数据和预算下的晋级价值，不证明所有物理建模无效。该失败也没有检验解码前空间对应这一不同假设。

## 新的单一变量

**control + query-conditioned多尺度空间特征对应**，不含geometry FiLM，不读实际毫米/方向条件。对应模块只使用G086已有的phase和相对锚点索引[-4,0,4,8]，避免把物理距离先验与空间对应一起引入。

G086原四锚点encoder、宽MA3、latent多尺度与双域残差保留。query来自linear coarse，在每个真实锚点1/4、1/2尺度的3×3邻域做特征对应，零初始化投影进入主干前的融合特征。目标是检验原同位置融合是否过早丢失横向结构对应；它不增加新采集信息。

初始化仅为原冻结G086，不使用geometry best。沿用control的实际样本顺序、归一化、有效batch16、80轮上限、冻结3轮、AdamW/warmup-cosine/EMA/loss/early-stop协议。batch2×累积8，10块checkpointing控制24GB显卡显存。旧源码不改；新manifest同时记录旧源码、新分支源码和本协议哈希。

## 固定晋级/停止门槛

先跑seed3407，与已完成的同seed control严格病例配对。PSNR提升≥+.10 dB，即≥25.662011；95%病例bootstrap下界>0；≥60%患者获胜；parent最差四分位平均增益≥0；SSIM/MAE/MSE/NCC及Dice/HD95 proxy均值方向不退；forward latency和显存各≤control1.5倍。

任一未过则停止本分支，不以调学习率、加轮数或叠geometry/频率/风险loss救援。一次通过后才补另外两seed及匹配control；仍需三seed总体验证和重新锁定才可外部复评。此pilot入口不支持external test。

这是在同一开发validation上的第二个架构假设检验，不是新的独立holdout；单seed bootstrap仅用于开发筛选，不当作最终确认。原23名患者validation、fastMRI development-test边界与IXI/NingXia锁定要求不变。

## full指令

```powershell
Set-Location D:\MRI
.\design\pastnet_v2_independent\full.ps1 -Seed 3407
```

执行前由助手完成真实smoke。完成后助手读取结果并运行本分支report，不自动启动其他full。
