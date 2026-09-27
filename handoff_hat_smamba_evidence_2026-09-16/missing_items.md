# 缺失项

本次没有 FORMAL_COMPLETE 结果。现有 fastMRI/NingXia 不是只有文档数值，原始 CSV、checkpoint、manifest 已找回；但其 strict-val 协议不合格，状态 INVALID。

| 缺失/不合格项 | 影响范围 | 证据 |
| --- | --- | --- |
| 独立 IXI n=25 test 结果、per-case/summary、final-test manifest | HAT、SMamba 两项 MISSING | search_scope.json、search_candidates.txt、run_candidate_audit.csv；n=115 manifest 位于各方法 IXI_n115_EXCLUDED |
| strict validation history、strict 选出的 best checkpoint | 两方法全部数据集 | checkpoint_audit.csv、checkpoint_metadata.json、reference/baseline/*/train.py |
| 测试 manifest 绑定 checkpoint SHA、normalization_mode、selection criterion | 所有现存旧 run | 各 run_manifest.json |
| 训练 seed | 所有现存旧 run | seed_audit.csv，原始 manifest/checkpoint 未记录 |
| 历史训练代码版本/哈希和 per-run 环境快照 | 所有现存旧 run | source_file_inventory.csv 仅为当前源文件指纹；environment.yml/requirements.txt 不是运行环境锁定证据 |
| 完整逐 epoch checkpoint 候选链 | 重点旧 run 仅有 best/final | source_file_inventory.csv、checkpoint_audit.csv |
| 官方 SMamba-UNet 等价实现证据 | 本地 surrogate 不能冒充原版 | reference/baseline/ixi_smamba_unet_2p5d/model.py；screening notes |
| 指定转移包与 3 份前置文档 | Handofff.md、协议.md、结果.md 未找到 | required_document_search.txt、archive_member_inventory.csv |

无需再补找的旧证据：两方法 NingXia fold_00 至 fold_07 的 CSV/history/checkpoint/manifest 全部找回，NX006/fold_05 保留；指定四折已完成探索性复算。训练 seed 和历史代码版本不能事后猜测或伪造。
