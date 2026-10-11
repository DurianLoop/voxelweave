# 当前证据、候选假设与后续执行准备

原同预算增强医学结果全部完成：native intensity/spatial patient-first fullDice .468329/.521877；raw intensity/spatial .518307/.463237。四臂均未过六医学门槛，原完整分解、全部患者分母与失败结果在[医学结果记录](../imputation_mask_and_conditional_uncertainty_2026_10_09/MEDICAL_RESULTS_AND_NEXT_ACTION.md)。native平均提升只有1/4患者为正，不能当稳定收益；低recall并非只由tail FP解释。

本批实际80c2d6 exit0完成全部11968冻结训练记录的轨迹描述、2992步配对核验。全11开发患者各272更新曝光，全部19series存在；不是漏采整个患者/序列。没有新增模型/MRI/GT数组加载、前向或训练。首544/末544训练mean：

| 分支 | 首544 | 末544 | 全2992 |
| --- | ---: | ---: | ---: |
| native/intensity | .134606 | .142504 | .139674 |
| native/spatial | .188604 | .169896 | .174569 |
| raw/intensity | .150976 | .147216 | .144554 |
| raw/spatial | .205888 | .179692 | .180136 |

spatial-minus-intensity全步骤平均约+.034895/native、+.035582/raw。空间增强改变输入与监督分布，训练loss更大或末段下降不能直接当优化失败原因/完整FOV能力/augmentation收益；patient-first窗口、全部11块与全曝光记录均保存，不择有利窗口。这是描述分析，不是新的患者实验。

## 优先顺序与待证伪内容

| 顺序 | 具体问题 | 已完成/准备 | 执行条件和失败后的决定 |
| --- | --- | --- | --- |
| 0 | 当前task模型是否连开发完整FOV都弱？ | 12652正在跑固定四模型全76production+76functional FOV；新完整比較脚本准备完 | 必须真实terminal/capture后全四臂比较。开发也弱先补普通能力；开发高验证弱先查泛化/常规增强。组间采集/患者不同，均值不能判因果 |
| 1 | 常规resolution/support/reliability-map等强控制能否消掉SR动作余量？ | v2统一强度35904数值资格90446正在跑；既有六臂普通增强入口准备 | 全资格、费用和存储通过后才训练。六final payload约33.73MB，而磁盘储备外约17MB，仍不足；不删历史或动现有训练腾资源 |
| 2 | 加采集信息是否超过任务/QC/error与动作条件UQ已有信息？ | [新增论文与作者审计](PRIMARY_AND_AUTHOR_FINDINGS.md)明确部署特征合法性；此前NEXT_TRIAL控制继续有效 | 同capacity、同fold、同预算；gain移除采集特征、metadata-only、matched action-conditioned risk差、static/random/always-action/defer全部需要。收益来自真实baseline-minus-action病灶损害，不用GT-derived HM当部署输入 |
| 3 | 收益能否同时减少漏检/过分割且净费用成立？ | 准备沿原full/missing/anchors/tail、recall/precision/signedRVE/absRVE和全部患者分母评分 | 不用仅zero hallucination、SSIM或平均Dice代替；若ordinary task不达能力或收益不稳定，不开确认集 |

动作gain/QC/UQ/定位/校准所有拟合按患者折内；见全11GT的19998parent不能作严格LOPO外折初始化。需要无病灶GT/native missing pixels的合法输入，支持mask生成计费。完整费用含训练、采集元数据处理、支持、每个动作、失败/defer/fallback；未测人类工作流时间不称临床省时。

8未见确认患者/12series与lockedIXI继续关闭。GPU已授权，最近1394MiB低于预设8192MiB准入，尚未启动新GPU训练；CPU任务不迁移/重启，不查控其他PID、不安装、不委派。归档前全强度实际6124e4达10128/35904仍live，工具内层输出无原生截断，不继承旧6216前缀；isolated0/fullchain最大1.9073486328125e-6，坐标1.1368683772161603e-13。开发实际38a913：native/intensity19/19、native/spatial15/19，总34/76均严格通过，尚未整体终态，不解读partial开发指标。实际磁盘储备外约16.75MB，RAM约100.9GB，仍不假设六final/11fold训练可容纳。

还没有独立确认的可发表claim。阅读/软件资格/训练loss描述均不是医学确认，goal active。
