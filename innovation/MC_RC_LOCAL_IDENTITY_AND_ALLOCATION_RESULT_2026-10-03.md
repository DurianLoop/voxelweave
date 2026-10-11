# 本地身份审计及事前患者分配候选

本批审计了503,812个文件名、23,432份文本（784,587,920字节）；随后以64KB分块补查14个超大CSV（1,453,853,303字节），其中没有任何API namespace PatientID或exact UID命中。官方API为160患者（102 MC-RC + 58共享VS-SEG），有标签候选仍为71人/159系列，两个分母不要混用。

共731命中文件，新固定15患者对应114个文件。3个需逐项复核的文件已明确为来源预检报告、nonpixel身份名单及元数据JSON；在已覆盖本地文本/文件名里没有找到新15人的任务/SR模型效果曝光。所有命中、上下文、SHA、人工用途分类保存于 [审计](experiments/mc_rc_local_identity_audit/attempt_02.json)、[补查](experiments/mc_rc_local_identity_audit/gap_stream_attempt_01.json)、[人工复核与分配](experiments/mc_rc_predeclared_patient_allocation/attempt_01.json)。

这是范围明确的本地记录结论，不是全项目绝无曝光证明。二进制内容仅按文件名检查；其他数据集未知别名、外部模型训练名单未验证；临时skill installer目录权限失败保留为范围排除，没有扩大权限。三个非文本来源响应保留签名及获取用途。首次rg失败、完整可用清单、stderr和当时脚本均保留，attempt02复用清单，不重新枚举或读锁定test。

按模型效果之前登记的规则生成如下分配候选；所有患者时点同角色，不按标签大小、厂商或方法效果换人：

| 角色 | 完整PatientID（均VS-MC-RC-前缀） | 患者数 | 候选系列 | 源资格通过系列 |
| --- | --- | ---: | ---: | ---: |
| 开发/训练候选 | 001,002,004,005,006,007,009,010,011,012,013 | 11 | 26 | 18 |
| 验证候选 | 020,022,025,024 | 4 | 9 | 9 |
| 最终确认保留候选 | 030,029,019,028,031,026,027,015 | 8 | 16 | 12 |
| 暂不分配、未源预检 | 其余48患者 | 48 | 108 | 0 |

固定后续12患者用SHA256('MRI-MCRC-adaptation-v1|' + exact PatientID)排序，前4验证、后8确认保留。旧8人始终开发；011/012/013追加开发。全部159系列以及阴性源资格保留在 [角色CSV](experiments/mc_rc_predeclared_patient_allocation/all159_predeclared_patient_roles.csv)。58共享VS-SEG患者整人排除，没有用后缀去猜同人。

分配状态为 `allocation_predeclared_provisional_training_inactive_not_clean_split_proof`：名单已经事前写定，科学split尚未启用。需要从头训练或完整训练身份已知的模型；作者MC-RC/混合权重可能见过这些人，不能直接当未见确认评价器。任务能力、完整输入流水线、优化器/augmentation/阈值/checkpoint和GPU条件也尚未满足。最终8人只支持小样本探索，不能预先宣称足够发表；科学确认人数仍0。

本批新来源与旧15合格开发系列合计39源合格系列/23分配候选患者；这不等于39独立样本。同人多时点的权重需先按患者，再在患者内部按预登记规则分配，bootstrap也在患者层面进行。任何分割/修正训练不得读最终确认患者的完整标签来选参数。
