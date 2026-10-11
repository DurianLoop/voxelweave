"""All45 analytic replay: alternative Hermite, ROI dot products, scalar bootstrap."""
import json, math, os, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from scipy.interpolate import PchipInterpolator
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source, reconstruct, array_sha, sha
from remind_native_t2_ixi_pair import prepared
OUT=ROOT/'experiments/vs_seg_resampling_order_cpu'
REGIONS=('support','original_json_lesion','rtstruct_lesion')
WEIGHTS=('target_equal_nmse','pixel_weighted_nmse')

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):
    Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def check(ok,label):
    if not ok: raise ValueError(label)
def close(x,y,label):
    check(x==y if x is None or y is None else math.isclose(x,y,rel_tol=1e-10,abs_tol=1e-12),label)

def harmonic(a,b):
    result=np.zeros_like(a,dtype=float)
    valid=(np.sign(a)==np.sign(b)) & (a!=0) & (b!=0)
    result[valid]=2/(1/a[valid]+1/b[valid])
    return result

def independent_plane(planes,i,t,kernel):
    left,right=planes[i],planes[i+1]
    if kernel=='linear' or i<1 or i+2>=len(planes):
        return (1-t)*left+t*right
    previous,left,right,following=[np.asarray(planes[j],dtype=float) for j in (i-1,i,i+1,i+2)]
    m0=harmonic(left-previous,right-left);m1=harmonic(right-left,following-right)
    return (2*t**3-3*t**2+1)*left+(t**3-2*t**2+t)*m0+(-2*t**3+3*t**2)*right+(t**3-t**2)*m1

def producer_order_plane(planes,i,t,kernel):
    # SciPy is shared only to check the exact producer's clip counts;
    # independent Hermite above separately checks interpolation numerics.
    if kernel=='linear' or i<1 or i+2>=len(planes):
        return (1-t)*planes[i]+t*planes[i+1]
    block=np.moveaxis(np.asarray(planes[i-1:i+3]),0,-1)
    return PchipInterpolator(np.arange(i-1,i+3)*4,block,axis=-1)(4*i+4*t)

def clip_row(coarse):
    changed=np.count_nonzero(np.logical_or(coarse<0,coarse>1))
    return dict(changed_pixels=int(changed),changed_plane=bool(changed),max_excursion=max(0.,-float(coarse.min()),float(coarse.max())-1))

def metrics(pred,native,refs,targets,span,saved):
    sums={r:[] for r in REGIONS}
    check([r['z'] for r in saved['per_plane']]==targets,'All target rows differ')
    for z,row in zip(targets,saved['per_plane']):
        i=z//4;left,right=native[:,:,4*i],native[:,:,4*i+4]
        support=np.logical_or(np.abs(left)>.01*max(float(np.abs(left).max()),1e-6),np.abs(right)>.01*max(float(np.abs(right).max()),1e-6))
        masks={'support':support,**{r+'_lesion':np.logical_and(support,labels[:,:,z]) for r,labels in refs.items()}}
        full=np.subtract(pred[:,:,z],native[:,:,z],dtype=np.float32).astype(float).ravel()/span
        close(float(np.dot(full,full))/len(full),row['full_image_nmse'],'Full image NMSE differs')
        for region,mask in masks.items():
            diff=np.subtract(pred[:,:,z][mask],native[:,:,z][mask],dtype=np.float32).astype(float)/span
            n=len(diff);sse=float(np.dot(diff,diff));prior=row[region]
            check(n==prior['pixels'],'ROI count differs');close(sse,prior['sse'],'ROI SSE differs');close(sse/n if n else None,prior['nmse'],'ROI mean differs')
            if n: sums[region].append((n,sse))
    result={}
    for region,values in sums.items():
        n=sum(x[0] for x in values)
        summary=dict(pixels=n,nonempty_targets=len(values),target_equal_nmse=math.fsum(s/k for k,s in values)/len(values) if values else None,pixel_weighted_nmse=math.fsum(s for k,s in values)/n if n else None)
        for k,v in summary.items(): close(v,saved['image_metrics'][region][k],'Patient '+region+'/'+k+' differs')
        result[region]=summary
    return result

