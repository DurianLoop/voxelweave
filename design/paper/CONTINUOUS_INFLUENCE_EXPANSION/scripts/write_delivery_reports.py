from adapters import *
import pandas as pd,json
def main():
    d=pd.read_csv(P/'CONTINUOUS_INFLUENCE_BIG_TABLE.csv');s=read(P/'outputs/final_science_verification.json');prot=read(P/'outputs/source_protection.json');build=read(P/'build_logs/build_audit.json')
    assert s['status']==prot['status']=='PASS' and all(r['success'] and not r['issues'] for r in build)
    q=d[d.technical_status=='ELIGIBLE'];passes=int((q.stability=='PASS').sum());supports=int((q.claim_status=='SUPPORTED').sum())
    negatives=q[q.fixed_count_high<0];nulls=q[(q.fixed_count_low<=0)&(q.fixed_count_high>=0)];fails=q[q.stability=='FAIL']
    previous=pd.read_csv(C/'UPDATED_MIRA_REPORT_CARD.csv');retained=previous[~previous.design.str.startswith('acquired-only')].copy()
    fresh=d.copy();fresh['design']='acquired-only '+fresh.model;fresh['cohort']=fresh.dataset;fresh['local_observability_gain']='NA';fresh['ranking_gain']='NA'
    pd.concat([retained,fresh],ignore_index=True).to_csv(P/'UPDATED_MIRA_REPORT_CARD.csv',index=False,na_rep='NA')
    lines=['# Continuous influence 扩展：最终中文报告','',
           f'已完成新增五模型的全部 **2,085 个目标响应文件、66,720 条上下文/幅度观察**。加上复用的 HAT、SwinIR、SAINT，实测覆盖 **8 个实现（7 个神经模型及 Linear 对照）、两个脑队列、16 个模型/队列单元**。大表列全 **13 模型 × 2 队列，共 26 行**；接口不适用的 10 行保留 NA。',
           '',f'16 个实测单元中，**{passes} 个通过各自冻结稳定性门槛，{supports} 个同时具有正的 beyond-count 同时区间**。这不意味着 fixed-count 关联全部为正，也不是 13 个模型共同验证了连续影响机制。',
           '','## 论文与大表入口',
           '- [13 模型完整大表](CONTINUOUS_INFLUENCE_BIG_TABLE.md)；[CSV](CONTINUOUS_INFLUENCE_BIG_TABLE.csv)，包含新联合家族区间、原 legacy 区间、三个稳定性值、效应方向、阈值和信息合同。',
           '- [修订主文 PDF](revised_manuscript/main.pdf)；[修订补充 PDF](revised_manuscript/supplement.pdf)。源码在同目录。',
           '- [全部次要端点和幅度](ALL_SECONDARY_SIGNS.csv)：384 行，未按正负筛选。',
           '- [更新 MIRA 报告卡](UPDATED_MIRA_REPORT_CARD.csv)；[主张—证据矩阵](UPDATED_CLAIM_EVIDENCE_MATRIX.md)。',
           '- `CVPR_CONTINUOUS_INFLUENCE_REVIEW_PACKAGE.zip` 为本地审阅包；`outputs/installed_files.json` 记录入口更新文件及前后哈希；`DELIVERY_STATUS.json` 记录最终是否已交付。',
           '','## 必须保留的失败、负结果和空结果']
    for _,r in fails.iterrows():lines.append(f'- {r.model}/{r.dataset}：稳定性最低 {r.rank_stability_min:.6f}，门槛 {r.threshold:.2f}，**FAIL**。即使 beyond-count 点估计 {r.beyond_count:.6f} 且区间为正，也不计为合格连续影响支持。')
    for _,r in negatives.iterrows():lines.append(f'- {r.model}/{r.dataset}：固定锚数关联 **{r.fixed_count:.6f} [{r.fixed_count_low:.6f}, {r.fixed_count_high:.6f}]**，新八模型同时区间全部为负。')
    for _,r in nulls.iterrows():lines.append(f'- {r.model}/{r.dataset}：固定锚数关联 {r.fixed_count:.6f} [{r.fixed_count_low:.6f}, {r.fixed_count_high:.6f}]，同时区间跨零。')
    lines +=['','历史 SAINT 的目标知情空结果、I3Net/CycleINR 的历史 .90 门槛失败、HAT/SwinIR 协方差最坏 126.4% 近似误差、fastMRI 排名不确定性、guard 负结果和既有预算敏感性均保留。不能用本轮信息合同下的新结果覆盖另一合同下的负结果。',
             '','## 工程修复与统计合同',
             'ACVTT/IXI 与 ResUNet/两个队列最初在读取目标、生成响应之前，未通过 batch1/batch4 一致性检查；单样本适配器与原生单样本输出则全部相同。按照 [事前工程补记](BATCH_EXECUTION_ADDENDUM.md)，仅这三个没有科学结果的单元改为统一单样本执行。九上下文的原 1e-5/1e-6 容差不放宽，复核全部通过后才生成响应。原三份失败日志保留；已完成的 ACVTT/fastMRI 科学稳定性 FAIL 没有重跑或替换。',
             '原始协议、上下文、检查/目标选择、采集切片掩膜和 Q1/Q99 范围、四随机场、四幅度、固定锚数协变量均不变。HAT/SwinIR 仍用原 .85 门槛，其余 .90。Linear 是解析双锚控制；ArSSR 稠密初始化中的插值平面不计作额外物理锚。',
             '大表的新同时家族为每队列、每端点全部八个计划模型，包括数值失败单元；5,000 次检查 bootstrap 在模型间使用同一抽样。所有四个家族均有 5,000 个联合有效 draw。原三模型的点估计完全一致，旧区间在 legacy 列/历史补充表中保留，不能与新八模型家族混称。',
             '','## 复算、保护和版面验收',
             f'- 新响应全部哈希核验；从物理锚槽独立重算影响，与原实现最大差 {s["independent_embedding_max_difference"]:.3g}；全部新观察保留。',
             f'- {s["explicit_cluster_bootstrap_checks"]} 项显式病例复制与加权 bootstrap 对照通过；四个八模型同时家族从保存的全部 draw 重新计算并逐项核对。',
             '- 工程修复前已经完成的 13 个模型/队列点估计和稳定性全部保持不变；修复只补齐原先空缺的三个单元。',
             f'- {prot["files"]} 个来源/上一轮交付文件保护核验通过，包括旧原始响应、输入、目标、权重、协议与原稿。原稿快照为 `original_snapshot/manuscript/`，TMI 未改动。',
             '- 新表采用 8 pt 字体；主文保留完整 13 模型双队列大表，补充材料列全稳定性、全端点、全幅度及森林图。旧阶段与本轮结果明确分开。',
             '- 编译记录：'+json.dumps(build,ensure_ascii=False)+'；最终可达表格/版面检查见 `outputs/manuscript_verification.json` 和 `VISUAL_REVIEW.md`。',
             '','## 尚未解决的投稿风险',
             '1. 方法的新颖性与同一队列反复回顾性分析仍是审稿风险；当前区间不覆盖整个研究历史中的选择，也没有新增独立确认队列。',
             '2. eight-model 是实现覆盖，含一个解析控制及本地适配模型；不是八个结构独立的神经机制验证。原模型门槛不同，已明示，不能隐瞒为统一门槛。',
             '3. 部分模型数值失稳，固定锚数存在负关联/空结果；不能把 beyond-count 的支持扩大为普遍单调关系、通用可靠性评分或临床效用。',
             '4. 批量与单样本的 FP32 差异是工程复现边界；本轮严格保留原已完成单元和失败结果，不通过反复改执行方式寻找更有利结果。',
             '5. 本轮未新增固定上下文协方差实验，Claim D 仍仅覆盖原 HAT/SwinIR/SAINT 的 IXI 实验；不能因 continuous-influence 覆盖增加而自动扩大 D。',
             '6. 真实伦理、同意、脱敏、精确数据 release/授权仍 NEEDS HUMAN CONFIRMATION；匿名年份、编号和投稿轮次仍由作者核对。没有对外提交、发布或发送。',
             '','## 复现',
             '使用 `D:/conda/envs/MRI/python.exe -B`；原推理脚本 `scripts/run.py` 和修复脚本 `scripts/repair_batch.py` 分别绑定原 freeze 与补记 freeze。不得重跑 setup 覆盖冻结记录。已有输出无需再次 GPU 推理。数值复算使用 `scripts/analyze.py`；全部补算完成后会生成八模型家族。稿件由 `scripts/publish.py`（含 refine_manuscript）生成，再 build/render、verify_science、verify_manuscript、write_delivery_reports。finalize 的安装仅运行一次，要求入口仍匹配原快照。',
             '', '本轮范围完成后停止，不继续搜索更有利模型、阈值、掩膜、分数或子集。']
    (P/'FINAL_REPORT_ZH.md').write_text('\n'.join(lines),encoding='utf-8')
    claim='''# 更新主张—证据矩阵

| 主张 | 本轮改变 | 模型与队列 | 正/负结果边界 | 信息合同与推断 |
|---|---|---|---|---|
| A：共享/分离证据改变局部可观测性 | 不增加新证据 | 原五核心跨模型矩阵及原相位敏感性 | 原方向、支持和排名边界保留 | 原上下文/掩膜与原20对家族不变 |
| B：架构多样性不保证独立误差 | 不增加新证据 | 原五核心跨架构实验 | 未新增跨架构主矩阵，不把本轮响应探针冒充相位干预 | 原目标一致性与物理锚合同不变 |
| C：连续影响包含超出锚数量的信息 | 增加有界支持，并明确失败/负关联边界 | 8 个实现，fastMRI24/IXI115；每模型每队列完整3目标 | 逐行保留数值FAIL、fixed-count负/空关联；Linear不是神经复制 | acquired-only；新八模型/队列/端点同时家族，旧家族另列；详见完整大表 |
| D：局部协方差模型描述有限神经响应 | 不扩大 | 仍是 HAT/SwinIR/SAINT，原12个IXI检查 | 原126.4%最坏近似误差和无opposing实证保留 | 原耦合/独立构造及各自家族不变 |

对应位置：主文表1为覆盖表，表3为13模型双队列大表；主文机制、讨论与结论保留正负边界；补充最后一节为全量扩展及其全部次要端点。历史合同的空结果与本轮信息隔离，禁止用新正结果抹掉旧负结果。
'''
    (P/'UPDATED_CLAIM_EVIDENCE_MATRIX.md').write_text(claim,encoding='utf-8')
    (P/'README.md').write_text('# Continuous influence 扩展交付\n\n已完成五个新增模型的全部 2,085 个目标响应；新旧合计实测八个实现，完整大表列出 13 模型、两个队列。\n\n- [完整中文报告](FINAL_REPORT_ZH.md)\n- [大表](CONTINUOUS_INFLUENCE_BIG_TABLE.md)及[CSV](CONTINUOUS_INFLUENCE_BIG_TABLE.csv)\n- [修订主文](revised_manuscript/main.pdf)及[补充材料](revised_manuscript/supplement.pdf)\n- [冻结协议](PROTOCOL.md)及[执行修复补记](BATCH_EXECUTION_ADDENDUM.md)\n\n原稿快照与所有原始响应保留。入口安装状态以 DELIVERY_STATUS.json 为准，最终哈希见 DELIVERY_MANIFEST.json。模型失败、负关联及空结果均未删除。\n',encoding='utf-8')
    print('Final detailed reports generated',flush=True)
if __name__=='__main__':main()
