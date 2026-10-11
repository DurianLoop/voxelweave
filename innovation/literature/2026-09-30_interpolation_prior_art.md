# 2026-09-30：单 T2 层间插值、自监督和任意尺度的近邻核读

本文是一次有界 prior-art 核验，不是穷尽检索。只读取项目文档、公开论文及公开代码；未运行训练、未执行下载的作者代码、未改动旧实验结果。在线材料取回时间：2026-09-30。下文“未见”仅指所读材料，不能写成首次。

## 1. 先给结论

1. **任意层间位置 + 条件扩散已经是 HiFi-Diff（MLMI 2023）的核心，不是新的 MRI 方向。** 本地文件 `CVPR_2023_Arbitrary Reduction of MRI Inter-slice Spacing.pdf` 的会议前缀错误。
2. **高分辨率面内学习、跨平面补全、频域特征、validity mask、自监督变 gap 均已有直接近邻。** I3Net 覆盖频域与跨视图；CRIS 2026 覆盖“面内自监督 → 正交条带补全 → 两视图均值”和单模型 gap 3–7。
3. **Zero-X21 是多对比度/多平面 INR，不应按名字归为 zero-shot 单 T2 方法。** 公开仓库实际加载 T1/T2 两种 LR 与两种 HR，并以 HR L1 训练。其方法思想是近邻，但输入信息量和本项目单 T2 合同不同。
4. **MRI 正向算子 + DDNM 零空间 + 精确循环一致性已有 IPMI 2025。** PubMed 将其记录为 2026，出版社明确 IPMI 2025、2025-08-03 首发。作者当前公开 FOCVS 仓库又明确发展 native-3D、非整数层中心间距、独立厚度/间隙建模，因此“加物理约束”不能单独成创新。
5. 本项目 geometry / correspondence-only / bilateral transport 已停，不能因这些论文重新启动同类模块。若继续探索，优先做**退化模型不确定时，哪些约束真的能被独立观测证伪**的最小机制试验；下文给出具体试验，不建议马上训练大扩散网络。

## 2. 阅读深度与证据来源

| 论文/项目 | 本轮实际读取 | 可支持的结论 | 尚不能支持的结论 |
|---|---|---|---|
| I3Net | 本地 PDF 提取全文中的方法、实验、消融和讨论，重点 PDF pp.1–6、9–12 | 固定整数倍率抽层、4 层输入、DCT/MLP、cross-view、IXI 协议与消融 | 不能把原表值直接当本项目同口径结果 |
| HiFi-Diff | 本地 PDF 全文，重点 pp.3–8；Crossref + Springer 书目 | 两相邻层和相对 offset 条件扩散、混合倍率训练、HCP 合成退化 | 原文未给出的 PSF、T2-only 设定、采样独立性保证 |
| Zero-X21 | Crossref；仓库 README 所载摘要；固定 commit 下 data/model/train/decoder/encoder/test 代码 | 多对比度双输入、HR 监督、条件 INR 和特征交互 | 未取得正式 PDF，不能声称已核表格、训练集与具体退化核 |
| Cycle-Consistent Zero-Shot | Europe PMC core 完整元数据/摘要、Springer 页面、作者出版列表 | IPMI 2025、DDNM + MRI 正向算子、T1 训练先验和外部站点评估 | PMC 正文 403、EuropePMC XML 500，未读全文，不提供页码/数字结果 |
| CRIS v2 | arXiv v2 PDF 全文关键部分，pp.1–8、16–17；公开 README | 自监督条带补全、整数 gap、Gaussian blur、单模型协议、局限 | 未复现，不能确认所有实验实现完全与论文一致 |
| FOCVS / ECLARE / PRISM | 作者公开 README；FOCVS CONTEXT | 已公开机制、输入合同、作者对继承部分的说明 | 仓库说明不等于已发表论文或独立验证性能 |

