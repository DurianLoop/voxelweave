# 45 CISS完整结果：原主假设被反证

原83910实际正常退出，322/322推断条件及46人输出proof完成；固定45CISS主名单和1TSE次要病例均保留。重建像素已逐患者独立再生成，保存任务预测的坐标/混淆/边界指标独立重算；没有声称另行重新推断全部分割网络。新增58个完整统计条目及原112个筛选条目各自独立标量bootstrap复核errors=[]，两套统计seed不同，区间不能混写。

固定主HAT−pipelinePCHIP支持NMSE：-0.00024501101 [-0.00027523727, -0.00021704913]；45/45患者降低。
固定主原JSON完整Dice：0.036381704 [0.007181222, 0.071980619]；26提高、16降低、3相同。
预写要求图像差与Dice差的区间上限均<0，实际Dice区间完全为正，所以固定负向联合claim被反证并停止。不能换SwinIR、raw基线或病灶子组救主claim。正向Dice结果也不自动变为原预注册成功或新方法贡献。

| 条件 | 原JSON Dice均值 | Dice中位数 | RT Dice均值 | 支持NMSE均值 | 原JSON绝对相对体积误差均值 | 空预测/边界非有限 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| native | 0.90743931 | 0.91072414 | 0.90405944 | 0 | 0.0918408 | 0/0 |
| raw_linear | 0.70204741 | 0.74323118 | 0.7015492 | 0.0015582149 | 0.36588807 | 2/2 |
| raw_pchip | 0.7445975 | 0.75621222 | 0.74413108 | 0.0015907202 | 0.26981758 | 1/1 |
| pipeline_linear | 0.56211897 | 0.68447479 | 0.56214675 | 0.001446984 | 0.4902447 | 7/7 |
| pipeline_pchip | 0.6547615 | 0.72106825 | 0.65449621 | 0.0014466172 | 0.3767934 | 3/3 |
| hat | 0.69114321 | 0.72661654 | 0.691531 | 0.0012016062 | 0.3131555 | 2/2 |
| swinir | 0.63913396 | 0.728125 | 0.63926085 | 0.0012083294 | 0.36355321 | 4/4 |

强基线敏感性：HAT−rawPCHIP完整Dice −.053454294，描述性95%区间[−.099770378,−.015642155]；同一HAT−pipelinePCHIP为+.036381704。比较的基底处理确实影响点估计方向；它们不是相同信息处理合同，当前结果不单独分离面内缩放、抗混叠、裁剪或任务网络的分布响应。HAT对rawLinear的Dice区间跨0，SwinIR对pipelinePCHIP的Dice区间也跨0；全部结果见下表，不挑有利模型。

HAT主比较的RT完整Dice+.037034794，区间[+.008048744,+.072598788]；1mm边界带排除后的Dice+.030980474及+.031037905，两个区间均跨0。slab在本批两标签/八对中与full相同，不是另一独立复制。原JSON病灶NMSE按目标等权和按像素加权结论强弱不同，均在112全表保留。001及202改善反证保留；不能把平均收益说成每个患者安全。

次要TSE248保持单列：native Dice .93207054；rawLinear .84852836，rawPCHIP .83836341，pipelinePCHIP .70736086；HAT、SwinIR、pipelineLinear均0。它不能补进45CISS主名单，也不能单例确认协议效应。

单中心、模拟抽层、单冻结任务网络、原JSON/历史NIfTI精确等价未证实及离散体素中心边界定义均保留。当前45队列已见结果，今后新选择器不能再将其声称全新未见确认。[本批两正文](literature/2026-10-03_task_utility_fulltext_reading.md)进一步排除图像/任务分离的宽首创。[任务评估器后续准备](FROZEN_TASK_EVALUATOR_FOLLOWUP_PREPARATION_2026-10-03.md)区分冻结pipeline与适配后的任务能力。

以下八对全部公开；支持NMSE与六种Dice敏感性为描述性未familywise校正区间，每项有效患者45、undefined0。

