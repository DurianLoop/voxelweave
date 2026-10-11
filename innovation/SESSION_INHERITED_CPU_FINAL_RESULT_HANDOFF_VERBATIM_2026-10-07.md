# 用户本次提供的接续摘要原文

以下是用户消息中可见的另一模型摘要原文；不是本助手补写的历史逐字记录。

任务仍 active，尚无可发表且独立确认的 claim。用户授权使用 GPU，但不得动其终端训练进程；所有内容只写入 `D:\MRI\innovation`。

**刚完成的关键结果**

CPU session **38045 已实际 exit0，结束，无需再 poll 或重启**。native/reference 与 raw PCHIP 各完成512更新，共1024；CUDA未初始化。两臂最终checkpoint全部保存后统一计算完整FOV。

| 指标 | native_reference | raw_pchip |
|---|---:|---:|
| 强制前景训练crop Dice | 0.834883136 | 0.814869522 |
| 完整训练系列Dice | 0.351452504 | 0.256330347 |
| recall | 0.975272008 | 0.976261128 |
| precision | 0.214347826 | 0.147533632 |
| absRVE | 3.549950544 | 5.617210682 |
| TP / FP / FN | 986 / 3614 / 25 | 987 / 5703 / 24 |

GT前景1011；预测前景4600/6690。两臂拟合gate均失败，主要是误报，并且训练crop也未达到.90。**不能据此声称SR损害病灶，或已经验证架构不能学习。**只训练了开发患者001的两个固定crop。

最终结果：
`experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json`

模型1,401,363参数，batch `[2,1,64,128,128]`，名义.5mm，seed20261007，深监督BCE+Dice权重4/7、2/7、1/7。原冻结协议：
`MC_RC_3D_CPU_FIXED_FIT_PROTOCOL_2026-10-07.md`

**接下来立即做**

均使用 `D:\conda\envs\MRI\python.exe -X utf8 -B`，路径以下相对innovation。

1. 运行已准备且不可覆盖修改的：
   `experiments/verify_mc_rc_3d_cpu_fixed_fit_2026_10_07.py`
   
   检查1024条history/LR、全部source/checkpoint/batch SHA，独立功能网络完整FOV和NumPy重采样、四域计数及gate。概率误差≤3e-6且二值预测相同。它是实现核验，不是第二独立训练网络。失败保留，用新版本修复。

2. 核验通过后运行：
   `experiments/diagnose_mc_rc_3d_final_patch_2026_10_07.py`
   
   已在最终效果打开前冻结协议：
   `MC_RC_3D_FINAL_PATCH_DIAGNOSTIC_PROTOCOL_2026-10-07.md`
   
   两臂最后权重分别检查原训练增强、仅flip、仅强度、identity四种相同crop；报告三head的BCE、soft/hard Dice、GT数量、前景/背景概率；闭式logit梯度与autograd比较。0新更新、不打开验证/确认。仅完成syntax检查，**尚未执行**。

3. 运行准备好的：
   `experiments/report_mc_rc_3d_cpu_fixed_fit_2026_10_07.py`
   
   生成完整结果Markdown和PNG/SVG，再view_image检查。注意图中absRVE高达5.6，可能压缩同轴Dice柱，必要时保留原源码/结果，另做新版本。

4. 写实际结果解释和下一步准备。候选路线已写：
   `INNOVATION_CANDIDATES_AFTER_3D_LOSS_READING_2026-10-07.md`
   
   优先仍是充分任务适配后预测具体缺层修正收益；另记录了“固定PCHIP参照的内部InstanceNorm统计”机制诊断，**未实现/未验证，不可称新颖性已确认**。当前训练crop和fullFOV都失败，需要充分更新/采样覆盖等能力对照。

5. 补齐本轮对话、terminal观察、handoff、实际exit ledger、图视觉登记。**当前这次compaction请求和本摘要尚未另存；CPU最终结果刚收到后尚未补归档。**

6. 最终归档入口已写、只syntax检查：
   `experiments/archive_cpu_fit_followup_2026_10_07.py`
   
   运行前须生成：
   - `SESSION_EXECUTION_LEDGER_CPU_FIT_FOLLOWUP_2026-10-07.json`
   - `SESSION_CPU_FIT_FIGURE_VISUAL_REVIEW_2026-10-07.json`
   
   该入口验证上述结果、全部失败、源码/SHA、旧165证据不变、相对链接、两张图视觉登记，生成新manifest/receipt；不覆盖旧归档。

**本阶段其他已完成内容**

