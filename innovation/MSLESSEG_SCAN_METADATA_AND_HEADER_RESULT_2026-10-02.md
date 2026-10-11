# MSLesSeg 原始 T2 来源：逐扫描核查结果

当前未认证任何可用于本项目的新原生薄层 T2 参考。完整 CSV 的 108 个已知层厚均为 2.75–5 mm；117 个 RAW T2 中读取到 110 个非像素头，最厚轴间距均为 3–6 mm。另 7 个头未取得，所以不能宣称全部 RAW 都已排除。处理包的 1 mm MNI 网格不能替代原生薄层真值。

[首轮执行前协议](MSLESSEG_SCAN_METADATA_AND_HEADER_PLAN_2026-10-02.md)、[CPU 全表联结](experiments/mslesseg_scan_metadata_gate/attempt_01.json)、[头部尝试原记录](literature/source_cache/mslesseg_raw_t2_headers_2026-10-02/attempt_01.json)、[独立复查及逐扫描联结](experiments/mslesseg_scan_metadata_gate/independent_metadata_header_verification.json)可复核。

## 全名单和参数

| 官方来源 | 扫描/文件数 | 人数 | 核查结果 |
| --- | ---: | ---: | --- |
| 处理包每一模态及 mask | 各 115 | 75 | train：P1–P53，93 时点；test：P54–P75，22 时点 |
| RAW T1/FLAIR | 各 118 | 75 | 文件目录记录；未读取这些模态的头/像素 |
| RAW T2 | 117 | 75 | 全名单预写选择，110 个头成功、7 个 TLS 失败 |
| T2 CSV | 115 | 75 | 5mm 75条、3mm 21条、4mm 10条、2.75mm 2条、NONE 7条 |
| T1 CSV | 118 个表行 | 75 | 115 个有效扫描键，末尾 3 行全空；不能称 118 个有效表记录 |

RAW T2 比处理包多 P7/T3、P17/T2、P19/T5；处理包 P19/T4 未在 RAW 中有同键文件。不能自动认定 T4=T5。test 文件名没有时点，本次只按命名推定 T1，并未认证空间映射。CSV 的 115 个 T2 键与处理包键一致。

初次临时展示误用逗号解析，发现 CSV 分隔符是分号后已纠正。正式脚本与独立复查都明确分号，保留临床无名末列及异常 RT 字符串，不推断其含义。

## 非像素头部与独立复查

首轮 HTTP range 实际传输 910,542 bytes。每个成功请求均核精确 206、Content-Range、长度和 SHA256；仅解压各 NIfTI-1 的 348 bytes 头部，未解压体素。110 个头的单位均可解释为 mm；sform 轴范数与 pixdim 最大差 4.45×10⁻⁷ mm；独立 NumPy 字节解析一致。

最厚轴间距（保留 3 位小数仅用于汇总）：3.000×16、3.667×2、4.000×1、4.400×2、4.600×2、4.800×2、5.000×5、5.500×2、6.000×78。所有已读头都不满足预写的全部空间轴 ≤1.5 mm 候选阈值。SliceThickness 与 slice-center spacing 含义不同，例如原表 5 mm 和头间距 6 mm，不能只据二者不等判数据损坏。

CSV 的 7 个 NONE 扫描在 RAW 全名单都存在，6 个头已取得，另一个仍未取得。未读取 image acquisition type、原 DICOM、标签或 mat 空间变换，所以没有原生采样与原图标签映射认证。

## 失败与补查

首轮七个 Python TLS UNEXPECTED_EOF：P1/T1、P14/T3、P20/T3、P5/T2、P58/T1、P7/T3、P73/T1，均保留完整错误。首轮没有自动重试。

随后按[单次 Schannel 替代协议](MSLESSEG_SEVEN_HEADER_SCHANNEL_FOLLOWUP_PLAN_2026-10-02.md)冻结同一七个失败成员，系统 curl 8.16.0/Schannel 全部在握手前返回 `SEC_E_NO_CREDENTIALS`、exit 35、HTTP 000、零下载。原字节 header 日志为空的事实亦保存，[补查结果](literature/source_cache/mslesseg_raw_t2_headers_2026-10-02/schannel_attempt_01.json)。没有关闭 TLS 校验、改系统凭证或反复循环请求。

这些是读取失败，不能计为厚层证据。后续若继续来源核查，可只补齐这七个同名文件的头；先前 110 个不重取。完整 ZIP MD5、成员完整 CRC 和 gzip trailer 未重算，独立审计通过不表示完整影像包已验证。

## 后续用途和门槛

MSLesSeg 可保留作真实厚层、多设备、多时点应用域候选；还需完整 RAW/注册时点清单、mat 文件/FLIRT 变换方向、源/目标 grid、标签逆映射 round-trip 和标签插值误差。在这些条件通过前，不启动 MRI 性能实验。即使以后能映射标签，也不能用配准插值图证明原生薄层重建精度。

本轮该来源新增独立确认患者数为 0。继续寻找独立原生薄层病灶来源；不替换当前 VS-SEG 固定患者名单或主要统计合同。
