"""All 28 sparse inputs must survive nonexistent hidden/reference/label paths and denied readers."""
import copy
import json
import sys
import traceback
from datetime import datetime,timezone
import mc_rc_3d_baseline_2026_10_07 as base
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,array_sha,fixed_cases,resource_guard,torch
OUT=ROOT/'experiments/mc_rc_3d_sparse_source_isolation_2026_10_07'

def denied(*args,**kwargs):raise AssertionError('Sparse branch called a full-native or label reader')

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],script_sha256=sha(__file__),
           actual_gpu_updates=0,confirmation_patients_opened=False,scientific_confirmation_patients=0,
           all_native_and_label_readers_denied=True,hidden_source_paths_nonexistent=True)
    certpath=ROOT/'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json'
    cert=read(certpath);assert cert['complete'] and not cert['errors']
    r['input_certificate_sha256']=sha(certpath)
    r['baseline_source_sha256']=sha(ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py')
    expected={x['uid']:x for x in cert['series']}
    old_reference,old_label=base.read_reference,base.read_reference_label
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        base.read_reference=denied;base.read_reference_label=denied
        for role,case,row in fixed_cases():
            resource_guard();fake=copy.deepcopy(case)
            for key in ('mr_zip_file','header_file','label_file'):fake[key]='__intentionally_absent_reference_'+key
            assert all(not (ROOT/fake[k]).exists() for k in ('mr_zip_file','header_file','label_file'))
            for key in ('mr_zip_sha256','header_sha256','label_sha256'):fake[key]='INVALID_REFERENCE_HASH_NOT_NEEDED_BY_SPARSE_INPUT'
            # A bogus supervision transform/foreground value must not affect image construction.
            fake['dicom_rcz_from_label_xyz']=None;fake['expected_label_foreground_voxels']=-123
            x,statistics=base.source_image(fake,row,'raw_pchip')
            target=expected[case['uid']]['inputs']['raw_pchip']
            assert array_sha(x)==target['normalized_rcz_sha256'] and statistics==target['observed_statistics']
            r['series'].append(dict(role=role,patient=case['patient'],uid=case['uid'],normalized_image_sha256=array_sha(x),complete=True))
            save();print(json.dumps(dict(role=role,patient=case['patient'],hidden_and_label_inputs_read=0,complete=True)),flush=True)
            del x
        assert not torch.cuda.is_initialized()
        r['complete']=len(r['series'])==28;r['cuda_initialized']=False;r['resources_after']=resource_guard()
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    finally:base.read_reference,base.read_reference_label=old_reference,old_label
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_gpu_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
