# Plan 14 运行指令

工作目录 `D:\MRI`，解释器 `D:/conda/envs/MRI/python.exe`。已有完整结果，不必重跑原生图像推理。下列脚本只向 paper 写结果；不更改训练、数据或 checkpoint。CPU 实验；没有 GPU 依赖。

## 核验当前交付

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/verify_new_contracts.py
```

## 分析和论文构建

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/bank_mask_audit.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/fastmri_geometry.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/ixi_scale_contract.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/analyze_topcow.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/figures.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/revise_papers.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/build.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/render.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/finalize_delivery.py
```

MiKTeX 的 pdflatex／bibtex 与 Poppler 的 pdfinfo／pdftotext／pdftoppm 需可调用。本会话在沙箱内不能正常读取 MiKTeX 用户配置，已通过授权的工具权限完成构建，不涉及安装或更换模板。

## 从图像重算

执行顺序为 `prepare_inventory.py` → `topcow_experiment.py` → `analyze_topcow.py` → `bright_anchor_experiment.py` → `cas_transfer.py`。本轮 CPU 墙钟约为 TopCoW 821 秒、亮区 146 秒、CAS 258 秒（图像阶段；不含所有 bootstrap、审计和排版）。病例 CSV 已存在时推理脚本跳过已有病例；这属于续跑，不是重新生成原始预测。

如需全量独立复算，应先把整个本轮目录复制到 paper 内新的兄弟目录，在副本中使用独立空结果目录并保留必要原始快照和协议版本，勿删除或覆盖当前证据。脚本以当前目录定位 paper 和 D:\MRI，依赖现有原始图像／标签、历史预测与 Plan 13 输出；派生证据 ZIP 不包含这些医学图像或模型权重。

`revise_papers.py` 从 original_snapshot 中的 Plan 13 稿件确定性生成当前稿，会覆盖当前两稿；人工继续修改后应先建立新快照。它不修改 Plan 13 历史目录。

E02 执行跨越了 E03 协议增补，但 E02 方法未变；记录中的两个版本哈希可在 protocol_versions 找到。E04 是读过 E02 结果后的探索，E05 是迁移前固定的规则；当前 PROTOCOL 不能追溯冒充早期外部预注册。重跑会记录当前协议版本，应保留初始运行 manifest 以区分执行。
