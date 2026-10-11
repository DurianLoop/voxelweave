"""Independently check public raw bytes/tables, coverage and join qualifications."""
from __future__ import annotations
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
META=ROOT/'literature/source_cache/mslesseg_public_zip_metadata_2026-10-02'
HEAD=ROOT/'literature/source_cache/mslesseg_raw_t2_headers_2026-10-02'
OUT=ROOT/'experiments/mslesseg_scan_metadata_gate'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    inv=read(META/'attempt_01.json'); audit=read(OUT/'attempt_01.json'); heads=read(HEAD/'attempt_01.json')
    selection=read(HEAD/heads['selection_file']);errors=[]
    if heads['selection_sha256']!=sha(HEAD/heads['selection_file']):errors.append('Header selection differs')
    expected=sorted(m['path'] for a in inv['records'] if a['key']=='raw' for m in a['members'] if m['path'].endswith('_T2.nii.gz'))
    if expected!=[r['path'] for r in heads['records']] or expected!=[r['path'] for r in selection['members']]:errors.append('Not all frozen 117 raw T2 members attempted')
    raw_keys={tuple(re.fullmatch(r'(P\d+)/(T\d+)/.*',p).groups()) for p in expected}
    official={}
    with (META/'registered_metadata_03_attempt_01.csv').open(encoding='utf-8-sig',newline='') as f:
        for row in csv.reader(f,delimiter=';'):
            if row[0]=='Patient':continue
            official[(row[0],row[1])]={'thickness':row[8],'spacing':row[7]}
    counts=Counter(v['thickness'] for v in official.values())
    if dict(counts)!=audit['tables']['T2']['thickness_raw_counts']:errors.append('Official thickness counts differ')
    reg_keys=set()
    split_keys={}
    for rec in inv['records']:
        if rec['key']!='registered':continue
        for member in rec['members']:
            if not member['path'].endswith('_T2.nii.gz'):continue
            parts=member['path'].split('/');name=parts[-1]
            patient=re.match(r'(P\d+)_',name)[1]
            m=re.match(r'P\d+_(T\d+)_T2\.nii\.gz',name)
            k=(patient,m[1] if m else 'T1')
            reg_keys.add(k);split_keys.setdefault(parts[1],set()).add(k)
    if reg_keys!=set(official):errors.append('Official T2 CSV and registered keys differ')
    for name,keys in split_keys.items():
        s=audit['registered_splits'][name]
        if s['scans']!=len(keys) or s['patients']!=len({k[0] for k in keys}):errors.append('Split counts differ')
    if {tuple(k) for k in audit['differences']['raw_T2_without_registered']}!=raw_keys-reg_keys:errors.append('RAW-only key list differs')
    if {tuple(k) for k in audit['differences']['registered_T2_without_raw']}!=reg_keys-raw_keys:errors.append('Registered-only key list differs')
    total=0
    for req in heads['requests']:
        if 'file' not in req:
            if 'error' not in req:errors.append('Range without data or failure record')
            continue
        path=HEAD/req['file'];length=path.stat().st_size;total+=length
        if sha(path)!=req['sha256'] or length!=req['end']-req['start']+1:errors.append('Range bytes differ')
        if req['http_status']!=206 or req['content_range']!=f'bytes {req["start"]}-{req["end"]}/1295472528':errors.append('Range boundary differs')
    if total!=heads['transferred_range_bytes'] or total>16*1024*1024:errors.append('Transfer total differs/exceeds budget')
    joined=[]; spacings=[]; unknown_units=0;sform_max=0.
    for record in heads['records']:
        k=tuple(re.fullmatch(r'(P\d+)/(T\d+)/.*',record['path']).groups())
        row={'path':record['path'],'key':list(k),'csv':official.get(k),'registered_key_present':k in reg_keys,
             'header_complete':record['header_complete'],'error':record.get('error')}
        if record['header_complete']:
            path=HEAD/record['header_file'];raw=path.read_bytes()
            if sha(path)!=record['header_sha256'] or len(raw)!=record['header_bytes']:errors.append('Saved header differs')
            # A distinct NumPy byte parser, limited to header bytes; all observed headers are NIfTI-1.
            size=int(np.frombuffer(raw[:4],dtype='<i4')[0]);endian='<' if size==348 else '>'
            size=int(np.frombuffer(raw[:4],dtype=endian+'i4')[0])
            if size!=348 or len(raw)!=348 or raw[-4:]!=b'n+1\0':
                errors.append('Unexpected header format in independent verifier');joined.append(row);continue
            dims=np.frombuffer(raw[40:56],dtype=endian+'i2').tolist()
            pix=np.frombuffer(raw[76:108],dtype=endian+'f4').tolist()
            units=raw[123]&7;factor={1:1000.,2:1.,3:.001}.get(units)
            spacing=[v*factor for v in pix[1:4]] if factor is not None else None
            offset=float(np.frombuffer(raw[108:112],dtype=endian+'f4')[0])
            d=record['decoded']
            if offset<352 or d['shape']!=dims[1:dims[0]+1] or spacing!=d['spacing_mm']:errors.append('Independent geometry differs')
            if spacing:
                spacings.append(max(spacing))
                sform=int(np.frombuffer(raw[254:256],dtype=endian+'i2')[0])
                if sform>0:
                    affine=np.frombuffer(raw[280:328],dtype=endian+'f4').reshape(3,4).astype(float)
                    norms=(np.linalg.norm(affine[:,:3],axis=0)*factor).tolist()
                    err=max(abs(a-b) for a,b in zip(norms,spacing));sform_max=max(sform_max,err)
                    if max(abs(a-b) for a,b in zip(norms,d['sform_axis_norms_mm']))>1e-10:errors.append('Independent sform differs')
            else:unknown_units+=1
            row.update(shape=dims[1:dims[0]+1],spacing_mm=spacing,thin_grid_candidate=bool(spacing and max(spacing)<=1.5))
        joined.append(row)
    complete=sum(r['header_complete'] for r in joined);thin=sum(r.get('thin_grid_candidate',False) for r in joined)
    if complete!=heads['complete_headers'] or thin!=heads['thin_grid_candidates']:errors.append('Header summary differs')
    missing_csv=[r for r in joined if r['csv'] and r['csv']['thickness']=='NONE']
    proof={'scope':'public scan metadata and saved non-pixel header independent check; retrieval incompleteness retained',
           'verification_script_sha256':sha(__file__),'metadata_result_sha256':sha(OUT/'attempt_01.json'),
           'header_result_sha256':sha(HEAD/'attempt_01.json'),'inventory_source_sha256':sha(META/'attempt_01.json'),
           'raw_T2_attempted':len(joined),'headers_verified':complete,'unretrieved_headers':len(joined)-complete,
           'thin_grid_candidates_observed':thin,'unknown_units':unknown_units,'max_axis_spacing_min_mm':min(spacings),
           'max_axis_spacing_max_mm':max(spacings),'max_sform_vs_pixdim_difference_mm':sform_max,
           'max_axis_spacing_rounded_histogram':dict(Counter(f'{v:.3f}' for v in spacings)),
           'csv_NONE_scans_in_raw':len(missing_csv),'csv_NONE_headers_complete':sum(r['header_complete'] for r in missing_csv),
           'retrieval_errors':heads['errors'],'joined_scans':joined,'bytes_transferred':total,
           'scientific_thin_reference_certified':0,'patient_pixels_decoded':False,'errors':errors}
    (OUT/'independent_metadata_header_verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items() if k!='joined_scans'},ensure_ascii=False,indent=2))
    return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
