# Slice profile / 厚度与间距解耦：先验研究核查（2026-09-30）

结论：**“把层厚与采样间距分开，并用 slice profile 建模 MRI 退化”不能作为本项目的新颖性主张。** SMORE 的 2023 后续论文已明确这么做，SPTSR 2023 也在观测方程中分别定义 PSF、厚度和间距。ESPRESO 2023 已从单个输入体积无外部训练数据地估计 slice profile。官方 SMORE 软件的更新记录还把用户提供 profile、gap/overlap 支持追溯到 2021。

尚未在本次阅读的论文和公开主入口中找到“同一模型把输入 profile、输入中心位置、输出 profile、输出中心位置全部作为独立请求，覆盖保持原层厚的插层和改变层厚的重建”的明确实现。但这是**有限检索下的待查证假设，不是已经确认的创新空白**。尤其“任意输出 profile”可由高分辨率重建后再卷积得到，单独增加这个接口并不足以构成方法贡献。

## 1. 已核实来源与阅读深度

本次未启动训练，未改旧模型或旧实验结论。原文以公开全文 XML / BioC 文本读取；没有把图中数值或未读全文的摘要扩写为实验细节。浏览日期统一为 2026-09-30。

| 文献 / 代码 | 年份与身份 | 本次实际阅读深度 | 可直接支撑的结论 |
|---|---|---|---|
| Zhao et al., *SMORE: A Self-Supervised Anti-Aliasing and Super-Resolution Algorithm for MRI Using Deep Learning* | TMI 40(3):805–817, 2021；DOI 在线年份为 2020 | 原文 BioC：引言、2D/3D退化与训练方法、讨论中限制；另读作者页面 | 2D MRI 的 profile 与采样是不同物理过程；原版用 Gaussian profile；公式可写 separation/thickness 比率，但文中所有数据比率为1，作者明确未实验不等厚度的spacing |
| Remedios et al., *Self-Supervised Super-Resolution for Anisotropic MR Images with and Without Slice Gap* | SASHIMI / MICCAI 2023, pp.118–128 | 原文 BioC：Introduction、Methods、Training、Inference、Experiments、Results、Conclusions及图注；未视觉读取曲线数值 | **已经明确独立建模厚度和间距**；ESPRESO估计PSF；8种厚度/间隙组合；输出匹配in-plane的isotropic体积 |
| Han et al., *ESPRESO: An algorithm to estimate the slice profile of a single magnetic resonance image* | Magnetic Resonance Imaging 98:1–9, 2023 | PubMed/Europe PMC正式摘要、IACL作者发表列表、作者GitHub README；**未取得论文全文** | 从单个输入体积估计PSF，无外部训练数据；GAN式分布匹配；将估计profile用于SR训练数据生成 |
| Lin et al., *High-Resolution 3D MRI With Deep Generative Networks via Novel Slice-Profile Transformation Super-Resolution* (SPTSR) | IEEE Access 11:95022–95036, 2023 | 原文XML：Introduction、Related Works、III-A观测方程(1)–(5)、训练/推理说明、profile消融、局限与图注 | 厚度L为PSF的FWHM，DS为spacing；明确无gap时二者才相同；SP-downsampling、SP-conv、SP-deconv处理训练/推理物理匹配 |
| 官方 SMORE GitLab README、CHANGELOG、`smore/main.py` | 当前主分支；README指向v4.0.5安装 | 逐文档/入口代码读取；**未运行、未复现，也未审计全部模块** | 2021的软件版本已支持独立spacing/thickness/custom kernel；2023 v4支持SLR profile；公开主入口没有独立target-profile参数 |

原文和作者来源：

- SMORE 2021 DOI：<https://doi.org/10.1109/TMI.2020.3037187>
- SMORE 2021全文：<https://pmc.ncbi.nlm.nih.gov/articles/PMC8053388/>；实际成功读取的全文接口：<https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC8053388/unicode>
- SMORE作者主页：<https://iacl.ece.jhu.edu/index.php?title=ISMORE>
- Remedios 2023 DOI：<https://doi.org/10.1007/978-3-031-44689-4_12>
- Remedios 2023全文：<https://pmc.ncbi.nlm.nih.gov/articles/PMC11613142/>；实际成功读取接口：<https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC11613142/unicode>
- ESPRESO DOI：<https://doi.org/10.1016/j.mri.2023.01.012>；正式摘要：<https://pubmed.ncbi.nlm.nih.gov/36702167/>；作者代码：<https://github.com/shuohan/espreso>
- IACL发表列表：<https://iacl.ece.jhu.edu/index.php?title=Publications>
- SPTSR DOI：<https://doi.org/10.1109/ACCESS.2023.3307577>；全文：<https://pmc.ncbi.nlm.nih.gov/articles/PMC10501177/>；实际成功读取XML：<https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10501177/fullTextXML>
- 官方SMORE：<https://gitlab.com/iacl/smore>；README：<https://gitlab.com/iacl/smore/-/raw/main/README.md>；CHANGELOG：<https://gitlab.com/iacl/smore/-/raw/main/CHANGELOG.md>；主入口：<https://gitlab.com/iacl/smore/-/raw/main/smore/main.py>

