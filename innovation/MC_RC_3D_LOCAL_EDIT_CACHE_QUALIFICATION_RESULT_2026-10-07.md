# 局部输入修改的完整FOV缓存资格结果

单开发MRI的已冻结1024-update PCHIP模型通过事前固定的全部11项门槛，实际工具session72885 / chunka23c43返回exit0。无GT读取、无Dice计算、无训练更新、CUDA未初始化；19series正式模型的中间/最后MRI能力仍未读取。

| 实际检查 | 结果 |
|---|---|
| observed-only开发001 / UID末尾369177 | native256×256×30，共1,966,080体素 |
| 事前ROI | z14，r/c125:132，49输入体素各加归一化float32 .25；anchors和observed统计不变 |
| 经原physical resampling实际改变 | 243体素；zrc边界30:32 / 131:139 / 131:139（表内是包含端点的索引） |
| 原16个window中真正受影响 | tile5、6、9、10 |
| 保留原batch pair后须重算 | tile4–11，共8window / 4forward；另8window复用 |
| 完整修改路径 | 16window / 8forward |
| 缓存与完整修改路径 | 全tile、physical及native概率SHA相同；最大误差0、阈值差异0 |
| 原生产infer_full_fov核验 | 概率SHA及coverage SHA相同 |
| 未受影响window | 原/修改输入及输出概率均逐位相等 |
| physical输出改变范围 | 受影响window并集外0体素改变 |
| baseline概率缓存 | 67,108,864bytes，即64MiB，仅RAM |

资格实验真实执行28次CPU forward / 56window，包括基线8、完整修改8、缓存4及原生产函数核验8。缓存路径省4次是单候选推断计数，不表示整项资格实验只做4次。基线缓存初始化必付8次；对同样支持的K个动作，总调用为8+4K，对比完整8K，K>2时才严格省总调用。新候选基线不同、统计/权重变化或union支持扩大须重新计算。

单次计时：baselineforward6.7718s，完整修改forward6.3620s，缓存forward3.2340s，缓存含聚合3.4038s。正式训练同时运行、无交替顺序/暖机/重复统计，因此不称“已证明2倍加速”；本次总墙钟24.5062s。实际稳定的资格结论是少4forward且该样本全体积逐位等价。

基线到修改图的任务概率：full976,599体素浮点非零变化、max5.2720e-5；anchors260,801体素、max4.0054e-5；missing682,510、tail33,288。所有四域阈值0.5预测变化均0。浮点非零范围不能解释为976,599个受损/受益体素，也不能把变化唯一归因为IN；这个结果只证实保留图像锚点并不保证任务概率锚点逐位不变。

## 全19开发series的成本准备

另一个真实exit0（session30385 / chunk223f0f）仅用metadata和合成binary mask，未读MRI/GT、未做模型forward。每series取shape中心、最近missing z，对宽7/32/64的单层中心ROI使用原physical_mr传播支持。只是保守输入支持成本，不是真实病灶或SR动作，更不是全部19MRI的数值等价资格。

| 单层中心ROI宽 | 有forward节省series / 19 | 完整forward / 缓存forward | 11患者先均值节省比例 | 5个同支持动作含baseline的总调用比例 |
|---|---:|---:|---:|---:|
| 7 | 19 | 572 / 99 | .77728 | .37308 |
| 32 | 17 | 572 / 145 | .70310 | .45350 |
| 64 | 17 | 572 / 188 | .55703 | .52867 |

001（UID369177）和开发另一series（UID尾103688）在宽32/64时无forward节省；它们保留在全分母中。上述第二列与计数合计不是患者效果。每series末尾独立小batch入账，不能用总1139tile除2代替真实572forward。

若同时存全19series最终概率需4,777,312,256bytes；逐series最多805,306,368bytes（768MiB）。后续建议按series缓存并释放，采用完整输入差分识别支持；预测/GT文件仍按原预算另计，不把RAM缓存装入stage存档。

缓存失效条件：模型权重/模式、baseline输入、observed统计、坐标/窗口/批次、blend、precision/device/backend/线程配置改变。新的SR候选即使名义local，也必须由最终实际physical输入差分决定支持；如果几乎全变则退回完整路径。

[事前协议](MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_PROTOCOL_2026-10-07.md) · [完整资格结果](experiments/mc_rc_3d_local_edit_cache_2026_10_07/attempt01.json) · [19series成本记录](experiments/mc_rc_3d_local_edit_cache_2026_10_07/development_metadata_cost_attempt01.json) · [资格入口](experiments/qualify_mc_rc_3d_local_edit_cache_2026_10_07.py) · [成本入口](experiments/plan_mc_rc_3d_local_edit_cache_development_cost_2026_10_07.py)。
