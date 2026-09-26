"""Final numerical/text assertions; all numerical inputs derive from preserved arrays."""
from pathlib import Path
import re,json,hashlib,datetime
import numpy as np,pandas as pd
from scipy.stats import spearmanr
P=Path(__file__).resolve().parents[1];CV=P/'revised_manuscript';OUT=P/'outputs';R=OUT/'array_reproduced';checks=[]
def check(label,actual,expected,atol=1e-10):
 ok=bool(np.isclose(actual,expected,atol=atol,rtol=0,equal_nan=True));checks.append(dict(check=label,reported=actual,recomputed=expected,tolerance=atol,status='PASS' if ok else 'FAIL'))
def nums(s):return [float(x) for x in re.findall(r'(?<![A-Za-z0-9])[-+]?\d*\.\d+',s.replace('--',' to '))]
def main():
 text=(CV/'main.tex').read_text(encoding='utf-8');abstract=text.split('\\begin{abstract}')[1].split('\\end{abstract}')[0]
 c=pd.read_csv(R/'cross_arch_shared_disjoint_intervals.csv');acq=pd.read_csv(R/'acquired_only_summary.csv');st=pd.read_csv(R/'acquired_only_stability.csv');pr=pd.read_csv(R/'proposition1_neural_validation.csv');prop=pd.read_csv(R/'proposition_summary.csv');local=pd.read_csv(OUT/'revised_local_control.csv')
 for ds,limits in [('fastmri',[6.2,16.0]),('ixi',[13.1,28.5])]:
  q=c[(c.dataset==ds)&(c.endpoint=='observable_gap')];check('Abstract/Fig4 '+ds+' pairs',20,len(q),0);check('Abstract/Fig4 '+ds+' positive CI',20,(q.simultaneous_low>0).sum(),0)
  for name,x,y in [('min',limits[0],100*q.delta.min()),('max',limits[1],100*q.delta.max())]:check('Main local range '+ds+' '+name,x,y,.051)
  rank=c[(c.dataset==ds)&(c.endpoint=='fixed_reference_ranking')];check('Main fixed-reference ranking '+ds,0 if ds=='fastmri' else 16,(rank.simultaneous_low>0).sum(),0)
 check('Abstract quantitative statements <=2',int(len(re.findall(r'\d+(?:\.\d+)?',abstract))<=2),1,0)
 check('Abstract preserves retrospective boundary',int('retrospectively' in abstract),1,0)
 check('Abstract preserves noncalibrated boundary',int('does not provide a calibrated correctness score' in abstract),1,0)
 tab=(CV/'local_control_table.tex').read_text(encoding='utf-8')
 for r in local.itertuples():
  name={'fastmri':'fastMRI','ixi':'IXI','ningxia':'NingXia'}[r.dataset];line=next(x for x in tab.splitlines() if x.startswith(name+' &'));values=nums(line);expected=[r.shared_O*100,r.disjoint_O*100,r.delta_O*100,r.delta_O_low*100,r.delta_O_high*100]
  for j,(a,b) in enumerate(zip(values,expected)):check('Table1/Fig2 '+r.dataset+' field'+str(j),a,b,.0051)
  check('Table1 '+r.dataset+' field count',len(values),5,0);check('Table1 units '+r.dataset,int(line.split('&')[1]),r.units,0)
 table=(CV/'final_acquired_table.tex').read_text(encoding='utf-8');oldtable=(P/'original_snapshot/manuscript/final_acquired_table.tex').read_text(encoding='utf-8')
 for ds in ['ixi','fastmri']:
  for m in ['hat','swinir']:
   name='IXI' if ds=='ixi' else 'fastMRI';model='HAT' if m=='hat' else 'SwinIR';line=next(x for x in table.splitlines() if x.startswith(name+' & '+model+' &'));oldline=next(x for x in oldtable.splitlines() if x.startswith(name+' & '+model+' &'));q=acq[(acq.dataset==ds)&(acq.model==m)].set_index('endpoint');b=q.loc['beyond_count'];f=q.loc['fixed_count'];v=st[(st.dataset==ds)&(st.model==m)].rank_stability.min();expected=[b.estimate,b.simultaneous_low,b.simultaneous_high,f.estimate,f.simultaneous_low,f.simultaneous_high,v]
   check('Table2 accepted row unchanged '+ds+'/'+m,int(nums(line)==nums(oldline)),1,0)
   for j,(x,y) in enumerate(zip(nums(line),expected)):check('Table2/Fig3 '+ds+'/'+m+' field'+str(j),x,y,.00051)
 check('Main/Fig3 worst individual relative error',126.4,100*pr.approx_relative_error.max(),.051)
 check('Main/Fig3 min median relative error',1.9,100*prop.median_relative_error.min(),.051);check('Main/Fig3 max median relative error',10.6,100*prop.median_relative_error.max(),.051)
 check('Main/Fig3 all eight signed intervals negative',8,(prop.simultaneous_high<0).sum(),0)
 check('Main/Fig3 minimum stability',.880,st.rank_stability.min(),.00051)
 cards=pd.read_csv(P/'MIRA_MAIN_REPORT_CARD.csv');cardtex=(CV/'mira_report_card_table.tex').read_text(encoding='utf-8');check('MIRA main card row count',7,len(cards),0)
 for ds in ['fastmri','ixi']:
  row=cards[(cards.cohort==ds)&(cards.design=='cross-architecture')].iloc[0];q=c[c.dataset==ds];o=q[q.endpoint=='observable_gap'];rk=q[q.endpoint=='fixed_reference_ranking']
  for field,x,y in [('O min',row.local_low,o.delta.min()),('O max',row.local_high,o.delta.max()),('ranking min',row.ranking_low,rk.delta.min()),('ranking max',row.ranking_high,rk.delta.max())]:check('MIRA '+ds+' '+field,x,y)
  name='fastMRI' if ds=='fastmri' else 'IXI';line=next(x for x in cardtex.splitlines() if x.startswith('Cross-arch. & '+name));vals=nums(line)
  for j,(x,y,tol) in enumerate(zip(vals,[100*o.delta.min(),100*o.delta.max(),rk.delta.min(),rk.delta.max()],[.051,.051,.00051,.00051])):check('MIRA LaTeX '+ds+' field'+str(j),x,y,tol)
 # A double hyphen denotes a range, not a negative sign on the upper endpoint.
 for r in cards[cards.design.str.startswith('acquired-only')].itertuples():
  m=r.design.split()[-1];q=acq[(acq.dataset==r.cohort)&(acq.model==m)].set_index('endpoint');check('MIRA influence '+r.cohort+'/'+m,r.beyond_count,q.loc['beyond_count'].estimate);check('MIRA fixed '+r.cohort+'/'+m,r.fixed_count,q.loc['fixed_count'].estimate)
 for r in cards.itertuples():
  if r.design!='cross-architecture':check('MIRA absent phase endpoints '+r.design+'/'+r.cohort,int(pd.isna(r.local_low) and pd.isna(r.ranking_low)),1,0)
  if not r.design.startswith('acquired-only'):check('MIRA absent influence endpoints '+r.design+'/'+r.cohort,int(pd.isna(r.beyond_count) and pd.isna(r.fixed_count)),1,0)
 old=pd.read_csv(P/'original_snapshot/accepted_evidence/mira_report_cards.csv');new=pd.read_csv(P/'mira_report_cards.csv');check('Detailed MIRA row count',len(new),len(old),0)
 for col in old.select_dtypes(include='number').columns:check('Detailed MIRA '+col,float(np.nanmax(abs(old[col].to_numpy()-new[col].to_numpy()))),0,1e-9)
 support=pd.read_csv(P/'CROSS_ARCH_SUPPORT_SENSITIVITY.csv');geo=pd.read_csv(P/'CROSS_ARCH_GEOMETRY_SENSITIVITY.csv');family=pd.read_csv(P/'CROSS_ARCH_FAMILY_ROBUSTNESS.csv')
 for (ds,analysis),q in support[support.pair!='equal_weight_family'].groupby(['dataset','analysis']):check('Support positive simultaneous '+ds+'/'+analysis,20,(q.simultaneous_low>0).sum(),0)
 for ds,count in [('fastmri',8),('ixi',6)]:
  q=geo[(geo.dataset==ds)&(geo.pair!='equal_weight_family')];mirror=q[q.analysis=='mirror_residue1_minus_residue3'];check('Main orientation warning '+ds,count,((mirror.simultaneous_low>0)|(mirror.simultaneous_high<0)).sum(),0)
  for analysis in ['residue_1','residue_3','residue_balanced','nearest_distance_matched_balanced']:check('Geometry positive simultaneous '+ds+'/'+analysis,20,(q[q.analysis==analysis].simultaneous_low>0).sum(),0)
 check('FastMRI four-anchor geometry NA',20,len(geo[(geo.dataset=='fastmri')&(geo.analysis=='full_four_anchor_balanced')&(geo.pair!='equal_weight_family')].query('units==0')),0)
 check('All family descriptive lower intervals positive',len(family),(family.low>0).sum(),0)
 # Figure 1 annotations derive from freshly read qualitative arrays in paper_assets.
 fig=json.loads((OUT/'figure1_annotation_manifest.json').read_text());check('Fig1 physical target z',fig['target_z'],9,0)
 for i,expected in enumerate([[73.8,77.7,22.8,2.0],[73.8,74.4,69.3,19.8]]):
  r=fig['values'][i]
  for key,x,y in zip(['reference_error','companion_error','disagreement','O_percent'],expected,[r['reference_error'],r['companion_error'],r['disagreement'],r['observable']*100]):check('Fig1 condition'+str(i)+' '+key,x,y,.051)
 # Public-facing source closure, excluding the final reproducibility section.
 visited=set()
 def visit(path):
  if path in visited:return ''
  visited.add(path);s=path.read_text(encoding='utf-8')
  for child in re.findall(r'\\input\{([^}]+)\}',s):
   pp=CV/(child if child.endswith('.tex') else child+'.tex')
   if pp.name!='final_supp_7.tex' and pp.exists():s+='\n'+visit(pp)
  return s
 visible=visit(CV/'supplement.tex');visible=visible.replace(r'\input{final_supp_7.tex}','')
 check('Reader-facing supplement has no internal Plan numbering',len(re.findall(r'\bPlan[ -]?\d+|\bPLAN\d+',visible)),0,0)
 check('Main retains 126.4% boundary',int('126.4\\%' in text),1,0);check('Main retains explicit orientation counts',int('8 fastMRI and 6 IXI' in text),1,0)
 check('No fabricated ethics assertion',int('Author confirmation required before submission' in visible),1,0)
 pd.DataFrame(checks).to_csv(OUT/'submission_headline_checks.csv',index=False)
 files=['array_checks_all.csv','new_array_reproduction_checks.csv','sensitivity_reproduction_checks.csv','reproduction_initial_checks.csv','submission_headline_checks.csv'];overview=[]
 for filename in files:
  d=pd.read_csv(OUT/filename);overview.append(dict(file=filename,checks=len(d),failures=int((d.status!='PASS').sum())))
 (OUT/'final_reproduction_summary.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':overview,'all_pass':all(x['failures']==0 for x in overview)},indent=2),encoding='utf-8')
 print(overview,flush=True)
 if any(x['failures'] for x in overview):raise SystemExit('Visible numerical/text mismatch; inspect submission_headline_checks.csv')
if __name__=='__main__':main()
