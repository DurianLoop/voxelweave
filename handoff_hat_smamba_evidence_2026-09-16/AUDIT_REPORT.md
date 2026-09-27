# HAT / SMamba baseline 审计报告

审计日期：2026-09-16。实际项目根目录：`D:\MRI`。判定协议：`reference/user_request.txt` 中的 friend-protocol。

## 1. 结论

| Method | fastMRI | IXI n=25 | NingXia 8-fold | NingXia 4-fold | Training seed | Evidence status |
| --- | --- | --- | --- | --- | --- | --- |
| HAT | INVALID | MISSING | INVALID | INVALID | unknown/unrecorded | 原始证据已找回；strict-val 不合规 |
| SMamba | INVALID | MISSING | INVALID | INVALID | unknown/unrecorded | 原始证据已找回；strict-val 不合规 |


发现的历史结果比附件描述更完整：两种方法 fastMRI 原始证据均在；NingXia 各自 8 folds/8 cases/22 series 全部在。故这些不再归类 NUMERIC_ONLY。然而存在明确的非 strict-val 选模证据，按用户的状态定义应归类 INVALID，而不是因为文件齐全就升级 FORMAL_COMPLETE。IXI n=25 独立运行结果仍为 MISSING；n=115 存在并隔离保存，不是 n=25 的替代物。没有一项只能停留在“文档有数值但原始 CSV 找不到”的 NUMERIC_ONLY 状态。

## 2. 搜索及前置文档

已对 D:\MRI 全树执行包含 hidden/ignored 文件的文件名搜索；并搜索用户 Documents、Desktop、Downloads、D:\BaiduNetdiskDownload、D:\BaiduNetdisk\download、D:\SAM、D:\xwechat_files。逐根目录统计及错误见 `search_scope.json`。D 盘根目录已检查；未发现另一个明显的 MRI 项目根目录。工作区 `model/runs`、`code`、`docs`、`notebooks` 不存在；现有源码与产物位于 `baseline/`、`pre/`、`processing/`、`docx/`、`logs/`、`design/`、`temp/`，均包含在搜索内。

在 D:\MRI 全树的 Python/Markdown/JSON/CSV/YAML 文件上进一步搜索 strict checkpoint/history/summary 的三个标志字符串，零命中；方法关键词内容命中 3292 个文件，见 `method_references.txt`。不把目录名中的 `strict_full` 当作 strict-val 证据。扫描覆盖约 88 万个文件路径；并未逐个读取与本任务无关的文件内容。

前置文档搜索结果：

- `Handofff.md`：没有找到。
- `model/协议.md` / 同名 `协议.md`：没有找到。
- `model/main_model/结果.md` / 同名 `结果.md`：没有找到。
- `baseline_exposed_problems_for_model_design(1).md`：同内容主题文件位于 `docx/experiment_notes/other/baseline_exposed_problems_for_model_design.md`，已读取并复制；桌面另一个同主题文件也保留副本。没有将名称不同的其他协议冒充指定文档。

找到并检索两个相关 zip 的成员目录：`transfer_hat_baseline_code_20260625.zip`（57 项，仅代码/说明）和 `PLAN15_BASELINES_PAPERS_AND_EVIDENCE.zip`（164 项）。未找到附件描述的 `transfer_package_t2x4_friend_2026-06-16_v2`。成员清单见 `archive_member_inventory.csv`；HAT 代码转移包中的关键代码已只读提取到 `archive_reference/`。

权限范围限制：D:\MRI 有 2 个测试/安装临时目录不可读，D:\SAM 有若干测试临时目录不可读；详细路径原样记录于 search_scope。用户 home 根目录枚举曾被拒绝，但 Documents/Desktop/Downloads 定向搜索成功。结论是“在记录的可访问范围中未找到”，不是对所有磁盘不可访问目录的绝对不存在证明。

## 3. 判定 INVALID 的证据

四个训练实现均调用普通 `_validate`，以 batch reconstruction loss 最小值保存 best：

- `reference/baseline/ixi_hat_2p5d/train.py:156` — `_validate`；`:158` — 比较 val_loss；`:162` — 保存 best。
- `reference/baseline/ixi_smamba_unet_2p5d/train.py:155`、`:157`、`:161` — 同样选模逻辑。
- `reference/baseline/fastmri_brain_hat_2p5d/train.py:168`、`:170`、`:174` — fastMRI 与 NingXia HAT 共用。
- `reference/baseline/fastmri_brain_smamba_unet_2p5d/train.py:155`、`:157`、`:161` — fastMRI 与 NingXia SMamba 共用。

