# Plan 17 复现与使用

工作目录为 `D:\MRI`，使用 `D:/conda/envs/MRI/python.exe -B`。本轮不安装依赖、不重新训练模型，真实神经图像复算使用 CPU。LaTeX 构建需要现有 MiKTeX、BibTeX 与 Poppler。

## 安全复核与构建

以下命令依次执行。验证命令仅更新本轮派生验证文件，构建更新当前 CVPR PDF 和构建辅助文件。

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/scripts/proposition_check.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/scripts/verify_framework.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/scripts/build.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/scripts/render.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/scripts/final_verify.py
```

## 分析依赖及记录保护

已有 `outputs` 保存冻结时间、开发病例、公式、所有输出及输入哈希。复现历史输出不代表获得一个新的未触及确认集。需要重新计算时，先在 `design/paper` 下复制本轮目录作为新的复现实验目录并保留快照；下列脚本会覆盖所在迭代目录内的同名派生输出。

| 顺序 | 脚本 | 作用与限制 |
|---|---|---|
| 1 | `extract_scores.py` | 读取 139 例原始体积及四模型既有预测，生成两配对逐平面/逐病例表及输入哈希清单。 |
| 2 | `analyze_scores.py` | 使用指定 12 例开发部分拟合经验 CDF，评估剩余 12 例及 IXI 115 例，保留零阳性与稀疏阳性。不得根据结果重选规则。 |
| 3 | `qualitative.py` | 按保存规则选中位效应病例与固定种子随机病例，CPU 复算 SwinIR，记录与旧 GPU 输出的数值差异。 |
| 4 | `practical_proxy.py` | 完整支持与两个 residue 条件不放宽；24 例 fastMRI 几何不合格，保留排除表；115 例 IXI 有效。 |
| 5 | `nonself_sensitivity.py` | 剔除历史 reference/self 966 行，进行六分层同时区间分析；明确属于事后检查。 |
| 6 | `figures.py` | 从真实数组与 CSV 生成本轮图，并更新 CVPR 对应新图文件。 |

`audit.py`、`audit_details.py` 是改稿前资产普查和绑定步骤，不应覆盖后再声称仍为原始盘点。`finish_ledger.py` 更新实验台账。`install_manuscript.py` 从 `main_revised.tex`、新增补充材料和原快照生成当前正文、表与补充材料；**它会覆盖当前 CVPR 的对应 TeX 文件，后续人工改稿前应先同步修改源或另存版本**。不要重建/覆盖 `original_snapshot`，也不要为“通过检查”重写原始清单。

## MIRA API 最小用法

`scripts/mira.py` 仅依赖 NumPy。将该目录加入 Python 导入路径后：

```python
from mira import audit_pair

def estimator(context, z):
    lo, hi = min(context), max(context)
    w = (z - lo) / (hi - lo)
    return (1-w) * context[lo] + w * context[hi]

result = audit_pair(
    estimator, {0: acquired_0, 4: acquired_4},
    {0: acquired_0, 6: acquired_6}, 2,
    amplitude=0.01, support=acquired_mask,
    support_source='acquired', normalization_source='acquired',
    target=retrospective_target,
)
```

示例数组需由调用者提供，位置 ID 必须代表真实同一锚点。目标只进入误差评价；调用者负责冻结模型、预处理和评估协议，并进行病例聚合与簇重采样。`target_free_score_contract` 是所声明信息来源的合同标记，不是检查任意模型闭包内部泄漏的自动证明。单次 amplitude 结果不构成稳定性验证，应按事先列明的幅度/符号/种子组重复审计。

完整绝对路径、权重哈希、掩膜/尺度例外、技术失败与统计单位见 `research_ledger.json`、`experiment_registry.csv`、`research_audit.md`。本轮没有外部未触及确认试验；不可将此目录复跑包装成前瞻性验证。
