"""Publish local entry points and a hash-verified source/derived-evidence archive."""
from pathlib import Path
import hashlib,json,zipfile,re
P=Path(__file__).resolve().parents[1];PAPER=P.parent;CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER';TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,t):p.write_text(t,encoding='utf-8')
write(P/'RUN_COMMANDS_ZH.md',r'''# Plan 15 运行与复现

工作目录 `D:\MRI`；使用现有 MRI Python 环境。无需重训或 GPU，原始文件只读，新增输出均在 paper。

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/audit_master.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/recover_saint.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/analyze_baselines.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/revise_and_plot.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/build.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/verify.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/render.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN15_BASELINE_INTEGRATION/scripts/finalize.py
```

仅核验现有结果时执行 `verify.py` 即可。`recover_saint.py` 会读原始 GT／SAINT 输出重新评价 48 个体数据；其余数值步骤主要读取既有 CSV，不运行网络。

`audit_master.py` 保留主表中的既定配置，寻找五指标匹配的原始 summary；所有完全匹配的候选来源都保留。它不会用后来更好的 profile 替换原主表。两项被覆盖的 SAINT summary 在 `analyze_baselines.py` 中接回原预测重建的结果。匹配不是独立实验，也不对已知结果赋予预注册身份。

`revise_and_plot.py` 从本轮 `original_snapshot` 读取修改前稿件，会重新生成当前 CVPR／TMI 主文及 baseline 补充；若已人工修改稿件，应先另建快照，避免覆盖人工工作。

LaTeX 使用已有 pdflatex/bibtex；PDF 文本与渲染使用 pdfinfo/pdftotext/pdftoppm。当前环境需要访问用户 MiKTeX 配置，构建及渲染已经通过授权执行；曾遇审批额度拒绝，重试同一低风险操作后完成，没有改用绕过方案。

ZIP 含当前论文源码、图表、派生 CSV 和本轮脚本，不含原医学图像、网络预测、checkpoint 或完整历史快照。编译当前论文可以使用包中源码；完整复算仍依赖 D:\MRI 下的源数据／baseline、pre 中的历史指标，以及快照文件。不要把此包描述为包含全部数据的自足环境。
''')
write(PAPER/'README.md',r'''# MRI 层间插值双论文项目

当前科学版本：**Plan 15，2026-09-10**。已将实验主表的全部 baseline 系统纳入两篇论文。[本轮中文报告](PLAN15_BASELINE_INTEGRATION/FINAL_REPORT_ZH.md) · [逐方法使用情况](PLAN15_BASELINE_INTEGRATION/BASELINE_USE_MAP_ZH.md)。

| 文档 | 当前 PDF | 页数与新增内容 |
|---|---|---|
| CVPR 主文 | [main.pdf](CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) | 9 页；第 8 页 Table 4 是完整 13 方法、三队列 ×4 表；技术内容止于第 8 页 |
| CVPR 补充 | [supplement.pdf](CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf) | 15 页；第 11–15 页含全部五指标、多尺度、20 项预算对照 |
| TMI 主文 | [main.pdf](TMI/TMI_ARCH_GENERALIZED/main.pdf) | 10 页；第 7 页 Table VI 完整 baseline，第 6 页预算分析 |
| TMI baseline 补充 | [baseline_supplement.pdf](TMI/TMI_ARCH_GENERALIZED/baseline_supplement.pdf) | 5 页；完整 baseline 证据 |

本轮核验 111 配置、555 指标值、3,735 行病例结果；补回 SAINT 两项覆盖丢失 summary。20 项延长训练比较中，15 项 MAE 同时区间支持改善，5 项跨零。Res-SRDiff 短预算退化受训练预算影响，不能外推为整个模型家族失败。原主表、原指标、预测和既有训练未改动。

13 个重建 baseline 不等于 13 架构物理干预验证：五架构干预的原有边界仍保留。原生全平面指标与旧 masked／共同支撑 QA 端点不互填，不能因为旧 masked 表缺失就说原 baseline 没跑完。

## 当前证据与复现

- [逐行来源](PLAN15_BASELINE_INTEGRATION/outputs/baseline_all_verified.csv)、[全部预算分析](PLAN15_BASELINE_INTEGRATION/outputs/training_budget_paired.csv)
- [协议](PLAN15_BASELINE_INTEGRATION/PROTOCOL.md)、[运行指令](PLAN15_BASELINE_INTEGRATION/RUN_COMMANDS_ZH.md)
- [数值与文件保护核验](PLAN15_BASELINE_INTEGRATION/outputs/verification.json)、[构建日志](PLAN15_BASELINE_INTEGRATION/build_logs/build_audit.json)
- [Plan 14 报告](PLAN14_SCIENTIFIC_STRENGTHENING/FINAL_REPORT_ZH.md)：225 例 MRA、固定规则迁移、模型库来源更正，相关结果仍在当前稿件中
- [Plan 13 历史报告](PLAN13_EVIDENCE_UPGRADE/FINAL_REPORT_ZH.md)、[Plan 12 历史报告](ARCHIVE/PLANS/PLAN12_STRICT_REVIEW_ITERATION/STRICT_REVIEW_ITERATION_REPORT_ZH.md)

所有新成果在 paper 内，本轮 149 文件快照保护改动前版本。A 类提交资料由用户处理。当前为研究候选稿，尚未提交或发布，接收概率没有可校准数值。
''')
for name,folder,rel in [('CVPR',CV,'../../../PLAN15_BASELINE_INTEGRATION'),('TMI',TMI,'../../PLAN15_BASELINE_INTEGRATION')]:
    pdf='CVPR_ARCH_GENERALIZED/PAPER/main.pdf' if name=='CVPR' else 'TMI_ARCH_GENERALIZED/main.pdf'
    write(PAPER/name/'README.md',f'# {name} 当前论文\n\n科学版本 Plan 15（2026-09-10）。[当前 PDF]({pdf})；[完整 baseline 整合报告](../PLAN15_BASELINE_INTEGRATION/FINAL_REPORT_ZH.md)。\n\n13 方法三队列主表进入正文，111 配置完整五指标和全部训练预算分析进入补充。旧物理干预、MRA 迁移与负结果保留；全部文件有改动前快照。\n')
    for file in ['CLAIM_TRACEABILITY.md','FINAL_BUILD_AUDIT.md','FINAL_REVIEW_SIMULATION.md']+(['EVIDENCE_SELECTION_AUDIT.md'] if name=='CVPR' else ['REVIEWER_RISK_AUDIT.md']):
        write(folder/file,f'''# {name} Plan 15 当前审计

日期 2026-09-10。原审计保存在本轮 original_snapshot。

新增主表覆盖全部 13 方法和三队列 ×4；补充保留 111 配置、555 指标值及 20 项已记录的延长训练实验。两份 SAINT 覆盖丢失 summary 已从 48 个输出恢复。主 MAE 同时区间 15 项改善、5 项跨零。原生整平面评价与 masked 共同支撑不能互填，13 方法重建比较不是 13 架构干预。

见 [完整报告]({rel}/FINAL_REPORT_ZH.md)、[方法使用说明]({rel}/BASELINE_USE_MAP_ZH.md)、[逐行来源]({rel}/outputs/baseline_all_verified.csv)、[保护与数值验证]({rel}/outputs/verification.json)、[构建]({rel}/build_logs/build_audit.json)。

四稿构建无错误、未定义引用及 overfull 警告：CVPR 主文 9 页（技术止于 8），补充 15 页；TMI 主文 10 页，baseline 补充 5 页。共 39 页已渲染并查看，新增主表和预算图另行查看，未发现遮挡或越界。

尚未解决：方法创新性、其余架构的同协议 QA 干预、神经模型 acquired-only 完整验证、临床筛选收益及历史训练／测试资格边界。当前不提供接收概率；A 类事项由用户处理。
''')
build=json.loads((P/'build_logs/build_audit.json').read_text());visual=[]
for name,pdf in [('cvpr',CV/'main.pdf'),('supplement',CV/'supplement.pdf'),('tmi',TMI/'main.pdf'),('tmi_baselines',TMI/'baseline_supplement.pdf')]:
    pages=next(r['pages'] for r in build if r['document']==name)
    assert len(list((P/'final_page_renders').glob(name+'-*.png')))==pages
    visual.append({'document':name,'pages':pages,'pdf_sha256':sha(pdf),'review':'all-page contact sheets; individual baseline tables and budget figure also viewed','clipping_or_overlap_observed':False})
