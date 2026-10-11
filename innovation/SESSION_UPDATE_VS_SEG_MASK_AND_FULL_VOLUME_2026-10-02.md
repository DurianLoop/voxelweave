# 本轮会话归档：标注转换、方法全文及完整体积 CPU 探索

用户继续要求基于既有 MRI 项目批量读论文、寻找创新点；GPU 已占用，可验证的先做 CPU 探索，不能验证的保存依据和后续准备，全部内容放在 D:\MRI\innovation。既有持续目标为“直到达成一个可发表的 claim，不动当前终端训练”。本阶段取得实质进展，但该发表目标仍未完成、未阻塞，不更新为 complete。

主要入口是 [本轮完整结果](VS_SEG_ORIGINAL_MASK_AND_FULL_VOLUME_CPU_RESULT_2026-10-02.md)、[论文/新意矩阵](literature/2026-10-02_vs_seg_model_method_and_label_novelty_audit.md)、[正式队列设计草案](VS_SEG_FULL_VOLUME_TASK_DESIGN_DRAFT_2026-10-02.md)和[可见对话原文](SESSION_VISIBLE_DIALOGUE_VS_SEG_MASK_2026-10-02.md)。用户提供的上一模型交接见[交接记录](SESSION_HANDOFF_VS_SEG_MASK_RAW_2026-10-02.md)；它描述的是本轮开始时状态，不代表最终结果。更早可见会话仍见 [既有记录](SESSION_VISIBLE_DIALOGUE_VS_SEG_2026-10-01_TO_02.md)。

本轮没有联系任何论文作者或他人，没有创建/委派子代理，没有运行 Git 同步，没有改 .gitignore/environment.yml，没有给当前训练进程发命令，没有读锁定 IXI test。Python 使用既有 MRI 环境执行分析；Slicer/旧 MONAI 依赖全部在 innovation/tools 独立解包或进程内兼容。文件写入均在 innovation。

| 工作及证据 | 成功与失败都保留的位置 |
| --- | --- |
| 官方扩展 API 参数核查 | literature/probe_vs_seg_slicerrt_matching_catalog.py；source_cache/vs_seg_original_mask_routes_2026-10-02 的 JS、baseName/noarch/revision 查询及索引。错误的 extension_name 空响应保留 |
| 官方 Slicer/SlicerRT 包认证 | literature/stage_vs_seg_slicer_cpu_packages.py；tools/vs_seg_slicer_cpu/download_attempt_01.json。SHA512 均通过；未运行安装器 |
| 解包与真实大小审计 | literature/unpack_vs_seg_slicer_cpu_packages.py、audit_vs_seg_slicer_unpacked_runtime.py。attempt_01 因空 Size 转 int 失败，attempt_02 解包成功但旧 size 仅计已知 NSIS entry；runtime_manifest 明确纠正实际 1.2226 GB，旧报告保留，后续未知大小预留全 3 GB |
| 独立 PythonSlicer 类加载 | experiments/vs_seg_slicer_cpu_runtime_probe/attempt_01.json；无 GUI/渲染，VTK 单线程 |
| 固定开发输入准备 | data/vs_seg_original_mask_development/prepare_attempt_01/02/03.json。第一次 182 JSON 请求使用了错误仓库 URL 得到 404；改从已固定树的真实仓库取得并验证 Git blob。第三次完整结构输入单独保留，不覆盖前两次的输入 |
| 固定 001/182 的原始掩膜 | experiments/vs_seg_original_mask_cpu_development/attempt_01/02 因当前 MRML 包装模块/类名不同而失败；attempt_03 成功。作者 helper 未改。原开发脚本按当时 SHA256 存 development_converter_v1_snapshot.py 后，才加入通用输入/输出参数 |
| 独立坐标与历史预测参照核验 | experiments/verify_vs_seg_original_mask_development.py；JSON 验证零错误，两例平面 RT 掩膜零体素差；001 复用旧预测重新评分，未新推断 |
| MONAI list→tuple 等价性 | experiments/vs_seg_001_sliding_window_tuple_equivalence.py、vs_seg_001_tuple_equivalence/attempt_01.json。四处索引替换，完整 logits 逐位相同，CUDA false |
| 七条件完整体积 CPU 预检 | VS_SEG_001_FULL_VOLUME_CPU_PREFLIGHT_PROTOCOL_2026-10-02.md；experiments/vs_seg_001_full_volume_cpu_preflight/attempt_01.json、全部 volume/prediction、逐层误差与独立验证。约 292 秒，七条件完成；开发病例不是独立确认 |
| 全 46 人头部及原始标签来源 | literature/qualify_vs_seg_full_volume_heldout_sources.py；source_cache/vs_seg_full_volume_source_gate_2026-10-02/attempt_01.json；data/vs_seg_full_volume_heldout_source。46/46 完成，45 CISS + 1 TSE，未解码图像像素或运行任务模型 |
| 全 46 人转换和复核 | experiments/vs_seg_full_volume_source_masks 两次转换、全部掩膜及 independent_source_geometry_verification.json。第一次 PowerShell 工具返回 status 1，但 JSON 已完整成功；保留原 log。改为 Python subprocess 捕获原生返回码后，返回 0，全部重复 mask SHA256 相同。stderr 仅含 deprecated representation name/缺显示色表的警告，不影响体素转换 |
| 方法全文与访问失败 | source_cache/vs_seg_original_mask_routes_2026-10-02 中 Wang 正式 PDF、页面渲染及正文，Shapey BioC/XML/正文、DOI/PMC/arXiv 原查询和索引。Europe PMC XML 500、PDF 403 保留；BioC 成功。MRI 环境没有 pypdf，改用已有 Poppler；MiKTeX 用户日志写入被沙箱拒绝，但读取/渲染成功，未改环境 |
| 假设效应量与后续准备 | experiments/vs_seg_full_volume_design_power_2026-10-02.json；完整设计草案。没有用 45 人任务分数估计方差，没有伪称联合 power 或已经预注册/完成主检验 |

所有新影像模型执行都明确 CPU，并记录 CUDA 未初始化；VTK 不创建 renderer/render window，也不启动 SlicerApp-real。只降低新建研究进程本身的优先级。当前磁盘仍高于 15 GB 底线。没有遗留研究命令在后台运行。

下一阶段必须先实现通用 46 人队列运行器、边界敏感性和统计代码，审核并冻结新协议/代码/输入合同，再运行独立任务研究。不能把旧 >=100 例门槛改为 45 后称旧确认成功；不能以 001 某个参照/汇总下的负分割差筛选新的主比较。正式队列可能需要约 8–10 小时 CPU，这是准备估计，不是实测结果。

本阶段档案使用 literature/verify_vs_seg_stage_archive.py 和 verify_archive.py 依次 write/verify。全局原 29 篇 PDF 的注册计数不含本轮位于 source_cache 的正式方法 PDF 响应；新增全文按 new_method_fulltext_reading_index.json 和全局 evidence hashes 核验，不偷换全文数量。
