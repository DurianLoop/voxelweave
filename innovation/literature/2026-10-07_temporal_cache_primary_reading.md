# Skip-Convolutions 与 MotionDeltaCNN：原文阅读及 MRI 候选修订

本轮新增核读2篇 CVF 正式会议原文。取得20物理页，实际完整文本阅读 Skip-Convolutions 页1–8、MotionDeltaCNN 页1–9，共17页；后者第9页包含限制/结论及部分参考文献。未读 Skip 页9–10、Motion 页10参考文献，未取得/阅读补充材料、未复现作者代码。4页实际渲染并视觉核看：Skip4/7、Motion5/8。下载、正文提取和关键页核看分开登记，不重复计已有 DeltaCNN、SIGE、DeepCache。

| 原文身份 | 直接核读位置 | 对项目的影响 |
|---|---|---|
| Habibian, Abati, Cohen, Ehteshami Bejnordi, *Skip-Convolutions for Efficient Video Processing*, CVPR2021, pp.2695–2704 | PDF3–4 Eq2/3/8/9；7 Table2；8 Table3/4及限制 | 残差门控、task+cost联合训练、结构化块、参考刷新已知；MAC与实测时间不同 |
| Parger et al., *MotionDeltaCNN: Sparse CNN Inference of Frame Differences in Moving Camera Videos with Spherical Buffers and Padded Convolutions*, ICCV2023, pp.17292–17301 | PDF4–5 reset/padding；6 evaluation；8 Tables1–3及Receptive Field；9 limitations | 动态ROI、缓存边界、状态重置已有先例；ROI信息来源、部分计时、保留旧上下文需明确 |

## Skip-Convolutions：任务门控的直接先例

卷积线性更新 Eq2 与有门控的 Eq3 不同：Eq3明确用波浪号标出近似，跳过了非零但判定不重要的残差。第一帧完整计算。Gumbel gate由每层单输出卷积、Bernoulli采样和straight-through训练构成，最小化 `L_task + beta L_gate`；Eq9从t=2起统计平均MAC，分母T−1，**不包含第一帧冷启动**。不能把“按任务重要性挑计算”“联合任务/预算训练”单独作为创新。

页4给出maxpool+nearest upsample使gate成块；页8 Table3不同block配置的训练结果不完全单调，不能从此推导我们越粗分块越省且无任务损失。页5 detection训练clip4，页6 pose训练/推断clip8；页8 Table4显示参考刷新频率影响准确率：Ttrain4、Ttest∞为PCK89.3 vs Ttest4为95.3，Ttrain8的相应94.2 vs94.5。长期复用不具备无条件任务保持。

页7 Table2测的是HRNet卷积/Skip-Conv层的CPU耗时（Xeon E5-1620 3.50GHz），不等于整个应用的端到端耗时。例：10.19→2.35 GMAC约4.34倍，548→287ms仅约1.91倍；其表内MAC比为4.33。作者未在此表给MRI/GPU实测。页6“reduces MAC by330%–350%”及页5“300% reduction”的文字不能按标准减幅理解；22.06→6.36 GMAC实际为3.47倍或约71.2%下降。

页6 pose按GT bounding box裁剪且PCK尺度也用box，不能称完整GT-free定位验证。页8承认强相机运动未明，warping留未来。本项目同一MRI网格的替代候选没有该相机问题，但动态InstanceNorm3d并未得到这里的有限局部更新证明；已有受影响完整patch重算仍是执行对照。

## MotionDeltaCNN：支持边界与计时范围

页4–5 homography对齐、ring buffer偏移、动态添加bias及padded convolution解决新区域接入。卷积对边界的旧影响要保留；只拼裁剪输出会丢邻居贡献（Figure5）。回到被覆盖的受限区域会全buffer reset再dense推断。页7记990帧9次reset，页8 Table3的moving子集为8次；二者集合不同，不制造矛盾。动态init移除变110次reset、IoU79.63 vs79.43，不能只报告速度。

