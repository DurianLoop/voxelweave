"""Check all 16 printed rows, trade-offs and literal curriculum endpoints; no MRI claim."""
import sys,json,re
from pathlib import Path
from decimal import Decimal,getcontext
import query_author_sources as client
HERE=Path(__file__).resolve().parent;OUT=HERE/'table_audit_attempt01'
D=Decimal

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();resources=client.previous.resource_guard()
    OUT.mkdir(exist_ok=False);getcontext().prec=40
    p=HERE/'ACAR_TABLE_TRANSCRIPTION.json';t=json.loads(p.read_text(encoding='utf-8'))
    comparisons=[];matched=0
    for table in ['table1','table2']:
        tab=t[table];text=(HERE/'primary_attempt01'/f"acar_page{tab['physical_page']:03d}.txt").read_text(encoding='utf-8')
        lines=[x.strip() for x in text.splitlines() if re.search(r'\d+\.\d{4}',x)]
        assert len(lines)==len(tab['rows']),(table,lines)
        for (name,vals),line in zip(tab['rows'].items(),lines):
            actual=re.findall(r'(?<!\S)\d+\.\d{4}(?!\S)',line)
            assert actual==vals,(table,name,actual,vals);matched+=1
        pairs=([('UNet → UNet (S)','UNet'),('Multi-Decoder UNet (S)','UNet'),
                ('UNet → UNet (S)','UNet → UNet'),('Multi-Decoder UNet (S)','Multi-Decoder UNet')]
               if table=='table1' else [('CascadeNet → MANet (S)','CascadeNet'),('CascadeNet → MANet (S)','CascadeNet → MANet')])
        for rate in ['R4','R8']:
            for proposed,before in pairs:
                a=list(map(D,tab['rows'][rate+'_'+proposed]));b=list(map(D,tab['rows'][rate+'_'+before]))
                delta={c:str(x-y) for c,x,y in zip(tab['columns'],a,b)}
                comparisons.append(dict(table=table,rate=rate,proposed=proposed,comparator=before,proposed_minus_comparator=delta))
    # Numerical demonstrations only: epsilon/P are assumed, not supplied by the paper.
    examples=[]
    for r in [D('.25'),D('.125')]:
        eps=D('.001');start=1-eps
        for patience in [10,50]:
            seq=[]
            for i in [1,patience,patience+1]:
                value=start*((r/start).ln()*D(i-1)/D(patience)).exp() if i<=patience else r
                seq.append(dict(epoch=i,retained_fraction=str(value)))
            examples.append(dict(assumed_epsilon=str(eps),assumed_P=patience,target_fraction=str(r),values=seq,
                author_parameters_verified=False,last_stabilization_epoch_not_exact_target=True))
    result=dict(complete=True,errors=[],all_16_rows_match_extracted_text=matched==16,transcribed_rows_checked=matched,
        comparisons=comparisons,literal_schedule_examples=examples,author_P_epsilon_total_epochs_verified=False,
        table1_and_table2_F_column_order_different=True,MSE_not_compared_across_tables=True,
        ROI_denominator_identical_across_methods_verified=False,segmentation_task_benefit_measured=False,
        patient_level_statistical_inference_performed=False,
        source_bindings=[client.base.entry(p) for p in [Path(__file__),p,HERE/'VISUAL_AND_TABLE_PLAN.md',
            HERE/'primary_attempt01/acar.pdf',HERE/'primary_attempt01/acar_page006.txt',HERE/'primary_attempt01/acar_page007.txt',
            HERE/'visual_attempt01/receipt.json']],resource_snapshot=resources,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    display=[c for c in comparisons if c['table']=='table2' and c['comparator']=='CascadeNet']
    print(json.dumps(dict(complete=True,rows_checked=matched,local_global_tradeoffs=display,
        author_schedule_parameters_verified=False,segmentation_effect_verified=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
