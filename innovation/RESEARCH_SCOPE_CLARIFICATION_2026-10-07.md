# 两条研究线的确认范围澄清

本接续阶段不修改任何先前冻结文件。用户授权继续批量读论文、寻找与既有MRI切片间超分辨率工作有关的创新、先做可验证探索、记录无法立即验证的方向，并允许GPU。长期goal仍是形成可发表claim，不操作用户终端训练。

- **旧MIRA机制线**：原fastMRI权重对在MSValid 84人/479目标有事前冻结的单配对外部确认；同患者IXI权重跟进不是新增独立患者。另有ReMIND 62/63人、UPENN处理后374人发布层结果。匿名来源不能简单相加为完全独立患者，也不证明原始采集身份或临床收益。
- **当前3D病灶效益线**：11开发患者/19series，4已见验证患者/9series；8保留确认患者/12series仍关闭。此前这条线的“科学确认患者0”不应扩展为整个项目没有外部科学确认。
- **已确认可发表claim**：仍未形成。旧MIRA有窄的上下文切换审计证据，但解析控制效应更大、物理身份与内容几何共变、外部响应预测/部署guard失败；当前3D任务充分适配尚在训练。软件资格、显著性、患者数量都不能单独关闭goal。

本阶段实际首次训练poll：session99542，chunk19ad31，仍live；native更新3960，invocation02新更新3861，累计正式墙钟7974.782554899924秒。PCHIP最近继承快照99，不宣称实时步数。GPU查询chunk0bb0c3：2026-10-07 18:03:31.211，free1394MiB/total24455MiB/util93%。未达既有8,000,000,000bytes启动门槛，不迁移正在运行的CPU/float32共同配方。

依据：MIRA_CLAIM_AUDIT_2026-09-30.md、PUBLIC_ONLY_CLAIM_REVIEW_STRESS_TEST_2026-10-01.md、CLAIM_PUBLICATION_GATE_2026-09-30.md、MC_RC_3D_19SERIES_COMMON_INIT_CPU_PROTOCOL_2026-10-07.md。本阶段publication gate只核读前60行，输出曾有截断，不冒称全文核读。
