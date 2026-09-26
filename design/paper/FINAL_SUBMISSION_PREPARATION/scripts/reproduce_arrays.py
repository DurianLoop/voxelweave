"""CPU-only, independent reconstruction of observation tables from saved arrays.

Historical CSVs supply keys/selection and assertion targets, never metric values.
No network inference, training, or additional scientific analysis is performed.
"""
from common import *
import argparse
UP=PAPER/'CVPR/archive/CVPR_UPGRADE/outputs'
DEST=OUT/'array_reproduced';DEST.mkdir(exist_ok=True)
CHECKS=[];BINDINGS=[]

def array(path):
    h=sha(path);meta=read(path.with_suffix('.json'))
    assert h==meta['sha256'],path
    BINDINGS.append({'path':path.relative_to(P).as_posix(),'sha256':h})
    return np.load(path),meta

def oldmetrics(a,b,y,m):
    # Retain historical float32 subtraction BEFORE double-precision energies.
    e=(a-y)[m].astype(float);f=(b-y)[m].astype(float)
    total=(np.dot(e,e)+np.dot(f,f))/2
    o=np.dot((e-f)/2,(e-f)/2)/total
    return dict(score=abs(e-f).mean(),error=(abs(e).mean()+abs(f).mean())/2,
                cosine=np.dot(e,f)/np.sqrt(np.dot(e,e)*np.dot(f,f)),
                observable_fraction=o,shared_fraction=1-o,
                native_disagreement=float(abs(a-b)[m].mean()),
                phase0_error=float(abs(a-y)[m].mean()))

def compare(name,old,new,keys,cols,atol=1e-7,rtol=1e-6):
    a=old.set_index(keys);b=new.set_index(keys)
    assert a.index.is_unique and b.index.is_unique,(name,'duplicate keys')
    assert len(a)==len(b) and set(a.index)==set(b.index),(name,'key mismatch',len(a),len(b))
    b=b.loc[a.index]
    for c in cols:
        x=a[c].to_numpy(float);y=b[c].to_numpy(float);d=abs(x-y)
        ok=np.isclose(x,y,atol=atol,rtol=rtol,equal_nan=True)
        CHECKS.append({'table':name,'column':c,'observations':len(a),'maximum_abs_difference':np.nanmax(d),
                       'mean_abs_difference':np.nanmean(d),'atol':atol,'rtol':rtol,'failed_observations':int((~ok).sum()),'status':'PASS' if ok.all() else 'FAIL'})
    new.to_csv(DEST/name,index=False)
    print(name,len(new),'failed columns',sum(r['status']=='FAIL' for r in CHECKS if r['table']==name),flush=True)

def controls():
    files=['clean_max_overlap_per_plane.csv','clean_max_overlap_ixi_per_plane.csv','overlap_covariance_per_plane.csv','overlap_covariance_ixi_per_plane.csv']
    templates={n:pd.read_csv(UP/n) for n in files}
    for n in files[2:]:templates[n]=templates[n].query('overlap==0').copy()
    p4=PAPER/'ARCHIVE/PLANS/PLAN02_TO_PLAN04/plan4_outputs'
    for n in ['disjoint_anchor_per_plane.csv','ningxia_disjoint_per_plane.csv']:
        d=pd.read_csv(p4/n).rename(columns={'case':'case_id','target_model':'model'})
        if 'dataset' not in d:d['dataset']='ningxia'
        templates[n]=d
    cache={};generated={n:[] for n in templates}
    # A file is opened once; only declared historical rows are measured.
    for file in sorted((BASEOUT/'legacy_control_arrays').glob('*.npz')):
        f,meta=array(file);ds,model,c=meta['dataset'],meta['model'],meta['case']
        with f:
            p0,pf,p2,y=f['p0'],f['flip'],f['p2'],f['target']
            for n,t in templates.items():
                q=t[(t.dataset==ds)&(t.model==model)&(t.case_id==c)]
                for r in q.to_dict('records'):
                    z=r['z'];a=p0[:,:,z];m=abs(a)>.01*max(float(abs(a).max()),1e-6)
                    b=pf[:,:,z] if n.startswith('clean') else p2[:,:,z-2]
                    v=oldmetrics(a,b,y[:,:,z],m)
                    if n.startswith('clean'):r.update({k:v[k] for k in ['score','error','cosine','shared_fraction','observable_fraction']})
                    elif n.startswith('overlap'):r.update(disagreement_mae=v['score'],mae=v['error'],error_cosine=v['cosine'],shared_fraction=v['shared_fraction'],observable_fraction=v['observable_fraction'])
                    else:r.update(disjoint_inconsistency=v['native_disagreement'],phase0_error=v['phase0_error'])
                    generated[n].append(r)
    for n,t in templates.items():
        cols=['score','error','cosine','shared_fraction','observable_fraction'] if n.startswith('clean') else (['disagreement_mae','mae','error_cosine','shared_fraction','observable_fraction'] if n.startswith('overlap') else ['disjoint_inconsistency','phase0_error'])
        compare(n,t,pd.DataFrame(generated[n]),['dataset','case_id','model','z'],cols)

