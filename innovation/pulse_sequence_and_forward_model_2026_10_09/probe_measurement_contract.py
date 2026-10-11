"""Fixed toy acquisition qualification: independently integrate every declared case."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,json,time,math,ctypes
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime,timezone
import numpy as np
from scipy.integrate import quad
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard

def budget():
    r=resource_guard();assert r['workspace_free_bytes']-3_000_000-2_000_000-600_000>=8_000_000_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<3_000_000
    return r

def exact_weights(centers,z,t):
    # Independent rational scalar intersection; no calls to NumPy overlap.
    rows=[]
    for center in centers:
        lo,hi=F(int(center))-F(t,2),F(int(center))+F(t,2)
        row=[]
        for cell in z:
            left,right=F(int(cell))-F(1,2),F(int(cell))+F(1,2)
            length=min(hi,right)-max(lo,left)
            row.append(max(F(0),length)/t)
        assert sum(row)==1
        rows.append(row)
    return rows

def exact_linear(centers,values,z):
    result=[]
    for cell in z:
        cell=int(cell)
        if cell<=centers[0]:result.append(values[0]);continue
        if cell>=centers[-1]:result.append(values[-1]);continue
        right=next(i for i,c in enumerate(centers) if c>=cell)
        left=right-1;weight=F(cell-centers[left],centers[right]-centers[left])
        result.append(values[left]*(1-weight)+values[right]*weight)
    return result

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();budget()
    handle=ctypes.windll.kernel32.GetCurrentProcess()
    assert ctypes.windll.kernel32.SetPriorityClass(handle,0x00004000)
    assert ctypes.windll.kernel32.GetPriorityClass(handle)==0x00004000
    out=HERE/'measurement_contract_attempt01';out.mkdir(exist_ok=False)
    config=dict(spacings=[2,3,4,6],phases='all integer phases 0..spacing-1',thicknesses=list(range(1,7)),
        latent_centers=list(range(-30,31)),measurement_centers_extent=[-24,24],
        profiles=['impulse_'+str(v) for v in range(-4,5)]+['plateau_5','triangular','alternating'],
        expected_piecewise_cases=1080,sphere_radii=[1,2,3,5],sphere_offsets=['0','1/4','1/2','3/4'],
        sphere_centers_extent=[-12,12],expected_sphere_groups=384,piecewise_atol=2e-14,sphere_atol=2e-12,
        protocol=entry(HERE/'MEASUREMENT_CONTRACT_PROTOCOL.md'),runner=entry(Path(__file__)),
        medical_data=False,new_algorithm=False)
    dump(out/'frozen_config.json',config)
    z=np.arange(-30,31);profiles=[]
    for position in range(-4,5):profiles.append(('impulse_'+str(position),[F(int(v==position)) for v in z]))
    profiles.extend([('plateau_5',[F(int(abs(v)<=2)) for v in z]),
        ('triangular',[max(F(0),F(4-int(abs(v)),4)) for v in z]),
        ('alternating',[F(int(abs(v)<=4 and v%2==0)) for v in z])])
    rows=[];maxw=maxy=maxlinear=maxproject=0.;counter=None
    try:
        # Explicit sparse-write counterexample, independent of reconstruction sweep.
        cz=list(range(-3,4));ew=exact_weights([0],cz,4)[0]
        latent=[F(int(v==1)) for v in cz];y=sum(a*b for a,b in zip(ew,latent))
        write=[F(0) for v in cz];write[cz.index(0)]=y
        measured=sum(a*b for a,b in zip(ew,write))
        assert y==F(1,4) and write[cz.index(0)]==y and measured==F(1,16) and y-measured==F(3,16)
        counter=dict(latent_centers=cz,weights=[str(v) for v in ew],true_box_measurement=str(y),
            point_center_before_write='0',point_center_after_write=str(y),box_after_sparse_write=str(measured),
            box_residual=str(y-measured),point_constraint_exact=True)
        for spacing in config['spacings']:
            for phase in range(spacing):
                centers=list(range(-24+phase,25,spacing));idx=np.asarray(centers)+30
                for thickness in config['thicknesses']:
                    assert time.perf_counter()-started<60;budget()
                    c=np.asarray(centers,dtype=np.float64)[:,None];zz=z.astype(np.float64)[None,:]
                    a=np.maximum(0,np.minimum(c+thickness/2,zz+.5)-np.maximum(c-thickness/2,zz-.5))/thickness
                    exact=exact_weights(centers,z,thickness)
                    maxw=max(maxw,float(np.max(np.abs(a-np.array(exact,dtype=np.float64)))))
                    assert maxw<=2e-14
                    assert np.linalg.matrix_rank(a)==len(centers)
                    for name,latent in profiles:
                        yf=[sum(w*v for w,v in zip(row,latent)) for row in exact]
                        y=np.asarray(yf,dtype=np.float64);yflo=a@np.asarray(latent,dtype=np.float64)
                        maxy=max(maxy,float(np.max(np.abs(y-yflo))));assert maxy<=2e-14
                        xp=np.interp(z,centers,y);xp[idx]=y
                        independent=exact_linear(centers,yf,z)
                        maxlinear=max(maxlinear,float(np.max(np.abs(xp-np.asarray(independent,dtype=np.float64)))))
                        assert maxlinear<=2e-14 and np.array_equal(xp[idx],y)
                        exact_res=[sum(w*v for w,v in zip(row,independent))-yv for row,yv in zip(exact,yf)]
                        point_res=float(np.max(np.abs(a@xp-y)))
                        assert abs(point_res-float(max(abs(v) for v in exact_res)))<=2e-14
                        if thickness==1:assert all(v==0 for v in exact_res)
                        solve_start=time.perf_counter();xdc=xp+a.T@np.linalg.solve(a@a.T,y-a@xp)
                        solve_seconds=time.perf_counter()-solve_start
                        rem=[math.fsum(float(w)*float(v) for w,v in zip(row,xdc))-float(yv) for row,yv in zip(exact,yf)]
                        project_res=max(abs(v) for v in rem);maxproject=max(maxproject,project_res);assert project_res<=2e-14
                        rows.append([spacing,phase,thickness,name,len(centers),str(max(abs(v) for v in exact_res)),
                            point_res,project_res,float(np.max(np.abs(xdc[idx]-y))),float(np.min(xdc)),float(np.max(xdc)),solve_seconds])
        assert len(rows)==1080
        sphere=[];sphere_max=0.;nquad=0
        for radius in config['sphere_radii']:
            for offset in [0,.25,.5,.75]:
                for spacing in config['spacings']:
                    centers=list(range(-12,13,spacing))
                    for thickness in config['thicknesses']:
                        assert time.perf_counter()-started<60
                        delta=0.;maxsignal=0.
                        for center in centers:
                            low=max(center-thickness/2,offset-radius);high=min(center+thickness/2,offset+radius)
                            if high<=low:analytic=numeric=0.
                            else:
                                l=low-offset;h=high-offset
                                analytic=math.pi*(radius*radius*(h-l)-(h**3-l**3)/3)/thickness
                                numeric=quad(lambda zz:math.pi*max(radius*radius-(zz-offset)**2,0),low,high,epsabs=1e-12,epsrel=1e-12)[0]/thickness
                                nquad+=1
                            delta=max(delta,abs(analytic-numeric));maxsignal=max(maxsignal,analytic)
                        sphere_max=max(sphere_max,delta);assert delta<=2e-12
                        sphere.append([radius,offset,spacing,thickness,len(centers),delta,maxsignal])
        assert len(sphere)==384
        summary=[]
        for thickness in config['thicknesses']:
            selected=[r for r in rows if r[2]==thickness]
            summary.append(dict(thickness=thickness,cases=len(selected),box_residual_exactly_zero=sum(F(r[5])==0 for r in selected),
                box_residual_positive=sum(F(r[5])>0 for r in selected),max_box_residual=max(r[6] for r in selected),
                max_projected_residual=max(r[7] for r in selected),max_center_shift_after_measurement_projection=max(r[8] for r in selected),
                projected_outside_0_1_cases=sum(r[9]<-2e-14 or r[10]>1+2e-14 for r in selected)))
        result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],counterexample=counter,
            all1080_piecewise_cases_completed=True,all384_sphere_groups_completed=True,quad_integrals=nquad,
            max_float_vs_fraction_weight_error=maxw,max_float_vs_fraction_measurement_error=maxy,
            max_float_vs_fraction_linear_interpolation_error=maxlinear,max_independent_projected_residual=maxproject,
            max_analytic_vs_quad_sphere_error=sphere_max,summary_by_thickness=summary,
            no_case_selected_or_removed=True,point_anchor_constraint_all1080_exact=True,
            measurement_consistency_not_anatomical_fidelity=True,box_not_scanner_model=True,
            medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
            CUDA_initialized=False,confirmation_patients_opened=False,lockedIXI_opened=False,
            publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-started,
            resources=budget(),source_bindings=[entry(out/'frozen_config.json'),entry(Path(__file__)),entry(HERE/'MEASUREMENT_CONTRACT_PROTOCOL.md'),
                entry(ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py')])
        dump(out/'cases.json',dict(piecewise_columns=['spacing','phase','thickness','profile','measurement_count','exact_max_box_residual',
            'float_max_box_residual','independent_projected_box_residual','projected_center_shift','projected_min','projected_max','projection_seconds'],
            piecewise_cases=rows,sphere_columns=['radius','offset','spacing','thickness','measurement_count','analytic_quad_error','max_integrated_signal'],sphere_groups=sphere))
        result['source_bindings'].append(entry(out/'cases.json'));dump(out/'receipt.json',result)
        assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<600000
        print(json.dumps({k:v for k,v in result.items() if k!='source_bindings'},ensure_ascii=False),flush=True)
    except Exception as error:
        dump(out/'failure.json',dict(complete=False,error=repr(error),piecewise_completed=len(rows),counterexample=counter,goal_status='active'))
        raise
if __name__=='__main__':main()
