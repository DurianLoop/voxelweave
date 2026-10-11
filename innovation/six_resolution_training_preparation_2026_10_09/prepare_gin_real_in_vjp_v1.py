"""Create a separately frozen IN diagnostic from the completed local-convolution version."""
from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
p=HERE/'diagnose_gin_real_local_vjp_v1.py';src=p.read_text(encoding='utf-8')
def replace(old,new):
    global src
    assert src.count(old)==1,(old,src.count(old));src=src.replace(old,new)
replace('One real case: isolate captured input/cotangent/backend at the worst convolution.','One real case: isolate InstanceNorm input/upstream/backend after the worst convolution.')
replace('self.observe(self.view,incoming,tensor)','self.observe(self.view,"conv",incoming,tensor)')
replace('                tensor=F.leaky_relu(tensor,.01,inplace=False)','                if name==TARGET:self.observe(self.view,"norm",None,tensor)\n                tensor=F.leaky_relu(tensor,.01,inplace=False)')
replace("out=HERE/'gin_real_local_vjp_attempt01'","out=HERE/'gin_real_in_vjp_attempt01'")
replace('len(blob.encode())<150_000','len(blob.encode())<180_000')
replace("HERE/'GIN_REAL_LOCAL_VJP_PROTOCOL_V1.md'","HERE/'GIN_REAL_IN_VJP_PROTOCOL_V1.md',HERE/'prepare_gin_real_in_vjp_v1.py',HERE/'diagnose_gin_real_local_vjp_v1.py',HERE/'gin_real_local_vjp_attempt01/receipt.json'")
replace("            def observe(vi,incoming,output):\n                if vi in records:return\n                q=dict(x=incoming.detach().cpu().clone(),z=output.detach().cpu().clone());records[vi]=q\n                def cotangent(grad):\n                    assert 'dy' not in q;q['dy']=grad.detach().cpu().clone();return grad\n                output.register_hook(cotangent);guard(True)","""            def observe(vi,kind,incoming,output):
                q=records.setdefault(vi,{})
                if kind+'_observed' in q:return
                q[kind+'_observed']=True
                if kind=='conv':q.update(x=incoming.detach().cpu().clone(),z=output.detach().cpu().clone())
                else:q['norm_output_sha256']=array_sha(output.detach().cpu().numpy())
                field='dy' if kind=='conv' else 'dn'
                def cotangent(grad):
                    assert field not in q;q[field]=grad.detach().cpu().clone();return grad
                output.register_hook(cotangent);guard(True)""")
replace("handles.append(model.get_submodule(TARGET).register_forward_hook(lambda mod,args,result:observe(active[0],args[0],result)))","""handles.append(model.get_submodule(TARGET).register_forward_hook(lambda mod,args,result:observe(active[0],'conv',args[0],result)))
                handles.append(model.get_submodule('decoders.2.layers.4').register_forward_hook(lambda mod,args,result:observe(active[0],'norm',None,result)))""")
