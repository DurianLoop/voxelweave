"""Current independently checked source qualification vs frozen historical roster."""
from __future__ import annotations
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_source_denominator_correction'
PLAN=ROOT/'MC_RC_SOURCE_DENOMINATOR_CORRECTION_PLAN_2026-10-03.md'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8')
 paths=[PLAN,Path(__file__),ROOT/'experiments/mc_rc_frozen_predicted_region_cpu/run_contract.json']
 initial=ROOT/'experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json'
 refined=initial.parent/'geometry_availability_attempt_01.json'
 p1=initial.parent/'independent_raw_geometry_grid_verification.json'
 follow=ROOT/'experiments/mc_rc_004_006_native_label_gate/resource_followup_attempt_01.json'
 p2=follow.parent/'independent_raw_geometry_grid_verification.json'
 final=ROOT/'experiments/mc_rc_007_010_native_label_gate/attempt_01.json'
 p3=final.parent/'independent_raw_geometry_grid_verification.json'
 a,b,c=read(p1),read(p2),read(p3)
 if a['errors'] or b['errors'] or c['errors']: raise ValueError('Source proof errors')
 for expected,path in [(a['first_label_result_sha256'],initial),(a['refined_result_sha256'],refined),(b['resource_followup_result_sha256'],follow),(c['label_result_sha256'],final)]:
  if sha(path)!=expected: raise ValueError('Source-proof hash lineage differs '+str(path))
 paths += [initial,refined,p1,follow,p2,final,p3]
 old=read(paths[2]); old_cases={r['uid']:r for r in old['cases']}
 raw=read(initial);raw_by={r['series_uid']:r for r in raw['series']}
 rows=[];case_records=[];excluded=[]
 groups=[(refined,a,'literature/source_cache/mc_rc_three_patient_headers_2026-10-02'),(follow,b,'literature/source_cache/mc_rc_004_006_native_headers_2026-10-02'),(final,c,'literature/source_cache/mc_rc_007_010_native_headers_2026-10-02')]
 for source,proof,folder in groups:
  d=read(source);verified={r['uid']:r for r in proof['series']}
  ledger_path=ROOT/folder/'attempt_01.json';ledger=read(ledger_path);paths.append(ledger_path)
  headers={r['source']['SeriesInstanceUID']:r for r in ledger['series']}
  for row in d['series']:
   uid=row.get('series_uid',row.get('uid'));v=verified[uid];qualified=v['source_preflight_passed']
   q=row['refined_header_and_label_grid_passed'] if source==refined else row['header_and_label_grid_preflight_passed']
   if bool(q)!=bool(qualified): raise ValueError('Source qualification vs proof differs '+uid)
   entry=dict(patient=row['patient'],uid=uid,description=row['description'],qualified=qualified,in_old_frozen_15=uid in old_cases,source_result=source.relative_to(ROOT).as_posix())
   rows.append(entry)
   if not qualified: excluded.append(entry);continue
   metadata=raw_by[uid] if source==refined else row
   h=headers[uid];hf=ROOT/folder/h['header_file'];zf=ROOT/h['transfer']['file'];lf=ROOT/metadata['label_file']
   for path,expected in [(hf,h['header_sha256']),(zf,h['transfer']['sha256']),(lf,metadata['label_sha256'])]:
    if sha(path)!=expected: raise ValueError('Authenticated source file differs '+str(path))
   paths += [hf,zf,lf]
   transform=row['grid_with_fitted_affine']['dicom_rcz_from_label_xyz'] if source==refined else row['grid']['dicom_rcz_from_label_xyz']
   if uid in old_cases:
    case=dict(old_cases[uid]);case.pop('component_file',None);case.pop('component_sha256',None)
   else:
    case=dict(patient=row['patient'],uid=uid,description=row['description'],study_uid=h['source']['StudyInstanceUID'],native_shape=metadata['dicom_shape_rcz'],native_spacing_rcz_mm=row['native_spacing_rcz_mm'],affine_rcz_ras=row['fitted_affine_rcz_ras'],ordered_zip_members=h['summary']['ordered_zip_members'],header_file=hf.relative_to(ROOT).as_posix(),header_sha256=h['header_sha256'],mr_zip_file=h['transfer']['file'],mr_zip_sha256=h['transfer']['sha256'],label_file=metadata['label_file'],label_sha256=metadata['label_sha256'])
   case.update(in_old_frozen_15=uid in old_cases,source_result=source.relative_to(ROOT).as_posix(),dicom_rcz_from_label_xyz=transform,expected_label_foreground_voxels=metadata['label_foreground_voxels'])
   case_records.append(case)
 case_records.sort(key=lambda r:(r['patient'],r['uid']))
 actual={r['uid'] for r in case_records};old_uids=set(old_cases)
 if len(rows)!=24 or len(actual)!=16 or len({r['patient'] for r in case_records})!=8 or len(actual-old_uids)!=1 or old_uids-actual: raise ValueError('Prespecified correction count differs')
 result=dict(created_utc=datetime.now(timezone.utc).isoformat(),scope='source-proof lineage and denominator correction; no pixel/label decoding',complete=True,errors=[],counts=dict(source_series=len(rows),qualified_series=len(actual),development_patients=8,excluded_or_pending=len(excluded),old_frozen_series=15,omitted_current_qualified_series=len(actual-old_uids)),all_source_qualification=rows,cases=case_records,omitted_uids=sorted(actual-old_uids),old_frozen_now_ineligible=sorted(old_uids-actual),MR_pixels_decoded=False,new_label_arrays_decoded=False,scientific_independent_validation_patients=0,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(paths))])
 OUT.mkdir(exist_ok=False)
 with (OUT/'attempt_01.json').open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(counts=result['counts'],omitted_uids=result['omitted_uids'],errors=result['errors'])))
if __name__=='__main__': main()
