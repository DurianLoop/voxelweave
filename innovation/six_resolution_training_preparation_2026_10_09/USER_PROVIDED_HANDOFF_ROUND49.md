# 用户传入的上一模型工作摘要（可见内容照录）

## 目标与约束

继续 active goal：**一直研究、探索、验证，直到获得可发表且独立确认的 claim；不动用户原终端训练进程。** 本轮 ROUND49 有实际医学数值诊断和论文来源进展，不是 blocked；尚无发表 claim。

- cwd `D:\MRI`，PowerShell，Python `D:\conda\envs\MRI\python.exe -B -X utf8`。
- 新增只写 `innovation`；不安装、不委派、不删除历史、不枚举或修改其他 PID。
- 已执行/冻结代码不编辑，改动另版本。
- CPU1/interop1/below-normal；RAM、磁盘各保留十进制8GB。
- GPU已授权：启动free≥8192MiB；allocator≤min(10%,2.4GB/total)，peak≤2.5GB，runtimefree≥4GB；FP32/TF32off/deterministic。
- 概率/强度/梯度/参数/moments gate3e-6，坐标3e-12，二值零差；六医学gate不降低。
- 11开发患者19series；4已见验证9series不作新确认；8未见确认12series和lockedIXI关闭。
- 19998 parent见全部开发GT，只作开发诊断；严格LOPO必须cold-init。
- 所有可见对话、传入摘要、实际工具结果、真实失败和准备保存到innovation；不补造不可访问聊天或隐藏推理。

## 最新冻结链

ROUND48已真实归档：

`innovation/six_resolution_training_preparation_2026_10_09/APPEND_ROUND48_INDEX.json`

- 累计7538，新增81，原7457全部保持。
- SHA `b9825de3824978e7a62dac4094455cdd292f32179930c07c1cb6e45ba5411615`
- archive actual `e2971f` exit0/no session；post-check `f31afe` exit0。
- 入口 `POST_ARCHIVE_HANDOFF_ROUND48.md`。
- **ROUND49尚未归档、写科研总结/对话/导出buffers或最终回复。**

ROUND48已完成SSC原文8页/8图、同输入52算子×96batch诊断、人工三视图卸载两步透明性。结果详见 ROUND48报告；不要重复计新论文或再跑这些已完成验证。完整GPU full38仍未通过。

## 唯一仍live的作业

原 `full_certified_schedule_2026_10_09/qualify_full_real_pipeline.py`

- session **44317**，不要重启。
- 最新真实poll actual `6d793d`仍带session_id，缓存 `round49_full_pipeline_latest`。
- **11880/35904**，elapsed12570.7717秒。
- 各强度误差0，coordinate1.1368683772161603e-13。
- 真实exit0/no session_id才保存 `ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json`，附44317，再 `audit_full_real_terminal_v2.py`。
- live `full_real_pipeline_attempt01`排除归档。
- 该代码WALL64800秒。启动reserve15.8MB，需读其runtime guard确认资源；没有修改它。

**其他ROUND49作业全部已真实终态，不再poll42978/12870。**

## ROUND49：独立CPU可微参考与真实病例失败

都在 `six_resolution_training_preparation_2026_10_09`。

### 独立CPU参考已实现并人工通过

- `gin_cpu_differentiable_reference_v1.py`
  - functional CPU conv/IN/pool/transpose，checkpoint；
  - 显式nearest-exact target索引；
  - binary softplus深监督loss，attached xlogy KL(mean||each)。
- `verify_gin_cpu_reference_v1.py`
- `GIN_CPU_REFERENCE_VERIFICATION_PROTOCOL_V1.md`
- `gin_cpu_reference_verification_attempt01/receipt.json`
- actual **a37390 exit0/no session**，缓存 `round49_cpu_reference_verify`。
- 人工16³两步、54参数/162moments每step：
  - loss max2.3842e-7、prob5.3644e-7、
  - grad4.47e-8、param1.7518e-6、moment5.3551e-9。
- 4个人工CPU updates；MRI/GT/CUDA0。
- 尚未独立audit此人工receipt，但后续真实诊断已验证CPU模型/optimizer复现。

