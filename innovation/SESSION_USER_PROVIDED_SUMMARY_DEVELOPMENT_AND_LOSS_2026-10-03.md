# 本次接续时用户提供的模型工作摘要（原文存档）

以下为用户提供的另一模型摘要，不把其中未核状态当本次独立观测。实际运行状态以后续session轮询和JSON证据为准。压缩前公开对话中缺失的句子无法逐字恢复，不虚构完整历史。

目标仍 **active**：持续研究探索，直到得到可发表且独立确认的 claim。尚未达到。上一轮是 **progress**；本轮也已有新诊断、源码核对及 CPU 数值证据。此次 compaction 不代表暂停研究。

### 约束

- 所有新增内容仅写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不用 GPU，不枚举/操作用户终端训练，不读 locked IXI test，不改根环境或 `.gitignore`，不创建/委派代理。
- CPU 单线程、自身 below-normal；磁盘≥15 GB、可用内存≥8 GB。
- 不重启已完成或仍 live 的任务；失败修复使用新 attempt。
- 固定角色：11开发/19系列、4验证/9系列、8确认保留/12系列。确认患者禁止提前开效果。
- 文件/源码/数值核验不等于科学确认。

### 上轮已完成，勿重跑

入口 `SESSION_HANDOFF_GLOBAL_LOCAL_TASK_2026-10-03.md`。

981,602参数、11开发人19系列、随机初始化、20,000步 CPU 全FOV/local模型：

- 4验证人9系列×PCHIP/linear=18条件完成。
- 患者先聚合，PCHIP full Dice `.1275216452`，missing `.1353040578`，recall `.1449649098`，absRVE `.7729488939`。
- 3系列完全漏检，能力门槛失败。
- 18组计数/物理距离、54完整plane重放通过。
- 本批总模型分支调用45,624；科学确认0。
- 3新论文/334正文块、MC-RC旧文19块补读登记完成。
- 上轮124文件stage和全局四项验收exit0，**不覆盖本轮新增内容**。

冻结权重：

- `experiments/mc_rc_global_local_task_training_cpu/final_update_20000.pt`
- checkpoint SHA `d2bdaccf111b88a1662e38a3e42abb9338aba7e82f0a6d8af2dc26917813e51f`
- final weights SHA `645727bb224c2745c4cbe9dcb23241d8994d6f241943ec93691d2e6e86f9a0cf`

### 当前最重要：先 poll session16876

**最后一次实际 poll 确认 session16876 live**，正在完整开发训练集诊断。不要依据时间或文件状态重启。

新协议：

- `MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_CPU_PROTOCOL_2026-10-03.md`
- `MC_RC_FROZEN_DEVELOPMENT_AFFINE_RESUME_PROTOCOL_2026-10-03.md`

当前运行入口：

`experiments/diagnose_mc_rc_frozen_global_local_development_attempt02_cpu.py`

输出：

`experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02/attempt_01.json`

只评训练匹配 PCHIP/observed_shared，完整19开发输入、全部原生z、固定冻结模型/.5，无训练更新、无隐藏MR。

最后输出已到013推断48/64层；012刚完成：

- 012 full `.1192125288`，missing `.1212939893`。
- 001两系列、002两系列、007、010一个系列、011均已见完全漏检。
- 004 `.32327`；005两系列 `.23863/.12108`；006三系列 `.34749/.17453/.27792`；009两系列 `.36904/.34658`；010另两系列 `.47512/.00673`。
- **完整聚合尚未读取，不提前宣布完整结果。**

### 本轮真实失败与修复

原session **70121实际exit1**，原输出保留：

`experiments/mc_rc_frozen_global_local_development_diagnosis_cpu/attempt_01.json`

原脚本：

`experiments/diagnose_mc_rc_frozen_global_local_development_cpu.py`

前三系列完成，第四系列002第二时点推断后，旧 `surface_metrics` 的严格orthogonality断言失败。不是训练进程问题。

开发19 affine中六个残差>1e−5，最大 `.000388951451`。新模块：

`experiments/mc_rc_full_affine_task_metrics_cpu.py`

采用六邻接surface体素中心→完整affine RAS→cKDTree距离，不放宽容差、不删病例、不修改旧metrics/support/验证结果。

