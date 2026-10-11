"""Freeze actual prose/table and source-reading coverage, preserving rendering limitations."""
import sys,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();receipt=HERE/'primary_xml_attempt01/receipt.json';v=read(receipt);assert v['complete']
    assert [r['blocks'] for r in v['records']]==[79,178,84]
    for r in v['records']:
        assert r['identity_verified']
        for b in r['source_bindings']:bind(b)
    result=dict(complete=True,errors=[],new_distinct_primary_maintexts_actually_read=3,blocks_actually_read=341,
        papers=[dict(key=r['key'],doi=r['doi'],pmcid=r['pmcid'],title=r['title'],unique_block_coverage=list(range(r['blocks'])),tables_read=r['tables']) for r in v['records']],
        data_tables_read=11,source_reading=dict(Phys_Seg_commit='7adc65d7b228b3a5702acfa9e6d0494d6b4c2dee',Phys_Seg_full_files=['README.md','Phys_Seg/network_architecture.py','Phys_Seg/utils.py'],
            Phys_Seg_predict_case_selected_lines_read=True,Phys_Seg_data_loading_full_read=False,Phys_Seg_training_loss_code_obtained=False,
            AMDU_commit='25225a808b6a363c48be705df0c6a06996bf035e',AMDU_full_files=['models.py','Unlearn/nnUNetTrainer_UnlearnPeriodicPerBatchKLDivConfusionLoss.py'],
            AMDU_base_gradient_optimizer_selected_ranges_read=True,AMDU_periodic_selected_ranges_read=True,AMDU_paper_adaptive_schedule_certified=False),
        actual_tool_keys=['turn41_read_core_1','turn41_dgtta_end_0','turn41_dgtta_end_1','turn41_missing_read_a_0','turn41_missing_read_a_1',
            'turn41_missing_read_b_0','turn41_missing_read_b_1','turn41_missing_peil_read_0','turn41_missing_peil_read_1','turn41_peil_end_0','turn41_peil_end_1','turn41_tables_and_math_0'],
        truncation_omissions_followed_up_in_shorter_ranges=True,figure_pixels_read=False,supplementary_PDF_read=False,PEIL_GIF_equations_fully_read=False,
        author_repository_executed=False,author_model_reproduced=False,source_index_hits_counted_as_maintexts=False,
        source_bindings=[entry(p) for p in [Path(__file__),receipt,HERE/'PRIMARY_FINDINGS_AND_NEXT.md',HERE/'PRIMARY_SELECTION.md',HERE/'source_diagnostics_attempt02/receipt.json']],
        publication_claim_confirmed=False,goal_status='active',resources=resource_guard())
    dump(HERE/'READING_PROVENANCE.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['papers','source_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
