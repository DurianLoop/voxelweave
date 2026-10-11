# 用户提供的接续摘要（原文归档）

以下为本次接续消息所包含的前一模型摘要；这是继承信息，不取代本次实际运行结果。

### 当前状态

目标仍 **active**，尚无可发表且独立确认的 claim。本轮有实质进展：启动完整 CPU 拟合、完成开发监督检查和两篇全文核读。**唯一正在运行的自身任务是 CPU session `38045`，不要重启训练入口。**

最新实际 poll 确认 session 仍 live：

- `native_reference` 已记录 **320/512** 更新，loss `.983136`，约 1164 秒。
- 随后自动训练 `raw_pchip` 512 更新，总预算 **1024 更新**。
- 两臂 checkpoint 全部保存后，脚本才统一评价完整 FOV。
- 尚无最终 checkpoint、完整 FOV 效果或拟合门槛结果。
- GPU 最新仍约 **1394 MiB 空闲**；本轮 CUDA 未初始化。

### 当前运行与协议

均相对 `D:\MRI\innovation`：

- 运行脚本：`experiments/run_mc_rc_3d_cpu_fixed_fit_2026_10_07.py`
- 动态结果：`experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json`
- 冻结协议：`MC_RC_3D_CPU_FIXED_FIT_PROTOCOL_2026-10-07.md`

这是新增 CPU 诊断，**不替代原 GPU 资格预检**。两臂使用相同 observed 统计、架构、初始 seed `20261007`、监督、固定 patch、augmentation primitive、512 更新与最后 checkpoint。

仅训练/评分首个开发系列：

`VS-MC-RC-001 / 1.3.6.1.4.1.14519.5.2.1.10875952303942319530925289292568369177`

模型 1,401,363 参数；batch `[2,1,64,128,128]`，名义 `.5mm` 网格；深监督 BCE+Dice 权重 `4/7,2/7,1/7`。第一更新已逐位匹配上一轮认证过的 CPU 更新。

CPU 合同：单线程、自身 below-normal，磁盘/RAM 各保留 ≥8GB，新增保存 ≤250MB。前32步总训练投影上限7200秒，总运行上限9000秒。当前投影约63分钟，通过。原 GPU 的3600秒门槛未改变。

训练内拟合门槛：foreground patch Dice≥.90，完整训练系列 Dice≥.90、recall≥.90、absRVE≤.25、TP>0；失败也保留。**这些不是原四验证能力门槛。**

### 本轮已完成

1. **开发深监督检查，actual exit0，session `96208` 已结束。**

   - 原11开发患者/19系列，每系列32 draws，共608。
   - 三尺度 GT 与独立 stride oracle 比较，共 **1,454,374,912 个重复 patch GT 值**。
   - 所有尺度 forced-FG 和 whole-batch 前景归零次数均0。
   - 最小系列011物理前景76，quarter尺度仅1–2体素，但非0。
   - 不支持“coarse GT完全抹除病灶”的解释；非零监督不代表已学会。
   - 无 MR source 像素读取、神经前向或训练。

   文件：

   - `MC_RC_3D_DEVELOPMENT_SUPERVISION_AUDIT_PROTOCOL_2026-10-07.md`
   - `experiments/audit_mc_rc_3d_development_supervision_2026_10_07.py`
   - `experiments/mc_rc_3d_development_supervision_2026_10_07/attempt_01.json`

2. **两篇原始 HTML 全文实际读完，共274提取块。**

   - 3D U-Net，arXiv `1606.06650`，blocks0–52。
   - DeepMedic，arXiv `1603.05959`，blocks0–220，包括附录和参考文献。
   - 未查看原图像素、作者代码或复现实验；获取/提取日志中的 historical reading=false 保持，另写阅读登记。

   文件：

   - `literature/2026-10-07_3d_context_supervision_fulltext_reading.md`
   - `literature/source_cache/3d_context_supervision_2026-10-07/`
   - 其中 `reading_provenance_2026_10_07.json` 已生成。

   重要判断：3D U-Net 的 sparse 指**缺标签切片**，完整图像仍输入，不能类比本项目缺 MRI 观测层。DeepMedic 已有 foreground sampling、dense segment training、扩大context、多尺度分支；这些不是新贡献。其多模态、brain masks、注册、筛除病例、CRF调参和ensemble预算均与本项目不同。

