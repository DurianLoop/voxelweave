# 补齐的直接先例与新增控制证据

完整复读MoEDiff-SR全部10文字页、6视觉页，补齐旧未完整读的7–8正文/10参考，不计新独立论文。读取固定作者提交的README及5个Python文件，CPU精确复核15行表/1组权重、AST解析5文件，没有作者模型执行或MRI效果实验。

关键新证据：TableIII42.21G是最昂贵的单个专家，异步行没有质量指标或完整患者耗时；不能把相对ensemble打印值24.79%下降称完整加速。当前公开forward无条件算全部3experts，global软权重不证明跳算；五文件没有完整async reverse sampler，且有静态接口/配方差异。临床仅一个MS示例，缺完整病灶端点统计。源码使用普通softmax且有temperature floor，纸面Eq4归一化例不当实际源码故障。

因此后续须保留同训练曝光的固定/学习normalized dense mixture，并把所有候选生成、分支和患者费用计入，与实际硬跳算/强static、risk/error/cost/defer/random/calibration-only控制比较。论文区域专家/相对收益先例仍成立，源码差异不构成本项目创新。

[完整读记](PRIMARY_AND_SOURCE_READING.md) · [新增具体控制准备](FULL_FLOW_DENSE_ENSEMBLE_CONTROL_PREPARATION.md) · [实际阅读范围](READING_PROVENANCE.json) · [CPU证据](cpu_audit_attempt01/receipt.json) · [可见对话](VISIBLE_DIALOGUE.md) · [实际工具结果/失败](OBSERVED_TOOL_RESULTS.json)。

原训练最后实际4fe8d3仍live，raw11880/new31680/wall71302.59866399993s；GPU4cc9ab free1394MiB，根两文件SHA保持。没有训练/权重/医学数组/神经forward/head/action新作业，不打开8未见/lockedIXI。final/真实exit0后立即优先既有CPU losslessV3全56FOV/六gates/strict，再充分适配/动作余量/全费强控制/冻后确认。当前可发表且经验证MRI claim未达到，goal active。

V1缺模块实际exit1保留，V2既有便携工具实际exit0；无环境安装、没有作者源码import/执行、没有审批拒绝。归档从完整5430+旧delta30（5460）接续，并纳入watch4–8及TADT四份post，成功结果以本阶段实际APPEND_PROOF.json为准，不冻结原训练rolling文件、不复制大manifest。
