# 第二次尝试：限定本阶段 checkpoint 字节读取

attempt01 的实际 tool session 64668 最终 chunk 3321ac / exit 1；连续 child exit 1。worker 实际完成 1 次人工更新/forward，写出第 1 步 checkpoint，随后给自身 checkpoint 做字节 SHA 时被 audit 错拦。父 receipt 的成功汇总仍为 0，不能将这个字段误写成实际 forward 0。原源码、计划、receipt、临时文件及 checkpoint 保留、不修写，未产生医学收益。

修正版另存 qualify_disk_worker_v2.py / qualify_disk_resume_v2.py / verify_disk_resume_v2.py，只修自身计划路径的 checkpoint 字节 hash 读取：连续模式允许自己 step001/step003；恢复模式允许原连续 step001 与自己 step003。真实 torch.load 仍仅恢复模式读原 step001，计数明确记录。不得读取旧权重、MRI 或其他资格尝试权重。仍使用原 training_engine 和磁盘原语；不变 PATCH、draw、模型、优化器或恢复断言。

新 attempt02 独立执行既定 15 次更新/forward，独立 verifier 读本尝试 9 个 checkpoint。整阶段包含已失败的 1 次后，计划实际累计 16 次人工更新/forward，成功值以工具退出和 worker 实测为准。阶段总磁盘上限仍 200,000,000 bytes / RAM 和磁盘仍各 8,000,000,000 bytes；失败文件纳入该上限。两次资格 wall 合计仍不能超过原 600 秒。没有新的 GPU/MRI 作业、没有正式充分适配预算。

上述失败是本地实现错误，没有自动审批拒绝。
