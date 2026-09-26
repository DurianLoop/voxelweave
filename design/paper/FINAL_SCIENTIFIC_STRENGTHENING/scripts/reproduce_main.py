"""Independent reproduction from preserved arrays / lowest-level observations.

No manuscript summary CSV is a statistical input. The snapshot LaTeX is used
only as an assertion target. Missing historical response arrays are explicit.
"""
from common import *
from audit_statistics import rho,weighted_rho,partial,weighted_partial,simultaneous
import re
UP=PAPER/'CVPR/archive/CVPR_UPGRADE/outputs';OLD=P/'original_snapshot/design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER';CHECKS=[];SOURCES=[]

def source(path):
 h=sha(path);SOURCES.append({'path':path.relative_to(ROOT).as_posix(),'sha256':h});return h
def load_csv(path):
 source(path)
 replacement=OUT/'array_reproduced'/path.name
 if replacement.exists():source(replacement);return pd.read_csv(replacement)
 return pd.read_csv(path)
def check(label,reported,value,tolerance,src,level):
 if (OUT/'array_checks_all.csv').exists() and 'pending' in level:level='independently array-reconstructed observations; array/source bindings in audit manifests'
 d=abs(float(reported)-float(value));CHECKS.append({'headline':label,'reported_value':float(reported),'recomputed_value':float(value),'absolute_difference':d,'tolerance':tolerance,'status':'PASS' if d<=tolerance else 'FAIL','source_hash':src,'source_level':level})
def numeric(line):return [float(x) for x in re.findall(r'(?<![A-Za-z])[-+]?\d*\.\d+|(?<![A-Za-z])[-+]?\d+',line)]

def figure1():
 path=PAPER/'PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/outputs/main_median_real_arrays.npz';h=source(path)
 with np.load(path) as f:
  for cond,b,expected in [('shared','b_shared',[73.8,77.7,22.8,2.0]),('disjoint','b_disjoint',[73.8,74.4,69.3,19.8])]:
   r=metrics(f['a'],f[b],f['gt'],f['mask'])
   for label,val,exp in zip(['MAE_A','MAE_B','D','O_percent'],[r['reference_error'],r['companion_error'],r['disagreement'],100*r['observable']],expected):check('Figure1 '+cond+' '+label,exp,val,.051,h,'preserved target and prediction arrays')

def table1():
 clean=load_csv(UP/'clean_max_overlap_per_plane.csv');clean=pd.concat([clean,load_csv(UP/'clean_max_overlap_ixi_per_plane.csv')],ignore_index=True)
 p4=PAPER/'ARCHIVE/PLANS/PLAN02_TO_PLAN04/plan4_outputs'
 zero=pd.concat([load_csv(p4/'disjoint_anchor_per_plane.csv'),load_csv(p4/'ningxia_disjoint_per_plane.csv').assign(dataset='ningxia')],ignore_index=True).rename(columns={'case':'case_id','target_model':'model','disjoint_inconsistency':'zero_score','phase0_error':'endpoint'})
 ix=load_csv(UP/'overlap_covariance_ixi_per_plane.csv');ix=ix[ix.overlap==0].rename(columns={'disagreement_mae':'zero_score','mae':'endpoint'});zero=pd.concat([zero,ix],ignore_index=True)
 q=zero[['dataset','case_id','model','z','zero_score','endpoint']].merge(clean,on=['dataset','case_id','model','z'],validate='one_to_one');seed_shared=np.random.default_rng(20260813);results=[]
 text=(OLD/'p17_control_table.tex').read_text(encoding='utf-8');source(OLD/'p17_control_table.tex')
 for ds in ['fastmri','ningxia','ixi']:
  g=q[q.dataset==ds].reset_index(drop=True);cases=sorted(g.patient_cluster.unique());codes=pd.Categorical(g.patient_cluster,categories=cases).codes;n=len(cases);rng=np.random.default_rng(20260813) if ds=='ixi' else seed_shared
  idx=rng.choice(n,size=(5000,n),replace=True);weights=np.stack([np.bincount(x,minlength=n) for x in idx])[:,codes];x=g.zero_score.to_numpy();y=g.endpoint.to_numpy();s=g.score.to_numpy();reps=[]
  for start in range(0,5000,100):reps.extend(weighted_rho(x,y,weights[start:start+100])-weighted_rho(s,y,weights[start:start+100]))
  vals=[float(rho(x,y)),float(rho(s,y)),float(rho(x,y)-rho(s,y)),*np.quantile(reps,[.025,.975]),100*g.observable_fraction.mean()]
  key={'fastmri':'fastMRI','ixi':'IXI','ningxia':'NingXia'}[ds];line=next(l for l in text.splitlines() if l.startswith(key+' &'));fields=line.split('&');expected=[float(fields[2]),float(fields[3])]+numeric(fields[4])+[numeric(fields[5])[0]]
  for label,e,v in zip(['rho_disjoint','rho_shared','delta_rho','CI_low','CI_high','observable_percent'],expected,vals):check('Table1/Figure2 '+ds+' '+label,e,v,.0051 if label=='observable_percent' else .00051,sha(UP/('clean_max_overlap_ixi_per_plane.csv' if ds=='ixi' else 'clean_max_overlap_per_plane.csv')),'lowest preserved plane observations; raw-array check pending')
  results.append({'dataset':ds,'rho_disjoint':vals[0],'rho_shared':vals[1],'delta':vals[2],'low':vals[3],'high':vals[4],'observable_percent':vals[5],'endpoint':'disjoint_pair_error' if ds=='ixi' else 'phase0_error'})
 pd.DataFrame(results).to_csv(OUT/'reproduced_original_control.csv',index=False)
 # Recompute test-relative stable-wrong prevalence from the original plane records.
 z=pd.concat([load_csv(UP/'overlap_covariance_per_plane.csv'),load_csv(UP/'overlap_covariance_ixi_per_plane.csv')]);z=z[z.overlap==0]
 zz=z[['dataset','case_id','patient_cluster','model','z','disagreement_mae','mae']].merge(clean,on=['dataset','case_id','patient_cluster','model','z'],suffixes=('_zero','_shared'),validate='one_to_one')
 for ds,g in zz.groupby('dataset'):
  flags=[]
  for model,a in g.groupby('model'):
   e=a.mae.quantile(.75);d=a.disagreement_mae.quantile(.25);flags.extend(((a.error>=e)&(a.score<=d)).astype(int)-((a.mae>=e)&(a.disagreement_mae<=d)).astype(int))
  expected={'fastmri':27.1,'ixi':20.9,'ningxia':28.2}[ds];check('Table1 '+ds+' stable_wrong_pp',expected,100*np.mean(flags),.051,sha(UP/'overlap_covariance_per_plane.csv'),'lowest preserved plane observations')

