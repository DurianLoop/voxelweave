# 本次续作：UPENN 标签空间与三来源内部稿

目标仍是形成可发表、经审稿人核查的 MRI 创新主张。上一轮四种子文献/标注目录核查带来新证据，本轮继续检查临床任务来源并同步内部稿；没有占用 GPU、操作终端训练进程、读取锁定 IXI test 或新增患者推理。

1. [UPENN 官方页面缓存](literature/source_cache/upenn_gbm_collection_page_2026-10-01.html)含提交者明确说明：专家修订标签与 SRI atlas 配准 NIfTI 对齐，NIfTI 与 DICOM 按设计不对齐。[来源判定](UPENN_GBM_LABEL_ALIGNMENT_GATE_RESULT_2026-10-01.md)因此拒绝将 NIfTI 标签直接赋给现有处理后 DICOM 的 374 人、1,496 目标。首个在线 NBIA SEG 查询因系统代理连接拒绝；绕过代理的[原始响应复核](literature/source_cache/upenn_gbm_label_routes_2026-10-01/index.json)返回空 SEG 正文，而无模态过滤的 3,680 套均为 MR，UID 集合与冻结 MR 清单相同。该 NBIA 清单不含 DICOM SEG，但不能否定单独发布的 NIfTI 标签。若要使用标签，先取得可核的空间变换或另起 NIfTI 合同。
2. [新三来源量化图](figures/PUBLIC_THREE_SOURCE_FIGURE_NOTE_2026-10-01.md)仅读 MSValid、ReMIND、UPENN 的冻结逐患者 CSV 与摘要，不含患者 ID/影像。绘图器逐来源核对人数、目标数和 Delta O 均值并存源哈希；PNG 已目视检查，三面板统一纵轴且无裁切。三来源分别为 84/479、62/248、374/1,496；不能合并成三次独立盲确认。
3. [英文内部稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)标题、摘要、第三来源方法/结果/限制、正式 UPENN 数据引文、两篇任务级全文先例和新图已更新。UPENN 处理后、结果前冻结但受前两来源阳性信息影响，且配对 MSE 未改善；临床、安全、部署与原始采集身份均未主张。旧五页 PDF 仍是两来源历史快照，未同步为投稿产物。
4. [创新优先级](INNOVATION_DECISION_MEMO_2026-10-01.md)、[临床标签来源门槛](CLINICAL_TASK_LABEL_SOURCE_GATE_2026-10-01.md)和[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)已同步。下一条关键科学证据仍需独立原始重复采集或能真实映射到目标平面的权威标签；Kuestner 2024 原文与正式投稿的权重许可、环境复现和作者审批也未关闭。

5. [官方 UPENN 可用性与采集参数 CSV](literature/source_cache/upenn_gbm_label_availability_2026-10-01/index.json)已按原始字节、URL、哈希归档，671 个扫描 ID 在两表完全一致。人工修订分割可用的 232 条均为后缀 _11 的不同受试者；与 DICOM 374 人仅有 114 个**受试者前缀**相交，未证明同一扫描或空间。条件性的[atlas NIfTI 新实验门槛](UPENN_GBM_NIFTI_LABEL_FEASIBILITY_RESULT_2026-10-01.md)已写下；官网 Aspera NIfTI/分割包约 69 GB，当前仅核 HTML 访问入口，未下载包或读像素。

6. 上述 232 条中 86 条 T2 厚度约 0.9 mm，缓存 NBIA 清单为其 83 人找到相应 192 层 T2 SAG SPACE 处理后系列。[事前选首例非像素计划](UPENN_GBM_THIN_T2_HEADER_PILOT_PLAN_2026-10-01.md)及[完整结果](UPENN_GBM_THIN_T2_HEADER_PILOT_RESULT_2026-10-01.md)得到 192/192 个派生/次级 3D 头、物理层距约 0.9 mm、无来源影像链；独立只读 ZIP/UID/几何复核 PASS。仅下载约 7.88 MB 官方 ZIP 到已忽略数据目录，未解码像素。这保留“发布层薄网格”线索，同时否定本例原始薄层身份捷径。

7. 官方 69 GB NIfTI/分割 Aspera 链接的只读 HEAD/GET 仅给网页应用 HTML；尝试的公开 API 路径返回 404，既无目录也无文件级小样本，不能据此断言官方包无法访问。本地无 Aspera 客户端，未下载大包。已归档 NBIA 清单中上述 86 人可识别的 83 套字面 T2 非 FLAIR 系列全是 Processed_CaPTk，无另外一套字面原始 T2；命名筛查不排除非常规名称或库外源数据。

8. 查官方 Aspera 网页脚本可见 API v5 包文件目录调用；未带会话授权的只读请求返回 HTTP 401 并要求授权头。此结果只表明直接 API 目录受限，不代表通过正式公开链接的授权浏览器/客户端无法列目录。本轮未绕过授权或启动 69 GB 下载。

9. [三来源复现补充材料](PUBLIC_ONLY_REPRODUCIBILITY_SUPPLEMENT_2026-10-01.md)与[发布/引文门槛](PUBLIC_SOURCE_RELEASE_CITATION_AUDIT_2026-10-01.md)已补入 UPENN 正式引文、第三来源冻结合同、源哈希、双复核命令和旧 PDF 状态；仍不声称可分发权重或全新环境复现。两套 UPENN 只读核验已重跑 PASS：374 套 ZIP/23,702 头均复核，统计重得 374 人/1,496 目标、Delta O=0.2811561514882688、患者区间 [0.2790058845438479, 0.28330885896901115]。没有加载 GPU 或目标影像像素。

归档校验、输入哈希与链接检查以最终的 [来源清单](literature/archive_manifest.json)和图的[输入清单](figures/public_three_source_observability_sources.json)为准。本次没有把缺少同空间标签的资料包装成病灶终点。
