"""Recover every master-table row from original full-run metric summaries."""
from pathlib import Path
from html.parser import HTMLParser
import os,re,json,hashlib,shutil
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parents[1]; PAPER=P.parent; ROOT=PAPER.parents[1];OUT=P/'outputs';OUT.mkdir(exist_ok=True)
MET=['psnr','ssim','mae','mse','ncc']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
master=ROOT/'docx/experiment/experiment_master_table.md'
if not (P/'original_manifest.json').exists():
    paths=[PAPER/'README.md',PAPER/'CVPR/README.md',PAPER/'TMI/README.md']
    for d in [PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER',PAPER/'TMI/TMI_ARCH_GENERALIZED']:
        paths += [x for x in d.rglob('*') if x.is_file()]
    records=[]
    for x in paths:
        rel=x.relative_to(PAPER);dst=P/'original_snapshot'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(x,dst)
        records.append({'path':rel.as_posix(),'sha256':sha(x)})
    (P/'original_manifest.json').write_text(json.dumps({'files':records},indent=2))
    shutil.copy2(master,P/'master_table_original.md')

def method(s):
    for key,name in [('res-srdiff','ressrdiff'),('resunet','resunet'),('smamba','smamba_unet'),('pix2pix','gan_2p5d'),('cycleinr','cycleinr'),('linear','linear'),('cubic','cubic'),('acvtt','acvtt'),('arssr','arssr'),('swinir','swinir'),('saint','saint'),('i3net','i3net'),('hat','hat')]:
        if key in s.lower():return name
    return None
class Table(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=[];self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        if tag=='td':self.cell=''
    def handle_data(self,data):
        if self.cell is not None:self.cell+=data
    def handle_endtag(self,tag):
        if tag=='td':self.row.append(self.cell.strip());self.cell=None
        if tag=='tr' and self.row:self.rows.append(self.row)
t=master.read_text(encoding='utf-8');parser=Table();parser.feed(t);wanted=[]
for row in parser.rows:
    if row[0]=='x4':row=row[1:]
    assert len(row)==16
    for j,ds in enumerate(['IXI','fastMRI','NingXia']):
        wanted.append(dict(dataset=ds,model=method(row[0]),scale=4,budget='master',**dict(zip(MET,map(float,row[1+5*j:6+5*j])))))
section='';ds=None;budget='master'
for line in t.splitlines():
    if line.startswith('##'):
        section=line
        if 'NingXia' in line:ds='NingXia'
        elif 'fastMRI' in line:ds='fastMRI'
        else:ds=None
        budget='90epoch' if '90-Epoch' in line else ('60epoch' if '60-Epoch' in line else 'master')
    if re.match(r'\| x[246] \|',line):
        cols=[x.strip() for x in line.strip('|').split('|')]
        if ds and len(cols)==7:
            wanted.append(dict(dataset=ds,model=method(cols[1]),scale=int(cols[0][1:]),budget=budget,**dict(zip(MET,map(float,cols[2:])))))
w=pd.DataFrame(wanted);assert w.model.notna().all();assert not w.duplicated(['dataset','model','scale','budget']).any();w.to_csv(OUT/'master_rows.csv',index=False)
raw=[];sources=[]
def source_walk():
    yield from os.walk(ROOT/'baseline')
    yield from os.walk(ROOT/'pre/ixi_diffusion')
for d,dirs,files in source_walk():
    dirs[:]=[x for x in dirs if x not in {'predictions','checkpoints','__pycache__','.git','visualizations'}]
    if 'summary_metrics.csv' not in files:continue
    p=Path(d)/'summary_metrics.csv';parts=p.relative_to(ROOT).parts; package=parts[1]
    ds='IXI' if package.startswith('ixi_') else 'fastMRI' if package.startswith('fastmri_') else 'NingXia' if package.startswith('ningxia_') else None
    profile=p.parents[1].name
    if not ds or not (profile.startswith('full') or profile in {'saint_full_t2_test115','resunet_full_t2_test115'}):continue
    fold=next((x for x in parts if re.fullmatch(r'fold_\d+',x)),None)
    if ds=='NingXia' and not fold:continue
    data=pd.read_csv(p)
    if not all(x+'_mean' in data for x in MET):continue
    path=p.relative_to(ROOT).as_posix(); sources.append({'path':path,'sha256':sha(p)})
    for _,r in data.iterrows():
        m=str(r['method']);m={'smamba':'smamba_unet','gan':'gan_2p5d','saint_residual':'saint'}.get(m,m)
        raw.append(dict(dataset=ds,model=m,scale=2 if '_x2' in profile else 6 if '_x6' in profile else 4,package=package,profile=profile,fold=fold or '',cases=int(r['cases']),path=path,**{x:float(r[x+'_mean']) for x in MET}))
r=pd.DataFrame(raw);r.to_csv(OUT/'all_full_summary_rows.csv',index=False)
groups=[]
for key,g in r.groupby(['dataset','model','scale','package','profile']):
    ds,m,s,pack,prof=key
    if ds=='NingXia':
        if set(g.fold)!=set(f'fold_{i:02}' for i in range(8)) or len(g)!=8:continue
    elif len(g)!=1 or g.cases.iloc[0] != (115 if ds=='IXI' else 24):continue
    groups.append(dict(dataset=ds,model=m,scale=s,package=pack,profile=prof,units=8 if ds=='NingXia' else int(g.cases.iloc[0]),paths=g.path.tolist(),**{x:g[x].mean() for x in MET}))
c=pd.DataFrame(groups); matches=[];out=[]
for idx,row in w.iterrows():
    candidates=c[(c.dataset==row.dataset)&(c.model==row.model)&(c.scale==row.scale)].copy()
    if row.budget=='60epoch':candidates=candidates[candidates.profile.str.contains('60')]
    elif row.budget=='90epoch':candidates=candidates[candidates.profile.str.contains('90')]
    else:
        # The master explicitly uses fastMRI HAT x4 full_extend60 as its baseline.
        if not (row.dataset=='fastMRI' and row.model=='hat' and row.scale==4):candidates=candidates[~candidates.profile.str.contains('extend60|extend90')]
    errors=abs(candidates[MET]-row[MET].to_numpy(dtype=float)).max(axis=1)
    best=candidates.loc[errors.idxmin()] if len(errors) else None
    good=candidates.loc[errors<=.000051]
    rec=row.to_dict();rec['row_id']=int(idx);rec['status']='MATCH' if len(good) else 'UNMATCHED';rec['max_rounding_difference']=float(errors.min()) if len(errors) else None
    rec['candidate_count']=len(good)
    if best is not None:
        rec.update(package=best.package,profile=best.profile,units=int(best.units),source_paths=json.dumps(best.paths))
        for m in MET:rec['source_'+m]=float(best[m])
    out.append(rec)
    for _,g in good.iterrows():matches.append({'row_id':int(idx),'package':g.package,'profile':g.profile,'paths':g.paths})
a=pd.DataFrame(out);a.to_csv(OUT/'master_provenance_audit.csv',index=False)
(OUT/'source_manifest.json').write_text(json.dumps({'master':{'path':str(master.relative_to(ROOT)),'sha256':sha(master)},'summary_files':sources,'all_exact_matches':matches},indent=2))
print(a.groupby(['dataset','budget','status']).size().to_string());print('Unmatched:',a.loc[a.status!='MATCH',['dataset','model','scale','budget','max_rounding_difference','profile']].to_string(index=False))