3. **独立 checkpoint 重放器已实现，合成 QA actual exit0。**

   - 三输出头与原 forward 误差全部0。
   - 独立全 FOV 概率最大误差 `7.7486038e-7`，阈值预测无差异。
   - 尚未重放真实最终 checkpoint，必须等主训练实际结束。
   - 实现核验不能当第二独立训练任务网络。

   文件：

   - `experiments/mc_rc_3d_independent_replay_2026_10_07.py`
   - `experiments/verify_mc_rc_3d_cpu_fixed_fit_2026_10_07.py`
   - `experiments/mc_rc_3d_independent_interpreter_preflight_2026_10_07/attempt_01.json`

   QA 已 SHA 绑定重放器和 verifier，**不要修改这些旧文件**；修复须新版本。

### 继承的有效证据与约束

上一轮已完成真实 native 参照全28系列认证：1993层、461,967,360 MR像素与等量标签坐标重放；observed 抽层全相等。修正后56个物理输入、全部标签重采样、稀疏来源隔离与实际尺寸两CPU更新通过。

入口：`SESSION_RESULT_NATIVE_REFERENCE_AND_3D_PREPARATION_2026-10-07.md`。上一轮归档验收48阶段文件、165证据文件，通过；本轮新文件尚未最终统一归档。

持续约束：

- 所有新增内容仅写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不操作或枚举用户终端训练，不改根环境/`.gitignore`，不读 locked IXI test，不委派子代理。
- 固定11开发/19系列、4已见验证/9系列、8确认/12系列，同患者时点同角色。
- 八确认 `030/029/019/028/031/026/027/015` 继续关闭，科学确认数0。
- 旧代码、协议、checkpoint、结果及失败保留 SHA，不覆盖。
- 原四验证 gate：患者内先平均系列，再患者平均；full Dice≥.70、missing≥.65、recall≥.70、absRVE≤.50，四患者full/missing均正，9系列无TP0；不缩分母或丢弃空/undefined。
- 原无增强/仅强度20k仍失败，不能据此声称SR损害病灶；旧45CISS反证及addback/QDA/线性政策失败不撤销。
- 原 GPU 拟合 `attempt01` 为 resource_deferred、0更新、已结束。只有新 totals ≥8GB，才允许原冻结协议的新 `attempt02`。

### 明确下一步

1. **继续 poll 同一 live session `38045`**，每约60秒提供简短进度。不要因为超时或观察中断重启。
2. 等主任务真实 exit 后检查最终 `attempt_01.json`、两臂512 checkpoint、全部域指标和拟合 gates；未通过也如实记录。
3. 主任务成功完成后运行：

   `D:\conda\envs\MRI\python.exe -X utf8 -B D:\MRI\innovation\experiments\verify_mc_rc_3d_cpu_fixed_fit_2026_10_07.py`

   verifier 检查1024条逐步history/LR、所有来源/checkpoint/batch SHA，并独立功能前向、完整FOV、NumPy重采样及全域计数。概率门槛≤3e-6且二值预测必须相同。失败保留并新版本修复。
4. 生成实际结果报告及适当科学图，归档本轮全部对话、协议、文献、诊断和训练证据。**本次 compaction 请求及这份摘要尚未另存新文件，接续时先补存。**
5. 根据完成的真实拟合证据决定充分19系列任务基线；CPU fixed-example成功也不证明强基线或泛化。GPU资格仍需实际GPU。
6. 能力充分后才公平 native/6×5矩阵、同observed直接任务及分辨率随机化；稳定残余成立才做预测 action gain 的修正。最终冻结后才八确认与第二独立网络。

精确创新问题不变：充分任务适配后，同observed信息/统计/监督/容量/预算，是否存在优于强raw PCHIP与直接任务适配的可观测缺层病灶修正。尚未验证正答案。