def order(pipeline,post,native,refs,targets,span,saved):
    maximum=0.;sums={r:[] for r in REGIONS}
    check([r['z'] for r in saved['per_plane_order']]==targets,'Order rows differ')
    for z,row in zip(targets,saved['per_plane_order']):
        i=z//4;left,right=native[:,:,4*i],native[:,:,4*i+4]
        support=np.logical_or(np.abs(left)>.01*max(float(np.abs(left).max()),1e-6),np.abs(right)>.01*max(float(np.abs(right).max()),1e-6))
        masks={'support':support,**{r+'_lesion':np.logical_and(support,labels[:,:,z]) for r,labels in refs.items()}}
        diff=np.subtract(pipeline[:,:,z],post[:,:,z],dtype=float)/span
        maximum=max(maximum,float(np.abs(diff).max()))
        for region,mask in masks.items():
            values=diff[mask];n=len(values);sse=float(np.dot(values,values));mx=float(abs(values).max()) if n else None
            check(n==row[region]['pixels'],'Order ROI count differs');close(sse,row[region]['normalized_difference_sse'],'Order SSE differs');close(mx,row[region]['max_abs_normalized_difference'],'Order max differs')
            if n: sums[region].append((n,sse,mx))
    close(maximum,saved['order']['max_abs_normalized_difference_full_image'],'Order full max differs')
    check((maximum<=1e-6)==saved['within_linear_explanatory_tolerance'],'Fixed linear threshold differs')
    for region,values in sums.items():
        actual=dict(pixels=sum(n for n,_,_ in values),nonempty_targets=len(values),target_equal_difference_nmse=math.fsum(s/n for n,s,_ in values)/len(values) if values else None,max_abs_normalized_difference=max(v[2] for v in values) if values else None)
        for k,v in actual.items(): close(v,saved['order']['regions'][region][k],'Order summary differs '+region+'/'+k)
    return maximum

