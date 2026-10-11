# 重采样顺序：正文选择与查新边界

本批依据已完成的三项公开索引检索选择正文，不依据尚未核读的CPU效应大小。27个返回题名含两条Brainana版本；不把返回数、摘要和正文混算。VINNA此前只在索引摘要中出现，先查是否已有正文后再计新增。

优先选择：

1. VINNA for neonates，DOI `10.1162/imag_a_00180`，PMC11576933：图像与标签插值、内置分辨率/刚体变换，直接限制“避免重采样”宽创新。
2. Influence of image preprocessing on reproducibility and longitudinal repeatability analysis of radiomics features in magnetic resonance image-guided accelerator imaging，DOI `10.21037/qims-2025-aw-2151`，PMC13178426：MRI预处理因素的实际重复性研究。
3. A Stability Atlas for IBSI Radiomics Features Using Synthetic Digital Phantoms, with Proof-of-Concept Physics-Based Normalisation，DOI `10.3390/jimaging12080392`，PMC13514157：插值因素、数字模体和物理归一化；区分已知处理敏感性和本项目的窄新问题。

每篇最多一次公开NCBI EFetch（30秒、12MB），保存原始XML、HTTP状态、实际URL、DOI身份、正文块、许可和SHA256。失败保留，不重复受限出版商路径。获取与阅读分开登记；只有实际核读相关正文及表格才计阅读。公式/表格被展平、未读图片/补充材料须声明；本批不生成PDF，不将抽取文字当视觉核验。

CPU研究为45已见CISS结果后诊断；不改变原主假设、病例或合同，不读locked IXI test、不运行GPU、不操作用户训练。文献既不能证明本项目效应，也不能将图像NMSE当分割/临床结论。
