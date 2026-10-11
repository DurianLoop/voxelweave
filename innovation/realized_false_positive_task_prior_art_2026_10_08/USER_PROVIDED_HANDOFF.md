# 本次接续用户提供的交接摘要

以下保存当前用户消息中提供的交接内容。它是已提供的摘要，不等同于此前所有轮次的原始对话逐字稿；本次能看见的用户消息、公开进度、失败和更正另存VISIBLE_DIALOGUE及ACTUAL_OBSERVATIONS，前轮冻结对话通过归档链保留。

目标仍 active：**持续研究、探索、验证，直到形成经验证的可发表 MRI claim；不要动用户现有终端训练。** 尚无已验证 MRI claim。上一轮是实质 progress；当前轮正在精读 MIRTO，未归档。

### 约束

- GPU 已获授权，但最近仅 free **1394 MiB**，新增医学作业既定 **8,000,000,000 bytes** 储备未满足。
- 不停止、重启、迁移、修改原训练，不操作其他 PID，不委派代理。
- 新文件只写 `D:\MRI\innovation`；已执行/绑定/冻结文件不改，修复另存版本。
- RAM、磁盘各留十进制 8 GB；不删历史、不改环境。
- 开发 **11 患者/19 series**；已见验证 **4/9**；未见确认 **8/12**、locked IXI 关闭。
- 执行：
  ```powershell
  & 'D:\conda\envs\MRI\python.exe' -X utf8 -B '脚本路径'
  exit $LASTEXITCODE
  ```
- 根 SHA 不变：
  - `.gitignore`：`7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524`
  - `environment.yml`：`dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257`
- PDF 技能已读，便携 PDFium 可直接复用，不重新安装。

### 先核查真实训练

接续先 poll **session 99542**。

本轮初始 `d63fcf` 返回 live、空输出、无 terminal exit；不是结束。最新真实 `b216db`：

```json
{"kind":"raw_pchip","updates":7128,"loss":0.17324107885360718,
 "new_updates":26928,"cumulative_wall_seconds":62253.950327}
```

native 19998 已完成是历史报告，raw 未 final。两臂各19998、总39996、累计30h现合同不变。`new_updates` 是 invocation02 新增累计，非 raw 单臂步数。

本轮 GPU `aa92d7`：1394 MiB、util90%。`2a807a` guard：disk **8,124,637,184 bytes**，RAM **99,119,550,464 bytes**。

### 已完成、已归档的上一轮

目录：
`innovation/adaptive_compute_task_budget_prior_art_2026_10_08`

- RD-ViT **2605.03999v1**：23完整文字页、12视觉页。
- HiFi-MambaV2 **2511.18534v1**：9完整文字页、7视觉页。
- 共32文字/19视觉；39行公开表审计 **d2ebe6=0**。
- RD MoE 参数53.2592%、Dice99.3880%，**训练时间1.94924倍**；不是推理加速。
- HiFi 同patch P1/P2 FLOPs为前代约2.54倍；M4Raw P1 AF8三指标略退化，表/文字多处不一致。
- CPU数学反例：
  - 保留所有attention时，ACT `8/1.4`不能当完整加速。
  - A=.36、f=.8*tanh(h)有界，却有三个不动点，A稳定不足以保证全非线性映射contraction。
  - soft概率近均匀可仍hard路由100%集中；不是作者模型实测。
- 四个repo查询返回 **9条 metadata**，未读README/源码；同名Recursive Dynamic-Dimension仓库不符合本篇身份。不能称作者未开源。
- Record **e531a5=0**；archive **cd597b=0**：
  - 前5191 SHA全部不变
  - 新101，累计 **5292**
  - manifest SHA：
    `78957a4b0a3696f9bf3d0a44e8bc2b5ca2baf5ec7ca5af8ece5331ad1ba09db2`
  - proof SHA：
    `b608ea26f2d9a099c71529723a7a905596c9b47bbbacd8a06127982179b63dc3`
- Post **c7ac30=0**。
- 下一归档须纳入该目录 manifest/proof/post三文件，共五文件；排除 rolling 训练。
- `RESULT.md`、`PRIMARY_READING.md`、`ACTION_VALUE_AND_ACTUAL_COMPUTE_CONTROLS.md`、可见对话均已冻结。
- 0新医学数组/权重、神经/GPUforward、训练/head/action labels；goal active。

### 当前新阶段：MIRTO

目录：
`D:\MRI\innovation\realized_false_positive_task_prior_art_2026_10_08`

目前已有：

