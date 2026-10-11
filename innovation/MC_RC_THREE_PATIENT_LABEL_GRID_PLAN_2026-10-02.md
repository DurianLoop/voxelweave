# MC-RC 标签映射、头部独立复核和标签grid：执行前方案

九个系列ZIP及官方标签包已经实际取得，头部attempt01完整成功，5条初步header-qualified、2条DERIVED/MPR、1条缺MRAcquisitionType、1条不规则几何。原始脚本/结果不覆盖。本方案在解码任何新标签数组前保存。

官方“pathname spreadsheet”实际为CSV，不需要转换/创建XLSX。Spreadsheets技能的bundled artifact-tool `Workbook.fromCSV`只读导入，检查的完整范围为虚拟sheet Official pathnames!A1:O488，实际487条记录/15列。全values已另存JSON，来源CSV原样保存；MacOS AppleDouble伪CSV不参与解析。现有tooling junction只指向只读bundled依赖，不更改依赖。

## 全目录联结

用原CSV的collection/patient_id/study_instance_uid/series_instance_uid/modality/num_files/SegmentationPath与当前487条API目录逐一联结，检查UID全集、唯一UID、病人/study身份和系列对象数量。`SegmentationPath`必须对应真实非__MACOSX的NIfTI目录条目。CSV与artifact-tool的全部单元格按字符串精确比较，UID不能经数字转型。路径取实际字段，不能根据病例名猜。

## 九条既定标签

只提取与上一预选九条UID精确对应的NIfTI，含不合格/待定头病例，不从ROI大小或是否成功选择病例。单个解压文件≤100MB、合计≤300MB，安全写到innovation/data下扁平文件名，不按ZIP路径写任意目录；保留CRC/SHA256/成员名/UID/source lineage。

只读取标签array、标签header和已取得DICOM **headers**，不解码MR pixel_array、不推断模型或质量/分割统计。标签检查3D、finite、值集合及前景体素/物理体积用于source gate，空标签保持记录，不以Dice强行评价无残余病例，也不因前景小就删病例。二值{0,1}为预期，异类标签/pix类型/映射冲突pending，不重编码。

标签NIfTI选择的affine和有效qform/sform均记录；有效qform与sform若在体积角点相差>0.05mm则pending。DICOM `(r,c,z)`实际RAS affine与标签xyz affine允许轴置换和翻转，不允许缩放、非整像素平移或非刚性注册修复。穷举48个带符号轴置换并用尺寸匹配筛选，八个角点最大世界位置差≤0.05mm，才可称same native grid；输出完整整索引变换与误差。若DICOM头几何本就不规则，不能靠标签affine把它“修好”，继续pending。

## 独立头部复核

从保存ZIP重新以pydicom stop_before_pixels读取逐对象记录，核SOP/身份/关键field与提取JSON一致。独立算法以排序后的首末IPP拟合z步长、逐plane完整世界位置残差验证affine，最大允许0.02mm；另核名义厚度、ORIGINAL/DERIVED、采集类型。缺失MRAcquisitionType明确分类为pending，不能把“不是3D”说成确认2D；原attempt01未放行该病例的结果继续保留。

最多5条header-qualified且label-grid通过的系列可列为“原生头/标签网格预检通过”。这是3人的来源预检/开发材料，不是新方法独立患者确认或可发表claim；旧VS-SEG八行crosswalk缺口仍保留。每患者多timepoint不能算独立人。