对应 `data.py` 的 `VolumeCache.get` 对完整 dense volume 做归一化，样本枚举为 `range(0, depth - stride)`，并非仅从 z%4==0 的固定 acquisition grid 构造 sparse 验证输入。IXI 相应数据实现是 `reference/pre/ixi_diffusion/data.py`。因此这个 validation 不能证明与本次 strict friend-protocol 等价，问题不仅是 checkpoint 文件名不同。

本次使用 `torch.load(..., map_location='cpu', weights_only=True)` 仅读取 checkpoint 元数据，不执行模型。21 个重点 run 的每个 best checkpoint 都核对了 epoch 和 best_val_loss，全部与同 run `training_history.csv` 的普通 val_loss 最小值一致。原始元数据见 `checkpoint_metadata.json`，逐 checkpoint SHA-256/epoch/选模判定见 `checkpoint_audit.csv`。仅有 best/final 文件，未找到 strict best 或逐 epoch 完整候选快照链。final 文件没有被拿来作正式 checkpoint。

历史 run_manifest 缺少测试所加载 checkpoint 的绝对路径/SHA、strict 选择记录、normalization_mode 和 seed。源码表明 run_all 将 train 函数返回的普通 best 传给 interpolator，但原始 manifest 不能密码学绑定当时实际加载的权重。该缺失另记为证据缺口，不凭当前源码宣称历史执行已完全可追溯。

## 4. 通过及未通过的其他项目

| 核验项 | 发现 |
| --- | --- |
| T2 / x4 / 数据规模 | manifest 标注 T2、stride=4；fastMRI 24；NingXia 8 病例 22 series |
| 输入来源 | run_all 将 `paths.eval_sparse` 传入 interpolator.process_folder；未发现 test inference 读取 GT 作输入的代码 |
| 测试归一化 | interpolate_volume 对收到的 sparse volume 调用 normalize_volume；lo=nanmin、hi=nanmax、分母+1e-8。常量体积有全零分支。原始 manifest 未记录该 mode |
| generated-only | 本地 `pre/topcow_diffusion/metrics.py` 使用 idx % factor != 0；逐病例 generated_slices 数量与 manifest target_depth 一致 |
| 正式 metrics 路径 | 附件 `code/topcow_diffusion/metrics.py` 在本树对应 `pre/topcow_diffusion/metrics.py`；代码导入 topcow_diffusion.metrics。转移包指定版本不存在，无法证明与该未找到版本字节相同 |
| 五项指标 | PSNR/SSIM/MAE/MSE/NCC 齐全且有限；105 个 run×metric 聚合检查通过 |
| 训练配置 | run_manifest 与 checkpoint model_config 提供部分实际配置；当前 settings 仅辅助，不冒充完整历史 config snapshot |
| 训练 history | 21 个重点 run 均存在 |
| strict-val history / strict best | 未找到，且现有 checkpoint 对应普通 val_loss 选模 |
| 代码版本/哈希 | 本次所有候选和引用代码 SHA 已记录；历史执行 commit 或 code SHA 未记录 |
| 环境 | 有 repository environment.yml/requirements.txt/env_setup_MRI.log；无每个 run 绑定的环境快照 |
| 训练 seed | 一律 unknown/unrecorded；checkpoint、manifest 和训练源码均不能证明具体训练随机 seed |
| 数据划分 seed | IXI split_manifest 明确 3407；fastMRI 目录及 split 代码指向 3407，但无历史 seed 日志；NingXia 是排序后 leave-one-case-out 轮转，3407 只是 seed_name 目录标签，不是随机 CV seed |

上述 inference/metric 行是**当前代码级核验加 CSV 一致性核验**，不是此次重新做像素指标计算，也不是对历史运行二进制的证明。详见 evidence_matrix.csv 中每项边界。

## 5. 数值重汇总

将原始 per_case_metrics.csv 按方法过滤，对每个 fold 内的 series 等权求均值；验证与该 fold 原始 summary 一致；再对 8 或指定 4 个 fold 等权求均值。没有按 series 数量加权 fold，没有剔除 NX006/fold_05。

