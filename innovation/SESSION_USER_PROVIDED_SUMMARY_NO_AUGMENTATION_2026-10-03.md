# 本次接续收到的用户提供摘要

以下逐字保存用户给出的上一个模型摘要；其中 live、未运行等状态仅对应接续时点，不覆盖后续实际结果。

目标仍 **active**：持续探索验证，直到形成可发表且独立确认的 claim。当前尚未达成。上一轮是实质进展；本轮新增了核验/评价实现和两篇全文阅读，训练仍需继续观察。

### 约束

- 新增内容仅写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不使用 GPU，不枚举或操作用户终端训练，不读 locked IXI test，不改根环境/`.gitignore`。
- 不创建/委派代理。
- CPU 单线程、自身 below-normal，磁盘≥15 GB、可用内存≥8 GB。
- 不重启 live 或已完成任务；失败保留，修复用新 attempt。
- 固定11开发/19系列、4验证/9系列、8确认/12系列。八确认效果继续关闭。
- 下列路径均相对 `D:\MRI\innovation`。

### 首先轮询当前训练

**session `4831`**：

`experiments/run_mc_rc_no_augmentation_all_development_cpu.py`

输出：

`experiments/mc_rc_no_augmentation_all_development_cpu/attempt_01.json`

本轮最后实际 poll 返回仍 live，显示 **7900/20000**；随后完成新论文阅读/写笔记，**尚未再次实际 poll**。不要根据时间推断完成或重启。

训练固定：11开发19系列、981602参数、seed20261004、原20k相同初权重/输入/监督/外生采样、BCE+Dice+.5global、AdamW/cosine、最后 checkpoint，仅关闭增强 bundle。每步核旧增强 SHA 和结束 RNG 状态，保存新输入 SHA/primitive SHA。不能修改运行中脚本、support或已绑定协议。

协议：

`MC_RC_NO_AUGMENTATION_ALL_DEVELOPMENT_CPU_PROTOCOL_2026-10-03.md`

### 上一轮已完成，勿重跑

入口：

`SESSION_HANDOFF_COVERAGE_AUGMENTATION_2026-10-03.md`

- 四臂训练 **25480 actual exit0**，三新臂共12000 updates。
- full Dice：
  - legacy_aug `.865311916`（旧臂精确复用）
  - legacy_none `.965504055`
  - coverage_aug `.747640783`
  - coverage_none `.914331078`
- 两个无增强臂通过原单病例 fit gate；单012/单seed，不是泛化或重建创新。
- 因子 verifier **53787 exit0**：16000 draw SHA、全部指标/完整 affine 距离、12完整 plane 重放。
- 19系列采样预检 **31096 exit0**：608 RNG/旧SHA/新reference，1216完整 patch 源像素映射，网络前向/训练0。
- 前景曝光约1877→684，coverage 两臂 tail FP5821/2449，必须保留。
- 上一阶段归档最终四检查全通过：78 stage 文件、2172 evidence、2670链接。首轮缺验收JSON链接的失败已保留。
- README/queue目前仍指向上一阶段。不要覆盖其已完成结果。

### 本轮新实现：代码已写，尚未运行实际核验/评价

1. **训练独立 verifier**

   `experiments/verify_mc_rc_no_augmentation_all_development_training_cpu.py`

   必须等训练实际结束、complete=true/errors=[]后运行。计划核全部20000 draw、40000完整 patch 映射、旧 SHA/RNG、新 reference SHA、primitive SHA、采样计数/学习率、checkpoint/meta/权重。网络前向0、训练0。

   独立性边界：primitive metadata 共用冻结生成器；旧 sampler、reference tensor assembly、编号整平面源像素支撑分别核验，不假称完全独立算法。

2. **新 frozen binding**

   `experiments/mc_rc_no_augmentation_evaluation_binding_cpu.py`

   要求新训练与训练 verifier完成；认证19开发和9验证输入、角色、几何、checkpoint。旧 binding 未修改。

