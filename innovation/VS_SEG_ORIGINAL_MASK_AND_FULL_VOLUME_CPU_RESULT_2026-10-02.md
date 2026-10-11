# 原始掩膜门槛已关闭；完整体积预检尚不支持独立 claim

本轮完成了独立 CPU 标注转换、两篇新增方法全文阅读、七条件完整体积开发预检，以及全部 46 名官方任务测试患者的来源与参考掩膜核验。**仍没有独立验证的可发表 claim**。值得继续检验的是同观测、强解析对照下全图收益与病灶任务结果的关系，以及病灶切片筛选对评价覆盖的影响。当前终端训练未受到启动、停止、重启或修改操作；新模型执行均为单线程 CPU，CUDA 未初始化，未读取锁定 IXI test。

[方法论文与新意矩阵](literature/2026-10-02_vs_seg_model_method_and_label_novelty_audit.md)记录两篇新增全文及其版本：Wang MICCAI 2019 正式修订 PDF、Shapey JNS 的 PMC 作者稿。它们来自当前模型同一研究线；2.5D、监督注意力、困难体素损失、T2 病灶分割和 ensemble 都不能算本项目新意。JNS 所取稿的摘要/正文人数冲突、T2 并未被证明人类等效、旧网络与当前 MONAI 单模型的不同都已保留。Sunderland/SlicerRT 工具论文仅取得元数据/摘要，未充当全文证据。

**原始离层轮廓现在可以转换。** 官方 Slicer 5.12.4 revision 34645 与 SlicerRT git `3b6ce695aadf6133c0e97778843aa577f6ddbe64` 匹配，两包官方 SHA512 校验通过。独立解包 1,222,575,394 字节；安装器未执行，未修改用户环境。PythonSlicer 只启动 python-real，不创建 Slicer 应用或渲染窗口；禁用 CUDA、限制 VTK 线程并忽略用户附加设置。使用逐 Git blob 核验的作者原始轮廓构建函数及官方 ExportSegmentsToLabelmapNode，保持原生 extent/affine、默认 smooth end cap，不把 JSON 投到最近层。

| 固定开发患者 | 原 JSON 体素 | RTSTRUCT 体素 | 两参考 Dice | 原 JSON 多出的完整层 |
| --- | ---: | ---: | ---: | --- |
| 001（作者训练集） | 7,534 | 7,505 | 0.9861028 | 29 |
| 182（作者验证集，已发表 Fig.2 边界例） | 780 | 634 | 0.8840170 | 43、48 |

[转换结果](experiments/vs_seg_original_mask_cpu_development/attempt_03.json)与[独立坐标/参照核验](experiments/vs_seg_original_mask_cpu_development/independent_geometry_and_reference_verification.json)保留全层统计。物理坐标误差小于 10⁻¹² mm，两例 RTSTRUCT 的官方转换与独立平面栅格化均零体素差。182 已复现原论文首尾整层缺失；这是已有现象的复现，不能称创新。当前官方工具版本及原始 helper 路径可追溯，但没有逐字节证明它与作者历史 NIfTI 掩膜相同，原论文当年的精确运行时版本仍未知。标签来源于 T1/T2 共识，任务结果只评价对这个参照的保留。

**滑窗兼容性已验证。** 将 MONAI 0.4 的四处多维 list 索引明确转为 tuple，001 原生影像的两次完整前向 logit 逐位相同，最大差为零；预测与前次原生预检也相同，CUDA 为 false。[结果与派生实现](experiments/vs_seg_001_tuple_equivalence/attempt_01.json)保留。没有修改官方 wheel 或网络数学。

**七条件完整体积预检完成。** 按事前 [开发合同](VS_SEG_001_FULL_VOLUME_CPU_PREFLIGHT_PROTOCOL_2026-10-02.md)，001 只观察 0/4/.../76，恢复全部 57 个内部缺失层，末端 77/78/79 对各重建方法复制 76；观测层逐位保留。分割评价用完整体积原 JSON 参照，没有病灶目标筛选。总耗时约 292 秒，七份重建体积、预测及逐层误差全部保存；[独立复核](experiments/vs_seg_001_full_volume_cpu_preflight/independent_saved_output_verification.json)重新打开输出并核查坐标、观测层、末端约定、TP/FP/FN 与误差统计，零错误。

