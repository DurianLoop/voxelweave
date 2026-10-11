# 用户提供的接续摘要（原文保存）

以下是用户本轮提供的接续文本；其中运行状态是其历史时点，后续实际结果见本轮SESSION_UPDATE。

## 当前目标与约束

科学目标仍 **active、未达成**：持续研究探索验证，直到形成可发表且独立验证的 claim。用户此次要求 checkpoint，**不是暂停研究**。

- 工作目录 `D:\MRI`，PowerShell；Python：`D:\conda\envs\MRI\python.exe`。
- 不使用 GPU、不干预用户终端训练、不读取锁定 IXI test、不改根环境或 `.gitignore`。
- 不新建/委派代理。CPU探索、公开数据获取已授权。
- 全部代码、证据、失败、公开对话及接续准备存入 `innovation`。
- 当前轮的 SESSION 文档、README、manifest 收尾 **尚未完成**。本条 checkpoint 也需写入 innovation。

## 原 CPU 队列：仍须保留

本轮实际 poll **session `83910`**，返回 live：

```powershell
D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py
```

不要重启或终止。最近读取的状态为 **42/45主患者、294 conditions**，仅历史进度；下轮先实际 poll 同一 handle，再读最新状态。

合同 SHA256：

`061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`

固定45 CISS +1 TSE、322计划条件、335合同引用。HAT−pipeline PCHIP两个主要方向不改，001/202 Dice改善反证保留，不动态子集评分、不挑SwinIR救方向。完整推断后驱动器自动逐患者再生成/输出核验/主分析，再运行 `vs_seg_selection_sensitivity.py`。

## 前一轮已完成的科学证据

入口：

`innovation/SESSION_HANDOFF_MC_RC_VISIBLE_QUEUE_ACTIVE_2026-10-02.md`

上一目标turn属于 **progress**，不是等待或状态重述：

- 五开发患者001/002/004/005/006的真值病灶约束oracle空间通过，240缺层、34,872 tiles。
- 原三人pipeline与五人raw无约束门槛均失败。
- 新30可见特征、λ=.01、五alpha网格、患者LOPO线性联合政策也失败：
  - 联合gain dB：`−.066440 / .039271 / .493958 / −.031182 / .367433`
  - 001/005两病灶guard失败；002不足.1dB；仅004/006通过。
  - 联合平均支持NMSE `.0017034239`，劣于固定α=.5的 `.0016965550`。
- 同容量10头的收益/绝对误差标签是线性坐标变换，预测差≤`6.085e-16`，政策逐tile相同。**不能把标签改名当贡献，也不外推所有神经模型等价。**
- 独立最终复核通过：增广lstsq、实际像素、全部348,720监督值、25行原生特征抽查，errors=[]。
- **按合同停止该固定30特征/岭/grid政策**，不事后调λ、ROI、门槛或挑患者。
- 后续方向：更多合格开发失败例、新病灶可见区域/边界表征，保持普通误差、风险路由、常数、随机与同容量/预算对照；任务及未见确认仍未做。

前轮归档20项检查通过，29主注册PDF、1834 evidence、1969链接。**本轮新增后这些全局manifest已过时。**

## 本轮新增：007/009/010七系列来源获取已完成

固定来源准备来自：

`experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json`

三人全部时间点整体归 **开发**，不是盲确认。固定7系列、API527对象、API FileSize合计261,941,288；包含007 MPR，不按性能/病灶筛选。

新增合同：

`innovation/MC_RC_007_010_SOURCE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md`

新增下载器：

`innovation/literature/download_mc_rc_007_010_native_headers_2026_10_02.py`

已实际执行，**session `35720` 已 exit0，不再 poll**。

结果：

`innovation/literature/source_cache/mc_rc_007_010_native_headers_2026-10-02/attempt_01.json`

原ZIP：

`innovation/data/mc_rc_007_010_native_header_gate/`

| 来源 | 实际传输bytes | 头资格 |
|---|---:|---|
| 007 MPR cor | 1,881,068 | 拒绝 |
| 007 FIESTA-C | 21,545,524 | 通过 |
| 009 FIESTA-C | 22,580,995 | 通过 |
| 009 TRIGEMINAL ci3d | 18,125,879 | 通过 |
| 010 3D FIESTA Hi Res | 36,877,952 | 通过 |
| 010 3D DRIVE AX | 11,280,323 | 通过 |
| 010 FIESTA-C | 22,442,521 | 通过 |

