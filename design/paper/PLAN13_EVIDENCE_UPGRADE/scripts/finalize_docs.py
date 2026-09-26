"""Refresh current entry points and archive a reviewable textual change set."""
from pathlib import Path
import hashlib, json, difflib, re

P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent
def write(p,t): p.write_text(t,encoding='utf-8')
write(PAPER/'README.md', '''# MRI 层间插值双论文项目

当前版本：Plan 13，2026-09-09。完整中文交付见 [证据审计与升级报告](PLAN13_EVIDENCE_UPGRADE/FINAL_REPORT_ZH.md)。原稿、图表和入口共 135 个文件已在修改前复制并校验，见 [保护清单](PLAN13_EVIDENCE_UPGRADE/original_manifest.json)。历史正式结果没有覆盖。

## 当前论文

| 稿件 | PDF | 源码 | 构建状态 |
|---|---|---|---|
| CVPR 机制稿 | [主文](CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) | [main.tex](CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex) | 9 页，技术内容止于第 8 页 |
| CVPR 补充材料 | [补充](CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf) | [supplement.tex](CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.tex) | 8 页 |
| TMI 医学 QA 稿 | [主文](TMI/TMI_ARCH_GENERALIZED/main.pdf) | [main.tex](TMI/TMI_ARCH_GENERALIZED/main.tex) | 含参考文献 10 页 |

三份 PDF 已重建并逐页渲染审查。当前是研究候选稿，不能直接视为投稿完成：伦理、作者资料、双稿重合与提交顺序、目标年份模板及临床验证仍未解决。

## 本轮核心结论

- fastMRI 24 例、IXI 115 例，五架构的局部 observable gain 在四种病例内/病例间汇总口径下，40 个五模型同时区间全部为正；这些敏感性结果不是独立重复试验。
- 排序提升较弱：历史中位数排名口径的同时区间仅支持 IXI 3/5 模型，fastMRI 0/5。历史逐模型区间和所有合格负结果保留。
- 控制当前 ×4 误差后，fastMRI/NingXia 全部 26 个 Anchor-CV 受益条件相关区间跨零。NingXia 推断仍按 8 患者簇携带 22 序列。
- 新增 IXI I3Net 同架构、倍率专用不同权重实验：115 对输出、7,334 个共同缺失平面。原始分数相关为正；acquired-only 归一化分数对原始尺度受益排序反转，50% 预算低于随机的负结果已写入两稿。
- 纠正 MAE/RMSE 定义，披露目标掩膜和旧尺度信息访问。IXI wrapper 零误差只验证每模型一例，不能说验证了全部 115 例。

## 证据与复现

| 入口 | 内容 |
|---|---|
| [Plan 13 完整报告](PLAN13_EVIDENCE_UPGRADE/FINAL_REPORT_ZH.md) | 方法、正负结果、修改细节、外部规则、14 项剩余风险 |
| [协议](PLAN13_EVIDENCE_UPGRADE/PROTOCOL.md) | E01–E04，探索性分析、纳入规则、重采样单位 |
| [证据映射](PLAN13_EVIDENCE_UPGRADE/CLAIM_EVIDENCE_MAP.md) | 当前有效的 paper 相对路径 |
| [运行指令](PLAN13_EVIDENCE_UPGRADE/RUN_COMMANDS_ZH.md) | 可执行新脚本、构建与验证 |
| [数值校验](PLAN13_EVIDENCE_UPGRADE/outputs/verification.json) | 原始保护、74 相关复现、独立条件相关、支持集检查 |
| [构建校验](PLAN13_EVIDENCE_UPGRADE/build_logs/build_audit.json) | 页数及日志问题计数 |

Plan 9–12 实际均位于 `ARCHIVE/PLANS/`，不是 paper 顶层：

- [Plan 9](ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/FINAL_REPORT.md)：架构泛化与重建语境。
- [Plan 10](ARCHIVE/PLANS/PLAN10_ACCEPTANCE_ITERATION/FINAL_REPORT_ZH.md)：全模型库与错误相关。
- [Plan 11](ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/PROTOCOL.md)：同架构受益、IXI 五架构、identity-swap。
- [Plan 12](ARCHIVE/PLANS/PLAN12_STRICT_REVIEW_ITERATION/STRICT_REVIEW_ITERATION_REPORT_ZH.md)：上一阶段严格审稿报告。

历史脚本的 `parents[]` 根路径会因归档失效，旧运行命令不能照抄。不要以 smoke/debug 覆盖 full；本轮新脚本显式读取正式历史输入并独立输出。

## 维护约定

当前稿在 `CVPR/CVPR_ARCH_GENERALIZED/PAPER/` 和 `TMI/TMI_ARCH_GENERALIZED/`；本轮全部新增研究产物在 `PLAN13_EVIDENCE_UPGRADE/`。旧稿保留在各自 `archive/`，旧 Plan 保留在 `ARCHIVE/PLANS/`，历史压缩包保留在 `ARCHIVE/PACKAGES/`。原始入口说明见 [Plan 13 修改前快照](PLAN13_EVIDENCE_UPGRADE/original_snapshot/README.md)。

两稿共享核心机制、队列和实验；不能作为互不相关的研究同时提交。详细边界及下一轮优先实验见完整报告。
''')
for name,folder,prefix in [('CVPR','CVPR_ARCH_GENERALIZED/PAPER','../'),('TMI','TMI_ARCH_GENERALIZED','../')]:
    write(PAPER/name/'README.md', f'''# {name} 当前论文入口

2026-09-09 更新。当前 [PDF]({folder}/main.pdf)、[LaTeX]({folder}/main.tex)、[构建审计]({folder}/FINAL_BUILD_AUDIT.md)。

完整交付：[Plan 13 中文报告](../PLAN13_EVIDENCE_UPGRADE/FINAL_REPORT_ZH.md)；数据路径：[证据映射](../PLAN13_EVIDENCE_UPGRADE/CLAIM_EVIDENCE_MAP.md)；复现：[运行指令](../PLAN13_EVIDENCE_UPGRADE/RUN_COMMANDS_ZH.md)。

当前版本已纳入同时区间、当前误差调整和 IXI 共同支持补充实验，包括全部合格负结果。仍为待作者核验的研究候选稿，投稿风险详见完整报告。修改前文件见 `../PLAN13_EVIDENCE_UPGRADE/original_snapshot/{name}/`。
'''+ ('\n[CVPR 补充 PDF](CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf)，8 页。\n' if name=='CVPR' else ''))

