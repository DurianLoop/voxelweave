# 用户提供接续摘要的完整技术信息归档

来源为本轮用户提供的另一模型摘要。以下保留其目标、授权、约束、完成证据、数值、文献范围、工具记录及待办；属于摘要归档，不声称压缩前逐字聊天。tool exit 的来源在新账本中明确区分导入观测和本次直接观测。

## 目标与约束

持续研究、探索、验证到可发表 claim；goal active，尚未达成。用户允许GPU，但不能操作、重启、迁移用户终端训练，不枚举/修改其他PID。新文件只写D:\MRI\innovation；不改根.gitignore/environment.yml；冻结/已执行源码不可覆盖，修正用新version/attempt，不委派代理。PowerShell；Python D:\conda\envs\MRI\python.exe -X utf8 -B；命令末尾exit $LASTEXITCODE，真实工具退出单列。

11开发患者/19series；4已见验证患者/9series；8确认患者/12series、lockedIXI关闭，旧MIRA/MSValid84确认证据保留。fresh calibration只限制正式风险保证，不是经验MRI效益论文额外门槛。本地日期已经2026-10-08。

## 原训练

先poll live session99542，不重启。导入的最后实际poll d20351返回同一live session，非terminal：native13365，invocation02新增13266，cumulative30014.629973300034s。GPU b01824 exit0：2026/10/07 23:59:32.693，free1394MiB/total24455MiB/util94%，未达新GPU8GB余量。

原两臂各19998/总39996、CPU4/interop1、float32、共同初始化/监督/增强、AdamW lr/wd=.0001、30h/8GB储备/250MB不变。PCHIP99仅历史。只有真实训练exit0且两臂最终冻结后，才退出receipt→原56FOV→全部6能力gates→独立strict。不读中间MRI效益，不用float解释覆盖旧direct absolute gate失败。

## 上一轮已完成已归档

入口为 SESSION_RESULT_ANCHOR_PRIOR_2026-10-07.md、MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_RESULT_2026-10-07.md、SESSION_CHECKPOINT_RECEIPT_ANCHOR_PRIOR_2026-10-07.json、literature/anchor_prior_stage_manifest_2026-10-07.json。

归档cf7387 exit0：1383新阶段文件（包含隔离依赖，不是实验数），累计3102冻结证据；stage87966671 bytes；前1708 SHA不变，最终全部hash已核。原pip失败tmp保留、明确排除内容hash。finalize889706 exit0。下一轮纳其post appendices：SESSION_FINAL_TOOL_OBSERVATIONS_ANCHOR_PRIOR、SESSION_POST_ARCHIVE_ANCHOR_PRIOR_UPDATE、SESSION_CHECKPOINT_RECEIPT_ANCHOR_PRIOR、SESSION_OBSERVED_EXITS_FINALIZE_ANCHOR_PRIOR、SESSION_DELIVERY_ANCHOR_PRIOR、experiments/finalize_anchor_prior_checkpoint及上轮manifest/proof。

19series诊断：v4生产c31426 exit0/318.8289238s；独立779eda exit0/535.8328358s；核19系列、57支持、3015缺层记录、704trees、1062独立anchor分类。empiricalQDA coverage.8820%、boundary1.2061%、ROI.3035%、条件saving60.8898%、gates0/19。主balancedQDA coverage98.9361%、boundary98.2023%、ROI12.9525%、saving16.7439%、gates0/19；99%coverage+boundary且saving交集12/19。balancedExtraTrees coverage92.2123%、boundary93.8427%、ROI9.0258%、saving17.5864%、gates0/19；交集12/19。N572；k175/447/417。

旧生产失败v1(joblib管道)、v2(中文编码)、v3(源文件allowlist)保留，v4仅执行修复。上轮数组76observedMR包、38observed标签、38完整开发GT；0nativeMR/神经/GPU/train。2新论文Logit Adjustment/Class-Balanced Loss，21文字页/4视觉页，已完整归档。

## 当前轮此前成功、尚未归档的工作

