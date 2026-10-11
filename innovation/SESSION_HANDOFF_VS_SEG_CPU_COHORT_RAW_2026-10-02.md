# 用户提供的本次恢复摘要原文

以下是用户在本阶段开始时粘贴的交接摘要。它描述恢复时的状态，后续结果以本阶段实际文件为准。

## 目标与约束

用户要求基于 MRI 既有工作持续读论文、探索并验证创新，直到得到可发表且独立验证的 claim；所有资料、代码、结果、失败和对话保存在 `D:\MRI\innovation`。**目标仍 active，尚无可发表 claim，本阶段取得实质进展。**

- 工作目录 `D:\MRI`，PowerShell，日期 2026-10-02。
- Python：`D:\conda\envs\MRI\python.exe`。
- 不使用 GPU、不控制当前终端训练进程、不读取锁定 IXI test，不改 `.gitignore`、环境。
- 不新建子代理；没有允许主动委派的指令。
- 已启动命令全部结束，**没有待轮询进程**。
- 普通读取、公开下载、CPU 验证已有授权，无需再问。

## 本阶段已完成

### 1. 原始 JSON + 官方 SlicerRT 转换跑通

- 官方 Slicer **5.12.4 / revision 34645**。
- 匹配 SlicerRT Git 树：`3b6ce695aadf6133c0e97778843aa577f6ddbe64`。
- 两包官方 SHA512 校验通过，未执行安装器，用现成 `D:\7-Zip\7z.exe` 解包。
- 独立运行时：`innovation/tools/vs_seg_slicer_cpu`，实际解包 **1,222,575,394 字节**。
- 使用 `PythonSlicer.exe --launcher-ignore-user-additional-settings --launcher-no-splash -B ...`，只启动 python-real，无 Slicer 应用、GUI 或 renderer；VTK 单线程。
- 原作者 helper 函数从认证源码 AST 提取，函数正文不改；官方 `ExportSegmentsToLabelmapNode` 导出原生网格，默认 smooth end cap，不把离层 JSON 投到最近层。

固定开发病例：

| 病例 | 原 JSON 体素 | RTSTRUCT 体素 | 两掩膜 Dice | JSON 多出的整层 |
|---|---:|---:|---:|---|
| 001，作者 training | 7534 | 7505 | 0.9861027994 | 29 |
| 182，作者 validation、论文 Fig.2 | 780 | 634 | 0.8840169731 | 43、48 |

独立坐标核查通过；两例 RT 掩膜与独立平面栅格化零体素差。182 **复现已发表现象，不能当创新**。尚未证明当前转换与作者历史 NIfTI 掩膜逐字节相同，历史精确运行时未知。

重要文件：
- `experiments/vs_seg_original_mask_cpu_development/attempt_03.json`
- `.../independent_geometry_and_reference_verification.json`
- `.../development_converter_v1_snapshot.py`，原开发脚本 SHA256：
  `7aafb6f2cbfaef6bbeea9c3adcf2b0415419327b5f7e93a55b05ac648535e919`
- 当前 `experiments/vs_seg_original_mask_cpu_development.py` 已增加可选 prepared/output/plan 参数，数学流程不变。

失败已保留：空 NSIS Size 解析、错误 JSON 仓库 URL、旧 MRML 包装名称；实际类在 `MRMLCorePython`。旧解包报告错误地把未知 Size 当零，`runtime_manifest.json` 明确纠正，后续未知尺寸预留完整 3 GB。

### 2. MONAI list → tuple 等价验证通过

- 原 MONAI 0.4 四处多维 list 索引改显式 tuple。
- 001 全尺寸两次前向 **logits 逐位相同，最大差零**，预测与旧原生预检相同；CUDA false。
- 官方 wheel、网络数学未改。

文件：
- `experiments/vs_seg_001_tuple_equivalence/attempt_01.json`
- `.../monai_0_4_tuple_inferer.py`
- 派生实现 SHA256：
  `333f4703d4a1711fa41c82d0c6b34aefe2282106ba9a59555fa44412051318ed`