部分PMC网页返回403，而官方BioC / Europe PMC全文接口可访问。这里只把成功获取的原文当作全文证据。

## 2. 四个概念必须区分

用简化的一维through-plane模型表示：

`y_i(x,y) = integral k_in(z - z_i) f(x,y,z) dz + noise_i`

`target_q(x,y) = integral k_out(z - z_q) f(x,y,z) dz`

- `k_in`：输入层的slice response/profile；名义层厚通常以其FWHM概括，不能由一个厚度数值确定完整核形状。
- `z_i`：采集中心位置；相邻中心差是spacing，可不均匀。spacing不是profile宽度。
- `k_out`：希望输出的层响应；“输出网格很密”不等于“输出有效层厚变薄”。
- `z_q`：输出中心位置；整数/非整数上采样率只描述网格关系，不完整描述MRI成像退化。

上述方程是整理既有观测模型的记号，不作为本项目新方法。真实MRI还涉及序列、激励/重聚焦脉冲、运动和噪声；本次不假设DICOM的SliceThickness足以提供真实profile。

本项目现行x4数据主要是从原生体积抽取每4层作为输入、其余原生层作为监督。对规则同序列体积，可理解为输入和目标沿用同一个原生层响应 `k_in ≈ k_out = k_native`，只是中心采样变稀；**并没有仅因为抽层就额外把输入层厚变成原来的4倍**。反之，临床厚层到真正薄层的SR通常要求 `k_in != k_out`。这两个目标不能用同一个“x4”标签混写。

本地依据：`design/pastnet_ixi_wavelet/PROTOCOL_ZH.md:13` 固定z=0,4,…观测网格；`:15`规定真实锚点与目标监督；`design/pastnet_v2/docs/01_证据与信息审计.md:71`起记录三域真实spacing。fastMRI x4间隔中位20mm、IXI5mm、NingXia17.6mm，这些是间距统计，不是实测profile。

## 3. 逐篇对新意的约束

### 3.1 SMORE 2021：不能将profile观测建模视为2026年的新想法

原文2D数据准备先做Gaussian profile卷积，再按spacing下采样，随后B-spline上采样制造相应aliasing。profile FWHM使用r，spacing使用`rs*r`。文中说明所有实验数据`rs=1`；讨论明确“did not experiment ... slice separation different from slice thickness”。因此准确说法是：**原文具有区分两者的模型表达，但没有验证一般gap情形**。不能把它概括为完全不理解层厚和spacing，也不能把其无gap验证外推为所有临床gap已经解决。

该文还明确区分2D切片选择造成的through-plane aliasing，与k-space欠采样；不是把普通图像缩放直接称作MRI物理模型。

### 3.2 Remedios 2023：直接覆盖“厚度/间距解耦”主张

Introduction中的原文短句：

> “model slice thickness independently of slice separation”

Methods分别定义厚度T、间隙G，中心间距`s=T+G`，且s可以非整数。Forward process先由ESPRESO估计PSF，对in-plane patch卷积，再以cubic B-spline按spacing重采样；Reverse process用WDSR、残差预测与pixel shuffle。非整数spacing先B-spline调整到适当整数放大关系。

验证包含8种T/G组合：3/0、3/1、4/0、4/1、4/1.2、5/0、5/1、5/1.5 mm。模拟采用Shinnar–Le Roux脉冲设计产生profile，厚度T和spacing T+G分别设置。数据为50名OASIS-3 T1和30名3D-MR-MS FLAIR；除PSNR/SSIM还检查脑区与MS病灶分割。分割参照是HR图像上的自动分割，不能写成所有都是人工解剖金标准。

**对本项目的限制：**“使用ESPRESO + profile卷积 + spacing抽样 + residual/WDSR”明显是既有路线。该论文输出为匹配in-plane的isotropic重建；本次阅读未发现用户任意请求target profile的功能。不过未发现不等于全领域不存在。

### 3.3 ESPRESO 2023：盲核估计和不依赖外部HR训练也已存在

正式摘要明确以单个2D multi-slice体积估计through-plane PSF。假设在正确profile校正下，不同方向的解剖patch具有相同分布；generator估计核并退化in-plane，discriminator判断方向数据是生成的还是实际低分辨率。估计核再用于当时的内部监督SR算法。

因此“从观测自适应估计未知slice profile”“无需成对HR-LR外部数据”均不能直接做首创主张。其各向同性统计假设对病灶、强方向结构、仅4个真实观测等情形的适用程度，仍是本项目需要实际测量的风险；本次未读其全文，不能声称已知所有实验边界或其在本数据上必然失败。