3. **完整评价**

   `experiments/evaluate_mc_rc_no_augmentation_full_task_cpu.py`

   协议：

   `MC_RC_NO_AUGMENTATION_FULL_EVALUATION_CPU_PROTOCOL_2026-10-03.md`

   固定顺序：19开发 raw PCHIP → 9验证各 raw PCHIP/raw linear，共 **37完整条件**。标签在完整预测后加载。完整 native FOV/.5、full-affine ASSD/HD95，保留四域、FP/FN、体积和空/undefined。

   输出预定：

   `experiments/mc_rc_no_augmentation_full_task_evaluation_cpu/attempt_01.json`

4. **评价独立 verifier**

   `experiments/verify_mc_rc_no_augmentation_full_task_cpu.py`

   计划全部37独立 label/bincount/affine surface及 **111完整 plane 重放**，独立患者均值/gate。共用 scipy KDTree库，surface mask构造不同；同架构重放不是第二独立训练网络。

前三个新脚本曾实际 `ast.parse` 通过；第四个写完后尚未做语法检查。上述37/111均是计划，**没有实际模型评价结果**，也没有训练 verifier结果。

原验证能力门槛保持：患者先series平均再四患者平均，raw PCHIP full Dice≥.70、missing≥.65、recall≥.70、absRVE≤.50；四人full/missing Dice均正，9series无TP0。四验证此前用过，不是独立确认。

### 本轮两篇新全文已读完并登记

目录：

`literature/source_cache/no_augmentation_task_fulltexts_2026-10-03/`

- **Aleatoric uncertainty estimation with test-time augmentation for medical image segmentation with convolutional neural networks**，2019，PMC6783308，DOI `10.1016/j.neucom.2019.01.103`，**0–90共91块全部实际读完**。
- **A k-Space Model of Movement Artefacts: Application to Segmentation Augmentation and Artefact Removal**，2020，PMC7116018，DOI `10.1109/TMI.2020.2972547`，**0–93共94块全部实际读完**。

获取脚本已 exit0；登记脚本已 exit0：

`literature/register_no_augmentation_task_reading_2026_10_03.py`

报告：

`literature/2026-10-03_no_augmentation_task_fulltext_reading.md`

`reading_provenance.json` 绑定原XML/block/text、报告SHA和实际185块。不改获取时 reading=false历史记录。没有看图像像素/单独补充/作者代码或复现作者实验。

关键限制：

- TTA/entropy/VVC及错误关联已有先例，20/40次推理额外预算；不能当跨域误差保证或第二训练网络。
- 2019正文块69“not significant (p<.05)”矛盾，报告明确保留。
- 2020已有直接任务 vs 先去伪影再分割；106真实 MPRAGE test-retest主要以clean预测作reference，不是独立手工GT准确率。
- 去伪影真实图像评价筛到98对、TIV mask，改善不显著；不能推广为全106病例。
- 2020正文与Fig7图注关于KLD/variance组合有不一致，记录未擅自修正。
- 两篇排除宽泛“不确定性修正”“直接任务胜过恢复”“物理增强”首创。

### 下一步

1. **先实际 poll 4831**，继续同句柄直到真实 exit。
2. 训练结束后运行训练 verifier，保留失败，不能修改运行中绑定源码。
3. 核验通过再运行37条件 evaluator及111-plane verifier。
4. 全部报告训练内与四验证能力；若失败，保留失败，不归因SR、不改门槛。
5. 只有能力充分后推进native/6×5公平矩阵、直接任务/分辨率随机化、具体observable修正；最后冻结后八确认及第二任务网络。
6. **本轮归档尚未完成**：保存本轮公开对话/此次compaction请求，写新阶段记录与handoff，更新README/queue并做stage/global归档。此前78/2172/2670检查不覆盖本轮新文件。

当前精确创新问题仍是：充分任务适配、同observed信息/统计/监督/预算后，是否存在优于强raw PCHIP和直接任务修复的可观测缺层病灶残余。科学确认0，不可 complete 或 blocked。
