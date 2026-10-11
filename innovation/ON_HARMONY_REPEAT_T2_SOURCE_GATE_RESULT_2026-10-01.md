# ON-Harmony 重复 2D T2w 来源门槛

**结论：同机重复组与 2D T2w FLAIR 采集扫描仪不相交，原始 2D 同机重复身份试验不成立。** 这是从论文采集协议与官方 release 非影像 CSV 的交集得出，未读取任何影像文件或像素。

## 证据链

1. [Warrington et al., *Scientific Data* 2025 全文 HTML 快照](literature/source_cache/on_harmony_article_2026-10-01/article.html)，DOI [10.1038/s41597-025-04822-2](https://doi.org/10.1038/s41597-025-04822-2)：20 人、六扫描仪/人；九人另外做五次同机重复。采集段写大多数扫描仪使用约 1 mm 各向同性 **3D T2w FLAIR**；GE MR750 因 3D 能力限制，另采 **2D T2w FLAIR**（1.5 mm isotropic 和 1 x 1 x 2 mm 两种版本）。这些均是 FLAIR，不能直接等同项目已有常规 T2w 队列。
2. 论文 Data Records 给出公开 OpenNeuro 数据集 `ds004712`、BIDS session 编码和同机重复表。其正文称 `session_delays.csv`；[官方 GitHub 镜像根目录快照](literature/source_cache/on_harmony_github_tree_2026-10-01/tree.html)实际列的是 **`scan_delays.csv`**。不存在的根目录名返回 404，见[入口探测](literature/source_cache/on_harmony_text_routes_2026-10-01/index.json)。
3. [OpenNeuro S3 官方发布的 `scan_delays.csv`](literature/source_cache/on_harmony_release_text_2026-10-01/s3_scan_delays.csv)与镜像 README 的[扫描仪编码](literature/source_cache/on_harmony_release_text_2026-10-01/github_readme.txt)共同说明：GE MR750 是 `NOT3GEM`。去掉 CSV 末尾空行后有 20 位受试者，九行填写 `Repeat scanner code`；其分布为 `OXF1PRI:2`、`OXF2PRI:2`、`OXF3TRI:1`、`NOT1ACH:1`、`NOT2ING:1`、`NOT4GEP:1`、`OXF4GEP:1`，**`NOT3GEM:0`**。因此论文中的 2D T2w 分支与发布的同机重复分支没有受试者交集。跨扫描仪的 3D-vs-2D 对比同时改变扫描仪/协议，不能替代同协议采集身份对照。
4. [官方 `dataset_description.json`](literature/source_cache/on_harmony_release_text_2026-10-01/s3_description.json)标注 `License: CC0`、DOI `10.18112/openneuro.ds004712.v2.0.1`、伦理和首选引文。许可和配对键可核，但不改变缺少同机 2D 重复的实验设计事实。

[只读独立复核脚本](experiments/verify_on_harmony_metadata_gate.py)校验两个官方文本哈希、20 个独立受试者、九人的五列重复 session、重复扫描仪分布及 MR750 交集为零。

此判定仅针对项目[原始 2D 层采集身份合同](ACQUISITION_ID_SOURCE_GATE_2026-10-01.md)。ON-Harmony 可以用于其他跨扫描仪或 3D FLAIR 重复性问题，但那些问题需要新的终点、几何/处理审计与先例检查。没有据当前数据声称原始 2D 同层配对、临床收益或稿件新意。没有下载 NIfTI、启动 GPU、触碰训练或锁定 IXI test。