### 3.4 SPTSR 2023：已有明确观测方程和输出去卷积

III-A Eq.(1)(2)把真实体积V与PSF卷积，再按DS位置取样；文字说明L为PSF的FWHM、DS为spacing，只有无gap时DS=L。该文实际例子包括3mm层厚与3.6mm间距，不能将二者绑定。

SP-downsampling制造训练退化；推理前SP-conv匹配两个方向的profile；输出先具有相应卷积特性，再通过Richardson–Lucy SP-deconv得到isotropic SR。论文还比较truncated sinc与Gaussian profile组合。因此“让训练与推理的slice profile相匹配”和“关注输出profile而非仅增加网格密度”也已有明确先例。

该文为T2 TSE前列腺等场景，训练/推理设置与本项目四真实锚点的监督插层不同；其结果不能直接作为本项目排名。已读方法目标是isotropic输出，本次未见任意target-profile请求实验。

### 3.5 SMORE2 / v2命名核查

不要把“SMORE2”写成一个已核验的新论文标题。作者当前项目名是SMORE，官方CHANGELOG区分软件版本：

- v2.1.1（2021-05-12）：支持iSMORE迭代；2.1.x支持用户提供slice selection profile kernel，并明确可补偿slice gap/overlap，常由ESPRESO估计。
- v3.1.0（2021-06-08）：能指定slice spacing、slice thickness和blur kernel；支持custom blur kernel。
- v4.0.0（2023-04-19）：WDSR、无须预训练、默认物理SLR profile、支持有理数slice separation。

这些是**官方软件更新记录的日期与功能陈述**，不是每项方法已在同日完成同行评审的证明。当前README将代码关联到Remedios 2023；主入口参数有`--slice-thickness`和`--blur-kernel-fpath`，没有独立`target-profile`参数。README称`--blur-kernel-file`而主入口为`--blur-kernel-fpath`，复现时应以锁定版本实际参数为准。本次未运行工具。

## 4. 对本项目建议保留的窄问题

最有价值的切入点是**目标语义与证据合同是否一致**：训练标签是保持原生层响应的缺失层，还是未知连续体积的薄层投影？让这两类任务可控地比较，可以避免只在合成抽层基准中提高PSNR，却误宣称恢复了临床真正薄层信息。

可研究的候选假设是：在输入profile与中心位置固定时，直接预测指定`k_out,z_q`的目标，比“先重建一个高分辨率潜在体积，再重卷积到同一目标profile”更准确、稳健或省计算。也可以研究profile估计误差如何影响不同输出厚度，以及模型何时应保留原响应、不做去卷积。**这些假设尚未证明新颖或有效。** 只有联合算子带来不可由简单预处理/后处理替代的收益，才能上升为方法贡献。

不能把单独增加厚度token、kernel embedding或FiLM作为核心创新：本项目geometry FiLM已只提升+.002126dB；已有文献也早已把profile用于退化。更合适的验证包括：

1. **保持原生profile的插层对照**：`k_out=k_in`，只改变中心网格；与现有PAST、I3Net在同合同评分。
2. **厚度与spacing的交叉组合**：用具有可信薄层参考的train/validation体积，分别改变输入厚度、gap、profile形状；保留未见组合，避免仅学习固定倍率。
3. **独立输出profile的反事实**：同一输入请求多个`k_out`，分别评分；基线必须包括同一重建结果后卷积/积分，不能只对比不支持参数输入的旧模型。
4. **profile估计误差对照**：真实/合成已知核、ESPRESO估计核、固定Gaussian或SLR核；把核估计错误与插层网络错误区分。
5. **真正目标支持**：现有原生厚层标签只支持恢复同原生响应的切片，不能把重采样/去卷积结果自动当真正薄层GT。若无可信薄层参考，厚到薄结论应限于有明确观测模型的模拟实验。

这些是下一步实验设计的建议，不构成启动训练授权。先完成prior-art边界与数据可行性判断，再决定是否值得实现。

## 5. 可用于后续汇总的措辞

可以写：

> 我们将检验：在现有抽层插值与真实厚层重建之间，显式规定目标层响应是否能减少训练目标混淆；并测试一个共同模型对独立输入profile、采样中心与输出profile请求的泛化。层厚/间距分离和slice-profile估计均采用既有成像知识，不作为新颖性来源。

目前不能写：

- “首次将层厚与层间距分离用于MRI超分/插值。”
- “首次使用PSF、slice profile或SLR进行物理退化。”
- “首次从单个MRI自监督估计slice profile。”
- “加目标厚度条件即可证明临床薄层恢复。”
- “SMORE没有考虑gap / profile”，或把2021原版限制当成2023后续方法限制。

本次已足以否决上述宽泛创新包装；尚不足以确认目标profile条件化是独占空白。2026最新方法仍需由本轮其他阅读记录补充，尤其明确采用slice profile kernel或厚度重采样的工作。
