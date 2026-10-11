"""Exact arithmetic of published columns, not a new clinical efficiency estimate."""
import sys,json,re,time
from fractions import Fraction
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
def seconds(s):
    s=s.split('(')[0];factors={'h':3600,'min':60,'s':1}
    items=re.findall(r'(\d+)\s*(h|min|s)\b',s);assert items
    return sum(int(n)*factors[u] for n,u in items)
def fraction(v):return dict(exact=str(v),decimal=float(v))
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resources=client.resource_guard()
    tables=json.loads((HERE/'extraction_attempt01/clinical_vs_tables.json').read_text(encoding='utf-8'));assert len(tables)==1
    rows=tables[0]['rows'];assert len(rows)==5
    names=['standard_preparation','assisted_preparation','standard_MDTM','assisted_MDTM'];values={}
    for name,row in zip(names,rows[1:]):
        offset=2 if len(row)>=4 else 1
        # MDTM standard has four cells because the last one is a footnote; the stage cell is present.
        if name=='assisted_preparation' or name=='assisted_MDTM':offset=1
        mean,total=seconds(row[offset]),seconds(row[offset+1]);values[name]=dict(original_cells=row,mean_seconds=mean,total_seconds=total,
            assumed_50_mean_product_seconds=mean*50,total_minus_50_mean_seconds=total-mean*50,
            total_divided_by_mean_not_assumed_patient_count=fraction(Fraction(total,mean)))
    assert [values[n]['mean_seconds'] for n in names]==[156,174,81,75]
    assert [values[n]['total_seconds'] for n in names]==[7650,8724,3756,2904]
    mean_prep=values[names[1]]['mean_seconds']-values[names[0]]['mean_seconds']
    mean_mdt=values[names[3]]['mean_seconds']-values[names[2]]['mean_seconds']
    total_prep=values[names[1]]['total_seconds']-values[names[0]]['total_seconds']
    total_mdt=values[names[3]]['total_seconds']-values[names[2]]['total_seconds']
    scenarios=[dict(assumed_MDT_attendees=k,mean_column_human_time_delta_seconds_per_case=mean_prep+k*mean_mdt,
        total_column_human_time_delta_seconds=total_prep+k*total_mdt,actual_person_time_estimated=False) for k in range(1,13)]
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],original_column_arithmetic=values,
        all50_patient_categories=dict(fully_accepted=36,one_session_revision=8,complete_revision=6,total=50),
        categories_fraction=[fraction(Fraction(v,50)) for v in [36,8,6]],
        per_case_mean_phase_delta_seconds=dict(preparation=mean_prep,MDTM=mean_mdt,sequential_sum=mean_prep+mean_mdt),
        total_phase_delta_seconds=dict(preparation=total_prep,MDTM=total_mdt,sequential_sum=total_prep+total_mdt),
        mean_based_50_case_sum_delta_seconds=50*(mean_prep+mean_mdt),
        column_discrepancy_not_explained_by_available_maintext=True,columns_not_merged_into_one_estimate=True,
        hypothetical_person_time_scenarios=scenarios,mean_column_break_even_attendees=fraction(Fraction(mean_prep,-mean_mdt)),
        total_column_break_even_attendees=fraction(Fraction(total_prep,-total_mdt)),
        abstract_DSC_mapping=dict(T1C=.9392,T2=.9331),maintext_block54_DSC_mapping=dict(T2=.9392,T1C=.9331),
        DOI='10.1093/jamiaopen/ooaf163',new_clinical_net_benefit_or_significance_estimated=False,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        publication_claim_confirmed=False,goal_status='active',resources=resources,elapsed_seconds=time.perf_counter()-started,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'TABLE_TIME_AND_TEXTURE_FOLLOWUP_PROTOCOL.md',HERE/'extraction_attempt01/clinical_vs_tables.json',HERE/'extraction_attempt01/clinical_vs_blocks.json']])
    out=HERE/'clinical_time_audit_attempt01';out.mkdir(exist_ok=False);client.dump(out/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,mean_columns_sequential_delta_seconds_per_case=mean_prep+mean_mdt,total_columns_sequential_delta_seconds=total_prep+total_mdt,
        mean_based_50_case_delta_seconds=50*(mean_prep+mean_mdt),mean_vs_total_columns_not_merged=True,clinical_net_benefit_estimated=False)),flush=True)
if __name__=='__main__':main()
