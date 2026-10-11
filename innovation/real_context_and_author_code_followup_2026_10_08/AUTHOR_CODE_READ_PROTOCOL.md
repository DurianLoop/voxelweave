# FastSurfer v2.3.0固定公开来源核读（运行前）

GOUHFI原文使用FastSurferVINN v2.3.0生成标签。此次先只读GitHub API解析Deep-MI/FastSurfer tag v2.3.0到commit（若annotated tag再解析一次），记录tag/ref/object SHA，不把当前main源码当2022论文完全等价实现。

固定commit后只取FastSurferCNN/models/interpolation_layer.py、networks.py、sub_module.py及data_loader/augmentation.py四个已知路径。逐请求timeout30秒、HTTPS证书验证、≤400000bytes、最多3跳，合计wall180秒/目录2MB。保存原字节/HTTP头及sha256；不import、不运行、不下载权重/影像、不clone整repo、不安装依赖。取得后实际分段核读，尚未阅读时数量0。

目标仅核VINN feature-grid尺寸、align_corners/crop/pad、SF扰动/逆变换和采样语义，服务于普通基线对照与文献解释。若v2.3.0代码与作者稿正文不同，保留版本差，不擅自修正文中结果/公式；最终训练和论文版本复现需另行取得准确版本。CPU1/低优先级、8GB磁盘/RAM储备、stage5MB，原训练/其他PID不动。
