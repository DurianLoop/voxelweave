# 最新接续：两模型40k/74完整评价/222plane均已实际结束

**最新覆盖状态：所有本轮任务已经实际结束，不要再poll/重启25991。** intensity-only25991 actual exit0/20000updates；训练verifier97494 actual exit0/全部20000partial reference/RNG/primitive/40000patch/checkpoint；GPU37 evaluator67623 actual exit0；GPU111 verifier84382 actual exit0。新[完整结果](MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md)和PNG/SVG生成、PNG已view_image。

新intensity-only开发/验证full Dice .342908628/.222203130，验证missing .224017359/recall .230260680/absRVE .695023002，3/9series TP0/0全空，6gate只有四人full/missing均正通过，其余5失败。旧noaug验证 .068768436，只作单seed/CPU-GPU不同训练执行/已见验证的描述，不归因增强因果。新训练409.009秒，最终权重d26a9f3b...，完整checkpoint/例SHA/报告均冻结。

当前无自身live训练/评价；以下11700/live/待实现段落仅为本轮归档中间时点，**都已被本段完成状态覆盖**。不重跑两CPU/GPU20k、两37/111与两个资源失败。接下来按[下一强任务准备](GPU_TASK_CAPABILITY_NEXT_AFTER_INTENSITY_ONLY_2026-10-03.md)做独立native参照loader资格/更充分任务架构与监督/合理GPU预算；不要用弱模型继续SR机制claim。先读[最新创新判断](INNOVATION_DECISION_AFTER_INTENSITY_ONLY_2026-10-03.md)。八确认仍关闭，科学确认0，goal active，无可发表且独立确认claim。

本轮全部公开对话/用户摘要/两原始全文/成功与两个失败/代码输入权重SHA/图表/后续准备见[最终阶段记录](SESSION_UPDATE_NO_AUGMENTATION_2026-10-03.md)、[完成extension ledger](SESSION_EXECUTION_LEDGER_INTENSITY_EXTENSION_2026-10-03.json)和最终归档receipt。初次136文件验收保留，最终extension另存manifest/receipt。

---

以下为此前动态接续状态的历史正文：

**先实际poll session25991**，运行器 `experiments/run_mc_rc_intensity_only_gpu_capability.py`，动态输出 `experiments/mc_rc_intensity_only_gpu_capability/attempt_01.json`。最后实际工具poll返回live，带时间[观测快照](literature/source_cache/no_augmentation_intensity_gpu_live_observation_2026-10-03.json)时11700/20000，complete=false/errors=[]；可能继续推进，不按时间推断exit、不重启live/完成任务。不修改绑定script/support/protocol。

用户最新明确“可以用gpu”，覆盖先前禁GPU。新增仅innovation，Python D:\conda\envs\MRI\python.exe -X utf8 -B；不委派代理，不枚举/操作用户终端训练，不读locked IXI test，不改根环境/.gitignore。CPU单线程/自身below-normal/15GB磁盘/8GB可用内存；GPU0 allocator10%/peak≤2.5GB/free≥4GB，用户GPU容量只读观测，不操纵其他任务。

新single intensity-only GPU：同981602参数/seed20261004/a146c0c4...初权重、11开发19series、raw PCHIP/observed_shared、原外生patient/series/z/patch流/源支撑、BCE+Dice+.5global、AdamW/cosine、固定20000、最后checkpoint/.5。CPU冻结input/context/resize/labels/坐标生成，network/context grid_sample/loss在GPU；无AMP/TF32，cuDNN deterministic；CUDAgrid backward不保证整体bitwise可重复。首10 .05852317秒/步，总20k投影1170.463<1800。验证在checkpoint前0，八确认不开效果。它是有界单配方能力开发，不是完成四因素或同CPU/GPU因果控制。

已结束、不要重跑：

