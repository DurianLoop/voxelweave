# MSLesSeg 全名单参数和非像素头部核查（执行前协议）

日期：2026-10-02。目的：判断该公开来源是否能成为本项目病灶薄层 T2 的新确认候选。不是患者重建实验，不改变已冻结 VS-SEG 合同。

来源为 Figshare article 27919209 v1；已有完整 ZIP central directory 与四个官方 CSV，见 `literature/source_cache/mslesseg_public_zip_metadata_2026-10-02/attempt_01.json`。CSV 用分号分隔；逗号还出现在小数和数组内，禁止按逗号拆列。第一次临时显示使用默认分隔符产生了无效列，已识别，正式审计使用明确分号。

1. 全量读取 clinical、T1、T2、FLAIR 表，保留原字段，包括空值、NONE 和没有名称的末列。不推断临床末列含义，不修复明显异常的 RT 数字。
2. 对全部注册包和 RAW 文件按模态、患者、时间点联结。处理包 test 文件缺时间点时，只记录“按命名推定 T1”，不认证映射；不把 P19/T4 自动改为 RAW 的 T5。
3. 保存每扫描原 T2 SliceThickness、PixelSpacing、设备和缺失状况。薄层候选阈值预设为全部有效空间轴间距 ≤1.5 mm；该阈值只用于后续候选筛查，不表示获得原生采集认证。逐扫描 CSV 已见 108 个数值层厚均 ≥2.75 mm、7 个 NONE；仍核完整 RAW 名单，不能把平均层厚当逐扫描结论。
4. 非像素头核查固定为 RAW 包所有以 `_T2.nii.gz` 结束的 117 个成员，按完整成员路径排序，冻结名单/原始目录 SHA256。缺失、坏头、参数矛盾全部保留，禁止只选薄层文件。
5. 用已记录 central-directory offset 从公开 URL 请求 local ZIP header、成员名与 extra，以及 ZIP-DEFLATE 的有限前缀。单成员前缀最多 65,536 compressed bytes；预定自适应大小为 8,192、32,768、65,536，不对网络失败重试。请求总预算 16 MiB，最多三线程，timeout 30 s。服务必须返回精确 206 与 Content-Range；若不支持 range 则停止该成员，禁止整包退化下载。
6. outer ZIP DEFLATE 只产生最多 65,536 bytes 的内层 `.nii.gz` 前缀；内层 gzip 先仅解压 4 bytes，再按 sizeof_hdr 仅解压到 348（NIfTI-1）或 540（NIfTI-2）bytes。不解压 extension、体素、标签，不运行影像库/模型/GPU。保存请求原字节和仅头部字节及 SHA256。
7. 核 magic、header length、维度、空间单位、pixdim、vox_offset 和 NIfTI-1 sform 的轴范数。CSV SliceThickness 与 NIfTI 轴间距不是同一种参数；不因不同立即判文件错误。无原生序列 / acquisition type 或标签逆变换认证，即使间距薄也只列候选。
8. 不声称核验完整 ZIP MD5、成员完整 CRC 或 gzip trailer。本工作只验证请求边界、目录一致和所读头部，后续独立脚本直接重新解析已保存头/官方 CSV。

输出全部保存 `innovation/experiments/mslesseg_scan_metadata_gate/` 和 `innovation/literature/source_cache/mslesseg_raw_t2_headers_2026-10-02/`。不触及 GPU、用户训练终端、锁定 IXI test、根环境或 `.gitignore`。
