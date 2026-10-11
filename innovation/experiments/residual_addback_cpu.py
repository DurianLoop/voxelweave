"""Post-result fixed addback baseline on all existing developer caches; no neural calls."""
import json, math, os, sys, traceback
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import numpy as np
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_runtime import reconstruct, sha, array_sha
from remind_native_t2_ixi_pair import prepared
import verify_mc_rc_three_development_action_oracle as three
import verify_mc_rc_001_002_raw_action_oracle as two
import vs_seg_001_local_action_oracle as seen
OUT=ROOT/'experiments/residual_addback_cpu'
PLAN=ROOT/'RESIDUAL_ADDBACK_CPU_PLAN_2026-10-03.md'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')

def inputs():
    entries=[];files={PLAN,Path(__file__).resolve(),Path(three.__file__),Path(two.__file__),Path(seen.__file__),ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/remind_native_t2_ixi_pair.py',ROOT/'experiments/vs_seg_task_cpu_support.py'}
    for folder,helper in [('mc_rc_three_development_action_oracle',three),('mc_rc_001_002_raw_action_oracle',two)]:
        base=ROOT/'experiments'/folder;prior=read(base/'attempt_01.json');proof=read(base/'independent_numerical_and_forward_verification.json');contract=read(base/'run_contract.json')
        if not prior['complete'] or proof['errors'] or proof['result_sha256']!=sha(base/'attempt_01.json') or prior['run_contract_sha256']!=sha(base/'run_contract.json'): raise ValueError('Old cache proof differs')
        for item in contract['files']:
            path=ROOT.parent/item['path']
            if sha(path)!=item['sha256']: raise ValueError('Old frozen source changed '+str(path))
            files.add(path)
        files.update([base/'attempt_01.json',base/'run_contract.json',base/'independent_numerical_and_forward_verification.json'])
        by={r['patient']:r for r in prior['patients']}
        for case in contract['cases']:
            old=by[case['patient']];cache=ROOT/old['hat_file']
            if sha(cache)!=old['hat_sha256']: raise ValueError('HAT cache changed')
            files.add(cache);entries.append(dict(kind='mc_rc',patient=case['patient'],case=case,prior=old,helper=helper))
    entries.sort(key=lambda r:r['patient'])
    if [r['patient'] for r in entries]!=['VS-MC-RC-001','VS-MC-RC-002','VS-MC-RC-004','VS-MC-RC-005','VS-MC-RC-006']: raise ValueError('All-five developer denominator differs')
    prior,paths,mask,old_contract=seen.freeze_inputs()
    for item in old_contract['files']: files.add(ROOT/item['path'])
    entries.append(dict(kind='seen_ciss',patient='VS-SEG-001',prior=prior,paths=paths,mask=mask))
    contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),post_result_development=True,formula='raw_PCHIP + (HAT - pipeline_PCHIP)',alpha=1.,clip=False,entries=[dict(patient=e['patient'],kind=e['kind']) for e in entries],independent_confirmation=False,files=[dict(path=p.relative_to(ROOT.parent).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
    write(OUT/'run_contract.json',contract)
    return entries

def load(entry):
    if entry['kind']=='mc_rc':
        native,label=entry['helper'].raw_source(entry['case']);prep=prepared(native[:,:,::4]);prior=entry['prior']
        raw=reconstruct('raw_pchip',native,prep,{});pipe=reconstruct('pipeline_pchip',native,prep,{})
        with np.load(ROOT/prior['hat_file']) as bundle: hat=bundle['image_rcz']
        obs,targets=prior['observation_indices'],prior['targets']
        expected={name:next(a for a in prior['actions'] if a['base']==name)['summaries']['fixed_0'] for name in ('raw_pchip','pipeline_pchip')}
        expected['hat']=next(a for a in prior['actions'] if a['base']=='raw_pchip')['summaries']['fixed_1']
    else:
        volumes={}
        for name,path in entry['paths'].items():
            with np.load(path) as bundle: volumes[name]=bundle['image_rcz']
        native,raw,pipe,hat=[volumes[x] for x in ('native','raw_pchip','pipeline_pchip','hat')]
        with np.load(entry['mask']) as bundle: label=bundle['original_mask_rcz'].astype(bool)
        obs,targets=entry['prior']['observation_indices'],entry['prior']['internal_targets']
        expected={r['condition']:r['image_metrics'] for r in entry['prior']['conditions'] if r['condition'] in ('raw_pchip','pipeline_pchip','hat')}
    span=float(native[:,:,obs].max())-float(native[:,:,obs].min())
    return native,label,raw,pipe,hat,obs,targets,span,expected

def summary(rows):
    result={}
    for region in ('support','lesion'):
        good=[r[region] for r in rows if r[region]['pixels']]
        count=sum(r['pixels'] for r in good)
        result[region]=dict(nonempty_targets=len(good),pixels=count,target_equal_nmse=math.fsum(r['sse']/r['pixels'] for r in good)/len(good) if good else None,pixel_weighted_nmse=math.fsum(r['sse'] for r in good)/count if count else None)
    return result

def scores(native,label,pred,targets,span):
    rows=[]
    for z in targets:
        left,right=native[:,:,z-z%4],native[:,:,z-z%4+4]
        support=(abs(left)>.01*max(float(abs(left).max()),1e-6)) | (abs(right)>.01*max(float(abs(right).max()),1e-6))
        if not support.any(): raise ValueError('Empty support')
        square=((pred[:,:,z].astype(float)-native[:,:,z].astype(float))/span)**2
        rows.append(dict(z=z,**{key:dict(pixels=int(mask.sum()),sse=float(square[mask].sum())) for key,mask in [('support',support),('lesion',support & label[:,:,z])]}))
    return summary(rows),rows

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();OUT.mkdir(exist_ok=False)
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,gpu_used=False,new_neural_inferences=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,series=[],errors=[])
    try:
        entries=inputs();report['run_contract_sha256']=sha(OUT/'run_contract.json')
        for entry in entries:
            resource_gate();native,label,raw,pipe,hat,obs,targets,span,expected=load(entry)
            candidate=(raw.astype(float)+(hat.astype(float)-pipe.astype(float))).astype(np.float32)
            if not np.array_equal(candidate[:,:,obs],native[:,:,obs]) or not np.array_equal(candidate[:,:,obs[-1]+1:],raw[:,:,obs[-1]+1:]): raise ValueError('Observed or tail preservation differs')
            metrics={};rows={}
            for name,pred in [('raw_pchip',raw),('pipeline_pchip',pipe),('hat',hat),('transfer',candidate)]:
                metrics[name],rows[name]=scores(native,label,pred,targets,span)
                if name!='transfer':
                    for region in ('support','lesion'):
                        for key in ('target_equal_nmse','pixel_weighted_nmse'):
                            if not math.isclose(metrics[name][region][key],expected[name][region][key],rel_tol=1e-7,abs_tol=1e-9): raise ValueError('Cached endpoint replay differs '+entry['patient']+'/'+name+'/'+region+'/'+key)
            best=min(metrics[k]['support']['target_equal_nmse'] for k in ('raw_pchip','hat'));gain=10*math.log10(best/metrics['transfer']['support']['target_equal_nmse'])
            guard={key:metrics['transfer']['lesion'][key] <= metrics['raw_pchip']['lesion'][key]+1e-12 for key in ('target_equal_nmse','pixel_weighted_nmse')}
            row=dict(patient=entry['patient'],kind=entry['kind'],targets=len(targets),observed_planes=len(obs),shape=list(native.shape),span=span,candidate_array_sha256=array_sha(candidate),metrics=metrics,per_plane=rows,gain_db_vs_better_raw_or_hat=gain,lesion_guard=guard,development_gate_passed=gain>=.1 and all(guard.values()))
            report['series'].append(row);write(OUT/'attempt_01.json',report)
            print(json.dumps({k:row[k] for k in ('patient','targets','gain_db_vs_better_raw_or_hat','lesion_guard','development_gate_passed')}),flush=True)
            del native,label,raw,pipe,hat,candidate
        report.update(complete=True,all_six_development_gate_passed=all(r['development_gate_passed'] for r in report['series']),fixed_candidate_stopped=not all(r['development_gate_passed'] for r in report['series']),task_inference_executed=False)
    except Exception as exc: report['errors'].append(type(exc).__name__+': '+str(exc));report['traceback']=traceback.format_exc()
    report['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',report)
    print(json.dumps({k:report.get(k) for k in ('complete','errors','all_six_development_gate_passed','fixed_candidate_stopped')}),flush=True)
    if not report['complete']: raise SystemExit(1)

if __name__=='__main__': main()