缓存已归档于 [source_cache](source_cache/) 和 [extracted](extracted/)；CRIS PDF 以 `2026_CRIS_v2.pdf` 归档。I3Net 与 HiFi-Diff 文本有 `=== PDF PAGE n ===` 标记。Zero-X21 固定仓库树 SHA：`8cb9496364a88172af96489ffb99a1218ecf99c5`，代码位于 `source_cache/zerox21_code/`。README 和 API 返回保留为 `.raw` / `.json`，便于复核在线证据。

## 3. I3Net：适合作强参照，不适合再包装频域/跨视图新意

**真实贡献。** 论文将高面内分辨率的采集平面作为主体，在通道混合的 inter-slice 分支中用 PixelUnshuffle/Shuffle 扩展信息交互；intra-slice 分支先 DCT，再 LayerNorm、频域不重叠窗口与 MLP-Mixer；cross-view block 在线融合另外两视角特征（pp.3–5）。不是简单把自然图像 SR 换到 MRI，也不是光流插帧。p.3 明确指出 MRI 相邻截面会出现形状扩大、收缩、纹理变化，不能假定视频式一一运动对应。

**退化与监督。** p.3 定义输出层数 `(S−1)R+1`。pp.5–6 将原体数据当 HR，对层轴 direct downsampling，倍率 2/4/6；训练输入 4 连续稀疏层，对应 HR 深度 `(4−1)R+1`。这是抽层插值实验；不能把它当作已验证未知真实层选择 PSF 的去卷积。p.5 使用标准 L1。p.6 为 Adam、1500 epochs、batch 6、初始学习率 3e−4、cosine；对一些比较模型同时测试本论文设置与原默认设置并报最好值。

**数据合同。** 主要方法分析建立于 MSD CT（liver/colon/hepatic vessels）与 KiTS19；MRI 为 IXI Hammersmith 185 体、150 train/35 test，含 PD/T1/T2，典型 0.9375 mm 面内、1.25 mm 层间（pp.5–6）。原文没有说输入必须联合三种对比度，不要与 Zero-X21 混淆。公开数据、原始维度、归一化、全体积/缺失层计分均须与本项目重训参照对齐，不能跨表相减。

**有价值的负结果。** p.11 cross-view 数量 0/1/3/5/9 时 PSNR 为 43.72/43.85/43.90/43.86/43.83（colon ×2）；跨视图更多不单调更好。p.12 两种相邻切片/特征对比学习策略没有稳定收益，作者指出相邻层可能差异显著、远层也可能相似。这支持先证明目标信息可用，再添加上下文或一致性损失。

**本项目边界。** DCT/FFT、跨平面、通道重排、增强高频机会、邻层语义对比均不能单独作为新意。值得借鉴的是训练合同和组件对照。已修复数据的 I3Net 完整调度参照，应与新模型候选分开解释。

## 4. HiFi-Diff：2023 年已经完成任意位置条件扩散

**书目纠正。** Springer 标题一致，会议为 *Machine Learning in Medical Imaging (MLMI 2023)*，pp.23–32，DOI `10.1007/978-3-031-45673-2_3`。本地文件名的 CVPR 标记不是可靠证据。

**方法。** 给定相邻观测 `x_i, x_(i+1)` 和相对 offset `k∈[0,1]` 生成 `x_(i+k)`（PDF pp.3–5）。HiFE 是分层条件特征提取；k 经过 MLP 做 channel modulation，条件特征以空间逐元素 scaling/bias 注入 diffusion U-Net。训练为 DDPM 噪声预测，目标中间层来自 HR 监督。

**合同与结果。** HCP-1200 共 1113 体，891 train/222 test，0.7 mm 等体素，N4 与 skull stripping；沿 sagittal 法向下采样（p.6）。单模型混合 ×2/×3/×4 训练，×4/×5/×6/×7 评估；训练 T=1000、推理 DDIM 100 步，A100 40 GB、700k iterations（pp.6–7）。因此它确有训练倍率外的评价，但“任意尺度”仍是条件函数可查询的能力，不等于所有临床扫描厚度分布的稳健性。

