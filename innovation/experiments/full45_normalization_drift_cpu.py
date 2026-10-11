"""Post-hoc fixed45 input-statistics audit; zero neural forwards and no CUDA."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[k] = '1'
import csv, json, math, sys, time, traceback
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import nibabel as nib
from scipy.stats import pearsonr, spearmanr
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_runtime import decode_source, reconstruct, array_sha, sha
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_selection_sensitivity import completion_gate
from remind_native_t2_ixi_pair import prepared
from vs_seg_resampling_order_cpu import post_resize
import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
def deny_cuda(*args, **kwargs):
    raise RuntimeError('CUDA initialization forbidden in statistics audit')
torch.cuda._lazy_init = deny_cuda
OUT = ROOT / 'experiments/full45_normalization_drift_cpu'
PILOT = ['VS-SEG-202', 'VS-SEG-203', 'VS-SEG-204']

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def write(p, x):
    Path(p).write_text(json.dumps(x, ensure_ascii=False, allow_nan=False, indent=2)+'\n', encoding='utf-8')

def moments(a):
    a = a.astype(np.float64)
    n = int(a.size)
    if not n:
        return dict(count=0, sum=0., sum_square=0., mean=None, variance=None)
    s, ss = float(a.sum()), float(np.square(a).sum())
    return dict(count=n, sum=s, sum_square=ss, mean=s/n, variance=max(0., ss/n-(s/n)**2))

def main():
    sys.stdout.reconfigure(encoding='utf-8'); resource_gate()
    gate, original = completion_gate(); assert gate['allowed']
    postdir = ROOT/'experiments/vs_seg_post_resize_task_cpu'
    p, q = read(postdir/'attempt_01.json'), read(postdir/'independent_all_tasks_and_estimates.json')
    assert p['complete'] and q['complete'] and not p['errors'] and not q['errors']
    assert q['result_sha256'] == sha(postdir/'attempt_01.json')
    assert p['main_roster'] == original['main_roster']
    OUT.mkdir(exist_ok=False)
    paths = {Path(__file__), ROOT/'FULL45_NORMALIZATION_DRIFT_CPU_PLAN_2026-10-03.md',
             postdir/'attempt_01.json', postdir/'independent_all_tasks_and_estimates.json',
             ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'}
    for f in ('vs_seg_full_volume_runtime.py','vs_seg_task_cpu_support.py','vs_seg_full_volume_cohort.py',
              'vs_seg_selection_sensitivity.py','remind_native_t2_ixi_pair.py','vs_seg_resampling_order_cpu.py'):
        paths.add(ROOT/'experiments'/f)
    for patient in original['main_roster']:
        paths.add(postdir/(patient+'.json'))
        paths.add(ROOT/'experiments/vs_seg_full_volume_cohort/patients'/patient/'raw_pchip_attempt_01.json')
    contract = dict(created_utc=datetime.now(timezone.utc).isoformat(), main_roster=original['main_roster'],
                    post_hoc_development_only=True, pilot_roster=PILOT, new_neural_forwards=0,
                    features=['a_minus_one','b','observed_normalized_rms'],
                    references=['original_json','rtstruct'],
                    files=[dict(path=x.relative_to(ROOT.parent).as_posix(),sha256=sha(x)) for x in sorted(paths)])
    write(OUT/'run_contract.json',contract)
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),
                  complete=False,active_stage='replaying_statistics',errors=[],patients=[],gpu_used=False,
                  new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(OUT/'attempt_01.json',result)
    cases = {x['patient']:x for x in cases_from_sources()}
    try:
        for patient in contract['main_roster']:
            started=time.perf_counter(); resources=resource_gate()
            native,affine,refs=decode_source(cases[patient]); del refs
            obs=list(range(0,native.shape[2],4)); targets=[z for z in range(1,obs[-1]) if z%4]
            zs={'observed_anchors':obs,'supported_missing':targets,'unsupported_tail':list(range(obs[-1]+1,native.shape[2]))}
            prep=prepared(native[:,:,::4]);raw=reconstruct('raw_pchip',native,prep,{});post,_=post_resize(raw,prep,targets)
            old=read(ROOT/'experiments/vs_seg_full_volume_cohort/patients'/patient/'raw_pchip_attempt_01.json')
            oldpost=read(postdir/(patient+'.json'))
            assert array_sha(raw)==old['reconstructed_array_sha256'] and array_sha(post)==oldpost['reconstructed_array_sha256']
            assert np.array_equal(raw[:,:,obs],post[:,:,obs]) and np.array_equal(raw[:,:,zs['unsupported_tail']],post[:,:,zs['unsupported_tail']])
            orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'))
            images={name:np.ascontiguousarray(nib.orientations.apply_orientation(a,orientation)) for name,a in [('raw',raw),('post',post)]}
            statistics={name:dict(mean=float(np.mean(a.ravel())),std=float(np.std(a.ravel()))) for name,a in images.items()}
            assert all(v['std']>0 for v in statistics.values())
            a=statistics['raw']['std']/statistics['post']['std'];b=(statistics['raw']['mean']-statistics['post']['mean'])/statistics['post']['std']
            domain_stats={name:{d:moments(v[:,:,z]) for d,z in zs.items()} for name,v in [('raw',raw),('post',post)]}
            full_moments={name:moments(v) for name,v in [('raw',raw),('post',post)]}
            partition_errors={}
            for name,m in full_moments.items():
                parts=domain_stats[name];assert sum(x['count'] for x in parts.values())==m['count']
                partition_errors[name]={key:math.fsum(x[key] for x in parts.values())-m[key] for key in ('sum','sum_square')}
                for key in ('sum','sum_square'):assert math.isclose(math.fsum(x[key] for x in parts.values()),m[key],rel_tol=2e-13,abs_tol=1e-5)
            same_domain={}
            for d in ('observed_anchors','unsupported_tail'):
                x=raw[:,:,zs[d]]
                if not x.size:
                    same_domain[d]=dict(count=0,rms_float32=None,rms_analytic_real=None,max_affine_float32_roundoff=None);continue
                nr=(x-np.float32(statistics['raw']['mean']))/np.float32(statistics['raw']['std'])
                npst=(x-np.float32(statistics['post']['mean']))/np.float32(statistics['post']['std'])
                diff=npst.astype(np.float64)-nr.astype(np.float64)
                m=domain_stats['raw'][d];c=1/statistics['post']['std']-1/statistics['raw']['std'];e=statistics['raw']['mean']/statistics['raw']['std']-statistics['post']['mean']/statistics['post']['std']
                analytic=math.sqrt(max(0.,c*c*m['sum_square']/m['count']+2*c*e*m['mean']+e*e))
                rms=float(np.sqrt(np.square(diff).mean()));roundoff=float(np.abs(npst.astype(np.float64)-(a*nr.astype(np.float64)+b)).max())
                assert abs(rms-analytic)<2e-6 and roundoff<4e-6
                same_domain[d]=dict(count=m['count'],rms_float32=rms,rms_analytic_real=analytic,max_affine_float32_roundoff=roundoff)
            dices={ref:dict(raw=old['task_metrics'][ref]['full']['dice'],post=oldpost['task_metrics'][ref]['full']['dice'],
                           post_minus_raw=oldpost['task_metrics'][ref]['full']['dice']-old['task_metrics'][ref]['full']['dice']) for ref in contract['references']}
            rec=dict(patient=patient,complete=True,shape=list(raw.shape),source_bindings=[dict(path=(ROOT/cases[patient][k]).relative_to(ROOT).as_posix(),sha256=sha(ROOT/cases[patient][k])) for k in ('input_file','masks_file')],
                     native_array_sha256=array_sha(native),raw_array_sha256=array_sha(raw),post_array_sha256=array_sha(post),statistics_ras_float32=statistics,
                     domain_indices=zs,domain_moments_float64=domain_stats,full_moments_float64=full_moments,partition_errors=partition_errors,
                     normalization_a=a,normalization_b=b,a_minus_one=a-1.,b=b,std_relative_change=statistics['post']['std']/statistics['raw']['std']-1.,
                     observed_normalized_rms=same_domain['observed_anchors']['rms_float32'],same_image_domains=same_domain,
                     saved_full_dice=dices,resource_gate=resources,cuda_initialized=torch.cuda.is_initialized(),seconds=time.perf_counter()-started)
            assert not rec['cuda_initialized'];path=OUT/(patient+'.json');write(path,rec)
            result['patients'].append(dict(patient=patient,file=path.relative_to(ROOT).as_posix(),sha256=sha(path)));write(OUT/'attempt_01.json',result)
            print(json.dumps(dict(patient=patient,completed_patients=len(result['patients']),seconds=rec['seconds'])),flush=True)
            del native,raw,post,images,domain_stats,full_moments,nr,npst,diff,x
        rows=[read(ROOT/e['file']) for e in result['patients']];associations=[]
        for feature in contract['features']:
            for ref in contract['references']:
                xx=[r[feature] for r in rows];yy=[r['saved_full_dice'][ref]['post_minus_raw'] for r in rows]
                for name,fn in [('pearson',pearsonr),('spearman',spearmanr)]:
                    coefficient=float(fn(xx,yy).statistic)
                    associations.append(dict(feature=feature,reference=ref,method=name,n=45,coefficient=coefficient,post_hoc_descriptive_only=True))
        summary={f:dict(mean=math.fsum(r[f] for r in rows)/45,minimum=min(r[f] for r in rows),maximum=max(r[f] for r in rows),
                        pilot_values={r['patient']:r[f] for r in rows if r['patient'] in PILOT}) for f in contract['features']+['std_relative_change']}
        cohort_dice={ref:{group:dict(n=len(rr),mean=math.fsum(r['saved_full_dice'][ref]['post_minus_raw'] for r in rr)/len(rr)) for group,rr in [('full45',rows),('fixed_pilot3',[r for r in rows if r['patient'] in PILOT]),('remaining42',[r for r in rows if r['patient'] not in PILOT])]} for ref in contract['references']}
        csvpath=OUT/'all45_statistics_and_saved_dice.csv';fields=['patient']+contract['features']+['std_relative_change']+[ref+'_post_minus_raw_dice' for ref in contract['references']]
        with csvpath.open('x',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
            for r in rows:writer.writerow({k:r[k] for k in fields if k in r}|{ref+'_post_minus_raw_dice':r['saved_full_dice'][ref]['post_minus_raw'] for ref in contract['references']})
        result.update(complete=True,active_stage='complete',summary=summary,associations=associations,cohort_dice=cohort_dice,
                      csv_file=csvpath.relative_to(ROOT).as_posix(),csv_sha256=sha(csvpath),old_arrays_replayed=90,unchanged_image_domains_checked=90)
    except Exception as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc));result['traceback']=traceback.format_exc();result['active_stage']='failed'
    result['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',result)
    print(json.dumps({k:result.get(k) for k in ('complete','active_stage','errors','old_arrays_replayed','new_neural_forwards')}),flush=True)
    if not result['complete']:raise SystemExit(1)
if __name__=='__main__':main()