replace("all('dy' in v for v in records.values())","all('dy' in v and 'dn' in v for v in records.values())")
replace("cotangent_sha256=array_sha(rec['dy'].numpy())","cotangent_sha256=array_sha(rec['dy'].numpy()),IN_output_cotangent_sha256=array_sha(rec['dn'].numpy()),norm_output_sha256=rec['norm_output_sha256']")
start=src.index("        r['captured_CPU_GPU_differences']=")
end=src.index("        assert r['CPU_local_VJPs']==",start)
src=src[:start]+'''        r['captured_CPU_GPU_differences']=[dict(view=i,
            IN_input_max_error=float((captured['cpu'][i]['z']-captured['cuda:0'][i]['z']).abs().max()),
            IN_output_cotangent_max_error=float((captured['cpu'][i]['dn']-captured['cuda:0'][i]['dn']).abs().max()),
            IN_input_cotangent_max_error=float((captured['cpu'][i]['dy']-captured['cuda:0'][i]['dy']).abs().max())) for i in range(3)]
        weight=initial[TARGET+'.weight'];coordinate=list(np.unravel_index(INDEX,tuple(weight.shape)));r['coordinate']=list(map(int,coordinate))
        gamma=initial['decoders.2.layers.4.weight'];beta=initial['decoders.2.layers.4.bias']
        assert bool((gamma==1).all()) and bool((beta==0).all());r['initial_IN_gamma_one_beta_zero']=True
        r['same_input_upstream_backend_comparisons']=[];r['original_IN_dx_reconstruction']=[]
        for input_device in ('cpu','cuda:0'):
            for cotangent_device in ('cpu','cuda:0'):
                tick=time.perf_counter();backend_rows={d:dict(input_source=input_device,cotangent_source=cotangent_device,backend=d,per_view=[]) for d in ('cpu','cuda:0')}
                for vi in (2,1,0):
                    guard(True);q=captured[input_device][vi];z=q['z'];dn=captured[cotangent_device][vi]['dn']
                    a=z.numpy().astype(np.float64);b=dn.numpy().astype(np.float64);axes=(2,3,4)
                    centered=a-a.mean(axis=axes,keepdims=True);invstd=1/np.sqrt((centered*centered).mean(axis=axes,keepdims=True)+1e-5)
                    xhat=centered*invstd
                    dx64=gamma.numpy()[None,:,None,None,None]*invstd*(b-b.mean(axis=axes,keepdims=True)-xhat*(b*xhat).mean(axis=axes,keepdims=True))
                    independent_coordinate=coordinate_vjp64(q['x'],torch.from_numpy(dx64),coordinate)
                    del a,b,centered,invstd,xhat;local={}
                    for backend in ('cpu','cuda:0'):
                        zz=z.to(backend).detach().requires_grad_(True);dd=dn.to(backend)
                        yn=F.instance_norm(zz,None,None,gamma.to(backend),beta.to(backend),True,.1,1e-5)
                        dx,=torch.autograd.grad(yn,zz,dd);dx=dx.detach().cpu();local[backend]=dx
                        r['CPU_local_VJPs' if backend=='cpu' else 'GPU_local_VJPs']+=1
                        coordinate_value=coordinate_vjp64(q['x'],dx,coordinate)
                        backend_rows[backend]['per_view'].append(dict(view=vi,coordinate_gradient=coordinate_value,
                            independent_float64_coordinate=independent_coordinate,
                            dx_max_error_from_float64=float(np.max(np.abs(dx.numpy()-dx64)))))
                        if input_device==cotangent_device==backend:
                            difference=float((dx-captured[backend][vi]['dy']).abs().max());equal=torch.equal(dx,captured[backend][vi]['dy'])
                            r['original_IN_dx_reconstruction'].append(dict(device=backend,view=vi,max_error=difference,bitwise_equal=equal))
                            assert equal,('IN dx not reproduced',backend,vi,difference)
                        del zz,dd,yn;gc.collect();torch.cuda.empty_cache();guard(True)
                    r['same_input_upstream_backend_comparisons'].append(dict(input_source=input_device,cotangent_source=cotangent_device,view=vi,
                        dx_max_backend_error=float((local['cpu']-local['cuda:0']).abs().max()),
                        coordinate_gradient_backend_error=abs(backend_rows['cpu']['per_view'][-1]['coordinate_gradient']-backend_rows['cuda:0']['per_view'][-1]['coordinate_gradient'])))
                    del dx64,local,dx;gc.collect();guard(True)
                for backend,q in backend_rows.items():
                    q.update(coordinate_gradient_sum=sum(v['coordinate_gradient'] for v in q['per_view']),
                        independent_float64_coordinate_sum=sum(v['independent_float64_coordinate'] for v in q['per_view']),
                        elapsed_seconds=time.perf_counter()-tick,resources=guard(True))
                    r['local_matrix'].append(q);save();print(json.dumps({k:q[k] for k in ('input_source','cotangent_source','backend','coordinate_gradient_sum','independent_float64_coordinate_sum')}),flush=True)
''' + src[end:]
target=HERE/'diagnose_gin_real_in_vjp_v1.py';assert not target.exists();target.write_text(src,encoding='utf-8')
compile(src,str(target),'exec')
print({'complete':True,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'new_bytes':target.stat().st_size,'new_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
