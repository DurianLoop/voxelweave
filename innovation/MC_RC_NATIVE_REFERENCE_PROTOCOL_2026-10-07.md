# 完整 native MR 参照认证协议

目的：建立旧 observed-only 部署接口之外的完整 MR 参照，解决旧变量 native 实为 PCHIP 的命名歧义。此步骤不是重建比较、任务能力实验或方法创新。仅原 11 开发/19 系列及 4 已见验证/9 系列可读；八确认患者仍拒绝。

认证项目：源 MR zip/header SHA；每个实际 DICOM 的 Patient/Study/Series/SOP/Frame UID、MONOCHROME2、单帧、Rows/Columns、IOP/IPP/PixelSpacing；逐层 RCZ 到 RAS 坐标与冻结 affine 的物理位置差 <=0.05 mm；所有原生 float32 rescaled MR 像素有限；完整像素抽取 z=0,4,8,... 后与旧 observed 数组 SHA、实际 package 内容、SOP/zip 顺序完全一致。完整 MR 与标签解码分离。

标签：从源 NIfTI 与冻结 RCZ-from-XYZ 转换验证二值、形状、前景数、标签数组 SHA。另用实际源 affine 推导整数变换并在全体体素坐标上重放标签，检查体素角点物理差 <=0.05 mm。观测层及完整源 MR 都不接受标签作为输入。native 的全体统计仅属于 native reference，禁止流入 observed 分支。

存储策略：不落盘保存任何完整 MR 副本；逐系列读取并释放，认证结果预计 <5 MB，阶段新增总存储上限 250 MB。当前只读测量空闲磁盘 10,209,808,384 字节、可用 RAM 105,640,308,736 字节。新阶段独立资源合同：磁盘保留 >=8,000,000,000 字节，RAM >=8,000,000,000 字节；单线程、自身 below-normal，单 native array <=256 MB，单 DICOM member <=8 MB。这是新有限存储阶段的合同，不覆盖旧实验 >=15GB 的 guard，不重启旧失败运行。若新的上限/保留量失败，保存失败并停止自己的步骤，不修改/删除用户或旧实验文件。

独立核验：所有 28 系列重新读真实源。对可解释的 uncompressed classic MR，核验器从原始 PixelData 字节/端序/有符号性重建每层像素，与 loader 逐层逐值对照；不只再调用同一 loader 求第二个 hash。标签用 affine 导出的坐标映射，与生产的转置/翻转路径分开。其他编码应明确失败，不跳过系列。资源审计不枚举或控制用户进程。

成功标准：28/28 系列 complete，无 errors，source/observed/label/coordinate 核验全通过，确认患者读取数和神经更新数均 0。成功只说明参照输入的来源/实现资格，不说明病灶准确率或可发表 claim。
