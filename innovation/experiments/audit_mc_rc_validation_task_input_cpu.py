"""Prepare only the frozen nine validation observed inputs. No task effect or GPU."""
import sys,json,traceback
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_task_roles_input_cpu import ROOT,read,sha,array_sha,read_task_observed,read_task_supervised_label,stats,reconstruct,normalize,to_ras,support_domains,VALIDATORS,np
OUT=ROOT/'experiments/mc_rc_validation_task_input_cpu';DATA=ROOT/'data/mc_rc_validation_observed_only'
def write(p,r):Path(p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();OUT.mkdir(exist_ok=False);DATA.mkdir(exist_ok=False);prepfile=ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json';prep=read(prepfile);assert prep['complete'] and len(prep['cases'])==9;path=OUT/'attempt_01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),loader_sha256=sha(ROOT/'experiments/mc_rc_task_roles_input_cpu.py'),preparation_sha256=sha(prepfile),series=[],validation_patient_ids=sorted(VALIDATORS),expected_series=9,saved_observed_bytes=0,max_total_saved_observed_bytes=500000000,phase=0,stride=4,label_input_separated=True,non_observed_MR_pixels_decoded=False,confirmation_patients_opened=False,torch_imported=False,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False);write(path,r)
    try:
        for case in prep['cases']:
            resource_gate();o=read_task_observed(case);dest=DATA/(case['patient']+'_'+case['uid']+'_observed_only.npz');np.savez_compressed(dest,observed_rcz=o.pixels,observed_indices=np.asarray(o.indices),native_shape=np.asarray(case['native_shape']),affine_rcz_ras=np.asarray(o.affine_rcz_ras));r['saved_observed_bytes']+=dest.stat().st_size;assert r['saved_observed_bytes']<=r['max_total_saved_observed_bytes']
            row=dict(patient=case['patient'],uid=case['uid'],observed_package=dest.relative_to(ROOT).as_posix(),observed_package_sha256=sha(dest),observed_array_sha256=array_sha(o.pixels),observed_indices=list(o.indices),decoded_zip_members=list(o.decoded_members),decoded_sop_uids=list(o.sop_uids),observed_stats=stats(o.pixels),domain_planes={k:int(v.sum()) for k,v in support_domains(o).items()},inputs={},complete=False)
            for method in ('raw_linear','raw_pchip'):
                raw=reconstruct(o,method);rh=array_sha(raw)
                for policy in ('observed_shared','full_own'):
                    x,st=normalize(raw,o,policy);ras,affine,orientation=to_ras(x,o);row['inputs'][method+'_'+policy]=dict(raw_reconstruction_sha256=rh,normalized_rcz_sha256=array_sha(x),normalized_ras_sha256=array_sha(ras),statistics=st,ras_shape=list(ras.shape),ras_affine=affine.tolist(),orientation=orientation.tolist());del x,ras
                del raw
            g=read_task_supervised_label(case);gras,affine,orientation=to_ras(g,o);row.update(label_array_sha256=array_sha(g),label_ras_sha256=array_sha(gras),label_foreground=int(g.sum()),label_read_after_all_inputs_recorded=True,complete=True);r['series'].append(row);write(path,r);print(json.dumps(dict(patient=case['patient'],uid=case['uid'],observed_planes=len(o.indices),missing_MR_decoded=0,complete=True)),flush=True);del o,g,gras
        r['torch_imported']='torch' in sys.modules;assert not r['torch_imported'];r['complete']=len(r['series'])==9
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r);print(json.dumps({k:r.get(k) for k in ('complete','errors','saved_observed_bytes','new_neural_forwards')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
