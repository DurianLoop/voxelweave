"""Complete 19-series pending qualification: true GT, cold init, CPU/GPU graph, two steps."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,time,json,gzip,gc,io,base64,traceback,subprocess,zlib,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,original_cuda_initializer,entry,bind,read,resource_guard,state_hash,array_sha,CheckpointedTaskUNet3D,np
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,sample_batch,batch_rng,QPATH
from mc_rc_3d_baseline_2026_10_07 import loss
sys.path.insert(0,str(ROOT/'development_optimizer_coverage_2026_10_09'))
from qualify_all_development_optimizer import equal_tree,optimizer_hash
from gin_reference_adapter_v1 import draw_parameters,gin,mean_target_kl
from gin_cpu_differentiable_reference_v1 import FunctionalCPUReference,independent_total_loss

WALL=21600;JOURNAL_LIMIT=1_200_000;RECEIPT_LIMIT=350_000

def full_numpy_target(native,grid):
    source=native.transpose(2,0,1);sizes=grid['unpadded_shape_zrc']
    axes=[np.clip(np.floor((np.arange(n,dtype=np.float64)+.5)*old/n).astype(np.int64),0,old-1) for old,n in zip(source.shape,sizes)]
    return np.pad(source[np.ix_(*axes)],grid['padding'],mode='constant',constant_values=0).astype(np.float32)

def encode_parameter(value):
    a=value.detach().cpu().numpy();blob=a.astype('<f4',copy=False).tobytes()
    text=base64.b64encode(blob).decode('ascii');b=np.frombuffer(base64.b64decode(text),dtype='<f4').reshape(a.shape)
    assert np.array_equal(a.view(np.uint32),b.view(np.uint32))
    return dict(shape=list(a.shape),dtype='little_endian_float32',sha256=array_sha(a),payload_base64=text)

def parameter_record(p):
    return dict(alpha=encode_parameter(p['alpha']),layers=[dict(k=v['k'],weight=encode_parameter(v['weight']),bias=encode_parameter(v['bias'])) for v in p['layers']])

def main():
    os.environ['CUDA_VISIBLE_DEVICES']='0';torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    started=time.perf_counter();out=HERE/'gin19_real_graph_attempt02';out.mkdir(exist_ok=False);journal=out/'steps.jsonl.gz'
    r=dict(complete=False,status='preparing',errors=[],branches=[],step_comparisons=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,
           parent_arrays_loaded=0,GPU_optimizer_updates=0,CPU_reference_optimizer_updates=0,
           GPU_whole_model_forwards=0,CPU_reference_whole_model_forwards=0,in_memory_captures=0,
           formal_training_launched=False,complete19series_GPU_three_view_qualified=False,
           medical_effect_scored=False,confirmation_patients_opened=False,lockedIXI_opened=False,
           original_training_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False,
           publication_claim_confirmed=False,goal_status='active')
    def save():
        blob=json.dumps(r,ensure_ascii=False,indent=2)+'\n';assert len(blob.encode())<RECEIPT_LIMIT
        p=out/'receipt.json.tmp';p.write_text(blob,encoding='utf-8');p.replace(out/'receipt.json')
    def guard(cuda=True):
        v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
        assert size<7_000_000 and fs<20_000_000
        assert v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
        assert time.perf_counter()-started<WALL and torch.get_num_threads()==torch.get_num_interop_threads()==1
        if journal.exists():assert journal.stat().st_size<JOURNAL_LIMIT
        if cuda:
            free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved()
            assert free>=4_000_000_000 and peak<=2_500_000_000
            v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        return v
    def hash_tensor(v):return array_sha(v.detach().cpu().numpy())
    save()
    try:
        r['resources_before']=guard(False)
        planp=HERE/'gin19_metadata_preparation_attempt01/manifest.json';plan=read(planp)
        verifiedp=HERE/'gin_cpu_reference_verification_attempt01/receipt.json';verified=read(verifiedp)
        assert plan['complete'] and plan['unique_development_series']==19 and plan['unique_development_patients']==11
        assert verified['complete'] and not verified['errors'] and verified['all_two_steps54_parameters162_optimizer_fields_strict_passed']
        cases=development_cases();assert len(cases)==19 and len({v['patient'] for v,row in cases})==11
        assert [(v['patient'],v['uid']) for v,row in cases]==[(v['patient'],v['uid']) for v in plan['cases']]
        for b in plan['source_bindings']:bind(b)
        refs={a['kind']:{v['uid']:v for v in a['cache_records']} for a in read(QPATH)['arms']}
        oldcfg=read(ROOT/'development_optimizer_coverage_2026_10_09/coverage_attempt01/frozen_config.json')
        sources={Path(__file__),HERE/'GIN19_REAL_EXECUTION_PROTOCOL_V2.md',planp,verifiedp,QPATH,HERE/'gin_cpu_differentiable_reference_v1.py',HERE/'gin_reference_adapter_v1.py'}
        sources.update((HERE/'qualify_gin19_real_graph_v1.py',HERE/'gin19_real_graph_attempt01/receipt.json',HERE/'prepare_gin19_real_graph_v2.py'))
        for b in oldcfg['source_bindings']:sources.add(bind(b))
        frozen=dict(expected_series=19,expected_patients=11,kinds=plan['kinds'],cases=plan['cases'],
                    expected_GPU_updates=76,expected_CPU_reference_updates=76,expected_GPU_whole_model_forwards=228,
                    expected_CPU_reference_whole_model_forwards=228,cold_initial_seed=20261009,
                    wall_seconds=WALL,journal_limit_bytes=JOURNAL_LIMIT,receipt_limit_bytes=RECEIPT_LIMIT,
                    probability_gradient_parameter_optimizer_gate=3e-6,confirmation_opened=False,
                    source_bindings=[entry(p) for p in sorted(sources)])
        blob=json.dumps(frozen,ensure_ascii=False,separators=(',',':'))+'\n';assert len(blob.encode())<250_000 and json.loads(blob)==frozen
        (out/'frozen_config.json').write_text(blob,encoding='utf-8');r['source_bindings']=frozen['source_bindings']
        torch.manual_seed(20261009);base=CheckpointedTaskUNet3D();initial={n:v.detach().clone() for n,v in base.state_dict().items()};del base
        initial_sha=state_hash(initial);assert initial_sha=='2f7987cf7b4f1d6160170a304df9b1dd4d6d88bb86f490888a3dd68f50b9f59a'
        r['cold_initial_state_sha256']=initial_sha
        query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
        aggregate=[list(map(int,v.split(','))) for v in query.stdout.strip().splitlines()]
        assert len(aggregate)==1 and aggregate[0][0]==0 and aggregate[0][1]>=8192;r['GPU_aggregate_before']=aggregate
        os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
        free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;r['status']='running';save()
        with journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=6) as stream:
            def record(value):
                stream.write((json.dumps(value,separators=(',',':'))+'\n').encode());stream.flush(zlib.Z_SYNC_FLUSH);raw.flush();guard()
            for selected,(case,row) in zip(plan['cases'],cases):
                guard();tick=time.perf_counter();grid=lattice(case);native_label=read_reference_label(case)
                target=physical_label(native_label,grid);independent=full_numpy_target(native_label,grid)
                assert np.array_equal(target.view(np.uint32),independent.view(np.uint32));del native_label,independent
                th=array_sha(target);assert th==refs['native_reference'][case['uid']]['label_sha256']==refs['raw_pchip'][case['uid']]['label_sha256']
                gt_seconds=time.perf_counter()-tick;r['GT_arrays_loaded']+=1
                for kind in plan['kinds']:
                    guard();branch_start=time.perf_counter();tick=time.perf_counter();image,stats=source_image(case,row,kind)
                    cache=physical_mr(image,grid);del image;ih=array_sha(cache);assert ih==refs[kind][case['uid']]['input_sha256']
                    mr_seconds=time.perf_counter()-tick;r['MRI_arrays_loaded']+=1
                    batches=[];prep_cost=[]
                    for si,step in enumerate(selected['scheduled_steps']):
                        tick=time.perf_counter();x,y,geometry=sample_batch(cache,target,batch_rng(19998+step));mother=hash_tensor(y)
                        fields=selected['original_fields'][si]
                        assert all(geometry[p]==fields[p]['geometry'] and mother==fields[p]['mother_label_sha256'] and
                                   array_sha(y.numpy()[p,0])==fields[p]['target_label_sha256'] for p in range(2))
                        crop_seconds=time.perf_counter()-tick;tick=time.perf_counter();parameters=[draw_parameters(x.shape,seed) for seed in selected['three_view_parameter_seeds'][si]]
                        parameter_seconds=time.perf_counter()-tick;tick=time.perf_counter();views=[];norms=[]
                        for p in parameters:
                            view,norm=gin(x,p);assert torch.isfinite(view).all();views.append(view)
                            norms.append({k:encode_parameter(v) for k,v in norm.items()})
                        gin_seconds=time.perf_counter()-tick;viewhashes=[hash_tensor(v) for v in views];assert hash_tensor(y)==mother
                        record(dict(type='prepared_three_views',case=selected['case'],patient=case['patient'],uid=case['uid'],kind=kind,
                                    step_index=si,scheduled_step=step,original_geometry=geometry,mother_target_sha256=mother,
                                    view_sha256=viewhashes,parameters=[parameter_record(p) for p in parameters],norms=norms,
                                    GT_not_used_to_generate_GIN=True,coordinates_and_target_unchanged=True))
                        batches.append(dict(views=views,target=y,view_hashes=viewhashes,mother_sha=mother))
                        prep_cost.append(dict(basic_crop_and_mother_check=crop_seconds,GIN_parameter_draw=parameter_seconds,GIN_convolution_and_norm=gin_seconds))
                        del x,parameters,norms;guard()
                    branch=dict(case=selected['case'],patient=case['patient'],uid=case['uid'],kind=kind,complete=False,
                                GT_load_reference_check_seconds=gt_seconds,MRI_load_resample_seconds=mr_seconds,view_preparation_cost=prep_cost,
                                input_sha256=ih,whole_target_sha256=th,device_branches=[])
                    r['branches'].append(branch);save();payloads=[]
                    for device in ('cpu','cuda:0'):
                        tick=time.perf_counter();counts=collections.Counter();handles=[]
                        model=FunctionalCPUReference(initial) if device=='cpu' else CheckpointedTaskUNet3D()
                        if device!='cpu':
                            model.load_state_dict(initial);model.to(device);model.train();torch.cuda.reset_peak_memory_stats()
                            def count(name):
                                def h(module,args):counts[name]+=1;guard()
                                return h
                            for i,mod in enumerate(model.encoders):handles.append(mod.register_forward_pre_hook(count('encoder.'+str(i))))
                            for i,mod in enumerate(model.decoders):handles.append(mod.register_forward_pre_hook(count('decoder.'+str(i))))
                        assert state_hash(model.state_dict())==initial_sha
                        opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False)
                        oracle={n:[p.detach().cpu().numpy().astype(np.float64).copy(),np.zeros(tuple(p.shape),np.float64),np.zeros(tuple(p.shape),np.float64)] for n,p in model.named_parameters()}
                        q=dict(device=device,complete=False,steps=[],model_optimizer_preparation_seconds=time.perf_counter()-tick)
                        branch['device_branches'].append(q);states=[]
                        for si,batch in enumerate(batches):
                            guard();opt.zero_grad(set_to_none=True);tick=time.perf_counter()
                            inputs=[v.to(device) for v in batch['views']];label=batch['target'].to(device)
                            if device!='cpu':torch.cuda.synchronize()
                            transfer=time.perf_counter()-tick;tick=time.perf_counter()
                            context=torch.autograd.graph.save_on_cpu(pin_memory=False) if device!='cpu' else __import__('contextlib').nullcontext()
                            with context:
                                outputs=[]
                                for vi,v in enumerate(inputs):
                                    outputs.append(model(v));r['CPU_reference_whole_model_forwards' if device=='cpu' else 'GPU_whole_model_forwards']+=1
                                    guard();print(json.dumps(dict(case=selected['case'],kind=kind,device=device,step=si,view=vi,
                                                               forward_completed=True,elapsed_seconds=time.perf_counter()-started)),flush=True)
                                if device=='cpu':value=independent_total_loss(outputs,label)
                                else:
                                    final=torch.stack([v[0] for v in outputs]);value=loss(outputs[0],label)+.1*mean_target_kl(torch.cat((torch.zeros_like(final),final),2))
                                value.backward()
                            if device!='cpu':torch.cuda.synchronize()
                            graph_seconds=time.perf_counter()-tick;guard();tick=time.perf_counter()
                            gradients={n:p.grad.detach().cpu().clone() for n,p in model.named_parameters()}
                            assert all(torch.isfinite(v).all() for v in gradients.values())
                            probs=[torch.stack([v[d].detach().sigmoid().cpu() for v in outputs]) for d in range(3)]
                            lossvalue=float(value.detach());capture_seconds=time.perf_counter()-tick
                            tick=time.perf_counter();opt.step()
                            if device!='cpu':torch.cuda.synchronize()
                            opt_seconds=time.perf_counter()-tick;r['CPU_reference_optimizer_updates' if device=='cpu' else 'GPU_optimizer_updates']+=1
                            tick=time.perf_counter();checks=[]
                            for n,p in model.named_parameters():
                                expected,m,v=oracle[n];g=gradients[n].numpy().astype(np.float64)
                                m*=.9;m+=.1*g;v*=.999;v+=.001*g*g;expected*=1-1e-8
                                expected-=1e-4*(m/(1-.9**(si+1)))/(np.sqrt(v/(1-.999**(si+1)))+1e-8)
                                st=opt.state[p];assert int(st['step'])==si+1
                                errors=dict(parameter=float(np.max(np.abs(p.detach().cpu().numpy()-expected))),
                                            exp_avg=float(np.max(np.abs(st['exp_avg'].detach().cpu().numpy()-m))),
                                            exp_avg_sq=float(np.max(np.abs(st['exp_avg_sq'].detach().cpu().numpy()-v))))
                                checks.append(dict(name=n,errors=errors));assert all(e<=3e-6 for e in errors.values()),(n,errors)
                            oracle_seconds=time.perf_counter()-tick;tick=time.perf_counter()
                            tree=dict(model=model.state_dict(),optimizer=opt.state_dict());buf=io.BytesIO();torch.save(tree,buf);nbytes=buf.tell();buf.seek(0)
                            restored=torch.load(buf,map_location='cpu',weights_only=True);assert equal_tree(tree,restored);r['in_memory_captures']+=1
                            params={n:p.detach().cpu().clone() for n,p in model.named_parameters()}
                            moments={n:{k:v.detach().cpu().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters()}
                            sh=state_hash(model.state_dict());oh=optimizer_hash(opt,model);restore_seconds=time.perf_counter()-tick
                            assert [hash_tensor(v) for v in inputs]==batch['view_hashes'] and hash_tensor(label)==batch['mother_sha']
                            data=dict(step=si,loss=lossvalue,ending_state_sha256=sh,optimizer_state_sha256=oh,
                                      original_input_and_mother_unchanged=True,independent_NumPy_AdamW_checks=checks,
                                      in_memory_capture_reload_bitwise_equal=True,capture_bytes=nbytes,
                                      cost_seconds=dict(transfer_sync=transfer,complete_graph=graph_seconds,probability_gradient_capture=capture_seconds,
                                                        AdamW_sync=opt_seconds,independent_numpy_update=oracle_seconds,state_capture_reload_and_hash=restore_seconds),resources=guard())
                            q['steps'].append({k:v for k,v in data.items() if k!='independent_NumPy_AdamW_checks'})
                            q['steps'][-1]['all54_NumPy_checks_logged_in_journal']=True
                            record(dict(type='actual_two_step_optimizer',case=selected['case'],kind=kind,device=device,**data))
                            states.append(dict(gradients=gradients,probs=probs,params=params,moments=moments))
                            del inputs,label,outputs,value,tree,buf,restored,params,moments,gradients,probs;gc.collect();guard();save()
                        for h in handles:h.remove()
                        q.update(complete=True,block_calls=model.block_calls if device=='cpu' else sum(counts.values()),
                                 whole_model_calls=model.whole_model_calls if device=='cpu' else 6)
                        payloads.append(states);del model,opt,oracle;gc.collect()
                        if device!='cpu':torch.cuda.empty_cache()
                        guard();save()
                    for si,(a,b) in enumerate(zip(*payloads)):
                        checks=[]
                        for n,av in a['params'].items():
                            fields=[]
                            for k,v in a['moments'][n].items():
                                if k=='step':assert torch.equal(v,b['moments'][n][k])
                                fields.append(dict(field=k,max_error=float((v-b['moments'][n][k]).abs().max())))
                            difference=(av-b['params'][n]).abs();index=int(difference.reshape(-1).argmax())
                            checks.append(dict(name=n,gradient_error=float((a['gradients'][n]-b['gradients'][n]).abs().max()),
                                               parameter_error=float(difference.max()),optimizer_fields=fields,
                                               maximum_parameter_flat_index=index,CPU_parameter_at_index=float(av.reshape(-1)[index]),
                                               GPU_parameter_at_index=float(b['params'][n].reshape(-1)[index]),
                                               CPU_gradient_at_index=float(a['gradients'][n].reshape(-1)[index]),
                                               GPU_gradient_at_index=float(b['gradients'][n].reshape(-1)[index])))
                        maxima=dict(probability=max(float((v-w).abs().max()) for v,w in zip(a['probs'],b['probs'])),
                                    loss=abs(branch['device_branches'][0]['steps'][si]['loss']-branch['device_branches'][1]['steps'][si]['loss']),
                                    gradient=max(v['gradient_error'] for v in checks),parameter=max(v['parameter_error'] for v in checks),
                                    optimizer_state=max(f['max_error'] for v in checks for f in v['optimizer_fields']))
                        binary=sum(int(torch.count_nonzero((v>=.5)!=(w>=.5))) for v,w in zip(a['probs'],b['probs']))
                        comparison=dict(case=selected['case'],kind=kind,step=si,max_errors=maxima,binary_disagreements=binary,
                                        all54_parameter_comparisons=checks,optimizer_fields_compared=162)
                        r['step_comparisons'].append({k:v for k,v in comparison.items() if k!='all54_parameter_comparisons'})
                        r['step_comparisons'][-1]['worst_parameter_rows']=sorted(checks,key=lambda v:v['parameter_error'],reverse=True)[:3]
                        r['step_comparisons'][-1]['all54_comparison_rows_logged_in_journal']=True
                        record(dict(type='CPU_GPU_strict_comparison',**comparison));save()
                        print(json.dumps(dict(case=selected['case'],kind=kind,step=si,max_errors=maxima,binary_disagreements=binary)),flush=True)
                        assert all(v<=3e-6 for v in maxima.values()) and binary==0,(maxima,binary)
                    assert array_sha(cache)==ih and array_sha(target)==th
                    branch.update(complete=True,elapsed_seconds=time.perf_counter()-branch_start);save()
                    if len(r['branches'])==1:
                        r['first_complete_branch_full38_wall_extrapolation_seconds']=branch['elapsed_seconds']*38
                    del cache,batches,payloads,states,a,b;gc.collect();guard()
                del target;gc.collect();guard()
            raw.flush();os.fsync(raw.fileno())
        assert len(r['branches'])==38 and all(b['complete'] for b in r['branches'])
        assert r['CPU_reference_optimizer_updates']==r['GPU_optimizer_updates']==76
        assert r['CPU_reference_whole_model_forwards']==r['GPU_whole_model_forwards']==228
        assert len(r['step_comparisons'])==76 and r['in_memory_captures']==152
        for b in r['source_bindings']:bind(b)
        r.update(complete=True,status='completed',complete19series_GPU_three_view_qualified=True,journal=entry(journal),resources_after=guard())
    except Exception as e:
        r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
        if journal.exists():r['partial_journal']=entry(journal)
    r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r[k] for k in ('complete','status','errors','GPU_optimizer_updates','CPU_reference_optimizer_updates','elapsed_seconds')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
