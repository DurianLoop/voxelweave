# 冻结资格checkpoint的透明NTFS压缩

目的仅为完整训练family与资格的8GB磁盘reserve准入。只取已冻结7291链内、innovation内、非tools、未压缩且非readonly/sparse/reparse/encrypted的.pt文件。排除当前19series GPU资格的两个19998 parent；不取原终端训练目录、不取MRI/GT/概率数组、不取任何live或未冻结文件。

这是区别于之前text-only stage的独立、可逆存储操作；旧协议和旧文件逻辑内容不改。本stage先只读inventory固定最多40个目标、原SHA/bytes/属性/GetCompressedFileSizeW；随后compact.exe /C /I /Q逐文件，仅改变NTFS存储属性。每次前后验证原SHA与逻辑bytes，全结果及实际compact输出保存。没有checkpoint反序列化、模型修改、重训、删除、移动、路径更名或格式改写。压缩节省以API物理差值计，当前disk snapshot另记，不混成科学增益。

目标仍是完整family；不得降低旧allowance、患者/step/分支/gate/reserve。新stage2MB，其他既有allowance加已备fullFOV20MB共40.8MB保留；RAM/disk各8GB、CPU1/below-normal、每mode wall300秒。独立own compact子进程隐藏窗口/低优先级继承，不枚举或控制其他PID。失败和所有历史保留，旧7291逻辑SHA/bytes在下一archive继续整体核验。此操作不证明训练或临床claim就绪。
