"""Static source/label/reading evidence audit; does not inspect live model scores."""
from __future__ import annotations
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'literature/mc_rc_anchor_stage_archive_manifest_2026-10-03.json'
def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    digest = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):
            digest.update(block)
    return digest.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    errors, files = [], {Path(__file__),ROOT/'README.md'}
    def require(ok,why):
        if not ok:
            errors.append(why)
    def match(p,expected,why):
        p = Path(p).resolve()
        valid = p.is_relative_to(ROOT) and p.is_file()
        require(valid,'Missing/outside archive ' + why)
        if valid:
            require(sha(p)==expected,'Hash differs ' + why)
            files.add(p)
    headers_dir = ROOT/'literature/source_cache/mc_rc_007_010_native_headers_2026-10-02'
    labels_dir = ROOT/'experiments/mc_rc_007_010_native_label_gate'
    header, label, source_proof = read(headers_dir/'attempt_01.json'),read(labels_dir/'attempt_01.json'),read(labels_dir/'independent_raw_geometry_grid_verification.json')
    match(ROOT/'literature/download_mc_rc_007_010_native_headers_2026_10_02.py',header['script_sha256'],'header producer')
    match(ROOT/'MC_RC_007_010_SOURCE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md',header['plan_sha256'],'source contract')
    match(ROOT/'experiments/audit_mc_rc_007_010_label_grid.py',label['script_sha256'],'label producer')
    match(ROOT/'experiments/audit_mc_rc_three_patient_label_grid.py',label['grid_helper_sha256'],'grid helper')
    match(headers_dir/'attempt_01.json',label['header_result_sha256'],'header/label lineage')
    match(ROOT/'experiments/verify_mc_rc_007_010_native_label_gate.py',source_proof['verification_script_sha256'],'source verifier')
    match(labels_dir/'attempt_01.json',source_proof['label_result_sha256'],'source proof result')
    match(headers_dir/'attempt_01.json',source_proof['header_result_sha256'],'source proof headers')
    selection = ROOT/'experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json'
    match(selection,header['selection_sha256'],'frozen seven roster')
    expected = {r['source']['SeriesInstanceUID']:r['source'] for r in read(selection)['next_batch_series']}
    require({r['source']['SeriesInstanceUID']:r['source'] for r in header['series']}==expected and len(expected)==7,'Fixed-seven exact API roster differs')
    require(header['complete'] and label['complete'] and label['source_preflight_series_passed']==6 and label['source_preflight_patients_with_a_passing_series']==3,'Source/label complete scope differs')
    require(source_proof['errors']==[] and source_proof['counts']['raw_DICOM_objects_checked']==527 and source_proof['counts']['label_arrays_checked']==7,'Independent source scope differs')
    require(label['array_nominal_total_bytes']==615471104 and label['label_ZIP_member_bytes']==2308969 and not label['MR_pixel_arrays_decoded'] and source_proof['scientific_independent_validation_patients']==0,'Source resources/scientific scope differs')
    for row in header['series']:
        match(ROOT/row['transfer']['file'],row['transfer']['sha256'],'raw ZIP')
        match(headers_dir/row['header_file'],row['header_sha256'],'all native headers')
    for row in label['series']:
        match(ROOT/row['label_file'],row['label_sha256'],'all seven label payloads')
        require(row['label_inspection_complete'] and row['grid']['same_native_grid'] and row['label_is_binary'],'All-seven label/grid coverage differs')
        if 'MPR' in row['description']:
            require(not row['header_and_label_grid_preflight_passed'],'MPR rejection lost')
    visibility_dir = ROOT/'experiments/mc_rc_label_anchor_visibility'
    result, contract, proof = read(visibility_dir/'attempt_01.json'),read(visibility_dir/'run_contract.json'),read(visibility_dir/'independent_label_phase_verification.json')
    match(visibility_dir/'run_contract.json',result['run_contract_sha256'],'label coverage contract')
    for entry in contract['files']:
        match(ROOT/entry['path'],entry['sha256'],'coverage input ' + entry['path'])
    match(ROOT/'experiments/verify_mc_rc_label_anchor_visibility.py',proof['verification_script_sha256'],'label coverage verifier')
    match(visibility_dir/'attempt_01.json',proof['result_sha256'],'coverage verification result')
    require(contract['accepted_series']==15 and contract['excluded_series']==9 and len(contract['patients'])==8 and contract['phases']==[0,1,2,3],'Fixed coverage roster differs')
    require(result['complete'] and result['errors']==[] and len(result['series'])==15 and len(result['patients'])==8 and len(result['excluded_sources'])==9,'Coverage completeness differs')
    require(proof['errors']==[] and proof['counts']['foreground_coordinates_checked']==787030 and proof['counts']['series']==15 and proof['counts']['patients']==8,'Independent label coordinate coverage differs')
    require(not result['gpu_used'] and not result['MR_pixels_decoded'] and result['neural_networks_executed']==0 and result['scientific_independent_validation_patients']==0 and not result['publication_claim_confirmed'],'Label diagnostic promoted to model/claim')
    for row in result['series']:
        match(ROOT/row['component_file'],row['component_sha256'],'component artifact')
        for connectivity in ('6','26'):
            require(row['topology'][connectivity]['phases'][0]['anchor_absent_components']==0,'Phase0 counterevidence lost')
            require(all(p['largest_component_anchor_absent'] is False for p in row['topology'][connectivity]['phases']),'Largest component visibility changed')
    require([sum(r['topology']['26']['phases'][p]['anchor_absent_components'] for r in result['series']) for p in range(4)]==[0,1,1,1],'Prespecified phase sensitivity differs')
    source_dir = ROOT/'literature/source_cache/anchor_visibility_fulltexts_2026-10-03'
    acquisition, reading = read(source_dir/'attempt_01.json'),read(source_dir/'reading_provenance.json')
    match(ROOT/'literature/fetch_anchor_visibility_fulltexts_2026_10_03.py',acquisition['script_sha256'],'fulltext retrieval producer')
    match(ROOT/'literature/2026-10-03_anchor_visibility_fulltext_selection.md',acquisition['plan_sha256'],'fulltext selection')
    match(source_dir/'attempt_01.json',reading['acquisition_index_sha256'],'read/acquisition lineage')
    require(reading['new_public_fulltexts_read']==2 and len(reading['papers'])==2,'Reading denominator differs')
    for paper in acquisition['papers']:
        xml_path = source_dir/paper['raw_file']
        match(xml_path,paper['raw_sha256'],'fulltext XML')
        match(source_dir/paper['text_file'],paper['text_sha256'],'extracted paragraphs')
        root = ET.parse(xml_path).getroot()
        article = root if root.tag=='article' else root.find('.//article')
        require(article is not None and article.find('body') is not None,'Fulltext body missing')
        if article is not None:
            require(paper['expected_doi'].lower() in [''.join(x.itertext()).lower() for x in article.findall('.//article-id') if x.get('pub-id-type')=='doi'],'Fulltext DOI differs')
        recorded = next(r for r in reading['papers'] if r['doi']==paper['expected_doi'])
        require(recorded['actual_reading_completed'] and recorded['paragraphs_read']==paper['paragraphs'] and recorded['paragraph_range_zero_based']==[0,paper['paragraphs']-1] and not recorded['supplementary_read'] and not recorded['figures_visually_inspected'],'Actual reading scope differs')
    for row in reading['existing_PDF_method_pages_rechecked']:
        match(ROOT/row['path'],row['sha256'],'existing method page reread')
    search_dir = ROOT/'literature/source_cache/anchor_visibility_search_2026-10-03'
    search = read(search_dir/'attempt_01.json')
    match(ROOT/'literature/search_anchor_visibility_2026_10_03.py',search['script_sha256'],'index query producer')
    match(ROOT/'literature/2026-10-03_anchor_visibility_literature_plan.md',search['plan_sha256'],'index query plan')
    require([r['returned'] for r in search['responses']]==[15,0,14] and all('error' not in r for r in search['responses']),'Bounded index response scope differs')
    for response in search['responses']:
        match(search_dir/response['raw_file'],response['raw_sha256'],'raw index response')
    old = read(ROOT/'experiments/mc_rc_visible_joint_development_diagnostic/attempt_01.json')
    require(not old['fixed_visible_joint_diagnostic_gate_passed'] and not old['original_raw_development_gate_passed'],'Old failed policies restored')
    snapshot_path = ROOT/'literature/source_cache/mc_rc_anchor_queue_observation_2026-10-03.json'
    snapshot = read(snapshot_path)
    expected_contract = '061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5'
    require(snapshot['unified_exec_session']==83910 and snapshot['poll_returned_live'] and snapshot['contract_sha256']==expected_contract and not snapshot['dynamic_subcohort_statistics_computed'] and not snapshot['scientific_goal_complete'],'Progress-only queue snapshot differs')
    match(ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json',expected_contract,'original queue immutable contract')
    files.add(snapshot_path)
    for folder in (headers_dir,labels_dir,visibility_dir,source_dir,search_dir):
        files.update(p for p in folder.iterdir() if p.is_file())
    names = ['MC_RC_007_010_NATIVE_LABEL_RESULT_2026-10-03.md','MC_RC_LABEL_ANCHOR_VISIBILITY_PLAN_2026-10-03.md','MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md','MC_RC_NEW_VISIBLE_REPRESENTATION_PREPARATION_2026-10-03.md','SESSION_UPDATE_MC_RC_ANCHOR_2026-10-03.md','SESSION_VISIBLE_DIALOGUE_MC_RC_ANCHOR_2026-10-03.md','SESSION_IMPORTED_CHECKPOINT_MC_RC_007_010_2026-10-03.md','SESSION_HANDOFF_MC_RC_ANCHOR_QUEUE_ACTIVE_2026-10-03.md','literature/2026-10-03_anchor_visibility_fulltext_reading.md','literature/record_mc_rc_anchor_stage_2026_10_03.py','literature/verify_mc_rc_anchor_all_archives_2026_10_03.py']
    for name in names:
        p = ROOT/name
        require(p.is_file(),'Missing stage document ' + name)
        if p.is_file():
            files.add(p)
    manifest = dict(scope='static source, label diagnostic, fulltext reading and preparation; excludes live model outputs/dependency junctions',new_source_series=7,source_preflight_series=6,visibility_series=15,development_patients=8,foreground_coordinates_independently_checked=787030,new_public_fulltexts_read=2,new_PDFs=0,index_records=29,old_visible_policy_gate_passed=False,scientific_independent_validation_patients=0,publication_claim_confirmed=False,files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
    if '--write' in sys.argv:
        MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        require(MANIFEST.is_file() and read(MANIFEST)==manifest,'Anchor stage manifest stale')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'} | dict(files=len(files),errors=errors),ensure_ascii=False,indent=2))
    return int(bool(errors))
if __name__=='__main__':
    raise SystemExit(main())