build=json.loads((P13/'build_logs/build_audit.json').read_text())
for rel,which in [('CVPR/CVPR_ARCH_GENERALIZED/PAPER',['cvpr','supplement']),('TMI/TMI_ARCH_GENERALIZED',['tmi'])]:
    d=PAPER/rel
    back='../../../../' if rel.startswith('CVPR') else '../../../'
    # Relative from current package to PLAN13 is one level shorter than to design.
    back='../../../' if rel.startswith('CVPR') else '../../'
    link=back+'PLAN13_EVIDENCE_UPGRADE/'
    write(d/'FINAL_BUILD_AUDIT.md', '# Plan 13 最终构建审计\n\n2026-09-09。\n\n'+ '\n'.join(f"- {r['document']}: {r['pages']} 页；成功 {r['success']}；undefined / LaTeX error / overfull 检出 {len(r['issues'])}；PDF {r['bytes']} 字节。" for r in build if r['document'] in which)+f'''\n\n采用 pdflatex → BibTeX（主文）→ pdflatex ×2。日志、文本提取及逐页预览见 [构建记录]({link}build_logs/build_audit.json) 和 [完整报告]({link}FINAL_REPORT_ZH.md)。CVPR 技术内容止于第 8 页；TMI 10 页包括参考文献。当前 CVPR 仍为 2026 review style 布局基线，未宣称符合最终 2027 author kit。非致命 underfull/font 提示保留在原始日志。

原审计已保存在 [修改前快照]({link}original_snapshot/{rel}/FINAL_BUILD_AUDIT.md)。编译成功不代表伦理、作者资料或科学风险已解除。
''')
    write(d/'CLAIM_TRACEABILITY.md',f'''# Plan 13 当前主张追溯

当前有效的正式结果路径、输出字段与主张边界统一见 [完整证据映射]({link}CLAIM_EVIDENCE_MAP.md)。本轮新增输出、哈希、数值复核见 [中文报告]({link}FINAL_REPORT_ZH.md)。

Plan 9–12 的真实位置是 `design/paper/ARCHIVE/PLANS/`。当前稿已明确 GT mask、不同倍率权重、IXI wrapper 一例 gate、同时区间与条件受益的边界。全部合格负结果保留。

原逐项追溯表按历史状态保存在 [修改前快照]({link}original_snapshot/{rel}/CLAIM_TRACEABILITY.md)，其中旧路径和旧范围表述应结合本轮证据映射阅读，不再作为当前审计结论。
''')
    audit='EVIDENCE_SELECTION_AUDIT.md' if rel.startswith('CVPR') else 'REVIEWER_RISK_AUDIT.md'
    write(d/audit,f'''# Plan 13 证据与投稿风险审计

当前审计以 [完整中文报告]({link}FINAL_REPORT_ZH.md) 第 2–6、9 节为准。原文件在 [修改前快照]({link}original_snapshot/{rel}/{audit})，用于历史追溯。

本轮没有因结果不利排除合格模型、病例或端点。保留低 influence 选择失败、jackknife IQR/residualization 失败、NingXia null/mixed、Res-SRDiff 反例及排序不稳健，并新增当前误差调整后相关衰减和 IXI 归一化预算低于随机。新增分析属于探索性再分析，不能冒充事前注册或独立确认。

未解除：伦理及作者资料、双稿科学重合和投稿顺序、目标年份最终模板、GT 支持/尺度信息、不同权重混杂、八患者小样本、适配模型谱系、真实采集与临床终点缺口。详情与下一轮优先级见完整报告。
''')