| 模型−基线 | 支持NMSE差[95%] | 标签/范围 | Dice差[95%] | Dice负/零患者 |
| --- | --- | --- | --- | --- |
| hat−raw_linear | -0.00035660871 [-0.00039588968, -0.00031959243] | original_json/full | -0.010904208 [-0.063232734, 0.034363485] | 23/1 |
| hat−raw_linear | -0.00035660871 [-0.00039588968, -0.00031959243] | original_json/observed_anchor_slab | -0.010904208 [-0.063232734, 0.034363485] | 23/1 |
| hat−raw_linear | -0.00035660871 [-0.00039588968, -0.00031959243] | original_json/exclude_reference_boundary_1mm | 0.033884774 [-0.029456614, 0.091787217] | 17/1 |
| hat−raw_linear | -0.00035660871 [-0.00039588968, -0.00031959243] | rtstruct/full | -0.010018194 [-0.062796294, 0.035886214] | 23/1 |
| hat−raw_linear | -0.00035660871 [-0.00039588968, -0.00031959243] | rtstruct/observed_anchor_slab | -0.010018194 [-0.062796294, 0.035886214] | 23/1 |
| hat−raw_linear | -0.00035660871 [-0.00039588968, -0.00031959243] | rtstruct/exclude_reference_boundary_1mm | 0.033835813 [-0.029574227, 0.091225813] | 17/1 |
| hat−raw_pchip | -0.000389114 [-0.00043080922, -0.00034994486] | original_json/full | -0.053454294 [-0.099770378, -0.015642155] | 28/1 |
| hat−raw_pchip | -0.000389114 [-0.00043080922, -0.00034994486] | original_json/observed_anchor_slab | -0.053454294 [-0.099770378, -0.015642155] | 28/1 |
| hat−raw_pchip | -0.000389114 [-0.00043080922, -0.00034994486] | original_json/exclude_reference_boundary_1mm | -0.031516713 [-0.084370529, 0.016375906] | 22/1 |
| hat−raw_pchip | -0.000389114 [-0.00043080922, -0.00034994486] | rtstruct/full | -0.052600083 [-0.09965924, -0.014271633] | 29/1 |
| hat−raw_pchip | -0.000389114 [-0.00043080922, -0.00034994486] | rtstruct/observed_anchor_slab | -0.052600083 [-0.09965924, -0.014271633] | 29/1 |
| hat−raw_pchip | -0.000389114 [-0.00043080922, -0.00034994486] | rtstruct/exclude_reference_boundary_1mm | -0.031552174 [-0.08485356, 0.016263071] | 22/1 |
| hat−pipeline_linear | -0.00024537784 [-0.00027561863, -0.00021724145] | original_json/full | 0.12902424 [0.068320195, 0.19621154] | 7/3 |
| hat−pipeline_linear | -0.00024537784 [-0.00027561863, -0.00021724145] | original_json/observed_anchor_slab | 0.12902424 [0.068320195, 0.19621154] | 7/3 |
| hat−pipeline_linear | -0.00024537784 [-0.00027561863, -0.00021724145] | original_json/exclude_reference_boundary_1mm | 0.1525265 [0.085058812, 0.22819001] | 9/3 |
| hat−pipeline_linear | -0.00024537784 [-0.00027561863, -0.00021724145] | rtstruct/full | 0.12938425 [0.068245296, 0.19652992] | 7/3 |
| hat−pipeline_linear | -0.00024537784 [-0.00027561863, -0.00021724145] | rtstruct/observed_anchor_slab | 0.12938425 [0.068245296, 0.19652992] | 7/3 |
| hat−pipeline_linear | -0.00024537784 [-0.00027561863, -0.00021724145] | rtstruct/exclude_reference_boundary_1mm | 0.15101427 [0.084421543, 0.22640584] | 8/3 |
| hat−pipeline_pchip | -0.00024501101 [-0.00027523727, -0.00021704913] | original_json/full | 0.036381704 [0.007181222, 0.071980619] | 16/3 |
| hat−pipeline_pchip | -0.00024501101 [-0.00027523727, -0.00021704913] | original_json/observed_anchor_slab | 0.036381704 [0.007181222, 0.071980619] | 16/3 |
| hat−pipeline_pchip | -0.00024501101 [-0.00027523727, -0.00021704913] | original_json/exclude_reference_boundary_1mm | 0.030980474 [-0.0034809416, 0.072541755] | 17/3 |
| hat−pipeline_pchip | -0.00024501101 [-0.00027523727, -0.00021704913] | rtstruct/full | 0.037034794 [0.008048744, 0.072598788] | 18/3 |
| hat−pipeline_pchip | -0.00024501101 [-0.00027523727, -0.00021704913] | rtstruct/observed_anchor_slab | 0.037034794 [0.008048744, 0.072598788] | 18/3 |
| hat−pipeline_pchip | -0.00024501101 [-0.00027523727, -0.00021704913] | rtstruct/exclude_reference_boundary_1mm | 0.031037905 [-0.0028866129, 0.071817258] | 16/3 |
| swinir−raw_linear | -0.00034988553 [-0.00038733915, -0.00031466815] | original_json/full | -0.062913456 [-0.13509028, -0.0026867601] | 28/1 |
| swinir−raw_linear | -0.00034988553 [-0.00038733915, -0.00031466815] | original_json/observed_anchor_slab | -0.062913456 [-0.13509028, -0.0026867601] | 28/1 |
| swinir−raw_linear | -0.00034988553 [-0.00038733915, -0.00031466815] | original_json/exclude_reference_boundary_1mm | -0.012391994 [-0.0960802, 0.061721615] | 16/1 |
| swinir−raw_linear | -0.00034988553 [-0.00038733915, -0.00031466815] | rtstruct/full | -0.062288348 [-0.1338802, -0.0026779153] | 28/1 |
| swinir−raw_linear | -0.00034988553 [-0.00038733915, -0.00031466815] | rtstruct/observed_anchor_slab | -0.062288348 [-0.1338802, -0.0026779153] | 28/1 |
| swinir−raw_linear | -0.00034988553 [-0.00038733915, -0.00031466815] | rtstruct/exclude_reference_boundary_1mm | -0.012830227 [-0.096040396, 0.060024592] | 16/1 |
| swinir−raw_pchip | -0.00038239082 [-0.00042229011, -0.00034470441] | original_json/full | -0.10546354 [-0.17336251, -0.044981404] | 31/1 |
| swinir−raw_pchip | -0.00038239082 [-0.00042229011, -0.00034470441] | original_json/observed_anchor_slab | -0.10546354 [-0.17336251, -0.044981404] | 31/1 |
| swinir−raw_pchip | -0.00038239082 [-0.00042229011, -0.00034470441] | original_json/exclude_reference_boundary_1mm | -0.077793481 [-0.15683723, -0.0064579652] | 21/1 |
| swinir−raw_pchip | -0.00038239082 [-0.00042229011, -0.00034470441] | rtstruct/full | -0.10487024 [-0.1718094, -0.04469991] | 32/1 |
| swinir−raw_pchip | -0.00038239082 [-0.00042229011, -0.00034470441] | rtstruct/observed_anchor_slab | -0.10487024 [-0.1718094, -0.04469991] | 32/1 |
| swinir−raw_pchip | -0.00038239082 [-0.00042229011, -0.00034470441] | rtstruct/exclude_reference_boundary_1mm | -0.078218214 [-0.15592616, -0.0078347312] | 20/1 |
| swinir−pipeline_linear | -0.00023865466 [-0.00026726986, -0.00021240455] | original_json/full | 0.07701499 [0.012717691, 0.14558344] | 10/4 |
| swinir−pipeline_linear | -0.00023865466 [-0.00026726986, -0.00021240455] | original_json/observed_anchor_slab | 0.07701499 [0.012717691, 0.14558344] | 10/4 |
| swinir−pipeline_linear | -0.00023865466 [-0.00026726986, -0.00021240455] | original_json/exclude_reference_boundary_1mm | 0.10624974 [0.032702727, 0.17843334] | 9/4 |
| swinir−pipeline_linear | -0.00023865466 [-0.00026726986, -0.00021240455] | rtstruct/full | 0.077114099 [0.012022932, 0.1466474] | 9/4 |
| swinir−pipeline_linear | -0.00023865466 [-0.00026726986, -0.00021240455] | rtstruct/observed_anchor_slab | 0.077114099 [0.012022932, 0.1466474] | 9/4 |
| swinir−pipeline_linear | -0.00023865466 [-0.00026726986, -0.00021240455] | rtstruct/exclude_reference_boundary_1mm | 0.10434823 [0.030726735, 0.17621468] | 9/4 |
| swinir−pipeline_pchip | -0.00023828783 [-0.0002667137, -0.00021189876] | original_json/full | -0.015627545 [-0.079300011, 0.039036756] | 19/3 |
| swinir−pipeline_pchip | -0.00023828783 [-0.0002667137, -0.00021189876] | original_json/observed_anchor_slab | -0.015627545 [-0.079300011, 0.039036756] | 19/3 |
| swinir−pipeline_pchip | -0.00023828783 [-0.0002667137, -0.00021189876] | original_json/exclude_reference_boundary_1mm | -0.015296294 [-0.082841268, 0.042323963] | 17/3 |
| swinir−pipeline_pchip | -0.00023828783 [-0.0002667137, -0.00021189876] | rtstruct/full | -0.01523536 [-0.077303815, 0.039288376] | 19/3 |
| swinir−pipeline_pchip | -0.00023828783 [-0.0002667137, -0.00021189876] | rtstruct/observed_anchor_slab | -0.01523536 [-0.077303815, 0.039288376] | 19/3 |
| swinir−pipeline_pchip | -0.00023828783 [-0.0002667137, -0.00021189876] | rtstruct/exclude_reference_boundary_1mm | -0.015628135 [-0.081335134, 0.040453374] | 16/3 |

[58条真实复核](experiments/vs_seg_complete_analysis_cpu/independent_all_frozen_estimates_replay.json)、[逐患者主差CSV](experiments/vs_seg_complete_analysis_cpu/primary_patient_differences.csv)、[原完整自动报告](VS_SEG_FULL_VOLUME_COHORT_COMPLETE_RESULT_2026-10-02.md)、[原45完整合同](experiments/vs_seg_full_volume_cohort/run_contract.json)。
