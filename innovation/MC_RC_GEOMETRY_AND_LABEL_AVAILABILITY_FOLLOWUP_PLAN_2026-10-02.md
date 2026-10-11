# 首跑标签不足与几何估计累计误差：追加核查方案

首次label_grid_attempt01保留exit1/complete=false：487条CSV与API UID全集/单元格吻合，实际标签包有301个非MacOS NIfTI；匹配301行，186行缺少指定标签文件或未指定path。初步核126条2026新增T2与7条新增T1均无包内文件；53条既有T1的SegmentationPath为空。空path不能称错误文件名，也不能自动套用同study的T2标签。

原头部中VS-MC-RC-002第二时间点判“Nonuniform/non-affine”：用相邻IPP差逐分量中位数作步长后144切片累计残差0.03mm>0.02mm。实际沿法向gap变化仅约5.2e-7mm，首末IPP步长拟合最大残差0.000776mm，最小二乘约0.000482mm；这说明原估计器可能对坐标量化敏感，尚不能称采集不规则。

本方案在重算/重分类前保存，不改变原计划、脚本、数据或阈值，未读MR像素/性能。追加三项：

1. 全CSV/ZIP/API以SQLite独立联结，分别报告明确blank path、指定path absent、available，不自动重编码path。按T1/T2描述和release date、共享患者/官方非重合候选分组；预选003仍全部缺标签。
2. 用所有IPP的中心化线性回归估affine原点/步长，残差仍≤0.02mm；方向一致性、法向gap、名义厚度、ORIGINAL/DERIVED、3D/缺field条件保持不变。独立实现使用完整设计矩阵np.linalg.lstsq和首末位置法，核新fit而非只看布尔值。缺MRAcquisitionType明确pending。
3. 标签same-grid仍采用原0.05mm八角点阈值及仅轴置换/翻转，不允许缩放或注册修复。只使用此前已经读取且实际存在的六个标签，第三名三个missing仍pending；解析两个有效forms及二值标签条件不变。独立算法用 `inv(DICOM affine) @ label affine`检查是否整signed permutation，避免照搬48穷举实现。

首跑header资格5、原grid预检3series/2人和failed全库gate保持历史；追加fit若恢复某系列，明确为事后几何估计器修正，不把旧判定删除或当新方法性能成功。非规则坐标/派生series不能通过fit伪装成native，不阈值搜索。

最大可预期来源预检为6条header候选，但当前preselected003缺标签，完整可用系列上限4条/2人；不是100个合格thin/native确认患者。旧八条VS-SEG UID crosswalk不足和患者分组要求不变。