合计 **134,734,262 bytes**；7系列头读取完整，6系列头资格通过。**尚未独立复核，也尚未检查本批标签/grid。**

MR传输包含像素字节，但 **未解码 MR pixel_array、未运行模型、未算性能**。

下载合同：单连接、无自动重试、socket30s、整体180s/系列；总实际传输350MB，单cap=max(5MB,ceil(1.15×API FileSize)+1MB)。复用旧下载/头函数，仅进程内改目录/预算/geometry，旧冻结源码未修改。

## 已写好、尚未执行的标签脚本

新增：

`innovation/experiments/audit_mc_rc_007_010_label_grid.py`

**尚未调用执行工具，因此没有标签任务handle。** 上一条公开进度说“启动标签检查”，实际启动仍待下一步完成，不要误报已运行。

下一步直接执行：

```powershell
D:\conda\envs\MRI\python.exe -B innovation\experiments\audit_mc_rc_007_010_label_grid.py
```

输出设计：

- `experiments/mc_rc_007_010_native_label_gate/attempt_01.json`
- `data/mc_rc_007_010_label_grid/`

脚本用已认证2023官方label ZIP、CSV及完整artifact cells proof，按精确UID/患者/Study/对象数联结。全部七标签都检查，包括派生MPR。

预写预算：

- ZIP成员单50MB、总150MB。
- 名义数组单400MB、总2GB，**全部nominal预算在任何新slab解码前核**。
- 实际slab≤32MB。
- 二值/finite、q/sform、整数signed-axis grid，角点误差≤.05mm。
- 原生头采用全部IPP、≤.02mm几何误差、ORIGINAL无DERIVED、3D、spacing/名义thickness≤1.5mm。
- 没有authenticated affine则grid pending，不制造affine或注册修复。
- 资源gate：可用RAM8GB、磁盘15GB，自身低优先级、单线程、隐藏CUDA。
- 成功目录使用 `exist_ok=False`，**不能盲目重跑或覆盖**。先核实际状态。

## 清晰下一步

1. 实际 poll `83910`，保留原队列。
2. 执行上述七标签流式检查，核完整结果/失败/资格；不把头资格称source资格。
3. 写并执行本批独立来源复核：
   - 重新读取原527 DICOM头；
   - 全矩阵lstsq核IPP affine，独立资格；
   - 固定4-plane slab核七标签值域/foreground；
   - 反解整数grid、角点/extent、q/sform与CSV/ZIP来源；
   - 核原始hash，不只比较JSON布尔值。
   - 可参考 `verify_mc_rc_004_006_native_label_preflight.py`，但其main硬编码旧first/followup，不能直接运行或改旧冻结文件。
4. 整理七源结果、实际合格系列/患者及后续新的开发读取合同。更多来源不是创新；本批仍开发、确认0。
5. 保存本轮 SESSION_UPDATE/VISIBLE_DIALOGUE/HANDOFF、这个checkpoint、README；新增stage核验及依赖旧stage/global的write/read-only刷新，排除live队列和dependency junction。
6. 原队列全部结束后才原主分析/筛选敏感性。
7. 继续新病灶可见表征与强对照、完整任务、真正未见患者确认；科学goal保持active。

## 本轮公开消息待归档

1. “上一轮的实际拟合和独立复核排除了标签改名与固定线性门控两条路线，属于实质进展。本轮先核实原 CPU 队列，再执行已冻结的 007、009、010 来源审核，补齐后续病灶可见表征研究所需的数据资格；继续不动 GPU 和你的训练进程。”
2. “七系列的有界下载已启动，顺序单连接、无自动重试，总实际传输上限 350 MB。已取得的 007 MPR 系列被原生头规则拒绝，记录会保留；随后逐一检查全部七个官方标签的原生网格，资格与模型性能分开报告。”
3. “七系列下载和 527 个原始头已完成，实际传输约 134.7 MB；六系列通过头资格，007 MPR 被拒绝。我会保存接续状态，并启动已经写好合同的标签流式检查；研究目标继续保持 active，原 CPU 队列不重启或终止。”

本轮目前没有新失败、没有新论文获取/阅读、没有新代理或GPU操作；新标签检查和独立复核仍待执行。