### 3. 七条件完整体积 CPU 预检完成

按先写协议，只用已见 training 病例 001：

- 唯一观测层 `0,4,...,76`，逐位保留。
- 恢复全部 **57 个内部缺失层，余数 1/2/3**。
- 不受支持的尾层 77/78/79 各重建方法均复制 76；不计入图像恢复目标。
- local 四锚点 PCHIP 在两端缺外侧锚点时回退 adjacent linear。
- 全原生体积任务评价用原 JSON 掩膜。
- 七条件耗时约 **292 秒**，重建体积、预测和逐层误差均保存。
- 独立重开输出核查零错误，CUDA false。

| 条件 | 支持域目标等权 NMSE | 全体积 Dice |
|---|---:|---:|
| native | 0 | 0.9579821 |
| raw linear | 0.00220533 | 0.8696871 |
| raw PCHIP | 0.00224690 | 0.8844858 |
| pipeline linear | 0.00205177 | 0.8637953 |
| pipeline PCHIP | 0.00204813 | 0.8758670 |
| HAT | 0.00169502 | 0.8814050 |
| SwinIR | 0.00170772 | 0.8739264 |

重要反证：
- HAT vs pipeline PCHIP：Dice **提高 0.005538**，没有支持任务损失方向。
- SwinIR：Dice 下降 0.001941。
- HAT vs raw PCHIP：Dice 下降约 0.003081，不能切换参照只展示负效果。
- 两模型病灶**目标等权** NMSE 变差，但**像素加权** NMSE 改善；不能把区域误差等同 Dice 损失。

文件：
- `VS_SEG_001_FULL_VOLUME_CPU_PREFLIGHT_PROTOCOL_2026-10-02.md`
- `experiments/vs_seg_001_full_volume_cpu_preflight/attempt_01.json`
- `.../independent_saved_output_verification.json`

### 4. 固定 46 名官方 test 的来源与掩膜全部完成

**没有在这些病例上运行本项目重建或分割模型，也未解码影像像素。**

- 46/46 来源准备成功，零失败。
- **45 CISS**：ORIGINAL、薄层 3D，全部 `448×448×80`，厚度/间距 ≤1.5 mm。
- **TSE 单例 VS-SEG-248**：ORIGINAL 3D，`384×384×40`，1.5 mm；单独次要报告。
- 首结构 TV 39、AN 7，无 Men。
- 全部原 JSON 和 RT 掩膜转换成功，独立坐标最大误差约 `4×10⁻¹² mm`。
- 两参考 Dice 范围 `0.919534–0.997263`。
- 首次 PowerShell 工具 status 1 与完整结果冲突，已保留日志；用 Python subprocess 重复并显式捕获，**返回码 0、全部 46 份 NPZ SHA256 相同**。
- 在固定45 CISS中，旧四目标规则加 ≥64 病灶体素及四锚点边缘约束、但**尚不交图像支持域**：RT 最多 **18 人**，原 JSON 最多 **19 人**。这是更严格上界，不能与旧放宽相位/方向、去掉像素门槛的22/46混用。

文件：
- `VS_SEG_FULL_VOLUME_HELDOUT_SOURCE_GATE_PLAN_2026-10-02.md`
- `literature/source_cache/vs_seg_full_volume_source_gate_2026-10-02/attempt_01.json`
- `data/vs_seg_full_volume_heldout_source`
- `experiments/vs_seg_full_volume_source_masks/attempt_01.json`、`attempt_02.json`
- `.../independent_source_geometry_verification.json`
- `.../explicit_launcher_status.json`

### 5. 新增两篇方法全文

阅读报告：
`literature/2026-10-02_vs_seg_model_method_and_label_novelty_audit.md`

