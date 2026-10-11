# 后续12患者来源资格与记录曝光核查

上一轮是实质进展：3论文、全45输入统计及固定011/012/013来源预检完成，但独立确认claim仍0。本轮继续原科学目标，不以更多归档文件或来源preflight充当成功。

本方案在获取新MR头/labels前，固定现有候选71人中去除已见8开发人及已完成011/012/013来源预检后的字典序前12人：015、019、020、022、024、025、026、027、028、029、030、031。全部25个labelled T2系列，不按header结果、标签大小、任务Dice或manufacturer筛系列。API1475对象、615,515,656预估字节，公开ZIP总传输上限800,000,000；单连接、180秒每series、30秒socket、无自动重试、首工具/传输失败保存并停止。阴性资格继续报告原固定名单。

每次传输前检查磁盘15GB/可用内存8GB底线，自身CPU单线程低优先级。官方getImageZIP含像素字节，dcmread(stop_before_pixels=True)只读取MR非像素头；不解码MR像素、不调用模型/GPU、不操作用户训练，不读locked IXI test。只写innovation。

复用已冻结的all-IPP物理拟合、ORIGINAL无DERIVED、均匀3D、无MPR/reformat、spacing/thickness≤1.5mm门槛。对全部25官方label精确UID/PatientID/StudyUID/路径检查，用流式label读取核对binary、非空、qform/sform及原网格。首实现失败保留，修复追加proof；不得改科学门槛。全部raw230+本批1475头及labels的独立重读另存。

同时核查全项目文本/目录中MC-RC患者的实际曝光，使用namespace PatientID与UID，而非数值后缀匹配。扫描只读代码、metadata及归档报告，排工具、.git、缓存和locked IXI test目录，不读取MR或锁定test数据。所有不明用途的命中标为需要复核，不自动宣布“未见”；已有明确模型效果的整患者归开发，所有时点必须同角色。API共享58个VS-SEG患者继续整体排除。

角色冻结必须在新患者模型效果之前完成，资格阴性保留在源队列，资格通过后才能确定patient-level角色。新的3人及后续12人来源检查不算模型确认；任务模型能力、完整训练预算矩阵和独立确认仍需要实测。新claim不靠换患者/掩盖旧失败。
