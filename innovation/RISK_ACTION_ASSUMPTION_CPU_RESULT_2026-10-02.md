# 固定缺层收益代理的合成审计结果

预先固定的三个合成审计全部完成；完整协方差SURE差和独立重复的noisy-target差与准确期望相符。对角噪声近似及共享重复噪声则能改变固定动作收益的符号。该结果只验证已知数学条件，不是新理论、真实MRI结果或可发表claim。

[执行前方案](RISK_ACTION_ASSUMPTION_CPU_PLAN_2026-10-02.md)、[CPU程序](experiments/risk_action_assumptions_cpu.py)、[输入合同](experiments/risk_action_assumptions_cpu/run_contract_attempt_01.json)、[全部准确式与随机结果](experiments/risk_action_assumptions_cpu/attempt_01.json)、[独立复查代码](experiments/verify_risk_action_assumptions_cpu.py)和[复查结果](experiments/risk_action_assumptions_cpu/independent_quadrature_verification.json)保存。没有读取当前45例分数、患者图像或运行网络。

## 固定phase的缺层风险

16维向量、四个phase-0观测，b=0，δ只在12个缺失坐标为1。两个真值x+=δ、x-=−δ有相同观测、同一b/r。完整均方误差收益b→r分别是+0.75和−2.25；两者的观测/投影误差都是0。故这套观测代理一般不能识别未观测位置的动作收益。数值是合成强度，不是患者NMSE单位。

枚举四phase时，与mask无关的固定误差可由inverse-probability weighting恢复全风险。对在每个mask观测位置都为0的mask依赖误差，平均完整MSE=.75，平均加权观测MSE=0；平均投影却是full rank。这仅提醒随机mask平均时不能省略估计误差与mask的关系，不是对ENSURE另置完整证明的复现或反驳。

## 协方差与重复监督

以下是八维合成实高斯、σ=.4、预写线性b/r的准确期望。收益为平方误差之和的减少，正数才有益，未按坐标取均值。

| 同次观测空间相关ρ | 真实收益 | 完整协方差SURE差 | 只用对角协方差SURE差 |
| ---: | ---: | ---: | ---: |
| −.6 | +.112 | +.112 | −.272 |
| 0 | −.080 | −.080 | −.080 |
| +.6 | −.272 | −.272 | +.112 |

完整Σ公式处理了这些相关性；不能把对角公式的失败说成所有SURE都失败。实验无需估Σ，已知Σ只是预写合成合同，不替真实CISS提供噪声认证。

| 跨重复相关γ（同次空间ρ=.6） | 真实收益 | noisy-target收益 | 期望偏差 |
| ---: | ---: | ---: | ---: |
| 0 | −.272 | −.272 | 0 |
| .5 | −.272 | −.080 | +.192 |
| 1 | −.272 | +.112 | +.384 |

γ=0时各次内部虽有空间相关，两次独立仍可估收益；γ=1表示完全共享噪声，能反转判断。这是噪声重复模型，不能据此测量/宣称HAT和SwinIR输出具有某个γ或与两次独立扫描等价。

每条件200,000次、六条件、同一固定种子，单线程NumPy，全部模拟均值在执行前指定的六标准误实施容差内。这个分母不是患者数，也不是发表显著性。独立程序不导入主程序，用标量Gaussian quadrature枚举270个配置核40个准确比较，最大差2.78e−16、零错误；它核准确期望与保存的随机汇总，不声称逐条重新播放全部随机draw。

## 对后续工作的影响

三篇[正文核读](literature/2026-10-02_risk_action_fulltext_collision_matrix.md)已有风险参数选择、random-operator自监督和独立重复监督先例。可继续的候选仍是用实际开发患者真值检验局部修正收益是否有足够空间且可预测；oracle、相关噪声数学和档案核验通过均不能放行一个缺数据/未排重的新GPU方法。