def legacy_influence():
    name='plan6_neural_shared_influence_confirm3_per_case_config.csv';old=pd.read_csv(UP/name);rows=[]
    for i,file in enumerate(sorted((BASEOUT/'legacy_influence_arrays').glob('*.npz'))):
        f,meta=array(file)
        with f:
            pred,resp,y,m=f['predictions'],f['responses'],f['target'],f['mask']
            for ci,ctx in enumerate(CONTEXTS):
                na=nb=num=0.
                for seed in range(4):
                    for a in range(2):na+=float(resp[0,a,seed]@resp[0,a,seed]);nb+=float(resp[ci,a,seed]@resp[ci,a,seed])
                    for off in set(REF)&set(ctx):num+=float(resp[0,REF.index(off),seed]@resp[ci,ctx.index(off),seed])
                v=oldmetrics(pred[0],pred[ci],y,m)
                rows.append({k:meta[k] for k in ['dataset','model','case','z','patient_cluster']}|dict(context=str(ctx),span=ctx[1]-ctx[0],asymmetry=abs(sum(ctx)),overlap_count=len(set(REF)&set(ctx)),neural_influence_cosine=num/np.sqrt(na*nb),error_cosine=v['cosine'],observable_fraction=v['observable_fraction'],shared_fraction=v['shared_fraction'],paired_error_mae=v['error'],disagreement_mae=v['native_disagreement']))
        if i%100==0:print('Response-array reproduction',i,flush=True)
    new=pd.DataFrame(rows)
    # Preserve historical row order: it determines the old bootstrap draw mapping.
    keys=['dataset','case','model','z','context'];new=new.set_index(keys).loc[old.set_index(keys).index].reset_index()
    compare(name,old,new,keys,['neural_influence_cosine','error_cosine','observable_fraction','shared_fraction','paired_error_mae','disagreement_mae'])

def architecture():
    p9=PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs';p11=PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs'
    paths=[p9/'p9_disjoint_shared_per_plane.csv',p9/'p9_disjoint_shared_per_plane_transformer_reference.csv',p11/'p11_ixi_clean_per_plane_full.csv']
    olds={p.name:pd.read_csv(p).rename(columns={'target_z':'z'}) for p in paths};rows=[]
    for r in read(P/'case_registry.json'):
        with np.load(P/r['cross_targets']) as target:y,m=target['gt'],target['mask']
        for model in MODELS:
            f,meta=array(BASEOUT/'phase_arrays'/f'{r["dataset"]}_{model}_{r["case"]}.npz')
            with f:
                a,s,d=f['p0_legacy'],f['flip'],f['p2_legacy'];full=bool(f['full_arrays'])
                for j,z in enumerate(r['targets']):
                    for cond,b in [('shared',s),('disjoint',d)]:
                        aa=a[:,:,z] if full else a[j];bb=b[:,:,z if cond=='shared' else z-2] if full else b[j]
                        v=oldmetrics(aa,bb,y[j],m[j]);rows.append(dict(dataset=r['dataset'],case=r['case'],model=model,z=z,condition=cond,paired_error_mae=v['error'],prediction_disagreement_mae=v['native_disagreement'],error_cosine=v['cosine'],shared_error_fraction=v['shared_fraction'],observable_error_fraction=v['observable_fraction']))
    allnew=pd.DataFrame(rows)
    for n,old in olds.items():
        ds='ixi' if n.startswith('p11') else 'fastmri';new=allnew[(allnew.dataset==ds)&allnew.model.isin(old.model.unique())].copy()
        # Source case keys omit the NIfTI suffix in these experiments.
        if old.case.iloc[0].endswith('.nii.gz'):new['case']+='.nii.gz'
        compare(n,old,new,['case','model','z','condition'],['paired_error_mae','prediction_disagreement_mae','error_cosine','shared_error_fraction','observable_error_fraction'])

def main():
    guard();ap=argparse.ArgumentParser();ap.add_argument('--part',choices=['all','controls','influence','architecture'],default='all');a=ap.parse_args()
    for name,fn in [('controls',controls),('influence',legacy_influence),('architecture',architecture)]:
        if a.part in ['all',name]:
            fn()
            pd.DataFrame(CHECKS).to_csv(OUT/f'array_checks_{a.part}.csv',index=False);write(OUT/f'array_bindings_{a.part}.json',BINDINGS)
    pd.DataFrame(CHECKS).to_csv(OUT/f'array_checks_{a.part}.csv',index=False);write(OUT/f'array_bindings_{a.part}.json',BINDINGS)
    if any(r['status']=='FAIL' for r in CHECKS):raise SystemExit('Historical numerical differences require investigation; original evidence remains unchanged.')
if __name__=='__main__':main()