页6 DAVIS仅选简单homography可可靠工作的14段，失败的视频未纳入；视频分割有首帧GT mask，ROI随后用上一帧预测。Human3.6M直接用标注bounding boxes并省略human detection。这样的ROI来源不能冒充当前MRI仅observed强度的部署定位，本轮冻结QDA/LDA也不能借用其覆盖能力。

页6计时：BMVOS仅DenseNet feature encoder；HRNet仅model inference，后处理和评价排除。没有在这些FPS中确认完整视频稳定化/数据流程费用。因此不能把表格速度搬成MRI总节省。

页8 Table1的All/RTX3090/b1：DeltaCNN sparse70.0FPS、Motion65.2FPS，后者约0.931倍，虽然GFLOPs15.5→6.8更少；b12则125→215FPS约1.72倍。moving/b12为106→201FPS约1.896倍，说明摘要“up to90%”是特定配置。页7明确说明低batch和未充分利用GPU时跳tile不一定省时间。

页8 Table2最大11.1倍对应† buffer/crop288²、GT框及b28（dense行b16），不能作为相同batch/完整FOV的单因素稀疏收益。普通1080Ti/b16 Motion228与cuDNN cropped71约3.21倍，可作作者表格内更接近范围的算术；仍不是MRI复现。

页8 Receptive Field 明确说**即使dense mode也与标准CNN不完全一致**：保留当前视野外的历史context，会改变当前预测。这里的连续序列状态不同于我们每个MRI替代候选都相对于固定PCHIP原输入；比较多个候选时必须声明是否累计编辑、按实际状态转换重新验证，不能沿用旧baseline的成本/收益。

页9限制：依赖可靠稳定化，blur/parallax可能失败；旋转/zoom超过buffer会crop或增memory。作者认为diffusion denoising因低空间差分稀疏与噪声敏感未必适合。不能宣称该系统已为MRI扩散恢复提供同等加速。

## 创新点更新

保留的主研究问题是：充分适配基线之后，observed-only信息能否预测**完整患者任务的净修正收益**，用真实窗口union/候选探索/初始化费用约束选择，超过相同总成本下的强对照，并在冻结确认患者复现。这是待验证候选；task-aware gating、成本预算、ROI与缓存已被这些原文及已有SACT/DynConv/SBNet/LTT/Pareto占位。

新真实输入探针只核PCHIP→ROI内linear的浮点差分：所有64候选的实际k等于几何k；这有助后续实现准备，未建立输出等价、局部生成速度或MRI效益。旧ROI覆盖失败仍是定位问题，不能由计算可复用性解除。后续优先取得能工作的observed任务模型/ROI，再冻结动作与完整费用；此时才值得投入收益头/控制器训练。若无剩余收益，保留负结果，缩小任务/退化范围。

## 来源与范围登记

- [Skip-Convolutions 官方landing](https://openaccess.thecvf.com/content/CVPR2021/html/Habibian_Skip-Convolutions_for_Efficient_Video_Processing_CVPR_2021_paper.html)，[本地PDF](source_cache/temporal_cache_primary_2026-10-07/skipconvs.pdf)。
- [MotionDeltaCNN 官方landing](https://openaccess.thecvf.com/content/ICCV2023/html/Parger_MotionDeltaCNN_Sparse_CNN_Inference_of_Frame_Differences_in_Moving_Camera_ICCV_2023_paper.html)，[本地PDF](source_cache/temporal_cache_primary_2026-10-07/motiondelta.pdf)。
- [取得记录](source_cache/temporal_cache_primary_2026-10-07/acquisition_attempt01.json)及[关键页渲染记录](source_cache/temporal_cache_primary_2026-10-07/render_attempt01.json)保留真实工具exit与当时visually_reviewed=false；随后实际view_image另记[阅读provenance](temporal_cache_reading_provenance_2026-10-07.json)。
