# 本阶段接续记录：MC-RC 原生头、标签与几何估计器复核

科学 goal 保持 active；这是取得来源资格证据并完成阶段归档的 progress，不是方法或发表目标完成。GPU 与用户终端训练未干预，锁定 IXI test 未读，根环境和 `.gitignore` 未修改；没有新建或委派代理。

## 已完成与结果

- 继承固定三名预选患者的九个 T2 描述系列，实际取得九个 MR ZIP 和一个官方标签 ZIP；合计 79,554,134 bytes，473 个 DICOM 对象头部已读。MR 传输包含像素字节，但 `pixel_array` 未解码；六个实际标签数组另按预写方案读取。
- 官方路径 CSV 的 487 行/15 列由 Spreadsheets 技能只读解析，并与 Python 全单元格精确比较。非 MacOS 标签包有 301 NIfTI/124 人；完整 gate 原首跑 `exit1 / complete=false`，186 个联结错误原样保留。
- 独立分项后：301 available、60 blank path、126 指定 T2 文件缺失（全为 2026 新增）；排除全部 58 名共享 VS-SEG 后，71 人/159 T2 系列有实际标签。003 三系列仍无标签。不能将目录资格当原生薄层/性能确认。
- 002 第二时间点的中位数步长 0.03mm 累计残差是估计器的坐标量化问题。追加全部 IPP 拟合，保留 0.02mm 几何、0.05mm grid 阈值和原首跑；独立完整最小二乘及逆 affine 整数变换复核通过：六条头资格、四条头+grid/两人。独立 proof `exit0 / errors=[]`，性能确认人数仍 0。
- 本次接续按已存精确 UID 来源生成下一批 004/005/006 的八个带标签系列准备 JSON；701 对象、API FileSize 385,990,404 bytes。没有为下一批发网络请求、读取新数组或启动模型。

完整解释见 [结果报告](MC_RC_NATIVE_T2_LABEL_PREFLIGHT_RESULT_2026-10-02.md)，设计判断见 [创新更新](INNOVATION_DECISION_AFTER_MC_RC_PREFLIGHT_2026-10-02.md)，来源和方法准备见 [后续计划](MC_RC_LABELLED_NATIVE_EXPANSION_PREPARATION_2026-10-02.md)。此前三篇论文重点核读见 [COBRAI/crossMoDA/Kujawa](literature/2026-10-02_cobrai_crossmoda_mc_rc_reading.md)；本次收尾没有重复下载论文或重新计算已通过的来源数组。

## 新脚本与数据

| 产物 | 内容/状态 |
| --- | --- |
| [下载脚本](literature/download_mc_rc_three_patient_headers_2026_10_02.py) | 首批有界传输与全头部读取，已执行，不重复 |
| [标签首跑](experiments/audit_mc_rc_three_patient_label_grid.py) | 全目录精确联结、六标签数组与网格检查；全库覆盖失败保留 |
| [追加核查](experiments/refine_mc_rc_geometry_and_label_availability.py) | SQLite 可用性分项、全部 IPP 拟合；已执行，事后修正 |
| [独立复核](experiments/verify_mc_rc_native_t2_label_preflight.py) | 重读 473 头、六标签，独立算法；已通过 |
| [下一批准备脚本](experiments/prepare_mc_rc_labelled_native_expansion.py) | 本次执行 exit0，仅生成来源候选，prepared_not_executed |
| [只读 CSV reader](tools/mc_rc_pathname_read_2026-10-02/read_official_mc_rc_pathnames.mjs) | 已执行；node_modules 为 bundled 只读依赖 junction，归档不递归哈希 |
| [头与请求 ledger](literature/source_cache/mc_rc_three_patient_headers_2026-10-02/attempt_01.json) | 完整请求时间/URL/响应/hash、九头提取 |
| [标签与几何结果目录](experiments/mc_rc_native_t2_label_gate) | 首跑失败、追加结果、独立 proof、后续准备 |
| [MR/标签 ZIP](data/mc_rc_three_patient_header_gate) 与 [六标签文件](data/mc_rc_three_patient_label_grid) | 本轮静态 manifest 包含这些实际数据文件 |

## 同一 CPU 队列

实际 poll session83910 成功、仍 live。进度快照见 [队列观察](literature/source_cache/mc_rc_native_queue_observation_2026-10-02.json)。固定 45 CISS + 1 TSE、335 文件合同 SHA256：`061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`。不重启、不终止，不分析动态已完成子集。主 HAT−pipeline PCHIP 双方向不改，001/202 Dice 改善仍为反证。

全部推断后驱动器自动重建再生成、保存输出独立复核及完整主分析；之后才执行 selection sensitivity。原队列/旧 live stage 保持历史 snapshot，本阶段 manifest 不锁实时预测或日志。

## 归档与未完成工作

[本阶段静态核验脚本](literature/verify_mc_rc_native_stage_archive.py)核计划/脚本/来源与数据 hash、473 头记录和六标签 proof、完整 CSV/ZIP/API 可用性分项、下一批未执行属性及原失败。它是档案/来源证据核验，不是再次患者模型推断。更新 README 后刷新五个依赖 README 的旧静态 stage，再 write/read-only 本 stage 和全局检查；[核验记录](SESSION_ARCHIVE_VERIFICATION_MC_RC_NATIVE_2026-10-02.json)保存实际命令、返回码、stdout/stderr及失败，不以保存记录推断科学成功。

静态核验首跑发现新脚本错误地将冻结合同内项目根目录的 46 个源码路径要求位于 innovation，返回 exit1。这是归档路径范围错误，并非源码 hash 改变或新的数据失败。已保留 [失败脚本](experiments/mc_rc_native_t2_label_gate/archive_verifier_failed_attempt_01.py)、[首跑 manifest](experiments/mc_rc_native_t2_label_gate/archive_manifest_failed_attempt_01.json)和核验记录的历史 attempt；修正为仅对冻结合同明列源码允许项目根目录的只读 hash 核查，不修改源码。五个旧静态 stage 首跑 write/read-only 均已通过；修正后只复查受影响的 action、本 stage 和全局归档。

本阶段用户请求、公开更新和交接原文见 [对话归档](SESSION_VISIBLE_DIALOGUE_MC_RC_NATIVE_2026-10-02.md)与 [用户交接保存件](USER_PROVIDED_HANDOFF_MC_RC_NATIVE_2026-10-02.md)。下一轮从 [接续入口](SESSION_HANDOFF_MC_RC_NATIVE_QUEUE_ACTIVE_2026-10-02.md)继续同一队列和源资格工作。尚需新批次完整来源检查、多开发病例 oracle、训练对照/预算、冻结患者分组和未见确认；目前没有可发表 claim。
