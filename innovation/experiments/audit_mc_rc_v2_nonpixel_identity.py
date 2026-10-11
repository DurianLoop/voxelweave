"""CPU-only full inventory join; exclude all previously seen VS-SEG patients."""
from __future__ import annotations
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02'
OLD=ROOT/'literature/source_cache/vs_seg_official_inventory_2026-10-01'
PLAN=ROOT/'MC_RC_V2_NONPIXEL_IDENTITY_PLAN_2026-10-02.md'
OUT=ROOT/'experiments/mc_rc_v2_nonpixel_identity'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1;errors=[]
    source=read(SOURCE/'attempt_01.json');src={r['key']:r for r in source['responses']}
    for r in src.values():
        if r.get('error') or r.get('http_status')!=200:raise ValueError('Incomplete public metadata '+r['key'])
        if sha(SOURCE/r['raw_file'])!=r['raw_sha256']:raise ValueError('Raw metadata hash differs')
    rows=read(SOURCE/src['series']['raw_file']);old=read(OLD/'series.json')
    old_index=read(OLD/'index.json')
    if next(r for r in old_index if r['name']=='series')['sha256']!=sha(OLD/'series.json'):raise ValueError('Legacy series metadata differs')
    with (SOURCE/src['overlap']['raw_file']).open(encoding='utf-8-sig',newline='') as f:overlap=list(csv.DictReader(f))
    lines=(SOURCE/src['manifest']['raw_file']).read_text(encoding='utf-8-sig').splitlines()
    marker=lines.index('ListOfSeriesToDownload=');manifest=[s.strip() for s in lines[marker+1:] if s.strip()]
    if any(not re.fullmatch(r'\d+(?:\.\d+)+',s) for s in manifest):errors.append('Manifest contains non-UID lines')
    uids=[r['SeriesInstanceUID'] for r in rows];byuid={r['SeriesInstanceUID']:r for r in rows}
    oldbyuid={r['SeriesInstanceUID']:r for r in old};oldpatients={r['PatientID'] for r in old}
    if len(byuid)!=len(rows):errors.append('Duplicate MC-RC UID')
    if len(set(manifest))!=len(manifest):errors.append('Duplicate manifest UID')
    if set(uids)!=set(manifest):errors.append('Actual API/manifest UID sets differ')
    patients=defaultdict(list);studies=defaultdict(set)
    for r in rows:
        patients[r['PatientID']].append(r);studies[r['StudyInstanceUID']].add(r['PatientID'])
        if r.get('Collection')!='Vestibular-Schwannoma-MC-RC' or r.get('Modality')!='MR':errors.append('Foreign collection/modality')
        if r.get('LicenseURI')!='https://creativecommons.org/licenses/by/4.0/':errors.append('Metadata license differs')
    if any(len(v)!=1 for v in studies.values()):errors.append('One study assigned to multiple patients')
    shared=sorted(p for p in patients if p.startswith('VS-SEG-'))
    novel=sorted(p for p in patients if p.startswith('VS-MC-RC-'))
    unknown=sorted(set(patients)-set(shared)-set(novel))
    if unknown:errors.append('Unknown patient ID rule')
    if not set(shared)<=oldpatients:errors.append('VS-SEG-prefix patient absent from old full inventory')
    if set(novel)&oldpatients:errors.append('Candidate ID collides with legacy patient')
    mapped=[]
    for r in overlap:
        left=byuid.get(r['VS-MC-RC Series Instance UID']);right=oldbyuid.get(r['VS-SEG Series Instance UID'])
        ok=left is not None and right is not None and left['PatientID']==r['Patient ID']==right['PatientID']
        if not ok:errors.append('Crosswalk UID/patient join failed '+r['Patient ID'])
        mapped.append({'patient':r['Patient ID'],'mc_rc_uid':r['VS-MC-RC Series Instance UID'],'vs_seg_uid':r['VS-SEG Series Instance UID'],'both_uid_patient_joins_valid':ok,'mc_rc_description':left.get('SeriesDescription') if left else None})
    if len(overlap)!=8:errors.append('Published eight-series crosswalk count differs')
    if len(shared)!=58 or len(novel)!=102 or len(patients)!=160 or len(rows)!=487 or len(studies)!=427:errors.append('V2/API/source patient-study-series counts differ')
    manifest_path=OUT/f'patient_roster_attempt_{attempt:02d}.csv'
    fields=['patient','exclude_shared_patient','series','studies','T2_by_description_only','T1_by_description_only']
    patient_rows=[]
    with manifest_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for p in sorted(patients):
            rs=patients[p];entry={'patient':p,'exclude_shared_patient':p in shared,'series':len(rs),'studies':len({r['StudyInstanceUID'] for r in rs}),'T2_by_description_only':sum(str(r.get('SeriesDescription','')).startswith('_T2_') for r in rs),'T1_by_description_only':sum(str(r.get('SeriesDescription','')).startswith('_T1_') for r in rs)}
            w.writerow(entry);patient_rows.append(entry)
    eligible=[r for r in rows if r['PatientID'] in novel]
    groups={name:rs for name,rs in [('full',rows),('excluded_shared_patients',[r for r in rows if r['PatientID'] in shared]),('candidate_nonoverlap_patients',eligible)]}
    counts={key:{'patients':len({r['PatientID'] for r in rs}),'studies':len({r['StudyInstanceUID'] for r in rs}),'series':len(rs),'T2_by_description_only':sum(str(r.get('SeriesDescription','')).startswith('_T2_') for r in rs),'T1_by_description_only':sum(str(r.get('SeriesDescription','')).startswith('_T1_') for r in rs),'patients_with_T2_description':len({r['PatientID'] for r in rs if str(r.get('SeriesDescription','')).startswith('_T2_')})} for key,rs in groups.items()}
    result={'attempt':attempt,'complete':not errors,'script_sha256':sha(__file__),'plan_sha256':sha(PLAN),'source_index_sha256':sha(SOURCE/'attempt_01.json'),'old_inventory_sha256':sha(OLD/'series.json'),'scope':'nonpixel identity/version audit; zero native geometry/label-space/performance qualifications','counts':counts,'manifest_count':len(manifest),'manifest_and_api_identical_uid_set':set(manifest)==set(uids),'legacy_exact_uid_intersection':len(set(uids)&set(oldbyuid)),'crosswalk':mapped,'excluded_shared_patients':shared,'candidate_nonoverlap_patients':novel,'unknown_patient_id_rules':unknown,'candidate_series_metadata':eligible,'release_dates':dict(Counter(str(r.get('DateReleased')) for r in rows)),'candidate_manufacturers':dict(Counter(str(r.get('Manufacturer')) for r in eligible)),'patient_roster_file':manifest_path.name,'patient_roster_sha256':sha(manifest_path),'scientific_independent_validation_patients':0,'new_native_T2_headers_verified':0,'patient_pixels_read':False,'errors':errors}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('complete','counts','manifest_count','manifest_and_api_identical_uid_set','legacy_exact_uid_intersection','release_dates','candidate_manufacturers','errors')},ensure_ascii=False,indent=2))
    return int(bool(errors))

if __name__=='__main__':raise SystemExit(main())
