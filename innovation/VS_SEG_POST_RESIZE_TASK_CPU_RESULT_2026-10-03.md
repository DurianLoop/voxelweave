# 处理顺序与下游分割：post任务完整45人结果

固定原45已见CISS，一人仅新增一次post_resize_pchip冻结分割CPU forward；原raw/pipeline七条件没有重跑。session20644实际exit0，全45保存预测/全网格物理边界混淆计数及18标量bootstrap独立复核errors=[]。GPU未用，新方法独立确认患者0；结果是开发机制诊断，不是新的临床或科学确认。

| 标签 | raw PCHIP full Dice均值 | pipeline PCHIP均值 | post_resize PCHIP均值 |
| --- | ---: | ---: | ---: |
| original_json | 0.74459750 | 0.65476150 | 0.65284400 |
| rtstruct | 0.74413108 | 0.65449621 | 0.65254288 |

post与pipeline的顺序不同，均仅处理插入缺层、保留原anchors/tail；raw省去面内256 down/up。三者使用相同observed-only强度范围和原网格。post−pipeline回答顺序的任务差，post−raw包含空间处理；不能把已知support NMSE的0.84%直接映射为Dice贡献。

| 标签 | 域 | 固定配对比较 | n/45 | 平均ΔDice | 95%患者bootstrap区间 | 负/零人数 |
| --- | --- | --- | ---: | ---: | --- | --- |
| original_json | full | post-pipeline | 45/45 | -0.00191750 | [-0.00483038, -0.00015858] | 33/4 |
| original_json | full | post-raw | 45/45 | -0.09175350 | [-0.14691696, -0.04704404] | 37/1 |
| original_json | full | pipeline-raw | 45/45 | -0.08983600 | [-0.14464719, -0.04586167] | 37/1 |
| original_json | observed_anchor_slab | post-pipeline | 45/45 | -0.00191750 | [-0.00483038, -0.00015858] | 33/4 |
| original_json | observed_anchor_slab | post-raw | 45/45 | -0.09175350 | [-0.14691696, -0.04704404] | 37/1 |
| original_json | observed_anchor_slab | pipeline-raw | 45/45 | -0.08983600 | [-0.14464719, -0.04586167] | 37/1 |
| original_json | exclude_reference_boundary_1mm | post-pipeline | 45/45 | -0.00184906 | [-0.00515599, +0.00030049] | 26/8 |
| original_json | exclude_reference_boundary_1mm | post-raw | 45/45 | -0.06434625 | [-0.12586902, -0.01179196] | 32/1 |
| original_json | exclude_reference_boundary_1mm | pipeline-raw | 45/45 | -0.06249719 | [-0.12463233, -0.00828102] | 32/1 |
| rtstruct | full | post-pipeline | 45/45 | -0.00195333 | [-0.00489935, -0.00018204] | 34/4 |
| rtstruct | full | post-raw | 45/45 | -0.09158821 | [-0.14699415, -0.04661392] | 38/1 |
| rtstruct | full | pipeline-raw | 45/45 | -0.08963488 | [-0.14478697, -0.04547213] | 38/1 |
| rtstruct | observed_anchor_slab | post-pipeline | 45/45 | -0.00195333 | [-0.00489935, -0.00018204] | 34/4 |
| rtstruct | observed_anchor_slab | post-raw | 45/45 | -0.09158821 | [-0.14699415, -0.04661392] | 38/1 |
| rtstruct | observed_anchor_slab | pipeline-raw | 45/45 | -0.08963488 | [-0.14478697, -0.04547213] | 38/1 |
| rtstruct | exclude_reference_boundary_1mm | post-pipeline | 45/45 | -0.00189873 | [-0.00488763, -0.00003464] | 27/7 |
| rtstruct | exclude_reference_boundary_1mm | post-raw | 45/45 | -0.06448881 | [-0.12602098, -0.01298929] | 31/1 |
| rtstruct | exclude_reference_boundary_1mm | pipeline-raw | 45/45 | -0.06259008 | [-0.12473015, -0.00946218] | 32/1 |

全部18端点均保留。full/slab固定45人；reference 1mm core为空时，三比较共同保留配对undefined名单，不填零。5000draw、seed20261101，区间是描述性患者配对bootstrap，未作familywise校正；区间跨0不能证明等效，区间不跨0不能单独证明临床因果。

冻结任务模型与科学限制：官方相同2.5D attention/hardness网络、相同checkpoint、相同RAS/grid与阈值。独立程序复核共享来源标签、decoder和NumPy RNG；没有第二任务模型，也没有新的未见患者。当前原HAT−pipelinePCHIP负向主张被全45原实验反证的状态保持。

所有患者反例及两参考完整输出见[45人任务CSV](experiments/vs_seg_post_resize_task_cpu/all45_task_dice.csv)，完整端点/undefined名单见[18端点CSV](experiments/vs_seg_post_resize_task_cpu/all18_descriptive_task_endpoints.csv)，[固定计划](VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md)及[独立proof](experiments/vs_seg_post_resize_task_cpu/independent_all_tasks_and_estimates.json)。

下一步区分空间bandwidth、anchors混合与整volume归一化；[45人带宽诊断](ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md)与[三人归一化预检](ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md)已完成，但尚未得到只改anchors的任务结果。改变anchors只能作为解释性干预。
