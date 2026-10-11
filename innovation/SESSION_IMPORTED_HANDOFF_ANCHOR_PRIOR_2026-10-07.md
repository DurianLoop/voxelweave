# 用户提供接续摘要的归档

本文件保存本轮可见用户提供的压缩前接续信息，属于摘要归档，不能称压缩前逐字完整对话。原始研究证据、历史完整可见消息和旧 SESSION 文档保持原文件及 SHA。

用户原目标：持续研究、探索、验证直到获得可发表 claim，GPU已授权；不操作、重启或迁移用户终端训练，不枚举/修改其他PID。新文件只写 D:/MRI/innovation，不改根.gitignore/environment.yml，不委派代理。Python D:/conda/envs/MRI/python.exe，PowerShell显式传递退出。

队列：11开发患者/19series，4已见验证患者/9series，8确认患者/12series关闭，locked IXI关闭。旧MIRA/MSValid84确认证据保留，当前病灶线尚无确认。fresh calibration只约束正式风险保证，不是经验MRI效益论文额外硬门槛。goal active。

必须先续原session99542，不重启。交接最新tool6c40e0仍live，native11880/new11781，累计26540.60200199997s；GPU637724于2026-10-07 22:59:56剩1394MiB/24455MiB/util87%，未达新GPU8GB余量。两臂各19998/总39996、CPU4/interop1/float32、共同初始化/监督/增强、AdamW lr/wd=.0001、30h/8GB/250MB不变。PCHIP99仅历史，真实exit0+两臂最终冻结后才原56FOV/6gates/strict，不读中间MRI效益，float解释不覆盖旧direct absolute失败。

上一轮入口SESSION_RESULT_OBSERVED_ROI、CHECKPOINT_RECEIPT、literature/observed_roi_stage_manifest及OBSERVED_ROI_TO_NET_BENEFIT_CLAIM_PREPARATION。归档0fb056 exit0：158stage/1708累计证据/23002490bytes，前1516hash不变；finalize12c4b6 exit0，根hash不变。旧QDA/LDA16series/8患者/4method支持共64，新3D费用独立核3456plane；joint_QDA N521/k209、省55.1371%，旧前景覆盖5.3781%/boundary6.0097%、原gate0/16。新是窗口费用，不能把旧低覆盖当新临床失败/成功。生产bba1ca、核验1a70af exit0。

上一轮真实observed输入探针：2mm冻结ROI缺层PCHIP赋值linear，anchors/tail不变；16series/64候选实际k=几何k、4156window逐位相同；540786、2ec36b exit0，80dc21字段误取exit1原样保留。合计33observed读取，0新GT/native/model/GPU/train；不是最终模型等价或MRI效益/真实提速。补读Skip-Convolutions2021与MotionDeltaCNN2023，17文字页/4视觉页，task+cost、动态ROI/cache/reset已有先例，GT框/首mask/部分计时/低batch减速/context非等价已记录。

需纳上一轮post appendices：SESSION_FINAL_TOOL_OBSERVATIONS_OBSERVED_ROI、POST_ARCHIVE_OBSERVED_ROI_UPDATE、CHECKPOINT_RECEIPT_OBSERVED_ROI、OBSERVED_EXITS_FINALIZE_OBSERVED_ROI、experiments/finalize_observed_roi_checkpoint。

本阶段协议已冻结：MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_PROTOCOL/RUNTIME_ADDENDUM/SERIAL_EXECUTION_ADDENDUM。全部19series/11患者整患者LOPO，10训练患者，仅observedMRI/observed标签。复用9通道feature_plane/normalization，所有19预测保存后才完整GT评分。主joint_QDA_balanced_prior_19只改priors=[.5,.5]；同队列empirical QDA及64trees/maxdepth16/maxleaf256/minleaf5/sqrt/bootstrapFalse/seed20261007的ExtraTrees为对照。每series/class<=8192 observed无放回样本，SHA种子+PCG64排序，class/series/patient权重均衡，fit/predict n_jobs1。固定0.5/原2mm/原gates/原窗口batch费用；不调阈值/半径、不挑最佳更名/删病例。CPU1/below-normal/1800s/8GBRAM磁盘/新阶段含依赖250MB。不校准概率，不风险证书，无MRI效益claim。

隔离依赖：19d435 exit1 sklearn缺失；MRI Python3.12.13/numpy2.4.3/scipy1.17.1。sklearn1.7.2/joblib1.5.2/threadpoolctl3.6.0仅innovation/tools/anchor_forest_runtime_v4内，c8677b exit0，38752060bytes，官方SHA/导入版本通过。不改根环境。失败405648 pip临时metadata权限、c77a29 joblibTLS EOF、1e0bc7 Schannel SEC_E_NO_CREDENTIALS保留；d16896 TLS1.2 joblib公开GET成功，wheelSHA4e1f0bdbb987e6d843c70cf43714cb276623def372df3c22fe5266b2670bc241；v4复用核过3wheel解包，无新GET。均非审批拒绝，无需用户许可。

v1诊断8a9599 exit1/47.9635784s：19observedMRI+19observed标签准备完成，矩/样本NPZ/SHA保存，QDAfit1/balanced1/forest0/预测0/完整GT0/prohibited=[]；joblib ThreadPool内部multiprocessing.SimpleQueue/connection.Pipe/_winapi.CreateFile WinError5。原sourceSHAa204e8d4d7675eb4ffe20a818035829c58f43980146d88870b4715feb2dc7ccc。

v2诊断1585da exit1/0.0535686s，AssertionError、0医学数组/forest/GT；交接尚未读traceback，怀疑PowerShell中文编码待实证。v2创建07bb98 exit0；复用19已准备矩/样本核SHA，不重复准备。已执行版本不可覆盖，修正用新版本。独立核验源码尚未执行，预计重建label indices/moments、CholeskyQDA、复拟合11forest并核704trees、leaf累加硬预测、physicaldisk/GTboundary/Fraction/window。需核float权重表达结合顺序，不为通过移除检查；共享feature/SciPy/sklearn traversal必须声明。

真正observed标签前景：001=[236,195]；002=[1753,291]；004=756；005=[12596,3389]；006=[5973,5293,2160]；007=344；009=[34283,78279]；010=[51756,719,203]；011=57；012=48208；013=175，均非0。预检14ee6a误命名旧label_foreground为observed foreground；实际是完整GT来源、未用于训练。001旧fold priors=[.9973414621153135,.0026585378846865374]。

接续要求：先poll99542；定位v2失败，新版本继续；三方法全19预测后评分并独立核验；结合覆盖与费用判断合法ROI空间，不能只报recall或用开发诊断冒充发表收益；当前阶段对话/账本/manifest归档，核前1708SHA，排除liveinvocation/history/resume；goal仍active、实质progress。