新协议 MC_RC_MATCHED_ANCHOR_ORACLE_PROTOCOL_2026-10-08.md：旧理想observed-label传播只15系列；旧19系列GT支持用2体素、部署ROI用2mm，不可直接匹配。唯一主支持 ideal_observed_anchor_union_2mm_19，全部19/11、phase0/x4、两侧真实observed标签并集+2mm、原grid/PATCH/overlap/batch2。全部19理想anchor包保存后才完整GT评分。annotation oracle不是部署输入、有效修正或所有有效支持的上下界。原面积/tile门槛保留，但不等价当前3D实测总成本，不能仅凭gates0断言大ROI不能有效。

附加6/26连接标签接触诊断，不推断MRI可识别性或临床病灶。固定两费用场景、m=[1,2,5,10]及metadata-only重打包场景。自身CPU1/interop1、CUDA不可见、below-normal，每生产/核验900s、RAM/disk8GB、当前阶段保存20MB。不读验证/确认/完整nativeMRI，不碰原训练。

新源码：experiments/mc_rc_matched_anchor_oracle_2026_10_08.py、verify_mc_rc_matched_anchor_oracle_2026_10_08.py、mc_rc_matched_anchor_oracle_independent_helpers_2026_10_08.py、matched_anchor_oracle_independent_helper_origin_2026_10_08.json。结果目录experiments/mc_rc_matched_anchor_oracle_2026_10_08：attempt01.json、independent_labels_disk_fraction_attempt01.json、19压缩ideal anchor NPZ与source snapshots。

生产启动3330dd/session38335，terminal c4b139 exit0/59.4633277s；独立启动29c808/session37999，terminal339626 exit0/61.2150639s；helper创建3e40c5 exit0。

独立核19系列、19支持、1005缺层记录：inverse observed索引、fullGT signedtranspose/flip、显式boundary；disk binary_dilation替代生产EDT，Fraction Booleanphysical支持、独立tile/batch/summary。成分partition仍共享SciPy ndimage.label/find_objects，aggregation改bincount；不称独立连接库/科学确认。helper从上轮独立脚本文本提取、不import sklearn/torch/生产geometry，origin记录SHA。errors/prohibited=[]。生产19observedlabel+19fullGT，独立也各19；本轮共observed标签38、fullGT38，MR/模型/神经/GPU/train全0。

核心新结果：ideal19/19gates、18/19满足99%coverage+boundary且saving，N/k572/181；patient/series等权coverage99.9649234%、boundary99.9228737%、ROI.4716437%、saving57.6984751%。旧balancedQDA0/19、12/19、572/447、ROI12.9525%、saving16.7439%；forest0/19、12/19、572/417、ROI9.0258%、saving17.5864%。理想最低单seriescoverage.9955604883462819、boundary.9921875，旧15已有最差值，不能说全新。唯一无saving理想series患者001，UID1.3.6.1.4.1.14519.5.2.1.145323920879447126481769535625802103688，N=k8，ROI fraction.0018596649169921875；面积小不保证省算。

新标签接触：GT总前景988239；6连接24full components、21有missing、2无observed接触；26连接21、20、1。隐藏全部012/均1体素：6index3/26index2为r290,c314,z29，half-openbbox[[290,291],[314,315],[29,30]]；6index4为r291,c328,z33，bbox[[291,292],[328,329],[33,34]]。保留不删，不称临床病灶/检测失败；012理想2mmROI仍coverage1，附近anchor扩张覆盖，“不接触”不等于不能恢复。旧15phase0无隐藏结论保持，当前19范围不同。

## 费用场景

脚本experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08.py；结果同名目录attempt01.json；106be7 exit0，纯metadata，无新医学数组。

A：cachedN+m*k vsdensem*N；B：两个真实流程都必须先同baseline，cachedN+m*k vsdenseN+m*N。必须按真实流程预定，不能选有利分母；定位/生成/探索/transfer/后处理未计，非真实加速。B为前报告已注明但未填当前19预测数字的语义，不申报新理论。

完整患者sumN/sumk后ratio且患者等权m5：idealA.6179526149709429/B.5149605124757858；empiricalA.5777881860225474/B.4814901550187895（覆盖极差）；balancedA1.0284567734011212/B.8570473111676009；forestA1.0198876909684023/B.8499064091403352。保留patient/series、complete-patient、pooled三口径，不挑pooled有利值。

仅计数hypothetical repacking，原k→sumceil(Taffected/2)：ideal181→142、empirical175→144、balanced447→413（最多7.61%原conditional-call减少）、forest417→404（3.12%）。未执行、未输出等价/延迟资格、不替换原batch。广泛触窗时不能解决主要定位成本。

