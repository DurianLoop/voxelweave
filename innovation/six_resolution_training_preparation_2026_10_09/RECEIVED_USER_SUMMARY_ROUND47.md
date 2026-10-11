## 目标与约束

继续 active goal：**一直研究探索验证，直到得到可发表且独立确认的 claim，不动用户原终端训练进程**。上一轮是实质 progress，本轮也已新增论文与运行中诊断；未达到发表目标，不标 complete/blocked。

- PowerShell，cwd `D:\MRI`；Python：`D:\conda\envs\MRI\python.exe -B -X utf8`。
- 新增只写 `D:\MRI\innovation`；不安装、不委派、不删除历史、不枚举/修改其他 PID。
- 已执行或冻结源码不编辑，修复另版本。
- CPU1/interop1/below-normal；RAM、磁盘各保留十进制8GB。
- GPU已授权：起始free≥8192MiB，allocator≤10%，peak≤2.5GB，runtime free≥4GB；FP32、TF32 off、deterministic。
- 概率/强度3e-6，坐标3e-12，二值零差，医学六gate不降低。
- 11开发患者19series；4已见验证9series不可作为新确认；8未见确认12series及lockedIXI关闭。
- 含全部11开发GT的19998 parent仅开发能力诊断，严格LOPO必须cold-init。
- 本接续未使用skill、未委派。

## 先接续两个真实 live handle

### 58242：全192tile逐层CPU/GPU定位

运行：

`gpu_full_fov_and_atomic_capture_2026_10_09/diagnose_all_tiles_layerwise.py`

最新实际 `32670a` 仍带session_id：

- 33/96 batches，elapsed407.00秒。
- 192唯一tile，2tile/batch，每设备重复两次，预期各384实际tile forwards。
- 48叶模块输出＋probability，共49字段；CPU独立functional，GPU只读hooks。
- 每设备重复的49字段必须逐位同。
- 最后重建完整FOV，CPU/GPU概率SHA必须复现原失败；不是医学评价。
- journal≤3MB，共享FOV stage20MB，OTHER22.8MB，wall3600秒。
- 输出：`layerwise_all_tiles_attempt01/receipt.json`、`batches.jsonl.gz`、`frozen_config.json`。
- 尚未terminal，不归档该attempt，不提前宣称完整成功。

已观察prefix：

- 首卷积 `encoders.0.layers.0` 到至少25batch最大误差为0。
- 第一InstanceNorm最大误差3.0517578125e-5。
- 后续卷积/归一化/heads差异继续出现。
- 到17batch的tile概率最大误差1.615285873413086e-5；融合后原native FOV差5.3346e-6。
- 只是逐层现象，不能当单一因果解释。等全96结束再定干预。

terminal后保存实际tool return和session58242，再独立枚举96batch×49字段、192tile及hash复现。成功exit0只是诊断完成，原概率gate依然失败。

### 44317：原完整35904数值合同

仍运行：

`full_certified_schedule_2026_10_09/qualify_full_real_pipeline.py`

最新实际 `a07ffb`：

- 6480/35904，elapsed6889.20秒。
- 强度各误差0，坐标1.1368683772161603e-13。
- 仍session_id。**不重启**。
- 真正exit0无session_id才写 `ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json`，附 `observed_unified_exec_session=44317`，再执行 `audit_full_real_terminal_v2.py`。
- live `full_real_pipeline_attempt01`始终排除冻结归档。

## 上一轮已经结束并冻结，不重复

最新冻结链：

`six_resolution_training_preparation_2026_10_09/APPEND_ROUND46_INDEX.json`

- 累计7380，SHA `ab87e6883439aed33c7e6291cb760a6645042de52d6e20d86b700e16294bbc66`。
- 原7291逻辑SHA全部保持；新增89。
- archive actual `a64c61`/session72192 exit0。
- `POST_ARCHIVE_HANDOFF_ROUND46.md`、实际archive terminal、最终答复是归档后静态文件，下次增量绑定。