write(P/'build_logs/visual_audit.json',json.dumps(visual,indent=2))
files=[]
for folder in [CV,TMI]:files += [x for x in folder.rglob('*') if x.is_file() and x.suffix.lower() in {'.tex','.bib','.cls','.sty','.bst','.pdf','.png','.jpg','.md'}]
files+=list(P.glob('*.md'))+list((P/'scripts').glob('*.py'))+list((P/'outputs').glob('*'))+[P/'original_manifest.json',P/'build_logs/build_audit.json',P/'build_logs/visual_audit.json']
files=sorted(set(files));manifest=[{'path':x.relative_to(PAPER).as_posix(),'sha256':sha(x),'bytes':x.stat().st_size} for x in files]
write(P/'delivery_manifest.json',json.dumps({'files':manifest,'raw_images_predictions_or_checkpoints_included':False},indent=2))
dest=P/'packages';dest.mkdir(exist_ok=True);archive=dest/'PLAN15_BASELINES_PAPERS_AND_EVIDENCE.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for x in files:z.write(x,x.relative_to(PAPER).as_posix())
    z.write(P/'delivery_manifest.json',str((P/'delivery_manifest.json').relative_to(PAPER)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256'] for r in manifest)
bad=[];count=0
for path in [PAPER/'README.md',PAPER/'CVPR/README.md',PAPER/'TMI/README.md']+list(P.glob('*.md')):
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'):continue
        count+=1
        if not (path.parent/target.split('#')[0]).exists():bad.append((str(path),target))
assert not bad,bad
summary={'status':'PASS','local_markdown_links':count,'zip_files':len(manifest)+1,'zip_bytes':archive.stat().st_size,'zip_sha256':sha(archive),'visual_review_pages':sum(r['pages'] for r in visual)}
write(P/'delivery_verification.json',json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
