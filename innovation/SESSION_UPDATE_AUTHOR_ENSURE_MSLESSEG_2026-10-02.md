# 本轮更新：作者代码/长稿核读、动作排序审计与新来源资格

科学目标仍 active，阶段是 progress，尚无可发表且独立验证的 claim。唯一 MRI 长任务是 session 83910 的既有 CPU 队列；没有重启、终止或另起高负载推断。阶段记录不评分动态子集。

## 论文与公开材料

- 精确 DOI 的 GitHub 搜索找到 midas-tum/recon_uncertainty；API ref 限流后改读匿名 HTML，固定提交 ce0e6ede3682a6901bfdd6ddc85b44ef28e72f3a。保存 README、训练入口、dataset、loss 和模型配置，静态阅读，没有执行作者代码。Küstner 正文仍未取得。
- ENSURE 长稿由会议正文 reference21 指向 arXiv:2010.10631；v1 PDF 406 原响应保留，abs 指明 v4，HTML 成功。正式 TMI DOI 10.1109/TMI.2022.3224359、2023/PMC10210546 有元数据认证。核方法/证明/实现/实验/讨论，原文自身写 mask 依赖近似，不能称新漏洞。
- MSLesSeg DOI 10.1038/s41597-025-05250-y / PMC12126551 JATS 及官方 Figshare v1、README、预处理代码取得。核 23 段正文/表图文字，未逐图观察；处理后 1mm 网格不是原生薄层。正文 test22/test24 矛盾由官方完整目录核为实际22，历史矛盾保留。
- MSSEG-2 / crossMoDA 扩展仍为检索/摘要候选，未将其计入新增全文或独立数据认证。检索返回157等数字不是全文数。

[新意边界与阅读笔记](literature/2026-10-02_author_code_ensure_long_and_mslesseg_reading.md)。来源目录含原响应、DOI/提交、失败、时间、SHA256。新增两份正文，不增加 PDF 注册数。

## 实际 CPU 探索

[动作排序审计](MASK_DEPENDENT_ACTION_RANKING_CPU_RESULT_2026-10-02.md)：执行前写完整网格，81 场景/972 风险/5,346 比较/324 控制；548 严格反号、1,458 加权并列。全部协方差差分恒等式、独立评价 mask 和固定常数对照通过；独立 Fraction 闭式最大差8.88e−16。非 MRI 模型、患者结果或新定理。

[MSLesSeg 全表与头部审计](MSLESSEG_SCAN_METADATA_AND_HEADER_RESULT_2026-10-02.md)：完整处理目录115扫描/75人、RAW T2 117；CSV108已知T2层厚≥2.75mm、7 NONE；110头成功，最厚轴3–6mm，未读像素。独立 NumPy 解析、哈希、Range边界和完整名单检查通过；7头因TLS未取得，不能称全量成功。Schannel一次替代读取因SEC_E_NO_CREDENTIALS全失败/零下载，保留具体原因。不做无依据的T4→T5映射。

[后续创新准备](ACTION_BENEFIT_INNOVATION_FOLLOWUP_2026-10-02.md)：优先有真值固定动作收益开发诊断，门槛为动作空间和病灶守卫，再同预算与绝对误差头比较。无真值路线需真实算子/独立观测/噪声，MSLesSeg尚无原生薄层确认。

## 执行错误和来源失败

- 临时读取PowerShell默认encoding造成中文乱码，正式读取/脚本均UTF-8；临时CSV默认逗号误分，正式审计与独立复查均用分号。未把失败显示当科学结果。
- earlier来源脚本的OpenAlex case重复键使用Python JSON处理，GBK非断空格改stdout UTF-8；大批输出截断后分块读，阅读范围明确。
- GitHub API403、arXiv v1PDF406、七Python TLS EOF、七Schannel凭证错误均保存。未关闭TLS校验/改系统配置/安装依赖。未取得材料明确留后续。

## 活跃队列与边界

冻结合同061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5：335引用，45 CISS+1 TSE，七条件，HAT−pipeline PCHIP两主要方向。最新工作时快照18/45已完成七条件、第222人继续推断；接续文件另存最后观察时间。全部推断结束后自动逐患者再生成核验及主统计。001/202 Dice改善仍反证。

未接触GPU、用户终端训练、锁定IXI test、根环境/.gitignore；未新建或委派代理。目录/metadata传输了压缩字节，NIfTI只解码header，不能称完全未接触影像文件。新确认患者数0。

## 归档

[可见对话](SESSION_VISIBLE_DIALOGUE_AUTHOR_ENSURE_MSLESSEG_2026-10-02.md)保存本轮用户请求和公开回复，引用接续摘要中的此前消息并注明来源。[接续入口](SESSION_HANDOFF_AUTHOR_ENSURE_MSLESSEG_QUEUE_ACTIVE_2026-10-02.md)保存唯一活跃handle和后续步骤。新增静态stage verifier在 `literature/verify_author_ensure_mslesseg_stage_archive.py`；动态MRI队列不纳入最终静态校验。

静态stage的write/read-only检查及此前三个受README变更影响的stage检查全部通过；全局write/read-only快照为29注册PDF、1745 evidence、1702本地链接、零错误。核验记录保存于 `SESSION_ARCHIVE_VERIFICATION_AUTHOR_ENSURE_MSLESSEG_2026-10-02.json`。本轮的两份正文、作者代码层级、110/117头部、7未取与scientific确认患者0的边界均纳入核验；没有把来源失败伪装成全量成功。