已结束：

- 19series资格：228 GPU更新、114 reset分支，各连续两步；terminal78758→ffb4af exit0，独立审核通过。
- 选择性插值：67821→aac516 exit0，228完整batch逐位GPU input SHA复现、456patch，独立420c96通过。失败大体积12配对原始/support逐位相同；49.0512s→4.81568s，约10.1857倍。**未全35904重新资格，未接入正式训练**。
- 原38FOV attempt：74453→e47835 exit1，第3series native_reference差5.3346157e-6>3e-6，二值0差；只做3/38。
- channels_last诊断25418→4e77ea exit0，但概率SHA与contiguous相同、无改善且更慢。
- CPU InstanceNorm诊断15492→e388fa exit0，概率差6.6161156e-6，推理49.24s vs5.34s，更差更慢，停止此方案。
- 两负诊断独立audit0c6a9d通过，仍full38=false。
- 首次layout诊断79699→89ca59因CPU输入模块将CUDA_VISIBLE_DEVICES=-1失败，v2在imports后恢复0。旧失败保留。
- checkpoint透明压缩只回收359472bytes，不重复或扩大压缩范围。

六臂入口最新是 `run_six_resolution_training_v3.py` / `build_deployment_qualification_v3.py`。真实预检ready=false：

- 完整family104156359bytes，保留旧allowance。
- 前次磁盘缺约49.2MB。
- 缺35904终态/审核、full38资格、磁盘准入。
- 无 `FULL_GPU_DEPLOYMENT_QUALIFICATION_V3.json`，未正式训练。
- 原完整grid六臂训练点估计25.208h；选择性candidate-only新估计另存，不能覆盖旧结果或当完整wall。

## 本轮新读GIN作者稿，尚未冻结provenance

目录均在：

`six_resolution_training_preparation_2026_10_09`

新增脚本/协议及actual结果：

1. `locate_gin_author_version.py`
   - arXiv唯一找到 **2111.12525v5**，七作者与TMI DOI10.1109/TMI.2022.3224067一致。
   - OpenAlex429保留，不重试绕限流。
   - **arXiv comment明确该稿是early non-peer-reviewed version，期刊final substantially revised**，final地址IEEE9961940。不可把此稿当final。
2. `fetch_gin_primary_html.py` 首次bs4缺失，实际e57dcc exit1，未联网/未生成attempt。不安装。
3. `fetch_gin_primary_html_v2.py` 使用stdlib HTMLParser，actual20a20b exit0。
   - 固定 `https://arxiv.org/html/2111.12525v5`。
   - `gin_primary_html_attempt02/primary.html.gz` SHA `a7977cbc4a6abf1666e6ec1ea7d2c3758b3ab1604f74e16d7935b0f43bd3017b`。
   - 提取105块、207math节点、13HTML tables。
4. 已实际完整读取 **0–103共104提取块**，refs heading104未计，参考列表未读。
   - `read_gin_ranges.py` 范围：0:30、30:49、49:74、74:87、87:104。
   - 实际tool：324bde、95f321、321082、14ecf6、9411b1，均未截断。
   - 13HTML tables实际是6公式布局＋4独立数据表，其中TableIII嵌套表重复，**数据表计4，不计13**。
   - `read_gin_auxiliary.py` actual b6d2a9补读遗漏Algorithm1全文及table身份/arXiv comment。
   - 图像像素、外部supplement、final PDF未读。
   - 一次临时shell regex报价错误05f34d保留；后用脚本成功。

论文关键判断：

