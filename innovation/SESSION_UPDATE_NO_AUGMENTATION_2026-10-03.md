# 本轮阶段记录：无增强完整能力、GPU启用与下一单配方

**最终extension已经全部结束，以下“新单配方live/待实现”是之前归档时点。** 25991 actual exit0/20000updates；97494 actual exit0/20000新partial参考/原sampler/RNG/primitive/40000patch/最后权重；67623 actual exit0/新37完整输入；84382 actual exit0/新111plane以及全部label/count/full-affine/gate。新reporter actual exit0、PNG已view_image。所有本轮训练/评价均已实际exit，当前无自身live任务，不重跑。

完整阶段总两个20k能力模型=40000updates，两个全20000独立训练输入/源patch核验=40000draw/80000整patch；74完整评价/222独立plane；两GPU资源失败各10updates另外保留，不混为完成因素模型。新intensity_only训练409.009秒，四验证full/missing .222203130/.224017359、recall .230260680、absRVE .695023002、3/9TP0/0全空，5/6gate失败。开发full .342908628/3TP0/1全空。旧noaug验证 .068768436，新描述性提高，CPU/GPU不同训练执行/单seed/已见验证不能作增强因果或创新确认。

两种配方都不足以作为强重建评价器。新[完整结果](MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md)、[最新创新判断](INNOVATION_DECISION_AFTER_INTENSITY_ONLY_2026-10-03.md)、[下一强任务准备](GPU_TASK_CAPABILITY_NEXT_AFTER_INTENSITY_ONLY_2026-10-03.md)和[全部完成ledger](SESSION_EXECUTION_LEDGER_INTENSITY_EXTENSION_2026-10-03.json)是最终状态；八确认仍未开，第二独立任务模型尚未用于最终重建claim评价，科学确认0/goal active。

最终验收见[最终extension验收](SESSION_ARCHIVE_FINAL_VERIFICATION_NO_AUGMENTATION_2026-10-03.json)。原136文件验收保留，最终另存manifest/receipt；本轮前段公开对话版本也有字节快照，所有进度都按其当时状态解释。

用户要求继续根据MRI已有工作批量读论文/探索创新，CPU能验证先做，不能验证写准备，并把本轮内容保存在innovation；中途明确补充“可以用gpu”。因此GPU禁用偏好被覆盖，原CPU已绑定训练合同不迁移，新GPU入口单独保留协议/source SHA。不枚举/操作其他训练，不写根环境/.gitignore，不读locked IXI test，不委派代理。

## 实际完成的研究

- 新两篇原始JATS正文/图注表格文字共185提取块已读完并登记：2019 TTA不确定性与2020 k-space运动增强/直接任务对去伪影。原XML/text/block/SHA、重复嵌套段落、作者正文矛盾、真实GT和clean预测区别、筛98/106对和推理额外预算均保存于[全文报告](literature/2026-10-03_no_augmentation_task_fulltext_reading.md)。不把TTA/error关联、物理增强或直接任务称首创，未看原图像素/独立补充/作者代码或复现其实验。
- CPU训练4831实际exit0：11开发19series、随机初始化981602参数/seed20261004、20000更新、最后checkpoint/.5，训练期间验证前向0；每step匹配原sampling外生流、旧增强SHA/结束RNG，仅关闭整个bundle。训练计时3056.763秒，输入缓存1.934GB。
- CPU训练verifier90018实际exit0：全部20000旧aug/新reference/primitive/RNG、40000完整patch编号平面源像素映射、采样/学习率/metadata/权重通过；0前向/0训练。primitive生成/context库共享的独立性边界明确。
- partial预检72028实际exit0：19series、608旧rng/aug/none/primitive、1216两个新臂输入/标签身份/全patch映射通过；网络前向/训练0。它不是20k多患者训练流核验。
- GPU合成runtime预检实际exit0：RTX5090 D v2/torch2.11cu128，CPU/GPUfeature最大误差1.3173e-5、sigmoid3.0994e-6，重复GPU完全相同；患者/标签0，GPUglobal/local各2次。
- GPU评价15853实际exit0：完整19开发PCHIP→四验证9series各PCHIP/linear，共37；标签在预测之后加载，完整nativeFOV/.5、四域、full-affine ASSD/HD95。global/local2573/11827次，完整inference61.845秒，peak_reserved171966464bytes。
- GPU独立99483实际exit0：全部37 label/bincount/affine surface/患者均值/gate与111完整首中末plane重放通过，global/local111/480次。同架构不是第二独立训练网络。
- 相同checkpoint六固定CPU/GPU完整plane核对实际exit0，0mask差异，其中仅一张有预测前景；无label读取，CPU/GPU各global/local6/21。不能据此称37体积概率逐值相同。
- reporter实际exit0：全部37/患者/四域空和undefined完整[结果](MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md)、PNG/SVG及provenance；PNG已实际view_image检查。

