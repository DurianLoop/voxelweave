# 任务因素矩阵：输入控制已实现，效果尚待最终模型

[本轮19系列结果](COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md)显示新的共同投影direct与旧direct**19/19完整体积输入逐位相同**，availability同旧资格也逐位相同。因而不用把它算作新的独立方法或重复正式训练臂；此次新增有解释意义的输入是共同投影dense-PCHIP。

## 已实现可调用接口

新[输入模块](experiments/mc_rc_common_projected_observed_2026_10_08.py)可直接以已认证 `ObservedMRI` 和原 `lattice(case)` 为输入：`shared_source(obs, grid)`生成只读锚点；`projected_pair_fields(source, grid)`返回dense、numerator、availability、valid_grid及native hashes。`final_affines`给physical/padded geometry。无GT/native图像参数，统计从实际全部observed取得，分支后不重估；不会读其他患者。沿用旧 `augment_pair`、canonical two-channel initialization和原几何label管线时，后者的训练标签仍只用于开发监督，不能混进新输入模块。

本轮生产和独立脚本已执行，各自输出目录已占用；不可原地重跑/覆盖。正式训练采用另存协议、脚本和输出目录，启动前绑定本轮prereg/source/result SHA。原独立v1失败保留，新v2分开资格；原理想双精度门槛仍有9系列/30样点失败，不能说旧门槛全通过。

| 后续臂 | raw观测 | 输入先后顺序 | 用途／当前状态 |
|---|---|---|---|
| 原native reference一通道 | 完整native（较多信息） | 原归一化→physical | 原最终强基线的诊断参照，当前同一99542正在训练；不作为部署observed方法 |
| 原dense-PCHIP一通道 | 固定每4层observed | native raw local-PCHIP→observed统计归一化→physical | 原训练的另一臂尚待轮到及完成；与两通道比较需说明容量/augmentation差异 |
| legacy dense-PCHIP两通道 | 同observed | 原native PCHIP流程 + 同availability | 旧两通道输入已资格；正式任务适配未启动，作为direct的同容量控制 |
| direct两通道 | 同observed | sparse normalized numerator→physical + availability | 旧资格与新共同投影实现19/19逐位相同，正式训练去重；充分适配不可用旧absolute失败或synthetic checks代替 |
| common projected dense-PCHIP两通道 | 同observed | normalized anchors面内投影→local PCHIP→z map + 同availability | 本轮新增已核实现，单独用于投影顺序／共同source因素对照；尚无任务训练 |
| confidence-aware normalized convolution | 同observed | 已知confidence/applicability机制 | 若普通direct充分适配仍弱，可按已读Eldesokey等准备额外强已知基线；未实现、不称创新 |

“19/19相同”是本开发包、grid、float32 CPU实现的完整输入事实，不外推新形状、后端、其他spacing或hidden data。相同输入和mask能支持去重数据臂，但实际训练状态、batch、初始化、GT几何、augmentation与optimizer都必须一致并独立记录，不能伪造第二条训练结果。

## 开始任务比较前的依赖

继续 poll live99542；不重启/迁移，不控制用户终端训练或其他PID。原两臂各19998、共同初始化/样本/监督/增强、CPU4/interop1、float32、AdamW lr/wd=.0001、30h、8GB RAM/disk储备和250MB合同不变。真正最后exit=0且两个最终模型冻结后：真实退出receipt→原56完整FOV→全部6能力gates→独立strict。不能用中间loss/旧PCHIP99/本轮输入资格跳过。

若强任务基线和完整预算有资格，再冻结上表 observed 同容量三臂的精确训练/推理合同；均用旧 canonical two-channel共同初始化，相同完整监督/抽样/预算，保留所有零收益和损害患者。ROI先从合法observed定位；native坐标修正与原观测一致性单列核验。全19开发中完成源、患者和系列合并，不将多系列当独立患者；目前未训练收益预测器，也没有实际FOV成本证据。

本轮GPU获准使用，但最近可用1394MiB，8GB新增作业预留未满足。GPU条件后来满足时，可依原既定预算启动已准备且依赖完成的新作业；不将现有CPU训练迁到GPU、不改变数值配方。授权无需重复询问。

## 等强基线结果后继续的可证伪问题

1. direct与legacy dense任务差异，是否会在共同投影dense控制下改变？需要实际患者配对端点和完整成本，输入SHA不能回答。
2. 强适配后是否还有固定合法动作能产生稳定的病灶任务净增益？若没有，保留负结果，不训练收益头来“找出”剩余空间。
3. 若有可修正余量，只用observed的收益选择能否在同成本下超过同特征/容量误差头、风险头、固定最佳合法动作、cost/defer、预算随机及union-aware greedy？交互从当前状态测差分，不能把单动作收益相加。
4. 选定方法、网络、指标、阈值、checkpoint及预算后再冻结8确认/12series与第二任务网；4已见验证/9series不更名新确认，lockedIXI保持关闭，旧MIRA/MSValid84证据保留。fresh calibration只限制正式风险保证，不增加经验任务论文门槛。

本轮[两篇理论核读](literature/2026-10-08_distortion_perception_primary_reading.md)不把Shannon rate当GPU成本、不把rank当MRI熵、不把perception/heldout误差当病灶收益；goal仍active，当前实质progress，尚无可发表MRI收益claim。
