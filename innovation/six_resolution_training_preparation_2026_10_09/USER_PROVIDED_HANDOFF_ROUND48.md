## 目标与约束

继续 active goal：**研究、探索、验证，直到得到可发表且独立确认的 claim；不动用户原终端训练进程**。本轮是实质 progress，目标未完成、不应标 blocked。

- cwd `D:\MRI`，PowerShell，Python：`D:\conda\envs\MRI\python.exe -B -X utf8`。
- 新增只写 `innovation`；不安装、不委派、不删除历史、不枚举/修改其他 PID。
- 已执行/冻结代码不编辑，修改另版本。
- CPU1/interop1/below-normal；RAM、磁盘各保留十进制8GB。
- GPU已授权：启动 free≥8192MiB；allocator≤min(10%,2.4GB/total)，peak≤2.5GB，runtime free≥4GB；FP32、TF32off、deterministic。
- 概率/强度3e-6，坐标3e-12，二值零差；医学六gate不降低。
- 11开发患者19series；4已见验证9series不作新确认；8未见确认12series、lockedIXI关闭。
- 19998 parent含全部11开发GT，仅开发能力诊断；严格LOPO必须cold-init。
- 未获得独立确认可发表claim。

## 最新冻结链及本轮状态

上一轮冻结：
`innovation/six_resolution_training_preparation_2026_10_09/APPEND_ROUND47_INDEX.json`

- 累计7457，SHA `c43c7dd3286c266280ff0137b6242ee629dffcdbde1d75cd18d320d371943608`。
- 原7380全部保持，新77。
- actual archive `79da4f` exit0/no session。
- 入口 `POST_ARCHIVE_HANDOFF_ROUND47.md`。
- **本轮 ROUND48 尚未记录阅读provenance、对话、导出buffers、归档或最终答复。**

## 两个真实 handle：先处理

### 6897 已真实终态，不能再当 live

运行：
`gpu_full_fov_and_atomic_capture_2026_10_09/diagnose_same_input_operators_v1.py`

最新实际 `adf1df` **exit0/no session_id**，缓存在：
`round48_after_vjp_0`（Promise fulfilled 的 `.value`）。

- 完整96batch、192唯一tile。
- 主49字段＋辅助3个max_pool，合计52。
- 每算子CPU/GPU各重复两次；每设备9984实际**算子**evaluations，不是完整网络tile forwards。
- 同一CPU输入传给实际GPU production leaf；传输逐位核对。
- 每batch CPU概率SHA复现上轮，最后CPU全FOV SHA及坐标gate复现。
- elapsed1682.5196秒。
- 输出 `same_input_operators_attempt01/{receipt.json,frozen_config.json,operators.jsonl.gz}`。
- **尚未保存实际terminal JSON，也未独立audit。**
- 请将实际 `adf1df` 终态保存，附 `observed_unified_exec_session=6897`，再独立枚举96×49主字段、96×3辅助字段、192tile、maxima/hash/重复及计数。
- 到25batch已见首Conv0、第二Conv自身差1.0681e-4、IN3.0518e-5，relu/pool同输入零差；**最终maxima须读终态receipt再报告**。
- 没有新的GPU整FOV，full38仍false，不能把local误差相加。

### 44317 仍 live，不重启

原：
`full_certified_schedule_2026_10_09/qualify_full_real_pipeline.py`

最新 actual `458ec1` **仍带session_id**，缓存在：
`round48_after_vjp_1`（fulfilled `.value`）。

- 10080/35904，elapsed10513.2768秒。
- 各强度误差0；坐标1.1368683772161603e-13。
- 真实exit0/no session_id才保存 `ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json`，附session44317，再 `audit_full_real_terminal_v2.py`。
- live `full_real_pipeline_attempt01`排除归档。

## 本轮新增论文：SSC 原文已完整读、看图

目录：
`six_resolution_training_preparation_2026_10_09`

使用并已读 PDF skill：
`C:/Users/user/.codex/plugins/cache/openai-primary-runtime/pdf/26.904.11930/skills/pdf/SKILL.md`

- 只读PDF，没有authoring marker、安装或清理历史。
- 复用既存 `innovation/tools/blindspot_pdf_reader_v3_2026_10_08/site_packages` 的pypdf/PDFium。
- 若最终回复提及该PDF，skill要求一次 source citation：
  `:codex-file-citation{path="D:/MRI/innovation/six_resolution_training_preparation_2026_10_09/ssc_primary_pdf_attempt01/primary.pdf" purpose="source"}`