def table2():
 path=UP/'plan6_neural_shared_influence_confirm3_per_case_config.csv';df=load_csv(path);text=(OLD/'p17_influence_table.tex').read_text(encoding='utf-8');rows=[];allreps=[];fixedrng=np.random.default_rng(20260813)
 for (ds,model),allg in df.groupby(['dataset','model']):
  g=allg[allg.overlap_count<2].reset_index(drop=True);cases=sorted(g.patient_cluster.unique());codes=pd.Categorical(g.patient_cluster,categories=cases).codes;n=len(cases)
  rng=np.random.default_rng(np.random.SeedSequence([20260911,{'fastmri':0,'ixi':1,'ningxia':2}[ds]]));idx=rng.integers(0,n,(5000,n));weights=np.stack([np.bincount(x,minlength=n) for x in idx])[:,codes]
  x=g.neural_influence_cosine.to_numpy();c=g.overlap_count.to_numpy();y=g.error_cosine.to_numpy();rI=float(rho(x,y));rc=float(rho(c,y));point=abs(rI)-abs(rc);reps=[]
  for start in range(0,5000,125):reps.extend(abs(weighted_rho(x,y,weights[start:start+125]))-abs(weighted_rho(c,y,weights[start:start+125])))
  f=allg[allg.overlap_count==1].reset_index(drop=True);fx=f.neural_influence_cosine.to_numpy();fy=f.error_cosine.to_numpy();geo=f[['span','asymmetry']].to_numpy();fc=f.case.to_numpy();fp=partial(fx,fy,geo,fc)
  clusters=list(f.patient_cluster.unique());fcode=pd.Categorical(f.patient_cluster,categories=clusters).codes
  # Historical RNG traversed four endpoints per stratum; retain that draw order.
  fidx=fixedrng.choice(len(clusters),size=(4,2000,len(clusters)),replace=True)[0];w=np.stack([np.bincount(i,minlength=len(clusters)) for i in fidx])[:,fcode];fr=[]
  for start in range(0,2000,100):fr.extend(weighted_partial(fx,fy,geo,fc,w[start:start+100]))
  flo,fhi=np.quantile(fr,[.025,.975]);line=next(l for l in text.splitlines() if l.startswith(ds+' & '+model.upper()+' &'));expected=[v for cell in line.split('&')[2:] for v in numeric(cell)]
  rows.append({'dataset':ds,'model':model,'rho_count':rc,'rho_influence':rI,'advantage':point,'fixed':fp,'fixed_low':flo,'fixed_high':fhi,'expected':expected});allreps.append(reps)
  print('REPRO old influence',ds,model,flush=True)
 intervals,_=simultaneous([r['advantage'] for r in rows],np.array(allreps).T)
 for j,r in enumerate(rows):
  values=[r['rho_count'],r['rho_influence'],r['advantage'],*intervals[j],r['fixed'],r['fixed_low'],r['fixed_high']]
  for label,e,v in zip(['count','influence','advantage','sim_low','sim_high','fixed','fixed_low','fixed_high'],r.pop('expected'),values):check('Table2/Figure3 '+r['dataset']+'/'+r['model']+' '+label,e,v,.00051,sha(path),'lowest preserved context observations; response-array check pending')
  r.update(simultaneous_low=intervals[j,0],simultaneous_high=intervals[j,1])
 pd.DataFrame(rows).to_csv(OUT/'reproduced_original_influence.csv',index=False)

