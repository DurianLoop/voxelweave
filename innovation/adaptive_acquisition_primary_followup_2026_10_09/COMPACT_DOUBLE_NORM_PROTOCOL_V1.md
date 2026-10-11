# 降低 FP64 InstanceNorm 临时张量的独立版本

旧模型profile实际7b66f1 exit1：decoders.2.layers.1之前allocated1804156416/reserved1923088384，输入(2,16,64,128,128)FP64。原x-mean与再乘inv分别要求256MiB；峰值定位有真实trace与只读hooks，不改变旧模型。

新custom autograd：FP64 var_mean，前向仅创建x-mean的输出buffer，随后原位乘inv、乘gamma、加beta；不原位更改输入。save_for_backward保存独立CPU input/gamma/mean/inv副本。反向按batch与channel重建FP64 normalized input和逐通道dx，使用解析InstanceNorm VJP；dgamma/dbeta按batch累加，最终只向原dtype参数返回梯度。eps1e-5、affine、biasedvariance、原FP32parameter/AdamWstate不变。

只支持训练使用的一阶VJP，明确不支持二阶导；checkpoint与offload后续另验。先CPU独立显式中心化方差autograd对照output/dx/dgamma/dbeta，random/constant/nearconstant/sparse cases，FP32/FP64affine；原绝对3e-6gate。FP64三个参数方向做h1e-3/1e-4/1e-5有限差分，最小步长误差<=1e-8。之后才小图CPU/GPU、原fullpatch/保存恢复关系。constant与nearconstant也需有限差分，但固定h不适合其高曲率；另预先缩放输入方向1e-3再用相同步长，保留实际方向范数。

不安装、不降gate、不调eps、不钳制小gradient，不读取MRI/GT/parent，不初始化GPU用于本CPU数学阶段。CPU1/interop1/below-normal、RAM/diskreserve8GB及现有stagecap不变。