- Wang MICCAI2019，DOI `10.1007/978-3-030-32245-8_30`：正式9页PDF，2021作者姓名修正版；Table1/2渲染并核对。245人、178/20/47，TensorFlow/NiftyNet、手动裁剪。2.5D、监督注意力、hardness Dice已有先例。
- Shapey JNS，DOI `10.3171/2019.9.JNS191949`：PMC7617042作者稿，NCBI BioC取得。摘要243/177/20/46与正文246/180/20/46冲突保留。T2 ensemble Dice88.25%，人类等效结论仅明确支持T1/联合模态。不能与当前MONAI单模型、242人发布混用或算独立来源。
- Sunderland2015、SlicerRT2012只取得元数据/摘要，**不计全文**。
- 继续沿用 Fischer2023/Morshuis2024 的全文碰撞结论，排除宽泛“首次任务感知重建”新意。

新PDF在 source_cache，后缀 `.response`，不是顶层29篇PDF注册列表的一员；其来源和提取哈希有独立索引。
访问失败 XML500/PDF403、缺pypdf后改已有Poppler均已记录。

## 当前报告与归档

- `innovation/README.md` 已更新最新入口。
- `VS_SEG_ORIGINAL_MASK_AND_FULL_VOLUME_CPU_RESULT_2026-10-02.md`
- `VS_SEG_FULL_VOLUME_TASK_DESIGN_DRAFT_2026-10-02.md`
- `SESSION_UPDATE_VS_SEG_MASK_AND_FULL_VOLUME_2026-10-02.md`
- `SESSION_VISIBLE_DIALOGUE_VS_SEG_MASK_2026-10-02.md`
- `SESSION_HANDOFF_VS_SEG_MASK_RAW_2026-10-02.md` 完整保存用户所供旧摘要。

**刚完成阶段 manifest write：10489文件，3,124,349,104字节，12作者Git blobs，零错误。**
阶段核验器已扩展检查 SlicerRT blobs、官方包SHA512、9384运行时文件及原开发脚本快照。

## 最先收尾

没有待运行命令。继续顺序执行：

```powershell
D:\conda\envs\MRI\python.exe -B innovation\literature\verify_vs_seg_stage_archive.py
D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py --write
D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py
```

`SESSION_VISIBLE_DIALOGUE...` 当前末尾写了“最终答复归档”，其实是拟交付文字，因用户请求 checkpoint **还未发送最终研究答复**。可改成“拟交付答复，尚未发送”，然后重新 write/verify 两个 manifests；必要时记录校验结果后同样刷新。

## 下一阶段工作

完整队列设计仍是**草案，未冻结，运行器尚未实现**：

1. 实现通用46人队列运行器、边界指标/敏感性与患者统计，先完成必要技术检查。
2. 冻结最终协议、代码和输入合同，再开始独立任务推断。
3. 主名单固定45 CISS，全部完成才能确认；1 TSE单列；不按小病灶、目标数、native Dice删人。
4. 主比较固定 HAT − pipeline PCHIP；双终点支持域NMSE与完整体积Dice的95%患者bootstrap区间上限都 <0 才支持候选联合方向。5000次、seed20261012。不能HAT失败后改挑SwinIR。
5. raw PCHIP强对照、RT标签重评分、夹在观测锚点范围的评价、1mm边界带敏感性、空预测/无限边界距离必须记录。
6. 448网格滑窗为八窗，001只有两窗；全单线程CPU队列估计 **8–10小时，未实测**。磁盘约18.8GB剩余，保持≥15GB；不要给45人保存所有大型重建体积导致超限，应设计可续跑、受限缓存，保留预测、逐层统计、源/输出哈希。
7. 假设paired Dice SD .02/.03/.05时45人单终点80%power MDE约 .00835/.01253/.02088；不是观察方差或联合power证明。
8. 若独立结果不足，继续反证与创新审查，不能强行声称可发表。旧≥100确认协议失败仍保留，不能把新45人研究称旧确认成功。
