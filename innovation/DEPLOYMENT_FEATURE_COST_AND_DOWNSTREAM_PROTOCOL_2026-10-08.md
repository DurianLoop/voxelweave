# 本阶段执行前协议：特征实际成本与下游分割原文

上一[阶段](SESSION_RESULT_OBSERVED_HOLDOUT_2026-10-08.md)为progress：19真实series的合法观测留出特征和独立复核改变了权威结果，非单纯等待。当前原live99542已直接poll确认native17622／new17523／40049.99794589996s，无terminal exit；不重启／迁移或修改原训练。新GPU作业仍需8GB余量，当前1394MiB不足。

本次新增可执行工作：对**实际生产特征路径**进行一次完整19series CPU测量，以补已有资格核验时间不能当部署成本的缺口。源限定原11开发患者／19observed-only包；不读native MR、GT、缺失层、任务模型、验证、8确认或lockedIXI。全部旧协议、source和结果保留，结果另存新attempt。

使用已通过的fold／retained-statistics／source-projection／linear及local-PCHIP／post-prediction-reference模块。每series只载入一次，实际执行两fold、计算完整面内scores及17个特征，独立检查导出的17特征与上轮冻结表一致。无需重复38个counterfactual或独立Hermite核验；不保存MRI预测体积。先核原NPZ SHA及shape／affine／索引，费用中记录source-hash、IO/decode、source构造、两预测、reference投影、score、汇总／一致性核验和输出／审计开销。资格检查费用与真正生产路径计算费用分列；完整launcher墙时含冷import、子进程启动、输出和退出，不能把仅计算核心当整个部署成本。

CPU1／interop1／BLAS1、CUDA不可见、自身below-normal、1200s、8GB RAM／disk余量，每医学作业≤20MB。一次运行，无warmup或重复，计19 observed实际加载、神经／GPUforward／训练更新0。按患者合并该患者全部series的实测秒数，再患者等权；series逐列保留。冷／热缓存状态没有控制，系统原训练与其他GPU负载存在；不解释成benchmark分布、GPU速度或任务净预算优势。记录特征成本只用于后续完整动作成本，不生成动作标签或理论保证。

论文队列：取得Noise2Same**官方摘要已验证链接**的单独Supplemental，仅核Theorem1／2证明及相关normalization条件，不计新增独立论文；查找Prakash等“Leveraging self-supervised denoising for image segmentation”（ISBI2020）的公开元数据／作者稿，先核题名／作者／年份／DOI。Crossref和EuropePMC各一次精确题名发现，≤3MB/response，30s单GET；不再重试先前OpenAlex429路径。取得后逐页文字／必要图页实际核读并记录未读范围。根据检索出的真实链接下载，不猜arXivID；获取／提取不是阅读。不联系作者或其他人。

仅公开GET，PDF≤10MB，各attempt不得覆盖；portable pypdf／pypdfium2沿用已核SHA的innovation内runtime，不改MRI环境／根文件。默认沙箱Schannel凭据错误此前已确认，必要时经工具自动审批使用公开GET，TLS验证保持。本阶段完整归档≤30MB，不再复制／安装runtime，只绑定以前已冻结文件。

目标仍是强基线后的真实患者病灶净动作收益：原两臂final exit0／最终冻结→56FOV→6gates→strict→同信息同容量三臂→动作余量／完整成本→整患者收益预测与强对照→冻结确认。特征成本或去噪分割论文不是当前MRI收益claim的替代品。goal active。
