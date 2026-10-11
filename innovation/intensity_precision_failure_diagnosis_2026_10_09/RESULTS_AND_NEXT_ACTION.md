# 原完整检查失败后的诊断和修复

此前goal turn有实质进展：两篇新主文、原表/公式CPU核验与累计6441冻结来源。本turn第一真实poll观察74234整体093916 exit1，不是推测进程停止；原四臂29823仍live。

## 失败与来源

原full pipeline成功6216/35904后，下一字段case3（VS-MC-RC-002第二series）raw-PCHIP/step1868/patch0/throughplane，isolated和full-chain误差均3.814697265625e-6，超原3e-6门槛。primitive.enabled=false，pre/shared-post/support差均0，coordinate5.684341886080802e-14、binary/padding差0。

旧receipt SHA510724eb7b0b554bf0d0e426a74275afb918808a3d617ce2ed11b27804b1fdb5、config SHA12077e91e16a271b686376138264d413d4fbbb1717d427f9267847de856c9c69、journal SHA78a97242b31a7bf12fe22d427e80c8a96a0f6d86bf874af52f82e87302da48a6及83938bytes均保留。旧max_errors只记录6216成功前缀，不能用其2.861e-6忽略failed_field的3.815e-6。真实工具terminal已保存到旧stage新文件，旧脚本/独立reference/原training绑定不改。

[原终止前缀独立审计](failed_terminal_audit_attempt01/receipt.json) b4f36e实际exit0：独立构造完整35904有序身份，旧journal6216条为精确前缀，下一条正好failed_field，原成功gates/maxima/series和patient counts均匹配。它的audit complete只是前缀审计完成，original_full_qualification_passed明确false，29688字段（含失败）未完成。

## 数值原因与新版本

[单字段确定性诊断](failed_field_attempt01/receipt.json) 0e1ca0实际exit0，用原observed MRI/cache SHA及frozen geometry重构，不新增GT读取。两种resolution输入完全一致；gamma stage已达到3.814697265625e-6，bias后同最大误差。原生产float32 input mean=.5250039101、std=1.1292895079，float64=.5250039414/1.1292895347；powered mean/std的两精度也不同。完整字段上的mean64+sd64+原float32恢复运算与**旧不变独立reference**逐位一致。已保存witness和其他精度组合，不以ULP/相对误差放宽absolute门槛。

新production module [intensity_float64_stats.py](intensity_float64_stats.py) 仅将gamma前后均值/标准差reduce改为float64；shape、输出float32、归一化/power/restore、bias/noise和旧seeded primitives接口相同。独立reference SHA11f3946b80d7c687acb03fedc607881b6813a2982290e9588431ad96cc63c81e不变。新旧生产图像最大差必须如实保存，这不是要求与旧生产逐位等价的兼容性补丁；数值资格仍以固定独立reference/3e-6衡量。

40完整synthetic×switch组合在实际423e7b时已通过、isolated/full-chain0；后续原228真实stress+3失败回归共271正式47298继续。7c9575快照205字段中，原失败三个mode的isolated/full-chain均0，累计full-chain1.9073486328125e-6，新相对旧生产最大差3.814697265625e-6。该快照不是全271完成，真实terminal后的独立identity audit另行保存。

## 后续仍是完整医学目标

271整个exit0且无session_id、独立audit后，才运行 sibling full_real_intensity_v2_2026_10_09 中完整35904新harness。b96d3a/363a5d实际exit0仅证明准备、源码绑定/语法和原field loop未改变，没有运行MRI/模型。重新全部字段，不继承旧6216成功prefix；保留所有患者/轴/patch、3e-6/3e-12/二值0。原failed success-audit不冒用，新终止audit绑定新实际session ID。full目录2MB、journal1.5MB、CPU1、wall32400秒和磁盘/RAM8GB保持。

原四臂最新65074c仍live，第四1540/2992；全四真正结束先四last2992/11968日志/每患者272，再36 production+36functional完整FOV医学评价。新普通三control后续如使用v2，intensity-only、resolution、roundtrip各臂全用同v2和same parent/schedule/update，以隔离resolution因素；不把旧legacy Γ四臂与新v2增强差都归因low-pass。新数值repair没有证明模型能力或病灶收益。

创新主线不变：先充分任务能力和真实动作余量，再验证采集可见性对具体动作病灶损害差/全费用的增量价值，并比较同信息/容量/监督/预算的强QC/error-cost/defer/static/random/去采集控制。已有spacing/latent interpolation/收益头等先例继续约束算法首创表述。全11GT父模型不能冒充严格LOPO初始化。

11开发患者/19series，已见4验证/9series不用于选此精度，8未见确认12series及lockedIXI保持关闭；本turn没有患者医学评分、神经forward或新训练更新。GPU授权有效但free1394MiB仍未到8192MiB起跑条件；原CPU任务不迁移、不查询/干预其他PID。储备外约30MB仍不足后续严格LOPO权重与全费用，医学评价3MB保留。科研goal active，尚无独立确认发表claim。