## 本轮已实际读/看、待写笔记的文献

协议literature/2026-10-08_shared_cost_primary_protocol.md；获取脚本fetch_shared_cost_primary_2026_10_08.py；缓存source_cache/shared_cost_primary_2026-10-08；ebb4f6 exit0，无获取失败。

1. Xu/Weinberger/Chapelle，The Greedy Miser: Learning under Test-time Budgets，ICML2012；作者arXivhttps://arxiv.org/pdf/1206.6451，8物理页，1–8全部文字实际读。
2. Xu/Kusner/Weinberger/Chen，Cost-Sensitive Tree of Classifiers，ICML2013；PMLR官方https://proceedings.mlr.press/v28/xu13.html→PDF，9物理页，1–8实际文字读，页9参考未逐页读。

17取得页、16文字实际读，不称全部supplement/作者复现。acquisition保持new_paper_read=false，另写真实provenance。0270bd渲染exit0/render保持visually_reviewed=false，之后实际view_image四图已核：greedy_page03_visual、greedy_page07_visual、cstc_page04_visual、cstc_page05_visual；4视觉页。PDF技能前轮已用，readonly无需authoring marker。

Greedy原文：PDF2式3，tree evaluation+所用feature首次提取，后续free/smallconstant；PDF3算法1/式5已用featurephi=0，union/set已有先例，L1重复罚不合理；PDF4式7–9cappedL1/分预算，树坐标只递增一次假设、局部近似，不MRI硬预算；PDF5–6Yahoo近似相对费用、irrelevant复制10次、验证bestiter，非MRIlatency；PDF7Scene15实测descriptor/kernel/SVM的CPU费用，15one-vs-all共享descriptor、首用后只再付SVM，共享费用已知；多randomsplit/validation不是MRI确认。

CSTC原文：PDF3式2首次支付/cache复用；PDF4–5每路径union只计一次，softpath权重expectedcost/mixednormrelaxation，非每患者hardbudget或硬路径证书；PDF5非凸初始化/validationpruning；PDF6留featuresupportfinetune；PDF7Yahoo不复制irrelevant，与Greedy不同不可跨paper受控对比；weaklearner单位，3h训练/10minfinetune不是测试整体latency；PDF8MSE改善而NDCG很小，端点不同，数据相关分支/成本路由有先例。

保留MRI候选为充分适配后，合法观测预测具体修正的完整患者净任务增益、真实窗口union和全探索/初始化费用、强同预算控制及冻结8确认。缓存、共享成本、cost-awarerouting、priorbalancing不单独创新。

## 已公开进度与后续待办

导入摘要记录四条公开进度：接续训练/抽层信号与ROI；旧15不计新、匹配19不作任务效益；oracle19/19与ROI/saving、A/B费用不同且非全成本；Greedy/CSTC先例及净任务收益候选、原训练13365。可见请求/goal/GPU许可/日期更新与本次压缩提示应归档；压缩前仅摘要，不伪造逐字。

接续先poll99542，再写文献provenance/笔记、oracle/两成本报告、创新准备、结果入口/对话/工具ledger。重点：oracle非MRI收益/必要支持下界；012singleton不推翻旧15、不称病灶；面积gates非实际总预算；A/B不是挑分母；packing未执行。

本阶段成功，没有新科学失败。此前查询工具问题904596 exit1（PowerShell literal wildcard error123）和dc2de3 exit1（rg排除未阻止旧piptmp权限），只读无修改；不是自动审批拒绝，无许可阻塞。

归档核前3102SHA，纳上轮postappendices及本轮所有源JSON/NPZ/论文PDF/txt/PNG/protocol/helpersorigin；排除live训练/pyc/旧失败tmp内容，阶段20MB合同。参考archive_anchor_prior_stage_2026_10_07.py，另建新版本，成功后才记真实退出，不编造未来exit。根.gitignore SHA7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524；environment.yml SHA dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257。

原训练terminal后才56FOV/6gates/strict；后续强适配dense/direct/SR、合法ROI/动作、配对净收益/全费用/强控制和冻结8确认。当前claim未验证，goalactive，不markcomplete/blocked。
