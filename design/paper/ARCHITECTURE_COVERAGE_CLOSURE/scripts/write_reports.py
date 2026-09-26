from pathlib import Path
import json,datetime
import pandas as pd,numpy as np
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';S=P.parent/'FINAL_SUBMISSION_PREPARATION'
def write(name,text):(P/name).write_text(text,encoding='utf-8')
def main():
 d=pd.read_csv(P/'FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.csv');e=pd.read_csv(P/'MODEL_EVIDENCE_ELIGIBILITY.csv');b=pd.read_csv(P/'EXPANDED_PHENOMENON_BREADTH.csv');c=pd.read_csv(P/'outputs/saint_covariance_summary.csv');v=json.loads((P/'outputs/reproduction_checks.json').read_text());build=json.loads((P/'build_logs/build_audit.json').read_text())
 assert v['status']=='PASS' and all(r['success'] and not r['issues'] for r in build)
 lines=['# 五核心架构 acquired-only 影响复核','','同一 acquired-only 信息合同下，实际可运行 HAT、SwinIR、SAINT；I3Net/CycleINR 保留接口不合格 NA。技术适用性、数值稳定性和 beyond-count 支持是三个不同判断。','','| 队列 | 模型 | 最低稳定性 / 门槛 | beyond count [同时95%CI] | 固定count [同时95%CI] | 判定 |','|---|---|---|---|---|---|']
 for r in d.itertuples():
  valid=r.technical_eligibility=='ELIGIBLE';fmt=lambda x:f'{getattr(r,x+"_estimate"):.6f} [{getattr(r,x+"_simultaneous_low"):.6f},{getattr(r,x+"_simultaneous_high"):.6f}]' if valid else 'NA'
  lines.append(f'| {r.dataset} | {r.model} | '+(f'{r.rank_stability_min:.6f} / {r.threshold:.2f}' if valid else 'NA / .90')+f' | {fmt("beyond_count")} | {fmt("fixed_count")} | {r.influence_claim} |')
 lines+=['','HAT/SwinIR 原每队列两模型同时家族原样保留。新增 SAINT 复制检验按每端点覆盖两个队列，仍使用原5000检查bootstrap及18003/18004种子；不是把它加入原家族，也不声称五模型全局同时覆盖。该扩展家族在新数值计算前写入 PROTOCOL.md。','SAINT 每个队列的 .005/.02/−.01 三次排名稳定性均须≥.90；HAT/SwinIR 的 .85 门槛不变。三者均数值 PASS 且对应 beyond-count 同时区间为正。原六-stratum 总体门槛仍为NA，未补造 acquired-only NingXia。','历史 SAINT beyond-count .014 [−.002,.029] 和 fixed-count .063 [−.021,.149] 仍是有效负/不确定结果。其全检查强度范围、目标掩膜和混合精度合同不同，不能与新 acquired-only 数值互填，也不能解释为旧空结果被证伪。','历史 I3Net (.859,.737,.939) 和 CycleINR (.779,.857,.876) 的 .90 门槛失败照常保留。这些数字属于历史 IXI 四锚实验，不是 fastMRI/IXI 本轮双锚 acquired-only 稳定性。','全部48个次要端点×幅度/队列组合保存在 outputs/saint_secondary_signs.csv，并在补充材料列全。较弱的直接disagreement优势（fastMRI primary .002943）不替换更有利alignment主端点；paired/reference error 关联较弱，不能泛化成可靠误差预测器。','所有417目标的原始响应数组和13344上下文/幅度观察保留；响应写盘并绑定哈希后才读取独立目标。输入掩膜、Q1偏移、Q99-Q1范围、物理锚点、四个Rademacher种子与九上下文记录均已核验。']
 write('FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.md','\n'.join(lines))
 write('UPDATED_CLAIM_EVIDENCE_MATRIX.md',f'''# 架构覆盖后的主张—证据矩阵

| 主张 | 适用模型 / 队列 | 信息合同 | 正结果 | 空结果 / 稳定性失败 | 推断家族 | 稿件落点 | 本轮影响 |
|---|---|---|---|---|---|---|---|
| A：共享/分离证据改变局部可观测性 | 原五核心；fastMRI24/IXI115，原同模型两架构另含NingXia8患者 | 主矩阵同目标 target1% support；原支持/几何敏感性不变 | 原每队列20/20有向对同时CI正 | orientation差8/20与6/20；浅层fastMRI严格四邻锚NA | 原20对/队列/端点；扩展八模型/队列/支持单列 | 主现象图、覆盖表；补充全部扩展表 | **仅澄清覆盖**。新增同输出对照 shared O=0为构造；不能把正ΔO当八次独立机制验证 |
| B：架构多样性不保证独立误差 | 原 HAT/SwinIR/SAINT/I3Net/CycleINR 五模型 | 固定A0，B0→B2；共同目标与支持；无TTA | 原主矩阵不变 | fastMRI fixed-A排名0/20，IXI16/20；几何混杂未完全解除 | 原20对同时家族不变 | 主跨架构图与讨论 | **仅澄清覆盖**。未新增可证明B的跨模型矩阵，不将八个self-control冒充B证据 |
| C：连续局部响应影响超出锚数 | HAT/SwinIR/SAINT；两个脑队列 | 掩膜、量程、扰动均acquired-only；目标只用于alignment评估 | 新SAINT fastMRI .032751 [.015435,.050067]；IXI .132790 [.125627,.139953]；fixed-count .379778/.417380；均PASS | 历史SAINT空结果保留；I3Net/CycleINR历史FAIL且本轮接口NA；五个可用接口未跑 | 原HAT/SwinIR每队列2模型家族原样；SAINT新2队列/端点家族，不混称全五模型校正 | 更新图3、全核心数值表、报告卡 | **增强有界证据**：新增非Transformer实测支持；不支持普遍性 |
| D：局部协方差模型描述有限神经响应 | HAT/SwinIR/SAINT；同12个IXI检查 | 固定上下文、共同锚、8平衡场、Cartesian独立构造、epsilon0=.0025；不读取目标 | SAINT四幅度mean同时区间均负；48例全部aligned | 原HAT/SwinIR worst126.4%保持；无opposing实证；不保证全局Jacobian | 原8模型幅度对比家族保持；SAINT单列4幅度家族 | 图3c、补充全部幅度表 | **增强有界证据**：非Transformer局部趋势；未缩小原实测最坏边界 |

13 个名称代表本地重建实现，不等于13种结构独立架构或13个MIRA机制基线。ArSSR与内部CycleINR共享代码谱系；实验使用的权重和接口绑定另列。

NEEDS HUMAN CONFIRMATION：NingXia机构/IRB或豁免/同意或豁免/脱敏/许可，以及精确fastMRI release与授权。计算不能替代真实文件。
''')
 rows=['# 架构覆盖闭环：详细中文变更报告','','本轮只处理当前CVPR稿件，TMI未改动。工作范围在新实验前冻结：13模型适用性审计、剩余核心的合格 acquired-only 复测、兼容已有基线的相位覆盖，以及稿件和报告卡重组。没有训练、加入新模型/队列、评分公式或阈值搜索。','','## 完成范围与实际计数',f'- 重建记录：13个实现，111个配置；原生PSNR/SSIM/MAE/MSE/NCC、20个预算比较与负结果保留在补充材料。',f'- 物理相位干预：{int((e.level_B=="ELIGIBLE").sum())}/13接口已完成；其中五核心仍为主跨模型实验，另外八个只做明示退化self-control的次要相位敏感性。因此“重建证据之外完全没有相位证据”的模型为0；不等于13模型都验证连续机制。','- 严格acquired-only：3个模型已实测有效（HAT/SwinIR/SAINT）；5个额外接口可用未运行（Linear/ACVTT/ArSSR/ResUNet/SMamba-UNet）；5个在当前精确合同下不合格（Cubic/Res-SRDiff/CycleINR/Pix2Pix-GAN/I3Net）。可用而未运行的模型不得计为验证成功。','- 稳定性：3个实测模型在两个脑队列各自门槛下PASS，共6个stratum。HAT/SwinIR .85、SAINT .90；既有六-stratum aggregate gate仍NA。数值稳定与beyond-count区间阳性分别记录。','- 固定上下文：3个模型有实际IXI证据；新SAINT仅在IXI稳定性通过后按既定12检查/四上下文/四幅度运行。','','## 新 acquired-only 结果','详见 [五核心影响审计](FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.md) 和同名CSV。SAINT的最小稳定性为fastMRI .950686、IXI .996341。beyond-count分别 .032751与.132790；fixed-count分别 .379778与.417380，规定家族区间均为正。','新结果与历史SAINT空结果合同不同，均保留。该变化不是为了正结果重调掩膜、精度、幅度或门槛；本次先固定复用最终acquired-only合同，再推理。直接disagreement的fastMRI beyond-count只有 .002943（描述），不能以alignment的阳性代替直接误差/可靠性结论。','','## 新固定上下文结果',f'SAINT四幅度的median相对近似误差为{100*c.median_relative_error.min():.3f}%–{100*c.median_relative_error.max():.3f}%，worst为{100*c.max_relative_error.max():.3f}%。原HAT/SwinIR的126.4%最坏误差完整保留；48个新例均aligned，无opposing例，不扩张到未观察符号分支。恒等式闭合仍单列为代数核验。','','## 扩展基线的解释限制','八个非核心基线均按原master x4 checkpoint与当前五目标注册运行两个脑队列，三种support全部保留。目标自身重复导致shared O=0，是构造事实。新增正ΔO主要确认物理相位响应与接口覆盖，不能当成八次独立shared-error机制验证。原五模型主矩阵未被替换，也没有结果导向扩展跨模型pair集合。','Res-SRDiff的源码实际使用Gaussian随机采样；不能沿用模型注释中“deterministic”的不准确标签。相位实验固定单一外生RNG状态，不搜索种子；这项条件化不自动使其满足原有限响应合同。','ArSSR现有wrapper接受变深度/stride，故列为潜在可用而未运行的有限响应接口；不能仅因为尚未写适配器就宣称结构不可能。CycleINR的既有有限响应合同另有明确四锚x4限制，不能在本轮静默改成双锚。','','## 工程修复与可复现性','ArSSR首个目标选算检查发现0.0001220703125 native-unit偏差，超过事前1e-4容差；原结果未进入相位输出，失败日志保留。修复把坐标运算恢复为原wrapper逐步float32运算；两个队列/两个phase与完整wrapper最大差均为0。没有放宽容差。','Res-SRDiff完整体积网络推理耗时较长，采用省略无关输出神经计算的加速；仍逐步消耗每张未用切片的全部采样随机数。两个队列、两phase的首病例对照同时验证输出最大差0及最终CUDA RNG状态完全相同。已完成的原路径病例被保留，剩余才使用等价路径。','所有输入/旧证据只读。原3955数组在推理前重新核验哈希通过；22个本轮脑队列权重完整加载检查，所有张量有限。新响应在目标读取前绑定文件哈希。后续原数组独立重算与稿件保留检查见 REPRODUCTION_CHECK.md。','','## 稿件变更','主文新增13行覆盖表，符号区分支持、历史空结果、资格/稳定性失败以及未运行。图3增加SAINT，保留原两模型及原最坏误差；所有五核心进入数值表和报告卡。摘要、引言、方法、结果、讨论、结论明确现象宽度与连续影响的更窄资格。完整重建排行榜仍在补充材料。','原稿快照：original_snapshot/manuscript。新稿：revised_manuscript。核验后仅将经审核的CVPR文件安装到原论文入口；原FINAL_SUBMISSION_PREPARATION交付包和TMI保留。','','## 尚未解决的投稿风险','1. 数据与伦理仍 NEEDS HUMAN CONFIRMATION：NingXia批准/豁免、同意/豁免、脱敏及许可，精确fastMRI来源release/授权均不能由代码推断。','2. 方法创新幅度和大量回顾性复用仍是强审稿风险；本轮没有新的独立确认队列，bootstrap不覆盖全部历史选择。','3. 新八模型self-control是弱对照；不能说13模型共同验证MIRA机制。即使数值全部为正，也没有消除该设计限制。','4. continuous influence仍只实测三个兼容模型，且支持的是局部association/covariance趋势，不是全模型普适性、校准可靠性或临床噪声模型。','5. 原空结果、历史稳定性失败、mirror方向效应、弱/空排名、guard无明确收益、NingXia与Res-SRDiff负结果全部有效。','6. 原匿名投稿年份/编号等元数据仍需作者与实际投稿轮次匹配；本地交付不是已向会议提交。','','## 终止','本轮边界已关闭。不得根据现在的正结果继续寻找更有利架构、score、mask、阈值或数据子集。论文证据有所加强，但无法从这些回顾性结果推导可信的接收概率。']
 write('ARCHITECTURE_COVERAGE_CHANGELOG.md','\n'.join(rows))
 lines=['# 本轮复现与保护检查','',f'状态：{v["status"]}；UTC {v["utc"]}。','']
 for r in v['checks']:lines.append('- '+r['check']+'：'+r['status']+'；'+json.dumps({k:x for k,x in r.items() if k not in ['check','status']},ensure_ascii=False))
 lines+=['','逐像素/物理锚嵌入重建独立于原influence查找实现；固定上下文使用完整两两距离矩阵重算。聚类bootstrap沿用冻结统计代码，并用显式重复检查重采样核对前3个draw。不是声称统计软件实现完全独立。','原HAT/SwinIR数值保留其旧完整原数组复现记录，本轮再断言原数值和家族不变；不冒称重训或重新计算全部111个训练配置。','扩展相位的数值表来自新NPZ与原目标/实际acquired mask。完整输出一致性与随机状态核验保存在outputs/phase_v2_validation.json；ArSSR最初失败记录未删除。','', '编译：'+json.dumps(build,ensure_ascii=False)]
 write('REPRODUCTION_CHECK.md','\n'.join(lines))
 write('REPRODUCIBILITY.md','''# 复现与文件入口

工作目录 D:/MRI，Python D:/conda/envs/MRI/python.exe，使用 -B 防止在受保护代码路径写缓存。

已冻结协议 PROTOCOL.md；旧原数组清单绑定 FINAL_SUBMISSION_PREPARATION/ARRAY_FREEZE_MANIFEST.json。SOURCE_MANIFEST.json 绑定来源与原稿快照；model_registry.json 是22个使用权重，不是所有候选checkpoint的总计。

CPU重新计算：依次运行 scripts/analyze_core.py、scripts/analyze_expanded.py、scripts/eligibility.py、scripts/revise_paper.py、scripts/reproduce_closure.py、scripts/build.py、scripts/write_reports.py。analyze_core 读取原观察表，reproduce_closure 从原始响应独立验证它；analyze_expanded 直接读新相位NPZ。

GPU推理（已有输出无需再跑）：core_acquired.py；通过IXI稳定性后 saint_covariance.py。expanded_phase.py 为首版冻结wrapper路径，ArSSR首病例精度检查失败记录保留。validate_phase_v2.py 验证坐标/RNG等价，全部通过才允许 expanded_phase_v2.py。该脚本复用已完整保存并有metadata的输出。不要再次运行setup.py覆盖当前冻结记录。

模型来源、native指标路径、确切信息合同在 MODEL_EVIDENCE_ELIGIBILITY.csv/.md。新419类数组与所有哈希在最终输出清单（实际数量以清单为准）。临床原数组不放入LaTeX交付ZIP，不对外发布。

LaTeX源码在 revised_manuscript；原稿在 original_snapshot/manuscript；经最终检查后仅更新 CVPR/CVPR_ARCH_GENERALIZED/PAPER 的相关文件。TMI与旧交付包未修改。数据伦理/使用授权仍由作者提供真实资料。
'''.replace('新419类数组','新响应、协方差和相位数组'))
 write('FINAL_REPORT_ZH.md','# 架构覆盖闭环交付\n\n详细结果、审计、文件入口与剩余投稿风险见 [完整中文报告](ARCHITECTURE_COVERAGE_CHANGELOG.md)。\n')
 print('Final Chinese reports generated')
if __name__=='__main__':main()