### 真实19series runner已实现，首病例失败停止

- `GIN19_REAL_EXECUTION_PROTOCOL_V1.md`
- `qualify_gin19_real_graph_v1.py`
- v1 actual **7ea18e exit1/no session**：
  - frozen_config indent JSON超过250000bytes预算；
  - MRI/GT/updates0；原代码和失败保留。
- `prepare_gin19_real_graph_v2.py` actual **fe2dcb exit0**。
- `GIN19_REAL_EXECUTION_PROTOCOL_V2.md`
- `qualify_gin19_real_graph_v2.py`
  - compact无损frozen JSON，完整scope没删；
  - 完整54参数详细检查只存journal，receipt摘要/最差3项；
  - 保持config250k/journal1.2M/receipt350k budget。
- **42978→7f7ed3 exit1/no session**，缓存 `round49_real_v2_poll2`。
- 已保存 `ACTUAL_GIN19_REAL_GRAPH_V2_FAILED_TERMINAL_TOOL.json`。
- 输出 `gin19_real_graph_attempt02`：
  - frozen_config158848bytes；
  - journal27034bytes、7条完整记录；
  - case0/native_reference，开发VS-MC-RC-001一个series。
  - MRI1/GT1、parent0；
  - CPU/GPU各两次真实optimizer updates、各6 whole-model forwards，各84 block调用含checkpoint；
  - CPU/GPU各自216个总参数更新检查均通过独立float64 NumPy AdamW；
  - 两步内存model+optimizer保存/恢复逐位一致；
  - 对比实际仅**step0**（先CPU两步、GPU两步，再对比第一步遇失败停止）：
    - prob **3.4868717193603516e-6**
    - loss1.1920928955078125e-7
    - grad **1.8425285816192627e-5**
    - param **0.0001992689212784171**
    - moments1.8421560525894165e-6
    - **5个二值差异**，跨全部3view×3head；
  - 完整19资格false，剩余病例未跑；不是正式医学训练/效益实验。
  - elapsed44.77756秒；CPU图18.23/17.55s，GPU图1.79/1.59s，峰GPU2279604224bytes。

最差参数 `decoders.2.layers.3.weight` flat1658：

- CPU梯度 `+3.7831850931979716e-6`
- GPU梯度 `-2.1291125449351966e-6`
- CPU参数−0.0005952856736257672
- GPU参数−0.0003960167523473501
- 差约两倍LR1e-4；原journal记录所有54参数最差位置两侧值，不能再声称没有坐标证据。

### 损失公式归因已完成

- `GIN_REAL_LOSS_ATTRIBUTION_PROTOCOL_V1.md`
- `diagnose_gin_real_loss_attribution_v1.py`
- **12870→81f534 exit0/no session**，缓存 `round49_loss_attribution_poll1`。
- 已保存 `ACTUAL_GIN_REAL_LOSS_ATTRIBUTION_TERMINAL_TOOL.json`。
- `gin_real_loss_attribution_attempt01/receipt.json`：
  - 原journal完整GIN字节参数反解，用相同病例/crop/target/3view。
  - 同一CPU logits分别原production loss与独立softplus/xlogy，两次autograd.grad。
  - 两个新诊断CPU AdamW updates，GPU0。
  - 独立loss分支逐位复现原真实CPU step0 **model和optimizer SHA**。
  - loss公式grad最大差5.681067705154419e-8；
  - 参数最大差2.8796494007110596e-6（≤gate）；
  - moments5.6461431086063385e-9；
  - 原3个最差坐标，两种CPU公式符号相同；最差坐标公式grad差仅2.5538611e-9。
  - 实际CPU/GPU梯度符号相反解释AdamW参数gap，**尚未定位具体conv/IN/前向或反向算子**。
  - 这是数值诊断，不说明临床伤害/GIN医学无效。
  - elapsed33.67556秒。

### 独立record audit通过

