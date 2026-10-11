# 图像双插值、原标签保留：CPU原型资格

来源为新读nbm70266主文blocks23–27：图像先rotation/scale后inverse，标签不变。作者主文只验证x-axis rotation、scale，没有给完整采样范围/概率、padding/坐标实现或全部成本。本原型是使用项目已冻结空间参数的探索，不称作者代码复现；不改原训练。

新增独立模块apply_roundtrip仅接收调用者已有x/y数组。用当前theta的3D物理inverse-sampling矩阵，再对完整齐次矩阵求逆进行第二次trilinear采样；不能把三个Euler角逐一取负当作同一顺序的逆旋转。GT逐位不变，两次图像采样均float64坐标/中间值、最终float32；zero padding、align_corners=False。零或disabled变换直接identity。合法训练时输入必须是已授权observed-PCHIP或其matched native能力臂，不增加部署缺层信息。

本次仅synthetic full production patch64x128x128：中心impulse、1-voxel细结构、边缘信号、constant/checker纹理；固定identity、single-axis rotation、三轴rotation+scale、disabled参数。形状/spacing/pivot显式记录（含anisotropic case）。不读MRI/GT/model，不神经forward，不CUDA或作者代码执行。

独立numpy物理坐标变换核theta/逆矩阵全角点与预选点误差<=3e-12；用不依赖grid_sample的八邻域两级标量采样oracle核固定点双插值概率误差<=3e-6。保留inverse矩阵composition及三轴neg-angle反例，GT/hash/input不变、finite、图像alias变化、边缘信息损失和零变换。32固定点不是完整全FOV独立核验，此原型通过也不是临床收益或训练推广资格。

CPU1/interop1/below-normal，wall<=120秒，stage累计<=5MB，磁盘/RAM各8GB储备。不保存全体phantom、训练state或大cache，只小JSON；不打开4验证/8未见确认及lockedIXI。若未来能力失败，先另立同预算三分支开发试验：intensity、普通spatial、image-roundtrip；需保持相同patient exposure/初始化/母GT/总更新并计两次augmentation额外费用，不能把已执行普通spatial臂中途改为新增强。
