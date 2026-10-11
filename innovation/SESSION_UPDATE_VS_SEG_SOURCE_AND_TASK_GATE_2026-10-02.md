# 本轮会话续作记录：VS-SEG 标签、目标数和任务模型

用户要求继续基于MRI既有工作批量读论文找创新，GPU被当前终端训练占用；可用CPU或元数据验证的先做，不能验证的记录并准备，所有本轮内容留在D:\MRI\innovation。持续目标是“一直研究探索验证下去，直到达成一个可发表的claim，注意不要动我现在终端训练的进程”。本轮开始时的上一目标回合分类为 progress：已完成242例标签审计、来源获取和单例预检；本回合也产生了改变后续行动的独立反证和实际CPU模型结果，不能判作阻塞或完成。

可见用户消息与助手进展更新原文见 [对话记录](SESSION_VISIBLE_DIALOGUE_VS_SEG_2026-10-01_TO_02.md)。自动压缩前的逐字工具转录不可由当前上下文恢复；既有脚本/结果及交接事实按证据文件保留，不编造丢失的转录。当前工具执行的科学结果、失败和源码以以下索引及逐次JSON记录。

| 工作 | 执行和结果 | 可复核记录 |
| --- | --- | --- |
| VS-SEG 初始来源、两系列头部、轮廓与标签小试 | 当前映射242，NBIA T2 241，缺133；001为384×384×80、3D、1.5mm。TV13条、7,505体素；四目标17/21/19/23 | [来源清单](literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json)、[头部](literature/source_cache/vs_seg_001_two_series_headers_2026-10-01/index.json)、[轮廓](literature/source_cache/vs_seg_001_contour_geometry_2026-10-01.json)、[像素小试](experiments/vs_seg_001_label_pixel_feasibility/result.json) |
| 旧模型预检和中止批次 | 001 HAT病灶均值0.00295866、pipeline PCHIP 0.00320356，不支持原方向。前14例仅1完成、6名称失败、6目标不足、1间距失败；没有完整队列结论 | [预检](experiments/vs_seg_001_model_preflight.json)、[逐例记录](experiments/vs_seg_thin3d_model_confirmation/cases)、[未改的协议](VS_SEG_THIN3D_MODEL_CONFIRMATION_PROTOCOL_2026-10-01.md) |
| 全部标签名称与作者首结构规则 | 242/242 RTSTRUCT非像素审计；抓固定Git树、3转换脚本、3说明、6原始T2轮廓例。首结构规则有代码依据，Men两例语义仍未核清 | [标签审计](literature/source_cache/vs_seg_rtstruct_labels_2026-10-01/summary.json)、[作者来源](literature/source_cache/vs_seg_author_code_2026-10-01/index.json) |
| 原目标规则的非像素上界 | 第一实现239例最多95；独立实现包括全部242、取消边缘限制，最多96，零未知，不能达到原100门槛 | [第一实现](experiments/vs_seg_nonpixel_target_upper_bound_2026-10-01.json)、[独立实现](experiments/vs_seg_target_bound_independent_2026-10-02.json) |
| 010间距复核 | 实际均匀1.5mm；原比较被1.500000000000007误触发 | [头部复核](experiments/vs_seg_010_header_spacing_check_2026-10-01.json) |
| 官方任务权重和名单 | DOI6323472公开CC BY4.0 T2 ZIP35,275,354字节，MD5通过。两日志与CSV176/20/46逐人完全一致；46 test全在公开清单，零前14例重叠，45CISS/1TSE，旧规则最多覆盖22 | [元数据/源码](literature/source_cache/vs_seg_task_model_sources_2026-10-02/index.json)、[档案日志](literature/source_cache/vs_seg_t2_release_logs_2026-10-02/index.json)、[名单复核](literature/source_cache/vs_seg_t2_release_logs_2026-10-02/split_verification.json) |
| CPU兼容性 | 官方MONAI wheel和作者网络本地隔离，Git/PyPI哈希通过；小输入严格权重加载、重复差0；官方大小单线程10.37秒/峰值5.91GB/无CUDA初始化 | [依赖清单](literature/source_cache/vs_seg_cpu_compat_sources_2026-10-02/index.json)、[失败1](experiments/vs_seg_cpu_compatibility_probe/attempt_01.json)、[成功2](experiments/vs_seg_cpu_compatibility_probe/attempt_02.json)、[整窗3](experiments/vs_seg_cpu_compatibility_probe/attempt_03.json) |
| 已见训练病例001原生影像任务预检 | RAS轴变换无插值，原版NormalizeIntensity与Gaussian滑窗CPU可运行；对RTSTRUCT平面掩膜Dice0.9590317。原JSON14轮廓离原生平面最远0.59972mm，不能做最近层替代SlicerRT | [冻结单例协议](VS_SEG_001_NATIVE_TASK_PREFLIGHT_PROTOCOL_2026-10-02.md)、[实际记录](experiments/vs_seg_001_native_task_preflight/attempt_01.json)、[输出分割](experiments/vs_seg_001_native_task_preflight/prediction_attempt_01.npz) |
| 论文复核与创新收缩 | 复核已缓存VS-SEG、CrossMoDA、Gazi、UCSF术后FLAIR、7T五篇全文；延续Fischer/Morshuis任务先例约束。尚无新独立重建任务阳性 | [阅读矩阵](literature/2026-10-02_vs_seg_source_task_reading_matrix.md)、[新任务准备](VS_SEG_FULL_VOLUME_TASK_STUDY_PREPARATION_2026-10-02.md) |

