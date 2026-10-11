# MC-RC 004–006：执行前原生头和标签合同

上一轮为实际来源资格进展，本轮科学目标仍 active。本合同在下载下一批或读取新标签数组前保存。继承 [固定准备](experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json)的 VS-MC-RC-004/005/006 全部八条有真实标签的 T2 系列，不按 spacing、病灶或效果修改名单。701 个 API 对象，FileSize 385,990,404 bytes 是目录字段，不是实际 ZIP bytes。

## MR 读取与资源

使用既有公开 TCIA getImage endpoint，八系列全部记录；只取这些 UID，不重新下载已取得标签 ZIP。顺序下载，最多一条连接；单系列上限 max(5MB, ceil(1.15*API FileSize)+1MB)，全部实际读取字节上限 500,000,000。每次 read 限制在剩余预算内；达到上限且未确认 EOF 则保留 partial 并判失败，不越预算探测。HTTP timeout30s、每系列整体180s，无自动重试。

请求开始/结束时间、最终URL、HTTP状态/类型/长度、源字段、实际bytes/hash及失败均保存；不因失败更换患者，完整分母仍八系列。ZIP传输包含MR像素字节，但逐对象均以 `stop_before_pixels=True`，**不解码 MR pixel_array、不计算重建/分割性能**。使用原始 helper 的 header_record/inspect_series，并对当前进程指定新的输出目录和预先冻结的 geometry v2；原 helper 文件/首跑结果不修改。

子进程隐藏 CUDA，BLAS/OMP/MKL 各1线程，own process below-normal priority；启动前核磁盘15GB和可用RAM8GB底线，不列举或干预用户训练进程。所有数据、partial、请求、日志存 innovation。

## 原生头与几何 v2

原生头条件与此前实质相同：逐对象 Patient/Study/SeriesUID吻合；SOP唯一/计数等于API；经典单帧MR；共同Rows/Columns、FrameOfReferenceUID；IOP与PixelSpacing分量差≤1e-6，方向单位/正交误差≤1e-4；无重复plane，法向gap偏差≤0.02mm，全部IPP中心化线性拟合残差≤0.02mm。缺必要field或enhanced多帧为pending，不默认合格。

全部 `MRAcquisitionType=3D`、ORIGINAL且无DERIVED/MPR/Reformat/localizer、三轴spacing和名义厚度均≤1.5mm才header-qualified；缺采集类型保持pending。orientation/spacing/厚度/identity不能通过回归抹去。v2在本批读取前固定使用全IPP拟合，不再使用首批中位数差估计器；这是先前事后修正后的新版本，不改变首批历史。

记录实际spacing与名义厚度，不把spacing解释为PSF/物理分辨率，也不将跨时间点作为重复监督。原始头资格仅为来源预检，不能证明完整物理观测算子。

## 八个既定标签数组/grid

使用已认证官方标签 ZIP 和已经由 artifact-tool 只读解析的 CSV 全表；本批只用精确SeriesUID/SegmentationPath联结，不重新编辑工作簿。仍核CSV全单元格/来源hash及患者study/objectcount，与准备UID全集一致。通过完整联结后提取这八个标签，包括头部不合格系列；不因标签大小/派生而跳过检查。

安全扁平目标路径；每个ZIP成员≤100MB、成员总bytes≤300MB；NIfTI实际数组每个≤100MB、合计≤300MB，读取前按shape/dtype计预算。检查3D/finite/{0,1}，保留空标签不按病灶大小删患者。有效qform/sform八角点差≤0.05mm。DICOM与label仅允许整数轴置换/翻转，最大角点误差≤0.05mm；禁止缩放/注册/非整平移修复。头部不合格或missing标签不放行。

处理完成与资格通过分别记：即使八条全部检查结束，也不称完整487标签覆盖通过。原完整label gate失败、126新增T2缺文件及旧legacy UID联结失败继续保留。

## 独立复核和结果边界

从本批原ZIP独立重读头/标签，完整 `np.linalg.lstsq` 与首末位置法核 affine、法向gap；使用 `inv(DICOM affine) @ label affine` 整数变换检查，避免复制主grid穷举。重新核资格、原生spacing/厚度/derived/pending，不只比较bool。

预检患者及其所有时间点整体归来源/开发，不成为新方法未见确认。当前实际科学独立性能确认0；本合同不启动MR数组或模型实验。来源合格后须另冻结观测/动作/预算/评价，再做多开发病例oracle。原CPU session83910继续原45+1合同，不能分析动态子集或改主方向。