- `audit_gin_real_failure_and_loss_v1.py`
- `gin_real_failure_audit_attempt01/receipt.json`
- actual **0e113a exit0/no session**，缓存 `round49_real_loss_audit`。
- 验真实终态、完整19计划仍在、7journal行、216 NumPy更新项、54跨设备参数/162state字段、54个GIN参数tensor完整base64 payload。
- 解析原3最差梯度的首步AdamW公式gap，与实测gap一致（误差≤4.1e-10）。
- 不重新跑模型/打开数据。
- **还未保存该audit的独立actual tool JSON**，可从缓存保存。

## 新论文进展：GIN期刊录用稿已下载、提取、render；阅读尚未完成！

新的独立目录：

`innovation/gin_accepted_primary_followup_2026_10_09`

### 来源版本与访问

- DOI **10.1109/TMI.2022.3224067**
- Ouyang等七作者，Causality-inspired Single-source Domain Generalization for Medical Image Segmentation。
- Imperial官方仓储标注 **Accepted version**，acceptance2022-11-01，issued2022-11-23。
- TMI42(4)1095–1106，published2023；**不称publisher typeset final**。
- 原PDF首页是通用模板 `VOL. XX ... XXXX 2020`，不能据此说发表2020。
- 这是此前读过arxiv2111.12525v5的**另一版本**，不能增加distinct论文数；可计新增accepted-primary-version全文阅读1次。
- OpenAlex/EuropePMC元数据closed不代表机构没有公开PDF；实测Imperial公开链接成功。
- Crossref只有publisher staging链接，**没请求staging**。
- 官网citation UI `/bitstreams/.../download` actual3a2485 HTTP405，原v1失败保留。
- 在真实public SSR HTML中发现字面官方REST content链接：
  `https://spiral.imperial.ac.uk/server/api/core/bitstreams/9f1f03f2-fac1-4402-8045-9f9455fdac2d/content`
- v2按普通匿名GET此明确public链接成功，没有认证/方法/cookie/访问权限绕过。
- `prepare_fetch_v2.py` actual4f4479 exit0。
- `fetch_and_extract_v2.py` actual **fa9325 exit0/no session**，缓存 `round49_accepted_v2_start`。
- `accepted_pdf_attempt02/accepted.pdf`
  - **4498435bytes**
  - SHA **c9b7dc075caceb7bc53743dbd7a138e774637fd1e18697c575ca972f11be8c56**
- 已提取 **12页** `.txt`，render **12页** `.png`（scale1.0、128色、约612×792）。
- **还没有实际看任何12页PNG**。
- PDF skill已读并告知用户正在使用，无安装/authoring marker。
- 若最终回复提该新PDF，source citation一次：
  `:codex-file-citation{path="D:/MRI/innovation/gin_accepted_primary_followup_2026_10_09/accepted_pdf_attempt02/accepted.pdf" purpose="source"}`

### 阅读状态（必须续读，不能已报全文）

- batch执行文本1–3和4–6，两个exec返回本身都未截断，但是外层总输出10109tokens被9500限制截断。
- 已明确**重新展示缓存完整1–3页**，目前这3页实际读完，未截断。
  - original chunk **0744d9**
  - cache `round49_accepted_read_1_3`
  - recovery flag `round49_accepted_read_1_3_recovered_untruncated=true`
- **4–6页要重新独立展示缓存**，避免外层截断：
  `load("round49_accepted_read_4_6").value.output`
  用一个functions.exec、max_output_tokens≥6000，只输出它。
- **7–12页尚未读**；每次3页独立展示，避免累计输出截断。
- **12页PNG全待实际view_image**，建议每批3–4张，存成功页范围。
- 下载/提取receipt里阅读false保持，不编辑；完成后另新reading provenance。
- 暂时已见：
  - shape不变/appearance变化的causal假设；A、C独立且C跨域不变。
  - 原文Eq3双视图监督＋两预测之间KL；与作者已读代码三view/监督第一view/attached mean-target KL仍存在表述边界。
  - IPA全图unsupervised pseudo-correlation map避免GT mask捷径；Eq6互补空间混合，AugMix已有关系。
  - 后文完整配置/实验/ablation/表/讨论未读，不提前声称accepted版改变或相同。
- 要完成版本对比、科研边界笔记；GIN/IPA/3D不是新方法claim，强对照依然pending医学通过。

