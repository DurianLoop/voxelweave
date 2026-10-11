"""One new analytic-input segmentation per fixed45, no GPU or old reruns."""
import json,os,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import numpy as np
import nibabel as nib
from vs_seg_task_cpu_support import ROOT,resource_gate,load_model
from vs_seg_full_volume_cohort import cases_from_sources,verify_contract,write_json
from vs_seg_selection_sensitivity import completion_gate,load_verified_records
from vs_seg_full_volume_runtime import reconstruct,decode_source,inference,load_tuple_inferer,array_sha,sha
from vs_seg_full_volume_metrics import task_metrics,outside_reference_band,paired_bootstrap
from remind_native_t2_ixi_pair import prepared
from vs_seg_resampling_order_cpu import post_resize
from verify_vs_seg_post_resize_task_cpu import verify_one,verify_analysis
OUT=ROOT/'experiments/vs_seg_post_resize_task_cpu'
PLAN=ROOT/'VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md'
ANALYTIC=ROOT/'experiments/vs_seg_resampling_order_cpu'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def emit(row):
    line=json.dumps(row,ensure_ascii=False);print(line,flush=True)
    with (OUT/'stdout.jsonl').open('a',encoding='utf-8') as stream: stream.write(line+'\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();verify_contract();gate,original=completion_gate()
    if not gate['allowed']: raise ValueError('Original queue incomplete')
    analytic=read(ANALYTIC/'attempt_01.json');proof=read(ANALYTIC/'independent_replay_attempt_01.json')
    if not analytic['complete'] or analytic['errors'] or not proof['complete'] or proof['errors'] or proof['result_sha256']!=sha(ANALYTIC/'attempt_01.json'): raise ValueError('Analytic all45 proof differs')
    OUT.mkdir(exist_ok=False);coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');old,provenance=load_verified_records(original['main_roster'],{r['patient']:r for r in coverage['patients']});cases={r['patient']:r for r in cases_from_sources()}
    paths={PLAN,Path(__file__).resolve(),ROOT/'experiments/verify_vs_seg_post_resize_task_cpu.py',ANALYTIC/'run_contract.json',ANALYTIC/'attempt_01.json',ANALYTIC/'independent_replay_attempt_01.json',ROOT/'experiments/vs_seg_resampling_order_cpu.py',ROOT/'experiments/vs_seg_full_volume_metrics.py',ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_full_volume_cohort.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_selection_sensitivity.py',ROOT/'experiments/remind_native_t2_ixi_pair.py'}
    for item in original['files']: paths.add(ROOT.parent/item['path'])
    for item in analytic['patients']: paths.add(ROOT/item['file'])
    for item in provenance: paths.add(ROOT/item['file'])
    contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),original_contract_sha256=sha(ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'),main_roster=original['main_roster'],condition='post_resize_pchip',bootstrap_seed=20261101,bootstrap_draws=5000,post_result_development=True,new_method_confirmation_patients=0,files=[dict(path=p.relative_to(ROOT.parent).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)],original_record_provenance=provenance)
    write_json(OUT/'run_contract.json',contract);report=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),main_roster=contract['main_roster'],complete=False,active_stage='loading_cpu_model',patients=[],errors=[],post_result_development=True,gpu_used=False,new_method_confirmation_patients=0,publication_claim_confirmed=False)
    write_json(OUT/'attempt_01.json',report)
    try:
        segmenter,runtime=load_model();infer=load_tuple_inferer();records={};report['active_stage']='cpu_task_inference_and_saved_output_verification';write_json(OUT/'attempt_01.json',report)
        for patient in contract['main_roster']:
            start=time.perf_counter();resource=resource_gate();case=cases[patient];native,affine,refs=decode_source(case);prep=prepared(native[:,:,::4]);obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];raw=reconstruct('raw_pchip',native,prep,{});generated,_=post_resize(raw,prep,targets);del raw
            analytic_row=read(ANALYTIC/(patient+'.json'))
            if array_sha(generated)!=analytic_row['conditions']['post_resize_pchip']['array_sha256']: raise ValueError('New task input differs from all45 analytic contract')
            orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));can_affine=affine@nib.orientations.inv_ornt_aff(orientation,native.shape);spacing=nib.affines.voxel_sizes(can_affine)
            if not np.allclose(can_affine[:3,:3].T@can_affine[:3,:3],np.diag(spacing**2),atol=1e-5,rtol=0): raise ValueError('Nonorthogonal physical grid')
            last=obs[-1];slab=np.zeros(native.shape,dtype=bool);slab[:,:,:last+1]=True;slab=nib.orientations.apply_orientation(slab,orientation);refs={k:nib.orientations.apply_orientation(v,orientation) for k,v in refs.items()}
            record=dict(patient=patient,condition='post_resize_pchip',complete=False,contract_sha256=report['run_contract_sha256'],runtime=runtime,resource_gate=resource,source_input_sha256=sha(ROOT/case['input_file']),reference_masks_sha256=sha(ROOT/case['masks_file']),native_array_sha256=array_sha(native),reconstructed_array_sha256=array_sha(generated),canonical_affine=can_affine.tolist(),spacing_ras_mm=spacing.tolist(),observed_indices=obs,unsupported_terminal_indices=list(range(last+1,native.shape[2])))
            task_start=time.perf_counter();prediction=inference(segmenter,infer,generated,orientation);record['task_seconds']=time.perf_counter()-task_start;record['task_metrics']={k:task_metrics(prediction,v,spacing,slab,outside_reference_band(v,spacing)) for k,v in refs.items()};p=OUT/(patient+'_prediction.npz')
            with p.open('xb') as stream: np.savez_compressed(stream,prediction_ras=prediction,affine=can_affine)
            import torch
            record.update(complete=True,prediction_file=p.relative_to(ROOT).as_posix(),prediction_sha256=sha(p),prediction_array_sha256=array_sha(prediction),cuda_initialized=torch.cuda.is_initialized(),elapsed_seconds=time.perf_counter()-start)
            write_json(OUT/(patient+'.json'),record);verification=verify_one(case,record);records[patient]=record;report['patients'].append(dict(patient=patient,record_file=(OUT/(patient+'.json')).relative_to(ROOT).as_posix(),record_sha256=sha(OUT/(patient+'.json')),verification_file=(OUT/('verification_'+patient+'.json')).relative_to(ROOT).as_posix(),verification_sha256=sha(OUT/('verification_'+patient+'.json')),seconds=time.perf_counter()-start));write_json(OUT/'attempt_01.json',report);emit(dict(patient=patient,completed_patients=len(report['patients']),complete=True,independent_saved_output_verified=verification['complete'],seconds=time.perf_counter()-start));del native,generated,prediction,refs,slab
        analysis=[]
        for ref in ('original_json','rtstruct'):
            for domain in ('full','observed_anchor_slab','exclude_reference_boundary_1mm'):
                values={p:{'post':records[p]['task_metrics'][ref][domain]['dice'],'pipeline':old[p]['pipeline_pchip']['task_metrics'][ref][domain]['dice'],'raw':old[p]['raw_pchip']['task_metrics'][ref][domain]['dice']} for p in contract['main_roster']};included=[p for p in contract['main_roster'] if all(v is not None for v in values[p].values())]
                for left,right in [('post','pipeline'),('post','raw'),('pipeline','raw')]:
                    delta=[values[p][left]-values[p][right] for p in included];analysis.append(dict(reference=ref,domain=domain,comparison=left+'-'+right,original_denominator=45,included_patients=included,undefined_patients=[p for p in contract['main_roster'] if p not in included],patient_differences=delta,estimate=paired_bootstrap(delta,seed=20261101,draws=5000) if delta else None,descriptive_without_familywise_claim=True))
        report.update(complete=True,active_stage='complete',analysis=analysis,new_neural_forwards=45,finished_utc=datetime.now(timezone.utc).isoformat());write_json(OUT/'attempt_01.json',report);verification=verify_analysis(report,records,old);emit(dict(complete=True,completed_patients=45,independent_estimates_verified=verification['complete'],errors=[]))
    except Exception as exc:
        report.update(complete=False,active_stage='failed',finished_utc=datetime.now(timezone.utc).isoformat());report['errors'].append(type(exc).__name__+': '+str(exc));report['traceback']=traceback.format_exc();write_json(OUT/'attempt_01.json',report);emit(dict(complete=False,active_stage='failed',errors=report['errors']));raise SystemExit(1)

if __name__=='__main__': main()
