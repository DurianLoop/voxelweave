# 患者暴露范围与任务驱动采集补读：阶段协议

本阶段接续 `TASK_ADAPTED_ACTION_UTILITY_NEXT_PREPARATION_2026-10-08.md`。所有新文件仅在本目录，exclusive-create；已绑定源码与结果不修改。原 session 99542 继续，不控制用户终端进程，不启动新的 GPU 或 MRI 数组作业。GPU 授权保持，新增 GPU 作业仍须已有 8GB 储备条件。根环境与 .gitignore 不改。

实质工作一：只读取冻结 feature table / 正式训练 frozen_config 的 JSON 与 Python 源文本，建立 11 患者 / 19 series 的 LOPO 分组和训练暴露审计。禁止 import 项目神经模块、MRI/GT/权重数组；只审计已知任务网暴露，不能仅凭未交叉 ID 就证明所有恢复器/调参/预处理均未见患者。现有两臂共同配置见过所有开发患者时，每个 head-heldout fold 应明确 task_model_patient_excluded=false、pipeline_patient_out=false。真实 action utility / full cost 未生成，保留 null，不用观测插值误差或 loss 代填。

实质工作二：定向公开索引查询 task-aware acquisition / active MRI acquisition 先例，最多三条查询，每条最多 8 条。标题/作者/版本从实际索引获取，不猜 arXiv ID；取得公开原文后分别登记实际文字页与视觉页，不把下载/提取计为阅读，也不把 k-space 采样当已有 CISS 层的合法修正。

预算：无医学数组作业；索引每响应 <=3MB，原文每份 <=10MB，最多两份 PDF；请求 30s / 最多 3 重定向 / TLS 验证保持 / 无自动重试。阶段新增总存储 <=30MB；CPU 单线程、below-normal优先级，单个元数据作业 <=120s。磁盘/内存只读检查，不删除旧证据。阅读沿用 portable pypdf/pypdfium2，不安装或修改 MRI 环境。

完成标准：真实患者 registry 与共同配置 exact 一致；所有 fold 的患者和全部 series 一致排除；任务训练暴露正确标注；真实标签缺口显式拒绝为可训练数据；方法/对照/下一次动作准备与实际阅读范围归档。不产生新的病灶效应、风险证书或发表 claim。
