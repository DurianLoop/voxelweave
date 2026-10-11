# 共同初始化前99步的独立执行核验

在两臂第一短段结束前准备，只在实际训练exit0、result complete/errors=[]、同预算99/99后运行。CPU4/1、below-normal、无CUDA、墙钟<=1200s、新增核验输出<=20MB、全阶段<=250MB、RAM/磁盘各8GB余量。仅开发11患者19series，四验证像素/效果、八确认与locked IXI test关闭。

核所有固定来源SHA、共同随机初始state、独立患者/series流、两臂不可变segment99 checkpoint/history的SHA、99更新计数、AdamW状态全部99和有限值、同GT/增强、全19series覆盖/每患者9步。逐series重建输入和native监督的physical缓存，然后以独立随机流/采样实现重建全部198真实batch的input/GT/primitive SHA。

每臂最后一个训练batch用最后99模型检查三个head的module与functional概率/阈值，最大概率差<=3e-6、二值差异0；独立float64 NumPy BCE+Dice与生产loss差<=3e-6。不进行新的optimizer更新，不重训99步，不跑完整FOV、不计算MRI任务效果；梯度有限性仍来自主入口真实检查，不能称独立训练重放。预检中的连续/恢复12合成步严格相等只认证断点执行，不替代真实任务泛化。

核验和实际exit0登记后才继续相同正式预算。短段checkpoint/history的不可变副本保留，rolling resume/history在后续继续追加/替换；本核验绑定不可变副本，避免后续修改历史证据。全部失败保留，不更改正式LR、总步数或原四验证gate。
