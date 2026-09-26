"""Read-only provenance census; preserve manuscripts before the next iteration."""
from pathlib import Path
import os,json,hashlib,shutil,datetime,re,subprocess,collections
import pandas as pd
P=Path(__file__).resolve().parents[1];PAPER=P.parent;ROOT=PAPER.parents[1]
OUT=P/'outputs';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
def utc(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
if not (P/'original_manifest.json').exists():
    files=[ROOT/'README.md',PAPER/'README.md',PAPER/'CVPR/README.md',PAPER/'TMI/README.md']
    files += list((PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER').rglob('*'))
    files += list((PAPER/'TMI/TMI_ARCH_GENERALIZED').rglob('*'))
    records=[]
    for f in files:
        if not f.is_file():continue
        dst=P/'original_snapshot'/f.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst)
        records.append({'path':rel(f),'sha256':sha(f)})
    save(P/'original_manifest.json',{'created_utc':utc(datetime.datetime.now().timestamp()),'files':records})

skip={'original_snapshot','.git','__pycache__','delivery','page_renders','final_page_renders','final_page_renders_verified','build_logs','node_modules'}
sources=[];csvs=[];rules=[];json_records=[];attempts=[]
categories={'split':r'split|train.*val|held.out','checkpoint':r'checkpoint|epoch_best|weights',
 'metric':r'Spearman|Kendall|PSNR|SSIM|MAE|RMSE|AURC|AUROC|AUPRC|error_cosine|observable_error_fraction',
 'mask':r'mask|foreground|support', 'context':r'context|anchors|phase.?0|phase.?2|offset',
 'perturbation':r'Rademacher|epsilon|amplitude|perturb|610[1-4]', 'stability':r'stability|\.90|0\.90|gate',
 'eligibility':r'exclud|includ|eligible|smoke|pilot|failure|not.retained',
 'normalization':r'normaliz|min.?max|quantiz|roundtrip|scale.contract',
 'bootstrap':r'bootstrap|resampl|simultaneous|cluster|seed',
 'chronology':r'prespec|prereg|prospectively|frozen|post.hoc|exploratory|before|after.inspect'}
for directory,dirs,files in os.walk(PAPER):
    dirs[:]=[d for d in dirs if d not in skip and not d.startswith('PLAN17')]
    for name in sorted(files):
        f=Path(directory)/name;ext=f.suffix.lower()
        if ext not in {'.py','.md','.json','.csv','.tex','.txt','.yaml','.yml'}:continue
        st=f.stat();record={'path':rel(f),'bytes':st.st_size,'mtime_utc':utc(st.st_mtime),'sha256':sha(f)}
        sources.append(record)
        if ext=='.csv':
            try:
                df=pd.read_csv(f,low_memory=False)
                csvs.append({**record,'rows':len(df),'columns':list(df.columns),'models':sorted(df.model.dropna().astype(str).unique()) if 'model' in df else [],'datasets':sorted(df.dataset.dropna().astype(str).unique()) if 'dataset' in df else [],'status':'technical_or_excluded' if re.search(r'smoke|debug|pilot|failure',name,re.I) else 'retained_or_unclassified'})
            except Exception as e:csvs.append({**record,'parse_error':str(e)})
        elif ext=='.json' and st.st_size<2000000:
            try:json_records.append({'path':rel(f),'payload':json.loads(f.read_text(encoding='utf-8-sig'))})
            except Exception:pass
        if ext in {'.py','.md','.tex','.txt','.yaml','.yml'} and st.st_size<1000000:
            for i,line in enumerate(f.read_text(encoding='utf-8-sig',errors='replace').splitlines(),1):
                tags=[k for k,v in categories.items() if re.search(v,line,re.I)]
                if tags:rules.append({'path':rel(f),'line':i,'categories':tags,'text':line})
        if re.search(r'smoke|debug|pilot|failure|amend|addendum|selection|ablat',name,re.I):attempts.append(record)
save(OUT/'source_inventory.json',sources);save(OUT/'historical_csv_inventory.json',csvs)
save(OUT/'rule_evidence.json',rules);save(OUT/'manifest_payloads.json',json_records)

splits=[];checkpoints=[];configs=[]
for top in ['dataset','baseline','pre','design']:
 for directory,dirs,files in os.walk(ROOT/top):
    dirs[:]=[d for d in dirs if d not in skip and d!='paper']
    for name in files:
        f=Path(directory)/name;ext=f.suffix.lower()
        if ext in {'.pth','.pt','.ckpt'}:
            st=f.stat();checkpoints.append({'path':rel(f),'bytes':st.st_size,'mtime_utc':utc(st.st_mtime),'role':'available_candidate; usage requires matching manifest/code'})
        elif ext in {'.txt','.json','.csv'} and 'split' in str(f).lower() and f.stat().st_size<1000000:
            t=f.read_text(encoding='utf-8-sig',errors='replace');splits.append({'path':rel(f),'sha256':sha(f),'contents':t})
        elif name in {'run_manifest.json','config.json','config.yaml','config.yml'} and f.stat().st_size<500000:
            configs.append({'path':rel(f),'sha256':sha(f),'contents':f.read_text(encoding='utf-8-sig',errors='replace')})
save(OUT/'split_inventory.json',splits);save(OUT/'checkpoint_inventory.json',checkpoints);save(OUT/'training_configs.json',configs)

# Directly re-check split membership; distinct examination IDs are not proof of
# cross-dataset patient uniqueness in the absence of a patient linkage file.
split_checks={}
for name,folder,patient in [('fastmri',ROOT/'dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407',lambda x:x.split('_')[0]),('ixi',ROOT/'dataset/IXI/splits/seed3407',lambda x:x.split('-')[0])]:
    sets={s:set((folder/f'{s}_cases.txt').read_text().split()) for s in ['train','val','test']}
    ps={s:{patient(x) for x in a} for s,a in sets.items()}
    split_checks[name]={'series':{s:len(a) for s,a in sets.items()},'patients':{s:len(a) for s,a in ps.items()},'overlaps':{a+'_'+b:sorted(ps[a]&ps[b]) for a,b in [('train','val'),('train','test'),('val','test')]},'files':[{ 'path':rel(folder/f'{s}_cases.txt'),'sha256':sha(folder/f'{s}_cases.txt')} for s in sets]}
history=subprocess.run(['git','--no-pager','log','--format=%H %aI %s','--','design/paper'],cwd=ROOT,capture_output=True,text=True).stdout
write_history=OUT/'git_history.txt';write_history.write_text(history,encoding='utf-8')
terms=[]
for f in (PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER').glob('*.tex'):
    for i,line in enumerate(f.read_text(encoding='utf-8').splitlines(),1):
        if re.search(r'prospectively frozen|prespecified|rule.frozen|held.out|independent.{0,20}replic|preregister|before.*result',line,re.I):
            terms.append({'path':rel(f),'line':i,'text':line,'decision':'remove prospective/prespecified/rule-frozen; held-out only from estimator fitting; independent refers to distinct cohort, not untouched analysis'})
save(OUT/'manuscript_provenance_phrases.json',terms)
ledger={'schema_version':'1.0','audit_utc':utc(datetime.datetime.now().timestamp()),'scope':'CVPR manuscript, all discoverable paper historical text/code/CSV/JSON evidence plus workspace split/config/checkpoint census. Not a rerun of all historical models. Missing causal chronology is explicit.',
 'source_inventory':'outputs/source_inventory.json','all_csvs':'outputs/historical_csv_inventory.json','every_extracted_rule':'outputs/rule_evidence.json','manifest_payloads':'outputs/manifest_payloads.json','every_available_checkpoint':'outputs/checkpoint_inventory.json','dataset_splits':'outputs/split_inventory.json','training_configs':'outputs/training_configs.json',
 'counts':{'scientific_source_files':len(sources),'csvs':len(csvs),'rule_lines':len(rules),'split_files':len(splits),'checkpoint_candidates':len(checkpoints),'training_configs':len(configs)},'split_checks':split_checks,'attempted_or_amended_artifacts':attempts,
 'chronology_evidence':{'git_history':history,'filesystem_mtime_status':'mutable/copy-sensitive; cannot alone establish preregistration','protocol_self_report_status':'documents assert prior freezing but independent proof not recovered','events':[{'order':1,'stage':'Plans 2-8','status':'iterative retrospective mechanism/metric/context exploration; same test cohorts repeatedly inspected'},{'order':2,'stage':'Plan9','date_claimed':'2026-08-14','status':'one repository snapshot includes both protocol and results; reverse-control smoke changed after observing its outcome; not independent proof of pre-outcome freezing'},{'order':3,'stage':'Plan10','status':'explicit post-hoc full-bank audit'},{'order':4,'stage':'Plan11-12','date_claimed':'2026-08-27 through 2026-09-06','status':'IXI full expansion; overlaps prior IXI influence subset; independent cohort from fastMRI, not pristine analysis holdout'},{'order':5,'stage':'Plan13','date_claimed':'2026-09-08','status':'post-hoc aggregation/multiplicity/current-error sensitivity'},{'order':6,'stage':'Plan14','date_claimed':'2026-09-09','status':'TopCoW bright-mask proposed after general-mask results; CAS transfer after TopCoW; not hidden challenge test'},{'order':7,'stage':'Plan15-16','date_claimed':'2026-09-10','status':'baseline recovery then generated schematic replacement'},{'order':8,'stage':'Plan17','status':'current audit before new experiment evaluation; historical tests remain reused'}]},
 'provenance_phrase_audit':terms,
 'critical_findings':['One fastMRI patient crosses train/validation; no train/test or validation/test ID overlap.','Plan9/11 disagreement evaluated inside GT mask; probe normalization uses full examination including targets. Not target-free.','Plan9 stable-wrong thresholds estimated on reported test planes; Plan8 uses different thresholds. Descriptive test-relative prevalence, not externally validated detection.','Historical primary endpoint shifted from ranking (Plan9) toward local observability (Plan11 onward). New main story is retrospective; local gain is not a newly preregistered primary success.','42-stratum HAT/SwinIR stability and new-model .90 gate are audited stability descriptions; no independent proof all gates were chosen before any outcomes.','Plane-level repeated measures require examination/patient bootstrap, family counts do not add patient sample size.','CAS/TopCoW results and all historical cohorts have already been inspected; no truly untouched inference cohort established.','OAI-prepared is label-like, MRNet independent patient linkage missing; do not force external validation with these resources.'],
 'completion':'discovery and substantive audit complete for available evidence; complete historical order and every unlogged attempt are not recoverable and must not be invented'}
save(P/'research_ledger.json',ledger)
print(json.dumps({'counts':ledger['counts'],'split_checks':split_checks,'history':history},ensure_ascii=False,indent=2))
