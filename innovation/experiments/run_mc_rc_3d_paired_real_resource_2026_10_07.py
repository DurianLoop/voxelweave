"""Real qualification entry: all prerequisite gates run before neural/MRI imports."""
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'MC_RC_3D_PAIRED_REAL_RESOURCE_ENTRY_PROTOCOL_2026-10-07.md'
CHECKER=ROOT/'experiments/check_mc_rc_3d_paired_resource_readiness_2026_10_07.py'
WORKER=ROOT/'experiments/mc_rc_3d_paired_resource_worker_2026_10_07.py'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def gpu_totals():
    q=subprocess.run(['nvidia-smi','--query-gpu=index,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=15)
    lines=q.stdout.strip().splitlines();assert len(lines)==1
    index,total,free,util=[int(x.strip()) for x in lines[0].split(',')];assert index==0
    return dict(observed_utc=datetime.now(timezone.utc).isoformat(),index=0,total_bytes=total*1048576,
        free_bytes=free*1048576,utilization_percent=util,PIDs_requested=False,PIDs_modified=False)
def own_rss():
    class M(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('pf',ctypes.c_ulong),('peak',ctypes.c_size_t),('current',ctypes.c_size_t)]+[(k,ctypes.c_size_t) for k in ('pqpu','qpu','pqnp','qnp','page','peakpage')]
    m=M();m.cb=ctypes.sizeof(m);k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p
    p=ctypes.windll.psapi;p.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    assert p.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(m),m.cb)
    return dict(own_peak_RSS_bytes=int(m.peak),own_current_RSS_bytes=int(m.current))
def main():
    sys.stdout.reconfigure(encoding='utf-8');ap=argparse.ArgumentParser();ap.add_argument('--device',choices=('cpu','gpu'),required=True);ap.add_argument('--attempt',required=True);args=ap.parse_args()
    assert len(args.attempt)==2 and args.attempt.isdigit()
    out=ROOT/('experiments/mc_rc_3d_paired_real_resource_2026_10_07_'+args.device+'_attempt'+args.attempt);out.mkdir(exist_ok=False)
    path=out/'attempt01.json';at=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,status='checking_prerequisites',errors=[],
        requested_device=args.device,script_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
        real_resource_qualification_completed=False,MRI_observed_packages_loaded=0,development_GT_loaded=0,
        native_MRI_pixels_loaded=0,validation_or_confirmation_pixels_loaded=0,actual_resource_updates=0,
        actual_formal_training_updates=0,updated_weights_saved=False,task_effects_scored=False,
        neural_modules_imported=False,CUDA_initialized=False,other_processes_modified=False,
        publication_claim_confirmed=False,goal_status='active')
    def save():
        path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<5_000_000
    save()
    try:
        readiness=out/'prerequisite_readiness.json'
        proc=subprocess.run([sys.executable,'-X','utf8','-B',str(CHECKER),'--output',readiness.relative_to(ROOT).as_posix()],capture_output=True,timeout=60)
        r['readiness_process_exit']=proc.returncode;r['readiness_stdout']=proc.stdout.decode('utf-8');r['readiness_stderr']=proc.stderr.decode('utf-8')
        q=read(readiness);r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (PROTOCOL,CHECKER,WORKER,Path(__file__),readiness)]
        r['missing_prerequisites']=q['missing_files'];r['failed_prerequisite_conditions']=q['failed_conditions']
        r['readiness_mutable_observations_not_frozen']=q.get('mutable_read_observations_not_frozen',[])
        if proc.returncode==3 and q['complete'] and not q['ready'] and not q['errors']:
            r.update(complete=True,status='prerequisite_deferred',reason='Original final training/evaluation/actual exits not qualified',
                torch_in_sys_modules='torch' in sys.modules,numpy_in_sys_modules='numpy' in sys.modules)
            assert not r['torch_in_sys_modules'] and not r['numpy_in_sys_modules'];save();return 3
        assert proc.returncode==0 and q['ready'] and q['complete'] and not q['errors']
        cert=ROOT/'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/attempt01.json'
        receipt=ROOT/'SESSION_OBSERVED_EXITS_PAIRED_RESOURCE_WORKFLOW_2026-10-07.json'
        if not cert.is_file() or not receipt.is_file():
            r.update(complete=True,status='synthetic_workflow_evidence_deferred');save();return 3
        c,e=read(cert),read(receipt)
        assert c['complete'] and not c['errors'] and all(c['gate'].values())
        assert e['synthetic_observed_tool_exit']==0 and e['synthetic_result_sha256']==sha(cert)
        assert e['verifier_observed_tool_exit']==0 and e['verifier_result_sha256']==sha(ROOT/e['verifier_result_file'])
        for b in c['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        r['source_bindings'].extend(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (cert,receipt))
        if args.device=='gpu':
            r['GPU_startup_totals']=gpu_totals()
            if r['GPU_startup_totals']['free_bytes']<8_000_000_000:
                r.update(complete=True,status='GPU_resource_deferred');save();return 3
        from mc_rc_reference_resources_2026_10_07 import resource_guard
        r['resources_before_neural_import']=resource_guard()
        import mc_rc_3d_paired_resource_worker_2026_10_07 as worker
        r['neural_modules_imported']=True;torch=worker.torch;torch.set_num_threads(4)
        assert torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        device='cpu'
        if args.device=='gpu':
            os.environ['CUDA_VISIBLE_DEVICES']='0';assert torch.cuda.is_available();device='cuda:0'
            torch.cuda.set_per_process_memory_fraction(.1,0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
            torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
        allowed_binary=set();seen_binary=[];denied=[]
        # Audit is limited to workspace data; only 19 certified observed/label paths may be read.
        prep=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json')
        obs=read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')
        assert len(prep['cases'])==len(obs['series'])==19
        allowed_binary.update((ROOT/c['label_file']).resolve() for c in prep['cases'])
        allowed_binary.update((ROOT/c['observed_package']).resolve() for c in obs['series'])
        def audit(event,arguments):
            if event!='open' or not arguments or not isinstance(arguments[0],(str,bytes)):return
            try:p=Path(arguments[0]).resolve()
            except (TypeError,ValueError,OSError):return
            mode=arguments[1] if len(arguments)>1 else None
            if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
            if p.is_relative_to(ROOT.parent) and p.name.endswith(('.zip','.nii','.nii.gz','.npy','.npz','.pt')):
                if p not in allowed_binary:denied.append(str(p));raise PermissionError('Uncertified MRI/weight read denied: '+str(p))
                seen_binary.append(p.relative_to(ROOT).as_posix())
        sys.addaudithook(audit)
        def guard():
            assert time.perf_counter()-at<=1200
            v=resource_guard();v.update(**own_rss(),cpu_threads=torch.get_num_threads());assert v['cpu_threads']==4
            if device!='cpu':
                free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0);totals=gpu_totals()
                v.update(GPU_free_bytes=free,GPU_total_bytes=total,GPU_peak_reserved_bytes=peak,GPU_totals=totals)
                assert free>=4_000_000_000 and totals['free_bytes']>=4_000_000_000 and peak<=2_500_000_000
            else:assert not torch.cuda.is_initialized()
            r['last_resource_observation']=v;return v
        r['status']='loading_development_cache';cache,stream,uid=worker.load_real_development(guard,save,r)
        r['status']='resource_workflow_running';worker.run_workflow(cache,stream,device,guard,save,r,uid)
        assert r['actual_resource_updates']==68 and not denied
        r.update(real_resource_qualification_completed=True,complete=True,status='completed',resources_after=guard(),
            certified_binary_reads=sorted(set(seen_binary)),denied_binary_reads=denied,CUDA_initialized=torch.cuda.is_initialized())
    except Exception as e:
        r.update(status='failed');r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    finally:
        r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-at;save()
        print(json.dumps({k:r.get(k) for k in ('complete','status','errors','real_resource_qualification_completed','MRI_observed_packages_loaded','development_GT_loaded','actual_resource_updates','neural_modules_imported','CUDA_initialized','elapsed_seconds')}),flush=True)
    return 0 if r['real_resource_qualification_completed'] else 1
if __name__=='__main__':raise SystemExit(main())