**不能过读。** p.6 只说 downsample，并未明确完整 slice-profile 模型；不要自行补写为某特定 Gaussian/Fourier 退化，也不要无证据将 HCP 模态指定为单 T2。其 slice-wise 条件生成没有在所读方法中给出相邻生成层之间的联合随机场约束，也没有证明 data consistency 即解剖正确。p.7 承认 ×4/×5 PSNR 最高的是按倍率专训的 DeepResolve；“扩散所有指标均优于确定性方法”不成立。

**新意边界。** 两锚点 + query offset、层级 conditioning、任意位置 diffusion、只生成 missing slices 均不是空白。若新方案保持本项目四锚点合同，还必须用容量/计算匹配对照区分“更多观测”的收益。

## 5. Zero-X21：多对比度 INR，不是 zero-shot 单 T2 插值

**书目。** *Pattern Recognition Letters* 196 (2025), 236–242；DOI `10.1016/j.patrec.2025.06.001`。Crossref 与公开仓库引用一致。ScienceDirect 返回 403、arXiv 标题检索未找到，正式 PDF 未取到。

**摘要可确认。** 任意整数或分数尺度；影像特征条件 INR；重点是不同对比度、不同平面的特征不一致、交互与调制。作者声称一个训练模型处理任意倍率。

**代码可确认，但不替代原文。**

- `data.py:55–78`：由 T1 文件名替换为 T2，加载两种 LR 与两种 HR；loader 并非只从测试图像生成自监督目标。
- `train.py:242, 288–290`：L1Loss，两种预测分别对两种 HR 监督后求均值。
- `model.py:283` 起：共享 encoder 分别提两体特征；AttentionGuidedInterpolation 查询连续位置；两分支 cross-attention 与动态 MLP 权重融合后，经 MLP/SIREN decoder 预测强度。`SimFeatureSearch` 还在平面内做 top-k 特征搜索。
- 下载树未见生成 LR 的预处理脚本或数据划分说明，LR 预先从路径读取，所以当前不能确证其下采样 PSF 和论文表的实验合同。未执行代码，未验证精度/可运行性。

**对本项目意义。** 任意尺度 INR + 特征条件化 + 距离/邻域注意力 + 多模态融合已有直接方法。若以单 T2 对其做对照，应明确改造去除辅助模态，并报两种版本输入合同；不能默认把含 T1 的结果与本项目单 T2 公平比较。名字中的 Zero 不能推出 zero-shot 或无 HR 训练。

## 6. Cycle-Consistent 与作者后续：物理一致性不能证明 missing anatomy 正确

**年份。** Springer 明确 IPMI 2025、First Online 03 August 2025、pp.249–264、DOI `10.1007/978-3-031-96628-6_17`；作者出版列表亦写 2025。EuropePMC/PubMed 的记录 `pubYear=2026`，同时给出 `firstPublicationDate=2025-08-03`。引用采用会议 2025，并可注明 PubMed 2026 收录，不宜保留 README 的“IPMI 2026”。

**只依据已读摘要。** 在多个 T1-w head MRI 数据集训练 DDPM；为 2D MRI acquisition 分析并构造线性 A，在 DDNM 中作 range/null-space 分解以满足精确循环一致性；测试含训练站点留出与两个外站点。因此 zero-shot 指逆问题适配方式，并不是没有学习先验或没有 HR 数据。当前没有全文，因此不填具体样本数、采样步数、切片方向、核细节或性能数字。

**数学边界。** 对已知线性 A，`A x_hat=y` 只约束被测分量；任意 `z∈ker(A)` 满足 `A(x_hat+z)=y`。故精确一致性无法排除零空间内的错误解剖。若 A 也不准，错误的硬投影可能强制错误物理模型。它是一项必要控制，不是绝对 hallucination certificate。

**进一步公开近邻（证据等级为仓库说明）。**

