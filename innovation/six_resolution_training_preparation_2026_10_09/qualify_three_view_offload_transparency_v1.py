"""Two fullpatch steps: builtin CPU saving vs audited saved tensor round-trips."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,time,json,gc,gzip,traceback,subprocess,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,original_cuda_initializer,read,entry,bind,resource_guard,state_hash,array_sha,CheckpointedTaskUNet3D
from mc_rc_3d_baseline_2026_10_07 import loss
from gin_reference_adapter_v1 import draw_parameters,gin,mean_target_kl

def main():
    torch.set_num_threads(1); assert torch.get_num_interop_threads()==1
    started=time.perf_counter(); out=HERE/'three_view_offload_transparency_attempt01'; out.mkdir(exist_ok=False)
    r=dict(complete=False,status='preparing',errors=[],branches=[],step_comparisons=[],
           MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
           synthetic_GPU_optimizer_updates=0,complete19series_GPU_three_view_qualified=False,
           medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active',
           confirmation_patients_opened=False,lockedIXI_opened=False,
           original_training_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False)
    def save():
        p=out/'receipt.json.tmp'; p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); p.replace(out/'receipt.json')
    def guard(cuda=True):
        v=resource_guard()
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'; fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
        assert size<7_000_000 and fs<20_000_000
        assert v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
        assert time.perf_counter()-started<360 and torch.get_num_threads()==torch.get_num_interop_threads()==1
        if cuda:
            free,total=torch.cuda.mem_get_info(); peak=torch.cuda.max_memory_reserved()
            assert free>=4_000_000_000 and peak<=2_500_000_000
            v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        return v
    def tensor_hash(x):
        return array_sha(x.detach().cpu().numpy())
    save()
    try:
        r['resources_before']=guard(False)
        oldp=HERE/'three_view_gpu_fullpatch_attempt01/receipt.json'; old=read(oldp)
        assert old['complete'] and not old['sequential_fullpatch_graph_completed']
        r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'THREE_VIEW_OFFLOAD_TRANSPARENCY_PROTOCOL_V1.md',oldp,
                            HERE/'gin_reference_adapter_v1.py',ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py',
                            ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py')]
        torch.manual_seed(20261009); base=CheckpointedTaskUNet3D()
        initial={n:v.detach().clone() for n,v in base.state_dict().items()}; del base
        initial_sha=state_hash(initial); assert initial_sha==old['common_initial_state_sha256']
        r['common_initial_state_sha256']=initial_sha
        tick=time.perf_counter(); shape=(2,1,64,128,128)
        x=torch.randn(shape,generator=torch.Generator().manual_seed(991))
        views=[gin(x,draw_parameters(shape,801+i))[0] for i in range(3)]
        vh=[tensor_hash(v) for v in views]; assert vh==old['shared_view_sha256']; r['shared_view_sha256']=vh
        axes=torch.meshgrid(torch.arange(64),torch.arange(128),torch.arange(128),indexing='ij')
        target=(((axes[0]-31.5)/16).square()+((axes[1]-63.5)/24).square()+((axes[2]-63.5)/24).square()<1).float()[None,None].repeat(2,1,1,1,1)
        th=tensor_hash(target); r['synthetic_target_sha256']=th; del axes,x
        r['synthetic_input_preparation_seconds']=time.perf_counter()-tick
        query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
        gpu=[list(map(int,v.split(','))) for v in query.stdout.strip().splitlines()]
        assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192; r['GPU_aggregate_before']=gpu
        torch.cuda._lazy_init=original_cuda_initializer; assert torch.cuda.is_available()
        free,total=torch.cuda.mem_get_info(); torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
        torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False; torch.backends.cudnn.deterministic=True
        audits=[]
        def branch(mode):
            q=dict(mode=mode,complete=False,errors=[],steps=[],actual_whole_model_forward_calls=0,
                   optimizer_updates=0,checkpoint_block_invocations={},save_pack_count=0,unpack_count=0)
            r['branches'].append(q)
            payload=[]; tick=time.perf_counter(); torch.cuda.reset_peak_memory_stats(); guard()
            model=CheckpointedTaskUNet3D(); model.load_state_dict(initial); model.to('cuda:0'); model.train()
            opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False)
            gv=[v.to('cuda:0') for v in views]; gt=target.to('cuda:0'); torch.cuda.synchronize()
            q['model_input_optimizer_preparation_seconds']=time.perf_counter()-tick
            counts=collections.Counter(); handles=[]
            def counter(name):
                def call(module,args):
                    counts[name]+=1
                return call
            for i,module in enumerate(model.encoders): handles.append(module.register_forward_pre_hook(counter('encoder.'+str(i))))
            for i,module in enumerate(model.decoders): handles.append(module.register_forward_pre_hook(counter('decoder.'+str(i))))
            live=[0]; peak=[0]; costs=dict(pack_copy_and_hash=0.,unpack_restore_and_hash=0.)
            class Packed:
                def __init__(self,cpu,index,device):
                    self.cpu=cpu; self.index=index; self.device=device
                    self.bytes=cpu.numel()*cpu.element_size(); live[0]+=self.bytes; peak[0]=max(peak[0],live[0])
                def __del__(self):
                    live[0]-=self.bytes
            def pack(value):
                tick=time.perf_counter(); cpu=value.detach().to('cpu',copy=True)
                index=len(audits); hashed=tensor_hash(cpu)
                audits.append(dict(id=index,step=step,mode=mode,shape=list(value.shape),dtype=str(value.dtype),
                                   original_device=str(value.device),original_stride=list(value.stride()),saved_stride=list(cpu.stride()),
                                   logical_bytes=value.numel()*value.element_size(),saved_sha256=hashed,unpack_events=[]))
                q['save_pack_count']+=1; costs['pack_copy_and_hash']+=time.perf_counter()-tick
                if q['save_pack_count']%16==0: guard()
                return Packed(cpu,index,value.device)
            def unpack(saved):
                tick=time.perf_counter(); a=audits[saved.index]
                assert list(saved.cpu.shape)==a['shape'] and str(saved.cpu.dtype)==a['dtype']
                assert tensor_hash(saved.cpu)==a['saved_sha256']
                restored=saved.cpu.to(saved.device,copy=True); roundtrip=restored.detach().cpu()
                same=torch.equal(saved.cpu,roundtrip); rh=tensor_hash(roundtrip)
                assert same and rh==a['saved_sha256']
                assert restored.device==saved.device and restored.dtype==saved.cpu.dtype and restored.shape==saved.cpu.shape
                a['unpack_events'].append(dict(restored_sha256=rh,roundtrip_bitwise_equal=same,
                                             CPU_saved_value_unchanged=True,restored_device=str(restored.device)))
                q['unpack_count']+=1; costs['unpack_restore_and_hash']+=time.perf_counter()-tick
                del roundtrip
                if q['unpack_count']%16==0: guard()
                return restored
            for step in range(2):
                guard(); opt.zero_grad(set_to_none=True); before_counts=dict(counts); tick=time.perf_counter()
                context=(torch.autograd.graph.save_on_cpu(pin_memory=False) if mode=='builtin_save_on_cpu' else
                         torch.autograd.graph.saved_tensors_hooks(pack,unpack))
                with context:
                    separate=[]
                    for view in gv:
                        separate.append(model(view)); q['actual_whole_model_forward_calls']+=1; guard()
                    final=torch.stack([v[0] for v in separate],dim=0)
                    total_loss=loss(separate[0],gt)+.1*mean_target_kl(torch.cat((torch.zeros_like(final),final),dim=2))
                    total_loss.backward()
                torch.cuda.synchronize(); whole=time.perf_counter()-tick; guard()
                tick=time.perf_counter(); probability=[torch.stack([v[d].detach().sigmoid().cpu() for v in separate],dim=0) for d in range(3)]
                true_loss=float(total_loss.detach()); grad={n:None if p.grad is None else p.grad.detach().cpu().clone() for n,p in model.named_parameters()}
                assert __import__('math').isfinite(true_loss) and all(v is None or torch.isfinite(v).all() for v in grad.values())
                capture=time.perf_counter()-tick; tick=time.perf_counter(); opt.step(); torch.cuda.synchronize(); optim=time.perf_counter()-tick
                q['optimizer_updates']+=1; r['synthetic_GPU_optimizer_updates']+=1; guard()
                tick=time.perf_counter(); params={n:p.detach().cpu().clone() for n,p in model.named_parameters()}
                moments={n:{k:v.detach().cpu().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters() if p in opt.state}
                state_capture=time.perf_counter()-tick; tick=time.perf_counter()
                assert [tensor_hash(v) for v in gv]==vh and tensor_hash(gt)==th
                hash_seconds=time.perf_counter()-tick
                info=dict(step=step,true_loss=true_loss,full_graph_forward_loss_backward_seconds=whole,
                          probability_and_gradient_capture_seconds=capture,AdamW_seconds=optim,
                          parameter_moment_capture_seconds=state_capture,input_immutability_hash_seconds=hash_seconds,
                          input_target_unchanged=True,state_sha256=state_hash(model.state_dict()),
                          block_invocations={n:counts[n]-before_counts.get(n,0) for n in counts},resources_after=guard())
                q['steps'].append(info); payload.append(dict(probability=probability,gradient=grad,parameters=params,moments=moments))
                del separate,final,total_loss,probability,grad,params,moments
                gc.collect(); guard(); print(json.dumps(dict(mode=mode,step=step,complete=True,loss=true_loss,
                                      GPU_peak_reserved_bytes=torch.cuda.max_memory_reserved())),flush=True)
            for h in handles: h.remove()
            del model,opt,gv,gt,context; gc.collect(); torch.cuda.synchronize(); guard()
            q.update(complete=True,checkpoint_block_invocations=dict(counts),hook_cost_seconds_included_in_graph=costs,
                     CPU_saved_payload_peak_logical_bytes=peak[0],CPU_saved_payload_final_logical_bytes=live[0],resources_after=guard())
            assert live[0]==0
            return q,payload
        payloads=[]
        for mode in ('builtin_save_on_cpu','audited_CPU_saved_tensors_hooks'):
            q,payload=branch(mode); payloads.append(payload); save()
            gc.collect(); torch.cuda.empty_cache(); guard()
        assert all(q['complete'] and q['optimizer_updates']==2 for q in r['branches'])
        for step,(a,b) in enumerate(zip(*payloads)):
            fields=[]
            assert a['gradient'].keys()==b['gradient'].keys()
            for name,av in a['gradient'].items():
                bv=b['gradient'][name]; assert (av is None)==(bv is None)
                ge=0. if av is None else float((av-bv).abs().max())
                pe=float((a['parameters'][name]-b['parameters'][name]).abs().max())
                am=a['moments'].get(name,{}); bm=b['moments'].get(name,{})
                assert am.keys()==bm.keys(); comparisons=[]
                for k,v in am.items():
                    if k=='step': assert torch.equal(v,bm[k])
                    comparisons.append(dict(field=k,max_error=float((v-bm[k]).abs().max()),bitwise_equal=torch.equal(v,bm[k])))
                fields.append(dict(name=name,gradient_error=ge,parameter_error=pe,optimizer_fields=comparisons))
            probability_error=max(float((v-w).abs().max()) for v,w in zip(a['probability'],b['probability']))
            loss_error=abs(r['branches'][0]['steps'][step]['true_loss']-r['branches'][1]['steps'][step]['true_loss'])
            maxima=dict(probability=probability_error,loss=loss_error,gradient=max(v['gradient_error'] for v in fields),
                        parameter=max(v['parameter_error'] for v in fields),optimizer_state=max(c['max_error'] for v in fields for c in v['optimizer_fields']))
            r['step_comparisons'].append(dict(step=step,max_errors=maxima,parameter_comparisons=fields,
                                             optimizer_fields_compared=sum(len(v['optimizer_fields']) for v in fields)))
            save(); assert all(v<=3e-6 for v in maxima.values()), maxima
        assert len(audits)>0 and sum(len(a['unpack_events']) for a in audits)>0
        journal=out/'saved_tensors.jsonl.gz'
        with journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
            for a in audits: f.write((json.dumps(a,separators=(',',':'))+'\n').encode('utf-8'))
        r.update(saved_tensor_journal=entry(journal),packed_tensors=len(audits),
                 unpack_events=sum(len(a['unpack_events']) for a in audits),
                 packed_without_unpack=sum(not a['unpack_events'] for a in audits),
                 all_actual_unpacks_bitwise_content_and_shape_dtype_device_verified=True,
                 builtin_and_audited_two_steps_strict_numeric_gates_passed=True)
        for b in r['source_bindings']: bind(b)
        r.update(complete=True,status='completed',resources_after=guard())
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e)); r.update(status='failed',traceback=traceback.format_exc())
        if 'audits' in locals() and audits:
            failure=out/'failure_saved_tensors.jsonl.gz'
            with gzip.open(failure,'wt',encoding='utf-8') as f:
                for a in audits: f.write(json.dumps(a)+'\n')
            r['failure_journal']=entry(failure)
    r['elapsed_seconds']=time.perf_counter()-started; save()
    print(json.dumps({k:r.get(k) for k in ('complete','status','errors','synthetic_GPU_optimizer_updates','packed_tensors','unpack_events','elapsed_seconds')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':
    raise SystemExit(main())
