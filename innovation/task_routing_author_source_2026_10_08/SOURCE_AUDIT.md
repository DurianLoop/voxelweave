# TADT 作者材料核查结果

本阶段完整读取了作者 README；没有取得可供审计的路由或训练实现。该结果限定于这次真实获取的作者网页和固定提交 README，不代表作者从未发布代码，也不能作为项目原创性的正面证据。

## 已读来源

- 此前已读论文 TADT，arXiv 2408.08736v2；本阶段仅复读第 1 页确认作者仓库，不计新论文或新全文页。
- 论文链接：https://github.com/Tillyhere/TADT 。匿名验证 TLS 的网页 GET 和 README GET 都实际返回 HTTP 200。
- 网页所示 main 提交：`74138572a1a0ac625927478d03db0f6d8036cc53`。网页根目录条目仅列 `README.md`，未另取得完整递归 tree。
- 固定提交 README：https://raw.githubusercontent.com/Tillyhere/TADT/74138572a1a0ac625927478d03db0f6d8036cc53/README.md 。完整保存 282 bytes，SHA256 `957bb0fad35f6a28ad712ef0699aa272f788eb0bd57bc243881991883a6410e4`。

README 全文说明其为 ECAI 2024 的 Task-Aware Dynamic Transformer 官方代码，并写有 **“Coming soon!”** 和联系邮箱。没有实现、命令或训练配置。本阶段没有使用邮箱发消息，没有下载权重、数据或执行作者代码。获取时的 `receipt.json` 中 `author_README_read=false` 是当时尚未阅读的真实状态，保留；本阶段的新增记录登记随后实际完整阅读。

| 核查问题 | 已有证据 | 保留的未知 |
|---|---|---|
| Bernoulli 与 STE 路由如何训练 | 此前已读论文方法描述 | 实际采样、梯度、训练和推断分支 |
| 关闭分支是否真正跳过计算 | 论文 FLOPs 表和此前算术复核 | 实际 kernel 调用、wall time、transfer 与选择开销 |
| 固定 β、静态模型是否公平训练 | 此前论文公开训练及消融描述 | 实际各臂曝光、初始化、预算和分支训练配方 |
| 作者结果能否按代码复现 | 本次只有 README 可完整阅读 | 可执行实现与结果复现 |

## 对 MRI 主候选的影响

继续保留“充分适配后，合法动作的真实病灶恢复价值及完整成本分配”作为待证伪候选。动态路由、预算控制或预计 FLOPs 减少本身已有先例。没有作者实现并不扩大本项目的新颖性边界。

后续比较仍需给强静态、双路径风险/误差、成本/defer、预算随机及 calibration-only 控制相同合法信息；分别报告训练曝光与部署完整费用。任务效益须来自具体动作后的完整患者配对端点，不能以路由熵、理论 FLOPs 或训练 loss 代替。作者实现细节保持未知，不据此指控论文不公平或无法复现。

## 实际范围与失败

本阶段新增完整 README 阅读 1 份，实现源文件阅读 0 份，新论文全文 0 篇，MRI/GT/权重数组加载和神经/GPU forward 均为 0。没有新的训练、head、action 标签、未见确认或 locked IXI 访问。

接续时一次读错 `identity.json` 文件名，实际文件为 `visible_identity.json`；PowerShell 报路径不存在后已正确读取，没有改文件。第一次不带 UTF8 的中文读取乱码，以及一次批量输出截断，不计完成阅读；后来用 UTF8 和有界输出重读了相关材料。无自动审批拒绝。

原 CPU 训练 session 99542 两次真实轮询均仍 live：raw 8613/8712，invocation02 累计新增 28413/28512。不能将这些值当作最终模型或把 invocation 累计当作 raw 单臂步数。GPU 已获授权，但实际 free 1394 MiB，不满足既定新 GPU 作业启动门槛。没有控制现有训练或其他 PID。可发表 MRI claim 尚未成立。

来源：[获取收据](identity_attempt01/receipt.json)、[固定提交身份](identity_attempt01/visible_identity.json)、[完整 README](identity_attempt01/README.source.txt)、[原论文阶段结论](../task_routing_and_reconstruction_shift_prior_art_2026_10_08/RESULT.md)。
