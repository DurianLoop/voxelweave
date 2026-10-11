"""Register actual primary reading separately from byte extraction; bind finished observations."""
import sys,json,gzip,time,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    p=HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN30.json.gz';q=json.loads(gzip.decompress(p.read_bytes()));assert len(q['entries'])==37
    records={r['key']:r['actual_tool_return'] for r in q['entries']}
    def direct(key):
        r=records[key]
        if r.get('status')=='fulfilled':r=r['value']
        assert r['exit_code']==0 and 'session_id' not in r
        return r
    fetch=direct('resume30_two_html_fetch');audit=direct('resume30_table_audit_start');arc=direct('resume30_archive29_start')
    assert fetch['chunk_id']=='c485b9' and audit['chunk_id']=='7e3666' and arc['chunk_id']=='752221'
    dump(HERE/'ACTUAL_PRIMARY_FETCH_TERMINAL_TOOL.json',fetch)
    dump(HERE/'ACTUAL_TABLE_AUDIT_TERMINAL_TOOL.json',audit)
    dump(HERE/'ACTUAL_PREVIOUS_ARCHIVE_TERMINAL_TOOL.json',arc)
    def scope(key,ranges):
        v=direct(key);found={int(m) for m in re.findall(r'^([0-9]+) \[',v['output'],re.M)}
        required={i for lo,hi in ranges for i in range(lo,hi+1)};assert required<=found,(key,sorted(required-found))
        return dict(actual_tool_chunk=v['chunk_id'],store_key=key,read_index_ranges_inclusive=ranges,individual_command_truncation_present='Warning: truncated output' in v['output'])
    scopes={
        'vinn':[scope('resume30_readfirst_1',[(15,48)]),scope('resume30_readmethods_1',[(49,95)]),
                scope('resume30_readresults_0',[(96,127)]),scope('resume30_formula_and_poll_0',[(128,137)]),
                scope('resume30_readresults_1',[(137,175)]),scope('resume30_appendix_and_tables_0',[(176,199),(202,212)])],
        'lesion_ensemble':[scope('resume30_readfirst_0',[(20,50)]),scope('resume30_readmethods_0',[(51,86)])]}
    fetch_receipt=read(HERE/'sources_attempt01/receipt.json');assert fetch_receipt['complete'] and not fetch_receipt['errors']
    result=[]
    for r in fetch_receipt['records']:
        result.append(dict(key=r['key'],DOI=r['DOI'],PMCID=r['PMCID'],title=r['citation_title'],identity_verified=True,
            public_primary_maintext_actually_read=True,actual_reading_scopes=scopes[r['key']],source_binding=r['raw_response_gzip'],
            extracted_bindings=r['extraction_bindings'],figure_captions_read=True,figure_pixels_reviewed=False,
            author_code_retrieved_or_executed=False,external_referenced_maintexts_read=False,
            unreviewed=('VINN blocks200-201/Table5, 213 onward/Table9-16, footnotes and references' if r['key']=='vinn' else 'blocks87 onward/references, figure pixels, Docker/webapp and potential external supplements')))
    audit_receipt=read(HERE/'table_audit_attempt01/receipt.json');assert audit_receipt['complete'] and not audit_receipt['errors']
    assert audit_receipt['clinical_mean_endpoint_comparisons']==28 and audit_receipt['weighting_formula_cases']==5456
    assert [audit_receipt[k] for k in ['post_improved_endpoints','post_degraded_endpoints','post_tied_endpoints']]==[13,11,4]
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        path=ROOT.parent/name;assert sha(path)==expected;roots.append(dict(path='../'+name,bytes=path.stat().st_size,sha256=expected))
    static=[Path(__file__),HERE/'PROTOCOL.md',HERE/'TABLE_AUDIT_PROTOCOL.md',HERE/'audit_primary_tables.py',HERE/'fetch_and_extract_html.py',
        HERE/'PRIMARY_READING_AND_INNOVATION_DECISIONS.md',HERE/'NEXT_TRIAL_PREPARATION.md',HERE/'VISIBLE_DIALOGUE_TURN30.md',
        HERE/'RECEIVED_HANDOFF_TURN30.md',p,HERE/'sources_attempt01/receipt.json',HERE/'table_audit_attempt01/receipt.json',
        HERE/'ACTUAL_PRIMARY_FETCH_TERMINAL_TOOL.json',HERE/'ACTUAL_TABLE_AUDIT_TERMINAL_TOOL.json',HERE/'ACTUAL_PREVIOUS_ARCHIVE_TERMINAL_TOOL.json']
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=result,
        new_distinct_primary_maintexts_actually_read=2,new_distinct_abstract_only_read=0,
        previous_failed_HTTP_routes_retained=True,acquisition_and_extraction_original_reading_false_flags_unchanged=True,
        combined_functions_output_truncation_supplemented_by_separate128_137_read=True,
        actual_fetch_chunk=fetch['chunk_id'],actual_table_audit_chunk=audit['chunk_id'],
        ensemble_below_best_single_displayed_endpoints=18,post_mean_endpoint_counts=dict(improved=13,degraded=11,tied=4,total=28),
        all24_HTML_table_cells_reextracted_identically=True,exact_formula_checks5456=True,
        no_individual_patient_significance_inferred=True,new_patient_medical_effects=0,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        root_file_bindings=roots,source_bindings=[entry(v) for v in static],resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'READING_PROVENANCE.json',receipt)
    assert sum(v.stat().st_size for v in HERE.rglob('*') if v.is_file())<1_200_000
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['records','source_bindings','root_file_bindings']}),flush=True)
if __name__=='__main__':main()
