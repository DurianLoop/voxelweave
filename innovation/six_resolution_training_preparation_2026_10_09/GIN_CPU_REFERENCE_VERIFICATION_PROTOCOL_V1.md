# 独立 CPU 可微参考的人工核验

先实现CPU functional graph，独立显式nearest-exact母target索引、binary softplus loss、深监督4/7、2/7、1/7、attached mean-target KL。与既存原模型/原loss/原KL对照，人工shape(2,1,16,16,16)、3个固定GIN view、相同cold-init seed20261009，两步AdamW。原所有概率、scalar loss、54参数梯度、更新、162 optimizer state字段每step均核3e-6，step逐位同。目标和view不变，所有深监督target必须逐位同。

独立reference不import原模型或原loss来forward，使用functional conv/pool/IN/transpose和非重入checkpoint，输入与所有参数CPU float32。二值target的softplus表达式和显式xlogy KL不替换GPU production语义；失败保留，不放宽门槛。再进行真实病例资格前必须先通过这个人工实现检查。它只是参考实现准备，不代替真实batch64×128×128和完整19series。

CPU1/interop1/below-normal，RAM/disk各8GB，prep7MB/FOV20MB/other22.8MB完整余量保留，wall180s。MRI/GT/parent/CUDA0，不访问未见确认/lockedIXI，不安装或委派，不影响原进程。实际工具/每步参数检查/全部费用与版本bindings保存于新attempt，不修改历史。
