"""Bounded full MR ZIP transfer, DICOM header reads, and official label inventory."""
from __future__ import annotations
import hashlib
import io
import json
import math
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path

os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import numpy as np
import pydicom

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/mc_rc_three_patient_headers_2026-10-02'
DATA=ROOT/'data/mc_rc_three_patient_header_gate'
SELECTION=ROOT/'experiments/mc_rc_v2_nonpixel_identity/native_header_followup_selection.json'
PLAN=ROOT/'MC_RC_THREE_PATIENT_NATIVE_HEADER_PLAN_2026-10-02.md'
BASE='https://services.cancerimagingarchive.net/nbia-api/services/v1/getImage?'
TOTAL_CAP=300_000_000
lock=threading.Lock()
budget_used=0

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def now():return datetime.now(timezone.utc).isoformat()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')

def download(key,url,cap,attempt):
    global budget_used
    target=DATA/f'{key}_attempt_{attempt:02d}.zip';partial=target.with_suffix('.partial')
    r={'key':key,'url':url,'cap_bytes':cap,'started_utc':now()};count=0;started=time.monotonic()
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            response=opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-native-header-source-gate/1.0','Accept-Encoding':'identity'}),timeout=30)
        except urllib.error.HTTPError as exc:
            raw=exc.read(64_000);p=OUT/f'{key}_attempt_{attempt:02d}.error_response';p.write_bytes(raw)
            r.update(http_status=exc.code,error_response_file=p.name,error_response_sha256=sha(p));raise
        with response:
            r.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'),content_length=response.headers.get('Content-Length'))
            if response.status!=200:raise ValueError('Expected complete public archive response')
            if r['content_length'] and int(r['content_length'])>cap:raise ValueError('Declared archive exceeds fixed cap')
            with partial.open('xb') as f:
                while True:
                    if time.monotonic()-started>120:raise TimeoutError('Series overall transfer deadline exceeded')
                    chunk=response.read(min(1024*1024,cap-count+1))
                    if not chunk:break
                    with lock:
                        budget_used+=len(chunk)
                        over_total=budget_used>TOTAL_CAP
                    f.write(chunk);count+=len(chunk)
                    if count>cap or over_total:raise ValueError('Archive/global transfer cap exceeded')
            if r['content_length'] and count!=int(r['content_length']):raise ValueError('Incomplete declared archive')
        partial.rename(target)
        r.update(complete=True,file=target.relative_to(ROOT).as_posix(),bytes=count,sha256=sha(target))
    except Exception as exc:
        r.update(complete=False,error=f'{type(exc).__name__}: {exc}',bytes=count)
        if partial.exists():r.update(partial_file=partial.relative_to(ROOT).as_posix(),partial_sha256=sha(partial))
    r['finished_utc']=now();return r

def strings(value):
    if value is None:return []
    return [str(x) for x in value] if isinstance(value,(list,tuple,pydicom.multival.MultiValue)) else [str(value)]
def number(ds,key):
    x=ds.get(key)
    return float(x) if x is not None and str(x).strip() else None
def vector(ds,key):return [float(x) for x in ds.get(key,[])]

def header_record(ds,member):
    r={'zip_member':member.filename,'uncompressed_bytes':member.file_size,'sop_uid':str(ds.get('SOPInstanceUID','')),'patient':str(ds.get('PatientID','')),'series_uid':str(ds.get('SeriesInstanceUID','')),'study_uid':str(ds.get('StudyInstanceUID','')),'modality':str(ds.get('Modality','')),'frame_uid':str(ds.get('FrameOfReferenceUID','')),'rows':int(ds.Rows) if 'Rows' in ds else None,'columns':int(ds.Columns) if 'Columns' in ds else None,'frames':int(ds.get('NumberOfFrames',1)),'pixel_spacing':vector(ds,'PixelSpacing'),'slice_thickness':number(ds,'SliceThickness'),'spacing_between_slices':number(ds,'SpacingBetweenSlices'),'iop':vector(ds,'ImageOrientationPatient'),'ipp':vector(ds,'ImagePositionPatient'),'image_type':strings(ds.get('ImageType')),'mr_acquisition_type':str(ds.get('MRAcquisitionType','')),'sequence_name':str(ds.get('SequenceName','')),'scanning_sequence':strings(ds.get('ScanningSequence')),'sequence_variant':strings(ds.get('SequenceVariant')),'tr_ms':number(ds,'RepetitionTime'),'te_ms':number(ds,'EchoTime'),'derivation_description':str(ds.get('DerivationDescription','')),'series_description':str(ds.get('SeriesDescription','')),'transfer_syntax_uid':str(ds.file_meta.get('TransferSyntaxUID',''))}
    return r

