# Processing Scripts

这个目录放数据处理、索引、划分和格式转换脚本。模型训练代码不要放这里。

## 当前脚本

| Script | Dataset | Output |
|---|---|---|
| `ningxia_prepare.py` | `dataset/NingXiaData/Data` | `dataset/NingXiaData/processed` |

## NingXiaData

运行：

```powershell
D:\conda\envs\MRI\python.exe -u -B .\processing\ningxia_prepare.py --data-root .\dataset\NingXiaData\Data --processed-root .\dataset\NingXiaData\processed --seed 3407 --extract-small-archives --convert-t2
```

注意：NingXiaData 已按老师确认口径统一记为 `T2`。脚本输出里的 `candidate` 是早期自动识别命名，表示从 DICOM 序列字段筛出的 T2 序列集合，不代表最终论文口径。
压缩 DICOM 依赖 `pydicom + pylibjpeg-openjpeg` 解码。
