# native接续失败：无更新诊断结果

主训练、独立核验及本诊断均实际exit0；MRI任务更新0，不评价四验证/八确认。

| 输入/模型状态 | 主head全部tile前景概率最大值 | 主head TP（tile实例） | 固定pair BCE encoder L2梯度 | 固定pair soft-Dice encoder L2梯度 |
|---|---:|---:|---:|---:|
| native_reference/initial | 1 | 10204 | 0.199972148 | 13.8400122 |
| native_reference/final | 1.0720867e-07 | 0 | 0.00555619946 | 2.39979496e-07 |
| raw_pchip/initial | 0.999999881 | 9859 | 0.0234561903 | 3.4735835 |
| raw_pchip/final | 1 | 13815 | 0.000572154202 | 0.00846437831 |

全部16tile、所有3个head、初始/最后checkpoint均纳入，未选择有利head或中途模型。重叠tile TP的分母是tile voxel instances，不是去重完整FOV。native最后三head均无二值预测，其前景概率最大值依次1.07209e-7、1.37078e-6、2.99730e-5。

native最后64步含前景的53batch平均loss1.010795；空GT的11batch平均.010529。PCHIP对应.007026/.007151。空batch低loss没有代表病灶拟合成功。

native初始主head权重范围[-6.22638,2.49883]，PCHIP为[-3.54885,2.43862]；固定pair native初始soft-Dice encoder L2梯度13.8400，最终2.39979e-7，而最终BCE梯度仍非零。这支持当前存在强负logit/极小soft-Dice梯度的优化状态，不能证明LR、IN、采样或初始化的唯一因果解释，也不证明作者方法问题。

下一对照只将恒定lr=.001降为.0001，两臂从原各自相同初始checkpoint重新运行同1024完整tile流；原gate和失败保留。此时不能启动有条件的19series资格，更不能打开确认病例。

[完整诊断](experiments/mc_rc_3d_backbone_collapse_diagnostic_2026_10_07/attempt01.json)、[训练端点](MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md)、[低LR预定协议](MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_CONTROL_PROTOCOL_2026-10-07.md)。
