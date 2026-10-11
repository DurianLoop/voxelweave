"""Full fixed45 analytic processing-order diagnostic, never a neural forward."""
import json, math, os, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import numpy as np
from scipy.interpolate import PchipInterpolator
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_selection_sensitivity import completion_gate, load_verified_records
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source, reconstruct, image_metrics, array_sha, sha
from remind_native_t2_ixi_pair import prepared
OUT=ROOT/'experiments/vs_seg_resampling_order_cpu'
PLAN=ROOT/'VS_SEG_RESAMPLING_ORDER_CPU_PLAN_2026-10-03.md'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')

def before_coarse(kernel,planes,z):
    i,t=z//4,z%4/4
    if kernel=='pchip' and i>=1 and i+2<len(planes):
        indices=np.arange(i-1,i+3);return PchipInterpolator(4*indices,np.stack([planes[j] for j in indices]),axis=0)(z)
    return (1-t)*planes[i]+t*planes[i+1]

def clip_information(coarse):
    changed=(coarse<0)|(coarse>1)
    return dict(changed_pixels=int(changed.sum()),changed_plane=bool(changed.any()),max_excursion=max(float(np.max(-coarse)),float(np.max(coarse-1)),0.))

def post_resize(raw,prep,targets):
    _,lo,hi=prep;span=hi-lo;post=raw.copy();rows=[]
    for z in targets:
        norm=((raw[:,:,z]-lo)/(span+1e-8)).astype(np.float32)
        coarse=resize(norm,(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
        rows.append(dict(z=z,**clip_information(coarse)))
        post[:,:,z]=(resize(np.clip(coarse,0,1),raw.shape[:2],preserve_range=True,anti_aliasing=True)*span+lo).astype(np.float32)
    return post,rows

def order_metrics(pipeline,post,native,refs,targets,span):
    output=[];max_abs=0.
    for z in targets:
        left,right=native[:,:,z-z%4],native[:,:,z-z%4+4]
        support=(abs(left)>.01*max(float(abs(left).max()),1e-6)) | (abs(right)>.01*max(float(abs(right).max()),1e-6))
        diff=(pipeline[:,:,z].astype(float)-post[:,:,z].astype(float))/span;max_abs=max(max_abs,float(abs(diff).max()))
        output.append(dict(z=z,**{name:dict(pixels=int(mask.sum()),normalized_difference_sse=float(np.dot(diff[mask],diff[mask])),max_abs_normalized_difference=float(abs(diff[mask]).max()) if mask.any() else None) for name,mask in [('support',support),*[(ref+'_lesion',support & label[:,:,z]) for ref,label in refs.items()]]}))
    summaries={}
    for region in ('support','original_json_lesion','rtstruct_lesion'):
        rows=[r[region] for r in output if r[region]['pixels']]
        summaries[region]=dict(pixels=sum(r['pixels'] for r in rows),nonempty_targets=len(rows),target_equal_difference_nmse=math.fsum(r['normalized_difference_sse']/r['pixels'] for r in rows)/len(rows) if rows else None,max_abs_normalized_difference=max(r['max_abs_normalized_difference'] for r in rows) if rows else None)
    return dict(max_abs_normalized_difference_full_image=max_abs,regions=summaries),output

def bootstrap(values):
    if any(v is None for v in values): raise ValueError('Unexpected undefined patient image endpoint')
    a=np.array(values,dtype=float);draws=np.random.default_rng(20261031).integers(0,45,size=(5000,45));estimates=a[draws].mean(axis=1)
    return dict(patients=45,mean_difference=float(a.mean()),ci95_percentile=[float(v) for v in np.percentile(estimates,[2.5,97.5])],draws=5000,seed=20261031,negative_patients=int((a<0).sum()),zero_patients=int((a==0).sum()),descriptive_without_familywise_claim=True)

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();gate,old=completion_gate()
    if not gate['allowed']: raise ValueError('Original whole queue must be complete')
    OUT.mkdir(exist_ok=False)
    coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');records,record_provenance=load_verified_records(old['main_roster'],{r['patient']:r for r in coverage['patients']})
    cases={r['patient']:r for r in cases_from_sources()};paths={PLAN,Path(__file__).resolve(),ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_full_volume_cohort.py',ROOT/'experiments/vs_seg_selection_sensitivity.py',ROOT/'experiments/remind_native_t2_ixi_pair.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'}
    for patient in old['main_roster']:
        case=cases[patient];paths.add(ROOT/case['input_file']);paths.add(ROOT/case['masks_file']);payload=read(ROOT/case['input_file']);paths.add(ROOT/payload['source_inputs']['image_zip']['path']);paths.add(ROOT/f'experiments/vs_seg_full_volume_cohort/verification_{patient}.json')
    contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),main_roster=old['main_roster'],post_result_development=True,original_contract_sha256=sha(ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'),record_provenance=record_provenance,files=[dict(path=p.relative_to(ROOT.parent).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(paths)],kernels=['linear','pchip'],linear_max_abs_normalized_order_tolerance=1e-6,new_method_confirmation_patients=0)
    write(OUT/'run_contract.json',contract);report=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,post_result_development=True,gpu_used=False,new_neural_inferences=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,patients=[],errors=[])
    try:
        for patient in old['main_roster']:
            resource_gate();started=time.perf_counter();native,affine,refs=decode_source(cases[patient]);prep=prepared(native[:,:,::4]);span=prep[2]-prep[1];obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];row=dict(patient=patient,shape=list(native.shape),observed_indices=obs,targets=targets,span=span,native_array_sha256=array_sha(native),conditions={},kernels={})
            if row['native_array_sha256']!=records[patient]['raw_pchip']['native_array_sha256']: raise ValueError('Native source hash differs')
            for kernel in ('linear','pchip'):
                raw=reconstruct('raw_'+kernel,native,prep,{});pipeline=reconstruct('pipeline_'+kernel,native,prep,{})
                for name,pred in [('raw_'+kernel,raw),('pipeline_'+kernel,pipeline)]:
                    if array_sha(pred)!=records[patient][name]['reconstructed_array_sha256']: raise ValueError('Existing analytic output bitwise hash differs '+name)
                    summary,per_plane=image_metrics(pred,native,refs,span)
                    for region in summary:
                        for key in ('target_equal_nmse','pixel_weighted_nmse'):
                            if not math.isclose(summary[region][key],records[patient][name]['image_metrics'][region][key],rel_tol=1e-10,abs_tol=1e-12): raise ValueError('Old endpoint replay differs')
                    row['conditions'][name]=dict(array_sha256=array_sha(pred),image_metrics=summary,per_plane=per_plane)
                post,clip_post=post_resize(raw,prep,targets)
                if not np.array_equal(post[:,:,obs],native[:,:,obs]) or not np.array_equal(post[:,:,obs[-1]+1:],raw[:,:,obs[-1]+1:]): raise ValueError('Post changes observed/tail')
                summary,per_plane=image_metrics(post,native,refs,span);row['conditions']['post_resize_'+kernel]=dict(array_sha256=array_sha(post),image_metrics=summary,per_plane=per_plane)
                clip_before=[dict(z=z,**clip_information(before_coarse(kernel,prep[0],z))) for z in targets]
                om,order_rows=order_metrics(pipeline,post,native,refs,targets,span)
                row['kernels'][kernel]=dict(order=om,per_plane_order=order_rows,clip_before=clip_before,clip_post=clip_post,within_linear_explanatory_tolerance=om['max_abs_normalized_difference_full_image']<=1e-6)
                del raw,pipeline,post
            patient_path=OUT/(patient+'.json');write(patient_path,row);report['patients'].append(dict(patient=patient,file=patient_path.relative_to(ROOT).as_posix(),sha256=sha(patient_path),targets=len(targets),seconds=time.perf_counter()-started));write(OUT/'attempt_01.json',report);print(json.dumps(dict(patient=patient,completed_patients=len(report['patients']),seconds=time.perf_counter()-started)),flush=True);del native,refs
        data=[read(ROOT/x['file']) for x in report['patients']];endpoints=[]
        for kernel in ('linear','pchip'):
            for region in ('support','original_json_lesion','rtstruct_lesion'):
                for weighting in ('target_equal_nmse','pixel_weighted_nmse'):
                    values={name:[r['conditions'][name+'_'+kernel]['image_metrics'][region][weighting] for r in data] for name in ('raw','pipeline','post_resize')}
                    for left,right in [('post_resize','raw'),('pipeline','post_resize'),('pipeline','raw')]:
                        diff=[a-b for a,b in zip(values[left],values[right])];endpoints.append(dict(kernel=kernel,region=region,weighting=weighting,comparison=left+'-'+right,patient_differences=diff,estimate=bootstrap(diff)))
        clipping={kernel:{stage:dict(changed_pixels=sum(x['changed_pixels'] for r in data for x in r['kernels'][kernel]['clip_'+stage]),changed_planes=sum(x['changed_plane'] for r in data for x in r['kernels'][kernel]['clip_'+stage]),max_excursion=max(x['max_excursion'] for r in data for x in r['kernels'][kernel]['clip_'+stage])) for stage in ('before','post')} for kernel in ('linear','pchip')}
        report.update(complete=True,all_main_patients=45,total_targets=sum(x['targets'] for x in report['patients']),existing_analytic_volumes_bitwise_replayed=180,new_post_volumes_constructed=90,clipping=clipping,order_above_linear_tolerance={kernel:sum(not r['kernels'][kernel]['within_linear_explanatory_tolerance'] for r in data) for kernel in ('linear','pchip')},analysis=endpoints)
    except Exception as exc: report['errors'].append(type(exc).__name__+': '+str(exc));report['traceback']=traceback.format_exc()
    report['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',report);print(json.dumps({k:report.get(k) for k in ('complete','errors','all_main_patients','total_targets','clipping','order_above_linear_tolerance')}),flush=True)
    if not report['complete']: raise SystemExit(1)

if __name__=='__main__': main()
