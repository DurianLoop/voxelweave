# COBRAI、crossMoDA 2026、Kujawa 2024：核读与项目新意边界

本阶段取得一份作者 PDF 和两份经 DOI 认证的 JATS 正文；重点核读方法、数据、评价和限制，并非三篇全部图表/补充材料的完整复现。主注册 PDF 库仍为29份；新增作者 PDF 保存在 source_cache，不计入该29份。没有新患者性能确认。

## 1. Insights on Scan-Specific Deep-Learning Strategies for Brain MRI Parallel Imaging Reconstruction

NMR in Biomedicine，2025，DOI [10.1002/nbm.70079](https://doi.org/10.1002/nbm.70079)，PMC12183417。正文70个提取块，保存于 [JATS及分段](source_cache/cobrai_crossmoda_public_2026-10-02/attempt_01.json)。重点核读[18,20,24–35,42,50–65,69]，其他若干方法/结果也分块检查；未执行作者代码、未完整审阅补充材料。

**实质方法。** 用同一次扫描的 ACS 分训练/验证，再按加速倍率R做K-fold和grid search，选kernel、depth、loss及线性程度；验证k-space MSE用于选择模型/超参数，随后以完整k-space生成的图像参考核性能。[18,20,30–33,54] 是直接选择先例，不能把“无完整图像真值选MRI模型”称为首次。

**关键更正：COBRAI不是无参考指标。** [34–36]定义：重建减去完整参考图像得到残差，11×11局部patch计算残差与参考的相关系数；在brain mask内平均绝对值。它量化结构残差，必须有完整参考。摘要的“can be used to drive model selection”不能解释成缺层部署时无需真值。真正无需完整图像参考的路径是ACS held-out k-space MSE。COBRAI可作为参考存在时的补充诊断，不能作为当前动作头的部署输入。

**证据范围。** fastMRI每种FLAIR/T1/T2/T1POST各随机20 volumes，约300 slices/contrast；另有自采T2和multi-echo GRE。Fig6为一个志愿者49 slices/两个echo，不能把slice检验当大规模患者确认。[61]明确极端破坏不一定被充分捕捉，应联合NRMSE、SSIM、PSNR。任务是2D多线圈k-space平行成像，不是本项目magnitude层间缺层重建；这种合同差异仍不足以单独构成方法新意。

**本项目要多证明什么。** 固定重建动作的局部净收益可预测性、与同容量绝对误差头/分歧阈值/固定混合/观测留出选择相比的增量，以及完整患者、病灶守卫和同预算表现；不能仅改名“收益”或从全局选择换成tile选择。

## 2. crossMoDA Challenge: Evolution ... from 2021 to 2023

Medical Image Analysis114，2026，104282，DOI [10.1016/j.media.2026.104282](https://doi.org/10.1016/j.media.2026.104282)，arXiv2506.12006；KCL作者机构accepted/peer-reviewed version封面认证。[来源响应](source_cache/action_crossmoda_adaptive_2026-10-02/attempt_01.json)，[PDF](source_cache/action_crossmoda_adaptive_2026-10-02/crossmoda_author_pdf_attempt_01.pdf)，[渲染/提取provenance](source_cache/action_crossmoda_adaptive_2026-10-02/crossmoda_pdf_provenance_2026-10-02.json)。完整重点核PDF页4–8的数据/标签/评价、页22–23讨论/结论；页9只核ranking延续，方法团队表未逐一核完。视觉检查页4–8中的4,5,6,7,8以及Table1专图和页23；页22为文字核读。

| 来源 | 正文采集线索 | 对本项目的资格判断 |
| --- | --- | --- |
| London SC-GK | 旧Shapey2021/VS-SEG | 不能作为新独立来源 |
| Tilburg SC-GK | Philips Ingenia1.5T，T2 3D-TSE，0.4×0.4×1.0mm；ceT1 0.8×0.8×1.5mm | 机构独立；公开T2人工标签仍未认证 |
| UK MC-RC | 十个UK sites，2006–2019，多厂家/场强，routine surveillance | 逐患者去重和逐扫描原生身份必须另核，不能只因多中心就判独立 |

Table1英国2023 challenge为source38人43扫描、target47人105扫描、val15人32扫描、test45人94扫描；总表145人274扫描。London/Tilburg同一患者可能跨模态出现，表含模态/阶段记录，不能直接相加作独立人数。PDF页6叙述原库165人，而Kujawa2024及当前TCIA原库160人；challenge子集和原库版本须各自登记。

训练source ceT1有标签，target T2无标签。页6的UK训练source重新独立标注ceT1/T2、不跨模态互看，不能与Kujawa原库的高分辨率参考加另一模态辅助协议混用。2023还增加intra/extra-meatal分区，原库二值VS标签不自动具备这些新类别。

**排版证据。** Fig1实际轴B=Slice thickness、D=Voxel volume，图注B/D互换；记录按图轴，不从violin估单扫描资格。Table8图注称individual cumulative ranks，但表实际列DSC/ASSD；本阶段不引用其为“rank数值”。页8明确DSC和ASSD，空预测ASSD设350mm；challenge按case/region/metric排名，并非本项目患者级配对CI。页9延续按case bootstrap，英国有重复扫描，不能直接借用其case作为独立患者的统计单位。

耳蜗下降原因仍开放；作者列出采集异质性、优化任务平衡和方法tradeoff等，不能当纯分辨率因果证明。

**发布核查。** 2022 Zenodo6504722公开元数据已读，训练zip7.79GB、验证zip1.04GB、source CSV/GIF；没有读压缩目录/影像/标签，因此未证公开T2标签。record license字段CC BY4.0，而description与论文为CC BY-NC-SA4.0，保存冲突，不能自动当宽松许可。2022 dataset页403，失败原响应保留。2023 Synapse syn51236108公开实体metadata200仅认证Project名称，不证明文件或标签无需登录可读。

## 3. Deep learning for automatic segmentation ... multi-center routine MRI

Frontiers in Computational Neuroscience18，2024，1365727，DOI [10.3389/fncom.2024.1365727](https://doi.org/10.3389/fncom.2024.1365727)，PMC11111906；经精确题名EuropePMC查到唯一结果并取JATS。[来源及分段](source_cache/cobrai_crossmoda_public_2026-10-02/attempt_01.json)。重点完整核[11–23,26–34,39–48,61,69,76–83]；未逐一核结果Tables2–4或全部评价公式/图像。

**原库和标签。** 最终160人、427 timepoints、487影像（T2 363、ceT1 124）；349高分辨T2、14低分辨T2是文中分类，[15]高分辨定义各方向spacing<1mm，不自动等于原生3D薄层认证。[14]排除厚度>3.9mm，[20]同模态多系列选平均spacing最小；仍可能有MPR/derived序列，须看原生DICOM tags。每人最多三时间点。人工标签为公司初标、三放射科医师迭代复核、专家裁决；双模态时在更高分辨率grid标注并辅助看另一模态。[33]组合输入将ceT1配准到T2，不能把NN标签重采样输出当独立原生标注。

**关键重合。** [31]明确58人也在SC-GK/旧VS-SEG中，8系列重复；时间点不同仍是同一患者。本文分割模型training/testing按患者分割，对交集系列放入各自training；“fully independent testing”只明确用于Tilburg，而其中T2的32例是当时private validation，并非立即公开人工标签。

**任务新意边界。** 已经做多中心通用性、worst cases、术后小残余与无残余假阳性体积分析；仅增加病灶分割/体积/最差病例评价不是新贡献。[76]术后低对比T2残余可几乎全漏（DSC1.9%），无残余时Dice和表面指标不合适；[61,69,77–78]改报告是否误检和假阳性体积，并讨论8mm³阈值。新实验应明确病灶保持的实质增量，不能引用这些例子证明本项目插值造成临床损害。

**官方第2版是新机会，不是已确认成果。** 数据引用 DOI10.7937/HRZH-2N82落地到TCIA当前版：2026-06-04补133序列，完整487series/160人已由API与manifest核对。标签zip公开页面列出NIfTI，图像DICOM已deface。严格排除58共享患者后，按官方ID规则剩102候选，其中100人/238个description为T2的序列；当前八行crosswalk旧UID侧全未联上。详见[CPU审计](../MC_RC_V2_NONPIXEL_IDENTITY_RESULT_2026-10-02.md)。没有核标签数组或native geometry，不能宣布100独立薄层确认患者。

## 检索边界

两批OpenAlex宽泛/引号query大量无关高引用结果；有些终端长输出截断，没有算全部阅读。EuropePMC精确命中COBRAI是有效近邻，不构成系统综述。未取得的image restoration model selection候选仍摘要级，不宣称无直接收益预测先例。当前结论是排除错误“无参考COBRAI”解读、补充已存在ACS模型选择先例，并找到可继续筛查的公开新版本。
