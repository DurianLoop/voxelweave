"""CPU arithmetic and extraction crosscheck of visually transcribed public tables."""
import sys, json, re, time
from pathlib import Path
from decimal import Decimal, getcontext
from datetime import datetime, timezone
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; OUT=HERE/'table_audit_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
getcontext().prec=32
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dec(x):return Decimal(x)
def mean(xs):return sum(map(dec,xs))/Decimal(len(xs))
def comparison(rows,ia,ib,direction=1):
    diffs=[direction*(dec(r[ib])-dec(r[ia])) for r in rows]
    return dict(n_correlated_conditions=len(diffs),higher_is_better_transformed_deltas=list(map(str,diffs)),
        mean_delta=str(sum(diffs)/Decimal(len(diffs))),win=sum(x>0 for x in diffs),
        tie=sum(x==0 for x in diffs),loss=sum(x<0 for x in diffs),
        minimum_delta=str(min(diffs)),maximum_delta=str(max(diffs)),patient_significance_test=False)
def nums(s):return re.findall(r'\d+\.\d+',re.sub(r'(\d)\s+\.(\d)',r'\1.\2',s))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();tick=time.perf_counter();OUT.mkdir(exist_ok=False)
    tr=read(HERE/'PAPER_TABLE_TRANSCRIPTION.json');checks=[];mmar=[];bindings=[]
    assert tr['all_selected_tables_visually_reviewed'] and not tr['patient_raw_predictions_available']
    for table in tr['mmar']['tables']:
        p=HERE/f"primary_attempt01/mmar_page{table['page']:03d}.txt";bindings.append(base.entry(p))
        lines=p.read_text(encoding='utf-8').splitlines()
        rawrows=[line for line in lines if re.match(r'^[✓✗]',line)]
        assert len(rawrows)==15,(table['table'],len(rawrows))
        for i,(line,row) in enumerate(zip(rawrows,table['macro'])):
            symbols=re.findall(r'[✓✗]',line)[:4];bits=''.join('1' if x=='✓' else '0' for x in symbols)
            assert bits==tr['mmar']['rows'][i]
            values=nums(line);has_specialist=not(table['table']==3 and i>=7)
            actual=values[1:4] if has_specialist else values[:3]
            assert list(map(dec,actual))==list(map(dec,row)),(table['table'],i,actual,row)
        mline=next(line for line in lines if line.startswith('Mean '));v=nums(mline)
        actualmean=v[1:4] if table['table']!=3 else v[:3]
        assert actualmean==table['printed_macro_mean']
        averages=[mean([row[i] for row in table['macro']]) for i in range(3)]
        discrepancy=[a-dec(b) for a,b in zip(averages,actualmean)]
        assert all(abs(x)<=Decimal('.011') for x in discrepancy)
        result=dict(table=table['table'],physical_page=table['page'],condition=table['condition'],
            printed_mean=actualmean,recomputed_mean=list(map(str,averages)),rounding_discrepancy=list(map(str,discrepancy)),
            MMAR_vs_UNet=comparison(table['macro'],0,2),MMAR_vs_UHeMIS=comparison(table['macro'],1,2))
        if table['table']>=4:
            result['all_clean_row']=table['macro'][-1]
            result['first14_only_MMAR_vs_UNet']=comparison(table['macro'][:14],0,2)
            result['first14_only_MMAR_vs_UHeMIS']=comparison(table['macro'][:14],1,2)
            result['first14_only_denominator_note']='Fourteen correlated modality conditions, not fourteen independent patients'
        if table['table']==3:
            indices=[tr['mmar']['rows'].index(b) for b in table['novel_combinations']]
            rows=[table['macro'][i] for i in indices]
            result['novel_only_MMAR_vs_UNet']=comparison(rows,0,2)
            result['novel_only_MMAR_vs_UHeMIS']=comparison(rows,1,2)
            result['novel_only_best_of_both_count']=sum(dec(r[2])>max(dec(r[0]),dec(r[1])) for r in rows)
        mmar.append(result);checks.append(dict(table=table['table'],visual_transcription_crosschecked_against_extraction=True))
    x=tr['xlstm_hved'];p=HERE/'primary_attempt01/xlstm_hved_page004.txt';bindings.append(base.entry(p))
    lines=p.read_text(encoding='utf-8').splitlines();rawrows=[s for s in lines if re.match(r'^[◦•]',s)]
    assert len(rawrows)==30
    xlstm={}
    for name,start,direction in [('HD95_mm',0,-1),('Dice_percent',15,1)]:
        for i,(line,row) in enumerate(zip(rawrows[start:start+15],x[name])):
            bits=''.join('1' if s=='•' else '0' for s in re.findall(r'[◦•]',line)[:4]);assert bits==x['rows'][i]
            values=nums(line);assert len(values)==12
            actual=[values[j] for j in [2,3,6,7,10,11]]
            assert list(map(dec,actual))==list(map(dec,row)),(name,i,actual,row)
        printed=x['printed_HD95_mean' if name=='HD95_mm' else 'printed_Dice_mean']
        averages=[mean([r[i] for r in x[name]]) for i in range(6)]
        discrepancies=[a-dec(b) for a,b in zip(averages,printed)]
        assert all(abs(v)<=Decimal('.011') for v in discrepancies),(name,discrepancies)
        xlstm[name]=dict(printed_mean=printed,recomputed_mean=list(map(str,averages)),
            rounding_discrepancy=list(map(str,discrepancies)),
            comparison_vs_mmformer={region:comparison(x[name],2*i,2*i+1,direction) for i,region in enumerate(['WT','TC','ET'])})
    ablation={}
    for key,prefix in [('without_SAVE','w/o SAVE '),('without_ViLA','w/o ViLA Module '),('without_SFECA','w/o SFECA Module ')]:
        line=next(s for s in lines if s.startswith(prefix));assert nums(line)==x['table2'][key]
        ablation[key]=[str((dec(a)-dec(b))*(1 if i<3 else -1)) for i,(a,b) in enumerate(zip(x['table2']['ours'],x['table2'][key]))]
    assert nums(next(s for s in lines if s.startswith('XLSTM-HVED (Ours) ')))==x['table2']['ours']
    xlstm['table2_full_minus_ablation_benefit_direction']=ablation
    # Count actual index identities, distinguishing pagination from an overlapping additional query.
    current=read(HERE/'index_attempt01/receipt.json')
    previous=read(ROOT/'joint_segmentation_mri_prior_art_2026_10_08/index_followup_attempt01/receipt.json')
    oldrows=[e for r in previous['records'] for e in r.get('entries',[]) if 'id' in e]
    currentrows=[e for r in current['records'] for e in r.get('entries',[])]
    oldids={re.sub(r'v\d+$','',e['id'].split('/abs/')[-1]) for e in oldrows}
    pages=[e for r in current['records'] if r['key'].startswith('joint_title_page') for e in r['entries']]
    pageids={re.sub(r'v\d+$','',e['id'].split('/abs/')[-1]) for e in pages}
    allids={re.sub(r'v\d+$','',e['id'].split('/abs/')[-1]) for e in currentrows}
    index=dict(previous_returned= len(oldrows),previous_unique=len(oldids),
        current_returned=len(currentrows),current_unique=len(allids),
        pagination_returned=len(pages),pagination_unique=len(pageids),pagination_overlap=len(oldids&pageids),
        title_pagination_union_unique=len(oldids|pageids),additional_query_overlap_with_current_pagination=len(allids&pageids),
        current_union_with_previous_unique=len(oldids|allids),SERANet_found_and_read=False,systematic_review=False)
    bound=[Path(__file__),HERE/'PROTOCOL.md',HERE/'PAPER_TABLE_TRANSCRIPTION.json',
        HERE/'visual_attempt01/receipt.json',HERE/'table_visual_attempt01/receipt.json',
        HERE/'index_attempt01/receipt.json',ROOT/'joint_segmentation_mri_prior_art_2026_10_08/index_followup_attempt01/receipt.json']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[base.entry(p) for p in bound]+bindings,mmar=mmar,xlstm_hved=xlstm,index_identity_audit=index,
        checks=checks,public_table_only=True,medical_arrays_loaded=0,model_checkpoint_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,medical_training_updates=0,new_project_MRI_effect=False,
        patient_level_statistical_significance_recomputed=False,elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=True,index_identity_audit=index,
        mmar=[dict(table=r['table'],vs_UNet=r['MMAR_vs_UNet'],vs_UHeMIS=r['MMAR_vs_UHeMIS']) for r in mmar],
        xlstm_hved=xlstm),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
