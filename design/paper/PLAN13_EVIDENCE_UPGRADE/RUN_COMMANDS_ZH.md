# Plan 13 复现指令

从 `D:\MRI` 的 PowerShell 执行。只写入 paper 下本阶段目录或当前两稿；历史 full 输出只读。首次快照脚本已经执行，**不要再次执行 `prepare.py`**；它也会在快照已存在时主动拒绝。

```powershell
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/analyze.py
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/ixi_benefit.py
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/verify.py
```

第一条复算两队列完整正式表和全部受益模型；第二条读取 115 例原始 T2 和两个 I3Net profile 的完整 NIfTI，重算共同支持；不调用 GPU、不训练。输出可重复生成于本阶段 outputs。若需保留另一轮新分析，先复制本阶段结果到新目录，不改旧协议。

图表与稿件重建：

```powershell
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/figures_tables.py
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/build.py
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/render.py
```

`build.py` 对两个正文运行 pdflatex → bibtex → pdflatex → pdflatex；补充材料无 bibliography，只运行 pdflatex。日志、PDF 文本和页数审计集中存入 `build_logs/`。MiKTeX 需要读取已安装的用户配置；受限沙箱中可能无法运行，正常用户 PowerShell 可使用本机配置。

`revise.py` 从 `original_snapshot` 确定性生成本轮正文修订。**它会覆盖当前 main.tex/references.bib，因此后续手工继续编辑后不要无条件重跑。** 需要完整复现本轮版本时才运行，再执行图表和构建脚本；新增补充分析文件 `p13_additional_analysis.tex` 是独立维护的源码。

环境：本机 `D:\conda\envs\MRI`，NumPy/Pandas/SciPy/Matplotlib/nibabel/Pillow；PDF 工具为 MiKTeX 的 pdflatex、bibtex、pdfinfo、pdftotext、pdftoppm。本轮没有下载模型或修改全局 Python 包。

历史 Plan 9–12 的脚本因归档改变了 `parents[]` 根目录语义；不得原样照旧 README 执行，更不能将 smoke 输出写成 full。若重跑旧神经推理，需要先在新阶段副本修复根目录和显式输出目录，并核对协议。

本轮交付入口及草稿源码包更新（需要先完成构建）：

```powershell
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/finalize_docs.py
D:\conda\envs\MRI\python.exe -B design/paper/PLAN13_EVIDENCE_UPGRADE/scripts/package_delivery.py
```

第一条更新 paper 入口、两稿审计和原稿差异；后续继续研究时不要用它覆盖已手工更新的说明。第二条只生成本地 DRAFT 源码 ZIP、验证压缩包并输出 `FINAL_ARTIFACT_MANIFEST.json`，不投稿、不上传，不包含原始 MRI 数据。检查修改前后文本可读 `outputs/manuscript_changes.diff`。
