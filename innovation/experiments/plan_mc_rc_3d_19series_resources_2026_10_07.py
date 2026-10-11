"""Metadata-only host cache/context planning; explicitly no GPU or efficacy projection."""
import hashlib,json,math,sys
from pathlib import Path
from datetime import datetime,timezone
from mc_rc_reference_resources_2026_10_07 import resource_guard
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json'
FIT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json'
OUT=ROOT/'experiments/mc_rc_3d_19series_resource_planning_2026_10_07'
PATCH=(64,128,128)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    resources=resource_guard();data=json.loads(SOURCE.read_text(encoding='utf-8'))
    assert data['complete'] and not data['errors'];rows=[];patients=set()
    for source in data['series']:
        if source['role']!='development':continue
        patients.add(source['patient']);grid=source['grid'];shape=source['inputs']['raw_pchip']['physical_image_shape_zrc']
        assert shape==source['inputs']['native_reference']['physical_image_shape_zrc']
        assert shape==[n+a+b for n,(a,b) in zip(grid['unpadded_shape_zrc'],grid['padding'])]
        voxels=math.prod(shape);real=math.prod(grid['unpadded_shape_zrc']);spacing=grid['realized_spacing_zrc_mm']
        assert voxels==source['all_label_grid_voxels_replayed']
        rows.append(dict(patient=source['patient'],uid=source['uid'],padded_shape_zrc=shape,
                         unpadded_shape_zrc=grid['unpadded_shape_zrc'],physical_voxels=voxels,
                         whole_grid_padding_fraction=1-real/voxels,realized_spacing_zrc_mm=spacing,
                         patch_span_zrc_mm=[n*s for n,s in zip(PATCH,spacing)],
                         real_series_span_zrc_mm=[n*s for n,s in zip(grid['unpadded_shape_zrc'],spacing)],
                         maximum_real_context_per_patch_zrc_mm=[min(n,p)*s for n,p,s in zip(grid['unpadded_shape_zrc'],PATCH,spacing)],
                         physical_foreground=source['physical_foreground']))
    assert len(rows)==19 and len(patients)==11
    voxels=sum(r['physical_voxels'] for r in rows)
    plans={name:dict(bytes=count,GiB=count/2**30,available_ram_after_cache_bytes=resources['available_ram_bytes']-count,
                     fits_host_reserve_at_observation=resources['available_ram_bytes']-count>=8_000_000_000)
           for name,count in [('one_input_and_float32_label',voxels*8),('two_inputs_shared_float32_label',voxels*12),
                             ('one_input_and_uint8_label',voxels*5),('two_inputs_shared_uint8_label',voxels*9)]}
    fit=json.loads(FIT.read_text(encoding='utf-8'));timing=[]
    for arm in fit['arms']:
        if arm.get('complete') and arm.get('updates_completed')==512:
            seconds=arm['training_elapsed_seconds']/512
            timing.append(dict(kind=arm['kind'],completed_fixed_example_updates=512,seconds_per_update=seconds,
                               ideal_update_only_hours={str(n):seconds*n/3600 for n in (20000,50000,250000)},
                               excludes_new_series_io_sampling_evaluation=True))
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],series=rows,
                source_sha256=sha(SOURCE),script_sha256=sha(Path(__file__)),
                protocol_sha256=sha(ROOT/'MC_RC_3D_19SERIES_RESOURCE_PLANNING_PROTOCOL_2026-10-07.md'),
                fit_observation=dict(status=fit['status'],complete=fit['complete'],updates=fit['total_updates_completed'],
                                     sha256=sha(FIT),dynamic_observation_not_final_certificate=not fit['complete']),
                development_patients=11,development_series=19,physical_cache_voxels=voxels,
                host_cache_plans=plans,completed_arm_cpu_timing_scenarios=timing,resources=resources,
                GPU_time_or_peak_measured=False,formal_19series_training_recipe_frozen=False,
                actual_training_updates=0,actual_gpu_updates=0,neural_forwards=0,MR_or_label_values_newly_loaded=0,
                validation_effects_opened=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,
                publication_claim_confirmed=False)
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ('complete','physical_cache_voxels','host_cache_plans','completed_arm_cpu_timing_scenarios')}))
if __name__=='__main__':main()
