## 目标与约束

继续 active goal：**持续研究、探索、验证，直到取得可发表且独立确认的 claim；不动用户原终端训练进程。** ROUND50 有新数学验证、真实失败及论文阅读进展，不是 blocked；尚未达成 claim。

- 工作区 `D:\MRI`，PowerShell；Python：`D:\conda\envs\MRI\python.exe -B -X utf8`。
- 新增仅写 `innovation`；不安装、不委派、不删除历史、不枚举或修改其他 PID。
- 已执行或冻结代码不编辑；修改另版本。
- CPU1/interop1/below-normal；RAM/disk 各保留十进制8GB。
- GPU已获授权：启动free≥8192MiB；allocator≤min(10%,2.4GB/total)，peak≤2.5GB，runtimefree≥4GB；FP32/TF32off/deterministic。
- 数值gate3e-6、坐标3e-12、二值零差；六医学gate不降低。
- 开发11患者19series；4已见验证9series不作新确认；8未见确认12series及lockedIXI关闭。19998 parent见全部开发GT，仅开发诊断；strict LOPO必须cold-init。
- 所有可见对话、实际工具结果、失败和准备保存到innovation；不补造旧聊天或隐藏推理。

## 冻结状态与唯一 live 作业

ROUND49已归档、独立post-check通过：

`innovation/six_resolution_training_preparation_2026_10_09/APPEND_ROUND49_INDEX.json`

- 原7538全部SHA/bytes保持，新增101，累计**7639**。
- index SHA：`6a76ef3d2e183e1df4cb757c0124ab9bfd593ffb332171bb9350e4059c945aa2`
- archive actual `2c9528` exit0；post-check `93c40d` exit0。
- 接续入口：`POST_ARCHIVE_HANDOFF_ROUND49.md`。
- **ROUND50尚未归档、导出buffers或写最终科研总结。**

唯一live仍是 `qualify_full_real_pipeline.py`，session **44317**，不要重启。

最新真实poll：`fdd63f`仍带session_id，缓存 `round50_initial_1`：

- **12840/35904**，elapsed14072.5006秒。
- 强度/support误差0，coordinate1.1368683772161603e-13。
- 仅真实exit0/no session后，保存actual terminal及44317，再跑 `audit_full_real_terminal_v2.py`。
- `full_certified_schedule_2026_10_09/full_real_pipeline_attempt01`继续排除归档。

ROUND50没有其他live作业。

## ROUND50：高精度CPU参考

均在 `six_resolution_training_preparation_2026_10_09`。

新增：

- `GIN_HIGH_PRECISION_CPU_REFERENCE_PROTOCOL_V2.md`
- `gin_cpu_differentiable_reference_v2.py`
- `verify_stable_norm_math_v2.py`
- `prepare_cpu_reference_verification_v2.py`
- `verify_gin_cpu_reference_v2.py`

v2保留FP32参数、conv/transpose/pool/head/optimizer；只将InstanceNorm统计、affine及反向归约显式置于float64，再cast回FP32。没有修改production或旧v1。

独立norm数学检查：

- `stable_norm_math_v2_attempt01/receipt.json`
- actual **ce605e exit0/no session**。
- 独立NumPy double output/dx/dgamma/dbeta误差≤3.6e-15；FP32 cast分支四项误差全部0。
- 预注册有限差分检查通过。
- 无MRI/GT/CUDA/optimizer更新。
- **这次actual完整返回没有store**；receipt与可见chunk存在。记录终态元数据即可，不伪造缓存。

完整人工模型检查失败：

- generation **d9b50e exit0**，缓存 `round50_verifier_generation`。
- verifier **72eb87 exit1/no session**，缓存 `round50_verify_or_prior_0`。
- `gin_cpu_reference_verification_attempt02/receipt.json`
- 原16³、3view、两step协议；实际只完成两分支step0，各1次CPU更新，合计**2人工CPU optimizer updates**。
- loss0，prob6.55651e-7，grad5.49480e-8，moment5.47152e-9；
- **parameter1.0646414e-5>3e-6**，停止，step1未运行。
- 未运行新GPU/真实19series；不要跳过人工失败启动完整资格。
- 尚未取失败坐标两侧梯度，不断言该新失败的具体坐标原因。
- 数学正确不等于与FP32完整训练状态通过一致性gate。

ROUND49的真实IN归因和有限差分失败保持原状；不得降低gate或修改旧receipt。

## ROUND50：新论文批次

新目录：

`innovation/adaptive_acquisition_primary_followup_2026_10_09`

**新目录cap2MB**。guard需加入它：

`free −22.8MB −(7MB−prep_actual) −(20MB−FOV_actual) −(6MB−accepted_actual) −(2MB−adaptive_actual) ≥8GB`

其余cap和六臂104156359预算保持。新目录不是2MB已占用额，需扣未花余量。磁盘余量很紧，不能再随意增加大PDF预算。

文件：

- `PROTOCOL.md`
- `locate_public_adaptive_sources_v1.py`
- `PRIMARY_SELECTION.md`
- `fetch_primary_html_v1.py`
- `read_primary_range_v1.py`

先查重发现旧队列的MASC2602.00348、fairness2604.10904、TADT2408.08736**已经全文读过**，没有重复计数。

新索引actual **b22c34 exit0**，缓存 `round50_source_locator_start`。两次官方arXiv API均200，七条摘要已读，摘要不计正文。选定：

