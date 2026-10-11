# 配对采样与完整FOV资格的实际结果

继承执行的两项合成验证已真实exit0，分别为chunk3e7ef8和f9749d；本轮读取原结果及退出receipt，未重跑、未修改旧代码/原始结果。新增资格推进了后续公平比较的实现准备，尚未验证MRI病灶效益。

24组draw与旧sampler的几何/增强primitive相同，dense/direct共享draw，独立NumPy构造batch逐位一致，label/mask相同，输入不回写。原PATCH64x128x128、batch2，两臂各两步、恢复再重做第二步，共6次合成更新；梯度有限非零，model/optimizer/RNG恢复tree exact；更新权重仅在内存。

生产和独立functional推断均按每臂8tile完整覆盖FOV，physical概率逐位一致，native阈值差异0。使用此前冻结且含非零mask权重的合成checkpoint，mask置0造成概率最大改变0.0007798075675964355。这里证明两通道被实际使用，不证明mask改善真实任务。

| 检查 | dense | direct |
|---|---:|---:|
| 理想float64坐标绝对误差 | 2.0265579223632812e-6 | 3.2186508178710938e-6 |
| 旧absolute<=3e-6 | 通过 | **失败** |
| 事前combined atol3e-6/rtol1e-5 | 通过 | 通过 |
| 独立float32坐标解释器最大误差 | 1.7881393432617188e-7 | 1.7881393432617188e-7 |
| float64坐标与torchfloat64最大误差 | 3.3306690738754696e-16 | 3.3306690738754696e-16 |
| 各坐标重放阈值差异 | 0 | 0 |

坐标舍入诊断说明当前误差来源，不能覆盖旧strict失败。原一通道56FOV代码和判据不改；未来两通道真实评价须事前定义对应数值解释器。

readiness attempt01保留真实tool exit1及Python exit转交问题；attempt02真实exit3，complete=true/ready=false/errors=[]，属于预期deferred。缺原训练终止、56FOV和真实退出/独立证据；未打开MRI数组、未加载live权重、未初始化CUDA、未启动真实MRI资源资格。

原正式训练session99542仍live；本轮起始实际chunk9e00ad最后native6831，新增6732，累计14689.236578600015秒。PCHIP99仅旧快照。GPU已授权，19:55:40.114空闲1394MiB，未满足新GPU入口条件。8确认和locked IXI test关闭，claim仍未确认。

来源：[合成资格](experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07/attempt01.json)、[坐标诊断](experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07/attempt01.json)、[真实退出绑定](SESSION_OBSERVED_EXITS_PAIRED_SAMPLING_FOV_2026-10-07.json)、[只读入口结果](experiments/mc_rc_3d_paired_resource_readiness_2026_10_07/attempt02.json)。