保留的技术失败包括：初始Git树超过1MB上限（提高受控上限后成功）；重复请求遭GitHub403速率限制（改用已固定的缓存树）；004原始JSON552,131字节超过500KB上限（以已知大小改1MB上限）；旧001 ZIP内LICENSE解析错误与把Skull越界当病灶失败（此前原失败保留）；日志名单解析首次匹配“Number of images ... =176”造成int不可迭代（只匹配列表行后修复）；MONAI首次导入使用已移除的FileFinder.find_module（进程内API兼容后成功）。Windows CIM内存读取被拒，未申请提权，后续Windows内存状态API在普通权限下读到约108GB可用内存。当前MONAI滑窗对列表多维索引有弃用警告，已列入后续等价性验证。没有自动审批拒绝或待授权动作。

阶段归档检查首次还发现两个核验实现错误：把每例的run_contract.json哈希直接与协议文件哈希比较，以及Windows文本写入把新增v1方案快照的LF转为CRLF。已分别改为核验run_contract及其各输入、按原始UTF-8字节保存快照；旧研究协议、批次脚本和逐例结果均未改写。该失败不代表科学数据或旧实验合同发生变化。

本轮所有写入位于innovation。未向作者或其他人发送消息，没有新建子代理，没有改变用户MRI环境、.gitignore、当前训练参数或训练进程，没有读取锁定IXI test。新脚本固定CPU、单线程、内存/磁盘底线；所有新进程在本记录形成时已返回终态，没有遗留研究作业等待轮询。

当前未完成的实质门槛：原JSON+SlicerRT掩膜复现；滑窗tuple索引等价性；独立队列原生基线和完整体积重建任务结果；患者统计与边界/序列稳健性；近邻先例排重与发布复现。不能用软件通过或归档通过声称可发表目标完成。

归档复核命令为 `D:\conda\envs\MRI\python.exe -B innovation\literature\verify_vs_seg_stage_archive.py --write` 后不带`--write`复核，以及 `D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py --write` 后不带`--write`复核。前者覆盖VS-SEG阶段方案/脚本/结果/来源，后者覆盖全局注册PDF、阅读证据与Markdown链接；它们不证明临床结果或新颖性。
