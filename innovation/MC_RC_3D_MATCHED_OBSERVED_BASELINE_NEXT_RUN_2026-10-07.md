# 后续公平任务实验：执行入口与未满足条件

当前19series共同初始化正式训练session99542仍live，本文件不启动、替换或迁移它。两通道资格及独立重放只证明可运行/输入正确；并未验证MRI任务拟合或泛化。GPU已由用户授权，但最新实际查询19:16:35.293只有1394MiB，低于既定8,000,000,000bytes新GPU启动门槛。

## 依赖与入口

1. 同session训练真实terminal exit0，两臂各19998；再按 `experiments/mc_rc_3d_19series_final_eval_2026_10_07.py` 的既有字段写final-exit receipt。不要用loss变小、快照或资格结果代替terminal证据。
2. 执行冻结的 `experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py` 和 `experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py`，完成56FOV及原四validation能力gates。如果失败先诊断；8确认不开放。
3. 新input模块 `experiments/mc_rc_3d_direct_observed_2026_10_07.py` 只从开发observed包构造两通道。主资格 `experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json`、独立 `experiments/mc_rc_3d_direct_observed_independent_2026_10_07/attempt01.json` 已真实通过。
4. 原能力通过后先另立真实资源资格，包含完整PATCH64×128×128、batch2、全部19series缓存及共同patient-first系列轮转；MRI开发GT仅在这项已授权监督训练入口读取，独立observed输入模块仍不接GT/native。对两个新arm真实forward/backward/优化、每branch梯度、保存恢复、FOV推断成本计量；丢弃资源资格权重。
5. 按实际资源结果冻结独立正式两臂训练budget、precision、device、共同初始化/抽样流、最终权重规则。GPU门槛满足则可使用；CPU/GPU不能中途迁移已有recipe。训练不按validation最优checkpoint挑选。两通道结果全部合格后再评估SR输入的公平matched adaptation。

## 必须保持的合同

- 输入0为dense normalized PCHIP或weighted direct numerator，输入1同一个fractional availability，完整FOV、真实observed stride4、同observed统计、同physical pixel-center map。PCHIP的尾层复制是固定已知预处理；direct尾区可能无支持，两者均来自同观测源，不能把前者称额外真实测量。
- native观测值在构造处逐位保留。physical重采样后的两种表示未证明可逆；“同信息范围”仅指相同原始observed源/metadata及无额外hidden source，不冒称physical变换信息损失完全相同。
- 两臂1,401,795参数，共同权重SHA7806fa169c4b8a9e930e0856ebd2944070f7de18c099a4a6e669c452939cc166。首层mask初值0，其余权重与当前live一通道seed20261007模型相同；原模型1,401,363，增加432。
- paired sampler需要一次产生foreground/random centers、起点、3轴flip、s,t，两臂完全复用；labels/ROI采样规则与任务相同。dense `s*x+t*valid_grid`；direct `s*numerator+t*availability`；mask不做灰度变换、padding0。新配方与旧sample_batch全patch加shift不同；保留one-channel及必要的padding因素对照，不能将所有差异归为mask或重建。
- 已知NConv/partial-conv若加入，architecture/normalization/优化会同时变动；需要独立强基线和实际总资源，不能把当前普通two-channel U-Net叫作者NConv复现。若做density robustness，还要另冻结整层phase/stride协议及相同mask信息，不能改当前stride4主实验。
- 同开发/4已见validation划分，patient-first统计完整19/9 series，不改变.5阈值以救结论；8保留confirm及locked IXI test关闭。输入MRI质量、native能力差距、任务效益、额外真实观测各自标明。

## 实际资源估算的边界

本轮19series一个physical float32 channel总954,856,000bytes。两臂共享availability/valid-grid/target时，dense+direct+availability+valid+target的五field数组约4,774,280,000bytes；它不包括解码临时数组、网络/optimizer、batch、cache元数据，也不是RAM/GPU实测峰值或训练预算。无需保存完整输入体积；未来可逐arm缓存避免重复峰值，实际资格后决定。

## 后续创新检验及失败路径

先回答充分适配的observed direct/PCHIP/SR是否存在稳定task差距。存在真实SR可修正余量后，才采真实GT-free local候选，测empty/single/pair/union的完整FOV输出及全部计算/搬运/cache warmup/policy训练成本。与error-risk、已知defer、同预算random、union-greedy比较；joint Dice变化需扣分式效应，避免把metric interaction当神经协同。

若direct或强PCHIP消除SR收益，记录受控负结果并评估独立benchmark价值；若收益存在但不可由observed预测，停止部署policy正向claim；若known risk/defer或union-greedy已经解释收益，不能把重新命名当新方法。开发选择完成后再冻结8确认与第二task网络recipe。当前尚无新可发表claim。