1. **Experimental design for MRI by greedy policy search**，Bakker/van Hoof/Welling，**2010.16262v2**。
2. **OpenMASC: An Open-Source Pipeline for Cross-Trajectory Metal-Aware Sampling and Correction in Accelerated MRI**，**2609.32343v1**；是已读MASC系列后续研究，不当独立重复验证。
3. **Active few-shot segmentation by reinforcing data selection**，**2607.22371v1**。

官方固定版本HTML获取actual **12bd7f exit0**，缓存 `round50_primary_fetch_start`。全部身份匹配成功；原HTML、blocks、MathML、tables、image链接等gzip保存。没有PDF、没有执行作者代码、没有实际读取图像像素。

### 实际阅读位置

`primary_html_attempt01/<name>/blocks.json.gz`

- **active_fewshot：0–58全部blocks已读**。chunk `c08feb`、`96b523`；缓存 `round50_read_fewshot_0_35`、`round50_read_fewshot_35_59`。
- **openmasc：0–119全部blocks已读**。chunk `4903d0`、`3400a1`、`a6078f`；缓存对应 `round50_read_openmasc_0_45`、`...45_84`、`...84_120`。
- **greedy：0–73已读**。主文0–72完整；73只有References标题。chunk `488d6f`、`d8940c`；缓存 `round50_read_greedy_0_38`、`...38_74`。
- **greedy appendix74–177尚未读，必须续读。**
- HTML参考列表没有被parser抽成blocks，不能称参考列表已读。
- 图像像素、外部supplement、作者代码均未读。
- 抽取及range receipt里的阅读false保持；完成后另立reading provenance。

### 已获得的关键边界

**Active few-shot：**

- 选择后需人工标注，再Reptile适配；不是无GT部署动作。
- 589个3D T2 images、8机构；NB/OI及机构3/4用于评估，156 volumes（74/82）。
- 原文另用8个带标签validation examples计算RL reward；不能只报K个标注预算。
- P=32，实际K固定4；K8/16通过重复随机pool选择，不是一次完整K集合优化。
- 8-channel/64 bottleneck 3D U-Net、GroupNorm；meta约24h、RL约72h，两A5000。没给本项目完整部署费用。
- Table1 combined：Random51.2/57.9/63.9；Proposed59.4/65.5/70.6。
- 文本K4提升8.1/4.5，而显示均值差8.2/4.6；可能是舍入，不能断言错误。
- RL reward究竟如何与held-out机构隔离需代码/ID核验，不认证无泄漏。
- 联合集合补充性及适配后任务收益已有直接先例。

**OpenMASC：**

- DC Rectifier放在每cascade后；SSIM reward、PPO；三阶段冻结backbone并周期共同适配DCR。
- autoPET200 subjects，160/20/20；每36slice，test720slice。
- fastMRI800 knee volumes也是**合成metal artifact**；全文承认没有真实植入物验证、single-coil/2D。
- Table3：full SSIM.777/PSNR27.62；同架构VD随机.776/27.53；去co-train.776/27.55；去DCR.710/21.45。
- 因此架构整体领先不能全部归因主动policy；可做独立表格算术。
- paired t-test n720 slices不等于720独立患者，只有20测试subjects。
- 图像质量、额外采样与合成metal结论不当本项目病灶净收益。
- 共享weights跨trajectory是作者文字声明，未核代码。

**Greedy目前：**

- 动作新增k-space column，训练可模拟GT counterfactual，部署会增加测量信息；不同于固定observed上的处理动作。
- frozen16-channel reconstruction；greedy γ0、non-greedy γ1、γ.9，q8。
- NA Oracle在**test GT**上选全局平均最佳列，不是可部署控制。
- Table1 greedy比NA oracle微小增益，γ.9通常更高；没有普遍greedy理论保证。
- Figure3写使用test表现最佳模型；SSIM和SNR的train/test描述也需保留边界。
- appendix含费用、MI、更多实验，未读完不能提前总结。
- 后续可核MI是否充分区分图像adaptivity与mask/历史变化；目前仅待核问题，未做CPU验证。

## 已发本轮进度

1. 上轮实质进展，继续核验独立参考，保持原终端不改动。
2. 高精度norm数学通过、人工模型参数gate失败；转向主动采样与固定输入动作区别。
3. 用户请求checkpoint后已告知将保存接续记录、避免重复和虚报阅读。

## 下一步

1. 本checkpoint后先保存摘要/可见对话及可用ROUND50 buffers到innovation；**本摘要尚未落盘**。
2. 续读greedy74–177，每批约25–35blocks独立输出，避免外层截断。
3. 依据三篇实际原文写新颖性/强对照笔记；可核Table3架构与policy增量、费用/分母，不把论文算术当项目临床效益。
4. 若有必要，在2MB cap内下载少量关键HTML图像并实际view；否则明确像素未读。
5. 保存norm数学终态元数据、人工失败actual；独立audit数学及失败receipt，不重跑已完成检查。
6. poll44317确认live，不重启；终态按原流程处理。
7. 写ROUND50归档接**7639**，包含新adaptive目录，保持所有旧hash，排除live；guard加2MB新cap，独立post-check。
8. 保持goal active。当前无发表claim，不将数值工程、经典增强、已有路由或论文复核改称新方法。
