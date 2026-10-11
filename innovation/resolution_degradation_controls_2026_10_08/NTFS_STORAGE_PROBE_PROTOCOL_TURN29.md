# 只对本轮新建文件探测透明压缩

只读存储预测b60a44已实际核验三个完成臂文件大小：每last2992约5,622,337bytes。现可用空间扣8GB储备仅17,334,272bytes；尚需原第四臂同尺寸last。后续六臂同架构仅6个last就33,734,022bytes，严格LOPO两输入22个task状态仅权重123,691,414bytes，还没有原子临时文件/日志/元数据。这里都是未执行新训练的forecast，不是放宽储备或缩小医学目标的理由。

fsutil volumeinfo只读调用实际d0189b Access denied，非自动审批拒绝。采用无管理员需求的低风险替代：仅创建本目录新8192byte文本probe，记录字节SHA、文件属性与GetCompressedFileSizeW分配字节；标准Windows compact.exe /C /I /Q指定唯一绝对probe路径，timeout30s，再核逻辑字节长度及SHA不变、FILE_ATTRIBUTE_COMPRESSED位与物理分配。没有删除、移动、编辑旧冻结内容或处理任何训练/数据文件，没有其他PID查询/控制，没有安装/网络。

本探测墙钟60秒/本进程低优先级，保存逻辑字节预算12KB，本stage5MB并继续预留full journal1.5MB、审计150KB、后附100KB，RAM/disk8GB守卫不变。仅判定workspace能否对文件透明压缩；失败原样保存，不强行提升管理员权限。此步不授权改任何旧源字节/路径、不得对MRI/model/live目录进行压缩；若成功且确有物理节省，另事前协议限定已完成的离线文本证据、逐文件冻结SHA核验与保留所有逻辑内容，才释放后续实验所需容量。
