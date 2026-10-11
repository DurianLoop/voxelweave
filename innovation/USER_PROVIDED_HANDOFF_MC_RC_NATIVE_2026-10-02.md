# 用户提供的本阶段交接摘要

以下保存接续时用户提供的摘要原文；这是历史状态材料，实时进度以新快照为准。

## 目标与约束

科学目标仍 **active，未达成**：继续研究与验证，直到形成可发表且独立验证的 claim。本轮属于 **progress**，新增了真实来源与几何证据；用户此刻要求 checkpoint，不是暂停目标。

- 目录 `D:\MRI`，PowerShell，Python `D:\conda\envs\MRI\python.exe`。
- 不使用 GPU、不干预用户终端训练、不读取锁定 IXI test、不改根环境或 `.gitignore`。
- 不新建/委派代理；公开读取和 CPU 探索已授权。
- 新证据、代码、失败、后续准备、公开对话都要保存到 `innovation`。
- 本轮新工作尚未完成阶段文档/对话归档/manifest 收尾。

## 唯一活跃长任务

继续同一个 unified exec **session `83910`**：

```text
D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py
```

最近实际 poll 成功、确认 live；日志 **27/45 人完成七条件（189 conditions），VS-SEG-231七条件完成**。先再次实际 poll，不重启或终止。

- 状态/日志：`experiments/vs_seg_full_volume_queue/`
- 冻结合同 SHA256：
  `061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`
- 45 CISS +1 TSE、335引用；主要 HAT−pipeline PCHIP 两方向不变。
- 不评分动态子集、不改挑 SwinIR。
- 全推断后自动 regenerate 和完整主分析，再跑 `vs_seg_selection_sensitivity.py`。
- 两主患者 CI 上限均 <0 才支持原联合方向；001/202 HAT Dice 改善仍是反证。
- 新下载 session **65690 已结束 exit0**，不要再 poll；其他新工具全部结束。

## 上一轮已收尾

入口：`SESSION_HANDOFF_ACTION_CROSSMODA_QUEUE_ACTIVE_2026-10-02.md`。

上一轮成果：COBRAI/crossMoDA2026/Kujawa2024重点核读，MC-RC v2 全目录及患者身份审计。COBRAI需要完整参考，真正无完整图像参考的选择路径是 ACS 留出 k-space MSE。优先方向仍为固定预算下预测局部动作净收益并保持病灶表现，当前不训练收益头。

全局最后通过：**29主注册PDF、1797 evidence、1745本地链接**，新增作者PDF在嵌套 source_cache，不计入29。五个静态stage（含 action_crossmoda）均已核；现在新增文件后全局manifest需要刷新。README本轮尚未修改。

## 本轮实际新增工作

### 1. 九条真实 MR 全系列头部取得

预选沿用上一轮固定的 **VS-MC-RC-001/002/003全部9条T2描述系列**，不是按性能选病例。

新计划/脚本：

- `MC_RC_THREE_PATIENT_NATIVE_HEADER_PLAN_2026-10-02.md`
- `literature/download_mc_rc_three_patient_headers_2026_10_02.py`

结果：

- `literature/source_cache/mc_rc_three_patient_headers_2026-10-02/attempt_01.json`
- MR/官方标签ZIP在 `data/mc_rc_three_patient_header_gate/`
- 9系列、**473 DICOM对象**，全部头读完。
- 总传输 **79,554,134 bytes**，上限300MB。
- **下载包含MR像素字节，但没有解码任何MR pixel_array**；不能称非像素下载。
- 初始头资格5条；2条明确DERIVED/MPR，1条缺MRAcquisitionType，1条被中位数步长算法误判几何不规则。

### 2. 官方路径表实际是 CSV，已用技能只读解析

已告知使用并读取 Spreadsheets skill：

`C:/Users/user/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.904.11930/skills/spreadsheets/SKILL.md`

API quick start、read-only、style、scientific guidance均已读。没有创建/修改/导出工作簿，没有运行authoring marker。

- 官方真实 CSV：
  `literature/source_cache/mc_rc_three_patient_headers_2026-10-02/official_label_metadata_00_attempt_01.csv`
- SHA256：
  `f9d8d2b2ecab74824d02c95fdccd42f60c82f5e17746b830e3c67f73f9a372eb`
- **487条记录，15列**；artifact-tool全范围 `Official pathnames!A1:O488`。
- Reader：
  `tools/mc_rc_pathname_read_2026-10-02/read_official_mc_rc_pathnames.mjs`
- 结果：
  `experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json`
- 全部单元格与独立Python CSV解析精确一致，UID未数字转换，错误搜索0。
- `tools/.../node_modules` 是指向 bundled只读依赖的junction。归档时**不要递归哈希该junction**。
- Node：
  `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`

忽略官方ZIP中的 `__MACOSX/._...csv`，它是AppleDouble，不是真正表格。

### 3. 标签首跑完整gate失败，已保留

计划/脚本：

- `MC_RC_THREE_PATIENT_LABEL_GRID_PLAN_2026-10-02.md`
- `experiments/audit_mc_rc_three_patient_label_grid.py`

结果：

`experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json`

**exit1 / complete=false**，不可覆盖。

实际官方2023标签包只有 **301 NIfTI/124患者**，虽然CSV/API包含当前487系列。完整联结分项后：