| Method | Dataset | Folds | Series | PSNR | SSIM | MAE | MSE | NCC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAT | NingXia_8fold | 8 | 22 | 23.9499 | 0.7519 | 86.1449 | 32226.9860 | 0.8933 |
| HAT | NingXia_4fold_exploratory | 4 | 13 | 24.6300 | 0.7663 | 85.0416 | 35614.9547 | 0.8862 |
| SMamba | NingXia_8fold | 8 | 22 | 23.9126 | 0.7500 | 86.8152 | 32498.3175 | 0.8917 |
| SMamba | NingXia_4fold_exploratory | 4 | 13 | 24.6228 | 0.7655 | 85.0325 | 35670.6220 | 0.8853 |


四折口径固定为用户指定 `fold01 + fold03 + fold04 + fold06`，对应本地 `fold_01 + fold_03 + fold_04 + fold_06`，不是从 1 开始重新编号。病例 NX002/NX004/NX005/NX007；series 数分别 4/4/2/3，共 13。

Post-hoc exploratory subset only.
Not a replacement for the formal 8-fold result.

两方法完整八折 series 数均为：fold_00/NX001=2，fold_01/NX002=4，fold_02/NX003=2，fold_03/NX004=4，fold_04/NX005=2，fold_05/NX006=3，fold_06/NX007=3，fold_07/NX008=2。逐折五项指标、病例及全部 series 名称、train/val/test 映射见各方法 `NingXia_8fold/per_fold_metrics.csv` 和 `fold_case_mapping.csv`。

附件给出的 4 组×5 项历史指标全部四位小数一致；差值明细在 `historical_value_comparison.csv`，未修改原始数值。这里“复现”指已有 CSV 的算术复算，不是重新推理、像素级 metric 复测或训练复现。

## 6. 新旧版本差异与排除项

附件 HAT fastMRI 数值来自 `baseline/fastmri_brain_hat_2p5d/runs/full`：22.7858 / .7536 / 49.6702 / 10454.4878 / .9079。当前 experiment_master_table 的 HAT fastMRI 行则是 23.0894 / .7688 / 47.2467 / 9773.1765 / .9138，对应 `full_extend60`。后者是另一个继续训练 profile，两套原始证据均复制，不择优替换、也不声称两套为同一运行。确切差值可从 run_level_audit.csv 获取。

IXI 两种方法仅找到 full_test115（各 115 个病例），HAT PSNR=28.7249，SMamba PSNR=29.3536；smoke/mini 也不是 n=25。未从 n=115 后选 25 个病例生成主表结果。当前本地主表已经改成 IXI n=115，且比较方法集合与附件的 11 baseline 不完全相同；本次仍严格按用户的 HAT/SMamba、IXI n=25 范围审计，没有修改论文表。

`baseline/*_root_results_202607` 中还有其他 profile（例如 full_60_scratch、x2、x6 等），没有将其他 epoch/scale 结果混入此次指定历史汇总。97 个 run 的 profile、stride、样本数及排除原因见 run_candidate_audit.csv。日志目录 `hat_smamba_three_datasets_strict_full_20260618` 的脚本实际仍调用上述普通 run_all，并未提供 strict 验证实现，名称不能作为合规依据。

## 7. 方法身份

`reference/docx/experiment_notes/other/hat_smamba_ixit2_screening_notes.md` 明确记载 HAT 为本地 HAT-style 2.5D 改编，SMamba 为 dependency-light directional selective scan surrogate，而非官方 SMamba-UNet 精确复现。`reference/baseline/ixi_smamba_unet_2p5d/model.py:21` 的类注释直接标为 surrogate，内部用累计平均实现方向扫描。

交接目录沿用 HAT/SMamba 短名只为匹配用户清单；结果实际身份必须保留上述 style/surrogate 标签。不能把这些权重宣称为官方 HAT/SMamba exact reproduction。即使未来补齐 strict-val，若论文要求原版模型，还需要先补模型来源/实现一致性审查。这次没有创建、替换或修改模型实现。

## 8. 验证及交付边界

本次完成 756 项重点运行一致性检查（全部通过，详见 validation_checks.csv），并逐个复制校验 SHA。协议不合规属于审计结论，并不与数据一致性检查通过冲突。打包前另验证全部源 inventory SHA 未改变、包内 SHA、复制一致性和 zip CRC；结果见 package_validation.json 及外部 zip .sha256 文件。

没有训练、推理、test 选 checkpoint、删除病例、覆盖原始结果或改写既有结果.md。最小补齐方案是先修复 strict 评估与模型身份问题，再执行 20 个独立训练/strict-val 周期及 20 个 final-test 任务；指定四折只需从合规 8-fold 再汇总，不新增训练。具体前提、可运行的只读命令和未实现的执行接口边界见 rerun_recommendations.md。