- **FOCVS**：作者称为 IPMI 2025 的 native-3D successor。README 和 CONTEXT 明确继承正向 A、DDNM 与 range/null-space 理论；区分厚度 τ、gap γ、中心间距 s=τ+γ，可非整数；separable 3D operator。不能将“厚度间距解耦 + 3D diffusion + 硬一致性”简单视为新机制。其 README 没有提供足够论文实验结果，不能当已验证 SOTA。
- **ECLARE**：作者 README 表明可从单图自学习，支持显式 relative slice thickness 或自定义 profile，slice separation 从头信息读取；说明厚度与间距分开建模、自监督 SR 已有成熟近邻。CRIS 也引用该方法并比较。
- **PRISM**：作者公开 README 称 MICCAI 2026 待刊，通过 HR reference 与 LR 的轴向功率谱匹配网格搜索 Gaussian PSF。它需要 HR reference，合同不同于本项目单 T2；“频谱估 slice thickness”本身已有。

## 7. CRIS v2：最新且最直接的自监督对照

**版本。** arXiv `2606.15967v2`，PDF 标 2026-07-08；题名 *CRIS: Cross-Plane Self-Supervised Isotropic Restoration for Anisotropic Volumetric Imaging Across Modalities*。预印本身份保持，不把 arXiv 记作已接收会议。

**核心过程（pp.4–6）。** 从原采集平面的 high-resolution in-plane slice 构造目标；MRI 沿面内一轴施加 1D Gaussian blur，再按周期 g 留行/列，其他位置设空白，并提供 binary validity mask。用两个通道输入的 Swin-UNet 类模型学习条带恢复。推理先沿真实稀疏轴插 `(g−1)` 个空白层，再恢复两个正交 reformat，回到统一坐标后 voxelwise mean。这里两视图来自同一体数据，不是额外扫描；其所谓 cross-plane consistency 主要由融合实现，不是严格真实解剖保证。

**任意尺度的实际边界（p.4、p.7）。** `g=round(r_th/r_in)` 是整数。非整数比例先按最近整数插空白，恢复后再 resample 到请求网格。单模型 robustness 实验训练 `g∈{3,4,5,6,7}`，测试同范围与 coronal/axial/sagittal 三种合成退化；不是 continuous-coordinate 解码，也不是未见 g 的外推证明。大部分脑 MRI 主实验仍固定 g=5。

**数据与退化（p.7）。** 公共脑 MRI 共 63 体，48/7/8 train/val/test；近等体素 1 mm 或 1×1.25×1，后者先插值到 1 mm 定义参考。主实验 Gaussian σ=5/3 + 每五层保留一层。真实腹部 115 FIESTA 体、70/15/15%，train/val 可用本来就有的轴位/冠状位扫描，但 test 重建只用冠状位输入，另一扫描仅作无参考比较；没有真实 isotropic GT。它并不证明 fastMRI 单 T2 缺失层增益。

**损失（pp.5–7）。** L2 + SSIM + Sobel + FFL；MRI 权重 10/5/5/10，按 epoch 逐步加入；vEM 关掉 Sobel/FFL。复用这些损失或“高频保真”不是新意。

**论文自己说明的局限（p.17）。** 脑实验主要是 synthetic anisotropy；腹部没有 isotropic reference；均值融合在两个视角置信度不同时可能欠佳；未来明确建议 adaptive/uncertainty-weighted fusion。所以只把均值换成 uncertainty weight 也很难支撑强创新。跨平面两结果可能共享同一缺失信息和共同偏差，分歧低不等于误差低。

## 8. 最值得验证的一项机制：由留出真实观测约束的退化歧义控制

这是一项**需要验证并继续查新**的机制假设，不是已经成立的首创，也不是下一条 full 指令。

**问题。** 固定 profile 的硬一致性与单 profile 自监督都把退化设定当正确；同一中心间距可对应不同厚度/间隙，多个 A 可能解释相同观测。单一 A 下的样本方差或跨视图分歧会遗漏这种共同偏差。新增模块前，应先证明本项目存在可被观测验证的 profile-sensitive 残差。

**候选机制。** 对合理的有限 profile 集合 `{A_φ}`，只用观测层分两组：用一组条件化恢复；让另一组真实观测作为 held-out forward prediction 校验，从而为 profile 保留/加权；在缺失位置同时输出 profile 内生成变异和 profile 间重建变异。最终对歧义大的区域限制新增高频幅度或退回已登记的确定性基线。新贡献若能成立，应在“留出观测能否识别错设的 A，并避免共享偏差误判”上，而不是 profile 混合、uncertainty 或 gate 名字上。

