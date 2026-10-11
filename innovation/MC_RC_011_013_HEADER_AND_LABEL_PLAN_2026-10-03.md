# 固定011/012/013：来源头部与标签网格资格

在获取本批图像头或新标签体素前，固定[元数据角色队列](experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json)的3人全部5个T2系列：011/012各1，013全部3时点。230个API对象、预估114,887,092字节。按患者/StudyDate/UID排序，不能因来源失败换人、按图像内容或模型结果选series。此次只检查来源，不做模型前向。

允许官方getImage公共ZIP下载（含像素字节），仅用`dcmread(stop_before_pixels=True)`读头，不解码MR像素数组。复用预定all-IPP拟合规则：身份与SOP唯一、几何均匀、ORIGINAL无DERIVED、非MPR/reformat、均匀3D、spacing与thickness≤1.5mm；缺字段保持pending。每series最多180秒、socket30秒、并发1、总字节上限150,000,000、零自动重试。首传输/读头错误保留并停止；资格阴性继续检查原固定其余series，不能将阴性当工具错误丢弃。

从已有官方label ZIP核对精确路径、NIfTI形状/affine/语义与DICOM原网格；label可以解码用于来源资格和非空/合法值检查，不计算任务性能、不用于选模型/裁剪。3时点患者013始终一角色，若有厚层时点阴性也全部报告。几何通过仍不证明完全未见患者，完整跨来源身份、训练/验证/确认分组与任务网络能力另需冻结。研究发表确认仍为0。

仅写innovation，不干预GPU/用户训练/locked IXI test。自身单线程低优先级，磁盘15GB/可用内存8GB门槛。每次公开传输、失败、全部非像素头、来源网格检查和独立重读的SHA均归档；所有旧失败保持。
