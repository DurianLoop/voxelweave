# IXI：I3Net–PAST 查询潜特征桥接，独立配对协议

登记于2026-10-10，正式full开始前冻结。用户目标是超过I3Net；当前没有保证或新的SOTA证据。旧代码、checkpoint及失败门槛均保留。本包是使用历史I3Net与PAST权重的混合模型；部署时两个模型都存在，必须计入总参数、推理时间和显存。

## 证据与核心假设

IXI wavelet独立测试在同协议下落后I3Net约2.1094 dB；此前六锚点STC在58位validation患者上仅比四锚点对照提高0.00340356 dB，未达0.10门槛，已经停止。fastMRI的latent频率读出、图像残差读出也没有实用晋级收益。继续延长旧模型训练或增加相同远端拟合缺乏支持。

I3Net的完整四锚点→13层表示包含已学习的跨平面与层内信息。[官方实现](https://github.com/eeeric-code/I3Net)及本地冻结Reference均保留其结构。当前PAST的独立四锚点混合没有直接访问这份预学习表示。本轮新增的信息是**相同稀疏观测经过强I3Net先验得到的成熟潜表示**，不增加真实采集层，也不把教师特征当作信息上限或额外测量。

核心模型固定I3Net，读取其tail之前的64通道成熟latent；PAST保留小波MA3宽主干、四锚点rich conditioning、linear coarse、多尺度latent和dual-domain路径。PAST混合latent、其有界预测残差、区间phase与相对I3窗口query位置，加上I3latent，经1×1/深度3×3/1×1读出产生±0.05的查询修正。

预测等于I3Net窗口内已裁剪预测加该修正，也可写为linear coarse + 有界I3残差 + 有界查询残差。修正头零初始化，两臂初始输出逐tensor等于冻结I3Net。已有PAST从固定IXI wavelet3 seed3407 best初始化；没有加载失败STC的新路径。

## 唯一主要变量及固定初始化

- blind：I3Net预测作为共同基点，进入新读出头的I3latent严格乘0。
- latent：仅解除这一64通道latent mask。

两臂全部初始参数、名义容量、教师计算、采样、优化、损失和执行配置相同。blind也接受同样的query位置、PAST特征和共同I3预测基点。latent−blind才是开放成熟表示的收益；latent−历史I3同时包含共同的PAST残差学习、目标与额外训练预算变化。

I3固定checkpoint：`baseline/ixi_i3net/runs/full_test115_stable/checkpoints/i3net_epoch_best.pth`，SHA256 `48927b521c834f5f6bc26c0b28886d873aae41c0beee5cdbe01c7dec704977f9`，历史best epoch38。

PAST固定checkpoint：`design/pastnet_ixi_wavelet/runs/full_wavelet3_ixi_seed3407/best.pth`，SHA256 `bee2006a5fde5e006feb42745b7048938c72e008068d7424867f8d0c4dc95acc`。

## 数据、目标及训练预算

沿用404 train、58 validation、115已开发test的病例划分，核对其与历史I3Net split文件逐ID一致。当前只允许train/val图像。复用已核验float32缓存；按病例全部真实观测层min/max归一化，不能读取缺失层极值。

train每轮无放回取4000个完整四锚点窗口，窗口网格为0,4,8,12；索引由seed*1000+epoch确定。每个样本只监督一个三缺失层区间，其位置由epoch seed+样本索引mod3确定，覆盖窗口内三组query；两臂一致，不按标签挑选。PAST边界槽只重复当前I3窗口的观测端点并携带无效mask；不额外偷读窗口外采集层。

AdamW，PAST参数lr2e−5、新读出lr1e−4，wd2e−5、betas(.9,.99)、warmup5/cosine floor.05、EMA.999、clip1。前3轮仅更新新读出，之后更新PAST，I3始终eval且无梯度。80轮上限、min30、patience15；只用validation PSNR选EMA best。

固定目标为MSE+.05×Charbonnier(ε²=1e−6)。这是本新包的共同背景目标，旨在检验强基点上的条件残差学习；不是在旧STC门槛内改loss救援。训练预测不clamp；所有配对臂使用相同目标、梯度累积与预算，质量守卫约束MSE优化可能产生的MAE/结构取舍。BF16自动混合精度用于PAST桥接，I3和loss为FP32；验证全部FP32。禁止静默跳过数据、非有限loss/梯度，或自动更换精度。

effective batch16。真实反传、AdamW状态、EMA与冻结I3共同驻留的显存测量确定micro-batch与重计算块数，写入`execution.json`并纳入源码哈希。目标约20GiB，allocated不得超过21.2GiB、reserved不得超过22.5GiB；不能添加无关张量占显存。

## 验证合同与预设门槛

先完整测冻结I3Net的58位validation患者并保存独立基点。对完整4→13窗口，先对每窗口输出clamp[0,1]，再均匀重叠融合；只评真实缺失层、患者等权。两臂同样计算全部三组query。PSNR/SSIM使用每张GT的强度范围，与主表范围定义一致；MAE/MSE仍为归一化单位，Dice/HD95仍为强度阈值代理，不能混入旧表raw/auto-mask排名。

seed3407晋级必须同时满足：

1. latent−blind PSNR≥+0.05 dB；latent−冻结I3Net≥+0.10 dB。
2. 两项比较患者配对bootstrap(10,000次，seed73019)的97.5%CI下界均>0。两项预登记比较用Bonferroni区间；另报告95%CI，不声称消除了全项目多轮开发。
3. 两项比较都至少60%患者胜出，各自reference最差15位患者的平均PSNR不退。
4. 相对两个reference，SSIM/MAE/MSE/NCC/Dice proxy/HD95 proxy/tail10 MSE均值方向均不退。
5. latent/blind训练时间与allocated显存比均≤1.5。另报告相对冻结I3Net的完整推理开销，不能称为同参数或同速度模型。

任一失败则停止当前桥接机制，不追加续训、LR扫描、头宽/修正幅度扫描、另两seeds或候选test。blind若改善，按共同适配结果记录，不能把它归为开放I3latent的贡献。两臂都只达到单seed的validation筛选条件，不能直接称为超过I3Net的外部SOTA。

## 三seed与外部锁定

seed3407全部门槛通过后，保持所有源码、配方、数据、初始化和执行配置，分别完成seed2027、9103的配对full；入口验证seed3407 gate后才允许它们启动。每seed的best只由validation选定。三个seed均报告同口径患者配对统计、质量、训练与推理效率；固定历史预训练源意味着这是三次独立适配随机性，不是三次独立从头预训练。

三seed成功后另行锁定模型/权重/评价合同，再运行IXI和NingXia外部比较。IXI test115此前已经开发查看，须标作开发后探索确认；不能凭它重选seed、epoch或loss。要论证广泛SOTA，还需要匹配基线训练合同及新的独立数据证据。本包当前没有test入口，也不自动读取test图像。

`freeze.py`在三个seed均通过全部门槛后核对全部best权重，并按配对seed与患者交叉重采样报告95%/97.5%CI与每seed增量/标准差。代表性展示权重固定为seed3407，外部完整结果须报告所有三个seed，不能按test结果挑权重。仅三个适配seed意味着训练随机性不确定性估计仍有限。

## 溯源、恢复与用户分工

所有本包Python/PS1/CMD、本协议、执行配置及冻结依赖源码哈希写入manifest；full启动后不得修改。best和last原子保存，last为唯一epoch提交点，包含模型/EMA/AdamW/RNG/history及可恢复best。未提交epoch重跑，完成的臂核验后跳过。

纯标准库启动器在导入PyTorch之前创建日志，保存stdout/stderr、完整Traceback及真实退出码；两臂顺序执行。助手完成信息合同、真实显存测量、两臂smoke和中断恢复核验；用户运行full。不要在24GB单GPU同时启动两份本包训练。所有旧源码和checkpoint保持不变。

验证执行固定为每个四锚点窗口仅计算一次冻结 I3Net，三个区间合并为 batch3 的 FP32 桥接推理，随后保持原有逐窗口裁剪与均匀重叠融合。每轮只运行一次全量 validation，晋级时复制该轮完整评分文件；若最终 best 仍为零初始化，重新评估实际桥接模型以记录真实推理成本，不能沿用纯 I3Net 的效率。