def percentile(values,q):
    position=(len(values)-1)*q/100;lo=math.floor(position);hi=math.ceil(position)
    return values[lo]+(position-lo)*(values[hi]-values[lo])

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();started=time.perf_counter()
    result=read(OUT/'attempt_01.json');contract=read(OUT/'run_contract.json')
    proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,patients=[],errors=[],gpu_used=False,new_neural_inferences=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,
               independent_constructor_max_normalized_tolerance=5e-7,
               independence='Shared authenticated native decoder, observed normalization/resize library, exact analytic runtime/hash and NumPy RNG. Independent uniform-knot Hermite and linear plane formulas, alternative post construction, fresh ROI dot products/math.fsum, scalar bootstrap and hand-written quantiles. No software-stack or scientific-cohort independence claim.')
    path=OUT/'independent_replay_attempt_01.json';check(not path.exists(),'Verifier first attempt already exists')
    try:
        check(result['complete'] and not result['errors'],'Complete producer required')
        check(result['run_contract_sha256']==sha(OUT/'run_contract.json'),'Contract binding differs')
        check([r['patient'] for r in result['patients']]==contract['main_roster'] and len(contract['main_roster'])==45,'All45 roster differs')
        for f in contract['files']: check(sha(ROOT.parent/f['path'])==f['sha256'],'Frozen input changed '+f['path'])
        cases={r['patient']:r for r in cases_from_sources()};patient_data=[];totals={k:{s:dict(changed_pixels=0,changed_planes=0,max_excursion=0.) for s in ('before','post')} for k in ('linear','pchip')};above={k:0 for k in ('linear','pchip')}
        for record in result['patients']:
            resource_gate();patient=record['patient'];check(sha(ROOT/record['file'])==record['sha256'],'Patient file hash differs');saved=read(ROOT/record['file']);native,_,refs=decode_source(cases[patient]);prep=prepared(native[:,:,::4]);planes,lo,hi=prep;span=hi-lo;observed=list(range(0,native.shape[2],4));targets=[z for z in range(1,observed[-1]) if z%4]
            check(array_sha(native)==saved['native_array_sha256'],'Native hash differs');check(saved['observed_indices']==observed and saved['targets']==targets,'Observed/target indices differ');close(span,saved['span'],'Observed span differs');check(saved['shape']==list(native.shape),'Native shape differs')
            independent_max=0.;condition_metrics={}
            for kernel in ('linear','pchip'):
                raw=reconstruct('raw_'+kernel,native,prep,{});pipe=reconstruct('pipeline_'+kernel,native,prep,{})
                for name,pred in [('raw_'+kernel,raw),('pipeline_'+kernel,pipe)]:
                    check(array_sha(pred)==saved['conditions'][name]['array_sha256'],'Exact replay SHA differs '+name)
                    condition_metrics[name]=metrics(pred,native,refs,targets,span,saved['conditions'][name])
                post=np.empty_like(native);post[:,:,observed]=native[:,:,observed];post[:,:,observed[-1]+1:]=native[:,:,observed[-1],None]
                raw_planes=[native[:,:,z] for z in observed]
                for j,z in enumerate(targets):
                    i,t=z//4,z%4/4
                    raw_alt=independent_plane(raw_planes,i,t,kernel).astype(np.float32)
                    coarse_alt=independent_plane(planes,i,t,kernel)
                    pipe_alt=(resize(np.clip(coarse_alt,0,1),native.shape[:2],preserve_range=True,anti_aliasing=True)*span+lo).astype(np.float32)
                    independent_max=max(independent_max,float(abs(raw_alt.astype(float)-raw[:,:,z]).max())/span,float(abs(pipe_alt.astype(float)-pipe[:,:,z]).max())/span)
                    normalized=np.divide(np.subtract(raw[:,:,z],lo),span+1e-8).astype(np.float32)
                    coarse=resize(normalized,(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
                    stats={'before':clip_row(producer_order_plane(planes,i,t,kernel)),'post':clip_row(coarse)}
                    for stage,row in stats.items():
                        expected=saved['kernels'][kernel]['clip_'+stage][j]
                        check(expected['z']==z,'Clip z differs')
                        for k,v in row.items(): close(v,expected[k],'Clip row differs')
                        totals[kernel][stage]['changed_pixels']+=row['changed_pixels'];totals[kernel][stage]['changed_planes']+=row['changed_plane'];totals[kernel][stage]['max_excursion']=max(totals[kernel][stage]['max_excursion'],row['max_excursion'])
                    bounded=coarse.copy();np.clip(bounded,0,1,out=bounded)
                    restored=resize(bounded,native.shape[:2],preserve_range=True,anti_aliasing=True)
                    post[:,:,z]=np.add(np.multiply(restored,span),lo).astype(np.float32)
                check(independent_max<=5e-7,'Independent Hermite normalized error exceeds fixed tolerance')
                check(array_sha(post)==saved['conditions']['post_resize_'+kernel]['array_sha256'],'Alternative post construction SHA differs')
                check(np.array_equal(post[:,:,observed],native[:,:,observed]),'Anchor preservation differs');check(np.array_equal(post[:,:,observed[-1]+1:],raw[:,:,observed[-1]+1:]),'Tail preservation differs')
                condition_metrics['post_resize_'+kernel]=metrics(post,native,refs,targets,span,saved['conditions']['post_resize_'+kernel])
                mx=order(pipe,post,native,refs,targets,span,saved['kernels'][kernel]);above[kernel]+=mx>1e-6
                del raw,pipe,post
            row=dict(patient=patient,targets=len(targets),conditions=6,max_independent_constructor_normalized_error=independent_max)
            proof['patients'].append(row);patient_data.append(condition_metrics);write(path,proof);print(json.dumps(row),flush=True);del native,refs
        check(totals==result['clipping'],'All45 clipping summary differs');check(above==result['order_above_linear_tolerance'],'All45 threshold summary differs');check(sum(r['targets'] for r in proof['patients'])==result['total_targets'],'Complete target denominator differs')
        draws=np.random.default_rng(20261031).integers(0,45,size=(5000,45));endpoints=[]
        for endpoint in result['analysis']:
            kernel,region,weight=endpoint['kernel'],endpoint['region'],endpoint['weighting'];left,right=endpoint['comparison'].split('-');values=[p[left+'_'+kernel][region][weight]-p[right+'_'+kernel][region][weight] for p in patient_data]
            for a,b in zip(values,endpoint['patient_differences']): close(a,b,'Patient comparison differs')
            estimates=sorted(math.fsum(values[int(i)] for i in draw)/45 for draw in draws);actual=dict(mean_difference=math.fsum(values)/45,ci95_percentile=[percentile(estimates,q) for q in (2.5,97.5)],negative_patients=sum(v<0 for v in values),zero_patients=sum(v==0 for v in values))
            for k,v in actual.items():
                prior=endpoint['estimate'][k]
                if isinstance(v,list):
                    for a,b in zip(v,prior): close(a,b,'Scalar bootstrap quantile differs')
                else: close(v,prior,'Scalar bootstrap summary differs')
            endpoints.append({k:endpoint[k] for k in ('kernel','region','weighting','comparison')})
        check(len(endpoints)==36,'All36 endpoints required')
        # Algebra check on fresh summaries, without reading a producer decomposition field.
        for p in patient_data:
            for kernel in ('linear','pchip'):
                for region in REGIONS:
                    for weight in WEIGHTS:
                        a,b,c=[p[name+'_'+kernel][region][weight] for name in ('raw','post_resize','pipeline')]
                        close(c-a,(b-a)+(c-b),'Descriptive decomposition differs')
        proof.update(complete=True,endpoints=endpoints,total_targets=sum(r['targets'] for r in proof['patients']),clipping=totals,order_above_linear_tolerance=above,existing_analytic_volumes_replayed=180,new_post_volumes_replayed=90)
    except Exception as exc:
        proof['errors'].append(type(exc).__name__+': '+str(exc));proof['traceback']=traceback.format_exc()
    proof['elapsed_seconds']=time.perf_counter()-started;proof['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,proof);print(json.dumps({k:proof.get(k) for k in ('complete','total_targets','errors','elapsed_seconds')}),flush=True)
    if not proof['complete']: raise SystemExit(1)

if __name__=='__main__': main()
