# MIRTO 原文核读与项目意义

本stage精读1篇：Negin Kafee Hernashki、Soumick Chatterjee，MIRTO: a registration-gated, multiverse-tested evaluation protocol for unsupervised anomaly segmentation in brain MRI，arXiv 2610.02136v1，2026-10-01。实际PDF43物理页，SHA256 275e37b395014a2a64fb45fc1f40402d6d636d52b8e4d5c3c2a5a6401c6038c1。全部43页文字已读（其中23、24为纯参考文献），13个不同物理页实际视觉核读，另对15页表4放大复核一次。提取43页、渲染13页不自动算阅读；具体批次由READING_PROVENANCE记录。不是系统综述或已复现作者实验。

## 实验身份和独立性

页1–3、9–10、21明确：312 BraTS2020测试患者也用于协议开发，所有推断是探索性；24患者为互斥validation，但其阈值估计仍有不确定性。四种UAD模型REFLECT、UCCD、cDDPM、AnomalyDINO的stored maps供评价，不再GPU推理。IXI-HH+Guys是共同数据来源，不是相同训练曝光或充分适配预算：504 vs324/81 vs361/92 volumes，DINO memory50；每训练集只有一个训练实例，种子变异未知。cDDPM不同训练集2854和79040steps（页40）。不能据此为本项目公平充分适配作背书。

## 配准和病灶分母

页4–6、10–11：canonical完整肿瘤reference不重采样；方法自身FOV外score0仍进入正式完整分母。56个候选变换是MIRTO的配准诊断，不能与本项目56个完整FOV评价case混作同一个操作。AUROC和slice score可对axis误差反应不同。页5“label-free”诊断使用maps和已有reference labels，含per-subject voxel AUROC；准确含义是无需额外标签，不是部署不需GT。

页5 Eq9、页25证明为Jaccard距离的反三角不等式，对任意同一集合域的P、R_A、R_B总成立。其从未被违反不能认证几何正确；若数值违反，应先查集合域、计算实现、数据关联或定义。CPU四元素全部4096三元组零违反，956紧等号，只验证此数学事实，不验证作者或本项目配准。

页10、17、35–36、Table41：6连通时472个above-floor病灶与5473个全部component；REFLECT命中287不变，287/472≈0.608而287/5473≈0.052，约11.60倍完全来自分母。原文部分表明确后者不是其正式病灶sensitivity。项目不能照搬50mm³过滤真实单体素标签；沿原冻结病灶定义和完整患者分母报告。

## 阈值转移是强控制，不能改造成部署策略

页5 Eq10在validation上最大化Dice，约束平均FP和sensitivity guard；test-matched Eq11明确仅GT-informed诊断，永不作为实际可用结果。页13/15 Table4：b20时FP mean为16.3、18.9、12.9、17.5cm³，p95为37.2、64.0、57.1、60.1。共同nominal b不是共同实际FP，也不是单患者保证。

页13、32 Table29/30：UCCD−cDDPM validation Dice=0.539−0.519=+0.020；test-matched=0.541−0.542=−0.001，后者区间含0。差分变化0.021由−(0.002−0.023)解释；Identity1对患者均值是精确代数，对median/pooled不一般精确。打印表独立舍入，CPU采用三位0.0015容差；不要求每个打印差严格0。

**阅读纠错**：本接续曾在缩小的15页图将cDDPM b20的CI下界0.503误当均值，并公开说与附录矛盾。实际提取文字和从原PDF scale3放大都确认0.519[0.503,0.535]。这是本助手视觉误读，已公开撤回；不是作者差异，不能用于查新论证。

## 后处理Dice增益与漏检可以背离

页15–16 Table7、页35 Table37/38：UCCD b20 total0.0846=fixedτ0.0064+relaxation0.0782，放宽占92.434988%。Table37的少数打印残差0.0001处在四位独立舍入范围，不构成Identity5失效。fixedτ项CI跨0；above-floor sensitivity0.674→0.629。REFLECT0.608→0.549，cDDPM0.665→0.619，DINO0.210→0.121。ROI内Dice/减少小component可能掩盖真实病灶伤害。该事实要求项目保留原漏检/FP/FN/volume等全部gates，不能只做局部Dice。

## 小样本风险控制边界

页3、6、25：CRC指示损失的修正式需α≥1/(n+1)才有可行τ。n24、α.1得到Beta(2,23)，mean.08、P(risk≤.1)=.707523、97.5%分位.211202。marginal跨校准集平均保证不等于95%校准集条件保证；RCPS/LTT是另一个更严格的问题。

CPU条件算术：4和8患者在此规则下不能以α.1找到可行阈值；11患者可行，但Beta(1,11)只约68.62%校准集满足risk≤.1。已见开发/验证不会因此成为合格独立校准集。即便未来8个独立患者观察到0伤害，一侧95%二项上界仍为31.2344%；此处没有读取确认数据、没有观察到0伤害。需要至少29个独立零伤害案例才使该上界≤10%，59个才≤5%，且病例定义、独立同分布/适用人群前提仍要满足。故11/4/8框架能做限定效果探索与确认，不能自动写低population risk保证。

## 推断、探索与公开文字边界

页9、25：以patient为bootstrap单位B10000，test threshold在replicate重选，validation阈值固定；validation结果CI不含24人拟合τ的不确定性，页21作者也承认。declared families内Holm不覆盖同队列所有探索选择。bootstrap raw floor2/10001，K16/24/32 adjusted floor分别约.0032/.0048/.0064；页9统一“at floor print p_H<.005”的文字不能适用于K32。这个打印规则问题真实存在，但源码未取得，不能断言实际p值算法有错。不要复用该统一打印规则。

页18–19、38–39、42–43：REFLECT aggregation family在两个checkpoint、同一测试队列上探索；MAD+.052/+.038不表示其在两模型里均为独立胜者，作者最终只保留family支持。原计划六规则未能全部计算，替代family被明确标探索性。Table52的threshold grid.01不同主分析.005，.492/.497的差异不自动是矛盾。论文的latent残差聚合既不是新的病灶action-value政策，也不是通过GPU资格的项目效果。

## 费用不能擅自补分母

页39–40 Table55的REFLECT inference11238s、32.5s/volume和IterMask3D9784s、28.3s/volume，一位小数舍入下均只兼容整数346，不兼容312+24=336；DINO923s、2.7s/volume则兼容336–348。作者实际计时case集合/分母未打印清楚，不补造为346例全方法，不直接判方法速度结论无效。REFLECT训练账本并非本checkpoint，UCCD/cDDPM训练缺可核账目而省略，Dinomaly2部分估算，不能拼成公平训练效率比较。

## 作者实现状态与范围

页21给https://github.com/soumickmj/MIRTO。API repo metadata HTTP200、tree HTTP403 rate limit；后续正常网页和公开raw README均HTTP200。网页实际列出.gitignore、LICENSE、README.md；已完整读160bytes README，内容为“The repo is coming soon! Let's have some MIRTO while waiting!”及MITRA展开。此访问时点网页展示占位仓库；未验证完整递归tree、其他branch/未来发布，未读实现源码，未执行作者31个synthetic tests。保留失败和fallback receipts，不称作者永久未开源。原文的“available”与此刻默认branch可见内容存在发布状态落差。

项目执行准备见 [PATIENT_TASK_CONTROLS.md](PATIENT_TASK_CONTROLS.md)，实际CPU结果见 [receipt](cpu_audit_attempt01/receipt.json)。当前没有新增MRI效果证据，可发表claim仍待医学验证。
