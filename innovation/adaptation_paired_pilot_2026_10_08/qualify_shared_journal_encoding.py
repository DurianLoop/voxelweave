"""Lossless grouping of redundant four-branch records; exact raw-byte replay using two gzip readers."""
import gzip,zlib,json,hashlib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    resource_guard();out=HERE/'shared_journal_attempt01';out.mkdir(exist_ok=False)
    fit=json.loads((HERE/'attempt01/receipt.json').read_text());assert fit['complete'] and len(fit['arms'])==4
    old={a['name']:(ROOT/a['history_path']).read_bytes() for a in fit['arms']}
    rows={n:[json.loads(x) for x in b.decode('utf-8').splitlines()] for n,b in old.items()}
    keys=list(rows['native_reference_basic'][0]);assert all(list(r)==keys for vv in rows.values() for r in vv)
    common=['step','patient','uid','label_sha256','geometry','strong_primitives','lr'];shared=[];branch={n:[] for n in rows}
    for i in range(99):
        first=rows['native_reference_basic'][i];entry={k:first[k] for k in common}
        assert all({k:vv[i][k] for k in common}==entry for vv in rows.values())
        entry['basic_inputs']={kind:rows[kind+'_basic'][i]['basic_input_sha256'] for kind in ['native_reference','raw_pchip']}
        shared.append(entry)
        for n,vv in rows.items():
            r=vv[i];kind=n.removesuffix('_basic').removesuffix('_strong')
            assert r['basic_input_sha256']==entry['basic_inputs'][kind]
            if n.endswith('_basic'):assert r['input_sha256']==r['basic_input_sha256']
            branch[n].append(dict(loss=r['loss'],total_step_seconds=r['total_step_seconds'],
                strong_input=r['input_sha256'] if n.endswith('_strong') else None))
    payload=dict(format_version=1,record_key_order=keys,shared=shared,branch=branch)
    encoded=json.dumps(payload,separators=(',',':')).encode();packed=gzip.compress(encoded,compresslevel=6,mtime=0)
    dest=out/'four_journals_shared.json.gz'
    with dest.open('xb') as f:f.write(packed)
    counts=[]
    for reader in [gzip.decompress,lambda b:zlib.decompress(b,wbits=31)]:
        p=json.loads(reader(dest.read_bytes()))
        for name,bb in p['branch'].items():
            kind=name.removesuffix('_basic').removesuffix('_strong');recovered=[]
            for s,b in zip(p['shared'],bb):
                fields={k:s[k] for k in common};basic=s['basic_inputs'][kind]
                fields.update(input_sha256=basic if name.endswith('_basic') else b['strong_input'],basic_input_sha256=basic,
                    loss=b['loss'],total_step_seconds=b['total_step_seconds'])
                recovered.append({k:fields[k] for k in p['record_key_order']})
            raw=(''.join(json.dumps(x,separators=(',',':'))+'\n' for x in recovered)).encode()
            assert raw==old[name];counts.append(dict(branch=name,rows=len(recovered),raw_SHA256=hashlib.sha256(raw).hexdigest()))
    weights=sum((ROOT/a['checkpoint_path']).stat().st_size for a in fit['arms'])
    forecast_logs=len(packed)*202;peak=int(forecast_logs*1.25)+weights+max((ROOT/a['checkpoint_path']).stat().st_size for a in fit['arms'])+2_000_000
    res=resource_guard();r=dict(complete=True,errors=[],actual_combined_raw_journal_bytes=sum(map(len,old.values())),actual_shared_gzip_bytes=len(packed),
        exact_raw_byte_replays=len(counts),history_rows_replayed=792,readers=['gzip','zlib gzip wrapper'],
        four_branch_full19998_journal_forecast_bytes=forecast_logs,weights_only_no_resume_forecast_peak_bytes=peak,
        forecast_fits_current_disk_margin=peak<=res['workspace_free_bytes']-8_000_000_000,
        forecast_is_not_full_budget_actual_measurement=True,formal_full_training_launched=False,full_training_budget_frozen=False,
        actual_medical_or_model_arrays_loaded=0,neural_forwards=0,publication_claim_confirmed=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),HERE/'attempt01/receipt.json',dest]],
        replay_records=counts,resources=res)
    with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ['source_bindings','replay_records','resources']}),flush=True)
if __name__=='__main__':main()
