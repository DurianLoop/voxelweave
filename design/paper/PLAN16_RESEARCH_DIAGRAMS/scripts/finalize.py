from pathlib import Path
import hashlib,json,re,difflib

P=Path(__file__).resolve().parents[1]; PAPER=P.parent
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'; TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def original(p): return (P/'original_snapshot'/p.relative_to(PAPER)).read_text(encoding='utf-8')
def write(p,s): p.write_text(s,encoding='utf-8')

t=original(PAPER/'README.md')
t=t.replace('当前科学版本：', '当前图稿版本：**Plan 16，2026-09-10**。两稿第 2 页图 1 已用内置图像生成工具重绘并替换，原稿受快照保护。[图稿中文报告、提示词与原图](PLAN16_RESEARCH_DIAGRAMS/FINAL_REPORT_ZH.md)。\n\n当前科学证据版本：',1)
t=t.replace('10 页；第 7 页 Table VI 完整 baseline，第 6 页预算分析','11 页；第 2 页新框架图，第 8 页 Table VI 完整 baseline，第 6 页预算分析')
t=t.replace('本轮核验 111','Plan 15 核验 111').replace('本轮 149 文件快照','Plan 15 的 149 文件快照')
write(PAPER/'README.md',t)
for name,folder in [('CVPR',CV),('TMI',TMI)]:
    p=PAPER/name/'README.md';t=original(p)
    t=t.replace('\n\n','\n\n图稿更新 Plan 16：第 2 页图 1 已重绘并替换。[图稿报告与提示词](../PLAN16_RESEARCH_DIAGRAMS/FINAL_REPORT_ZH.md)。'+('主稿 9 页，技术正文仍为 8 页。' if name=='CVPR' else '跨栏图提高可读性，主稿现为 11 页。')+'\n\n',1)
    write(p,t)
    rel='../../../' if name=='CVPR' else '../../'
    audit=f'''# {name} Plan 16 当前构建审计

2026-09-10：第 2 页图 1 已替换为内置 image_gen.imagegen 生成的科研框架示意图。工具没有型号选择参数，不能确认后端为用户指定的 image2.5。原图与改前文稿保存在 Plan16/original_snapshot；既有结果图、表格与补充 PDF 保持原字节。

CVPR 主文 9 页、技术内容止于第 8 页；TMI 主文 11 页。两稿 pdflatex → bibtex → pdflatex ×2 成功，无 LaTeX Error、未定义引用和 overfull 警告。20 页已渲染并检查，两张图另行整页核对。TMI 新图跨栏带来一页篇幅增长。

详见 [本轮图稿报告]({rel}PLAN16_RESEARCH_DIAGRAMS/FINAL_REPORT_ZH.md)、[构建日志]({rel}PLAN16_RESEARCH_DIAGRAMS/build_logs/build_audit.json)、[文件保护核验]({rel}PLAN16_RESEARCH_DIAGRAMS/verification.json)。科学证据仍以 [Plan 15]({rel}PLAN15_BASELINE_INTEGRATION/FINAL_REPORT_ZH.md) 为准；本轮不新增实验或消除既有科学风险。
'''
    write(folder/'FINAL_BUILD_AUDIT.md',audit)

manifest=json.loads((P/'original_manifest.json').read_text())['files']
snapshot_fail=[];changes=[];missing=[];unchanged_figures=0
allowed_suffix={'.tex','.pdf','.aux','.log','.bbl','.blg','.out','.brf'}
for row in manifest:
    rel=row['path']; saved=P/'original_snapshot'/rel; current=PAPER/rel
    if not saved.exists() or sha(saved)!=row['sha256']: snapshot_fail.append(rel)
    if not current.exists():missing.append(rel);continue
    if sha(current)!=row['sha256']:changes.append(rel)
    elif '/figures/' in rel:unchanged_figures+=1
unexpected=[]
for rel in changes:
    q=Path(rel)
    allowed=(q.name in {'README.md','FINAL_BUILD_AUDIT.md'} or (q.stem=='main' and q.suffix in allowed_suffix))
    if not allowed:unexpected.append(rel)

def normalize(t,name):
    label='mechanism' if name=='cvpr' else 'concept'
    pattern=r'\\begin\{figure\*?\}\[t\].*?\\label\{fig:'+label+r'\}.*?\\end\{figure\*?\}'
    t,n=re.subn(pattern,'',t,count=1,flags=re.S); assert n==1
    if name=='cvpr':
        t,n=re.subn(r'(\\section\{Conclusion\}).*?(?=\\clearpage)',r'\1',t,count=1,flags=re.S);assert n==1
    else:
        t=re.sub(r'Figure~\\ref\{fig:concept\} summarizes .*?\.', 'FIGURE_OVERVIEW.',t,count=1)
    return re.sub(r'\s+',' ',t).strip()
body_checks={}
for name,folder in [('cvpr',CV),('tmi',TMI)]:
    old=original(folder/'main.tex');new=(folder/'main.tex').read_text(encoding='utf-8')
    body_checks[name]=normalize(old,name)==normalize(new,name)
    write(P/(name+'_source_changes.diff'),''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='Plan15/main.tex',tofile='Plan16/main.tex')))
supp_checks={str(p.relative_to(PAPER)):sha(p)==sha(P/'original_snapshot'/p.relative_to(PAPER)) for p in [CV/'supplement.pdf',TMI/'baseline_supplement.pdf']}
asset_checks=[]
for row in json.loads((P/'generation_manifest.json').read_text())['assets']:
    asset_checks.append(sha(PAPER/row['project_path'])==sha(PAPER/row['paper_path'])==row['sha256'])
build=json.loads((P/'build_logs/build_audit.json').read_text())
cv_pages=(P/'build_logs/cvpr_text.txt').read_text(encoding='utf-8').split('\f')
cv_body8='validation remain necessary.' in cv_pages[7] and 'References' in cv_pages[8]
audit={'snapshot_files':len(manifest),'snapshot_hash_failures':snapshot_fail,'deleted_original_files':missing,'changed_original_files':changes,'unexpected_changes':unexpected,'unchanged_existing_figure_assets':unchanged_figures,'body_identical_outside_declared_figure_and_caption_and_cvpr_conclusion_edits':body_checks,'supplement_pdf_byte_identical':supp_checks,'selected_pngs_byte_identical':asset_checks,'cvpr_technical_text_ends_on_page_8':cv_body8,'builds':build,'final_pdf_sha256':{n:sha(f/'main.pdf') for n,f in [('cvpr',CV),('tmi',TMI)]},'visual_review':{'pages':20,'figure_pages':{'cvpr':2,'tmi':2},'contact_sheets_and_full_figure_pages_viewed':True,'obstruction_or_clipping_observed':False}}
assert not snapshot_fail and not missing and not unexpected,audit
assert all(body_checks.values()) and all(supp_checks.values()) and all(asset_checks) and cv_body8,audit
write(P/'verification.json',json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,ensure_ascii=False,indent=2))
