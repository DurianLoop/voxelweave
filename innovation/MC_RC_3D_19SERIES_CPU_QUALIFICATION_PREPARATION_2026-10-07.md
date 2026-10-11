# 全19开发series的CPU资源资格：条件准备

这份文件是下一阶段准备，不是正式19series训练schedule。只有当前单001两臂原拟合gate全部通过、独立module/functional及生产坐标重放通过、主训练/核验实际exit0后才允许执行。float32与NumPy坐标严格差异若仍失败，必须另列保留，不用float64通过改判。八确认和四验证的MRI/GT不加载。

动机：当前4线程速度来自单001固定tile，不能直接当作19series随机采样的真实时间。若GPU仍未达原8GB启动条件，可先测真实多患者CPU流，避免未经估时启动十几小时以上的训练。GPU资格/门槛和已有入口保持。

CPU资格预定：4 intra-op/1 interop、自身below-normal、float32、无CUDA；读取全部11开发患者/19series的认证native、observed-only PCHIP与既有native监督，物理grid不变。两臂分开缓存，不向磁盘新增体积缓存；RAM/磁盘各留8GB，新输出<5MB、总墙钟<=1200秒。

事前生成患者均衡流：患者ID固定排序，患者内series按UID排序再用seed20261007独立置换；轮数取最大患者内series数，每轮11患者各出现一次，患者顺序按独立同种子置换，患者内series循环。因此全部19series至少一次、每患者更新数相同。两臂共享该流，batch2仍用既有FG/背景中心clamp与三轴flip/强度增强，逐batch独立同种子，保证label/augmentation一致。资格记录真实series、batch的input/label SHA、FG计数和全部augmentation primitive。

各臂从本次最后单001checkpoint载入，AdamW新优化器 lr=.001/weight_decay=.0001、原三尺度BCE+Dice。只用于计时/有限值/梯度资格，全部更新最终丢弃，不保存更新后checkpoint，不评价任务效果，不与正式训练累计，不根据loss判断能力。记录cache加载、真实sample_batch、forward/backward/step、总update时间；逐batch检查资源。

通过条件：全部19series均覆盖；两臂患者流/增强/GT完全一致；所有loss/梯度有限、各encoder/decoder/ups/head分支第一次梯度非零；所有预定更新执行；未初始化CUDA；资源门槛未破坏。此资格不是强任务能力，也不授权读取验证/确认效果。后续用实际中位数/最大时间以及两臂19series完整推断成本，另立正式预算；不能照搬单001或纯更新下界。现有局部统计原型没有整网资格，仍不得加入本次训练。
