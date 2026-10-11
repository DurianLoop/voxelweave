# Kirby21 重复 T2w 来源门槛：论文与官方目录核读

结论：**论文层面有重复采集的 T2 加权序列，但不满足本项目“独立采集的原始 2D 切片”机制试验来源定义。** 暂不下载约 200--250 MB/Session 的影像包，也不读取像素。若另行研究 3D 采集的重定位/重建影响，可在不同预注册合同下重新评估；不能把该结果解释为 2D 邻层采集身份效应。

## 可直接核实的事实

1. Landman et al., *NeuroImage* 2011, DOI [10.1016/j.neuroimage.2010.11.047](https://doi.org/10.1016/j.neuroimage.2010.11.047) 的[归档全文](literature/source_cache/kirby21_pmc_html_2026-10-01/article.html) Methods 说明：21 名健康志愿者，10 人短协议、11 人长协议；每人两次约一小时 session，中间离开扫描室，志愿者、线圈和垫具完全重新摆位；共 42 次 session。匿名 session 号 01--42 是随机代码，**相邻编号不能直接视为一对**。
2. 同文 Table 1 把 **DTI Geometric Reference** 列为矢状位 3D 序列，名义采集分辨率三个方向均为 2 mm。表下注明带星号的序列才不在短协议；DTI Geometric Reference **没有星号**。因此论文协议设计支持它覆盖短、长两组，并随两次相同 session 重复。它不同于表中轴位多层的 qT2 mapping。
3. 同文正文的 DTI Geometric Reference 段明确称其为 **T2-weighted**、3D multi-shot turbo-spin-echo，180 张矢状层，2 x 2 mm 平面分辨率；正文还写 1 mm slice thickness、overlap 和 re-sampling factor 1。**Table 1 的 2 mm 足头方向采集分辨率与正文的 1 mm 层厚不能混作 1 mm 独立物理采集分辨率。** 原始数据是 3D Fourier 采集，不是逐层独立激发的 2D T2w。论文 Analysis 说 fMRI/DTI 对齐到各自 session 的 T2w target，但没有逐文件列出 42 套该序列。
4. NITRC [官方项目页快照](literature/source_cache/kirby21_public_metadata_2026-10-01/nitrc_project.html)及[正确文件页快照](literature/source_cache/kirby21_corrected_files_2026-10-01/page.html)对应 `group_id=313`，列出 42 个不同的 `Session 01`--`Session 42` 下载入口。先前 `group_id=324` 查询误入登录页，见[纠正记录](literature/source_cache/kirby21_corrected_files_2026-10-01/index.json)。[Session 01 HEAD 记录](literature/source_cache/kirby21_paper_access_2026-10-01/index.json)解析到 `KKI2009-01.tar.bz2`，状态 200、Content-Length 250,396,987 字节、正文读取 0 字节。下载页没有包内 NIfTI 清单、文件级采集参数或 session 到同一受试者的配对表。
5. 官方项目页内嵌 **BIRN Data License / Data Use Agreement** 全文：公众可取得数据，但文本要求有效邮箱并接受协议；不得尝试识别个人；发表时注明 BIRN、资助和相关 accession；原始数据再分发须保留同样条款，派生数据另有条件；出版后向 BIRN 提供文献引文。论文结论也说接受协议者可访问、再分发和发表。此处仅核读公开条款，**没有以用户身份接受协议、登录或下载影像**；实际下载前仍要按正式入口完成适用条款流程，且核实本项目应填的 accession。

## 与现有创新候选的关系

本项目[原始采集身份来源门槛](ACQUISITION_ID_SOURCE_GATE_2026-10-01.md)要求可核验的独立原始 2D 层及同物理层位配对。Kirby21 至多支持“同人重新摆位后的重复 3D T2w volume”线索；不提供 2D 缺层目标的真实独立邻层采集，也不能因 NIfTI 有 1 mm 切片就称存在独立 1 mm acquired slices。健康志愿者也不提供病灶任务标签。故它不升级当前[创新点备忘录](INNOVATION_DECISION_MEMO_2026-10-01.md)的机制或临床 claim。

若未来另立 **3D repeatability** 问题，先核实使用条款、包内 T2w 原始/配准版本、匿名受试者键、两次 session 对照、NIfTI shape/affine/voxel size 和来源处理记录，再冻结同人/同几何入排与重定位容忍度。第一批只做文件级和非像素头审计；若找不到可核验配对或序列只有配准/重采样版本即停。Session 01 与 02 不能事先宣称为同一受试者，也不在此阶段选作配对影像下载。

本报告的证据级别是**论文全文 + 官方网页 + 一个 HEAD**，不是文件内容核验。无 GPU、锁定 IXI test、运行中训练或患者像素读取。
