# 真实资源入口 v2：CUDA 异常状态记录补充

原入口和已执行 source_snapshot 保留。v2 仅新增尾部 CUDA 状态观察：若本进程已 import torch，则在 finally（包括异常）用 is_initialized() 记录实际状态；无 torch 则记录 false，并标明观察有效。观察 API 不主动初始化 CUDA。若观察失败，标 invalid/null 及错误，禁止保留不可信初始 false。v2 保存自身源码 SHA 及本补充协议 SHA；依然逐一核原 synthetic certificate 的旧源码绑定。

旧入口初始 false 在 GPU 执行发生异常时可能失真，不能用于判断实际未初始化。旧 attempt01 是先验缺失且没有 import torch 的真实延期运行，该结果无此歧义。新 v2 当前只运行已授权的 --device gpu 延期入口；资格 gate 缺失前不初始化 GPU，不读取 MRI。该延期不证明真实 GPU 更新或 GPU 异常路径已实测；相关路径仍需资源满足且原正式训练/56FOV/strict/真实退出证据全部通过。