report=P13/'FINAL_REPORT_ZH.md'
t=report.read_text(encoding='utf-8').replace('日期：2026-09-08。','分析与外部核验：2026-09-08；最终交付：2026-09-09。')
write(report,t)

manifest=json.loads((P13/'original_manifest.json').read_text())
changed=[]; diffs=[]
for r in manifest['files']:
    p=PAPER/r['path']; old=P13/'original_snapshot'/r['path']
    if not p.exists(): raise RuntimeError('Protected original path removed: '+r['path'])
    current=hashlib.sha256(p.read_bytes()).hexdigest()
    if current!=r['sha256']:
        changed.append({'path':r['path'],'original_sha256':r['sha256'],'current_sha256':current})
        if p.suffix in ['.tex','.bib','.md']:
            diffs.extend(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),p.read_text(encoding='utf-8').splitlines(True),fromfile='original/'+r['path'],tofile='current/'+r['path']))
write(P13/'outputs/changed_original_files.json',json.dumps(changed,indent=2,ensure_ascii=False))
write(P13/'outputs/manuscript_changes.diff',''.join(diffs))

# Check local links in the current delivery documents, ignoring external URLs/anchors.
docs=[PAPER/'README.md',PAPER/'CVPR/README.md',PAPER/'TMI/README.md',P13/'FINAL_REPORT_ZH.md',P13/'CLAIM_EVIDENCE_MAP.md',P13/'RUN_COMMANDS_ZH.md']
docs += [PAPER/r/'CLAIM_TRACEABILITY.md' for r in ['CVPR/CVPR_ARCH_GENERALIZED/PAPER','TMI/TMI_ARCH_GENERALIZED']]
broken=[]; n=0
for doc in docs:
    for s in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
        if '://' in s or s.startswith('#'): continue
        n+=1
        if not (doc.parent/s.split('#')[0]).exists(): broken.append({'document':str(doc.relative_to(PAPER)),'target':s})
write(P13/'outputs/document_link_audit.json',json.dumps({'checked':n,'broken':broken},indent=2,ensure_ascii=False))
print(json.dumps({'modified_existing_files':len(changed),'links_checked':n,'broken_links':broken},ensure_ascii=False))
if broken: raise RuntimeError('Broken delivery links')
