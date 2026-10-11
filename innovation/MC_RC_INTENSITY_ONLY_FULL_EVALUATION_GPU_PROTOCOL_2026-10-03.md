# 单intensity-only GPU20k权重的完整能力评价

25991已实际exit0、单臂20000updates/errors=[]、最后checkpoint已冻结，训练内未开验证。CPU独立全20000draw/40000patch/权重认证脚本正在运行；必须取得真实exit0/complete=true/errors=[]后才能此评价。训练raw记录的metadata在arms[0]，新binding明确用核验过的单臂metadata转换，不借旧noaug schema读取错误权重。旧结果不覆盖。

同固定37条件：19开发raw PCHIP→四验证9series各raw PCHIP/raw linear，完整nativeFOV/全部z/.5/最后20k、标签在完整预测后加载。四域计数/空undefined/体积/full-affine边界、患者先series平均再等患者平均；六项原能力gate不改。独立111plane、全部label/bincount/affine与聚合核验用同架构，不是第二独立训练模型。八确认不开效果。

评价使用此前已认证GPUadapter的网络分支/CPU context/grid_sample/fusion/native概率映射。训练则在GPU算context grid_sample和loss；坐标来自相同CPUfloat32公式，已认证synthetic context误差2.98e-7、梯度7.28e-12、loss1.19e-7，但不声称所有患者训练/评价逐值等价或GPUbackward完全确定。相同接口/draw支撑和输入SHA保持；旧CPU训练与新GPU训练的效果比较仅描述，不是完整四因素因果控制。

GPU合成runtime原预检复用并认证，不重复做已通过无变化的库测试。CPU单线程/below-normal/15GB磁盘/8GB内存、GPU allocator10%/peak2.5GB/free4GB、初完整输入37总投影≤3600秒仍作为资源守卫；不按效果停止，不选择有利患者/checkpoint/阈值。输出新目录，失败保留，源/code/protocol/checkpoint SHA全量绑定。

这个配方是已见验证引导的能力开发，只有一个seed，不能说已独立确认。完整80k四因素仍未完成；此单臂不等于四因素结果。能力不足继续强基线，充分后再native/6×5公平矩阵/observable具体修正，最后冻结保留八确认与第二独立任务网络。
