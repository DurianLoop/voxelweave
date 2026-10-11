# 全192tile同输入算子定位的执行补充

承接已冻结MATCHED_INPUT_OPERATOR_PROTOCOL.md，原case2/native_reference、19998 parent、原输入SHA不变。完整96batch，每batch2tile；CPU独立functional逐算子执行并重复一次，相同CPU输入传给生产GPU leaf module各执行两次。主字段49：原48叶模块加sigmoid；另明确增加3个max_pool辅助字段，52个字段全部记录，不把辅助字段冒称原48叶模块。torch.cat/跨层skip的CPU排列沿原独立functional；不重新运行真实GPU整条pipeline，因此不会产生新的完整GPU FOV概率。本轮原GPU SHA仅绑定上轮已结束重构的证据。

每字段记录shape/elements、CPU输入SHA、CPU输出SHA、GPU输出SHA、两设备各自逐位repeat、max/mean error、范围和最差位置。GPU输入传输后SHA必须与CPU输入相同；GPU module类型/配置及参数由实际同一production model核对。所有norm仍native、eps1e-5；FP32/TF32off/deterministic，参数不更新。三个pool辅助字段也是相同输入重复GPU/CPU。input统计和中间最大值不能代医学概率gate。

CPU参考每batch概率SHA必须与上轮已完成journal的相同batch SHA一致；所有tile概率加独立weight/native mapping，最终CPU概率SHA必须与原完整CPU FOV SHA一致，坐标独立float64误差<=3e-12/二值零差。这里没有“独立GPU整FOV通过”标志；full38=false，训练ready=false，无医学评分/GT。

GPU不同时常驻全部CPU中间层：每次只转移当前算子输入，取回两次输出，比较后释放GPU中间张量；CPU只保持reference flow/skip必要张量。journal<=3MB、共享FOV stage20MB；准备目录7MB未来余量和other22.8MB一并保留，RAM/disk各8GB。wall3600s，CPU1/interop1/below-normal；GPU启动free8192MiB、allocator<=min(10%,2.4GB/total)、peak2.5GB/runtimefree4GB。只操作本进程，不枚举或修改其他PID，不触及用户原训练、未见确认或lockedIXI。所有新增只写innovation，旧源/证据不编辑。

实际CPU参考tile forwards仍为192，因逐算子重复CPU工作量相当于384，但不能称又得到384个不同tile或患者；GPU实际是每batch52算子×2 repeat，不称为全网络tile forward。最终审核按96×49主字段与96×3辅助字段分别核对，并与已结束传播误差统计对照；local error不可逐层相加作因果结论。
