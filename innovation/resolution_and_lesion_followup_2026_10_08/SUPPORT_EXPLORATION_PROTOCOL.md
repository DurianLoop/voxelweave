# 图像往返插值的支持范围资格（冻结在运行前）

问题：旧 prototype 在目标 patch 内连续做两次三线性采样，零填充会制造边界信息损失。标签保持原位不能消除这种损失。准备支持范围计算与两级采样原型，不修改原四分支训练。

给定旧物理变换矩阵 M，第二次采样为完整 M 的逆。将归一化坐标显式变到原 patch 的 xyz 体素中心坐标。由目标立方体八角确定第二次采样所需的 intermediate 整数格点范围，floor/ceil 外扩一个体素；再由 intermediate 立方体八角确定第一次采样所需的 source 整数格点范围。保持 spacing、pivot、变换相同，以两个不同格点范围创建采样网格，最后返回原大小图像和完全不变 GT。

支持范围计算函数不接收图像或 GT，输出是覆盖所需邻域的保守包围盒，不宣称最小 halo。pivot 若来自当前训练的 foreground crop，仍属于原训练监督，不宣称整个数据流程无需 GT。未来部署仅用合法输入定义的 pivot。

预写资格：生产大小 64×128×128、两组 anisotropic spacing、中心/偏心 pivot、identity/disabled、两组角度与 scale 的 stress 配方；独立物理坐标 oracle 3e-12、两级 8 邻域 32 点强度 oracle 3e-6；constant/非恒定线性梯度/checkerboard/wide 小结构合成图像；GT 全位不变，原源数组不改。对 constant，充足真实上下文的中心输出应保持 1；原 crop-only zero padding 作反例控制。有限 source 上下文不足必须明确报错，不能用复制边界或反射补造真实组织。

几何支持仅排除人工 crop 边界影响，不反演第一次插值、不保证薄结构纹理或诊断信息无损。成本包含扩大 source/intermediate 体素数和两次采样；不执行新的神经训练、不加载患者图像/GT、不打开验证/确认。

运行限 CPU 1、低优先级、wall 180 秒、新 stage 5 MB、磁盘/RAM 8 GB 储备。失败保留原脚本和 receipt，不改成成功。