def geometry(records,source):
    issues=[];missing=[];qualified=False
    if len(records)!=int(source['ImageCount']):issues.append('Object count differs from API ImageCount')
    if len({r['sop_uid'] for r in records})!=len(records) or any(not r['sop_uid'] for r in records):issues.append('Duplicate/missing SOPUID')
    if any(r['patient']!=source['PatientID'] or r['series_uid']!=source['SeriesInstanceUID'] for r in records):issues.append('Patient/series identity differs')
    if any(r['frames']!=1 for r in records):missing.append('Enhanced/multiframe geometry not interpreted')
    required=[r for r in records if r['rows'] and r['columns'] and len(r['pixel_spacing'])==2 and len(r['iop'])==6 and len(r['ipp'])==3 and r['slice_thickness'] is not None and r['frame_uid']]
    if len(required)!=len(records):missing.append('Required classic MR geometry field absent')
    result={'issues':issues,'pending_fields':missing,'header_qualified_candidate':False,'image_types':sorted(set(tuple(r['image_type']) for r in records)),'mr_acquisition_types':sorted(set(r['mr_acquisition_type'] for r in records)),'slice_thicknesses_mm':sorted(set(r['slice_thickness'] for r in records if r['slice_thickness'] is not None))}
    if missing or not records:return result
    iop=np.asarray([r['iop'] for r in records]);spacing=np.asarray([r['pixel_spacing'] for r in records]);positions=np.asarray([r['ipp'] for r in records])
    first=iop[0];normal=np.cross(first[:3],first[3:]);projection=positions@normal;order=np.argsort(projection);positions=positions[order];projection=projection[order]
    gaps=np.diff(projection);step=np.median(np.diff(positions,axis=0),axis=0);affine=np.eye(4);affine[:3,0]=first[3:]*spacing[0,0];affine[:3,1]=first[:3]*spacing[0,1];affine[:3,2]=step;affine[:3,3]=positions[0]
    predicted=positions[0]+np.arange(len(records))[:,None]*step;residual=float(np.max(np.linalg.norm(positions-predicted,axis=1)));variation=float(np.max(abs(gaps-np.median(gaps))))
    if len({(r['rows'],r['columns']) for r in records})!=1:issues.append('Rows/columns inconsistent')
    if len({r['frame_uid'] for r in records})!=1:issues.append('FrameOfReferenceUID inconsistent')
    if np.max(abs(iop-first))>1e-6:issues.append('Orientation inconsistent')
    if np.max(abs(spacing-spacing[0]))>1e-6:issues.append('PixelSpacing inconsistent')
    if max(abs(np.linalg.norm(first[:3])-1),abs(np.linalg.norm(first[3:])-1),abs(first[:3]@first[3:]))>1e-4:issues.append('IOP not orthonormal')
    if np.min(gaps)<=1e-4:issues.append('Duplicate/degenerate planes')
    if residual>.02 or variation>.02:issues.append('Nonuniform/non-affine slice geometry')
    native_spacing=[float(spacing[0,0]),float(spacing[0,1]),float(np.linalg.norm(step))]
    acq=all(r['mr_acquisition_type']=='3D' for r in records)
    original=all('ORIGINAL' in [x.upper() for x in r['image_type']] and 'DERIVED' not in [x.upper() for x in r['image_type']] for r in records)
    derivative=any(re.search(r'MPR|REFORMAT|LOCALIZER',str(r['series_description'])+' '+str(r['derivation_description'])+' '+' '.join(r['image_type']),re.I) for r in records)
    thin=max(native_spacing)<=1.5 and max(r['slice_thickness'] for r in records)<=1.5
    qualified=not issues and acq and original and not derivative and thin
    reasons=[]
    if not acq:reasons.append('MR Acquisition Type not uniformly3D')
    if not original:reasons.append('Not uniformly ORIGINAL without DERIVED')
    if derivative:reasons.append('MPR/Reformat/localizer evidence')
    if not thin:reasons.append('Native spacing or nominal SliceThickness >1.5mm')
    result.update(header_qualified_candidate=qualified,qualification_fail_reasons=reasons,native_spacing_rcz_mm=native_spacing,rows=records[0]['rows'],columns=records[0]['columns'],planes=len(records),actual_spacing_min_max_mm=[float(gaps.min()),float(gaps.max())],max_spacing_deviation_mm=variation,max_affine_position_residual_mm=residual,affine_rcz_lps=affine.tolist(),affine_rcz_ras=(np.diag([-1.,-1.,1.,1.])@affine).tolist(),ordered_zip_members=[records[int(i)]['zip_member'] for i in order],original_no_derived=original,acquisition_type_3D=acq,derivative_evidence=derivative,thin_geometry=thin)
    return result

