"""Exact descriptive arithmetic of printed tissue endpoints, with no patient inference."""
import sys,json,re
from decimal import Decimal, getcontext
from pathlib import Path
import query_seranet_stdlib_v3 as prior

HERE=Path(__file__).resolve().parent
OUT=HERE/'table_audit_attempt01'

def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.base.own_priority();resources=prior.resource_guard()
    OUT.mkdir(exist_ok=False);getcontext().prec=40
    t=json.loads((HERE/'SADFN_TABLE_TRANSCRIPTION.json').read_text(encoding='utf-8'))
    page=(HERE/'primary_attempt01/sadfn_page014.txt').read_text(encoding='utf-8')
    patterns={
        'ZF':'ZF+Pre-SegNet','TLMRI':'TLMRI+Pre-SegNet','PANO':'PANO+Pre-SegNet','GBRWT':'GBRWT+Pre-SegNet',
        'Pre-RecNet5':'Pre-RecNet5+Pre-SegNet','SADFN5-WOS':'SADFN5-WOS+Pre-SegNet',
        'Liu26':'Liu[26]+Pre-SegNet','SADFN5':'SADFN5+Pre-SegNet','Full-sampled':'Full-sampled+Pre-SegNet'}
    matches={}
    for name,label in patterns.items():
        line=next(x.strip() for x in page.splitlines() if x.strip().startswith(label+' '))
        vals=re.findall(r'(?<!\S)\d+\.\d+(?!\S)',line[len(label):])
        assert vals==t['rows'][name],(name,vals)
        matches[name]=True
    rows={k:list(map(Decimal,v)) for k,v in t['rows'].items()}
    sad=rows['SADFN5'];full=rows['Full-sampled'];comparisons={}
    for name in ['Pre-RecNet5','SADFN5-WOS','Liu26','GBRWT']:
        before=rows[name];d=[sad[i]-before[i] for i in range(9)]
        oriented=[d[i] if i%3==0 else -d[i] for i in range(9)]
        comparisons[name]=dict(sadfn_minus_comparator={c:str(x) for c,x in zip(t['columns'],d)},
            oriented_improvement_count=sum(x>0 for x in oriented),tie_count=sum(x==0 for x in oriented),
            oriented_regression_count=sum(x<0 for x in oriented),
            descriptive_equal_tissue_Dice_gain_pp=str(sum(d[::3])/3))
    tissue_gap=[full[i]-sad[i] for i in [0,3,6]]
    q=dict(complete=True,errors=[],all_transcribed_rows_match_extracted_text=all(matches.values()),row_matches=matches,
        source_bindings=[prior.base.entry(p) for p in (Path(__file__),HERE/'SADFN_TABLE_TRANSCRIPTION.json',
          HERE/'METADATA_FOLLOWUP_PLAN.md',HERE/'primary_attempt01/sadfn.pdf',HERE/'primary_attempt01/sadfn_page014.txt',HERE/'table_visual_attempt01/receipt.json')],
        comparisons=comparisons,fullsample_minus_sadfn_tissue_Dice_pp=list(map(str,tissue_gap)),
        descriptive_mean_fullsample_gap_pp=str(sum(tissue_gap)/3),
        printed_runtime_sadfn_to_prerecnet_ratio=str(Decimal('0.06')/Decimal('0.03')),
        printed_runtime_sadfn_to_wos_ratio=str(Decimal('0.06')/Decimal('0.07')),
        all_nine_endpoints_best_among_reconstructions=False,
        counterexample=dict(endpoint='CSF_HD',GBRWT='1.647',SADFN5='1.649'),
        resource_snapshot=resources,statistical_inference_performed=False,clinical_lesion_effect_verified=False,
        runtime_scope_or_full_deployment_cost_verified=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    assert comparisons['GBRWT']['oriented_regression_count']==1
    prior.base.new(OUT/'receipt.json',q)
    print(json.dumps({k:q[k] for k in ('complete','all_transcribed_rows_match_extracted_text','comparisons','fullsample_minus_sadfn_tissue_Dice_pp','counterexample')}),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