### 新目录预算注意

新paper目录 **总cap6MB**，原PDF4.498MB加12PNG/文本已保存，需fresh查看实际size。
原prep7MB、FOV20MB、other22.8MB全部保留。

新paper的guard用**剩余余量**：

`free -22.8MB -(7MB-prep_actual) -(20MB-FOV_actual) -(6MB-paper_actual) ≥8GB`

这是旧GPU验证一直用的剩余预算逻辑，没有降低任何cap。

旧archive_round48.py的guard减42.8MB（直接减完整FOV20MB，重复计已占用FOV字节）。下载4.5MB后照搬旧archive guard可能失败。**ROUND49新archiver须用上述完整剩余预算逻辑，并保留原各cap及新paper6MB；不要降低预算、删文件或编辑冻结archive来过gate。** free本身已扣当前文件，用limit−actual防止双重计数；明确记录这是账目修正，非缩scope。六臂104156359预算原值，正式训练仍不ready。

## 已发用户进度（ROUND49需保存）

1. 上一轮实质进展，推进独立可微CPU参考/真实母GT和optimizer检查，观察live完整流程。
2. CPU参考人工两步已通过54参数/162optimizer；真实首case失败就保留停止。
3. 首真实病例概率3.49e-6/5二值/参数1.99e-4失败，最差位置梯度两设备符号相反，准备排查独立loss。
4. loss公式最大grad差5.68e-8，原最差位置CPU两种公式符号一致，AdamW放大跨设备符号差；具体算子未定位、资格未过。
5. 找到Imperial Accepted version，将用PDF技能核早期版差异和强对照版本。

## 缓存与其他文件

ROUND49缓存需导出，已用key：

- `initial_0..2`
- `cpu_reference_verify`
- `real_start`（v1失败）
- `real_failure_read`
- `real_v2_generation`、`real_v2_start`、`real_v2_poll2`
- `parallel_read_0..3`
- `gin_final_locator_read`
- `real_result_read_0..1`
- `loss_attribution_start`、`loss_attribution_poll1`
- `real_loss_audit`
- `final_source_locator_start`
- `repository_landing_start`
- `imperial_v2_start`
- `official_public_api_locator`
- `full_pipeline_latest`
- `content_link_read`
- `accepted_fetch_start`（HTTP405）
- `accepted_v2_generation`、`accepted_v2_start`
- `accepted_read_1_3`、`accepted_read_4_6`
- `accepted_read_1_3_recovered_untruncated`

一些读命令结果未store，不补造；必要结果已经visible、receipt或源文件保留。

机构来源metadata/landing都在prep中：
- `locate_gin_final_public_source_v1.py`，Crossref/OpenAlex准确DOI；
- `fetch_gin_repository_landing_v1.py`：TUM元数据成功，Imperial首HTML150k大小上限失败；
- `fetch_gin_imperial_landing_v2.py`：661087byte完整public HTML、压缩111387bytes、visible_text4344bytes，标Accepted/4.29MB/DOI和citation_pdf_url。
这些是**metadata/landing阅读，不计全文论文**。

## 下一步优先顺序

1. 完成新accepted PDF剩余文本4–12与12页PNG实际阅读，避免总输出截断。
2. 对比早期版、已有固定作者代码与accepted文本；写笔记/阅读provenance和具体后续实验，不预设版本变更。
3. poll44317确认live，不重启；若终态按原程序保存actual/audit。
4. 保存ROUND49实际terminal（CPU参考、v1预启动失败、real audit等）、可见对话和可用buffers。
5. 写本轮研究/失败归因总结，明确：一患者一series真实诊断，CPU/GPU各2update但只step0跨设备判定；全19资格false，非医疗增益。
6. 写新archive_round49.py，接7538，原全部hash保持；包含新paper目录，排除live35904。用完整剩余预算防止双重计FOV占用，不改历史。
7. 独立post-check、归档后handoff/最终答复落盘。目标仍active，不mark complete/blocked。
8. 后续真正推进强baseline/完整fullFOV/动作患者净收益；不能把CPU/GPU数值诊断或经典增强改称发表claim。
