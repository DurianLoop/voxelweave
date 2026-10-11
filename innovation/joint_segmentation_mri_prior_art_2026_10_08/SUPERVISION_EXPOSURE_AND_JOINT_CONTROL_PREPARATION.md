# 监督曝光与联合控制的后续准备

触发证据是SegNetMRI的三阶段/不同batch-unit训练，以及calibrationless的4/40seg labels+全部40reconstruction targets、matched-parameter共同训练Cascade。这里准备后续研究合同，不在结果后改原能力gate/端点，不替代实际资源实测，不要求现在启动新joint训练。

## 将来需要绑定的监督账

为每项训练单独记录patient/series role、observed输入来源、target类型、target来源角色、manual/algorithmic label、optimizer更新、patient/patch/voxel曝光、增强draw、pretrain/continue/joint阶段、checkpoint和source content SHA。次数/epoch和patient遍数不相互替换。记录“本次只使用seg标签的患者数”之外，也记录被reconstruction loss或encoder预训练用过的全部患者数，以及每阶段全部实际训练成本。

manual lesion、FAST/SAMSEG类pseudo组织标签、native HR reconstruction target、部署可见input不是同一监督对象。未来若用开发HR图做reconstruction target，须在方法启用前单独冻结允许的监督及资源合同，给受控对照相同训练信息；不能静默加进已冻结task-only三臂。部署action、feature和任务网推断仍只看合法observed；native_reference始终仅能力参照，不填成action gain。

unlabelled仅表示缺seg labels时，不写成unsupervised/no-target：有fully-sampled reconstruction target的loss仍是监督。患者外确认要求整个representation/reconstruction/task/head/calibration链未使用该患者，不只head LOPO。8未见/12series与lockedIXI继续关闭，原11/19开发与已见4/9角色保持。

## 控制层次与执行决定

| 候选将来变更 | 需要的比较与账 | 现在状态 |
|---|---|---|
| 固定修正后的分割改善 | 各部署输入自己的充分适配任务网，common observed/初始化/监督/增强/容量/预算，原全FOV病灶端点 | 原final/gates前不生成新label |
| 共享encoder或joint loss | 与共同训练的级联比较；精确learnable参数、全部reconstruction target与额外训练曝光匹配；另记冻结任务网对照作为失配诊断 | 可选另立方案，本轮未实现/资格化 |
| 低标注/auxiliary reconstruction | patient-level预定labelled subset，其他开发MRI exposure/target全部计入；强对照获得同target覆盖；不得拿pseudo endpoint充manual lesion | 本轮不削减现有标签或重分patient |
| 动态修正/选择器 | backbone静态继续训练等量曝光，加全费用、双路径cost/defer、DC-based、最强固定动作 | 真实动作余量与成本尚缺 |

共享网络不是必须加入的第四臂，也不是绕过三臂真实资源的理由。保留当前三臂legacy_dense/direct/common_projected_dense的主要对角比较；formal充分适配训练的预算、最终权重及是否增加joint诊断，必须据真实资源在看新task结果前另冻。不能把未定预算准备写成可直接执行的正式runner。

## 可证伪的判断

对已冻结完整患者Dice/boundary/volume端点分别判断。原文两fold×三组织的4正2负，不许通过新建tissue平均或SNR+Dice复合分数把它改成“全胜”；本项目也不看到结果后改主要端点。原native能力差异不替代可部署表示差异。

若强适配后合法动作没有病灶余量，就不使用旧weak9pair或57,600旧gain训练新正式head；若只有frozen/cross-input失配下改善，则以失配诊断记录。余量成立后才测真实全部费用和固定/已知强策略，再冻结所有组件，最后开8未见患者确认。失败与阴性结果原样保留。

