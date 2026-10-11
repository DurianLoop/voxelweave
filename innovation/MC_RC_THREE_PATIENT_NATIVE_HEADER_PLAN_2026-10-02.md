# MC-RC 三名预选患者：原生头与官方标签目录执行合同

本计划在新患者字节读取前保存。继承 `experiments/mc_rc_v2_nonpixel_identity/native_header_followup_selection.json`：VS-MC-RC-001/002/003全部9条T2描述序列，不按性能或实际spacing再选人。它们是来源资格/后续开发材料，不能补充为新方法的未见确认。

## 读取范围与资源

- MR仅取上述9个UID，使用项目既有TCIA公开 `getImage?SeriesInstanceUID=` endpoint。API FileSize合计227,737,860 bytes。为取得完整几何，下载完整系列ZIP再以pydicom `stop_before_pixels=True`核每个DICOM对象；传输包含MR像素字节，**不解码MR pixel_array、不推断模型、不计算质量/任务性能**，不能称纯非像素下载。
- 每系列上限 `max(5MB, ceil(1.15*FileSize)+1MB)`，最多两下载线程，所有成功/失败传输合计上限300MB。HTTP read timeout30s，每系列总时限120s，无自动重试；部分文件另存partial并保留失败。
- 官方标签ZIP只从此前DOI认证页面的实际链接读取，上限5MB；列全部目录和大小/hash，先只提取≤1MB的metadata/xlsx/readme，不解码NIfTI标签。本阶段metadata仅为来源联结，不是标签grid确认。
- 保存每请求URL/时间/最终URL/HTTP状态/Content-Type/Content-Length、字节和SHA256，成功ZIP保存在innovation/data，头与目录记录保存在source_cache。不会运行Data Retriever、启动GUI/账户、下载权重、调用GPU或干预终端训练。

## 固定头部资格判据

每对象必须PatientID/SeriesUID符合预选，SOPUID唯一且对象数与API ImageCount一致；经典单帧MR，enhanced多帧另标pending，不猜几何。逐对象核Rows/Columns、PixelSpacing、SliceThickness、ImageOrientationPatient、ImagePositionPatient、FrameOfReferenceUID及MR Acquisition Type、ImageType、SequenceName/ScanningSequence/SequenceVariant、TR/TE。

几何要求：共同rows/cols、orientation每分量差≤1e-6、spacing差≤1e-6mm，方向余弦单位/正交误差≤1e-4；沿法向排序无重复plane，位置可由单一affine表示，最大位置残差≤0.02mm，沿法向spacing相对中位数的最大绝对差≤0.02mm。实际逐plane间距与名义SliceThickness分别记录。

只有MR Acquisition Type全为3D、ImageType有ORIGINAL且无DERIVED、最大三轴native spacing与SliceThickness均≤1.5mm且上述几何通过，才列为“header-qualified candidate”。ImageType/Derivation/SeriesDescription有MPR、Reformat或localizer证据则不放行，需进一步来源认证。缺失关键field标pending，不能作合格默认。DERIVED/MPR不以插值后的漂亮spacing替代原生thin参考。

DICOM affine以(r,c,z)坐标构造：row步长=IOP第二triplet×PixelSpacing[0]，column步长=第一triplet×PixelSpacing[1]，z步长=排序后真实位置差中位数；LPS转RAS用diag(-1,-1,1)。独立复查会从原始记录重新构造，而非只检查程序返回布尔值。病灶标签暂未核grid，本阶段合格头不是完整来源合格。

## 标签路径表

已读取Spreadsheets技能，使用bundled artifact-tool只读导入官方pathname xlsx并提取实际表头/单元格/表范围，不改写工作簿，不运行authoring marker。保留全表、formula/error情况和精确source sheet/range。按真正UID/path列联结，不靠病例名字猜路径；若读取失败，记录工具/格式失败后按技能允许的只读fallback解析原始OOXML，不能悄悄换成宽松映射。

下一阶段须另冻结label数组/grid检查范围和条件，再读取匹配标签；此阶段不报告独立患者性能、临床损害或新的方法成功。
