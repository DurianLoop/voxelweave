# 两通道表征的独立核验范围

在主资格真实 exit0（chunk82fbfe）之后，固定以下核验；不改变主资格程序、输出或既有训练。只访问19开发observed包、开发元数据、已冻结表征SHA和合成checkpoint。不加载MRI GT/native/验证/确认，不推断MRI任务。

逐series独立从observed数值计算float64 mean/std，再转换float32 normalized observation；直接构造native binary mask/zero numerator并匹配主SHA。独立pixel-center坐标从native shape与physical shape推导，不调用physical_mr。512个预固定SeedSequence[20261007,703,index]随机physical坐标，加每个native anchor相邻的physical z及r/c中心/边界；8邻点float64权重，比较主qualification SHA绑定的新映射值（主physical_mr只作待检对象）。预固定误差atol3e-5/rtol3e-5，因原torchfloat32坐标舍入，不将float64理想坐标要求逐位一致。重新检查全volume SHA及两输入共同availability。

模型独立解释器为既有functional_forward，使用canonical seed20261007一通道权重，显式添加432个零mask权重，不调用two_channel_model。用同已冻结合成direct step0数据，分别按3个输出独立算BCE+smoothed Dice及4/7,2/7,1/7深监督；每参数梯度有限，进行AdamW .0001/.0001一次。要求其model/optimizer/torch_rng/full checkpoint tree与主资格保留的direct_after1逐位相同。随后functional step1，最终model SHA与主资格direct final SHA逐位相同。两次都是合成更新，MRI更新0；不称泛化或病灶效果。

CPU4/interop1、float32、自身below-normal，600秒、8GB RAM/磁盘余量，新增输出≤5MB，无CUDA。把真实tool exit/result SHA另存receipt。主资格已证明两臂resume；本核验独立复现其中direct一路的模型、loss、optimizer与checkpoint。
