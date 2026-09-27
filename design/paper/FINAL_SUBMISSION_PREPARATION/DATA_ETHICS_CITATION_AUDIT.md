# 数据、伦理与引文审计

核查日期：2026-09-12。PASS 只适用于该行明确限定的事实，不表示数据使用权或整个项目通过伦理审查。来源网页、正式论文/作者论文与本地转换、注册表分别核查；没有借用其他项目的伦理编号。下列未解决事项需要真实作者材料，技术编辑不替代它们。

## 数据与许可

| 对象 | 状态 | 已核查事实、修改与剩余事项 |
|---|---|---|
| fastMRI 原引文 | FIXED | Knoll 2020 标题确实是 knee dataset，但 [NYU 官方门户](https://fastmri.med.nyu.edu/)仍明确要求该文引用。保留 initiative 归属引用，并增补 brain 论文与门户，避免只用膝关节论文证明脑部样本身份。摘要加入 NYU fastMRI 归属。 |
| fastMRI brain 方法文献 | FIXED | 新增 Muckley et al., Results of the 2020 fastMRI Challenge，TMI 40(9):2306–2317, DOI 10.1109/TMI.2021.3075856。[作者论文](https://arxiv.org/abs/2012.06318)、[作者机构记录](https://pure.amsterdamumc.nl/en/publications/results-of-the-2020-fastmri-challenge-for-machine-learning-mr-ima/)。该文支持脑部资源背景，不证明本地24例就是官方challenge test。 |
| fastMRI 本地精确 release | NEEDS HUMAN CONFIRMATION | 本地 `dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_nifti_manifest.csv` 与 `design/pastnet_v2/prepare.py::recover_fastmri` 绑定原DICOM与转换。既有24例物理位置/像素审计通过，但没有检索到下载凭证、正式release/accession与官方下载文件的完整对应。正文改为 locally catalogued，补充材料明确不能认证官方split。作者应提供原下载/授权记录及release映射。 |
| fastMRI 使用/图像刊登 | NEEDS HUMAN CONFIRMATION | 官方门户说明受数据协议约束，图像刊登许可须核实。本轮未发现签署记录或针对图1图像的许可；没有声称已取得。门户的来源机构去标识说明不能自动认证本地副本。[官方来源与政策](https://fastmri.med.nyu.edu/)。 |
| IXI 来源与许可 | FIXED | [官方 IXI 页面](https://brain-development.org/ixi-dataset/)列出T2 NIfTI与三个伦敦采集点，明确CC BY-SA 3.0。归属Imperial College Biomedical Image Analysis Group；去除无依据的2014出版年份，更新访问日期。未误用二次预处理仓库的4.0许可。 |
| IXI 本地划分 | PASS | 本地404/58/115 ID划分与源集合区分；既有ID互斥审计保留，不称独立于项目开发的未触碰验证。公开数据许可不等于本地机构批准已被证明。 |
| NingXia provenance | NEEDS HUMAN CONFIRMATION | 本地有原始/处理资料和八患者、22series实验键；真实提供机构、采集来源证明、数据保管责任人不完整。补充材料明确暂只能称本地 knee T2 collection。 |
| NingXia 去标识 | NEEDS HUMAN CONFIRMATION | 原始目录命名含直接身份线索，不能认证整体已脱敏。没有把这些内容转写到本文或报告；需要作者提交抽取流程、DICOM元数据及像素去标识验证。患者分组不是去标识证明。 |
| NingXia IRB/豁免 | NEEDS HUMAN CONFIRMATION | 未发现可核实的审批机构、决定号、日期、覆盖的研究范围或合法豁免。补充材料新增明确待作者填写的声明。没有捏造编号。 |
| NingXia 同意/允许用途 | NEEDS HUMAN CONFIRMATION | 知情同意或豁免、研究/发表许可、数据使用协议均需真实资料；不能从同队列旧论文、OAI子目录或其他项目借用。 |
| TopCoW | PASS | 只描述125个本地可用已标注public-challenge training cases，保留探索史，不称隐藏测试集。[正式研究 DOI](https://doi.org/10.1056/AIdbp2500994)与既有本地来源审计对应；现行文献已到2026正式版，不能因年份新就误删。 |
| CAS2023 | PASS | 只描述100个公开训练image/label pairs。[组织者学校公告](https://hsee.sztu.edu.cn/info/1109/3103.htm)和[SMRA原公告](https://society4mra.org/index.php/2023/06/14/cerebral-artery-segmentation-challenge-cas2023/)支持挑战归属；后者直接打开曾404，搜索索引仍可见，故不能将页面可访问性误写为数据权利确认。 |
| 外部MRA release/允许用途 | NEEDS HUMAN CONFIRMATION | 本地hash/配对/affine审计不认证原始download agreement；作者应核实TopCoW/CAS具体release及使用/再分发条件。本轮未新增外部分析或打包原数据。 |

## 主要重建方法与实现措辞

| 引文 | 状态 | 具体支持及修订 |
|---|---|---|
| HAT | FIXED | 补正式[CVPR 2023](https://openaccess.thecvf.com/content/CVPR2023/html/Chen_Activating_More_Pixels_in_Image_Super-Resolution_Transformer_CVPR_2023_paper.html)，22367–22377。原始方法是图像超分，本文使用本地MRI训练/输入封装，不宣称官方MRI权重。 |
| SwinIR | FIXED | 补[ICCV Workshops 2021](https://openaccess.thecvf.com/content/ICCV2021W/AIM/html/Liang_SwinIR_Image_Restoration_Using_Swin_Transformer_ICCVW_2021_paper.html)，1833–1844；明确本地实现与训练条件。 |
| I3Net | PASS | [作者论文](https://arxiv.org/abs/2405.02857)支持inter/intra-slice结构与医学切片插值任务，DOI 10.1109/TMI.2024.3394033一致。正文增加locally configured，既有模型注册表绑定实际checkpoint，输出复现不等于官方性能复现。 |
| SAINT | PASS | [CVPR 2020](https://openaccess.thecvf.com/content_CVPR_2020/html/Peng_SAINT_Spatially_Aware_Interpolation_NeTwork_for_Medical_Slice_Synthesis_CVPR_2020_paper.html)，7750–7759；原文主体实验为CT。本文始终称adapted SAINT-style，单独记录物理z坐标修正与legacy预测，不能把这个MRI变体说成原文精确复现。 |
| CycleINR | PASS | [CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Fang_CycleINR_Cycle_Implicit_Neural_Representation_for_Arbitrary-Scale_Volumetric_Super-Resolution_of_CVPR_2024_paper.html)，11631–11641。本文internal CycleINR-style，只借方法谱系，不声称官方训练/体积拟合流程完全一致。 |

## 每一条新增 diversity/uncertainty 引文的句子支持

| 引文 | 状态 | 本文句子可以支持什么；不能借它主张什么 |
|---|---|---|
| Krogh–Vedelsby 1994 | PASS | [NIPS官方论文](https://papers.nips.cc/paper_files/paper/1994/hash/b8c37e33defde51cf91e1e03e51657da-Abstract.html)建立ambiguity/ensemble-generalization关系。本文明确恒等式与diversity思想非新。1994为会议年，1995书籍出版标年不构成两篇研究。 |
| Liu–Yao 1999 | PASS | [期刊原文](https://www.sciencedirect.com/science/article/pii/S0893608099000738)支持通过correlation penalty协同训练ensemble；不是物理MRI输入身份实验，不能据此声称本文首次研究相关误差。直接抓取403由可见原站搜索摘要与原论文版本交叉检查补足。 |
| Kuncheva–Whitaker 2003 | PASS | [期刊摘要/正文记录](https://link.springer.com/article/10.1023/A:1022859003006)研究多种diversity指标与accuracy，且明确关系不普遍简单。本文不把它引用成diversity必然带来可靠性。 |
| Ho 1998 | PASS | [原始TPAMI论文副本](https://pdfs.semanticscholar.org/b41d/0fa5fdaadd47fc882d3db04277d03fb21832.pdf)用随机特征子空间形成不同树；支持输入多样性早已有之，不等于MRI物理身份控制。 |
| Kariyappa–Qureshi 2019 | PASS | [作者论文](https://arxiv.org/abs/1901.09981)讨论loss-gradient错齐与transfer attack，支持敏感度多样性先例。保留arXiv preprint身份，不写成已证实的MRI不确定性校准。 |
| Wang et al. 2019 | PASS | [作者论文](https://arxiv.org/abs/1807.07356)针对医学分割TTA aleatoric uncertainty。本文只将TTA列为预测变动来源，未把分割结果当作MRI重建实验或校准证明。 |
| Hendrycks–Gimpel 2017 | PASS | [作者论文](https://arxiv.org/abs/1610.02136)支持misclassification/OOD detection作为实际可靠性任务；本文不声称本文分歧优于其基线。 |
| Geifman–El-Yaniv 2017 | PASS | [NIPS官方论文](https://papers.nips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)支持selective classification/risk-coverage为不同下游目标；本文没有借用其风险保证。 |

## 其余主文重要引文

| 引文 | 状态 | 核查来源与引用范围 |
|---|---|---|
| Brown et al. 2005 | PASS | [作者机构记录](https://research.birmingham.ac.uk/en/publications/diversity-creation-methods-a-survey-and-categorisation/)支持diversity创建方法分类，卷6(1),5–20。 |
| Ortega et al. 2022 | PASS | [PMLR](https://proceedings.mlr.press/v151/ortega22a.html)系统讨论diversity与generalization，不把本文基本代数包装成新定理。 |
| Gal–Ghahramani 2016 | PASS | [PMLR](https://proceedings.mlr.press/v48/gal16.html)支持dropout Bayesian approximation；不是本文的受检确定性cross-context方法。 |
| Lakshminarayanan et al. 2017 | PASS | [NIPS](https://papers.nips.cc/paper_files/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html)支持deep ensembles预测不确定性；本文不否认其全部校准结果。 |
| Hu et al. 2021 | PASS | [作者论文](https://arxiv.org/abs/2002.05582)区分MRI随机与系统误差，是common-error blindness的重要先例。 |
| Edupuganti et al. 2021 | PASS | [作者论文](https://arxiv.org/abs/1901.11228)用VAE posterior variance与SURE讨论MRI风险，直接支持“variance不等于总风险”的背景。 |
| Narnhofer et al. 2022 | PASS | [作者论文](https://arxiv.org/abs/2102.06665)支持learned variational MRI epistemic uncertainty，未与本文物理输入干预混同。 |
| Luo et al. 2023 | PASS | [作者正式论文](https://ggluo.github.io/assets/pdf/Luo_Magn.Reson.Med._2023.pdf)支持diffusion posterior sampling/uncertainty，卷90,295–311，DOI一致。 |
| Lustig–Pauly 2010 | PASS | [期刊](https://onlinelibrary.wiley.com/doi/abs/10.1002/mrm.22428)是acquired k-space consistency先例；本文明确区分缺失切片预测之间的一致性。 |
| Greenspan et al. 2002 | PASS | [原论文](https://www.mriquestions.com/uploads/3/4/5/7/34572113/greenspan_1-s2.0-s0730725x02005118-main.pdf)支持MRI inter-slice SR与互补采集背景；不支持本文采集收益的因果结论。 |
| Nicastro et al. 2022 | PASS | [期刊原文](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2022.1044510/pdf)比较shift/rotate采集，支持互补采集已有研究。 |
| Horvath et al. 2017 | PASS | [作者机构记录](https://edoc.unibas.ch/entities/publication/0d68226a-b0b8-4630-85d9-823c99c585e1)与[作者海报](https://dbe.unibas.ch/fileadmin/user_upload/dbe/04_Research/CIAN/Projects/Antal_poster2.pdf)支持高阶切片插值背景。不能据其单独证明本文Anchor-CV是原论文提出的方法。 |

未在当前主文引用的历史bib记录不作为本轮科学论据，也不因仍在历史文件就自动赋予PASS。原始文件与完整历史记录已快照，未删改不利结果。主要数据使用、作者身份与投稿年份信息需要作者最终核实，但不阻断本轮已授权的本地计算和稿件整理。
