# MC-RC 后续原生T2与标签资格准备（未执行）

前置文件：[候选患者和完整目录审计](MC_RC_V2_NONPIXEL_IDENTITY_RESULT_2026-10-02.md)，[固定预选JSON](experiments/mc_rc_v2_nonpixel_identity/native_header_followup_selection.json)。这份准备不宣称来源通过，也没有启动头/影像/标签下载。

预选为按官方非重合候选ID排序且有T2描述的前三人VS-MC-RC-001/002/003，包含其全部9条T2描述序列；不从初步性能或最小spacing选病例。身份可信度来自官方页面排除全58共享患者规则，旧crosswalk仍未联上。预选用于来源可行性，不是正式确认队列。

下一执行阶段先补写有范围/字节上限的读取合同，然后核：

1. 实际原生DICOM：MR Acquisition Type、ImageType/DERIVED、SequenceName、TR/TE、PixelSpacing、SliceThickness与逐切片ImagePosition/Orientation；逐切片实际spacing不同于名义厚度，不能从description中的3D/iso/MPR判断资格。仅取第一切片不足以确认全体积几何。
2. 官方标签zip目录与metadata映射：从认证TCIA链接读取；先列压缩目录、路径与版本，若需解析其pathname spreadsheet，应使用spreadsheets技能，不能仅靠文件名猜UID/空间。完整标签数组与DICOM网格必须实际对齐验证，再说“有人工病灶标签”。
3. 保留defacing、注册/重采样和像素改变说明。只允许原生符合预写薄层/3D/几何条件的系列作缺层参考，derived MPR不补充作原生thin truth。
4. 查固定任务模型训练来源。若用作者MC-RC或MC-RC+SC-GK模型，其训练患者可能包括新候选，不能作独立任务模型确认；当前旧SC-GK来源模型也需按已核split排除患者，而非按weights文件名。任何新训练需要GPU空闲后另按既有授权继续。
5. 对全新收益方法，应在读取性能前冻结患者级开发/验证/校准/确认、重复检查归属、同预算动作集合和主要端点。前三人资格预检如用于设计就不留作未见确认。

若八行旧UID联结需修补，只接受官方新版mapping或经认证的索引对应；不改ID、不按description推断。源数量、缺失/网络失败和无残余标签单列。本阶段准备不影响正在运行的45人主队列，不启动GPU，不干预用户终端。
