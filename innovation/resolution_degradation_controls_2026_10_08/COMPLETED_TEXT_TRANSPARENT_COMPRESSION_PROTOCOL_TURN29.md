# 已完成离线文本的透明物理压缩，不改逻辑证据

只读ab1e96已由当前6376冻结链筛到29份离线文本、逻辑28,116,603bytes。新probe9bbd20真实exit0：逻辑8192byte和SHA不变、分配8192→4096、FILE_ATTRIBUTE_COMPRESSED=1，确认无需管理员权限的compact.exe可用；fsutil旧Access denied失败保留，不提升权限。

执行只限已冻结清单可验证的、131072..4000000bytes、未压缩且非只读/加密/sparse的文本。范围：旧archive/index/tool-observation/provenance公开记录或literature/extracted和search_snapshots；排除整个本stage、data/tools/experiments、原spatial训练目录以及任何training_attempt组件。扩展名限.json/.txt/.html，无MRI/GT/model/PDF，任何新/滚动训练或资格输出都不在候选内。实际29路径事前保存gzip计划，并逐项对原冻结逻辑bytes/SHA核验。

每次compact.exe /C /I /Q仅一个核验后的D:/MRI/innovation内绝对文件，不递归、不通配、不移动/删文件；不编辑文件内容或路径。压缩只改变NTFS的物理表示和compressed属性，常规读取的原字节和所有冻结SHA必须严格相等。没有对其他PID查询/控制或训练脚本/参数/模型/输入修改。无法压缩的条目保存错误，不解除只读、不强制其他操作。

CPU1/本进程低优先级、wall300秒、单compact timeout20秒、逻辑处理上限30MB、输出25KB。开始/每文件/结束核磁盘和RAM8,000,000,000bytes；本stage5MB并保留full日志至1.5MB、审计150KB和后附100KB。新物理节省只按GetCompressedFileSizeW前后计，workspace free另报可能同时受其他任务写入影响，不冒充源内容删除/数据减少。完成后另全6376来源归档核验，确认原冻结字节保持。

本次目的仅改善已有实际存储不足；即使节省成功，也必须fresh预算预测才能新训练，不能以压缩替代GPU8192MiB、完整MRI数值资格或六医学门槛。123,691,414bytes为22同架构LOPO task last文件的最低预测，未含日志、其他QC/收益模型、原子临时及完整标签生成成本，不宣称已具备整个科研所需容量。发表goal仍active。
