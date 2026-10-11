# 本轮接入的用户提供 checkpoint

这是用户提供的上一模型接续摘要的归档转录。它记录的是接入时的历史状态，不是当前任务状态；当前状态以本轮 SESSION_UPDATE、HANDOFF 和实际 poll 为准。

## 目标与约束

目标仍 **active、未达成**：继续探索验证，直到形成可发表且独立验证的 claim。此次 checkpoint **不暂停研究**。

- `D:\MRI`，PowerShell；Python：`D:\conda\envs\MRI\python.exe`。
- 不使用 GPU、不干预用户终端训练、不读锁定 IXI test、不改根环境或 `.gitignore`。
- 不新建或委派代理。全部代码、证据、失败、公开对话和接续记录存入 `innovation`。
- 本轮属于 **progress**：完成新的标签传播实验和独立复核，并实际启动冻结分割器诊断。

## 两个需要实际 poll 的任务

1. **原队列 session83910，最近实际 poll 仍 live。**
   ```powershell
   D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py
   ```
   322/322 条件、45/45 主患者推断完成；仍在逐患者再生成核验。最近文件阶段为 `verify_VS-SEG-217`，仅历史状态，先实际 poll 再读文件。不要重启或终止。

   合同 SHA256：
   `061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`

   完整核验/原主分析之后才运行 `vs_seg_selection_sensitivity.py`。主 HAT−pipeline PCHIP 比较、001/202 Dice 改善反证保持，不挑模型救方向。

2. **新预测区域诊断 session77501，最近实际 poll 仍 live，13/15 系列已处理。**
   ```powershell
   D:\conda\envs\MRI\python.exe -B innovation\experiments\mc_rc_frozen_predicted_region_cpu.py
   ```
   不盲目重跑；成功目录 `exist_ok=False`。当前 `errors=[]`，已处理系列的主区域门槛均失败；完整结果和独立复核仍待完成。

## 本轮已完成：理想观测区域传播

合同：`innovation/MC_RC_OBSERVED_REGION_PROPAGATION_PLAN_2026-10-03.md`

执行与输出：

- `experiments/mc_rc_observed_region_propagation.py`，**session55551 exit0**
- `experiments/mc_rc_observed_region_propagation/attempt_01.json`
- `experiments/mc_rc_observed_region_propagation/run_contract.json`

固定上一轮的 **15 系列、8 开发患者、759 内部缺层**，9 个策略/对照。唯一主要策略：真实观测标签两侧并集，加 **2 mm** plane 内膨胀。

15 系列全部通过预写几何门槛：

- 前景覆盖范围：`.9955604883–1`
- 边界覆盖范围：`.9921875–1`
- ROI/完整缺层平面面积：`.0003473618–.0276431129`
- tile32 面积：`.0022977941–.0500992063`
- tile 前景覆盖全部 `1`

同时保留 nearest、union、1/4 mm、环移、像素面积匹配随机、tile 数与实际面积匹配随机、完整平面对照。**真值观测 mask 是理想输入，不能称可部署能力或新方法优势。**

独立验证：

- `experiments/verify_mc_rc_observed_region_propagation.py`
- **session91233 exit0**
- `experiments/mc_rc_observed_region_propagation/independent_raw_label_roi_verification.json`
- `errors=[]`

从原标签重建 native 前景；EDT 主实现对照 physical-offset disk dilation；显式六邻居边界；全部 **787,030 前景体素、759×9 策略计数、3×759 packed masks、随机预算和患者汇总**复核通过。

## 本轮实际启动：可见 MRI 预测区域

合同：`innovation/MC_RC_FROZEN_PREDICTED_REGION_CPU_PLAN_2026-10-03.md`

脚本与输出目录：

- `experiments/mc_rc_frozen_predicted_region_cpu.py`
- `experiments/mc_rc_frozen_predicted_region_cpu/`

使用已认证官方冻结 T2 分割器，仅解码 MR 的 **0,4,…真实观测 planes**，构造 raw-PCHIP display；不解码隐藏 MR planes、不训练网络。RAS、NormalizeIntensity、Gaussian 384×384×64 滑窗；先保存预测，再读真值评分。

主 ROI：预测在观测 planes 的 mask 两侧并集 +2 mm。dense prediction +2 mm 只是次要条件，不能替换主失败。

最近完成的13个系列主 gate 都失败。若干系列预测/覆盖为0；也有实际检测能力：

- 006 `t2_spc_tra_iso_384` 全体积 task Dice `.867673`，但主 ROI 前景覆盖 `.982213`，仍未达到 `.99`。
- 010 `3D FIESTA Hi Res` 全体积 Dice `.436919`，主 ROI 前景覆盖 `.492393`。

**不能尚未复核就归因为 domain shift 或抽层损害；native 基准尚未运行。** 继续全部15系列，不调半径、阈值、crop或checkpoint。

## 已写好但尚未执行的独立模型复核

```powershell
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_mc_rc_frozen_predicted_region_cpu.py
```

**尚未执行，无 session handle。必须等77501完整15系列成功结束后再运行。**

预期输出：`experiments/mc_rc_frozen_predicted_region_cpu/independent_observed_input_roi_and_model_replay.json`

它会从原 ZIP 独立按 IPP 排序并只解码真实 anchors；Hermite 公式复算 PCHIP，再核实际 display hash；**重新进行全部15次冻结 CPU 前向**；用显式整数 voxel mapping 回到 native，逐位比较预测；原标签、disk dilation、全部六种 ROI/对照、task competence及患者汇总复核。

源码尚未冻结到执行 proof，可以先检查实现；执行后不要覆盖成功 proof。它复用认证 inferer、Pydicom、PCG64库，不声称全算法独立重写。

## 重要待核实的来源分母问题

本轮15名单沿用上一轮基于 **初始 `label_grid_attempt_01.json`** 的合同。已读历史结果提到002第二时间点在追加几何修正后合格，因此需优先核：

- `experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json`
- `experiments/mc_rc_native_t2_label_gate/independent_raw_geometry_grid_verification.json`

确认它是否使当前实际合格总数多于15。**尚未完成此核对，不要把冻结15名单无条件称为当前全部合格来源。** 保留已冻结实验，不修改运行中的合同/源码；如有遗漏，用单独范围更正和新合同处理，不能事后抹去旧结果。

## 下一步与归档

1. 实际 poll **83910、77501**，读取最新状态；都不要重启。
2. 核清上述初始/追加来源资格差异。
3. 77501 terminal complete 后执行独立模型复核。
4. 据完整且复核后的结果停止或继续固定预测配置；若失败，另准备 **全部来源的真实 native 分割能力对照**，区分预测器能力与抽层效应，不能凭猜测解释。
5. 保存本轮 SESSION_UPDATE、VISIBLE_DIALOGUE、HANDOFF、此 checkpoint、结果报告、README及新 stage核验；**本轮这些收尾尚未完成**。上一阶段22项归档通过，但本轮新文件已使 manifest 过时。
6. 原队列完整结束后做原主分析与预写筛选敏感性。

旧30特征/λ=.01/五alpha联合岭失败、收益/绝对误差线性等价保持；8人全部时点属于开发，科学独立确认仍0。本轮没有新增论文获取，没有 GPU 操作。
