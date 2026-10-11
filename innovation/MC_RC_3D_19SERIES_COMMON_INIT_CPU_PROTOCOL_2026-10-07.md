# 19series共同随机初始化的正式CPU任务训练协议

本协议在新的多患者训练、任务效果或验证效果打开前冻结。目标是建立同容量/监督/预算的native信息上限与observed-only PCHIP任务候选，检查充分训练后任务能力。不是重建方法创新，不称nnU-Net官方规划器复现，不以训练完成代替强能力认证。上一低LR阶段已经归档，旧失败和全部证据不回改。

## 已有实测与资源预算

11开发患者19series，缓存单臂1,909,712,000 bytes；资源更新median native1.71855s、PCHIP1.70218s；两臂完整开发FOV358.20/395.83s、各1139tiles。依据完整资源结果正式冻结**各19,998更新**，共39,996；19,998=1818完整患者轮×11，每患者1818步。纯更新median估算19.00小时，样本max估算20.57小时；未来耗时不受这两个估值保证。cache、checkpoint、正式随机初始化模型速度、独立核验和四验证额外成本另计。

CPU4 intra-op/1interop、float32、自身below-normal，不控制其他进程；无CUDA。所有文件只在innovation；本新阶段累计保存<=250,000,000 bytes，RAM与磁盘各留8,000,000,000 bytes。正式训练累计实际进程墙钟上限90,000s（25h），每步检查累计时间与资源；该上限只约束训练，不包含未来独立评价/核验，它们需要另设有界协议。GPU原8GB启动/4GB运行余量/2.5GB peak门槛保持；本CPU实验不得中途换设备或精度。未来GPU正式训练另立共同配方，不操作用户终端训练。

执行分段但预算不按效果更改。先跑每臂99步（9完整患者轮）的可恢复短段，1200s墙钟上限；后续继续相同优化器状态、相同流至19,998，保留真实退出。短段是本正式训练前99步，不是丢弃资源更新；此前66资源更新全部不累计。第一段不计算MRI任务端点。若数值/来源/资源失败，记录并停止，不静默跳样本、换LR或把另一臂继续成不匹配比较。每99步和正常短段结束提交断点；突发中断存在未提交日志时拒绝静默继续，保留后另审。

## 固定输入、模型与优化

开发患者为001/002/004/005/006/007/009/010/011/012/013。验证患者020/022/024/025仅在本训练入口核已存在角色元数据，**不读其MRI/GT或效果**。确认030/029/019/028/031/026/027/015及locked IXI test不读。

native只能由已认证完整native loader读取，作为信息上限；PCHIP只能由真实每4层observed包构造，不读取隐藏MR像素。两臂用相同observed全体mean/std，名义0.5mm物理grid与取整后的实际affine保持；MR trilinear、标签用已修正像素中心精确nearest整数映射。严格核每series image/label hash与已有19series资源资格缓存记录；不保存native或physical完整体积缓存。

现有1,401,363参数3D U-Net（16/32/64/128、IN、LeakyReLU、三decoder heads）、PATCH64×128×128、batch2、深监督BCE+Dice权重4/7、2/7、1/7原样。**两臂从同一seed20261007的全新随机state_dict开始**，不从单001拟合或丢弃资源权重接续。AdamW恒定LR=.0001、weight_decay=.0001；无scheduler、无warmup、无新loss或归一化。LR依据开发内低LR控制选择，不能称唯一最优。

患者按ID、series按UID排序。每轮用SeedSequence([20261007,611])流置换11患者，各患者内series用独立SeedSequence([20261007,610,patient_index])流循环随机置换；患者内每次完整deck含全部series一次，最后截断deck每series更新数差<=1。固定整数序列表保存并SHA绑定，两臂完全共用。第k步sample_batch RNG=SeedSequence([20261007,612,k])；同强制FG/背景中心clamp、三轴mirroring、scale[.9,1.1]/shift[-.1,.1]，两臂逐batch GT和augmentation primitive必须一致。已知clamp边界概率偏倚保留，不将此采样包装首创。

每步记录患者/UID、input/GT SHA、全部primitive、FG计数、loss/LR、真实耗时；loss/所有梯度/更新后参数均有限，首步encoder/decoder/ups/heads非零。checkpoint含state_dict、AdamW moments/step、torch RNG、已完成步数和绑定hash；原子提交和恢复校验，以独立合成连续vs保存恢复的严格相等资格验证。预检不读MRI像素，不把合成核验称MRI泛化。

## 最后模型和后续资格

只采用每臂最后19,998模型。保存中间断点用于恢复，不按其训练loss或开发/验证效果挑最佳模型。**两臂最后权重都冻结后**另立评价入口，对开发19series和已见验证9series全FOV、半patch stride、正Gaussian blending、native概率回映、阈值.5，无GT ROI/connected component过滤/TTA；full/anchors/missing/tail全分母和空undefined保留。当前训练入口无任务评分。

原四验证能力门槛原样：病例内先series均值、再四患者均值；full Dice>=.70、missing Dice>=.65、full recall>=.70、full absRVE<=.50；四患者full/missing Dice均>0，全部9series full TP>0。两臂均报告；部署候选PCHIP需要全部通过，native参照失败也必须解释，不能用差值声称SR收益。之前开发label roundtrip的011失败保留，不删病例、不提高阈值或改网格救结果。

只有充分能力和公平基线资格之后才开展6×5、同observed直接任务、分辨率随机化和具体修正残余探索；收益头必须与双路径成本头、已知defer、普通风险/误差、预算随机对照。全部方法/阈值/端点/预算冻结后才八确认和第二独立训练网络。当前科学确认0、已确认可发表claim0、goal active。

[实测资源](MC_RC_3D_19SERIES_CPU_RESOURCE_AND_FOV_RESULT_2026-10-07.md) · [上一阶段closing receipt](SESSION_CLOSING_RECEIPT_LOW_LR_CONTEXT_2026-10-07.json) · [原验证gate实现](experiments/mc_rc_intensity_only_evaluation_binding_cpu.py) · [创新排重判断](INNOVATION_DECISION_AFTER_DEFER_READING_2026-10-07.md)。
