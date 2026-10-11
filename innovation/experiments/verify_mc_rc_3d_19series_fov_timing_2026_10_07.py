"""Metadata-only independent tile/time aggregation; does not rerun neural inference."""
import hashlib,itertools,json,statistics,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');source=OUT/'attempt01.json';q=json.loads(source.read_text(encoding='utf-8'))
    assert q['complete'] and not q['errors'];path=OUT/'independent_metadata_and_time_aggregation_attempt01.json';assert not path.exists()
    qualifier=ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json'
    previous=json.loads(qualifier.read_text(encoding='utf-8'));assert previous['complete'] and not previous['errors']
    for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    verified=[]
    for a,old in zip(q['arms'],previous['arms']):
        assert a['kind']==old['kind'] and a['complete'] and len(a['series'])==19
        assert sha(ROOT/a['checkpoint_file'])==a['checkpoint_sha256']==old['initial_checkpoint_sha256']
        by={v['uid']:v for v in old['cache_records']};assert set(by)==set(v['uid'] for v in a['series'])
        count=0
        for s in a['series']:
            cache=by[s['uid']];assert s['patient']==cache['patient'] and s['physical_input_sha256']==cache['input_sha256']
            axes=[]
            for n,p in zip(cache['shape_zrc'],(64,128,128)):
                positions=list(range(0,n-p+1,p//2))
                if n-p not in positions:positions.append(n-p)
                positions.sort();assert positions[0]==0 and positions[-1]+p==n
                assert all(y-x<=p for x,y in zip(positions,positions[1:]));axes.append(positions)
            assert axes==s['inference']['axis_starts'];tiles=sum(1 for unused in itertools.product(*axes))
            assert tiles==s['inference']['total_tiles'] and s['inference']['coverage_min']>0
            assert len(s['probability_sha256'])==64 and s['complete_inference_seconds']>0 and s['load_and_input_hash_seconds']>0
            count+=tiles
        assert count==a['total_tiles']==q['planned_tiles_per_arm']==1139
        assert sum(s['complete_inference_seconds'] for s in a['series'])==a['all19_complete_inference_seconds']
        assert sum(s['load_and_input_hash_seconds'] for s in a['series'])==a['all19_load_and_input_hash_seconds']
        assert statistics.median(s['complete_inference_seconds'] for s in a['series'])==a['median_series_inference_seconds']
        verified.append(dict(kind=a['kind'],all19_metadata_verified=True,total_tiles_verified=count,
            timings_reaggregated=True,neural_probability_pixels_not_independently_replayed=True,
            complete_FOV_seconds=a['all19_complete_inference_seconds']))
    assert not q['predictions_saved'] and not q['task_effects_scored'] and q['GT_files_loaded']==0
    assert not list(OUT.glob('*.pt')) and not list(OUT.glob('*.npz'))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_file=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),arms=verified,
        GT_files_loaded=0,neural_forwards=0,actual_training_updates=0,actual_gpu_updates=0,publication_claim_confirmed=False)
    with path.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(r,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
