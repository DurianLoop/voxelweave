# metadata作业磁盘单位修复

v2 tool `52f33d` 真实 exit1，最终磁盘断言失败、未写 receipt。随后直接 DriveInfo 观测为 8,431,284,224bytes；旧 mc_rc_reference_resources_2026_10_07.py 第17行使用 8,000,000,000bytes 的 8GB 储备。本阶段误写成 8×1024³bytes（8GiB），高于已有合同。另存 v3 改为原 8,000,000,000bytes，其他120s、无数组与分组条件不改。失败源码/attempt目录保留。此修复不改变原训练、医学作业、GPU储备或科学容差。
