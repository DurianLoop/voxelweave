# 固定2992匹配增强：完整医学结果与下一动作

原完整医学评价实际6ede46整体exit0，76项不是本阶段：本阶段是36production+36functional完整FOV，CPU4，elapsed1352.960498200031s。原capture0fbd7c与summary a165da成功；四last2992、11968训练配对已由df9ebf确认。全部严格概率3e-6/坐标3e-12/0binary通过，但四臂均未过原六医学门槛。独立functional与production同进程，不能当新的未见患者确认。

| 输入/增强 | patient-first fullDice | missingDice | recall | absRVE | 原六gate通过 |
| --- | ---: | ---: | ---: | ---: | ---: |
| native/intensity | 0.468329 | 0.470420 | 0.559930 | 1.112327 | 2/6 |
| native/spatial | 0.521877 | 0.521347 | 0.453378 | 0.483695 | 3/6 |
| raw-PCHIP/intensity | 0.518307 | 0.519431 | 0.512911 | 0.512050 | 2/6 |
| raw-PCHIP/spatial | 0.463237 | 0.462797 | 0.446741 | 0.932067 | 2/6 |

同预算的spatial-minus-intensity不是SR/采集可见性收益。native fullDice平均+0.053548，但只有020正（+0.273676），其余3患者均负，去掉020后描述均值-0.019828；4患者recall全部下降。raw平均-0.055071，2正/2负，所有四个描述性leave-one-out均值仍负，3患者recall下降。全部leaveout都保留，没有挑最有利的版本，它们不是独立检验/新的cross-fit。

024是共同严重漏检：native intensity recall0.136/spatial0.112，raw intensity0.116/spatial0.119；后三条件precision约0.976–0.980。仅从现有counts可断定在这些已见序列上的预测主要漏掉GT，不能由此判定病灶位置、输入质量或训练原因。025的raw spatial absRVE2.0069，比intensity增加1.8362；对该患者的三个series需完整保留，不能只看整体Dice。

tail FP不是这些差异的共同解释：native intensity总tailFP1419/单series最多占全部FP8.865%；raw intensity18/最多2.711%；两个spatial分支tailFP都是0，却仍有上述能力失败。不会把这个诊断当尾部裁剪的依据，原完整FOV和tail评分合同保持。

全部36series的四region计数划分、144region/720指标、patient先均值和六gate又由Fraction完整核对，最大报告差0；实际1f38d5 exit0。新helper首次32d597因过滤null不符合原全分母合同失败，另建attempt02恢复“任何未定义则null”，原失败/源和完整患者分母保留。没有改原结果/阈值/门槛。

下一可执行动作已经启动：development_capacity_after_matched_2026_10_09/evaluate_development_capacity.py，actual ca6253 session12652。四个相同最终模型，全原11开发patient/19series，共76production+76functional完整FOV，CPU4/interop1/5400s/本目录3MB。只判断开发任务拟合与已见验证的描述性差异，不新训练、不选checkpoint、不加载validation图像/GT或确认集。

开发集模型也弱→先检查普通任务拟合/输入与监督/部署一致性，再补强普通基线；开发高但已见验证弱→检查泛化与常规增强，不能把低能力模型造成的动作余量当新意。两集合条件不同，均值差不直接证明原因。原19998parent已对19development评分，可读冻结结果作描述；新四模型必须全76做完，真正terminal后走新capture，不挑模型或series。

完整强度90446仍live，最新daa91b达到6336/35904并已越过旧6217失败位置，isolated0/fullchain最大1.9073486328125e-6/coordinate1.1368683772161603e-13。这不是35904全部成功，不继承旧前缀。只在真正terminal/audit后补统一v2 ordinary resolution/support controls和资源准入。

GPU授权保持但fresh1394MiB<8192；磁盘储备外约19MB且仍保留原医学3MB/full2MB/新开发2.8MB，六finalpayload33.73MB不可假设容纳。没有迁移/重启其他终端训练、依赖安装/代理委派或历史删除。8确认patient/12series与lockedIXI继续关闭，尚无独立确认发表claim，goal保持active。
