# 下载前的实际来源选择

本阶段索引76e094=0：两个joint题名分页8+3条，recurrent/attention查询5条。首次combined输出截断，不据此称筛全；另存show_index_pages.py，b8cf01=0完整打印11个分页题名摘要后实际核读，attention5条在原输出完整核读。ccf0cc=1是PowerShell对inline Python引号传递问题、未读取医学/模型或改文件；改为本地脚本执行，失败不抹除。分页与旧8合计是否19unique由后续实际ID核对，仍非系统综述。SERANet未取得原文，不声称查新完整。

选择actual-indexed来源：
1. Jesse Phitidis等，Hetero-modal learning and corruption-resistant hetero-modal inference for joint segmentation of white matter hyperintensities and ischaemic stroke lesions in MRI，2610.00553v1。索引摘要描述206 vascular patients、训练不重叠模态以及MMAR对未标记catastrophic corruption的动态加权；必须核正文中真正标注/患者split/augmentation/对照，摘要不算实证已核。
2. Shenghao Zhu等，XLSTM-HVED: Cross-Modal Brain Tumor Segmentation and MRI Reconstruction Method Using Vision XLSTM and Heteromodal Variational Encoder-Decoder，2412.07804v3。摘要涉及缺失模态重建与task feature交互，直接限制泛称“先补缺失MRI再优化病灶”的新颖性。须核输入是多模态而非through-plane、恢复目标、强充分适配/容量/费用对照。

实际查询未找到目标SERANet，当前选择根据真实返回的MRI病灶/输入损坏与缺失修正近邻推进；不伪造题名/ID、不声称它们是同固定CISS观测下直接baseline。其他14返回记录仅题名摘要筛查；AnatoMask等未取正文，不借摘要证明方法/患者结果。未取作者代码或训练材料，若后续正文新增强对照，另准备不改当前训练合同。