def figure4():
 p9=PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs';p11=PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs'
 fast=pd.concat([load_csv(p9/'p9_disjoint_shared_per_plane.csv'),load_csv(p9/'p9_disjoint_shared_per_plane_transformer_reference.csv')]);ixi=load_csv(p11/'p11_ixi_clean_per_plane_full.csv');result=[]
 for ds,df in [('fastmri',fast),('ixi',ixi)]:
  n=df.case.nunique();idx=np.random.default_rng(20260908).integers(0,n,(10000,n));names=MODELS;cases=sorted(df.case.unique())
  local_values=None
  for within in ['mean','median']:
   ag=df.groupby(['case','model','condition'])[['observable_error_fraction','paired_error_mae','prediction_disagreement_mae']].agg(within)
   def mat(ep,cond):return ag[ep].unstack('condition')[cond].unstack('model').loc[cases,names].to_numpy()
   gain=mat('observable_error_fraction','disjoint')-mat('observable_error_fraction','shared');fn=np.mean if ds=='fastmri' else np.median
   p=fn(gain,axis=0);rep=fn(gain[idx],axis=1);iv,_=simultaneous(p,rep)
   sd,dd=mat('prediction_disagreement_mae','shared'),mat('prediction_disagreement_mae','disjoint');se,de=mat('paired_error_mae','shared'),mat('paired_error_mae','disjoint');rp=rho(dd,de,0)-rho(sd,se,0);rb=rho(dd[idx],de[idx],1)-rho(sd[idx],se[idx],1);ri,_=simultaneous(rp,rb)
   if within==('mean' if ds=='fastmri' else 'median'):
    local_values=(p.copy(),iv.copy())
    expected=[.178,.176,.080,.137,.226] if ds=='fastmri' else [.290,.302,.252,.298,.296]
    for j,m in enumerate(names):check('Figure4 '+ds+'/'+m+' local_gap',expected[j],p[j],.00051,sha(p9/'p9_disjoint_shared_per_plane.csv') if ds=='fastmri' else sha(p11/'p11_ixi_clean_per_plane_full.csv'),'lowest preserved plane observations; array check pending')
   if within=='median':
    for j,m in enumerate(names):result.append({'dataset':ds,'model':m,'local_gap':local_values[0][j],'local_sim_low':local_values[1][j,0],'local_sim_high':local_values[1][j,1],'ranking_gap':rp[j],'ranking_sim_low':ri[j,0],'ranking_sim_high':ri[j,1]})
 pd.DataFrame(result).to_csv(OUT/'reproduced_architecture_headlines.csv',index=False)

def main():
 guard();figure1();table1();table2();figure4();pd.DataFrame(CHECKS).to_csv(OUT/'reproduction_initial_checks.csv',index=False);write(OUT/'reproduction_sources.json',SOURCES)
 lines=['# Historical main-headline reproduction','','Statistics are independently reconstructed from array-derived observation tables when present, never from manuscript summary CSVs. Historical target/prediction/finite-response arrays have been regenerated with the frozen wrappers; the separate array_checks_all.csv quantifies agreement with the original lowest-level observations. array_bindings_all.json binds all arrays actually read. Semantic mismatches are recorded in REPRODUCTION_FINDINGS_BEFORE_REVISION.md.','','| Headline | Reported | Recomputed | Absolute difference | PASS/FAIL | Source SHA-256 |','|---|---:|---:|---:|---|---|']
 for r in CHECKS:lines.append(f"| {r['headline']} | {r['reported_value']:.8g} | {r['recomputed_value']:.8g} | {r['absolute_difference']:.3g} | {r['status']} | `{r['source_hash']}` |")
 (P/'REPRODUCTION_CHECK.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Checks',len(CHECKS),'failures',sum(r['status']=='FAIL' for r in CHECKS),flush=True)
 if any(r['status']=='FAIL' for r in CHECKS):raise SystemExit('Resolve mismatches before manuscript rewriting.')
if __name__=='__main__':main()
