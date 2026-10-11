# 本轮正文选择与检索补充

四条预写查询实际返回 47 条索引记录，其中重复作品和大量 radiomics 分类论文；47 不等于相关论文数或阅读量。初始森林查询按接口默认排序，前 12 条没有早期逐像素 lesion forest 方法。另加一条限定 FIRST_PDATE 1900–2020 的同一 lesion_forest 查询，最多 8 条；单次 30 秒/5 MB，保留原响应。这是覆盖年代不足的补充，不以实验结果挑文献。

先选择三篇新的直接相关公开正文（均非已完成方法验证）：

- Medical volume segmentation by overfitting sparsely annotated data，2023，PMC10434268，DOI 10.1117/1.jmi.10.4.044007：同一病例稀疏标签能否成为区域表示的直接先例。
- Contour interpolation by deep learning approach，2022，PMC9768435，DOI 10.1117/1.jmi.9.6.064003：插值标签/形状模型的直接先例。
- Efficient contour-based annotation by iterative deep learning for organ segmentation from volumetric medical images，2023，PMC9889459，DOI 10.1007/s11548-022-02730-z：逐层真实注释与传播/模型迭代的直接先例。

仅从 NCBI EFetch 取得 JATS，验证 article/body 和 DOI，原响应每篇最多 12 MB。按正文结构导出带序号的段落、表格、公式和图注。取得后再核读，补充文件与图像没有实际读取就不称已读。历史森林索引不自动增加正文数量；如另取第四篇，须记录明确选择依据。
