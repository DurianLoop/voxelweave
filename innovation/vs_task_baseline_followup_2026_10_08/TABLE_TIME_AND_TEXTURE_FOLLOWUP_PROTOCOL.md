# 两个非医学CPU补核，执行前固定

1. 临床Table1按原单元格的mean-per-case与total-time两种口径分别算算术，不混为一套患者分母。根据主文36 fully accepted、8 one-session revision、6 complete revision保留全部50患者。探索不同假定MDT同时参与人数k下的person-time算术；未取得逐患者时间、真实每人出勤、自动pipeline耗时或完整两阶段联合统计，因此不估新显著性、净临床效益或本项目收益。正文/摘要T2与T1的Dice映射冲突保存，不静默统一。
2. 原roundtrip协议包含checker纹理；首轮8fb81e完整检查了impulse/细线/边缘/constant，但没有checker。本次独立新增checkerboard和宽结构输入，仍全64x128x128；固定single-axis rotation和三轴scale，标签不变，32固定点scalar oracle<=3e-6。参考前轮独立坐标函数，不改已执行首轮或原模块。记录高频变化、非identity与GT不变，不拿原文“underlying structure preserved”推断逐位图像不变。

均CPU1/interop1/below-normal，wall<=120秒，磁盘/RAM各8GB储备，整个stage<=5MB；不读MRI/GT/model数组，不CUDA或神经forward，不训练/验证/确认，不执行作者代码。原session29823不动。