## 科学结果与限制

开发full/missing Dice .686213574/.682023450，recall .768960140、absRVE .407929624，19series中2TP0/2全空；full precision整体undefined（9/11患者defined），不能只报剩余患者。

四验证raw PCHIP full/missing .068768436/.072293523，recall .046884826、absRVE1.371381311，9series4TP0/1全空；raw linear full/missing .070897549/.074795051。原六项gate全部失败，固定.5/最后权重/全患者不改变。旧全增强开发/验证 .127947/.127522；取消bundle提高训练内而验证下降。单seed、旧CPU评分/新GPU评分、已见验证，不作群体因果/显著性或去增强泛化优势。

本阶段解决的是弱任务能力的诊断，不是重建新claim。原45CISS HAT对pipeline PCHIP均值为正的反例及旧风险政策失败保留。具体创新问题及必须做的强对照见[创新判断](INNOVATION_DECISION_AFTER_NO_AUGMENTATION_2026-10-03.md)。科学确认0/goal active。

## 后续GPU实际尝试和失败

四臂80k同GPU协议/运行器已实现，但两次资源预检实际失败，原attempt不覆盖。52790 actual exit1：10updates、.0682037秒/步、总投影5456.296>3600；33664 actual exit1：10updates、全GPU kernel数值预检通过、.04590079秒/步、投影3672.063>3600。两网络分支分别56/44参数确有梯度，失败不是效果对照，合计20updates未生成新能力checkpoint/未开验证。原3600门槛未放宽。

另立单配方intensity_only固定20k、同初权重/患者series/z/patch/监督/loss/预算/.5/最后权重；不是完整因素，CPU历史不作为GPU精确因果控制。session25991已经启动且最后实际poll仍live；[观测快照](literature/source_cache/no_augmentation_intensity_gpu_live_observation_2026-10-03.json)时11700/20000、complete=false/errors=[]，首10 .05852317秒/步，总20k投影1170.463<1800门槛。快照时点和当前状态分开，不推断完成或重启。

当前新20k的训练全量verifier和新37/111 binding/evaluator/verifier尚须编写/运行；八确认继续关闭。完整80k/148预测/444plane未完成。后续具体文件/启用条件见[准备](GPU_GEOMETRY_INTENSITY_NEXT_PREPARATION_2026-10-03.md)与[单配方协议](MC_RC_INTENSITY_ONLY_GPU_CAPABILITY_PROTOCOL_2026-10-03.md)。

## 本轮内容与归档

[完整用户摘要](SESSION_USER_PROVIDED_SUMMARY_NO_AUGMENTATION_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_NO_AUGMENTATION_2026-10-03.md)、[实际exit/失败ledger](SESSION_EXECUTION_LEDGER_NO_AUGMENTATION_2026-10-03.json)、原论文、输入/代码/协议/checkpoint SHA、全部成功与失败、图表、后续准备均写在innovation。此前只见摘要的前段不伪造逐字历史。临时文件猜测/括号检查失败也写ledger，未改变研究attempt。

本阶段完整结果/source/code/reading与新准备的验收见[验收JSON](SESSION_ARCHIVE_VERIFICATION_NO_AUGMENTATION_2026-10-03.json)。新GPU单配方live结果仅以带时间快照归档，不把动态JSON哈希作为最终完成证据。此前归档结果保留；README/queue更新前字节快照保存在source_cache/no_augmentation_entry_snapshot_2026-10-03。
