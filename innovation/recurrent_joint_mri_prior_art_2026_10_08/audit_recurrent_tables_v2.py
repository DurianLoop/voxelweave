"""Audit v2: keep transcription checks strict; report source arithmetic inconsistencies."""
import sys,json,re,time
from pathlib import Path
from decimal import Decimal
from datetime import datetime,timezone
import audit_recurrent_tables as prior
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'table_audit_attempt02'
base=prior.base;resource_guard=prior.resource_guard
dec=prior.dec;mean=prior.mean;nums=prior.nums;comparison=prior.comparison;read=prior.read
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();tick=time.perf_counter();OUT.mkdir(exist_ok=False)
    tr=read(HERE/'PAPER_TABLE_TRANSCRIPTION.json');mmar=[];bindings=[];mismatches=[]
    assert tr['all_selected_tables_visually_reviewed'] and not tr['patient_raw_predictions_available']
    for table in tr['mmar']['tables']:
        p=HERE/f"primary_attempt01/mmar_page{table['page']:03d}.txt";bindings.append(base.entry(p))
        lines=p.read_text(encoding='utf-8').splitlines();rawrows=[s for s in lines if re.match(r'^[✓✗]',s)]
        assert len(rawrows)==15
        for i,(line,row) in enumerate(zip(rawrows,table['macro'])):
            bits=''.join('1' if s=='✓' else '0' for s in re.findall(r'[✓✗]',line)[:4])
            assert bits==tr['mmar']['rows'][i]
            values=nums(line);actual=values[:3] if table['table']==3 and i>=7 else values[1:4]
            assert list(map(dec,actual))==list(map(dec,row)),(table['table'],i,actual,row)
        values=nums(next(s for s in lines if s.startswith('Mean ')))
        actualmean=values[:3] if table['table']==3 else values[1:4];assert actualmean==table['printed_macro_mean']
        averages=[mean([r[i] for r in table['macro']]) for i in range(3)]
        discrepancy=[a-dec(b) for a,b in zip(averages,actualmean)]
        assert all(abs(x)<=Decimal('.011') for x in discrepancy)
        result=dict(table=table['table'],physical_page=table['page'],condition=table['condition'],
            printed_mean=actualmean,recomputed_mean=list(map(str,averages)),rounding_discrepancy=list(map(str,discrepancy)),
            MMAR_vs_UNet=comparison(table['macro'],0,2),MMAR_vs_UHeMIS=comparison(table['macro'],1,2))
        if table['table']>=4:
            result.update(all_clean_row=table['macro'][-1],
                first14_only_MMAR_vs_UNet=comparison(table['macro'][:14],0,2),
                first14_only_MMAR_vs_UHeMIS=comparison(table['macro'][:14],1,2),
                first14_only_denominator_note='Fourteen correlated modality conditions, not independent patients')
        if table['table']==3:
            rows=[table['macro'][tr['mmar']['rows'].index(b)] for b in table['novel_combinations']]
            result.update(novel_only_MMAR_vs_UNet=comparison(rows,0,2),
                novel_only_MMAR_vs_UHeMIS=comparison(rows,1,2),
                novel_only_best_of_both_count=sum(dec(r[2])>max(dec(r[0]),dec(r[1])) for r in rows))
        mmar.append(result)
    x=tr['xlstm_hved'];p=HERE/'primary_attempt01/xlstm_hved_page004.txt';bindings.append(base.entry(p))
    lines=p.read_text(encoding='utf-8').splitlines();rawrows=[s for s in lines if re.match(r'^[◦•]',s)]
    assert len(rawrows)==30;xlstm={}
    printed_rows=[nums(s) for s in lines if s.startswith('Average ')];assert len(printed_rows)==2
    for name,start,direction,average_index in [('HD95_mm',0,-1,0),('Dice_percent',15,1,1)]:
        for i,(line,row) in enumerate(zip(rawrows[start:start+15],x[name])):
            bits=''.join('1' if s=='•' else '0' for s in re.findall(r'[◦•]',line)[:4]);assert bits==x['rows'][i]
            values=nums(line);assert len(values)==12
            actual=[values[j] for j in [2,3,6,7,10,11]]
            assert list(map(dec,actual))==list(map(dec,row)),(name,i,actual,row)
        printed=x['printed_HD95_mean' if name=='HD95_mm' else 'printed_Dice_mean']
        assert [printed_rows[average_index][j] for j in [2,3,6,7,10,11]]==printed
        averages=[mean([r[i] for r in x[name]]) for i in range(6)]
        discrepancy=[a-dec(b) for a,b in zip(averages,printed)]
        bad=[dict(paper='xlstm_hved',table=1,page=4,metric=name,column=x['columns'][i],
            printed=printed[i],recomputed=str(averages[i]),difference=str(v),explanation_in_source_not_resolved=True)
            for i,v in enumerate(discrepancy) if abs(v)>Decimal('.011')]
        mismatches.extend(bad)
        xlstm[name]=dict(printed_mean=printed,recomputed_mean=list(map(str,averages)),
            discrepancy=list(map(str,discrepancy)),printed_summary_inconsistencies=bad,
            comparison_vs_mmformer={region:comparison(x[name],2*i,2*i+1,direction) for i,region in enumerate(['WT','TC','ET'])})
    ablation={}
    for key,prefix in [('without_SAVE','w/o SAVE '),('without_ViLA','w/o ViLA Module '),('without_SFECA','w/o SFECA Module ')]:
        assert nums(next(s for s in lines if s.startswith(prefix)))==x['table2'][key]
        ablation[key]=[str((dec(a)-dec(b))*(1 if i<3 else -1)) for i,(a,b) in enumerate(zip(x['table2']['ours'],x['table2'][key]))]
    assert nums(next(s for s in lines if s.startswith('XLSTM-HVED (Ours) ')))==x['table2']['ours']
    xlstm['table2_printed_full_minus_ablation_benefit_direction']=ablation
    xlstm['table2_note']='Uses printed summary cells; does not fix Table 1 inconsistency or establish patient significance'
    current=read(HERE/'index_attempt01/receipt.json')
    previous_path=ROOT/'joint_segmentation_mri_prior_art_2026_10_08/index_followup_attempt01/receipt.json'
    previous=read(previous_path)
    oldrows=[e for r in previous['records'] for e in r.get('entries',[]) if 'id' in e]
    currentrows=[e for r in current['records'] for e in r.get('entries',[])]
    pages=[e for r in current['records'] if r['key'].startswith('joint_title_page') for e in r['entries']]
    extra=[e for r in current['records'] if not r['key'].startswith('joint_title_page') for e in r['entries']]
    def ids(rows):return {re.sub(r'v\d+$','',e['id'].split('/abs/')[-1]) for e in rows}
    oldids,pageids,extraids,currentids=map(ids,[oldrows,pages,extra,currentrows])
    index=dict(previous_returned=len(oldrows),previous_unique=len(oldids),current_returned=len(currentrows),
        current_unique=len(currentids),pagination_returned=len(pages),pagination_unique=len(pageids),
        pagination_overlap=len(oldids&pageids),title_pagination_union_unique=len(oldids|pageids),
        additional_query_returned=len(extra),additional_query_unique=len(extraids),
        additional_query_overlap_with_current_pagination=len(extraids&pageids),
        current_union_with_previous_unique=len(oldids|currentids),SERANet_found_and_read=False,systematic_review=False,
        current_unique_identities=sorted(currentids),previous_unique_identities=sorted(oldids))
    bound=[Path(__file__),HERE/'audit_recurrent_tables.py',HERE/'AUDIT_REPAIR.md',HERE/'PROTOCOL.md',
        HERE/'PAPER_TABLE_TRANSCRIPTION.json',HERE/'visual_attempt01/receipt.json',HERE/'table_visual_attempt01/receipt.json',
        HERE/'index_attempt01/receipt.json',previous_path]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[base.entry(p) for p in bound]+bindings,
        mmar=mmar,xlstm_hved=xlstm,index_identity_audit=index,source_printed_summary_inconsistencies=mismatches,
        all_transcribed_rows_match_extracted_text=True,all_printed_summaries_arithmetically_consistent=not mismatches,
        public_table_only=True,medical_arrays_loaded=0,model_checkpoint_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        medical_training_updates=0,new_project_MRI_effect=False,patient_level_statistical_significance_recomputed=False,
        elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=True,index_identity_audit=index,printed_summary_inconsistencies=mismatches,
        mmar=[dict(table=r['table'],UNet_mean_delta=r['MMAR_vs_UNet']['mean_delta'],UHeMIS_mean_delta=r['MMAR_vs_UHeMIS']['mean_delta'],
            UNet_wins=r['MMAR_vs_UNet']['win'],UHeMIS_wins=r['MMAR_vs_UHeMIS']['win']) for r in mmar],
        xlstm_hved=xlstm),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
