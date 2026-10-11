# 本轮续作记录：官方两文件访问与任务级全文排重

用户要求在 GPU 正被占用时继续批量阅读 MRI 论文、结合现有项目找创新点，能验证的先做，不能验证的记录后续条件，并将本轮内容归档在 `D:\MRI\innovation`。本记录承接此前[会话与论文归档导航](README.md)，不是替代前面各次完整记录。本次没有碰训练终端/GPU、锁定 IXI test 图像、已有 `.gitignore` 修改或系统安装。研究目标仍是形成可经审稿的发表 claim，当前保持未完成。

## 已有证据定位

- 项目是单 T2 的 x4 缺失层重建。当前最强可审的 MIRA 结果是固定 IXI HAT/SwinIR 模型对、同一目标和参考下切换发布层邻片伙伴上下文时的回顾性成对误差可见性：MSValid 84 人/479 目标 `Delta O=+24.1856` 点，ReMIND 62/248 `+26.3999` 点，后续 UPENN 派生 DICOM 374/1,496 `+28.1156` 点。见[第三来源结果](UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md)、[内稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)和[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)。三来源不能解释为原始采集身份机制、临床安全或重建 MSE 改善；线性伙伴等负对照已排除“跨深度架构特有”宽解释。
- 已有[论文阅读导航](README.md)与[创新决策表](INNOVATION_DECISION_MEMO_2026-10-01.md)记录插值、扩散、MRI 误差估计和任务先例。Verschuur 2022 已覆盖 T2 插值/分割，Kuestner 2024 仍只有正式摘要；窄新意不是全球首创证书。当前最值得新增的证据是可靠同空间标签或真正独立同几何采集，而不是继续累积无标签阳性 DICOM 队列。
- UPENN 官方公开包目录有 671 个结构像扫描目录，与官方 CSV 完全匹配；CSV 的 232 个修订分割标记中，包内 `images_segm` 只有 147 个候选链接，薄层 T2 元数据候选 60 个。首例 `UPENN-GBM-00002_11` 的 T2 和修订分割只有文件名/体积级证明；atlas NIfTI 标签与现有 DICOM 按官方说明不对齐，不能跨发布物回填。

## 本次可执行验证

1. 从 IBM 官方 Connect 下载页取得签名有效的 4.2.19.956 Windows MSI，以只读 Windows Installer API 提取 CAB，再提取便携 `ascp`、支持 DLL、随包密钥与许可文件。未运行 MSI 安装、未改系统环境。[来源/哈希及试验细节](UPENN_ASPERA_TWO_FILE_ACCESS_RESULT_2026-10-01.md)已归档。
2. 官方 Faspex 公开授权流对**冻结的两条文件路径**返回 `connect` 规格；逐字比较包根与两条完整路径，限制本地 10 MB、120 秒、5 Mbps。此前 HTTP-gateway 规格有 `zip_required=true`，这次 `connect` 规格为 `null` 且把包根嵌入每条 `source`；仅报告此格式差异，不推断 zip 的服务端语义。[v1 至 v9 的非敏感阶段记录](literature/source_cache/upenn_gbm_two_file_ascp_pilot_v9_2026-10-01.json)保留了校验、Windows CLI 参数修正、许可缺失修正和最终结果。最终 `ascp` 经认证阶段退出 1、零文件/零字节。临时 token/cookie 未进命令行、报告或文件；自动诊断日志已清理。认证失败原因未定，不能据此推论符号链接坏或标签不存在。
3. 因未取得 NIfTI，事前规定的前 352 字节 gzip 头、shape/affine、同网格检查均**未执行**，更未读患者像素或计算病灶终点。正式后续仅在取得 IBM 文档支持的规格消费方式并仍能限制两文件时重试，随后按[预写方案](UPENN_NIFTI_OFFICIAL_INVENTORY_AND_PILOT_PLAN_2026-10-01.md)做头部检查。临床任务协议需要以实际可读且同网格的扫描重新冻结分母。

## 本次论文核读与创新点变化

公开[全文](literature/source_cache/segmentation_guided_mri_2026-10-01/article.html)使 Morshuis、Hein、Baumgartner 2024 从摘要级升为方法/结果级先例。其 SKM-TEA 膝 MRI 固定欠采样 k-space 下，分割梯度引导同一个扩散模型产生上下界重建；每个加速因子分析 869 层。16x 时下界 precision/上界 recall 为 0.980/0.990，重复重建为 0.951/0.957，SSIM 两者近似相同。完整[碰撞审计](literature/2026-10-01_segmentation_guided_mri_fulltext_result.md)确认它不是 MIRA 的发布层邻片切换，但进一步否定“首次通过多重 MRI 重建揭示分割不确定性”宽主张。仍未取得 Kuestner 2024 方法全文，不能声称完全排重。

进一步取得[Fischer、Kuestner、Baumgartner 2023 公开预印本全文](literature/2026-10-01_fischer_mri_uq_fulltext_result.md)：PHiRec 在固定 SKM-TEA 膝关节欠采样 k-space 上抽样 20 个重建，经分割 U-Net 传播并比较分割方差图与误差图，另有加速倍率分布外实验。它是更早且更直接的任务误差先例，排除宽泛“重建分歧首次提示分割错误”主张；它仍非发布层邻片切换。其图中 NCC 数值没有被本次文本抽取独立量化，不能编造效应大小。Kuestner 2024 是另篇论文，依然只有摘要。

当前优先级不变：第一是带完整负结果和来源边界的发布层成对误差审计；第二是另寻有原始独立同几何采集证据的数据源；第三是只有取得同空间真实标签后才启动的任务终点实验。UPENN 两文件认证失败是访问门槛，不是临床/统计阴性结果。五页旧 PDF 仍是两来源快照，英文三来源 Markdown 内稿仍非正式投稿包。IXI 衍生权重分发权限、作者/场合确认、干净环境复现与 Kuestner 方法级查新仍未关闭。

本次新增的脚本、非敏感规格摘要、IBM 厂商包/便携文件、访问结果、公开全文及审计均在本目录。归档一致性以[清单](literature/archive_manifest.json)和 `python innovation/verify_archive.py` 的最终复核为准。

最终只读复核：29 份 PDF、236 个证据文件、1,071 个本地链接、零错误；三个新增 Python 脚本均通过 AST 语法解析。便携目录没有传输诊断日志，受控影像目录为空。所有后续事项仍按未完成门槛记录。