**为什么比再叠 correspondence 值得先测。** 本地 `pastnet_v2/README.md` 记录 geometry +0.002126 dB、correspondence-only +0.002471 dB，均未达晋级门槛；`pastnet_residual_audit/README.md` 记录远端观测相对增量 +0.000552 dB 且 MAE guard 失败；`pastnet_bilateral_transport/README.md` 容量筛选未过。当前更缺的是能预测失败来源的可检验证据，而不是更多邻域特征。

**最小可证伪试验。**

1. 先锁定任务合同：当前若仍是直接抽层，令 `A=P`，不得把已有 thick-slice target 当未知 isotropic 真值。真实 acquisition-profile 分支另列实验，不能混入原基准抬分。
2. 在 training-only 病例上生成可控 blur × separation 的小型二维因素矩阵：相同 separation、不同 blur；相同 blur、不同 separation。若 profile 都无法区分，结果就是不可辨识，不得让网络虚构识别能力。
3. 留出的观测不进入条件输入、归一化极值、profile 拟合或 gate 训练。与原全部锚点合同不同的额外稀疏化必须明示，且对照方法收到相同锚点。
4. 对照 fixed-profile、最佳训练集固定 profile、profile ensemble、观测留出加权；全部共享同一冻结恢复器，先测 held-out prediction error 是否能预测 missing-slice 的真实风险、是否比普通跨视图/seed 方差更有效。
5. 同时评估缺失层 PSNR/MAE、风险覆盖曲线及低分歧高误差病例。若只降 data-consistency residual、不降真实 missing-slice 风险，机制失败。若没有 beyond ensemble 的收益，停止而不叠 gate 或扩散网络。

**重要边界。** 这个检查也不能证明最终细节是真实，只能校验部分泛化与退化错设。若本项目当前专注同分布抽层且 profile 影响不存在，应停在这一步，回到完成严格 baseline 和论文机制证据，不把问题强行改成新数据任务。正式声称新意前还须完整阅读 ECLARE、PRISM 和 FOCVS 对 misspecified profile 的公开论文/实验。

## 9. 已验证链接

- I3Net 作者代码（本地 PDF p.1 给出）：https://github.com/DeepMed-Lab-ECNU/Medical-Image-Reconstruction
- HiFi-Diff 出版社：https://link.springer.com/chapter/10.1007/978-3-031-45673-2_3
- HiFi-Diff Crossref：https://api.crossref.org/works?query.title=Arbitrary%20Reduction%20of%20MRI%20Inter-slice%20Spacing&rows=1
- Zero-X21 DOI：https://doi.org/10.1016/j.patrec.2025.06.001
- Zero-X21 仓库：https://github.com/momo123875/Zero-X21
- Zero-X21 固定树：https://api.github.com/repos/momo123875/Zero-X21/git/trees/8cb9496364a88172af96489ffb99a1218ecf99c5?recursive=1
- Cycle-Consistent 出版社：https://link.springer.com/chapter/10.1007/978-3-031-96628-6_17
- Cycle-Consistent EuropePMC core：https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:41552688&format=json&resultType=core
- 作者出版列表：https://sremedios.github.io/publications/
- FOCVS：https://github.com/sremedios/FOCVS
- FOCVS CONTEXT：https://raw.githubusercontent.com/sremedios/FOCVS/main/CONTEXT.md
- ECLARE：https://github.com/sremedios/ECLARE
- PRISM：https://github.com/sremedios/PRISM
- CRIS v2：https://arxiv.org/abs/2606.15967v2
- CRIS v2 PDF：https://arxiv.org/pdf/2606.15967v2
- CRIS 作者代码：https://github.com/adi-hatav/CRIS

访问失败记录：ScienceDirect Zero-X21 页面 403；PubMed 页面返回 cookie interstitial；PMC 403；EuropePMC fullTextXML 500；Springer PDF 路径重定向到订阅预览。上述失败没有被表述为全文阅读。
