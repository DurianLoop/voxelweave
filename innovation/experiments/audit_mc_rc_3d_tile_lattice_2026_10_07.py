"""Metadata-only source of potential tile phase shifts, not a performance assertion."""
import hashlib,itertools,json,math,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_3d_tile_lattice_audit_2026_10_07'
SOURCE=ROOT/'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json'
PATCH=(64,128,128);FACTOR=8
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    data=json.loads(SOURCE.read_text(encoding='utf-8'));assert data['complete'] and not data['errors']
    rows=[]
    for series in data['series']:
        if series['role']!='development':continue
        shape=series['inputs']['raw_pchip']['physical_image_shape_zrc'];axes=[]
        for n,p in zip(shape,PATCH):
            starts=[];s=0
            while s+p<=n:starts.append(s);s+=p//2
            if starts[-1]!=n-p:starts.append(n-p)
            axes.append(starts)
        tiles=list(itertools.product(*axes));shifted=[list(s) for s in tiles if any(v%FACTOR for v in s)]
        # Aligned geometry candidate is preparation only, not an executed/selected method.
        extra=[(-n)%FACTOR for n in shape]
        aligned_shape=[n+e for n,e in zip(shape,extra)]
        rows.append(dict(patient=series['patient'],uid=series['uid'],padded_shape_zrc=shape,
            axis_starts=axes,axis_start_phases_mod8=[[v%FACTOR for v in a] for a in axes],
            all_tiles=len(tiles),tiles_not_on_origin_pooling_lattice=len(shifted),nonaligned_tile_locations=shifted,
            right_high_padding_to_multiple8=extra,aligned_candidate_shape_zrc=aligned_shape,
            aligned_candidate_extra_voxels=math.prod(aligned_shape)-math.prod(shape)))
    assert len(rows)==19 and len({r['patient'] for r in rows})==11
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_file=SOURCE.relative_to(ROOT).as_posix(),source_sha256=sha(SOURCE),series=rows,
        downsampling_factor=FACTOR,series_count=19,patient_count=11,
        series_with_nonaligned_tile_starts=sum(r['tiles_not_on_origin_pooling_lattice']>0 for r in rows),
        total_tiles=sum(r['all_tiles'] for r in rows),total_nonaligned_tiles=sum(r['tiles_not_on_origin_pooling_lattice'] for r in rows),
        neural_forwards=0,actual_gpu_updates=0,mr_and_label_values_loaded=0,
        validation_effects_opened=False,confirmation_patients_opened=False,publication_claim_confirmed=False,
        interpretation='Potential pooling lattice inconsistency only. InstanceNorm input spatial statistics already violate finite-local-RF assumptions; aligned starts alone cannot guarantee exact full-volume inference.',
        candidate_execution_performed=False)
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:result[k] for k in ('complete','series_with_nonaligned_tile_starts','total_tiles','total_nonaligned_tiles','neural_forwards')}))
if __name__=='__main__':main()
