# 不改变旧模型的单图显存定位

上轮是实质进展：两步人工GPU/CPU通过；原fullpatch首路forward在FP64归一化临时乘法OOM。继续目标为可发表且独立确认的医学claim，人工数值通过不是目标完成。

本次只为旧high_precision_task_model_v2注册只读module pre/post hooks，记录layer名、输入/输出shape、仅本进程allocated/reserved与peak。与原成本测试相同的人工输入(2,1,64,128,128)、seed991、GINseed801、初始权重seed20261009；只跑第一个人工view的forward，不跑backward/optimizer/loss/GT。前向失败保留，成功也只认证该单图成本。

GPUaggregate admission8192MiB、本进程allocator min(10%,2.4GB/total)、peak2.5GB/runtimefree4GB、strictdeterministic/TF32off，CPU1/interop1/below-normal、decimal8GB RAM/diskreserve，原目录cap与wall180s不变。不枚举或改变其它PID，不动原终端，不读医学数组。
