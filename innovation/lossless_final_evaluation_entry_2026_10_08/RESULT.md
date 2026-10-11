# 最终评价无损存储入口的实际结果

新CPU主评价/独立重放V3已准备并通过无损预测存储资格，**真实MRI评价尚未执行，可发表MRI claim未达成**。这是当前磁盘资源导致的必要入口修复，不是新增科学模型或重复FOV/神经数值合成资格。

旧入口56份预测使用未压缩np.savez：packed内容115,491,840bytes，加56×1348bytes容器为115,567,328。482af5实际metadata/资源检查显示当时8GB储备外115,671,040bytes，仅比预测文件多103,712bytes；按当前history增长约9.73MB和最终raw权重约5.62MB估算，未来旧入口约差15.25MB，还未计评价JSON、临时写和训练原子resume约16.88MB瞬时副本。后者是条件估算，不是未来文件大小保证；本轮不动原训练、不删历史、不放宽8GB储备。

V3仅将二值预测容器改为np.savez_compressed，输出与源码绑定另立版本。生产writer/reader和独立算法资格e54f9e真实exit0：

- 14组合成输入，覆盖1/7/30/105非整字节shape、空背景/全前景、随机、非连续反向view和来自既有metadata的最大native shape512×512×144。
- 两writer产出的四个.npy成员逐byte一致；两真实reader分别读取两种格式，共56次精确相同，padding bits为0。合成大预测只留内存，不落大文件。
- scientific函数及主评价/独立重放main经AST比较，除文件路由/source binding和无损序列化外算法一致；所有原threshold、六gates和独立strict保持。
- 结构化最大shape合成例4,719,940→9,009bytes，ratio0.0019087；随机例4,719,940→4,720,994，反而增加1054bytes、约0.0223%。随机例写入+自检.1197→.2388秒，不能称推理加速，也不能由结构化例推断真实MRI压缩比。

V2独立readiness1a864d实际exit1，原因是新目录缺experiments import path。已保留V2及原BUILD_RECEIPT，另存V3显式设置路径。V3由482af5独立真实子进程运行，probe脚本exit0，内部CLI实际exit3：缺最终actual-exit receipt、成功terminal result、两last19998冻结和raw final。MRI/GT数组加载0、CUDA未初始化、医学输出目录未创建；这是正常延期，不是医学效果或gate失败。

主医学执行命令和全部前置条件见 [MEDICAL_EXECUTION.md](MEDICAL_EXECUTION.md)，资格见 [receipt](compression_qualification_v3/receipt.json)，实际延期与空间账见 [probe](readiness_probe_v3/receipt.json)。最新fe6f95仍返回live session99542、空输出而无terminal exit；此前a5372d原训练raw7920、新增累计27720、wall64132.80965880002秒。空输出不表示停止。c69eea GPUfree1394MiB，原终端/其它PID未干预，根.gitignore/environment.yml SHA保持。没有新MRI/GT/权重数组、神经/GPUforward、训练/head/action labels，8未见和locked IXI未打开。goal active。