- `PROTOCOL.md`
- `PRIMARY_SELECTION.md`
- 已执行 `fetch_mirto_primary.py`
- `primary_attempt01`：PDF、43页提取文字、headers、receipt
- `AUTHOR_SOURCE_PLAN.md`
- 已执行 `fetch_mirto_repo_identity.py`
- `author_identity_attempt01`：repo metadata、tree403错误、receipt

**尚无渲染、CPU审计、阅读笔记、RESULT、ledger、归档/post。**

原文身份：

- **2610.02136v1**
- Negin Kafee Hernashki、Soumick Chatterjee
- *MIRTO: a registration-gated, multiverse-tested evaluation protocol for unsupervised anomaly segmentation in brain MRI*
- 实际上一索引 `mri_budget` 返回，之前仅摘要；本轮 `2a807a` 再核身份。
- 下载 **ad0bf6=0**，HTTP200、43物理页、1,123,674 bytes。
- PDF SHA：
  `275e37b395014a2a64fb45fc1f40402d6d636d52b8e4d5c3c2a5a6401c6038c1`

### MIRTO实际阅读

已读文字内容的页：
**1–28、32、33、35、37、39、40、43，共35页**。

初次1–12批读外层输出截断：
- `9bf022` 页1–6、`ac相关第二chunk` 页7–12的组合输出截断。
- 实际显示1–3与10–12完整；4–9随后补读。
- 为阅读 provenance 最稳妥，接续再小批读 **1–3、10–12**，避免用外层截断输出支持整批已读。
- 已明确完整补读：
  - `3dbd85`：4–6
  - `914d31`：7–9
  - `ac072d`：13–16
  - `cc5835`：17–19
  - `911b5a`：20–23
  - `45c8cb`：24–26
  - `875dfa`：27–28
  - `857aa7`：32–33
  - `9b657d`：35、37
  - `4ccb5d`：39、40、43
- `47a12e` 只读27–43各页头12行作定位；**不算这些页完整阅读**。
- 未完整读：29–31、34、36、38、41–42。
- 纯参考页23、24；22还含code/disclosure，不能算纯参考。
- **尚无任何视觉核读**。

### MIRTO关键事实与待核问题

- 312 BraTS2020 test、24 disjoint validation；**同312用于协议开发和检验，全部探索性**。未见独立确认。
- 四UAD方法：REFLECT、UCCD、cDDPM、AnomalyDINO；fixed stored maps，不再GPU推理。
- 同IXI源 **不是同训练曝光/优化预算**：
  - REFLECT504 volumes，UCCD324/81，cDDPM361/92，DINO memory50。
  - 单seed/每训练集一个模型；cDDPM不同训练集2854 vs79040steps。
- canonical完整tumor不重采样，out-of-FOV score0保留；方法裁剪/自身reference与正式主分母分开。
- 页5 Eq10 validation阈值；Eq11 test-matched阈值 **明确只作GT-informed诊断，不可部署**。
- Table4 页15，b20：
  - REFLECT Dice.497、FP16.3
  - UCCD .539、FP18.9
  - cDDPM .519、FP12.9
  - DINO .166、FP17.5 cm³
  - 同nominal b不等realized burden。
- 页13：UCCD−cDDPM validation **+.020**，equal realized FP **−.001**，间隔包含0。
  - Identity1：Δval=Δmatched−(ga−gc)
  - ga=.002、gc=.023，解释+.021变化。
  - Table29页32打印值有舍入，不能要求严格0误差。
- Post-processing：
  - Table37页35 UCCD b20 total **.0846** = fixedτ **.0064** + relaxation **.0782**，约92.4%来自阈值放宽。
  - Table7页16三位打印均值有±.001舍入残差。
  - Above-floor lesion sens UCCD **.674→.629**；其他也下降。Dice升不代表漏检改善。
- Lesion分母：6-connectivity、floor50mm³、IoU≥.1；472 above-floor vs5473 all components；REFLECT命中287不变，.608 vs.052，约11.6倍仅分母。
  - **不能把这些floor移植来删本项目单体素标签**。
- “label-free diagnostics”实际上页5用 **maps和已有reference labels**，只是无需额外标签，不是部署无需GT。
- Jaccard Eq9是reverse triangle inequality，对同一集合域的任何P/RA/RB总成立；原文称“违反可证reference不同”不准确。可CPU穷举验证；never violated不是geometry correct证据。
- CRC页6/25：
  - loss1[FP>b]，n校准时 α≥1/(n+1)才能满足其公式的非空可行集。
  - n24 α.1 → Beta(2,23)，mean.08、CDF(.1)=.708、q97.5=.211。
  - **marginal guarantee不是当前校准集95% guarantee**，需RCPS/LTT等。
  - 可CPU算本项目小n4/8/11限制；不能把已见开发/验证自动视作合法独立校准集。
  - 8未见患者即便0伤害，一侧95%二项upper≈31.2%，不支持低风险population保证。这是未来条件算术，不读确认数据。