- 原19开发series/608draw深监督审计 exit0：1,454,374,912重复GT值重放；forced-FG及whole-batch三尺度归零均0。
- 新密度汇总 exit0：
  `experiments/mc_rc_3d_supervision_density_2026_10_07/attempt01.json`
  
  forced前景比例最小0.0072479%、中位0.553417%、最大20.0832%。608个uniform crops中167个fine非空，其中half/quarter各11/17个GT归零；441个fine空crop保留undefined。不能将重复crop当独立患者或推断失败因果。
- 密度图已生成且view_image实际检查：
  `figures/mc_rc_3d_supervision_density_2026_10_07/supervision_density.png`
  
  provenance里的historical visual=false未覆盖，最终视觉登记需另写。
- metadata资源规划 exit0：
  `experiments/mc_rc_3d_19series_resource_planning_2026_10_07/attempt01.json`
  
  19series共238,714,000缓存voxels；双float32输入+共享标签2.6678368GiB。主机约100GB可用，缓存足够。native CPU实测3.6476秒/更新，单臂20k仅更新约20.26小时。其fit SHA是动态观察，不是最终证书；正式19series配方尚未冻结。

**论文阅读**

本CPU阶段实际读5篇可提取原文，共738块：

- 3D U-Net、DeepMedic：继承完成274块。
- *Do We Really Need Dice?* `2104.08717v4`：216块，正式DOI `10.1016/j.media.2023.103015`。
- Generalised Dice `1707.03237v3`：66块。
- Dice Semimetric `2303.16296v4`：182块。

新报告：
- `literature/2026-10-07_dice_region_bias_fulltext_reading.md`
- `literature/2026-10-07_generalised_and_soft_dice_fulltext_reading.md`

缓存、metadata、原始HTML、LaTeX公式及reading provenance完整保留。**Generalised Dice的三张数值表为SVG路径图形，已下载但未视觉核读，不宣称表值已读。**此前nnU-Net两篇另阶段157块，不重复计新增。

关键判断：区域偏置是拆分项偏好，不代表完整Dice必然全背景；当前hard GT直接换DML与原Dice理论等价；平均软占比GT与多rater不确定性不是同一语义。换3D/context/loss/采样/soft标签已有先例。

**GPU尝试及后续入口**

四个小型合成GPU尝试都已实际 exit1，全部保留：

- attempt01：继承输入模块设置 `CUDA_VISIBLE_DEVICES=-1`，初始化前失败，0更新。
- attempt02/03/04：恢复自身可见性，各1次合成float32更新，合计3次；无患者训练，BF16未执行。
- 最后shape仅 `[2,1,16,16,16]`。FP32三个head CPU/GPU概率最大误差：
  `8.9407e-7 / 1.0133e-6 / 1.7583e-6`，阈值差异全0。
- reserved峰值192,937,984 bytes超过小任务160MB门槛；清自身缓存没降低峰值，未再扩大门槛。
- 同一次guard的 `nvidia-smi free≈691MB` 与CUDA接口 `free≈23GB`不一致；不能把后者当共享物理可用显存，不猜驱动原因。

准备的新完整GPU入口：
`experiments/run_mc_rc_3d_gpu_fit_pilot_totals_v2_2026_10_07.py --attempt 02`

仅syntax/diff核对，**尚未执行**。保留原8GB启动、4GB运行、2.5GB peak、3600秒、float32、每臂512协议；增加两个显存接口同时过运行门槛及断言前资源记录。原GPU attempt01仍resource_deferred/0更新，不覆盖。最新退出后totals仍约1394MiB空闲，只有新totals≥8GB才启动完整入口。

**持续约束及归档入口**

- 不修改根环境、`.gitignore`；不读locked IXI test；不枚举/操作用户PID；不委派代理。
- 固定11开发/19series、4已见验证/9series、8确认/12series，同患者时点同角色。
- 八确认 `030/029/019/028/031/026/027/015`继续关闭，科学确认0。
- 原四验证gate及全部分母、患者内先均值后患者均值、9series无TP0不变；旧45CISS反证及addback/QDA/线性policy失败不撤销。
- 旧源码/协议/checkpoint/结果及失败保留SHA，修复另写新版本。
- 可见对话目前归档到：
  `SESSION_VISIBLE_DIALOGUE_CPU_FIT_CONTINUATION_2026-10-07.md`
- 继承摘要原文：
  `SESSION_INHERITED_CPU_FIT_HANDOFF_VERBATIM_2026-10-07.md`
- 旧native/3D阶段归档165证据已通过，新CPU阶段尚未最终统一归档。
- **目前无自身live计算任务。不要重启已经结束的38045。**
