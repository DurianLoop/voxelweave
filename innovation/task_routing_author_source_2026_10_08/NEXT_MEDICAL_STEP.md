# 接续执行：先完成医学检验

本阶段不新增网络、医学适配配方或软件资格工作。继续观察原 session 99542，不重启、迁移或控制用户终端训练；各臂 19998、总 39996、累计 30h 的现有合同保持。只有工具真实 terminal exit0、两臂最终权重及来源齐备后，才能形成实际退出收据并使用已有 V3 入口。空输出、metadata 或文件出现均不能替代真实退出。

1. 真正满足最终入口后，执行 [evaluate_final_lossless_v3.py](../lossless_final_evaluation_entry_2026_10_08/evaluate_final_lossless_v3.py)。这是 CPU 评价；不依赖新 GPU 空闲。全部 28 series × 两臂 = 56 个完整 FOV 预测，含 11 开发患者/19 series 与已见 4 验证患者/9 series。
2. 主评价真正 exit0 后，依据实际结果另存 `OBSERVED_EVALUATION_EXIT_V3.json`，再执行 [verify_final_lossless_v3.py](../lossless_final_evaluation_entry_2026_10_08/verify_final_lossless_v3.py)。软件成功、六能力 gates 与独立 strict 分别报告，不混为医学成功。
3. 如能力通过，再依已备三 observed 臂 19 series 真实费用入口、另冻结充分适配配方、具体合法动作余量、全费用与强控制的顺序继续。收益为空或不稳定就记录负结果，不以新增包装或查新代替真实效应。
4. 方法、阈值、checkpoint、端点、动作和预算全部冻结后才开启 8 未见患者/12 series 一次确认。4 已见验证不称新确认，locked IXI 保持关闭。

GPU 授权有效。新增 GPU 作业仍须既定 8GB 启动、4GB 运行余量和 2.5GB peak 条件；当前 1394 MiB 余量不足。已运行的正式 CPU 训练不因此中途改设备。新文件只在 innovation，已有执行/绑定/冻结文件不改，RAM/磁盘各保留十进制 8GB，不删历史、不改环境。

本阶段采用小型 append 索引，绑定原 5430 份证据的完整 manifest/proof、lossless 的五份后附文件和前三次 watch 记录；后续医学阶段再纳入累积索引。原训练滚动 history/resume 不冻结。
