"""Reverse intervals vs forward Boolean support of this U-Net, conditional on finite local normalization."""
import json, sys, time, traceback
from datetime import datetime, timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT, sha, resource_guard, torch, np, TaskUNet3D, PATCH
OUT = ROOT/'experiments/mc_rc_3d_finite_context_halo_audit_2026_10_07'

def backward_interval(i):
    lo=hi=i
    # Main output deepest path: decoder convs, upsampling, bottleneck convs, encoder stages.
    for _ in range(3):
        lo-=2;hi+=2
        lo//=2;hi//=2
    lo-=2;hi+=2
    for _ in range(3):
        lo*=2;hi=2*hi+1
        lo-=2;hi+=2
    return lo,hi

def graph_support(n):
    # Each row stores actual symbolic original-input dependencies of one spatial position.
    def conv(a):
        out=a.copy();out[1:] |= a[:-1];out[:-1] |= a[1:];return out
    def block(a):return conv(conv(a))
    x=np.eye(n,dtype=bool); skips=[]
    for depth in range(4):
        if depth:
            assert len(x)%2==0;x=x[::2] | x[1::2]
        x=block(x);skips.append(x.copy())
    for skip in reversed(skips[:-1]):
        x=np.repeat(x,2,axis=0);assert x.shape==skip.shape
        x=block(x|skip)
    return x

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        source_bindings=[dict(path=p,sha256=sha(ROOT/p)) for p in (
            'MC_RC_3D_FINITE_CONTEXT_HALO_PREPARATION_2026-10-07.md','experiments/mc_rc_3d_baseline_2026_10_07.py')],
        current_instance_norm_finite_halo_equivalence=False,conditional_on_local_fixed_normalization=True,
        actual_training_updates=0,actual_gpu_updates=0,mri_or_label_values_loaded=0,
        confirmation_patients_opened=False,publication_claim_confirmed=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        resource_guard();model=TaskUNet3D()
        convs=[m for m in model.modules() if isinstance(m,torch.nn.Conv3d) and m.kernel_size==(3,3,3)]
        ups=[m for m in model.modules() if isinstance(m,torch.nn.ConvTranspose3d)]
        norms=[m for m in model.modules() if isinstance(m,torch.nn.InstanceNorm3d)]
        assert len(convs)==14 and len(ups)==3 and len(norms)==14
        assert all(m.stride==(1,1,1) and m.padding==(1,1,1) and m.dilation==(1,1,1) for m in convs)
        assert all(m.kernel_size==(2,2,2) and m.stride==(2,2,2) and m.padding==(0,0,0) and m.output_padding==(0,0,0) for m in ups)
        full=graph_support(256);rows=[]
        for i in range(56,200):
            lo,hi=backward_interval(i);expected=np.zeros(256,bool);expected[lo:hi+1]=True
            assert np.array_equal(expected,full[i])
        for i in range(96,104):
            lo,hi=backward_interval(i)
            rows.append(dict(output_index=i,phase_mod8=i%8,input_min=lo,input_max=hi,
                support_width=hi-lo+1,left_radius=i-lo,right_radius=hi-i))
        assert all(backward_interval(i+8)==tuple(v+8 for v in backward_interval(i)) for i in range(56,192))
        r['phase_supports']=rows;r['forward_matrix_all_interior_positions_verified']=144
        radius=max(max(a['left_radius'],a['right_radius']) for a in rows);halo=((radius+7)//8)*8
        r['max_radius']=radius;r['conservative_aligned_halo']=halo
        local=graph_support(128); core=range(halo,128-halo);comparisons=[]
        for offset in (64,65):
            embedded=np.zeros((128,256),bool);embedded[:,offset:offset+128]=local
            equal=[np.array_equal(embedded[i],full[offset+i]) for i in core]
            comparisons.append(dict(tile_input_length=128,global_offset=offset,core_positions=len(equal),
                equal_dependency_sets=sum(equal),different_dependency_sets=len(equal)-sum(equal)))
        assert comparisons[0]['different_dependency_sets']==0 and comparisons[1]['different_dependency_sets']>0
        small=graph_support(64);embedded=np.zeros((64,256),bool);embedded[:,96:160]=small
        equal=[np.array_equal(embedded[i],full[96+i]) for i in range(64)]
        r['tile_dependency_comparisons']=comparisons
        r['length64_tile_matching_full_axis_positions']=sum(equal)
        assert sum(equal)==0
        r['current_patch']=list(PATCH);r['conservative_core_shape_for_tiling_all_three_axes']=[max(0,p-2*halo) for p in PATCH]
        r['whole_axis_exception']='When the tile covers the entire full-image axis, no internal crop boundary on that axis exists; core formula is for internal tiling.'
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        assert time.perf_counter()-started<=120;r['resources_after']=resource_guard();r['complete']=True
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    assert path.stat().st_size<1_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','phase_supports','max_radius','conservative_aligned_halo',
        'tile_dependency_comparisons','conservative_core_shape_for_tiling_all_three_axes','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
