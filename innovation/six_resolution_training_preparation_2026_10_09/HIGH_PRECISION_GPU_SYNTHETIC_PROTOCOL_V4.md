# 保留严格确定性的池化版本

V3 actuald88ffe exit1/no session，严格 deterministic algorithms 在 max_pool3d_with_indices_backward_cuda 停止；其 CPU/GPU optimizer updates 都为0。保存原失败，不关 deterministic、不使用 warn_only。

high_precision_task_model_v2 使用不重叠 2³ 窗口 reshape/permute 后 max(dim=-1)，保留 z/row/column 顺序与 first-maximum tie 规则。先在 CPU FP32/FP64 上分别以随机值、全相等值、重复最大值验证 native pooling 输出与全部输入 VJP bitwise 一致。非重叠窗口使每个输入只属于一个输出窗口。

V4 绑定上述 CPU 检查，GPU 使用 v2 模块图；独立 CPU reference 仍使用原 native pooling 与中心化归一化，其他初始化/人工输入/target、两步54参数/162state、3e-6及binary0、严格 deterministic 和资源限制全部不变。新 attempt04，与原 FP32/真实医学资格隔离。完整 graph GPU 验证才可证明该分支在这套人工输入上通过。