- GIN为随机Gaussian浅卷积＋LeakyReLU，四层/隐藏2通道；随机α混合后 **Frobenius norm归一化**，不能只实现DG-TTA简化blend。
- IPA为两GIN输出用低频空间变化权重互补混合，避免用GT mask使目标突出形成捷径。
- 论文因果模型明确假设acquisition与content独立且跨域content不变；不能套到本项目患者/病灶构成变化，不能把普通模拟增强当实际物理采集干预。
- TableIV GIN→GIN+IPA：腹部86.04→86.31，心脏83.83→85.01，前列腺65.10→70.37，器官各有取舍。
- 作者承认源域腹部约−2.0、前列腺约−1.0 Dice points。
- 宽泛“采集不变特征/破背景相关/空间变强度增强”已有先例；候选仍需强普通对照之后的真实paired病灶净收益增量。

## 作者源码已取得和核读

arXiv comment提供官方repo：

`cheng-01037/Causality-Medical-Image-Domain-Generalization`

固定commit：

`d4d5056ded88951fc3967f8f294f4a12420e13c6`（2022-11-28）

- `fetch_gin_author_tree.py` actual981dac exit0。
- `fetch_gin_selected_code.py` actual0af449 exit0。
- 七文件下载并核Git blob SHA1，未执行。
- `gin_selected_author_code_attempt01/*.source.txt`

完整实际读六文件，共 **1122行**：

- README122
- configs_exp107
- imagefilter.py96
- imagefilter3d.py102
- exp_trainer.py379
- dev_traintest_ginipa.py316

实际tool：05a56a、80d0cd、e077d3、019837，未截断。

第七文件 `adv_bias.py`367行只读两段：

- 170–269，共100行。
- 288–367，共80行。
- actuald8697a。
- **270–287及1–169尚未读**；rg定位c430ab被截断，不算全文。

代码关键：

- 已有3D GIN，不是我们新发明的3D移植。README明确3D IPA尚待发布。
- GroupConv每sample独立Gaussian kernel与Gaussian bias，kernel从1/3选，四层/隐藏2，末层无activation。
- Frobenius分母代码含1e-5。
- trainer实际生成 **三份**GIN视图，IPA互补混合前两份，第三份保持GIN。
- CE＋Dice只对第一份视图；三份预测softmax均值作为KL target，`KLDivLoss()`默认reduction，target源码未detach。
- **不要把它自动称主文两视图Eq3精确实现或forward JS**；KL方向为KL(mean||each)，当前/旧Torch target梯度语义需另核，不凭静态代码宣称错误。
- trainer IPA设置interpolation_order=2/downscale2，主文写cubic；需要继续读bias完整构造及bspline helper，**尚不能断言degree不一致**。
- 原训练脚本每250epoch评价target并记录；未见由target选择checkpoint的直接语句。不要无依据指控泄漏，也不能认作一次独立确认。
- 代码与公开稿/final配置关系需保留边界。

## 缓存与下一步

本轮尚未写最终阅读provenance、科研结果、公开对话、导出tool buffers、归档或最终回复。

缓存已有：

- `turn47_layerwise_session`=58242。
- `turn47_layerwise_start`
- `turn47_initial_0..2`
- `turn47_parallel_0..2`
- `turn47_primary_follow_0..2`
- `turn47_html_v2_0..1`
- `turn47_reading1_0..2`
- `turn47_reading2_0..2`
- `turn47_reading3_0..2`
- `turn47_aux_0..2`
- `turn47_author_and_layer_0..2`
- `turn47_code_fetch_0..2`
- `turn47_code_read1_0..3`
- `turn47_code_read2_0..2`

优先：

1. poll58242/44317，依据真实terminal处理，不重启。
2. 完成192tile诊断后独立审核，再选一个有依据的算术/后端干预；原全CPU norm/channels_last不重复。
3. 补bias缺失段及核bspline构造；冻结GIN阅读provenance和源码范围，明确early稿/final差别。
4. 为GIN-only及GIN+IPA/consistency建立具体同预算强对照准备；不可用GT生成augmentation，不直接执行作者repo，不靠改名声称创新。
5. 继续解决数值资格与完整资源条件，不能用所选456字段替代35904或临床增益。
6. 保存本轮可见对话、实际缓存及失败；接7380归档，排除所有live attempt，保持goal active。
