# 3D 标签坐标第二次预检

首次3D输入预检实际 exit1，前三系列通过，第四系列 VS-MC-RC-002 / 1.3.6.1.4.1.14519.5.2.1.76141570754740903352816737277274474217 标签 replay 失败。源native标签没有问题；native参照全28源核验仍通过。

重新直接观察：native z36 → target z58，output index43 的中心nearest位置应选择 native index27，torch CPUfloat32 nearest-exact却选26；512→520的r/c轴没有不同。旧 target前景1976、整数坐标参考1870，差异120voxel。padding z前3层使差异在padding后index46出现。保留旧输入预检和旧3D支持源码/协议全部SHA，不将失败冒充成功。

第二次新label模块按 nominal align_corners=False 中心语义选择 floor((j+.5)*n/m)，采用 ((2*j+1)*n)//(2*m) 的 int64计算保证半格tie选择上侧index。空间定义/GT来源不改变，不使用GT选择规则、不更改原评分门槛；纠正的是浮点tie的实现差异。独立oracle用有理数 Fraction逐坐标求floor，不依赖Torch resampler或生产函数。全体输出标签需逐值相等，不放宽gate。

正式3D模型和sampling/inference本体沿原候选，无已执行GPU更新。这只是预处理可靠性修复，不声称nearest/整数坐标重采样是本项目的可发表创新。深监督的patch到decoder分辨率均为整数2/4比例，可保留Torch nearest-exact；须GPU preflight检查梯度和实际输出。