- Bootstrap页9/25：
  - patient resampling，B10000（multiverse1000），test阈值每replicate重选。
  - validation阈值固定，**区间未含校准拟合不确定性**。
  - raw双侧p floor2/(B+1)，Holm K32 floor.0064，原文却称统一 `pH<.005` at floor，需记录该打印规则矛盾，源码未核。
  - Holm只声明families，不覆盖同队列所有探索选择。
- Latent aggregation：
  - 页18/19 +.052、+.038来自两训练checkpoint，**同测试队列**。
  - MAD不是两个模型一致赢家，作者最终只支持aggregation family；原计划六规则算不了，替代family探索性。
  - Table52页39阈值grid .01不同主.005，.492 vs.497不是自动矛盾。
- Cost页39/40 Table55：
  - REFLECT inference3:07:18、32.5s/volume；DINO15:23、2.7；IterMask3D2:43:04、28.3。
  - 似乎对应约346 volumes，312+24=336，**别擅自补分母，须算并记录未打印清楚**。
  - REFLECT训练记录不是此checkpoint，UCCD/cDDPM训练无法核而省略，Dinomaly估算；不能用于公平效率结论。
- 软件页43说31synthetic tests，但未读源码，不称已复现。

### 作者repo已实际访问，但受API限流

页21实际作者链接：
`https://github.com/soumickmj/MIRTO`

`fetch_mirto_repo_identity.py` **32f8e6=1**：

- repo metadata GET200：
  - full_name `soumickmj/MIRTO`
  - default_branch `master`
  - description **“The repo is coming soon! Let's have some MIRTO while waiting!”**
  - created2026-09-30、pushed2026-10-02、Apache2.
- 下一git tree GET **403 rate limit exceeded**，错误原文已保存。
- 没取得tree/README/源码，不能把metadata的coming soon当已完整核查。
- 正常匿名GitHub网页 GET 可作安全fallback，不需重复API或权限申请；写新fallback plan/script，保留原失败，不改已执行源码。
- 这是远端API限流，不是自动审批拒绝。自动审批拒绝0。
- 若公开页面确实仅placeholder，记录实际README/文件列表，不猜不存在的代码，不执行作者代码/安装环境。

### 本轮公开进度要保存

1. “上一轮取得了两篇新原文和可复核的 CPU 结果，属于实质进展，但还没有 MRI 效果证据。我先核查训练和既有验证入口，再推进与患者漏检、假阳性和预算约束直接相关的工作；GPU 资源足够且前置条件满足后，就接入医学验证。”
2. “MIRTO 原文揭示了一个重要的比较问题：相同的名义假阳性预算，可能在测试患者上产生不同的实际负担，进而改变 Dice 排名。它也明确将测试集上匹配假阳性的阈值标为诊断分析，并承认同队列开发的结果仍属探索性。我会把这些条件核清，避免后续把阈值转移带来的优势当作修复收益。”
3. 最新用户消息要求context compaction/handoff；未取消原goal。

### 下一步

1. poll99542，核GPU/RAM/disk；不改原训练。
2. 小批补读1–3、10–12；必要时读尚未读的关键附录，准确计页。
3. 渲染/逐张核关键身份、Eq9/CRC、Table4/7/29/37/55与探索声明，render≠read。
4. 正常GitHub网页fallback核作者repo实际状态。
5. 有意义的CPU公开算术：
   - 真实/名义FP、transfer与postprocess分解，舍入容差明确；
   - CRC Beta与小患者数/零伤害upper条件限制；
   - Jaccard穷举前提；
   - 表55时间分母不补造。
   不写额外镜像测试或重复合成资格。
6. 写MIRTO笔记、与项目匹配的阈值/漏检/完整患者控制；不要改现行threshold/gates或开确认集。
7. 保存本轮对话、真实失败与后续尝试，ledger→接前**5292**archive→post五文件链。
8. 主要候选仍需MRI验证：**同容量充分适配后，固定observed CISS合法局部action是否有真实病灶余量；再看action-value+完整成本能否胜强静态/risk/defer/cost/DC等。** 宽attention/ACT/MoE与泛评价创新均有先例。
9. 医学入口已存在，原两final/真实exit0后优先推进56全FOV/全部六gates/独立strict，不无限新增准备和查新目录。当前0新医学数组/权重/神经/GPUforward/训练/head/action标签，goal保持active。
