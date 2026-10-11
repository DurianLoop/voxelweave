# 接续拟合执行预算（训练开始前冻结）

CPU 资格实际 exit0：1线程中位 3.4892742 s/update，4线程中位 1.5942602 s/update；4/1=.45690306。初始 sigmoid 最大数值差异通过 <=3e-6 门槛。12 次测试更新全部丢弃，不接续这些权重。

依据 `experiments/mc_rc_3d_cpu_thread_qualification_2026_10_07/attempt01.json` 选择 4 intra-op 线程、1 interop，自身 below-normal。正式本次两臂各 1024 次所有参数更新，共 2048；预计纯更新 3265.04 秒，允许总墙钟 5400 秒，保留评估/写盘和实际波动余量。不是完整19series训练预算，也不代表 GPU 资格。

每臂从 `mc_rc_3d_all_tile_head_fit_2026_10_07` 相应最后 checkpoint 接续；AdamW 新优化器，恒定 lr=.001、weight_decay=.0001，原 BCE+Dice deep supervision。tile顺序由 seed20261007 的128个独立16tile permutation事前产生；相邻两tile为一batch，每轮全16tile无删选，两臂完全一致。保存完整 1024 history，最终 checkpoint 和固定训练crop/完整FOV四域端点；两个最后 checkpoint 均冻结后再评估，不选择最优模型。

任何原 gate 失败仍失败。single001成功仅是已见训练系列能力，不打开4验证和8确认，也不以 native-PCHIP 差异声称 SR 损害。全部新输出 <=120MB；RAM/磁盘各保留8GB；不初始化 CUDA。
