"""Independent SQLite arithmetic audit; does not clear the full crosswalk failure."""
from __future__ import annotations
import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02'
OUT=ROOT/'experiments/mc_rc_v2_nonpixel_identity'
PLAN=ROOT/'MC_RC_V2_CROSSWALK_FAILURE_FOLLOWUP_2026-10-02.md'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[]
    result=read(OUT/'attempt_01.json')
    db=sqlite3.connect(':memory:')
    db.executescript('CREATE TABLE mc(uid TEXT PRIMARY KEY, patient TEXT, study TEXT, description TEXT); CREATE TABLE legacy(uid TEXT PRIMARY KEY, patient TEXT); CREATE TABLE manifest(uid TEXT PRIMARY KEY); CREATE TABLE crosswalk(patient TEXT, mc_uid TEXT UNIQUE, old_uid TEXT UNIQUE);')
    for r in read(B/'series_attempt_01.response'):db.execute('INSERT INTO mc VALUES(?,?,?,?)',(r['SeriesInstanceUID'],r['PatientID'],r['StudyInstanceUID'],r.get('SeriesDescription','')))
    for r in read(ROOT/'literature/source_cache/vs_seg_official_inventory_2026-10-01/series.json'):db.execute('INSERT INTO legacy VALUES(?,?)',(r['SeriesInstanceUID'],r['PatientID']))
    lines=(B/'manifest_attempt_01.response').read_text(encoding='utf-8-sig').splitlines()
    for line in lines[lines.index('ListOfSeriesToDownload=')+1:]:
        if line.strip():db.execute('INSERT INTO manifest VALUES(?)',(line.strip(),))
    with (B/'overlap_attempt_01.response').open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):db.execute('INSERT INTO crosswalk VALUES(?,?,?)',(r['Patient ID'],r['VS-MC-RC Series Instance UID'],r['VS-SEG Series Instance UID']))
    counts={}
    for key,where in [('full','1=1'),('excluded_shared_patients',"substr(patient,1,7)='VS-SEG-'"),('candidate_nonoverlap_patients',"substr(patient,1,9)='VS-MC-RC-'")]:
        n=db.execute('SELECT COUNT(DISTINCT patient),COUNT(DISTINCT study),COUNT(*),SUM(substr(description,1,4)=\'_T2_\'),SUM(substr(description,1,4)=\'_T1_\'),COUNT(DISTINCT CASE WHEN substr(description,1,4)=\'_T2_\' THEN patient END) FROM mc WHERE '+where).fetchone()
        counts[key]=dict(zip(['patients','studies','series','T2_by_description_only','T1_by_description_only','patients_with_T2_description'],n))
    if counts!=result['counts']:errors.append('Independent SQL counts differ')
    qa={
      'api_not_manifest':db.execute('SELECT COUNT(*) FROM mc LEFT JOIN manifest ON mc.uid=manifest.uid WHERE manifest.uid IS NULL').fetchone()[0],
      'manifest_not_api':db.execute('SELECT COUNT(*) FROM manifest LEFT JOIN mc ON mc.uid=manifest.uid WHERE mc.uid IS NULL').fetchone()[0],
      'crosswalk_rows':db.execute('SELECT COUNT(*) FROM crosswalk').fetchone()[0],
      'crosswalk_MC_uid_and_patient_matches':db.execute('SELECT COUNT(*) FROM crosswalk c JOIN mc m ON c.mc_uid=m.uid AND c.patient=m.patient').fetchone()[0],
      'crosswalk_legacy_uid_matches':db.execute('SELECT COUNT(*) FROM crosswalk c JOIN legacy l ON c.old_uid=l.uid').fetchone()[0],
      'exact_uid_overlap':db.execute('SELECT COUNT(*) FROM mc JOIN legacy ON mc.uid=legacy.uid').fetchone()[0],
      'unknown_patient_patterns':db.execute("SELECT COUNT(*) FROM mc WHERE substr(patient,1,7)!='VS-SEG-' AND substr(patient,1,9)!='VS-MC-RC-'").fetchone()[0],
      'studies_with_multiple_patients':db.execute('SELECT COUNT(*) FROM (SELECT study FROM mc GROUP BY study HAVING COUNT(DISTINCT patient)>1)').fetchone()[0]}
    if qa!={'api_not_manifest':0,'manifest_not_api':0,'crosswalk_rows':8,'crosswalk_MC_uid_and_patient_matches':8,'crosswalk_legacy_uid_matches':0,'exact_uid_overlap':0,'unknown_patient_patterns':0,'studies_with_multiple_patients':0}:errors.append('Independent metadata QA differs')
    if result['complete'] or len(result['errors'])!=8 or any(not e.startswith('Crosswalk UID/patient join failed ') for e in result['errors']):errors.append('Original crosswalk failure not preserved')
    with (OUT/result['patient_roster_file']).open(encoding='utf-8',newline='') as f:roster=list(csv.DictReader(f))
    expected=db.execute('SELECT patient,COUNT(*),COUNT(DISTINCT study) FROM mc GROUP BY patient ORDER BY patient').fetchall()
    if [(r['patient'],int(r['series']),int(r['studies'])) for r in roster]!=expected:errors.append('Patient roster differs from independent SQL')
    for r in roster:
        if (r['exclude_shared_patient']=='True')!=r['patient'].startswith('VS-SEG-'):errors.append('Patient exclusion flag differs')
    proof={'verification_script_sha256':sha(__file__),'plan_sha256':sha(PLAN),'result_sha256':sha(OUT/'attempt_01.json'),'source_index_sha256':sha(B/'attempt_01.json'),'patient_roster_sha256':sha(OUT/result['patient_roster_file']),'scope':'independent nonpixel directory arithmetic only; retains failed legacy crosswalk','counts':counts,'qa':qa,'original_complete':result['complete'],'original_errors_retained':result['errors'],'full_crosswalk_certified':False,'native_T2_or_label_grid_certified':False,'scientific_independent_validation_patients':0,'errors':errors}
    (OUT/'independent_sqlite_verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proof[k] for k in ('scope','counts','qa','full_crosswalk_certified','native_T2_or_label_grid_certified','errors')},ensure_ascii=False,indent=2))
    return int(bool(errors))

if __name__=='__main__':raise SystemExit(main())