def inspect_series(transfer,source,attempt):
    if not transfer['complete']:return {'source':source,'transfer':transfer,'headers_complete':False}
    records=[];sidecars=[]
    try:
        with zipfile.ZipFile(ROOT/transfer['file']) as z:
            for m in z.infolist():
                if m.is_dir():continue
                if m.file_size>10_000_000:raise ValueError('Unexpected large DICOM member')
                if not m.filename.lower().endswith('.dcm'):
                    sidecars.append({'path':m.filename,'bytes':m.file_size});continue
                with z.open(m) as f:ds=pydicom.dcmread(f,stop_before_pixels=True,force=False)
                records.append(header_record(ds,m))
        summary=geometry(records,source);p=OUT/f'{source["PatientID"]}_{source["SeriesInstanceUID"]}_headers_attempt_{attempt:02d}.json'
        write(p,{'source':source,'records':records,'summary':summary,'sidecars':sidecars,'MR_pixel_array_decoded':False})
        return {'source':source,'transfer':transfer,'headers_complete':True,'header_file':p.name,'header_sha256':sha(p),'summary':summary}
    except Exception as exc:return {'source':source,'transfer':transfer,'headers_complete':False,'header_error':f'{type(exc).__name__}: {exc}'}

def inspect_labels(transfer,attempt):
    if not transfer['complete']:return {'transfer':transfer,'directory_complete':False}
    try:
        members=[];metadata=[]
        with zipfile.ZipFile(ROOT/transfer['file']) as z:
            for m in z.infolist():
                if m.is_dir():continue
                members.append({'path':m.filename,'compressed_bytes':m.compress_size,'uncompressed_bytes':m.file_size,'crc32':f'{m.CRC:08x}'})
                if Path(m.filename).suffix.lower() in ('.xlsx','.csv','.txt','.md','.json') and m.file_size<=1_000_000:
                    raw=z.read(m);p=OUT/f'official_label_metadata_{len(metadata):02d}_attempt_{attempt:02d}{Path(m.filename).suffix}'
                    p.write_bytes(raw);metadata.append({'archive_path':m.filename,'file':p.name,'sha256':sha(p),'bytes':len(raw)})
        return {'transfer':transfer,'directory_complete':True,'members':members,'metadata':metadata,'label_arrays_decoded':False}
    except Exception as exc:return {'transfer':transfer,'directory_complete':False,'error':f'{type(exc).__name__}: {exc}'}

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True);DATA.mkdir(parents=True,exist_ok=True);attempt=len(list(OUT.glob('attempt_*.json')))+1
    selected=read(SELECTION);sources=sorted(selected['candidate_series'],key=lambda r:(r['PatientID'],r['StudyDate'],r['SeriesInstanceUID']))
    if selected['candidate_patient_ids']!=['VS-MC-RC-001','VS-MC-RC-002','VS-MC-RC-003'] or len(sources)!=9:raise ValueError('Frozen selection differs')
    page=read(ROOT/'literature/source_cache/mc_rc_official_2026-10-02/attempt_01.json')
    links=[u for u in page['responses'][0]['links'] if u.endswith('/VS-MC-RC-Segmentations_with_pathname_spreadsheet-Release2023.zip')]
    if len(links)!=1:raise ValueError('Exactly one authenticated label link required')
    ledger={'attempt':attempt,'started_utc':now(),'script_sha256':sha(__file__),'plan_sha256':sha(PLAN),'selection_sha256':sha(SELECTION),'scope':'full archive byte transfers; MR headers only and label directory/metadata only','MR_pixel_array_decoded':False,'label_arrays_decoded':False,'complete':False,'series':[]}
    write(OUT/f'attempt_{attempt:02d}.json',ledger)
    labels=download('official_labels',links[0],5_000_000,attempt);ledger['labels']=inspect_labels(labels,attempt);write(OUT/f'attempt_{attempt:02d}.json',ledger)
    def one(src):
        uid=src['SeriesInstanceUID'];cap=max(5_000_000,math.ceil(1.15*src['FileSize'])+1_000_000)
        transfer=download(src['PatientID']+'_'+uid,BASE+urllib.parse.urlencode({'SeriesInstanceUID':uid}),cap,attempt)
        return inspect_series(transfer,src,attempt)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(one,sources):
            ledger['series'].append(r);write(OUT/f'attempt_{attempt:02d}.json',ledger)
            print(json.dumps({'patient':r['source']['PatientID'],'uid':r['source']['SeriesInstanceUID'],'headers_complete':r['headers_complete'],'header_qualified_candidate':r.get('summary',{}).get('header_qualified_candidate'),'transfer_bytes':r['transfer']['bytes'],'error':r.get('header_error',r['transfer'].get('error'))},ensure_ascii=False),flush=True)
    ledger.update(finished_utc=now(),complete=all(r['headers_complete'] for r in ledger['series']) and ledger['labels']['directory_complete'],total_transfer_bytes=budget_used,header_qualified_series=sum(r.get('summary',{}).get('header_qualified_candidate',False) for r in ledger['series']),patient_performance_statistics_computed=False)
    write(OUT/f'attempt_{attempt:02d}.json',ledger)
    print(json.dumps({'complete':ledger['complete'],'total_transfer_bytes':budget_used,'header_qualified_series':ledger['header_qualified_series'],'label_directory_complete':ledger['labels']['directory_complete'],'metadata':ledger['labels'].get('metadata',[])},ensure_ascii=False),flush=True)
    return int(not ledger['complete'])

if __name__=='__main__':raise SystemExit(main())
