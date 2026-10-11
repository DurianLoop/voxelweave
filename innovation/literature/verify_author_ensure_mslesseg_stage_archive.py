"""Verify static author/fulltext/metadata/toy evidence; exclude live inference."""
from __future__ import annotations
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'literature/source_cache'
BODY=CACHE/'author_repo_and_mslesseg_2026-10-02'
MANIFEST=CACHE/'author_ensure_mslesseg_stage_archive_2026-10-02.json'
EVIDENCE=CACHE/'author_ensure_mslesseg_reading_anchors_2026-10-02.json'
EXPECTED='061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[];anchors=[]
    paragraphs={int(m[1]):m[2] for m in re.finditer(r'^\[(\d{3})\] (.*?)(?=^\[\d{3}\]|\Z)',
                    (BODY/'ensure_long_attempt_01_maintext.txt').read_text(encoding='utf-8'),re.M|re.S)}
    for i,literal in [(60,'ignoring its dependence on'),(62,'\\approx'),(63,'matrix square root'),
                      (129,'computing their average'),(164,'nine volunteers'),(171,'fixed for each image'),
                      (218,'fully sampled center'),(228,'impossible to realize an unbiased estimate'),(229,'fixed during the training process')]:
        if literal not in paragraphs[i]:errors.append(f'ENSURE anchor absent {i}')
        anchors.append({'source':'ensure_long','paragraph':i,'literal':literal,'source_sha256':sha(BODY/'ensure_long_attempt_01_maintext.txt')})
    ms=read(BODY/'mslesseg_attempt_01_paragraphs.json')
    for i,literal in [(7,'53 patients'),(9,'MNI152'),(11,'registered FLAIR images'),(16,'same masks used to create'),(19,'54 to 77')]:
        if literal not in ms[i]['text']:errors.append(f'MSLesSeg anchor absent {i}')
        anchors.append({'source':'mslesseg','paragraph':i,'literal':literal,'source_sha256':sha(BODY/'mslesseg_attempt_01_paragraphs.json')})
    xml=ET.parse(BODY/'mslesseg_jats_attempt_01.response').getroot()
    dois=[(x.text or '').strip().lower() for x in xml.findall('.//article-id') if x.get('pub-id-type')=='doi']
    if '10.1038/s41597-025-05250-y' not in dois or xml.find('.//body') is None:errors.append('MSLesSeg certified body/DOI absent')
    epmc=read(BODY/'ensure_tmi_epmc_attempt_01.response')
    matches=[r for r in epmc['resultList']['result'] if r.get('doi','').lower()=='10.1109/tmi.2022.3224359' and r.get('pmcid')=='PMC10210546']
    if len(matches)!=1:errors.append('ENSURE long exact DOI/PMCID certification differs')
    for filename,literal in [('kuestner_pinned_readme_attempt_01.response','10.1002/mrm.30030'),
                              ('kuestner_train_attempt_01.response','epistemic_uncertainty = np.mean(y ** 2, axis=0) - y_ensemble ** 2'),
                              ('kuestner_ensemble_dataset_transforms_py_attempt_01.response',"fnum = ''.join([n for n in sample['fname'] if n.isdigit()])"),
                              ('kuestner_ensemble_models_losses_py_attempt_01.response','sigma = torch.exp(log_sigma) + var_eps')]:
        if literal not in (BODY/filename).read_text(encoding='utf-8'):errors.append('Author code anchor absent: '+filename)
        anchors.append({'source':'kuestner_author_code','file':filename,'literal':literal,'source_sha256':sha(BODY/filename)})
    checks=[(CACHE/'author_material_and_ms_sources_2026-10-02/attempt_01.json','search_author_material_and_ms_sources_2026_10_02.py'),
            (BODY/'attempt_01.json','fetch_author_repo_and_mslesseg_2026_10_02.py'),
            (BODY/'public_page_attempt_01.json','read_public_author_pages_2026_10_02.py'),
            (BODY/'followup_attempt_01.json','fetch_author_source_followup_2026_10_02.py'),
            (BODY/'pinned_code_attempt_01.json','fetch_kuestner_pinned_code_2026_10_02.py')]
    rows=0
    for path,script in checks:
        data=read(path)
        if data['script_sha256']!=sha(ROOT/'literature'/script):errors.append('Source script changed: '+script)
        for row in data.get('sources',data.get('responses',[])):
            rows+=1
            if 'raw_file' in row and sha(path.parent/row['raw_file'])!=row['raw_sha256']:errors.append('Raw source differs: '+row['key'])
            for field in ('maintext','paragraph'):
                if field+'_file' in row and sha(path.parent/row[field+'_file'])!=row[field+'_sha256']:errors.append('Extraction differs: '+row['key'])
    pins=read(BODY/'public_page_attempt_01.json')['public_html_pins']
    if pins.get('midas-tum/recon_uncertainty')!='ce0e6ede3682a6901bfdd6ddc85b44ef28e72f3a':errors.append('Kuestner commit differs')
    metadata=ROOT/'experiments/mslesseg_scan_metadata_gate'
    meta_proof=read(metadata/'independent_metadata_header_verification.json')
    header=CACHE/'mslesseg_raw_t2_headers_2026-10-02'
    hdr=read(header/'attempt_01.json');alternate=read(header/'schannel_attempt_01.json')
    if meta_proof['errors'] or meta_proof['header_result_sha256']!=sha(header/'attempt_01.json') or meta_proof['metadata_result_sha256']!=sha(metadata/'attempt_01.json'):errors.append('Independent header/metadata proof differs')
    if meta_proof['verification_script_sha256']!=sha(ROOT/'experiments/verify_mslesseg_scan_metadata_and_headers.py'):errors.append('Metadata verifier changed')
    if hdr['script_sha256']!=sha(ROOT/'literature/read_mslesseg_raw_t2_headers_2026_10_02.py'):errors.append('Header retrieval script changed')
    if alternate['script_sha256']!=sha(ROOT/'literature/read_mslesseg_seven_headers_schannel_2026_10_02.py') or alternate['original_source_sha256']!=sha(header/'attempt_01.json'):errors.append('Alternative scope/script differs')
    if sorted(r['path'] for r in alternate['records'])!=sorted(r['path'] for r in hdr['records'] if not r['header_complete']):errors.append('Alternative failure set differs')
    for row in alternate['requests']:
        for prefix in ('headers',''):
            field=prefix+'_file' if prefix else 'file';digest=prefix+'_sha256' if prefix else 'sha256'
            if field in row and sha(header/row[field])!=row[digest]:errors.append('Alternative raw log differs')
    toy=ROOT/'experiments/mask_dependent_action_ranking_cpu';result=read(toy/'attempt_01.json');proof=read(toy/'independent_fraction_verification.json')
    if not result['complete'] or result['errors'] or proof['errors'] or proof['source_sha256']!=sha(toy/'attempt_01.json'):errors.append('Toy independent result/proof differs')
    if result['script_sha256']!=sha(ROOT/'experiments/mask_dependent_action_ranking_cpu.py') or proof['verification_script_sha256']!=sha(ROOT/'experiments/verify_mask_dependent_action_ranking_cpu.py'):errors.append('Toy script differs')
    for data,plan in [(result,'MASK_DEPENDENT_ACTION_RANKING_CPU_PLAN_2026-10-02.md'),(hdr,'MSLESSEG_SCAN_METADATA_AND_HEADER_PLAN_2026-10-02.md'),(alternate,'MSLESSEG_SEVEN_HEADER_SCHANNEL_FOLLOWUP_PLAN_2026-10-02.md')]:
        if data['plan_sha256']!=sha(ROOT/plan):errors.append('Prewritten plan differs: '+plan)
    contract=ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'
    if sha(contract)!=EXPECTED:errors.append('Frozen main contract differs')
    frozen=0
    for row in read(contract)['files']:
        if Path(row['path']).suffix in ('.md','.py'):
            if sha(ROOT.parent/row['path'])!=row['sha256']:errors.append('Frozen main code/protocol differs: '+row['path'])
            frozen+=1
    evidence={'scope':'method/data/code reading anchors; no visual/equation reproduction certification','anchors':anchors}
    if '--write' in sys.argv:EVIDENCE.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif not EVIDENCE.exists() or read(EVIDENCE)!=evidence:errors.append('Reading evidence differs')
    files={EVIDENCE}
    for folder in ('author_material_and_ms_sources_2026-10-02','author_repo_and_mslesseg_2026-10-02','mslesseg_public_zip_metadata_2026-10-02','mslesseg_raw_t2_headers_2026-10-02'):
        files.update(p for p in (CACHE/folder).rglob('*') if p.is_file())
    files.update(p for base in (metadata,toy) for p in base.rglob('*') if p.is_file())
    for pattern in ('MSLESSEG_*_2026-10-02.md','MASK_DEPENDENT_ACTION_RANKING_CPU_*_2026-10-02.md','ACTION_BENEFIT_INNOVATION_FOLLOWUP_2026-10-02.md','SESSION_*AUTHOR_ENSURE_MSLESSEG*_2026-10-02.md'):
        files.update(ROOT.glob(pattern))
    files.update((ROOT/'literature').glob('2026-10-02_author*.md'))
    scripts=['README.md','USER_PROVIDED_HANDOFF_AUTHOR_MATERIAL_2026-10-02.md','SESSION_ARCHIVE_VERIFICATION_AUTHOR_ENSURE_MSLESSEG_2026-10-02.json','literature/2026-10-02_author_material_and_ms_source_plan.md','literature/2026-10-02_author_source_adaptive_followup.md',
             'literature/verify_author_ensure_mslesseg_stage_archive.py','experiments/audit_mslesseg_scan_metadata.py',
             'experiments/verify_mslesseg_scan_metadata_and_headers.py','experiments/mask_dependent_action_ranking_cpu.py','experiments/verify_mask_dependent_action_ranking_cpu.py',
             'literature/inventory_mslesseg_public_zips_2026_10_02.py','literature/read_mslesseg_raw_t2_headers_2026_10_02.py',
             'literature/read_mslesseg_seven_headers_schannel_2026_10_02.py']+['literature/'+s for _,s in checks]
    files.update(ROOT/p for p in scripts)
    observation=CACHE/'author_ensure_mslesseg_queue_observation_2026-10-02.json'
    if observation.exists():files.add(observation)
    entries=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]
    manifest={'scope':'static fulltext/author code/metadata/header/toy audit; excludes live inference',
              'new_primary_bodies':2,'new_PDFs':0,'author_repo_paper_body_obtained':False,'reading_anchors':len(anchors),
              'source_request_rows':rows,'raw_T2_attempted':len(hdr['records']),'raw_T2_headers_verified':meta_proof['headers_verified'],
              'raw_T2_headers_unretrieved':meta_proof['unretrieved_headers'],'Schannel_download_bytes':alternate['transferred_range_bytes'],
              'synthetic_risks':proof['risks_checked'],'synthetic_pairs':proof['pairs_checked'],'synthetic_strict_reversals':proof['strict_pair_ranking_reversals'],
              'main_contract_sha256':EXPECTED,'main_frozen_code_and_protocol_files_checked':frozen,'scientific_independent_patients':0,'files':entries}
    if '--write' in sys.argv:MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif not MANIFEST.exists() or read(MANIFEST)!=manifest:errors.append('Static stage manifest differs')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'}|{'files':len(entries),'bytes':sum(r['bytes'] for r in entries),'errors':errors},ensure_ascii=False,indent=2))
    return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
