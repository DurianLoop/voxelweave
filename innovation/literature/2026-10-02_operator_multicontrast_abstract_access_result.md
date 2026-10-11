# 近期任意尺度、各向同性与靶区采集候选：摘要层证据与全文访问

本阶段对四个已确定 DOI 各请求 Europe PMC 和 OpenAlex，八份公开元数据响应全部成功；另对三篇新候选取得 Crossref 正式卷期/来源地址，再有边界地尝试出版社和arXiv路径。新增正文取得数为0，不能计作四篇或三篇全文阅读。来源索引：[DOI/摘要](source_cache/operator_multicontrast_candidates_2026-10-02/attempt_01.json)、[公开正文路径](source_cache/public_operator_candidate_bodies_2026-10-02/attempt_01.json)。此前[四篇实际全文核读](2026-10-02_task_throughplane_fulltext_collision_matrix.md)仍保持原阅读层级。

| 精确论文身份 | 本阶段可认证的摘要事实 | 与项目比较及不能推断的内容 |
| --- | --- | --- |
| Chen et al., *Multi-Contrast MRI Super-Resolution in Brain Tumors: Arbitrary-Scale Implicit Sampling and Unsupervised Fine-Tuning*, DOI [10.1109/TMI.2025.3628113](https://doi.org/10.1109/TMI.2025.3628113)。正式 TMI 45(4),1395–1406,2026；OpenAlex online日期2025-11-03 | 隐式采样/生成 ISG、任意尺度和测试时无监督 fine-tuning；利用高分辨率参考模态，临床 APTw 肿瘤与5T FLAIR，两组影像、放射科医生评价 | arbitrary-scale、test-time adaptation、临床肿瘤SR 都已有明确摘要先例。高分辨率参考模态改变了观测预算，不能直接拿来证明本项目单T2 x4获益。LR构造、人员划分、输入模态和具体任务指标待正文认证 |
| Hsu et al., *Self-supervised isotropic reconstruction for abnormality detection in anisotropic MRI*, DOI [10.1016/j.compmedimag.2026.102786](https://doi.org/10.1016/j.compmedimag.2026.102786)。CMIG133,102786,2026 | 8:1 knee TSE，单向multi-view GAN加contrastive/adversarial目标，第二阶段anatomy-conditioned diffusion产生健康counterfactual及病灶map。摘要报告2,225个OAI knee scans、五中心、perceptual指标/医生偏好和femur-tibia分割F1改善 | “self-SR + diffusion异常检测 + 下游任务”已有摘要先例。不能把scans数当独立患者数，也不能在没有正文/人工真值合同下认证病灶准确度、无信息泄漏或各中心真实独立性。不是脑CISS来源 |
| Mickevicius & Paulson, *Target-driven acquisition and super-resolution reconstruction for magnetic resonance imaging*, DOI [10.1016/j.mri.2026.110675](https://doi.org/10.1016/j.mri.2026.110675)。MRI130,110675,2026 | 放疗靶区位置已经确立；旋转2D采集每个prescribed slice均与target相交，以parallel imaging加SR重建出靶区较高、远处较低细节的3D体积。摘要说3T phantom和in vivo示范 | 它主动改变采集方向与信息分布，不能从题名误读为对固定轴向缺片作普通插值，也不是任务loss的名称。采集operator/靶区优先已是明确动机；扫描人数、误差与临床结局需要正文 |
| Küstner et al., *Predictive uncertainty in deep learning-based MR image reconstruction using deep ensembles: Evaluation on the fastMRI data set*, DOI [10.1002/mrm.30030](https://doi.org/10.1002/mrm.30030),2024 | aleatoric/epistemic deep ensemble、五种架构、sampling pattern/contrast/orientation/anatomy/pathology shift，预测uncertainty与NMSE关联 | 仍是摘要层近邻；像素uncertainty、架构/域迁移不能作为首创。是否包含本项目精确的同目标伙伴上下文切换，仍不能认证 |

OpenAlex 对 knee 第二作者的姓名展开与 Crossref 不同；以 DOI 定位，不自行补齐人名。出版卷期年份与 DOI 中的2025不一致属线上/卷期日期差别，不把TMI DOI后缀直接当2025正式卷期。

## 实际公开路径与失败

三份Crossref响应均200。TMI publisher地址由Crossref认证为IEEE document11224014，实际HTTP202、零字节，不是正文。两份Elsevier XML响应200，只有coredata（题名、DOI、PII、期刊、openaccess=false等），没有body/originalText；服务根节点叫full-text-retrieval-response也不能说全文已得。原响应与哈希保留。

三个arXiv标题查询：TMI/target-driven返回HTTP429；knee读取超时。这不是成功搜索的零结果，不证明没有预印本。不为绕过限流换身份、登录或使用私人凭证；当前仅记录待稍后公开路线可用时再读。

Kuestner的最新两个公共索引仍只指向Wiley、PubMed和TUM1752940，没有新增可读正文地址。OpenAlex的OA/CC-BY标签与Europe PMC无开放全文/PMCID不一致，应视为可用性线索而非下载成功。此前[公开访问审计](2026-10-01_kuestner_fulltext_access_audit.md)的403/401和TUM无正文状态未被此元数据刷新关闭；本阶段没有重复所有已失败出版社路径。

## 对创新路线的具体影响

原始采集、未知层响应与任意尺度/TTA首先是输入合同与现有方法问题；不能把已知模块叠加换名称。当前模型只使用固定phase-0单T2观测，而MRI“multi-contrast”“多方向stack”“实时主动旋转编码”通常使用更多或不同测量，需要明确预算才能比较。

新做的[开发例固定动作上限](../VS_SEG_001_LOCAL_ACTION_ORACLE_RESULT_2026-10-02.md)给出有限空间和pipeline守卫反证；它并没有解决未知operator、真实薄层参考或外部任务确认。下一步仍以固定45 CISS完整研究为主，同时保留Kuestner方法级碰撞缺口。本索引不支持任何“已证明没有同类工作”的主张。
