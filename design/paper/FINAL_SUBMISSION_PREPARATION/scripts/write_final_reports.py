from pathlib import Path
import json,datetime,pandas as pd
P=Path(__file__).resolve().parents[1]
def main():
 run=json.loads((P/'outputs/reproduction_run.json').read_text());summary=json.loads((P/'outputs/final_reproduction_summary.json').read_text());build=json.loads((P/'build_logs/build_audit.json').read_text());freeze=json.loads((P/'freeze.json').read_text());protection=json.loads((P/'outputs/final_protection.json').read_text())
 assert len(run)==6 and all(r['returncode']==0 for r in run),'Wait for full replay'
 assert summary['all_pass'] and protection['status']=='PASS'
 groups=summary['groups'];count=sum(x['checks'] for x in groups)
 text=['# 最终复现检查','','本报告由实际完整执行日志和数值检查生成，未以计划代替完成。全部输入为保全数组，历史汇总CSV仅作为断言目标；历史CSV中的冻结行键/选择仍用于忠实复现原合同。','','## 运行状态','','| 步骤 | 开始UTC | 完成UTC | 返回码 |','|---|---|---|---:|']
 for r in run:text.append(f"| {r['script']} | {r['started']} | {r['finished']} | {r['returncode']} |")
 text+=['','## 逐项核验','','| 检查文件 | 项数 | 失败 |','|---|---:|---:|']
 for r in groups:text.append(f"| outputs/{r['file']} | {r['checks']} | {r['failures']} |")
 text += ['',f'合计 **{count} 项检查，0 项失败**。其中71项是既有主要/历史观察的数组列比较，24项是新增敏感性的独立像素/几何复算与统计合同重放，87项历史显示值和148项本轮主文/图表/NA/边界断言。检查项是列级或显示值级断言，不可把330项当330个独立实验。', '', '## 主图与表格', '', '- 图1重新读取固定定性数组，断言物理z=9、四项shared/disjoint显示数值；没有新挑选案例。', '- 图2和表1由原数组重建paired-plane局部O，经预先声明的目标→模型→series→患者权重聚合；三个队列单位为24/115/8。旧ranking及stable-wrong分别重新计算并保留在补充。', '- 图3a/b及表2来自acquired-response数组；图3c和补充scatter来自全部24个proposition数组、384个幅度/上下文观察。符号、固定epsilon0、worst126.4%均保留。', '- 图4从695个phase文件重建全部40个队列×有向模型对；完整20对同时推断、fixed-A与paired-error两个排名端点分离。', '- 主表3七行和详细54行报告卡重新生成；未测字段检查NA，无跨实验借值；同条件原主要数值不改变。', '- 敏感性逐像素计算由第二实现独立重读相同预测、目标和acquired anchors；两种能量公式一致。bootstrap统计聚合复用冻结合同，因此不称完全独立软件实现。', '', '## 保护与编译', '',f"冻结 {freeze['arrays']} 个数组/原NIfTI文件，共 {freeze['array_bytes']:,} 字节；协议 SHA-256 `{freeze['protocol_sha256']}`。原址保全而非操作系统写保护。结束检查 {protection['checks']} 个数组、快照、既有证据/使用源文件，结果PASS。", '', '| 文档 | 页数 | 编译成功 | 溢出/未定义引用/LaTeX错误 |','|---|---:|---|---:|']
 for r in build:text.append(f"| {r['document']} | {r['pages']} | {r['success']} | {len(r['issues'])} |")
 text+=['','原始初次排版主文9页、末尾3行独占一页；已删去重复方法文字，将主文缩为8页（正文7页、参考文献1页）。补充材料完成浮动表格整理。精确最终页数以上表为准。MiKTeX曾因工具自动审批额度耗尽无法启动，恢复后的正常重建通过；这不是被掩盖的编译失败或科学负结果。', '', '## 可复现性边界', '', '此次重放不是全部baseline重新训练，也不认证原数据release/伦理/访问权限。历史负评分结果及外部MRA等非本轮重算部分按冻结原记录保留，不冒称都从原MRI重新计算。原文件、协议修改史和详细失败边界均可追溯。最终安装操作另外记录每个CVPR文件的前后hash；TMI不在本轮修改范围。']
 (P/'REPRODUCTION_CHECK.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
 text=f'''# 最终投稿准备变更报告

本轮严格执行有界投稿准备：完成支持区域/几何/家族敏感性、主文重排、真实报告卡、引用伦理审计和原数组复现。没有新训练、新架构、新数据集、阈值选择或评分公式。产物位于本目录，核验后同步到现有CVPR PAPER目录；原稿保存在 original_snapshot/manuscript。TMI保持原状态。

## 一、最重要的科学结论

1. **支持区域反对意见得到实证缓解。** 使用同一A0/B0/B2，替换为既有acquired-union或full common-valid支持后，fastMRI与IXI仍各20/20正同时区间。模型对效应排序最多移动一名。acquired支持的ΔO范围为6.165–15.878与13.009–28.420pp；full支持为6.153–15.870与12.995–28.356pp。不是对所有可能掩膜的普遍证明，O仍需GT评价。
2. **几何平衡保留现象，却没有消除几何解释。** residue1、residue3、等权平衡和nearest-distance匹配均保持20/20正同时区间。新mirror差异fastMRI8对、IXI6对显著，已写入主文、摘要与结论。严格四邻锚双residue合同在fastMRI不可行，所有20对保留NA；IXI可行。禁止写成纯测量身份因果作用。
3. **家族结论不是单一模型主导。** 去除任一架构所涉及的全部方向对后，剩余12对均值及中位数的描述CI仍为正。重采样检查，保留模型对相关性。不得称20个独立复现。

这些都是明确标注的事后敏感性。本轮协议在结果计算前冻结，但整个研究仍回顾性，不能倒写为预注册主要检验。

## 二、稿件和图表

- 采用题名 **When Agreement Hides Error: Auditing Shared Measurement Dependence in MRI Slice Interpolation**，原因见 TITLE_DECISION.md。连续influence的资格只在两模型、两脑队列，不能作为所有架构的泛化题名。
- 摘要重写为问题、框架、最强实证、边界四部分；只保留一个定量主线，不再把所有次级结果塞入摘要。
- 图1保留同一真实病例与物理锚标识；图2改为同一local estimand下的shared/disjoint O和shared common/observable energy。
- 表1采用新的明确聚合重表达：fastMRI ΔO16.74 [15.73,17.74]pp，IXI28.63 [28.19,29.07]pp，NingXia15.03 [13.73,16.35]pp。旧pooled-plane排名与stable-wrong图/表移到补充、数值不变，不用新聚合暗中改写历史结果。
- 图3新增观察到的signed coupled-minus-independent能量变化与固定epsilon0=.0025响应预测，保留HAT/SwinIR全部四幅度。主图caption明确worst individual error126.4%；完整scatter仍在补充。
- 图4完整跨架构矩阵保留。主表3展示七行真实MIRA报告卡，原详细54行另存；全部未测量字段为NA，covariance不冒充local ΔO。
- 主结论强调architecture diversity与evidence diversity是不同维度；MIRA不判断单次重建是否正确、不宣称临床建议或校准score。
- 补充reader-facing内部Plan数字改为语义名称，完整源路径仅留最后复现/证据地图。完整13模型、111配置、训练budget、所有adverse/null/stability/scoring结果保留。修复单列/双列浮动表格造成的空页问题。

## 三、引用与数据真实性

逐条核查主要方法和新增diversity/uncertainty引文。新增HAT/SwinIR正式原文引用，保留adapted/internal措辞；把“held-out acquired-slice checks已经由这些文献建立”的过宽句子收缩为互补采集与高阶插值先例。

fastMRI膝关节论文仍是NYU门户要求的initiative引用，不能直接删除；新增brain challenge论文和门户。精确本地release/accession及图像刊登权限仍需作者凭证，DICOM像素/位置一致不等于release认证。IXI明确CC BY-SA3.0和Imperial归属，去掉缺乏依据的2014年份。NingXia来源机构、IRB/豁免、同意/豁免、去标识和允许用途均显式待作者真实资料，不编造编号。外部挑战数据仍限定public training collections。

完整逐项PASS/FIXED/NEEDS HUMAN CONFIRMATION见 DATA_ETHICS_CITATION_AUDIT.md。上述文档缺口没有用模板文字掩盖，也没有阻断本轮可完成的本地科学与编辑任务。

## 四、复现与文件保护

冻结完成时间 {freeze['utc']}；绑定 {freeze['arrays']} 个数组/源NIfTI，{freeze['array_bytes']:,} 字节，旧主文与全部补充/最终证据另行快照。最终保护检查 {protection['checks']} 项PASS。最终六步完整CPU重放全部返回0，合计 {count} 项数值/语义检查零失败；细节见 REPRODUCTION_CHECK.md 和 outputs/reproduction_run.json。编译与逐页视觉结果见 build_logs/build_audit.json 和 VISUAL_REVIEW.md。

正常审批曾因使用额度耗尽拒绝重建调用；收到继续指令后正常恢复，没有绕过审批。当前生成的PDF经过成功重建；所有新文件留在 design/paper，本轮未向任何投稿系统或外部服务发送稿件。

## 五、仍未解除的投稿风险

| 风险 | 严重性 | 已做处理与不能替代的证据 |
|---|---|---|
| 新颖性/会议影响力 | 高 | 基本恒等式和diversity思想已知；本贡献在物理输入审计和可核验边界，CVPR是否认为足够仍不确定 |
| 回顾性选择与cohort重复使用 | 高 | 明示历史与本轮post-hoc；bootstrap不能估计全研究选择偏差，没有未接触确认队列 |
| identity与geometry未纯分离 | 高 | 平衡后正结论保留，但8/6个mirror警告；不声称identity-only因果效应 |
| 个体可靠性/实用校准缺失 | 高 | 固定A排名fastMRI无正同时CI，IXI仅16/20；失败score全部保留，不继续搜索 |
| 数据来源/伦理/图像许可 | 投稿前必须作者解除 | 具体fastMRI release；NingXia真实审批/同意/去标识/用途；数据图像刊登条件，不能凭哈希替代 |
| 窄机制适用范围与非线性边界 | 中高 | acquired-only仅HAT/SwinIR×两脑队列，worst126.4%，无opposing-sensitivity实证 |
| 模型实现与患者规模 | 中 | adapted模型非官方复现；NingXia八患者，训练预算与源协议不同不能当公平统一benchmark |
| 提交元数据与双稿范围 | 作者最终核实 | 模板仍保留原CVPR2026及匿名占位；实际目标年份/author kit/作者元数据、与TMI稿件的投稿顺序及重叠范围需作者确认，本轮不代填或发布 |

## 六、停止决定

五种最强反对意见、逐项证据和仍未解决内容见 FINAL_HOSTILE_REVIEW.md。停止新科学探索；不追加自然图像、模型、阈值或scalar。除非作者先提供真正未接触、来源认证且授权完整的新队列，再于看结果前立新协议，否则不建议在投稿前继续扩展实验。不能从现有证据给出“80%接收概率”。
'''
 (P/'FINAL_SUBMISSION_CHANGELOG.md').write_text(text,encoding='utf-8')
 print('Final reproduction and Chinese change/risk reports generated from completed checks')
if __name__=='__main__':main()
