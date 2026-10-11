# 本轮会话与研究交接

## 用户要求与执行范围

本轮先后要求“接着基于我的MRI项目读论文找创新点”，以及“目前GPU正在被占用着，你批量地读论文和根据我之前的工作找创新点，能验证的先试着探索一下，不能验证的也做好记录和准备后续尝试，把这轮对话所有的内容放进D:\MRI\innovation里”。因此阅读与 CPU 诊断在既有训练外执行；没有启动训练、运行下载的论文代码、修改旧模型或读取锁定 test 图像。

当前 IXI wavelet full 训练仍在运行，本轮只查看其历史文件作为状态快照；该文件会继续变化。仓库原有大量未跟踪研究材料，本轮没有清理它们。本轮改动限于 `innovation/` 的归档、脚本和报告，以及 `.gitignore` 中对本地大 PDF 的忽略规则。

## 已形成的判断

1. [主综述](literature/2026-09-30_MRI_innovation_review.md)将现有 PAST、orientation、I3Net、IXI wavelet 和几何审计放在同一个证据框架内。修复后的 fastMRI control/wavelet3 PSNR 为 25.567453/25.585002 dB，小波增益 +0.017549 dB；旧方向增强相对旧 control 为 +0.094388 dB，但 HD95 强度代理退化。两组结果不能混合成一个受控对比。
2. 分方向论文笔记及[五篇补读](literature/2026-09-30_focused_additional_papers.md)记录了直接近邻：任意位置扩散、跨平面自监督、profile/间距处理、残差 flow、联合区间生成、选择性恢复与风险认证、小波扩散均已有先例。只将“相对固定修正的可预测收益及其结构代价”保留为待证伪的窄问题，不声称首创。
3. [CPU 结果](experiments/CPU_RESULTS_2026-09-30.md)对 23 名历史 fastMRI validation 患者进行了病例级与 207 张缺失层的逐层二选一诊断。按 phase/毫米间隔从其余患者学习的简规则没有优于固定选择；真值 oracle 无法部署，也不构成 patch 融合上限。验证集已用于旧 checkpoint 开发选择，不能称整条链独立 OOF。
4. 同一结果文件记录了 fastMRI train 112、clean validation 23 个匹配 DICOM 系列的全系列头审计。名义 5 mm 层厚分别为 105/112、22/23；名义厚度与已核实中心间距差超过 0.1 mm 分别为 6/111、1/23。系列内部的两个字段一致。名义字段不识别真实 profile。
5. 后续又对同合同旧 control/orientation 做了完整 CPU 成对推理，形成[局部动作研究](experiments/LOCAL_ACTION_STUDY_2026-09-30.md)。真值 patch oracle 对最佳固定混合有 +0.14815 dB PSNR 空间，但 HD95 代理相对 control 仍退；留一患者可观测 patch ridge 只超过留一患者固定混合 +0.01382 dB，且 HD95 略退。患者真值幅度有乐观收益，可观测幅度预测尚不能守住所有患者。旧 orientation 仍停止；这不是可发表的正向 claim。
6. 同一协议下 repaired control/wavelet3 的 patch 真值 oracle 仅比固定 wavelet3 多 +0.01651 dB，HD95 代理略退；不再为这对固定模型做 gate。进一步审计了现有 MIRA CVPR 研究线，见[候选 claim 审计](MIRA_CLAIM_AUDIT_2026-09-30.md)：旧队列回顾性机制证据较强，部署评分仍失败。
7. 随后找到新来源 [MSValid](https://zenodo.org/records/10875606) RRMS 脑 T2 队列。先用 ZIP Range 取得索引和 84 人头信息，冻结[外部协议](MSVALID_CONFIRMATION_PROTOCOL_2026-09-30.md)，再分段提取 84 人首份 T2、验证全部 CRC/gzip/NIfTI/有限值，最后用 CPU 冻结 HAT/SwinIR 跑 479 目标。主端点 `ΔO=+19.7565` 个百分点，患者 bootstrap 95% CI +19.3276 至 +20.1605，84/84 人为正；phase-2 SwinIR 的整体 MAE 反而略低。详见[完整报告](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)。这给现有机制论文增加一个事前固定的单配对外部确认，但不是新主重建方法，也不解决可部署 guard 或相位/上下文混杂。

## 可复核材料

论文、按页提取文本、在线快照、来源登记及哈希索引都在 `literature/`。三项 CPU 诊断的脚本和完整 JSON 都在 `experiments/`：`patient_selection_diagnostic.py`、`slice_selection_diagnostic.py`、`slice_geometry_header_audit.py`。只读复核命令：

```powershell
D:/conda/envs/MRI/python.exe -B innovation/verify_archive.py
D:/conda/envs/MRI/python.exe -B innovation/experiments/patient_selection_diagnostic.py
D:/conda/envs/MRI/python.exe -B innovation/experiments/slice_selection_diagnostic.py
D:/conda/envs/MRI/python.exe -B innovation/experiments/slice_geometry_header_audit.py
```

各脚本会覆写自身的聚合 JSON；复核前若要保留当前字节级快照，应先记录哈希。`verify_archive.py` 只读检查 PDF/来源快照哈希及 Markdown 相对链接，不访问网络或 GPU。原项目证据路径与来源哈希见各诊断 JSON；归档之外的原有模型、CSV 和训练文件仍为原项目权威来源。

外部数据的 ZIP 远程索引、84 人头清单、几何资格快照、提取文件 SHA 清单及完整性审计均在 `literature/msvalid_*`；原始 T2 在 `data/msvalid_first_t2/` 且被其局部 `.gitignore` 排除提交。冻结 CPU 推理脚本及逐患者/逐目标 CSV 在 `experiments/msvalid_mira_confirmation*`。推理脚本拒绝覆盖已存在的结果目录；保留原快照，需重跑时在隔离副本中进行并注明代码哈希。

## 接手时先做

旧 control/orientation 的同病例完整预测现已用 CPU 生成并以哈希登记，位置见[局部动作研究](experiments/LOCAL_ACTION_STUDY_2026-09-30.md)。该动作的局部 oracle 有空间，但简单选择器和结构守卫没有成功。MIRA 的外部单配对确认已完成；下一步先在稿件中明确新队列的协议、边界和来源，并把任何 MSValid 后续相位控制标为结果后探索。若追求更强的测量身份因果解释或跨架构普适性，需要另一个真正未触及的队列及预定复制。IXI 锁定 test 遵守原协议，与此研究隔离。