| 条件 | 全支持域目标等权 NMSE | 病灶目标等权 NMSE | 病灶像素加权 NMSE | 全体积 Dice |
| --- | ---: | ---: | ---: | ---: |
| native | 0 | 0 | 0 | 0.9579821 |
| raw linear | 0.00220533 | 0.00698837 | 0.00444066 | 0.8696871 |
| raw PCHIP | 0.00224690 | 0.00796505 | 0.00478636 | 0.8844858 |
| pipeline linear | 0.00205177 | 0.00633967 | 0.00397877 | 0.8637953 |
| pipeline PCHIP | 0.00204813 | 0.00710712 | 0.00419509 | 0.8758670 |
| HAT | 0.00169502 | 0.00784895 | 0.00413715 | 0.8814050 |
| SwinIR | 0.00170772 | 0.00748125 | 0.00407389 | 0.8739264 |

这份结果只属于已见、参与分割训练的开发病例。HAT 相对 pipeline PCHIP 全图误差下降，但 Dice **提高 0.005538**；SwinIR Dice 下降 0.001941。HAT 相对 raw PCHIP 的 Dice 又下降约 0.003081，说明不能换一个参照后只展示任务损失。两模型的病灶目标等权误差变差，但病灶像素加权误差改善；因此本例不支持“区域像素误差增加必然造成分割损失”，也不能把有利汇总方式选成确认指标。

**46 名独立任务患者的源级门槛已完成。** [固定名单来源方案](VS_SEG_FULL_VOLUME_HELDOUT_SOURCE_GATE_PLAN_2026-10-02.md)、[逐例头部/原 JSON 来源](literature/source_cache/vs_seg_full_volume_source_gate_2026-10-02/attempt_01.json)、[全部掩膜](experiments/vs_seg_full_volume_source_masks/attempt_01.json)及[独立验证](experiments/vs_seg_full_volume_source_masks/independent_source_geometry_verification.json)覆盖 46/46，零来源失败。45 例为 ORIGINAL 薄层 3D CISS，均 448×448×80；TSE 单例 248 为 ORIGINAL 3D 384×384×40、1.5 mm，另行描述。首结构为 TV 39、AN 7；没有以名称、64 像素、病灶层数或 native Dice 筛人。全部物理坐标核验最大误差约 4×10⁻¹² mm，原 JSON/RTSTRUCT 两参考 Dice 范围 0.91953–0.99726。直接捕获 PythonSlicer 的返回码为零，重复转换 46 份 mask archive 的 SHA256 完全一致。

在 45 名 CISS 中，若加入原规则的 >=64 病灶体素和四锚点边缘条件、仍暂不与图像支持域求交，RTSTRUCT 至多 18 人、原 JSON 至多 19 人可能满足四目标要求。它比前次取消像素门槛、允许全部相位/方向的 22/46 上界更严格，二者不能混算。该分析没有运行重建或分割模型；仍不能据此宣称已证明完整队列上的方法排序会反转。

下一步 [完整体积设计草案](VS_SEG_FULL_VOLUME_TASK_DESIGN_DRAFT_2026-10-02.md)明确固定 45 CISS 主名单、HAT − pipeline PCHIP 双终点主比较、强 raw PCHIP、标签/边界敏感性、失败分母和假设功效计算。它尚需通用队列运行器与统计/边界实现后冻结；46 人尚未产生本项目任务预测。448 网格需要八个滑窗，完整单线程 CPU 队列预计约 8–10 小时，尚未实测。新增训练方法的 GPU 尝试保持为后续准备，未动当前训练。发表目标保持 active。

本轮全部传输、兼容、解包和源级失败/修复，以及可见对话与归档入口见 [会话记录](SESSION_UPDATE_VS_SEG_MASK_AND_FULL_VOLUME_2026-10-02.md)。