attempt02：

- 仅复用前三个完整登记SHA的预测，复制并重新评分；这三项零新前向。
- 第四孤立输出保留但不沿用，重新生成；不能算独立复制。
- 生成与源码SHA记录：
  `experiments/frozen_development_affine_resume_generation.json`
- 原失败run的最终forward计数未写出；**不要虚报完整调用数**。

独立复核已实现但**尚未启动**：

`experiments/verify_mc_rc_frozen_global_local_development_cpu.py`

它已指向attempt02，要求19组指标、57完整plane重放。复用旧独立label/bincount/geometry算法；对非正交且非空surface另用分块 `scipy.cdist` 核全部双向距离，避免生产与复核仅共享KDTree算法。仍是同architecture重放，不是第二独立训练模型。

### Unified Focal 作者源码与CPU移植已完成

论文直接链接作者仓库。获取文件：

`literature/source_cache/unified_focal_author_code_2026-10-03/`

原始commit：

`411c9c5ce43b2ef847f0903d1b841512ad8d2eee`，2022-05-13。

仓库/commit/tree/raw响应及Git blob SHA1/SHA256都核过；未安装或import TensorFlow，未执行作者包。

实际读完README和 `loss_functions.py`，重要发现：

- 原代码第262行有 **IndentationError**；原字节保留。
- channel0背景、channel1前景。
- Tversky分母是 `tp + δ*fn + (1−δ)*fp`，δ提高FN权重；与正文扁平公式系数顺序有出入。
- 按每image空间求和，再平均batch/classes，区别于当前模型跨两个patch合并的前景Dice。
- asymmetric CE只压低背景，前景不加focal压制。
- FT背景 `1−TI`，前景 `(1−TI)^(1−γ)`。
- code weight乘FT，1−weight乘CE；默认.5时无命名差异。

报告：

`literature/2026-10-03_unified_focal_author_code_audit.md`

**实际源码阅读provenance尚未登记**；获取manifest的 `actual_source_read=false` 不回写，应另建阅读记录。本轮没有新增论文正文，不重复计论文数。

CPU移植：

- `UNIFIED_FOCAL_BINARY_CPU_PORT_PLAN_2026-10-03.md`
- `experiments/unified_focal_binary_cpu_port.py`
- 显式epsilon1e−7、weight.5、δ.6、γ.5，单logit sigmoid，两class，支持area softlabel。
- 是本项目适配，不能称原Keras训练复现或新loss。

已实际exit0：

1. `verify_unified_focal_binary_cpu_port.py`
   - 输出 `experiments/unified_focal_binary_cpu_port/attempt_01.json`
   - binary/soft/empty/full/extreme五情形scalar值核验。
   - 24个NumPy central finite-difference梯度通过。
   - MRI0/network forward0/training update0/GPU0。

2. `check_unified_focal_output_bias_cpu.py`
   - 输出同目录 `output_bias_and_input_guards_attempt_01.json`
   - 相同.7错误幅度：clean `.1624901677`，FN `.3081779025`，FP `.2348811747`。
   - negative/above-one/nonfinite target拒绝通过。
   - 单个toy方向不能外推真实recall收益。

### 下一步

1. **先poll16876**。实际exit且complete后，运行上述19开发独立verifier；保存其session并持续poll，不能重启。
2. 完整聚合并报告训练内表现，与已有验证低分区分。当前迹象显示训练内也不足，但需完整核验后表述。
3. 登记作者源码实际阅读/SHA及原syntax失败，保存本轮公开对话、用户goal续作和compaction请求。
4. 根据训练内结果另写可拟合性/同预算loss实验协议；优先既有开发012，不用验证患者训练，不改旧失败门槛。CPU移植已具备，真实新loss训练**尚未启动**。
5. 更新README/queue、当前handoff和新stage/global验收。**本轮报告、对话及归档尚未完成**。
6. 原native完整控制、6×5公平矩阵、直接/随机分辨率强对照、具体可观测修正、8确认患者和第二独立任务网络仍未执行。目标不能complete或blocked。

本轮最后公开更新说明：保留原affine评分失败和前三预测继续剩余系列；loss源码有缩进错误，CPU移植及24梯度核验只是后续对照准备。此次compaction请求未取消研究。
