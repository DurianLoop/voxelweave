# 模型权重分包说明

原完整归档：`experiment_master_table_weights_2026-09-20.zip`。本次拆为 4 个普通 ZIP，
每包文件大小严格小于 **2,000,000,000 字节（十进制 2 GB）**。

## 上传和解压

1. 分别上传下列全部 ZIP，不需要上传原来的 6.61 GiB 完整 ZIP。
2. 每个 ZIP 均可独立打开、独立解压，不是 .z01 分卷，不需要拼接二进制文件。
3. 需要完整集合时，将全部 ZIP 解压到同一个空目录。公共说明、代码和指标文件内容一致，重复文件可覆盖或跳过。
4. 每份权重只出现在一个包中。同一主表实验项的 NingXia 8 折权重不会拆散。

## 分包清单

| ZIP 文件 | 权重数 | 对应学习实验项数 |
|---|---:|---:|
| `experiment_master_table_weights_2026-09-20_part01of04.zip` | 106 | 29 |
| `experiment_master_table_weights_2026-09-20_part02of04.zip` | 112 | 28 |
| `experiment_master_table_weights_2026-09-20_part03of04.zip` | 123 | 25 |
| `experiment_master_table_weights_2026-09-20_part04of04.zip` | 117 | 26 |

合计 **458 份 best checkpoint，108 项学习模型结果**，与原完整 ZIP 一致。
原 ZIP 和工作区模型文件保持不动；本次直接从已校验的原 ZIP 读取，不重新训练，不调用 GPU。

## 包内文件

- `README_ZH.md`：本分包说明，每包相同。
- `README_FULL_ARCHIVE_ZH.md`：原完整权重包的中文说明，包含历史记录和科学有效性边界。
- `part_assignment.csv`：全部权重到 ZIP 文件的对应关系，可按方法、倍率、数据集筛选。
- `partNN_checkpoint_index.csv`：当前包专属的权重清单。
- `partNN_file_manifest.csv`：当前包文件的 SHA256 和大小；不包含该清单自身。
- `checkpoint_index.csv`、`CHECKPOINT_CATALOG_ZH.md` 等：原完整归档的总索引，描述全部四包，不代表当前单包有全部权重。
- `FULL_ARCHIVE_file_manifest.csv`：原完整 ZIP 的文件清单，仅用于追溯原包，不用于检查单个分包。
- `project/`：保持原相对路径。权重分配到各包，其余代码、配置、指标、日志均在每包中重复提供。

## 完整性

生成时先核对原 ZIP 的 SHA256，再核对每份文件内容；每包写完后逐文件回读，验证 SHA256 和 ZIP CRC。
外部 `split_validation_report.json` 记录四包实际大小、整包 SHA256、458 份权重不遗漏不重复等检查结果。
同目录还有 `SHA256SUMS.txt` 和各 ZIP 的 `.sha256` 文件。上传后可据此核对下载文件。

未包含 MRI 原始影像和预测。运行记录可能含病例/序列标识；公开发布前请按原说明审查匿名化和许可证。