SSC：
Heinrich等，MICCAI2013，DOI `10.1007/978-3-642-40811-3_24`，pp187–194。

- `fetch_ssc_primary_pdf.py` actual `51b34a` exit0。
- publisher PDF249477bytes，SHA `058e96f9d877abeea15a1caeb57a04a0f8ea2189bf71d6b565886cd3eee8367d`。
- `extract_and_render_ssc_primary.py` actual `220a61` exit0。
- `ssc_extraction_render_attempt01/page_01..08.txt/.png`。
- **8页文本全部实际读**：chunks `5cb1d9`（1–4）、`b8c52c`（5–8），均未截断。
- **8页PNG全部实际看**：`round48_ssc_visual_1_4` / `_5_8` 保存成功范围。
- 4图、3条编号公式，无独立实验表；参考列表也读了。
- 未读作者源码/未执行作者实现。
- 笔记 `SSC_PAPER_AND_CONTROL_PREPARATION.md`，尚未最终reading provenance。

关键判断：

- 六邻域非对向pair共12，避开中心patch作共同端点；patch3、邻居距离2vox、0.5mm isotropic。
- exp(-SSD/meanSSD)，归一化max1。
- 每元素5bit**一元/thermometer**编码，只支持六级0/5…5/5，12元素共60bit。
- XOR+popcount/60精确等于**量化后**SAD，不等于任意连续SAD，也不能用普通二进制32级。
- 13对MRI–US BITE、每对约27landmarks；TRE2.12±1.29mm，MIND2.45±1.44、MI3.07±1.74，约20s SSC。
- 这是注册证据，不能当CISS病灶Dice。
- 对比引用SeSaMI时初始TRE和额外US tracking信息不同；不能忽略信息差。
- SSC/自相似/bitpacking是已有强对照，不作为创新。

### SSC 算子验证已通过

`ssc_reference_adapter_v1.py`
`verify_ssc_preparation_v1.py`

actual `5d5ffe` exit0，无session，缓存 `round48_ssc_verify`。

`ssc_operator_preparation_attempt01/receipt.json`：

- 4种完整人工场2184voxels：NumPy vs独立Torch CPU公式误差全0。
- 4种exact affine/contrast inversion probe差0。
- 中心单voxel扰动+1000：SSC该点差0，中心包含6NH control差0.37706。
- 12slots×36级配对＋1000随机完整向量，1432配对，Hamming量化SAD差0。
- 最大nearest量化误差0.09999932。
- constant→ones、replicate边界和tie规则是我们显式约定，不称作者逐位复现。
- CUDA/MRI/GT/model/训练0；不是医学收益。
- 该“忽略中心异常”的性质可能对QC有盲点，后续真实病灶验证仍需准备。

## 三视图图/显存工作

### CPU人工图验证

原model/原深监督loss；人工16³ patch，batch2×3view，λ0.1仅人工参数。

- v1 `qualify_three_view_graph_synthetic_v1.py` actual `0dce50` exit0，`three_view_synthetic_attempt01`。
- v1漏记录protocol要求的optimizer moments；**没有编辑v1**。
- `prepare_three_view_graph_v2.py` actual `306b30`生成新v2。
- v2 actual `aec011` exit0，`three_view_synthetic_attempt02`，缓存 `round48_threeview_v2`。
- packed batch6 vs顺序3×batch2，两步共同AdamW；
  概率max5.6624e-7、gradmax3.2969e-7、参数max2.0023e-7、
  全optimizer162字段/step max3.5856e-8，全部3e-6门槛通过。
- v1/v2各4人工updates，不增加医学患者/训练分母。

### GPU原尺寸直接两方案都 OOM，保留失败

`probe_three_view_gpu_fullpatch_v1.py`
`THREE_VIEW_GPU_FULLPATCH_PROTOCOL.md`

actual `7f94bb` exit0（只是探测完整），缓存 `round48_threeview_gpu_start`。

`three_view_gpu_fullpatch_attempt01/receipt.json`：

- 原patch64×128×128，三份固定GIN view，人工target、cold-init原model。
- packed6 forward OOM，峰reserved2172649472。
- plain sequential2保留3图，在第3forward OOM，峰2373976064。
- optimizer updates0，完整成功forward2。
- job complete=true只表示两方案尝试完，strict comparison=false；
  不当医疗资格。
- 本进程cap未提高，释放/empty_cache只限自身。

### CPU激活卸载能跑；two-pass VJP 严格参数gate失败

`qualify_three_view_offload_vjp_v1.py`
`THREE_VIEW_OFFLOAD_AND_VJP_PROTOCOL.md`

