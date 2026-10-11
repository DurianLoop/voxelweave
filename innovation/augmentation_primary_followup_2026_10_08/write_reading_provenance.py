"""Register actual maintext reading ranges and real tool exits, distinct from extraction."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    before=read(HERE/'RECOVERED_TURN18_TOOL_OBSERVATIONS.json');current=read(HERE/'TURN19_TOOL_OBSERVATIONS_PART01.json')
    records={r['key']:r['value'] for r in before['records']+current['records']};assert not before['missing'] and not current['missing']
    for key in ['turn18_bigaug_html_launch','turn18_bigaug_stdlib_extraction','turn18_bigaug_methods_data_training_read',
        'turn19_bigaug_results76_95','turn19_bigaug_results_discussion96_115_footnotes','turn19_bigaug_background26_44_recheck',
        'turn19_robust_qc_html_actual','turn19_primary_extraction_and_table_arithmetic','turn19_robust_qc_read18_49',
        'turn19_robust_qc_read50_81','turn19_robust_qc_methods82_110_and_spatial_return','turn19_robust_qc_methods111_134_refs','turn19_robust_qc_metric_actual']:
        assert records[key]['exit_code']==0,key
    sources=[Path(__file__),HERE/'PRIMARY_READING_AND_PROJECT_DECISIONS.md',HERE/'QC_AND_ACTION_NEXT_TRIAL_PREPARATION.md',
        HERE/'RECOVERED_TURN18_TOOL_OBSERVATIONS.json',HERE/'TURN19_TOOL_OBSERVATIONS_PART01.json',
        HERE/'sources_attempt01/bigaug_pmc_html.html',HERE/'sources_attempt01/bigaug_exact_doi.json',HERE/'sources_attempt01/receipt.json',
        HERE/'extraction_attempt01/blocks.json',HERE/'extraction_attempt01/receipt.json',
        HERE/'robust_qc_sources_attempt01/robust_qc_pmc_html.html',HERE/'robust_qc_sources_attempt01/receipt.json',
        HERE/'robust_qc_index_attempt01/receipt.json',HERE/'robust_qc_extraction_attempt01/receipt.json',
        HERE/'robust_qc_extraction_attempt01/blocks.json',HERE/'robust_qc_extraction_attempt01/tables.json',
        HERE/'robust_qc_extraction_attempt01/bigaug_tables.json',HERE/'robust_qc_extraction_attempt01/bigaug_table_arithmetic.json',
        HERE/'robust_qc_metric_audit_attempt01/receipt.json']
    assert sha(HERE/'sources_attempt01/bigaug_pmc_html.html')=='62f1d6a8f1835d61670b51738c5e0bfabe2d0b118b5c5399849ca88ecde287c8'
    assert sha(HERE/'robust_qc_sources_attempt01/robust_qc_pmc_html.html')=='5d1d53c0091c598722c56c74d2c690a358e072e6f175169665653c96e2d6d0f5'
    papers=[dict(title='Generalizing Deep Learning for Medical Image Segmentation to Unseen Domains via Deep Stacked Transformation',
        DOI='10.1109/TMI.2020.2973595',PMCID='PMC7393676',primary_HTML_URL='https://pmc.ncbi.nlm.nih.gov/articles/PMC7393676/',
        maintext_block_range_inclusive=[22,115],additional_footnotes=[120,121,133,135],selected_reference_blocks=[153,169,173,174,175,177,181,188],
        maintext_actual_reading_completed=True,all_references_read=False,newly_completed_in_this_stage=True,
        reading_tool_keys=['turn18_bigaug_methods_data_training_read','turn19_bigaug_background26_44_recheck','turn19_bigaug_results76_95','turn19_bigaug_results_discussion96_115_footnotes','turn19_bigaug_notes_refs'],
        caveats=['No figure pixel review or author code execution','ADAM/SGD ambiguity','Perturb table aggregate arithmetic mismatch','Small and large source experiments use different normalization']),
        dict(title='Robust machine learning segmentation for large-scale analysis of heterogeneous clinical brain MRI datasets',
        DOI='10.1073/pnas.2216399120',PMCID='PMC9992854',primary_HTML_URL='https://pmc.ncbi.nlm.nih.gov/articles/PMC9992854/',
        maintext_block_range_inclusive=[18,120],additional_data_availability_blocks=[132],selected_reference_blocks=[153,162,163,164,165,166,167,187],
        maintext_actual_reading_completed=True,all_references_read=False,newly_completed_in_this_stage=True,
        reading_tool_keys=['turn19_robust_qc_read18_49','turn19_robust_qc_read50_81','turn19_robust_qc_methods82_110_and_spatial_return','turn19_robust_qc_methods111_134_refs'],
        caveats=['Supplementary appendix and author code not read','QC metric positive class unresolved','66 vs 64 research scans','ICV correlation caption/maintext assignment inconsistent','Segmenter synthetic data and D/R real-image corruption pipelines differ'])]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],papers=papers,
        new_distinct_primary_maintexts_completed=2,prior_SynthSeg_TumorSynth_not_recounted=True,systematic_review_or_global_novelty_search=False,
        figure_pixels_reviewed=False,PDF_pages_read=0,independent_supplement_read=False,author_code_executed=False,
        downloaded_pretrained_weights=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,
        new_real_patient_outcomes=False,publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources])
    with (HERE/'READING_PROVENANCE.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,new_distinct_primary_maintexts_completed=2,neural_forwards=0,publication_claim_confirmed=False)),flush=True)
if __name__=='__main__':main()
