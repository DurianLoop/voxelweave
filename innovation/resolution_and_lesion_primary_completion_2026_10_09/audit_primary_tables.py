"""Exact source-table comparisons and printed weighting identity, not clinical validation."""
import sys,time,json,gzip,itertools
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
sys.path.insert(0,str(ROOT/'augmentation_primary_followup_2026_10_08'))
from extract_bigaug_stdlib import Parser,Node
EXPECTED={'vinn.html.gz':'723b0df3085ec7ba8ba1f0453fa2690ffc155d604d71a844cd84bb441235730b',
          'lesion_ensemble.html.gz':'da59c8ddc74c9c9babfb95d95508e542022c59e9411267a6e4dba799817d8224'}
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    src=HERE/'sources_attempt01';fetch=read(src/'receipt.json');assert fetch['complete'] and not fetch['errors']
    for b in fetch['records']:
        for e in [b['raw_response_gzip']]+b['extraction_bindings']:
            p=ROOT/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes']
    recovered={};sources=[Path(__file__),HERE/'TABLE_AUDIT_PROTOCOL.md',src/'receipt.json']
    for key in ['vinn','lesion_ensemble']:
        path=src/(key+'.html.gz');assert sha(path)==EXPECTED[path.name];sources.append(path)
        parser=Parser();parser.feed(gzip.decompress(path.read_bytes()).decode('utf-8'))
        article=next(n for n in parser.root.walk() if n.tag=='article');direct=[]
        for n in article.walk():
            if n.tag!='table':continue
            rows=[]
            for tr in n.walk():
                if tr.tag=='tr':
                    cells=[' '.join(c.text().split()) for c in tr.children if isinstance(c,Node) and c.tag in ['th','td']]
                    if cells:rows.append(cells)
            direct.append(rows)
        tablepath=src/(key+'_tables.json');sources.append(tablepath)
        saved=[[[c['text'] for c in row] for row in t['rows']] for t in read(tablepath)]
        assert saved==direct;recovered[key]=direct
    independent_arithmetic_checks=0
    def difference(a,b):
        nonlocal independent_arithmetic_checks
        exact=Fraction(a)-Fraction(b);assert exact==Fraction(Decimal(a)-Decimal(b));independent_arithmetic_checks+=1
        return dict(before=b,after=a,exact=str(exact),delta=float(exact))
    lt=recovered['lesion_ensemble'];weights=[]
    for j,task in enumerate(lt[0][0][1:],1):
        values=[row[j] for row in lt[0][1:]];s=sum(map(Fraction,values));assert s==sum(Fraction(Decimal(v)) for v in values)==1
        weights.append(dict(task=task,printed_values=values,printed_exact_sum=str(s),printed_formula_sum_for_three_models=2))
    groups=[('PED_LW',lt[1][2:7],list(range(12)),['Dice_'+s for s in ['CC','ED','ET','NET','TC','WT']]+['NSD_'+s for s in ['CC','ED','ET','NET','TC','WT']]),
            ('MET_global',lt[2][2:7],[0,1,2,3,5,6,7,8],['Dice_ET','Dice_TC','Dice_WT','Dice_RC','NSD_ET','NSD_TC','NSD_WT','NSD_RC']),
            ('MEN_LW',lt[2][9:14],[0,1,2,5,6,7],['Dice_ET','Dice_TC','Dice_WT','NSD_ET','NSD_TC','NSD_WT']),
            ('MEN_RT_LW',lt[2][16:21],[4,9],['Dice_GTV','NSD_GTV'])]
    endpoints=[]
    for name,rows,indices,metrics in groups:
        assert len(rows)==5 and rows[3][0]=='Ensemble' and rows[4][0]=='Post-processing'
        values=[row[-(12 if name=='PED_LW' else 10):] for row in rows]
        for ix,metric in zip(indices,metrics):
            best=max((v[ix] for v in values[:3]),key=Fraction)
            row=dict(task=name,metric=metric,best_single_mean=best,ensemble_vs_best_single=difference(values[3][ix],best),post_vs_ensemble=difference(values[4][ix],values[3][ix]))
            endpoints.append(row)
    assert len(endpoints)==28
    expected={('MET_global','Dice_ET'):Fraction('-0.045'),('MET_global','Dice_TC'):Fraction('-0.045'),
              ('MET_global','Dice_WT'):Fraction('-0.050'),('MET_global','Dice_RC'):Fraction('0.202'),
              ('PED_LW','Dice_ET'):Fraction('-0.027')}
    for row in endpoints:
        key=(row['task'],row['metric'])
        if key in expected:assert Fraction(row['post_vs_ensemble']['exact'])==expected[key]
    vt=recovered['vinn'];vrows={i:{row[0]:row[1:] for row in vt[i][2:]} for i in [10,11,12]};comparisons=[]
    for ti,a,b in [(10,'FastSurferVINN + exSA','FastSurferVINN'),(12,'+ Attention','FastSurferVINN'),(12,'+ HiRes Loss','FastSurferVINN')]:
        for j,metric in enumerate(['DSC_subcortical','DSC_cortical','ASD_subcortical','ASD_cortical']):
            d=difference(vrows[ti][a][j].split()[0],vrows[ti][b][j].split()[0]);signed=Fraction(d['exact'])*(1 if j<2 else -1)
            comparisons.append(dict(primary_table_number=ti-4,comparison=a+' minus '+b,metric=metric,delta=d,improves_displayed_mean=signed>0,degrades_displayed_mean=signed<0))
    formula_cases=0
    for n in range(2,7):
        for fs in itertools.product(range(1,5),repeat=n):
            s=sum(fs);direct=[sum(Fraction(f,s) for j,f in enumerate(fs) if j!=i) for i in range(n)]
            closed=[1-Fraction(f,s) for f in fs];assert direct==closed and sum(direct)==n-1
            normalized=[w/(n-1) for w in direct];assert sum(normalized)==1 and all(0<w<Fraction(1,n-1) for w in normalized)
            formula_cases+=1
    assert formula_cases==5456 and time.perf_counter()-started<180
    contradictions=dict(vinn_bilinear_subcortical_ASD_table6=vrows[10]['FastSurferVINN'][2],
        vinn_bilinear_subcortical_ASD_table7=vrows[11]['Bi-Linear'][2],
        vinn_bilinear_subcortical_ASD_table8=vrows[12]['FastSurferVINN'][2],
        source_values_retained=True,code_actual_normalization_unknown=True)
    out=HERE/'table_audit_attempt01';out.mkdir(exist_ok=False)
    receipt=dict(complete=True,errors=[],all24_HTML_tables_reextracted_identically=True,
        clinical_mean_endpoint_comparisons=28,independent_exact_decimal_checks=independent_arithmetic_checks,
        weighting_formula_cases=5456,weights=weights,lesion_endpoint_rows=endpoints,vinn_comparisons=comparisons,
        ensemble_below_best_single_endpoints=sum(Fraction(r['ensemble_vs_best_single']['exact'])<0 for r in endpoints),
        post_degraded_endpoints=sum(Fraction(r['post_vs_ensemble']['exact'])<0 for r in endpoints),
        post_improved_endpoints=sum(Fraction(r['post_vs_ensemble']['exact'])>0 for r in endpoints),
        post_tied_endpoints=sum(Fraction(r['post_vs_ensemble']['exact'])==0 for r in endpoints),
        primary_literal_discrepancies=contradictions,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        patient_neural_forwards=0,training_updates=0,new_patient_medical_effects=0,patient_level_significance_inferred=False,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in sources])
    dump(out/'receipt.json',receipt);assert sum(p.stat().st_size for p in out.rglob('*'))<50_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<1_200_000
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['weights','lesion_endpoint_rows','vinn_comparisons','source_bindings']}),flush=True)
if __name__=='__main__':main()
