### 当前状态

目标仍 **active**：持续研究，直到形成可发表且独立确认的 claim。目前尚未达成。**本轮所有自身训练、评价和核验进程均已实际结束，无 live 任务。不要重新运行旧入口。**

用户最初要求批量读论文、探索创新点、先验证可行内容，并把全部内容存入 `D:\MRI\innovation`；随后明确 **“可以用gpu”**，覆盖此前禁用 GPU 的偏好。

### 已完成

两种任务能力配方各完成 20,000 步训练及完整认证：

| 配方 | 开发患者均值 full Dice | 四验证 full Dice | missing Dice | recall | absRVE | 验证 TP=0 |
|---|---:|---:|---:|---:|---:|---:|
| 无增强，CPU训练 | .686214 | .068768 | .072294 | .046885 | 1.371381 | 4/9 |
| 仅强度增强，GPU训练 | .342909 | .222203 | .224017 | .230261 | .695023 | 3/9 |

仅强度配方改善已见验证均值，但仍有 **5/6 能力检查失败**；无增强全部六项失败。两训练执行设备不同、单 seed、验证已反复使用，**不能单独归因增强因果，也不能据此解释 SR 损害病灶**。

实际完成的本阶段总量：40,000 正式训练更新、40,000 draw/80,000 完整 patch 映射认证、74 完整输入评价、222 完整平面独立重放。重放验证实现，不能当第二独立任务网络的科学证据。

已结束的关键 session：

- 无增强：训练 `4831`、训练核验 `90018`、GPU评价 `15853`、评价核验 `99483`，均 exit 0。
- 仅强度：训练 `25991`、训练核验 `97494`、GPU评价 `67623`、评价核验 `84382`，均 exit 0。
- 两次 GPU 四臂 80k 资源尝试 `52790`、`33664` 均 exit 1，各仅发生 10 更新；失败完整保留。80k 投影分别 5456.296、3672.063 秒，超过冻结的 3600 秒门槛。**完整四因素/148评价/444重放未完成**，单配方不冒充因素结果。

新增两篇原始 JATS 全文共 **185 提取块**已实际阅读和登记：

- TTA uncertainty，2019，PMC6783308，DOI `10.1016/j.neucom.2019.01.103`。
- k-space motion augmentation / artefact removal，2020，PMC7116018，DOI `10.1109/TMI.2020.2972547`。

TTA/entropy/VVC/error 关联、物理增强、直接任务对先恢复均有先例。原文矛盾、真实 GT 与 clean 预测的区别、筛选 98/106 对、额外推理预算等限制已记录。未看原图像素、独立补充或复现作者实验；不要修改获取记录中的历史 reading=false。

### 约束与重要细节

- 新增内容仅写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不操作或枚举用户终端训练，不读 locked IXI test，不改根环境或 `.gitignore`。
- 不创建/委派子代理。
- 固定 **11开发/19系列、4验证/9系列、8确认/12系列**；同患者所有时点同角色。
- 八确认 `030/029/019/028/031/026/027/015` 效果继续关闭，科学确认数 **0**。
- 旧运行脚本、support、协议、checkpoint、结果均有 SHA 绑定，不能修改或覆盖；新尝试用新文件/目录。
- 现有 CPU 守卫：单线程、自身 below-normal、磁盘≥15GB、可用内存≥8GB。现有 GPU helper 使用 GPU0、10% allocator、peak≤2.5GB、free≥4GB；新实验应另定合理资源合同。
- GPU 是 RTX5090 D v2，torch `2.11.0+cu128`；可用量需重新只读检查，不能沿用旧空闲观测。
- 当前模型 981,602 参数、seed20261004、physical .5mm、五通道 z±2/±1/0mm、BCE+Dice+.5global、AdamW/cosine、固定20k、最后 checkpoint、阈值 .5。
- **代码中的 `native = sparse_image(...)` 只是原生网格上的 PCHIP 重建，不是真正完整 native MR。**
- 使用完整 affine RAS 的 ASSD/HD95；不要复用正交 EDT 假设。
- GPU训练 context/loss 与 CPU执行存在数值差异，CUDA grid_sample backward 不保证整体逐位重复。启用 GPU 时参考 `mc_rc_authorized_gpu_adapter.py` 的导入顺序，保留旧 CPU 模块的 CUDA 禁用逻辑。

原能力门槛保持：四患者先各自平均系列，再患者平均；full Dice≥.70、missing≥.65、recall≥.70、absRVE≤.50，四患者 full/missing 均正，9系列无 TP=0。保留空结果/undefined，不缩小分母或改门槛。

### 入口与归档

以下均相对 `D:\MRI\innovation`：

- `SESSION_HANDOFF_NO_AUGMENTATION_2026-10-03.md`：**顶部最终状态有效**，下方 live/11700/待实现属于历史。
- `MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md`
- `MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md`
- `INNOVATION_DECISION_AFTER_INTENSITY_ONLY_2026-10-03.md`
- `GPU_TASK_CAPABILITY_NEXT_AFTER_INTENSITY_ONLY_2026-10-03.md`
- `SESSION_UPDATE_NO_AUGMENTATION_2026-10-03.md`
- `SESSION_VISIBLE_DIALOGUE_NO_AUGMENTATION_2026-10-03.md`
- `SESSION_EXECUTION_LEDGER_INTENSITY_EXTENSION_2026-10-03.json`
- `literature/2026-10-03_no_augmentation_task_fulltext_reading.md`

最终实验归档验收已 exit 0：**194阶段文件、2191证据文件、2774本地链接**，全部重 hash 无差异。

- receipt：`SESSION_ARCHIVE_FINAL_VERIFICATION_NO_AUGMENTATION_2026-10-03.json`
- manifest：`literature/no_augmentation_full_task_final_manifest_2026-10-03.json`
- 原136文件初验单独保留，未覆盖。
- `SESSION_FINAL_RECEIPT_NO_AUGMENTATION_2026-10-03.md` 中有预拟最终答复；用户随后改为要求 checkpoint，应以本摘要为接续状态。

### 下一步

1. 阅读上述最新判断和准备文件，**不要再 poll 或重跑已结束任务**。
2. 实现独立的真实 native MR 参照 loader，限定开发/验证，认证 source pixels、UID/RCZ affine、标签轴，以及抽取 observed 层的 SHA 一致性；与稀疏部署接口隔离。
3. 准备更充分的 3D/较宽2.5D任务基线，分别核物理上下文、前景监督、完整 FOV 推断和 GPU 资源，冻结新架构/预算后训练。当前 native loader/强基线尚未实现。
4. 能力充分后再做 native/6×5公平矩阵、同 observed 直接任务和分辨率随机化强对照。
5. 只有稳定残余成立，才开发预测 **action gain** 的 observable 修正；最终冻结后才开八确认和第二独立任务评价器。

精确创新问题仍是：充分任务适配后，在同 observed 信息/统计/监督/容量/预算下，是否存在能胜过强 raw PCHIP 和直接任务适配的可观测缺层病灶修正。尚未验证其正答案。旧45CISS反证“SR平均损害任务”的结果及失败的 addback/QDA/线性政策不能撤销或改名重启。

本次压缩请求及本摘要尚未额外写成新文件；下一位可先补存到 `innovation`，不要改动已验收实验文件。
