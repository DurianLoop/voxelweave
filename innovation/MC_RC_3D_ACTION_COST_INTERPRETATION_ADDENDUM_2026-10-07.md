# 联合支持增量与串行执行成本的区别

原probe协议与代码已运行，保持其SHA不变。本补充解释字段，不改动原输出。

对预先确定、一次联合执行的集合S，固定batch足迹的保守调用数是 `C_joint(S)=|union R_a|`。这类coverage成本一般是单调子模函数，属于已知集合代数，不是新理论；它也不是Golovin/Krause的可加item cost。

原JSON的 `marginal_second_after_first` 仅表示 `C_joint({a,b})-C_joint({a})` 的支持集合增量。它不表示已经执行A之后，再改变输入执行B的真实成本。新的输入使共享batch缓存失效，必须重新推断；采用逐步执行的策略要累计每次更新的实际重算batch、候选评价、模型生成、聚合、搬运与cache初始化成本。

同样，在获取真实候选标签时全量评估7非空组合，真实调用数是各状态推断调用的总和。本轮实际116forward/232tile包含baseline、baseline repeat、7 full、7 cached、production联合参考；不能写成本轮只用了ABC联合的7forward。

混合native概率响应非零并不直接识别神经非线性。相互不影响同一tile的动作，在tile概率可由singleton逐位拼接后，剩余native残差可由后续聚合/float32回映/差分舍入解释。后续须对窗口级碰撞和数值原语单独检查，阈值预测和任务效益另报告。
