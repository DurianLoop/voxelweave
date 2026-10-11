"""Static source/reading/identity provenance audit; excludes live inference data."""
from __future__ import annotations
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'literature/source_cache'
MANIFEST=CACHE/'action_crossmoda_stage_archive_2026-10-02.json'
ANCHORS=CACHE/'action_crossmoda_reading_anchors_2026-10-02.json'
EXPECTED='061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[];anchors=[]
    body=CACHE/'cobrai_crossmoda_public_2026-10-02'
    for key,doi,tests in [
        ('cobrai_jats','10.1002/nbm.70079',[(18,'Train'),(30,'K was set equal to R'),(32,'ACS only'),(34,'fully'),(35,'ground truth'),(35,'11'),(54,'KSPACE'),(61,'extreme corruption')]),
        ('kujawa_jats','10.3389/fncom.2024.1365727',[(14,'3.9 mm'),(22,'160 patients'),(22,'349 high and 14 low'),(26,'higher resolution'),(31,'58 patients'),(31,'8 series'),(32,'private validation'),(34,'no patient overlap'),(61,'DSC is less meaningful')])]:
        root=ET.parse(body/(key+'_attempt_01.response')).getroot()
        a=root if root.tag=='article' else root.find('.//article')
        ids=[(x.text or '').strip().lower() for x in a.find('front').findall('.//article-id') if x.get('pub-id-type')=='doi']
        if doi not in ids or a.find('body') is None:errors.append('Primary DOI/body differs: '+key)
        path=body/(key+'_attempt_01_paragraphs.json');paras=read(path)
        for number,literal in tests:
            if literal not in paras[number]['text']:errors.append(f'Reading anchor absent: {key} {number} {literal}')
            anchors.append({'source':key,'doi':doi,'paragraph':number,'literal':literal,'source_sha256':sha(path)})
    p=CACHE/'action_crossmoda_adaptive_2026-10-02';pdf=p/'crossmoda_author_pdf_attempt_01.pdf';txt=p/'crossmoda_author_pdf_attempt_01_layout.txt'
    pages=txt.read_text(encoding='utf-8').split(chr(12))
    if not pdf.read_bytes().startswith(b'%PDF-') or '10.1016/j.media.2026.104282' not in pages[0] or len([t for t in pages if t.strip()])!=26:errors.append('Source PDF identity/page count differs')
    for number,literal in [(4,'without manual'),(5,'Slice thickness'),(5,'Voxel volume'),(6,'0.4'),(6,'165'),(7,'CC BY-NC-SA'),(8,'350mm'),(23,'does not fully resolve')]:
        if literal not in pages[number-1]:errors.append(f'PDF page text anchor absent {number} {literal}')
        anchors.append({'source':'crossmoda_author_pdf','pdf_page':number,'literal':literal,'text_sha256':sha(txt),'pdf_sha256':sha(pdf)})
    provenance=read(p/'crossmoda_pdf_provenance_2026-10-02.json')
    if provenance['script_sha256']!=sha(ROOT/'literature/crossmoda_pdf_reading_provenance_2026_10_02.py') or provenance['source_pdf_sha256']!=sha(pdf):errors.append('PDF provenance script/source differs')
    for r in provenance['files']:
        if sha(p/r['path'])!=r['sha256']:errors.append('PDF extraction/render file differs: '+r['path'])
    if any(r['returncode']!=0 or not (p/r.get('png_file','absent')).is_file() for r in provenance['new_render_records']):errors.append('New PDF renders incomplete')
    official=CACHE/'mc_rc_official_2026-10-02/mc_rc_doi_attempt_01_visible_text.txt'
    text=official.read_text(encoding='utf-8')
    for literal in ('2026/06/04','133 series','58 patients','Version 2','CC BY 4.0'):
        if literal not in text:errors.append('Official data version/identity anchor absent '+literal)
        anchors.append({'source':'mc_rc_official_page','literal':literal,'source_sha256':sha(official)})
    checks=[('action_selection_and_crossmoda_2026-10-02','search_action_selection_and_crossmoda_2026_10_02.py','2026-10-02_action_selection_and_crossmoda_followup_plan.md'),
            ('action_crossmoda_adaptive_2026-10-02','fetch_action_crossmoda_adaptive_sources_2026_10_02.py','2026-10-02_action_crossmoda_adaptive_selection.md'),
            ('cobrai_crossmoda_public_2026-10-02','fetch_cobrai_crossmoda_public_2026_10_02.py','2026-10-02_cobrai_crossmoda_public_followup_plan.md'),
            ('mc_rc_official_2026-10-02','fetch_mc_rc_official_2026_10_02.py','2026-10-02_mc_rc_official_adaptive_plan.md'),
            ('mc_rc_v2_identity_2026-10-02','fetch_mc_rc_v2_identity_2026_10_02.py','../MC_RC_V2_NONPIXEL_IDENTITY_PLAN_2026-10-02.md')]
    request_rows=0;source_failures=[]
    for folder,script,plan in checks:
        b=CACHE/folder;data=read(b/'attempt_01.json')
        if data['script_sha256']!=sha(ROOT/'literature'/script) or data['plan_sha256']!=sha(ROOT/'literature'/plan):errors.append('Source script/plan differs '+folder)
        if 'helper_sha256' in data:
            helper='search_action_selection_and_crossmoda_2026_10_02.py' if folder=='action_crossmoda_adaptive_2026-10-02' else 'fetch_cobrai_crossmoda_public_2026_10_02.py'
            if data['helper_sha256']!=sha(ROOT/'literature'/helper):errors.append('Source helper differs '+folder)
        for r in data['responses']:
            request_rows+=1
            if r.get('error'):source_failures.append({'key':r['key'],'error':r['error'],'http_status':r.get('http_status')})
            for field in ('raw','paragraph','maintext','pdf'):
                if field+'_file' in r and sha(b/r[field+'_file'])!=r[field+'_sha256']:errors.append('Source/extraction differs '+r['key']+' '+field)
    identity=ROOT/'experiments/mc_rc_v2_nonpixel_identity';result=read(identity/'attempt_01.json');proof=read(identity/'independent_sqlite_verification.json')
    if result['complete'] or len(result['errors'])!=8 or proof['errors'] or proof['result_sha256']!=sha(identity/'attempt_01.json'):errors.append('Identity arithmetic proof or original failure differs')
    if result['script_sha256']!=sha(ROOT/'experiments/audit_mc_rc_v2_nonpixel_identity.py') or proof['verification_script_sha256']!=sha(ROOT/'experiments/verify_mc_rc_v2_nonpixel_identity.py'):errors.append('Identity script hashes differ')
    if result['plan_sha256']!=sha(ROOT/'MC_RC_V2_NONPIXEL_IDENTITY_PLAN_2026-10-02.md') or proof['plan_sha256']!=sha(ROOT/'MC_RC_V2_CROSSWALK_FAILURE_FOLLOWUP_2026-10-02.md'):errors.append('Identity plan hashes differ')
    if proof['full_crosswalk_certified'] or proof['native_T2_or_label_grid_certified']:errors.append('Pending source gate was incorrectly certified')
    if result['counts']['candidate_nonoverlap_patients']['patients']!=102 or result['counts']['candidate_nonoverlap_patients']['patients_with_T2_description']!=100:errors.append('Candidate counts differ')
    future=read(identity/'native_header_followup_selection.json')
    if future['status']!='prepared_not_executed' or future['source_result_sha256']!=sha(identity/'attempt_01.json') or future['candidate_patient_ids']!=['VS-MC-RC-001','VS-MC-RC-002','VS-MC-RC-003'] or len(future['candidate_series'])!=9:errors.append('Followup selection differs')
    contract=ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'
    if sha(contract)!=EXPECTED:errors.append('Frozen main contract changed')
    frozen=0
    for r in read(contract)['files']:
        if Path(r['path']).suffix in ('.md','.py'):
            if sha(ROOT.parent/r['path'])!=r['sha256']:errors.append('Frozen main code/protocol changed '+r['path'])
            frozen+=1
    evidence={'scope':'literal reading anchors only; visual/source qualification limits in report','anchors':anchors,'visual_pages_reviewed':[4,5,6,7,8,23],'Table1_closeup_reviewed':True,'pdf_page22_text_reviewed':True}
    if '--write' in sys.argv:ANCHORS.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif not ANCHORS.exists() or read(ANCHORS)!=evidence:errors.append('Reading anchors file differs')
    files={ANCHORS,Path(__file__),ROOT/'README.md',official}
    for folder,script,plan in checks:
        files.update(x for x in (CACHE/folder).rglob('*') if x.is_file());files.add(ROOT/'literature'/script);files.add((ROOT/'literature'/plan).resolve())
    files.update(x for x in identity.rglob('*') if x.is_file())
    files.update(ROOT/p for p in ['experiments/audit_mc_rc_v2_nonpixel_identity.py','experiments/verify_mc_rc_v2_nonpixel_identity.py','literature/crossmoda_pdf_reading_provenance_2026_10_02.py','literature/verify_action_crossmoda_all_archives_2026_10_02.py','literature/2026-10-02_cobrai_crossmoda_mc_rc_reading.md','USER_PROVIDED_HANDOFF_ACTION_CROSSMODA_2026-10-02.md','INNOVATION_DECISION_AFTER_COBRAI_CROSSMODA_2026-10-02.md'])
    files.update(ROOT.glob('SESSION_*ACTION_CROSSMODA*_2026-10-02.md'));files.update(ROOT.glob('MC_RC*_2026-10-02.md'))
    files.add(CACHE/'action_crossmoda_queue_observation_2026-10-02.json')
    entries=[{'path':x.relative_to(ROOT).as_posix(),'bytes':x.stat().st_size,'sha256':sha(x)} for x in sorted(files)]
    manifest={'scope':'static literature/nonpixel source arithmetic and known failure; excludes live inference','new_source_PDFs':1,'main_registered_PDFs_do_not_include_new_nested_source_PDF':29,'new_JATS_bodies':2,'source_request_rows':request_rows,'source_failures':source_failures,'reading_anchors':len(anchors),'metadata_patients':160,'official_prefix_nonoverlap_candidates':102,'T2_description_candidate_patients':100,'original_crosswalk_complete':False,'legacy_crosswalk_matches':0,'new_native_T2_headers_verified':0,'scientific_independent_validation_patients':0,'main_contract_sha256':EXPECTED,'frozen_code_and_protocol_files_checked':frozen,'files':entries}
    if '--write' in sys.argv:MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif not MANIFEST.exists() or read(MANIFEST)!=manifest:errors.append('Static stage manifest differs')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'}|{'files':len(entries),'errors':errors},ensure_ascii=False,indent=2))
    return int(bool(errors))

if __name__=='__main__':raise SystemExit(main())
