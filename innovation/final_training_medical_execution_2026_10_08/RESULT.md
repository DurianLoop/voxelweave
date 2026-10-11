# 最终训练、医学评价、精度修复与文献决定

原正式训练 session99542 真实 exit0，共39996更新，两输入臂各19998；主医学评价 session76250 真实 exit0，但能力门槛失败。V3独立全56重放 session14716真实exit1：22/56概率误差不满足3e-6，二值预测及计数全部相符。单病例定位到最终 native 概率映射 float32 精度，旧代码/失败结果均保留。

V4 session70619 真正 exit0（chunk cc6710）。56/56完整生产与独立functional FOV、float64坐标、无损重读、独立计数和患者聚合全部完成并通过严格门槛；最大概率误差5.960464477539063e-8、旧二值预测变化0、旧医学指标全部相同、CUDAfalse，用时2193.88126秒。来源与实际退出绑定于 ACTUAL_PRECISION_V4_EXIT.json。这是同入口两实现核验，不冒充第三次跨进程独立重跑。

| 已见验证4患者/9series，患者先均值 | native | raw PCHIP |
| --- | ---: | ---: |
| full Dice | .506632 | .445159 |
| missing Dice | .507568 | .445335 |
| full recall | .462613 | .372408 |
| full absRVE | .474591 | .571475 |

native六门槛通过3/6，raw通过1/6；两臂都未证明足够医学能力，raw存在1series零TP且空预测。原开发full Dice为.890639/.859645。当前证据支持基础泛化失败，不能发表正面的SR病灶保持、任务净收益或选择策略claim。

标签来源审计：28个允许series的官方CSV/标签ZIP/DICOM首尾56header UID和去标识日期一致。多时间点真实体积不应相等，不把去标识日期当治疗记录。纵向方向事后诊断：已见验证3患者5区间，两臂均2个方向错误且涉及2患者，患者先均值错误比例.5；没有临床阈值、独立确认或SR因果结论。

新4篇原文文字核读的资料、精确范围、数值与局限见 ADAPTATION_PAPER_NOTES.md 和 READING_PROVENANCE.json，不统称全文复现。BigAug 旧NCBI正文429；本阶段一次EuropePMC替代端点仍500（真实exit1），两次失败均保留，未计入已读原文数量，未连续重试。MC-RC属于复读。

已经准备并合成核验同容量四分支标准增强续训：每种输入分别basic/strong，从各自原最后state开始、重置相同optimizer、共享99个patient-balanced draws与crop/flip/GT，只改强度变换。合成full-size独立公式与确定性均通过。新session80513已经真实启动；启动GPUfree1394MiB，未达8192MiB门槛，使用CPU4。此时尚未观察其真正退出，不将运行中的结果冻结或宣布完成。其完整FOV最终评价入口已准备但未启动；不以短pilot宣称充分适配或新意。详见相邻 adaptation_paired_pilot_2026_10_08 目录的协议和记录。

8名未见确认患者/12series、locked IXI保持关闭；未操作用户训练终端/其他PID，未安装依赖或改environment.yml/.gitignore。科研目标仍active，下一步先核验pilot实际退出，再评价四个固定最后state；若能力不足，依据实际费用准备更充分增强/同架构迁移控制。
