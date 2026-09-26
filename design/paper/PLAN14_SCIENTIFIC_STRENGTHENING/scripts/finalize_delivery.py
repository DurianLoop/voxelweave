"""Write current entry points and a portable source/derived-evidence package."""
from pathlib import Path
import hashlib,json,re,zipfile
import pandas as pd
P=Path(__file__).resolve().parents[1]; PAPER=P.parent
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER';TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
def write(p,t):p.write_text(t,encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mapping='''# Plan 14 声明与证据映射

所有路径相对于本目录。Plan 13 原始结论保持历史身份；其模型库 mask／成员解释由本轮 SOURCE_CORRECTIONS_ZH.md 更正。

| 声明 | 可复算输入与结果 | 稿件位置 |
|---|---|---|
| 模型库预测掩膜及成员来源 | [原预测复算](outputs/bank_mask_raw_reproduction.csv)、[manifest](outputs/bank_mask_manifest.json)、[原始脚本](scripts/bank_mask_audit.py) | 两稿支持定义；CVPR 补充 Section 15 |
| 三种评分支持的受益关联 | [全部模型相关](outputs/bank_mask_correlations.csv)、[预算](outputs/bank_mask_budgets.csv)、[配对差异](outputs/bank_mask_paired_differences.csv) | TMI retrospective consequence；CVPR 补充 |
| fastMRI 患者划分与 DICOM | [划分](outputs/fastmri_split_audit.json)、[几何](outputs/fastmri_test24_geometry.json) | 两稿方法／限制 |
| IXI 评分／端点单位交叉 | [相关](outputs/ixi_scale_contract_correlations.csv)、[预算](outputs/ixi_scale_contract_budgets.csv)、[源哈希](outputs/ixi_scale_contract_manifest.json) | TMI 受益结果；CVPR 补充四格图 |
| TopCoW 局部增益与血管负边界 | [逐平面](outputs/topcow_per_plane.csv)、[病例](outputs/topcow_per_case.csv)、[效应](outputs/topcow_effects.csv)、[排名](outputs/topcow_rankings.csv)、[风险](outputs/topcow_risk_coverage.csv) | 两稿外部实验；补充完整协议 |
| 固定估计器倍率对照 | [病例受益](outputs/topcow_benefit_per_case.csv)、[预算](outputs/topcow_benefit_budgets.csv) | TMI 外部结果；CVPR 补充 |
| TopCoW 探索性亮区规则 | [排名](outputs/bright_anchor_rankings.csv)、[覆盖](outputs/bright_anchor_coverage.csv)、[执行来源](outputs/bright_anchor_manifest.json) | TMI 解剖段落；CVPR 补充八行表 |
| CAS2023 固定规则迁移 | [逐平面](outputs/cas_transfer_per_plane.csv)、[病例](outputs/cas_transfer_per_case.csv)、[排名及风险](outputs/cas_transfer_rankings.csv)、[源哈希](outputs/cas_transfer_manifest.json) | TMI 摘要／主图／结果；CVPR 补充 |
| 历史五架构及条件相关 | [Plan 13 映射](../PLAN13_EVIDENCE_UPGRADE/CLAIM_EVIDENCE_MAP.md)，来源解释以上述更正为准 | 原主结果保持；未当作新增试验 |
| 文件保护与构建 | [原始快照清单](original_manifest.json)、[数值验证](outputs/verification.json)、[编译](build_logs/build_audit.json) | 本轮交付审计 |

L/C 是固定解析估计器，不是新神经架构。disjoint 的分歧值需要互补 phase-2 测量；亮区 mask 本身只需 phase-0 锚点。不能把该结果描述为无需额外测量的普遍获益。
'''
write(P/'CLAIM_EVIDENCE_MAP.md',mapping)
commands='''# Plan 14 运行指令

工作目录 `D:\\MRI`，解释器 `D:/conda/envs/MRI/python.exe`。已有完整结果，不必重跑原生图像推理。下列脚本只向 paper 写结果；不更改训练、数据或 checkpoint。CPU 实验；没有 GPU 依赖。

## 核验当前交付

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/verify_new_contracts.py
```

## 分析和论文构建

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/bank_mask_audit.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/fastmri_geometry.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/ixi_scale_contract.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/analyze_topcow.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/figures.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/revise_papers.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/build.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/render.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/scripts/finalize_delivery.py
```

MiKTeX 的 pdflatex／bibtex 与 Poppler 的 pdfinfo／pdftotext／pdftoppm 需可调用。本会话在沙箱内不能正常读取 MiKTeX 用户配置，已通过授权的工具权限完成构建，不涉及安装或更换模板。

## 从图像重算

执行顺序为 `prepare_inventory.py` → `topcow_experiment.py` → `analyze_topcow.py` → `bright_anchor_experiment.py` → `cas_transfer.py`。本轮 CPU 墙钟约为 TopCoW 821 秒、亮区 146 秒、CAS 258 秒（图像阶段；不含所有 bootstrap、审计和排版）。病例 CSV 已存在时推理脚本跳过已有病例；这属于续跑，不是重新生成原始预测。

如需全量独立复算，应先把整个本轮目录复制到 paper 内新的兄弟目录，在副本中使用独立空结果目录并保留必要原始快照和协议版本，勿删除或覆盖当前证据。脚本以当前目录定位 paper 和 D:\\MRI，依赖现有原始图像／标签、历史预测与 Plan 13 输出；派生证据 ZIP 不包含这些医学图像或模型权重。

`revise_papers.py` 从 original_snapshot 中的 Plan 13 稿件确定性生成当前稿，会覆盖当前两稿；人工继续修改后应先建立新快照。它不修改 Plan 13 历史目录。

E02 执行跨越了 E03 协议增补，但 E02 方法未变；记录中的两个版本哈希可在 protocol_versions 找到。E04 是读过 E02 结果后的探索，E05 是迁移前固定的规则；当前 PROTOCOL 不能追溯冒充早期外部预注册。重跑会记录当前协议版本，应保留初始运行 manifest 以区分执行。
'''
write(P/'RUN_COMMANDS_ZH.md',commands)
readme='''# MRI 层间插值双论文项目

当前科学版本：**Plan 14，2026-09-09**。新增 TopCoW 125 例、CAS2023 100 例解剖实验及固定规则迁移。完整交付见 [中文报告](PLAN14_SCIENTIFIC_STRENGTHENING/FINAL_REPORT_ZH.md)。A 类提交资料由用户自行处理；本轮不据此停止科学工作，也不虚构 80% 接收概率。

| 稿件 | PDF | 源码 | 构建 |
|---|---|---|---|
| CVPR | [主文](CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) | [main.tex](CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex) | 9 页，技术内容止于第 8 页 |
| CVPR 补充 | [补充](CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf) | [supplement.tex](CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.tex) | 10 页 |
| TMI | [主文](TMI/TMI_ARCH_GENERALIZED/main.pdf) | [main.tex](TMI/TMI_ARCH_GENERALIZED/main.tex) | 含参考文献 10 页 |

本轮核心：TopCoW 两个解析配对局部可观测性增加约 34.5 个百分点，但血管风险覆盖变差。固定亮区规则从 TopCoW 迁移到 CAS 后，不相交条件血管排序 Δρ=.073/.070，同时区间为正；整体误差排序下降，风险覆盖区间跨零。全部负结果保留。

模型库 `target_0.01` 实为目标模型预测掩膜，Linear/Cubic 是候选成员；Plan 13 对这两点的解释已在 [来源更正](PLAN14_SCIENTIFIC_STRENGTHENING/SOURCE_CORRECTIONS_ZH.md) 撤回并改正当前稿。Plan 9/11 神经机制 GT 掩膜限制仍在。IXI 四种评分／端点单位合同保留两个正关联和两个负关联，不将归一化当作普遍修复。

## 证据入口

- [协议](PLAN14_SCIENTIFIC_STRENGTHENING/PROTOCOL.md) 与 [执行版本](PLAN14_SCIENTIFIC_STRENGTHENING/protocol_versions/)
- [声明映射](PLAN14_SCIENTIFIC_STRENGTHENING/CLAIM_EVIDENCE_MAP.md)、[运行指令](PLAN14_SCIENTIFIC_STRENGTHENING/RUN_COMMANDS_ZH.md)
- [数值与保护验证](PLAN14_SCIENTIFIC_STRENGTHENING/outputs/verification.json)、[构建审计](PLAN14_SCIENTIFIC_STRENGTHENING/build_logs/build_audit.json)
- [本轮原稿快照清单](PLAN14_SCIENTIFIC_STRENGTHENING/original_manifest.json)：140 文件；Plan 13 的 135 文件快照同时验证通过。
- [Plan 13 历史报告](PLAN13_EVIDENCE_UPGRADE/FINAL_REPORT_ZH.md)、[Plan 12 报告](ARCHIVE/PLANS/PLAN12_STRICT_REVIEW_ITERATION/STRICT_REVIEW_ITERATION_REPORT_ZH.md)

所有新增成果在 paper 中，原图像、预测、checkpoint、其他项目训练不变。历史 Plan 9–12 位于 ARCHIVE/PLANS；历史脚本根目录可能因归档而失效，当前运行以 Plan 14 指令为准。当前文件为研究候选稿，尚未提交或发布。
'''
write(PAPER/'README.md',readme)
for name,folder in [('CVPR',CV),('TMI',TMI)]:
    pdf='CVPR_ARCH_GENERALIZED/PAPER/main.pdf' if name=='CVPR' else 'TMI_ARCH_GENERALIZED/main.pdf'
    write(PAPER/name/'README.md',f'# {name} 当前论文\n\n科学版本 Plan 14（2026-09-09）。[当前 PDF]({pdf})；[完整中文报告](../PLAN14_SCIENTIFIC_STRENGTHENING/FINAL_REPORT_ZH.md)。\n\n新增外部 MRA、固定规则迁移、来源纠错和单位对照；负结果完整保留。原稿与旧审计已保存在 Plan 14 original_snapshot，Plan 13 历史报告未改。\n')
    for filename in ['CLAIM_TRACEABILITY.md','FINAL_BUILD_AUDIT.md','FINAL_REVIEW_SIMULATION.md']+(['EVIDENCE_SELECTION_AUDIT.md'] if name=='CVPR' else ['REVIEWER_RISK_AUDIT.md']):
        rel='../../../PLAN14_SCIENTIFIC_STRENGTHENING' if name=='CVPR' else '../../PLAN14_SCIENTIFIC_STRENGTHENING'
        write(folder/filename,f'''# {name} Plan 14 当前审计

2026-09-09。本文档替代当前入口中的旧审计；原文完整保存在 Plan 14 original_snapshot。

见 [完整报告]({rel}/FINAL_REPORT_ZH.md)、[声明对应证据]({rel}/CLAIM_EVIDENCE_MAP.md)、[来源更正]({rel}/SOURCE_CORRECTIONS_ZH.md)、[构建记录]({rel}/build_logs/build_audit.json)。

已完成：225 例新增 MRA 解析实验、固定规则迁移、506 行模型库三掩膜审计、115 例 IXI 四种单位合同、test-24 DICOM 复核。主要风险仍是神经模型外推、CVPR 方法创新、风险筛选价值与回顾性开发；不能给出经校准的接收概率。所有合格负结果保留，A 类提交资料由用户处理。

CVPR 主文 9 页（技术止于第 8 页），补充 10 页，TMI 10 页。编译错误、未定义引用、overfull 警告均为零；最终全页渲染记录位于本轮 final_page_renders。
''')

# Check relative Markdown links in the active deliverables (not historical sources).
paths=[PAPER/'README.md',PAPER/'CVPR/README.md',PAPER/'TMI/README.md']+list(P.glob('*.md'))
bad=[];count=0
for path in paths:
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'):continue
        count+=1
        if not (path.parent/target.split('#')[0]).exists():bad.append({'file':str(path),'target':target})
assert not bad,bad

# Bind the scientific script hashes; reports and packaging may evolve independently.
for manifest,script in [('topcow_run_manifest.json','topcow_experiment.py'),('bright_anchor_manifest.json','bright_anchor_experiment.py'),('cas_transfer_manifest.json','cas_transfer.py')]:
    m=json.loads((P/'outputs'/manifest).read_text());assert m['script_sha256']==sha(P/'scripts'/script)
audit=json.loads((P/'build_logs/build_audit.json').read_text());assert all(x['success'] and not x['issues'] for x in audit)
visual={'status':'REVIEWED','method':'all-page contact sheets plus individual final anatomical-transfer figure and TMI page 8','documents':[]}
for name,pdf in [('cvpr',CV/'main.pdf'),('supplement',CV/'supplement.pdf'),('tmi',TMI/'main.pdf')]:
    pages=list((P/'final_page_renders').glob(name+'-*.png'))
    page_count=next(x['pages'] for x in audit if x['document']==name);assert len(pages)==page_count
    visual['documents'].append({'document':name,'pages':page_count,'pdf_sha256':sha(pdf),'render_count':len(pages),'observed_clipping_or_overlap':False})
write(P/'build_logs/visual_audit.json',json.dumps(visual,indent=2))

packages=P/'packages';packages.mkdir(exist_ok=True)
files=[]
for folder in [CV,TMI]:
    files.extend(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in {'.tex','.bib','.sty','.cls','.bst','.pdf','.png','.jpg','.md'})
files+=list(P.glob('*.md'))+list((P/'scripts').glob('*.py'))+list((P/'protocol_versions').glob('*.md'))+list((P/'outputs').glob('*'))
files+=[P/'original_manifest.json',P/'build_logs/build_audit.json',P/'build_logs/visual_audit.json']
files=sorted(set(files));records=[{'path':p.relative_to(PAPER).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]
write(P/'delivery_manifest.json',json.dumps({'files':records,'raw_medical_images_included':False},indent=2))
archive=packages/'PLAN14_PAPERS_AND_DERIVED_EVIDENCE.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(PAPER).as_posix())
    z.write(P/'delivery_manifest.json','PLAN14_SCIENTIFIC_STRENGTHENING/delivery_manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256'] for r in records)
result={'status':'PASS','local_markdown_links_checked':count,'package_files':len(records)+1,'package_bytes':archive.stat().st_size,'package_sha256':sha(archive),'scientific_script_hashes_match_execution':True,'build':audit}
write(P/'delivery_verification.json',json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':pass
