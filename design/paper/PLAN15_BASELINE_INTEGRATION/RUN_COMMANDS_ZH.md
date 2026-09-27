# Plan 15 运行与复现

工作目录 `D:\MRI`；使用现有 MRI Python 环境。无需重训或 GPU，原始文件只读，新增输出均在 paper。

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/audit_master.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/recover_saint.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/analyze_baselines.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/revise_and_plot.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/build.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/verify.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/render.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/finalize.py
```

仅核验现有结果时执行 `verify.py` 即可。`recover_saint.py` 会读原始 GT／SAINT 输出重新评价 48 个体数据；其余数值步骤主要读取既有 CSV，不运行网络。

`audit_master.py` 保留主表中的既定配置，寻找五指标匹配的原始 summary；所有完全匹配的候选来源都保留。它不会用后来更好的 profile 替换原主表。两项被覆盖的 SAINT summary 在 `analyze_baselines.py` 中接回原预测重建的结果。匹配不是独立实验，也不对已知结果赋予预注册身份。

`revise_and_plot.py` 从本轮 `original_snapshot` 读取修改前稿件，会重新生成当前 CVPR／TMI 主文及 baseline 补充；若已人工修改稿件，应先另建快照，避免覆盖人工工作。

LaTeX 使用已有 pdflatex/bibtex；PDF 文本与渲染使用 pdfinfo/pdftotext/pdftoppm。当前环境需要访问用户 MiKTeX 配置，构建及渲染已经通过授权执行；曾遇审批额度拒绝，重试同一低风险操作后完成，没有改用绕过方案。

ZIP 含当前论文源码、图表、派生 CSV 和本轮脚本，不含原医学图像、网络预测、checkpoint 或完整历史快照。编译当前论文可以使用包中源码；完整复算仍依赖 D:\MRI 下的源数据／baseline、pre 中的历史指标，以及快照文件。不要把此包描述为包含全部数据的自足环境。
