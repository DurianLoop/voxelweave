# MC-RC 第2版 CPU 来源审计：数量可复现，完整crosswalk失败

公开元数据已实际读完并保留响应：[获取记录](literature/source_cache/mc_rc_v2_identity_2026-10-02/attempt_01.json)。当前Version2 API与官方manifest的487个UID全集相同，无重复UID、未知ID模式或跨患者study。官方页面摘要卡仍写124，Version2表及API是160，旧版354序列/新版新增133序列不能混用。[原始审计](experiments/mc_rc_v2_nonpixel_identity/attempt_01.json)保留exit1/complete=false；[SQLite独立算术复核](experiments/mc_rc_v2_nonpixel_identity/independent_sqlite_verification.json)通过，不消除来源失败。

| 分组 | 患者 | studies | series | 描述为T2的series | 有T2描述的患者 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 第2版全集 | 160 | 427 | 487 | 363 | 157 |
| 全部共享VS-SEG患者，排除 | 58 | 165 | 187 | 125 | 57 |
| 官方ID规则下非重合候选 | 102 | 262 | 300 | 238 | 100 |

T2仅按SeriesDescription前缀计数，不是像素/采集认证。候选含不同厂家、重复时间点及可能MPR/derived系列；100人不是100个已合格患者。所有候选/排除ID见[患者表](experiments/mc_rc_v2_nonpixel_identity/patient_roster_attempt_01.csv)。

八行官方CSV的MC-RC UID和patient均可联上；八个旧VS-SEG UID在此前冻结的476条旧目录中全不存在。新旧UID直接交集=0，却有官方明确58人/8系列重合，因此“UID无交集”不是独立性证明。未证原因，不能按description猜映射，也不能以不同defacing/hash清除共享患者。详细失败与分项复核限定见[followup](MC_RC_V2_CROSSWALK_FAILURE_FOLLOWUP_2026-10-02.md)。

以当前官方声明和ID规则排除全58人，可准备其余102人候选的后续资格审计；完整source qualification仍pending。文献原库、challenge子集和新发布版本的数目分别保留。原生T2头、NIfTI标签路径/grid、薄层/非derived、任务模型训练患者身份、方法开发/确认分组均未完成。本阶段没有下载MR、标签数组、模型权重；科学独立性能确认患者=0。

[下一步预选](experiments/mc_rc_v2_nonpixel_identity/native_header_followup_selection.json)已固定VS-MC-RC-001/002/003的全部9条T2描述序列，尚未执行头/标签读取；未看性能结果选人。见[后续准备](MC_RC_NATIVE_T2_LABEL_FOLLOWUP_PREPARATION_2026-10-02.md)。
