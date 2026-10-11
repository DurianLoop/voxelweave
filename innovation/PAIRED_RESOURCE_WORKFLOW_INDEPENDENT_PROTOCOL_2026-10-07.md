# 配对资源 workflow 独立核验协议

只读取上一实际合成运行 attempt01.json、8 份 source_snapshot 及对应源码文本。禁止 MRI/权重读取，不 import 生产执行器、torch 或其他神经模块，不重跑训练。用 NumPy 独立生成固定合成字段（seed 20261007+710）、两个 UID；按 seed sequence [20261007,813,step] 重建三批监督 draw；独立 crop/float32 affine/翻转重建两臂六批 x/y SHA。核输入 SHA、监督一致、第二步恢复记录、有限非零梯度记录、计数、固定 FOV tile/高斯 coverage 和重复 metadata/source SHA。

神经权重及概率数组未落盘，故不宣称独立重放网络 forward、梯度或完整 checkpoint tree；这些只核原运行记录及内部一致性，继承此前独立 FOV 解释器资格。新 verifier 必须真实 exit0 才记录 observed exit receipt。任一失败保留文件，新 attempt 修正，不覆盖原证据。
