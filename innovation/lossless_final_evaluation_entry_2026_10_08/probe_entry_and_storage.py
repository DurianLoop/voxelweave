"""Run the new CLI's actual metadata-only route and record current storage limits."""
import sys,json,subprocess,math,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'readiness_probe_v3'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard();OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    qualification=read(HERE/'compression_qualification_v3/receipt.json');assert qualification['complete'] and not qualification['errors']
    exe=HERE/'evaluate_final_lossless_v3.py'
    p=subprocess.run([sys.executable,'-X','utf8','-B',str(exe),'--readiness-only'],capture_output=True,text=True,encoding='utf-8',timeout=30)
    for name,text in [('stdout',p.stdout),('stderr',p.stderr)]:
        with (OUT/(name+'.txt')).open('x',encoding='utf-8') as f:f.write(text)
    status=json.loads(p.stdout);assert p.returncode in [0,3]
    assert status['MR_or_GT_arrays_loaded']==0 and not status['CUDA_initialized'] and not (HERE/'medical_attempt03').exists()
    assert status['ready']==(p.returncode==0)
    train=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
    snapshot=read(train/'invocation02.json')
    arms=[{k:a.get(k) for k in ['kind','updates_completed','complete']} for a in snapshot['arms']]
    files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size) for p in train.iterdir() if p.is_file() and p.name in
        ['raw_pchip_history.jsonl','native_reference_history.jsonl','raw_pchip_last19998.pt','native_reference_last19998.pt','raw_pchip_resume.pt','invocation02.json']]
    raw=next(a for a in arms if a['kind']=='raw_pchip');native=next(a for a in arms if a['kind']=='native_reference')
    rawbytes=next(b['bytes'] for b in files if b['path'].endswith('raw_pchip_history.jsonl'))
    perrow=rawbytes/raw['updates_completed'];remaining=max(0,19998-raw['updates_completed'])
    extras={r['uncompressed_NPZ_bytes']-r['raw_packed_bytes'] for r in qualification['records']};assert len(extras)==1
    overhead=extras.pop();uncompressed=115491840+56*overhead
    finalbytes=next(b['bytes'] for b in files if b['path'].endswith('native_reference_last19998.pt'))
    resume_bytes=next(b['bytes'] for b in files if b['path'].endswith('raw_pchip_resume.pt'))
    headroom=resources['workspace_free_bytes']-8_000_000_000
    planning=dict(disk_bytes_above_original_8GB_reserve=headroom,uncompressed56_NPZ_payload_and_container_bytes=uncompressed,
        old_writer_container_bytes_per_file=overhead,uncompressed_prediction_bytes_currently_fit_before_other_costs=headroom>=uncompressed,
        history_remaining_rows=remaining,history_bytes_per_row_estimate_from_running_nonatomic_metadata=perrow,
        estimated_remaining_history_growth_bytes=remaining*perrow,estimated_new_raw_final_checkpoint_bytes_from_native=finalbytes,
        possible_atomic_resume_transient_bytes_from_current_file=resume_bytes,
        estimated_headroom_after_history_and_new_final=headroom-remaining*perrow-finalbytes,
        estimated_old_prediction_deficit_after_history_and_new_final=max(0,uncompressed-(headroom-remaining*perrow-finalbytes)),
        estimates_are_not_future_resource_guarantees=True,rolling_files_snapshotted_as_metadata_only_not_frozen_or_hashed=True,
        actual_final_MRI_compression_bytes_unknown=True)
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        actual_subprocess_exit=p.returncode,actual_subprocess_status=status,medical_output_directory_created=False,
        original_training_result_metadata=dict(status=snapshot.get('status'),complete=snapshot.get('complete'),arms=arms),
        current_training_file_sizes=files,storage_planning=planning,resource_snapshot=client.resource_guard(),
        source_bindings=[client.base.entry(p) for p in [Path(__file__),exe,HERE/'final_eval_lossless_v3.py',HERE/'PROTOCOL.md',
            HERE/'REPAIR_V3.md',HERE/'compression_qualification_v3/receipt.json']],
        output_bindings=[client.base.entry(OUT/n) for n in ['stdout.txt','stderr.txt']],
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,GPU_forwards=0,
        original_training_modified=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,elapsed_seconds=time.perf_counter()-tick)
    client.base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=True,actual_subprocess_exit=p.returncode,status=status,storage_planning=planning,
        resource_snapshot=q['resource_snapshot']),ensure_ascii=False),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
