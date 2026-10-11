# anchors-only × 归一化：三个固定开发患者的CPU任务机制预检

这是新合同的开发机制实验，不是新SR方法验证。原45CISS全部已见，科学独立确认0。固定患者与归一化预检相同：VS-SEG-202/203/204，不按post Dice或本轮bandwidth结果挑人。只在原post队列45人、18端点及保存预测复核全部完成后启动，不重跑旧baseline。GPU、用户训练、locked IXI test、根环境/.gitignore不操作。

预备证据：45人解析bandwidth与90旧数组/855间隔复核通过；三个患者的six fixed-stats对照使missing/tail网络前输入逐位不变。第一normalizer试验最后的torch导入检查失败，追加修正版实际通过，首失败保留。

每人固定新增4次官方冻结分割CPU forward，12次总计：

| 条件 | 基线缺层 | anchors | 任务NormalizeIntensity |
| --- | --- | --- | --- |
| raw_anchor_own | raw PCHIP逐位相同 | observed-only256 down/up | 该干预自己的整volume均值/std |
| raw_anchor_fixed | 与上行同一原网格数组 | 与上行逐位相同 | 固定原raw PCHIP基线均值/std |
| post_anchor_own | mixed post PCHIP逐位相同 | observed-only256 down/up | 该干预自己的整volume均值/std |
| post_anchor_fixed | 与上行同一原网格数组 | 与上行逐位相同 | 固定原mixed post基线均值/std |

全部tail不改。改变anchors的四条件不满足observed-preserving合同，不能用其Dice直接声称SR改善。fixed条件先通过authenticated MONAI完整加载环境中的真实NormalizeIntensity逐位input检查，再前向；own条件使用原全volume流程。其余RAS、checkpoint、Gaussian窗、阈值、labels和指标与原任务合同相同。

保留两标签 × full/slab/去reference1mm边界全部结果，core为空为undefined。逐患者保存12张完整预测，独立confusion/真实spacing的full-grid物理边界核验；不重复12次神经推断来冒充科学独立确认。不读取动态子集新Dice；全12完成后才比较以下six contrasts：raw_own−raw、raw_fixed−raw、post_own−post、post_fixed−post、raw_own−raw_fixed、post_own−post_fixed。逐人和3人平均描述，不bootstrap显著性或familywise claim。主要关注JSON full的post_fixed−post，但两个标签和全部域不能挑选。

本pilot回答能否用实际任务反应区分anchors介入与global normalization影响；不能从3人诊断宣布病灶/临床因果。之后是否做全45须另冻结开发方案，不把pilot中最好条件当独立确认方法；新科学claim仍需来源合格且未用于选择的患者、第二/适配任务模型、强原网格基线。

CPU单线程、只调自身低优先级，每个forward前磁盘15GB/可用内存8GBgate；任一失败保存首日志、停止该队列，不自动重启。所有文件放innovation，新队列可运行较久，必须用真实poll确认状态。