- 无增强CPU4831 **actual exit0**：20000updates，最终checkpoint已冻结。
- 训练verifier90018 **actual exit0**：20000旧aug/新reference/primitive/RNG、40000完整patch支撑、最后权重/采样/LR通过，0前向/训练。
- partial输入72028 **actual exit0**：608rng/冻结primitive、1216新partial输入/标签身份/完整patch，0网络/训练。
- GPU37 evaluator15853 **actual exit0**：19开发+18四验证完整条件、global/local2573/11827，inference61.845秒。
- GPU37/111 verifier99483 **actual exit0**：全部label/count/full-affine/患者均值/gate与111完整plane通过，global/local111/480。
- GPUsynthetic runtime/samecheckpoint六plane device核对/reporter均actual exit0，六mask0差、只有一张有预测前景。PNG已view_image。不要以六plane扩展为37概率等价。
- 四臂80k第一GPU52790 **actual exit1**，10updates、投影5456.296>3600；第二fullGPU33664 **actual exit1**，10updates、投影3672.063>3600。两个失败保留，不重启、不续用失败权重。两个分支梯度/全GPUkernel预检已通过，不是新能力结果。四臂/148/444全部未完成。
- 两篇新原JATS全文185块已读完和登记：2019TTA、2020k-space运动/直接任务对去伪影；原文矛盾和GT/clean预测/98筛样/推理预算限制保留。获取/登记已exit0，勿把旧获取reading=false改掉。

完整主结果：开发full/missing Dice .686213574/.682023450，19series2TP0/2全空；四验证PCHIP .068768436/.072293523、recall .046884826、absRVE1.371381311、4/9TP0/1全空，**六项原gate全部失败**；linear .070897549/.074795051。旧增强开发/验证 .127947/.127522。去增强提高训练内而验证下降，单seed/已见验证、不能归因SR。全precision因空结果保留undefined，tail也不删除。

下一明确工作：

1. 继续25991到真实exit；若失败，保存原attempt，不能重启或修改绑定代码。
2. 若complete=true/errors=[]，编写新的**intensity-only全20000训练verifier**：认证全部源/SHA/primitive/原stream/RNG、独立partial tensor SHA/40000源patch/采样/LR/最后checkpoint。源cases/prod是训练source_bindings[5]/[6]，原noaug已核训练是[0]、proof[1]；`arms[0]`含20k example SHA、初/终权重、counts/history/checkpoint。primitive/context/库共享边界披露。该verifier现在尚不存在，不能套原noaug verifier的schema。
3. 编写新binding及完整19开发PCHIP→9验证各PCHIP/linear共37评价/111plane verifier。可复用已冻结无增强GPU脚本的逻辑，但**不能修改旧脚本/协议/结果**；新训练header与checkpoint在arm里、需明确认证后新接口。训练GPUcontext与评价CPUcontext的数值边界另行说明。全部37保留，原四验证门槛不改，不称独立确认。
4. 能力充分后原生控制/6×5公平矩阵/同observed直接任务与分辨率随机化；弱能力时继续架构/监督/任务适配。只有残余成立才具体observable修正，八确认及第二独立训练任务网络最后冻结后开。科学确认0，没有可发表且独立确认claim；goal active，不complete/blocked。
5. 本阶段归档是已完成无增强科研批次+两个失败+下一single GPU带时间观测/源码准备；它不证明新20k最终完成。归档结果链接在阶段记录，最新阶段实际check后继续保存后续公开对话和代码/源SHA。

入口：[完整结果](MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md)、[创新判断](INNOVATION_DECISION_AFTER_NO_AUGMENTATION_2026-10-03.md)、[后续准备](GPU_GEOMETRY_INTENSITY_NEXT_PREPARATION_2026-10-03.md)、[阶段记录](SESSION_UPDATE_NO_AUGMENTATION_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_NO_AUGMENTATION_2026-10-03.md)、[实际exit ledger](SESSION_EXECUTION_LEDGER_NO_AUGMENTATION_2026-10-03.json)。