- 301行实际标签存在。
- **60行SegmentationPath为空**：原2023 T1 53条 +2026新增T1 7条。
- **126条指定T2路径不存在**：全部为2026新增T2。
- 2026开放MR影像不代表标签同步开放。
- 排除58共享VS-SEG患者后：**71候选患者/159条T2系列有实际标签**；这是目录资格，native几何仍未全核。
- VS-MC-RC-003三系列全部无标签，仍pending，不能借其他标签替代。

首跑读取了001/002的六个标签数组（MR数组未读），其中3系列/2人过原中位数affine的头+grid预检；派生系列即使grid吻合也不放行。

### 4. 几何估计器问题已修正并独立验证

初始002第二时间点144切片，中位数IPP差步长累计位置误差 **0.03mm**，触发0.02mm阈值；实际法向gap变化仅约 `5.2e-7mm`，坐标量化让估计器累计偏移，不能称真实采集不规则。

追加计划在重算前保存：

`MC_RC_GEOMETRY_AND_LABEL_AVAILABILITY_FOLLOWUP_PLAN_2026-10-02.md`

追加脚本/结果：

- `experiments/refine_mc_rc_geometry_and_label_availability.py`
- `experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json`

对所有IPP中心化线性回归拟合 affine，**阈值仍0.02mm**；label grid角点阈值仍 **0.05mm**，只允许整数轴置换/翻转，不注册修复。

独立脚本：

`experiments/verify_mc_rc_native_t2_label_preflight.py`

证明：

`experiments/mc_rc_native_t2_label_gate/independent_raw_geometry_grid_verification.json`

实际 exit0/errors=[]：

- 重读9个原ZIP的473 DICOM头，与保存字段吻合。
- 独立 `np.linalg.lstsq` +首末位置算法复核拟合。
- 独立 `inv(DICOM affine) @ label affine` 整数变换核grid，避免照搬48穷举。
- 6标签数组重查。
- **6条原生头资格通过；4系列/2患者头+label-grid预检通过**。
- 所有原首跑失败保留，完整标签覆盖仍false。
- 科学独立性能验证患者 **0**。

四个通过系列：

| 患者/时间点 | native spacing r,c,z mm | 名义层厚 | 标签前景体素 | 新fit grid最大角点误差mm |
|---|---|---|---:|---:|
| 001 t1 | .527344,.527344,.7000 | 1.4 | 1011 | .000401 |
| 001 t3 | .527344,.527344,.7000 | 1.4 | 750 | .001537 |
| 002 t1 | .507812,.507810,.8000 | .8 | 1192 | .008307 |
| 002 t2 | .507812,.507813,.4000 | .8 | 7046 | .045605 |

**间距0.4/0.7不等于物理分辨率0.4/0.7**，名义层厚和oversampling须分别记录。缺MRAcquisitionType的001 t2明确pending，不能称已确认2D；003两个原生头通过但缺标签。

## 下一步

1. poll同一83910，继续原队列，不统计动态子集。
2. 收尾本轮：写原生头/标签结果报告、创新/数据资格更新、SESSION_UPDATE/VISIBLE_DIALOGUE/HANDOFF，保存下面公开消息和本次checkpoint请求。
3. 建本轮静态stage verifier：核计划/脚本/请求/473头/6标签/独立证明哈希，**显式保留原标签gate失败、缺标签、几何估计器修正的事后属性**；涵盖本轮data ZIP/标签文件，排除依赖junction和live队列。
4. 更新README；因此此前五个静态stage依赖README需write/read-only刷新，再本轮stage与全局 `verify_archive.py --write` / read-only。记录核验结果。不要重复已通过CPU复算/下载，除非有新修改。
5. 后续来源可转向**实际有标签的71人/159T2系列**做预写的native头资格扩展；100有T2描述患者不能全部认证。003和2026新增126T2标签缺失保留，不猜新下载地址。
6. 当前四个通过系列可用于后续来源/开发预检；**尚未解码MR数组、未计算任何重建或分割性能**。开始模型/动作实验前写新合同，患者重复时间点整体分组，预检/开发病例不作新方法未见确认。
7. 原45全部推断/regenerate/主分析后按冻结合同判断，再做既有selection sensitivity、多开发病例动作oracle/收益预测对照。无可发表claim前goal保持active。
8. 旧八行crosswalk的legacy UID联结缺口仍存在；全58共享患者排除，不能只排除八序列。

## 本轮需归档的公开更新

1. “上一轮取得了能改变后续设计的证据，属于实际进展。这一轮先核实同一 CPU 队列，再推进 MC-RC 原生 T2 与标签的资格检查；继续避开 GPU 和你的终端训练，所有新增工作保存到 `innovation`。”
2. “队列已确认仍在运行，24/45 人完成七个条件。接下来会读取预选三人的全部九个 T2 序列头部，并核对官方标签路径表；这一步只检查采集与标签资格，不计算重建性能。路径表涉及 Excel，我会使用 Spreadsheets 技能只读解析。”
3. “九个序列的完整头部已读完，五个符合预写的薄层原生 3D 条件；另外两个有明确的派生/MPR 标记，一个缺少采集类型，一个几何不规则。官方路径表实际是 CSV，已只读解析。接下来核对标签是否覆盖当前目录、与 DICOM 网格是否一致；切片间距和名义层厚会分别报告。”
4. “标签检查发现：2026 年新增影像对应的 126 个 T2 标签不在当前标签包中，第三名预选患者因此不能放行。独立几何复算还显示，中位数步长估计在一个序列上产生了舍入累积偏移；我会用全部切片位置拟合复核，并保留首跑判定。”

第3条“几何不规则”是首跑判定，已被后续独立证据修正；不能继续作为采集结论。
