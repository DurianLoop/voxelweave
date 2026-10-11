# MoEDiff-SR 完整范围与固定提交作者源文件核读

本次完整读现有PDF全部10页文字（1–9正文及第9页少量参考、10纯参考），视觉核1/4/6/7/8/9，共6页；完整读README和5份作者实现。不是新增论文：旧记录已定向读1–6/9，本次新增补齐7–8正文与10参考，旧页复读不重计新论文。原PDF6312305bytes、SHA e2591160fd07307106ff95152cd4c28b9cad5706c8edde4e94a4da5a7169ebd8；page1核标题、作者、arXiv2504.07308v1/2025-04-09与作者URL。LaTeX模板刊名不是发表证明。

## 方法和信息合同

3T T1→7T-like T1跨场强映射。训练184对3T/7T volume、7T的bias/gradient corrections；3T1.5mm和7T0.7mm各向同性体积重采260×310×260、slice256×256×3。p6明确写slice pairs随机8:1:1，本次仍无患者ID/split清单，不能认证患者外或家族独立。推断描述3T+Gaussian noise，不能当本项目仅固定CISS observed每4层的同信息动作。

p3 Eq2在token维softmax，再对全部tokens求专家Score；p4 Eq4给每专家Gi，Eq9把各专家latent加权求和。Fig2画全部三个专家，TableIV p8示例每个slice一组0.21/0.48/0.31权重。区域专家训练/自适应加权已有先例；这些公式和图不单独证明硬跳算或局部窗口有界执行。

训练p6：VQ-VAE128base、512embedding、1024codebook，AdamW1e-6、batch32、5000epochs，前1000epochs统一专家权重，diffusion T为E1=500/E2=2000/E3=1000；A10080GB。没有同曝光固定专家/固定混合的充分适配反事实实验，不能从各方法同数据/分辨率直接推断同训练预算。

## 公开费用和病灶证据

TableIII p8：ensemble133.02M/56.12G，asyn62.69M/42.21G；脚注明确后者是异步推断中**最昂贵的单个专家**。该行PSNR/SSIM/LPIPS/RMSE为空，没有完整采样路径、迭代分母、gate/encoder/decoder/preprocessing/transfer/全部专家/整患者wall time。1391/5612=24.78617%仅是打印数值差，不能当完整加速。仅异步调度不自动减少同一图所需运算，实际跳算与完整费用仍须执行证据。

TableI full b/g LPIPS=.0311；TableIII按p7给定10^-2单位，Ours1.18=.0118。3T reference .0896与8.96×.01一致，Ours差.0193的具体实验范围/原因未明确。记录该未解释数值/范围差，不猜作者修复或将不同表当同一可合并效应。

临床TableV/p8–9展示一个representative MS T1黑洞病例，正文承认3T/7T exact slice correspondence不能保证。没有临床患者总数、完整病灶标注、reader计数、Dice、敏感度、FP/漏检或CI，不将示例图和IRB号当定量患者外病灶验证。p9作者报告约45GB显存；不是本机实测，也不是本轮GPU资格。完整公开版本要在本机24455MiB显存上原样复现尚无执行方案，且当前新作业余量门槛未满足。

## 作者源码：以本次固定快照为准

论文URL https://github.com/ZWang78/MoEDiff-SR，匿名GET200，main commit `224fc36c38d3fec46a907a74c4bc0e090998ad89`。可见根6文件：README.md/data_loader.py/experts.py/moe_model.py/train_moediffer.py/vqvae.py。本次取得并完整读这5个py的.source.txt、全部HTTP200；不import/执行，不取weights/data。未另取得完整recursive tree或私有/其它branch，不断言作者真实论文实现只能是这份快照。

- **部署/跳算**：moe_model的MultiScaleSwinGating.forward平均所有tokens后Linear+softmax，输出B×3整图权重；MoEModel.forward无条件循环全部3experts，stack后加权。已取得5文件没有完整从3T+noise产生SR的reverse sampler、top-k/硬跳算或异步runner。不能把training forward当部署费用复现。
- **公式与实现分开**：printed Eq4是两个独立softmax因子的乘积；K=3全相同Score/usage时每Gi=1/9，总1/3，Eq9等值latent1会输出1/3。TableIV权重总1。源码实际是普通softmax，不是该Eq4乘积；没有因此声称源码权重不归一。源码T在MAD为0时floor1e-8，variance也有epsilon，不把纸面零除推论当作者运行失败。
- **接口矛盾（静态）**：train传timesteps=[500,1000,2000]，model的共同schedule按标量timesteps+1、Embedding需要整数；vqvae(in_ch=1)之后encode 3ch的7T_input；VQ embedding512与MoE base_ch128不匹配expert融合的通道约定。模型F.pad(acp[:-1],(0,0))保持T-1元素，default100时与T元素betas不匹配。不是实际作者runtime stack或本机复现失败，没有运行到这些位置。
- **模块和权重（静态）**：experts三个类共16个self层序列存普通Python list，没有ModuleList/Sequential注册。按PyTorch模块注册约定，列表中的子模块不自动进入parameters/state_dict/.to遍历。train的moe.apply(init_weights)遍历Conv/BN/Linear，包含已加载并冻结的VGG子网；源码的“pretrained perceptual”与该初始化步骤有差别。本轮未构造对象或测实际参数/显存。
- **训练分布/配方**：data_loader明确g/b为zeros占位；train VQ预训5000epochs、MoE3000epochs/Adam1e-4，无论文前1000epochs统一gate配方/所述scheduler。MoE的conditional feature直接area interpolate到8×8再expand，不是全文描述的条件token重映；像素VGG/梯度均值/global FFT loss与论文latent VGG/Sobel+FFT/multiscale STFT不同。requires_grad=False后VQ仍未eval，源码VectorQuantizer在training会EMA更新；冻结参数不等于所有buffers冻结。没有数据划分/验证/test/资源profile入口，外部预分目录仍未知。

以上限制阻止本轮把这份公开快照当论文canonical效果/完整费用复现，并不抹去论文区域专家/恢复收益排序的先例，不以作者实现差异证明本项目新颖性或论文结果无效。CPU只做打印表算术、Fraction公式和AST元信息，没有运行作者源代码、神经forward或MRI实验。

## 对本项目的可证伪后续

新增具体对照检查：如果gate之前所有动作输出都已生成，必须全部计入费用；全专家soft ensemble/固定normalized mixture与实际硬跳算策略在同合法信息/任务适配/训练曝光下比较，逐患者同时报告完整端点和总成本。global weight、token attention、参数使用峰值、ROI面积均不能替代实际跳过调用和window union成本。

科学主候选仍为**充分适配后固定observed合法动作是否有真实病灶可恢复余量；若有，按当前状态增益和完整实测成本分配能否超越匹配强控制**。期望gain排名已与既有cost-sensitive/defer相同，区域专家也已存在，不能包装算法首创；若无稳定余量保留负结果。见[后续控制准备](FULL_FLOW_DENSE_ENSEMBLE_CONTROL_PREPARATION.md)。

原两final/真实exit0→既有V3全56FOV/六gates/strict→三observed19series真实资源/另冻充分适配→合法动作余量/全费用强控制→全冻结后8未见一次确认；当前无可发表且经验证MRI claim。
