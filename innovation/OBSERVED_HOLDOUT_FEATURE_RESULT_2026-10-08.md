# 真实19系列的观测留出特征与独立核验结果

本阶段完成11开发患者／19系列／38固定fold的普通可观测特征资格。没有MRI病灶任务评分；这不是新的去噪算法、插值方法或理论风险证书。

患者等权（患者内series等权）normalized MSE：linear=0.284702296827，PCHIP=0.286547507866；差=0.00184521103912（0.648119%）。18/19系列、10/11患者差为正，VS-MC-RC-007是保留的负差。

| 患者 | series数 | linear MSE | PCHIP MSE | PCHIP−linear |
|---|---:|---:|---:|---:|
| VS-MC-RC-001 | 2 | 0.563912664 | 0.56904584 | 0.00513317662 |
| VS-MC-RC-002 | 2 | 0.237258353 | 0.23813926 | 0.000880906788 |
| VS-MC-RC-004 | 1 | 0.286804857 | 0.289256514 | 0.00245165655 |
| VS-MC-RC-005 | 2 | 0.159562812 | 0.160127652 | 0.000564840014 |
| VS-MC-RC-006 | 3 | 0.376904107 | 0.381484294 | 0.00458018642 |
| VS-MC-RC-007 | 1 | 0.211385557 | 0.211044063 | -0.00034149366 |
| VS-MC-RC-009 | 2 | 0.360302805 | 0.363431822 | 0.00312901697 |
| VS-MC-RC-010 | 3 | 0.269435964 | 0.270762821 | 0.00132685766 |
| VS-MC-RC-011 | 1 | 0.235798987 | 0.23629354 | 0.00049455274 |
| VS-MC-RC-012 | 1 | 0.189638892 | 0.190660235 | 0.00102134353 |
| VS-MC-RC-013 | 1 | 0.240720267 | 0.241776545 | 0.0010562778 |

先mask再用retained层统计／投影／预测，完成预测后才加入同retained统计的heldout reference；首末observed保留，奇偶内部层各留出一次。每fold仅改变heldout值+10000，source／两种完整预测SHA不变，而reference／scores改变。生产38和独立v2的38次完整检查均通过；原失败attempt另有5次已完成检查。81是检查事件，只有38个唯一真实fold。

生产19包，原独立失败3包，新v2独立19包，共41次加载、唯一19包；原失败只完成2完整series／5fold，第3series fold1的统计严格相等失败保留。生产C-copy与fancy-index数组布局的浮点归约顺序不同；另冻v2指定C-copy，未改原生产结果和3e-5容差，另用1e-12独立中心矩核统计。

完整source／prediction／reference及score共享库重放exact；独立float32坐标bilinear是样点检查，最大绝对误差1.03067545e-06；独立非均匀Hermite覆盖完整heldout数组，linear/PCHIP最大绝对误差分别4.76837164e-07/4.7683716e-07。共享库SHA重放与独立数学核验分开记录。

留出将每4层observed中的一部分去掉，改变间距和输入量；首末保留亦会产生非均匀间距。本误差包括完整面内背景，且归一化统计随fold变化；不能推出原x4缺层恢复、病灶分割或线性部署更好，不据此选winner。MRI magnitude无偏与噪声条件独立未证明；原部署从全部合法observed计算统计本来合法，只有heldout诊断的预测需要先mask。

已导出[19行可观测特征表](experiments/observed_holdout_feature_table_2026_10_08.json)，其中任务标签、动作收益、完整成本明确为null。后续必须与真实患者配对动作收益和实测成本连接，整患者cross-fitting；本表不含模型、native GT、验证、确认、lockedIXI或缺失MR。没有新增神经／GPUforward／训练更新。

[科学JSON](experiments/observed_holdout_feature_summary_2026_10_08.json)；[原协议](OBSERVED_HOLDOUT_FEATURE_PROTOCOL_2026-10-08.md)；[原失败](experiments/observed_holdout_feature_independent_2026_10_08/attempt01.json)；[v2布局协议](OBSERVED_HOLDOUT_FEATURE_LAYOUT_V2_PROTOCOL_2026-10-08.md)；[v2结果](experiments/observed_holdout_feature_independent_layout_v2_2026_10_08/attempt01.json)。
