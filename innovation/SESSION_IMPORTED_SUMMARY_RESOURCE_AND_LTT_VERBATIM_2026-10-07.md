## 目标与约束

持续研究，直到形成并验证可发表 claim；goal **active**。本次压缩不是暂停。

- 用户已允许 GPU，但不得操作、重启或迁移用户终端训练。
- 新文件仅写 `D:\MRI\innovation`；不改冻结证据、根环境、`.gitignore`。
- 不委派代理。
- PowerShell；Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`；运行后用 `exit $LASTEXITCODE` 转交退出码。
- 11 开发患者/19 series，4 已见验证患者/9 series；8 确认患者/12 series 和 locked IXI test 关闭。
- 上一 goal turn及当前续作均有实质 progress，不能标 blocked/complete。

## 先接续训练

**首先 poll 同一 session `99542`，不要重启。**

最近实际 poll：chunk `927aa8`，仍 live；native 最后 **7821**，invocation02 新增 **7722**，累计 **17005.17974749999 秒**。PCHIP **99** 仅历史快照。

两臂各19998/总39996；CPU4/interop1、float32、共同初始化/GT/增强、AdamW LR/WD `.0001`；累计30h、8GB余量、250MB保存限制不变。不读取中间 MRI 效益。

最近 GPU：chunk `6cce66`，**20:20:00.812**，free1394MiB/total24455MiB/util90%，低于新 GPU 8GB 启动门槛。

只有真实 training exit0、两臂 last19998 冻结，才能记录正式训练退出，运行原56FOV评价及独立 strict 核验。原4验证患者有6项判据；不得用新资格替代。旧 MIRA 有 MSValid84人确认；“确认0”只指当前病灶线。

## 已冻结上一阶段

入口：

```text
innovation/SESSION_RESULT_PAIRED_AND_CALIBRATION_2026-10-07.md
innovation/SESSION_CHECKPOINT_RECEIPT_PAIRED_AND_CALIBRATION_2026-10-07.json
innovation/literature/paired_and_calibration_stage_manifest_2026-10-07.json
```

归档 chunk `0c61e8` exit0：**105新stage文件、1240累计证据、15,765,078bytes**；前1130 SHA不变。后置 finalize chunk `444aaa` exit0。

该阶段完成3篇原文选读23/38页、7页实际view，以及校准风险/收益、校准位置两个CPU审计。direct 理想坐标 absolute gate **仍失败**；float32/float64解释器通过不覆盖它，原56FOV不改。

## 本续作新增，尚未归档

### 真实资源入口已经实现

文件均在 `innovation/experiments`：

```text
mc_rc_3d_paired_resource_worker_2026_10_07.py
run_mc_rc_3d_paired_real_resource_2026_10_07.py
qualify_mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07.py
```

协议：

```text
innovation/MC_RC_3D_PAIRED_REAL_RESOURCE_ENTRY_PROTOCOL_2026-10-07.md
```

外层先运行旧 readiness，合格后才 import 神经/MRI模块。之后要求本轮合成资格和真实退出/独立 verifier receipt。GPU沿旧 loader 本进程设置 `CUDA_VISIBLE_DEVICES=-1` 后，再仅自身恢复0的顺序。

真实路径**已实现但未执行验证**，计划：

- 19开发series，共享5个float32字段，缓存期望4,774,280,000bytes。
- 沿旧 `stream_for` 生成33个患者平衡draw，两臂共享。
- 每臂33资源更新及一次恢复重放，总68；LR/WD `.0001`，共同canonical两通道初始化。
- 权重仅内存、全部丢弃，不作formal training或病灶评分。
- 按固定tile数最大、UID排序选择代表FOV，每臂重复两次。**不是全部19个MRI FOV资格**，也不证明所有资源维度最坏峰值。

### 合成 workflow 已真实通过

session `14984`，chunk **`d6352c` exit0**，**45.025657299906015秒**。

结果：

```text
innovation/experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/attempt01.json
```

- 原PATCH64×128×128/batch2；合成68×132×136。
- 两synthetic UID、3共享draw；两臂各3更新加一次恢复重放，**8合成更新**。
- 共**24模型forward**：训练8，FOV16；FOV32tile。
- 全branch/mask梯度有限非零，model/optimizer/RNG恢复tree exact。
- 每臂8tile FOV重复两次，完整metadata/SHA一致。
- 输入未回写，审计无MRI访问，CUDA未初始化，权重未落盘。
- 保存8份 `.source_snapshot`；不要修改已执行源码而破坏绑定。

尚无独立 verifier 和以下 receipt，**下一步必须补**：

```text
SESSION_OBSERVED_EXITS_PAIRED_RESOURCE_WORKFLOW_2026-10-07.json
```

外层要求字段：`synthetic_observed_tool_exit`、`synthetic_result_sha256`、`verifier_observed_tool_exit`、`verifier_result_sha256`、`verifier_result_file`。真实 verifier exit0 后才写。

可用独立核验方式：仅NumPy重建固定合成输入、独立crop/affine/flip重放6个训练batch SHA，检查draw/labels/更新计数/FOV覆盖与重复metadata、源码snapshot SHA。不要冒称重放未保存的神经权重。

### 真实外层当前延期已验证

实际运行：

```powershell
& 'D:\conda\envs\MRI\python.exe' -X utf8 -B 'innovation\experiments\run_mc_rc_3d_paired_real_resource_2026_10_07.py' --device cpu --attempt 01; exit $LASTEXITCODE
```

chunk **`300d9f`真实exit3**，0.07546740001998842秒。

```text
innovation/experiments/mc_rc_3d_paired_real_resource_2026_10_07_cpu_attempt01/attempt01.json
innovation/experiments/mc_rc_3d_paired_real_resource_2026_10_07_cpu_attempt01/prerequisite_readiness.json
```

complete=true/status=`prerequisite_deferred`/errors=[]；MRI、GT、更新、神经import、CUDA均0。live invocation SHA仍仅mutable observations，不冻结。

注意一个待修的GPU记录细节：外层 `CUDA_initialized` 只在成功结束时更新；未来GPU异常时可能保留初始false。真实GPU执行前应另立修正版/记录补充，并保留当前已执行源码及资格绑定，不能静默改原文件。

## 新论文：Learn then Test

取得 **arXiv2110.01052v5**，35PDF页，chunk **`bb7039` exit0**。作者 Angelopoulos、Bates、Candès、Jordan、Lei；第一页标v5 2022-09-29。

```text
innovation/literature/2026-10-07_learn_then_test_primary_protocol.md
innovation/literature/fetch_learn_then_test_primary_2026_10_07.py
innovation/literature/source_cache/learn_then_test_primary_2026-10-07/
```

已完整读文字页 **1–9、11–12，共11页**。**尚未render/view、尚未写阅读笔记/provenance**；下载reading=false保留。可继续读13–15补instance segmentation结果，再render/view关键页4、5、6、14。

已确认：

- 有限非单调策略、多个风险的高概率控制已有直接先例，不能称新理论。
- i.i.d.独立calibration；valid p-values + FWER选择。
- certified集合内可用同calibration数据选效用较好的策略，保证仍覆盖该集合；不能据此随意训练新策略/grid。
- fixed-sequence顺序必须不看calibration数据，首个不拒绝即停止；多起点要校正。
- 多风险在每策略内取 **max p-value**，不是简单另乘风险数量。
- binary loss可用exact binomial；连续Dice/无界absRVE不能直接当同一binary检验。

拟做的CPU解析反例**尚未写协议/执行正式审计**，仅chunk `74af0b`预算：n8、alpha=.3、delta=.1，两独立策略真实错误率均.31；零错误p-value `.7^8=.05764801`。固定顺序FWER `.69^8=.0513798374428641`；按calibration结果排序再当固定顺序，FWER **.10011978719007306 > .1**。这是已知多重检验反例，不是MRI发现。

## 下一步顺序

1. poll `99542`，保留同session。
2. 完成资源 workflow 独立核验，真实exit后写receipt；不要启动真实MRI资格直到原gates全部通过。
3. 完成LTT相关阅读、实际render/view、笔记；需要时做上述明确合成审计。
4. 保存本续作公开对话、当前压缩摘要、结果/交接/台账；**当前还未完成该写入和新manifest归档**。此前公开说将写接续文件，尚未执行。
5. 另立stage归档，核验前1240 SHA；排除live invocation/history/resume，纳入上一阶段post-manifest appendices。
6. 原训练真实结束后，完成原56FOV/6能力gates/strict，再执行真实资源资格和充分适配dense/direct/SR。存在真实修正余量才推进合法特征、全部成本、强cost/defer/union-greedy/random及冻结后8确认。

**新可发表 claim 未确认，完整目标保持 active。**
