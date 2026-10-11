"""Independent original-XML cells and exact printed arithmetic, not patient reanalysis."""
import sys,json,re,time,xml.etree.ElementTree as ET
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
def textval(e):return ' '.join(''.join(e.itertext()).split())
def tag(e):return e.tag.rsplit('}',1)[-1]
def tables(path):
    root=ET.parse(path).getroot()
    return [dict(id=e.get('id'),rows=[[textval(c) for c in row if tag(c) in {'th','td'}] for row in e.iter() if tag(row)=='tr']) for e in root.iter() if tag(e)=='table-wrap']
def scientific(s):
    m,p=s.split('× 10');exponent=int(p.replace('−','-'));base=F(10)**exponent
    return F(m.strip())*base,F('0.005')*base
def rational(v):return dict(fraction=str(v),decimal=float(v))
def overlap(a,b):return max(a[0],b[0])<=min(a[1],b[1])
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    src={key:HERE/('xml_attempt01/'+key+'.xml') for key in ['synthsr','vsrad']}
    http=read(HERE/'xml_attempt01/HTTP_RECEIPT.json');assert http['complete'] and not http['errors']
    original={key:tables(path) for key,path in src.items()}
    for key,values in original.items():
        saved=read(HERE/('xml_extraction_attempt01/'+key+'_tables.json'))
        assert values==[{k:v[k] for k in ['id','rows']} for v in saved]
    vtable=original['vsrad'];assert [x['id'] for x in vtable]==['tab1','tab2']
    pvalues=[]
    for cells in vtable[0]['rows'][1:]:
        assert len(cells)==5
        raw,eraw=scientific(cells[3]);adj,eadj=scientific(cells[4]);reported=(adj-eadj,adj+eadj)
        seven=(7*(raw-eraw),7*(raw+eraw));nine=(9*(raw-eraw),9*(raw+eraw))
        pvalues.append(dict(variable=cells[0],raw_printed=cells[3],adjusted_printed=cells[4],
            printed_ratio=rational(adj/raw),declared7_times_raw=rational(7*raw),alternative9_times_raw=rational(9*raw),
            declared7_compatible_with_display_precision=overlap(seven,reported),alternative9_compatible_with_display_precision=overlap(nine,reported),
            significant_under7_and9=(7*raw<F('0.05') and 9*raw<F('0.05'))))
    limits=[]
    for cells in vtable[1]['rows'][1:]:
        assert len(cells)==7
        vals=[F(s.replace('−','-')) for s in cells[1:5]];median,iqr,lo,hi=vals
        e=F('0.005');possible_width=F('2.5')*e
        lo_calc=median-F('1.5')*iqr;hi_calc=median+F('1.5')*iqr
        count=int(cells[5]);pct=F(cells[6]);actual=F(100*count,64)
        limits.append(dict(variable=cells[0],median_printed=str(median),IQR_printed=str(iqr),
            exact_from_printed_lower=rational(lo_calc),exact_from_printed_upper=rational(hi_calc),
            reported_lower=str(lo),reported_upper=str(hi),lower_delta=rational(lo-lo_calc),upper_delta=rational(hi-hi_calc),
            lower_compatible_with_hidden_rounding=overlap((lo_calc-possible_width,lo_calc+possible_width),(lo-e,lo+e)),
            upper_compatible_with_hidden_rounding=overlap((hi_calc-possible_width,hi_calc+possible_width),(hi-e,hi+e)),
            outlier_count=count,analyzed_denominator=64,exact_outlier_percentage=rational(actual),
            printed_outlier_percentage=cells[6],percentage_rounding_compatible=abs(pct-actual)<=F('0.05')))
    assert len(pvalues)==len(limits)==7
    assert all(not v['declared7_compatible_with_display_precision'] and v['alternative9_compatible_with_display_precision'] for v in pvalues)
    assert all(v['significant_under7_and9'] for v in pvalues)
    assert all(v['lower_compatible_with_hidden_rounding'] and v['upper_compatible_with_hidden_rounding'] and v['percentage_rounding_compatible'] for v in limits)
    st=original['synthsr'];assert [v['id'] for v in st]==['T1','T2','T3']
    rows=st[0]['rows'];spacing=st[1]['rows'];contrasts=[]
    for i,region in enumerate(rows[0][1:],1):
        full,ablation,patient=[F(rows[j][i]) for j in [1,2,3]]
        low,mid,high=[F(spacing[j][i]) for j in [1,2,3]]
        contrasts.append(dict(region=region,scan_full=rational(full),scan_ablation=rational(ablation),subject_median=rational(patient),
            full_minus_ablation=rational(full-ablation),subject_minus_scan=rational(patient-full),
            spacing_up_to4=rational(low),spacing4_to6=rational(mid),spacing_over6=rational(high),
            over6_minus_up_to4=rational(high-low)))
    assert len(contrasts)==9
    result=dict(complete=True,errors=[],vsrad_Bonferroni_checks=pvalues,vsrad_limits_checks=limits,synthsr_table_contrasts=contrasts,
        seven_rows_show_factor9_not_declared7=True,original_significance_unchanged_under_both=True,
        all7_limits_and_percentages_compatible_with_display_rounding=True,
        denominators=dict(vsrad_generated=75,vsrad_excluded=11,vsrad_analyzed=64,vsrad_AD_reported=29,vsrad_normal_reported=8,
            vsrad_ROC_classified_cases_reported=37,synthsr_correlation_scans=435,synthsr_correlation_subjects=41,
            synthsr_spacing_groups=[197,110,128],synthsr_AD_selected=100,synthsr_AD_failed_reference_segmentations=4,
            synthsr_BraTSReg_landmarks_original=1252,synthsr_BraTSReg_landmarks_kept=1075,synthsr_ATLAS_original=655,synthsr_ATLAS_lateralized_subset=598),
        excluded_proportion=rational(F(11,75)),landmark_removed_proportion=rational(F(177,1252)),
        acquisition_only_saved_seconds=127,acquisition_plus_generation_saved_seconds=50,
        whole_pipeline_or_person_time_saving_claimed=False,paired_raw_volumes_or_diagnostic_scores_available=False,
        table1_difference_of_medians_not_treated_as_median_of_paired_difference=True,
        original_DeLong_statistic_not_repaired=True,universal95percent_guard_inferred=False,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        confirmation_patients_opened=False,new_patient_medical_effects=0,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'TABLE_AUDIT_PROTOCOL.md',HERE/'xml_attempt01/HTTP_RECEIPT.json',*src.values(),
            HERE/'xml_extraction_attempt01/synthsr_tables.json',HERE/'xml_extraction_attempt01/vsrad_tables.json']])
    out=HERE/'table_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    assert time.perf_counter()-started<60 and sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<100000
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','vsrad_Bonferroni_checks','vsrad_limits_checks','synthsr_table_contrasts']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