actual `cb5674` **exit1/no session**，缓存 `round48_vjp_start`。

`three_view_offload_vjp_attempt01/receipt.json`：

1. `sequential_save_on_cpu`
   - `torch.autograd.graph.save_on_cpu(pin_memory=False)`，
     原完整三图attached mean-target KL＋第一view深监督，一次backward/AdamW。
   - 完成1人工GPU更新，3 forward；graph/backward1.50025s。
   - peak2275409920bytes，约2.28GB。

2. `two_pass_attached_vjp`
   - no_grad三view logits → 独立GPU leaf logits计算**attached** mean-target梯度，
     保存完整上游梯度CPU → view2/1/0重算并即时backward，最后一次AdamW。
   - 完成1人工更新，6 forward；全部第一/第二pass logits逐位相同。
   - peak2399141888bytes，极接近2.4GB cap。
   - firstpass0.1018s、upstream0.0107s、secondpass/backward0.3746s。

比较：

- 概率差0，loss差0。
- gradient max7.4505805969e-9，optimizer state9.313225746e-10。
- **AdamW后参数max3.0994415283e-6 >3e-6**，整体failed，不能降低门槛/称qualified。
- 最差param `encoders.1.layers.0.weight`，该param grad差2.386514097e-9；没有记录最差位置两侧实际梯度值，**不能未经核实断言近零梯度因果**。
- 下个参数误差1.5269e-6。
- CPU激活卸载分支成功，但尚未独立核保存张量往返逐位透明性，亦未真实19series资格。

**最新公开进度已告诉用户**：保留VJP负结果，继续核验CPU激活卸载的张量往返逐位一致。

下一可做：另冻新script/protocol，用`torch.autograd.graph.saved_tensors_hooks`为同一原尺寸三视图完整图记录CPU pack/unpack tensor dtype/shape/SHA，核恢复GPU张量逐位同、目标/输入不变、原loss/全梯度/一次AdamW正常、显存/RAM/全费用。不要改v1，不把VJP理论等价当FP32参数gate已通过；CPU卸载作为完整图可行候选仍需真实19series/两步/全费用。

## 资源与科研方向

只读storage检查actual `7cabb8`（缓存 `round48_storage_read_1`）：

- 当时free disk8049561600bytes。
- prep3781390、FOV6842491、coverage1356816、GPUgraph180519、
  full35904stage233587、frozen-storage79836。
- 后续文件增长，需fresh guard。
- 六臂v3完整预算104156359保持，原预检ready=false，磁盘不足＋35904/full38未齐。
- **本轮没有新压缩、删除、预算降低、正式训练或CPU部署替代实施**；只是读了预算来源。
- 历史PT37文件透明压缩只省359472，不重复/扩大。
- 新脚本guard保留prep7MB/FOV20MB/other22.8MB未来余量。
- prep已约4MB，导出buffers/归档注意7MB上限。

创新仍是窄待证伪假设：强task与真实动作余量之后，合法采集/observed响应对动作患者净收益是否有额外价值。须同信息risk差/QC/defer/metadata/static/random、全费用、cold-init LOPO及未见独立确认。新SSC/GIN/图内存实现都属强对照/基础设施，不包装新方法claim。

## 缓存导出与收尾

本轮缓存统一 `round48_*`，尚未导出。已用keys：

- `initial_0..3`
- `sameinput_start`
- `ssc_skill_0..2`
- `pdf_available_0..1`
- `ssc_fetch_0..1`
- `ssc_identity_0..2`
- `ssc_extract`
- `ssc_read_0..3`
- `ssc_visual_1_4`、`ssc_visual_5_8`（只存范围/状态，图片文件已在磁盘）
- `ssc_verify`
- `midpoint_0..2`
- `storage_read_0..3`
- `threeview_start`
- `threeview_v2_generate`、`threeview_v2`
- `threeview_gpu_start`
- `vjp_start`
- `after_vjp_0..2`

优先顺序：

1. 保存6897真实terminal并独立audit完整同输入诊断，读取最终maxima。
2. poll44317确认仍live，不重启。
3. 完成已公开承诺的CPU激活卸载透明性验证，保留全部GPU OOM/VJP失败。
4. 冻SSC全文/图像阅读provenance、科研判断、未执行后续尝试。
5. 保存本轮可见对话/实际buffers，接7457增量归档，排除所有live attempt。
6. 若继续医疗GIN资格，先具体完整19series/母GT/schedule/两步AdamW/显存与费用协议；人工成功不能代替。
7. 目标保持active，未达到发表目标。
