# 最终评价的无损预测压缩版本

上一轮MIRTO精读/CPU审计属于实质progress，但不是MRI claim。接续真实poll113721确认session99542仍live（raw7623/new27423/wall63439.549753700034秒），e80cef GPU free1394MiB。医学主评价实际是CPU4 intra-op/1interop，不依赖GPU空闲；真正前置条件仍是两最后19998权重、39996正式更新、真实terminal exit0与来源/历史认证。GPU正式资源后续仍遵守原8GB启动/4GB运行/2.5GB peak；不操作用户原训练或其它PID。

当前磁盘8GB储备外约116MB，而原56预测packed原始115,491,840bytes且使用np.savez（不压缩）。native/raw长程history继续增长、raw final尚未创建，不能据当前数字保证旧入口存储够用。**这是真实资源导致的新问题，不重跑既有数值/网络合成资格，也不新增模型/head/动作标签。**

新版本仅将pack_prediction的np.savez改为np.savez_compressed，并将主评价/独立核验的输出、退出receipt和源码绑定指向本目录新版本。shape、little bitorder、array SHA、所有概率/预测/计数/aggregation/六gates、τ=.5、完整56FOV、4验证/8确认身份和strict 3e-6/3e-12/0阈值差异不改。源文件和原协议全部不回改；生成时逐项记录精确替换和diff，资格时以AST核科学函数和原独立核验算法同一。

压缩资格仅测试新旧生产packer/两真实reader的lossless互操作、非整字节padding、noncontiguous布局和合成最大真实shape（只读既有shape metadata）。使用BytesIO保存合成结果，资格过程只对file-like reader添加seek(0)适配，不改生产源码。所有合成payload内部数组/metadata精确相等并跨reader可读，实际压缩/解压wall单列；不是神经推断速度或MRI compression收益保证。保留不可压缩随机预测的膨胀/耗时，不能以结构化样例证明真实56例的全部空间或预算已够。

新生产入口须同时绑定压缩资格receipt和其所绑定全部源码，未资格化/来源变化不得读最后权重或MRI。readiness-only仍不加载MRI/GT数组，不初始化CUDA，不创建医学输出目录。两final真实未齐时实际返回deferred/exit3，不造退出receipt。不运行医学评价、独立核验、三臂资源或确认患者，直到各自真实前置条件满足。

本准备stage保存30MB内、below-normal/CPU1、120秒；资格只内存合成数组，不写预测测试大文件、不安装环境、不删除历史。真实主评价/独立核验沿原每步3600s和共享医学保存250MB，RAM/disk十进制8GB guard原样；本新版本仍可能在真实存储或实际时间不足时失败，完整保留而不放宽guard。只有真实最终模型的完整能力和strict都过，才继续充分适配/action-value/匹配强控制，MRI发表claim尚未达成。

[原执行协议](../MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_EXECUTION_PROTOCOL_2026-10-07.md) · [既有资格结果](../MC_RC_3D_FINAL_EVALUATION_ENTRY_PREPARATION_RESULT_2026-10-07.md) · [MIRTO控制准备](../realized_false_positive_task_prior_art_2026_10_08/PATIENT_TASK_CONTROLS.md)。
