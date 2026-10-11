"""Complete 5984 geometries x two inputs x three controls; independent full MRI/intensity chain."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import sys,time,json,gzip,zlib,gc,collections,itertools,traceback
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
OLD=ROOT/'resolution_degradation_controls_2026_10_08'
REPAIR=ROOT/'intensity_precision_failure_diagnosis_2026_10_09'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import (
    development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,
    sample_batch,batch_rng,array_sha,QPATH)
sys.path.insert(0,str(OLD))
sys.path.insert(0,str(REPAIR))
sys.path.insert(0,str(ROOT/'certified_resolution_rounding_2026_10_09'))
import intensity_float64_stats as intensity
from resolution_control import baseline_patch
from certified_resolution import apply
from direct_numeric_adapter import independent_apply
from independent_intensity import apply_reference
from qualify_synthetic_and_schedule_v2 import independent_domain
MODES=['throughplane','inplane','allaxes'];KINDS=['native_reference','raw_pchip']
PATCH=(64,128,128);WALL=64800;JOURNAL_LIMIT=1_500_000
COLUMNS=['step','patch','case','kind','mode','enabled','pre_intensity_error',
         'shared_post_intensity_error','isolated_intensity_error','full_chain_error',
         'support_error','coordinate_error','binary_disagreements',
         'valid_voxels','changed_voxels','pre_intensity_padding_disagreements',
         'image_bitwise_disagreements','candidate_exact_fallback_voxels','reference_exact_fallback_voxels']


def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1)
    assert torch.get_num_interop_threads()==1
    started=time.perf_counter();res=resource_guard()
    assert res['workspace_free_bytes']-8_000_000_000>=15_800_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+1_800_000<2_000_000
    for name,session in [('ACTUAL_REAL_STRESS_TERMINAL_TOOL.json',5725),
                         ('ACTUAL_INTENSITY_COMPOSITION_TERMINAL_TOOL.json',31866),
                         ('ACTUAL_INDEPENDENT_INTENSITY_TERMINAL_TOOL.json',None)]:
        terminal=read(OLD/name)
        assert terminal['exit_code']==0 and 'session_id' not in terminal
        assert terminal['observed_unified_exec_session']==session
    prerequisites=['geometry_and_synthetic_attempt01/receipt.json','real_stress_attempt01/receipt.json',
                   'intensity_composition_attempt01/receipt.json','independent_intensity_attempt01/receipt.json']
    sources={Path(__file__),HERE/'FULL_REAL_PIPELINE_PROTOCOL.md',OLD/'resolution_control.py',
             OLD/'independent_resolution.py',OLD/'independent_intensity.py',
             OLD/'qualify_synthetic_and_schedule_v2.py',Path(intensity.__file__),QPATH,
             ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',
             ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
             ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py'}
    sources.update(OLD/name for name in ['ACTUAL_REAL_STRESS_TERMINAL_TOOL.json',
        'ACTUAL_INTENSITY_COMPOSITION_TERMINAL_TOOL.json','ACTUAL_INDEPENDENT_INTENSITY_TERMINAL_TOOL.json'])
    for name in prerequisites:
        p=OLD/name;q=read(p);assert q['complete'] and not q['errors'];sources.add(p)
        for b in q['source_bindings']:bind(b)
    assert read(OLD/prerequisites[-1])['all40_full_synthetic_fields_verified']
    repaired_terminal=REPAIR/'ACTUAL_REPAIRED_STRESS_TERMINAL_TOOL.json'
    repaired_observation=read(repaired_terminal)
    assert repaired_observation['exit_code']==0 and 'session_id' not in repaired_observation
    assert repaired_observation['observed_unified_exec_session']==47298
    repaired_path=REPAIR/'repaired_stress_attempt01/receipt.json';repaired=read(repaired_path)
    assert repaired['complete'] and repaired['status']=='completed' and not repaired['errors']
    assert repaired['all40_synthetic228_real3_failed_regressions_verified']
    assert repaired['all11_patients19_series_two_inputs_three_modes_verified']
    assert len(repaired['fields'])==271 and repaired['MRI_input_arrays_loaded']==38
    for b in repaired['source_bindings']:bind(b)
    assert sha(OLD/'independent_intensity.py')=='11f3946b80d7c687acb03fedc607881b6813a2982290e9588431ad96cc63c81e'
    assert sha(OLD/'qualify_full_real_pipeline.py')=='b27c5ed516fca0a4cb9e5cc194b7987cc1ffc51689e518d63780203d3671e403'
    failed_terminal=OLD/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json';failed=read(failed_terminal)
    assert failed['exit_code']==1 and 'session_id' not in failed and failed['observed_unified_exec_session']==74234
    sources.update([repaired_terminal,repaired_path,REPAIR/'repaired_stress_attempt01/frozen_config.json',
        Path(intensity.legacy.__file__),Path(__file__).parent/'build_full_harness.py',
        failed_terminal,OLD/'full_real_pipeline_attempt01/receipt.json',OLD/'full_real_pipeline_attempt01/frozen_config.json',
        OLD/'qualify_full_real_pipeline.py'])
    certified=ROOT/'certified_resolution_rounding_2026_10_09';fast=ROOT/'direct_oracle_efficiency_2026_10_09'
    for stage in [certified,fast]:
        terminal=read(stage/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json');assert terminal['exit_code']==0 and 'session_id' not in terminal
        audit=read(stage/'all_patient_terminal_audit_attempt01/receipt.json');assert audit['complete'] and audit['all542_unique_field_identities_verified']
        receipt=read(stage/'all_patient_stress_attempt01/receipt.json');assert receipt['complete'] and receipt['all542_full_fields_verified']
        for b in receipt['source_bindings']:bind(b)
        sources.update([stage/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json',stage/'all_patient_terminal_audit_attempt01/receipt.json',stage/'all_patient_stress_attempt01/receipt.json'])
    admission=read(HERE/'compute_admission_attempt01/receipt.json');assert admission['complete'] and admission['admitted']
    for b in admission['source_bindings']:bind(b)
    sources.update([HERE/'compute_admission_attempt01/receipt.json',HERE/'direct_numeric_adapter.py',HERE/'build_full_harness.py',certified/'certified_resolution.py',certified/'direct_interval_reference.py',certified/'exact_tensor_reference.py',fast/'direct_separable_reference.py'])
    previous=ROOT/'real_context_and_author_code_followup_2026_10_08'
    auditpath=previous/'full_schedule_audit_attempt01/receipt.json';audit=read(auditpath)
    assert audit['complete'] and not audit['errors'] and audit['all2992_original_sample_batch_geometry_and_mother_labels_matched']
    for b in audit['source_bindings']:bind(b)
    fullpath=previous/'full_schedule_attempt01/receipt.json';full=read(fullpath)
    journalpath=ROOT/full['journal_path'];assert sha(journalpath)==full['journal_sha256']
    with gzip.open(journalpath,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
    indexed={(x['step'],x['patch']):x for x in rows}
    assert len(indexed)==len(rows)==5984
    assert set(indexed)==set(itertools.product(range(1,2993),range(2)))
    sources.update([auditpath,fullpath,journalpath])
    train=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
    configpath=train/'frozen_config.json';config=read(configpath)
    schedulepath=train/config['schedule_file'];assert sha(schedulepath)==config['schedule_file_sha256']
    schedule=np.load(schedulepath,allow_pickle=False)[:2992]
    sources.update([configpath,schedulepath])
    oldpath=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    old=read(oldpath);assert old['complete'] and not old['errors'];sources.add(oldpath)
    oldseries={s['uid']:s for s in old['series']}
    q=read(QPATH);assert q['complete'] and not q['errors']
    refs={a['kind']:{s['uid']:s for s in a['cache_records']} for a in q['arms']}
    cases=development_cases();assert len(cases)==19
    assert config['series']==[dict(patient=c['patient'],uid=c['uid']) for c,row in cases]
    for c,row in cases:
        for rel in [c['label_file'],c['header_file'],c['mr_zip_file'],row['observed_package']]:
            bind(next(b for b in old['source_bindings'] if b['path']==rel));sources.add(ROOT/rel)
    out=HERE/'full_real_pipeline_attempt01';out.mkdir(exist_ok=False)
    journal=out/'fields.jsonl.gz'
    dump(out/'frozen_config.json',dict(expected_fields=35904,geometries=5984,kinds=KINDS,modes=MODES,
         image_gate=3e-6,support_gate=3e-6,coordinate_gate=3e-12,binary_gate=0,
         wall_seconds=WALL,journal_limit_bytes=JOURNAL_LIMIT,stage_limit_bytes=2_000_000,
         schedule_prefix_sha256=array_sha(schedule),journal_columns=COLUMNS,
         source_bindings=[entry(p) for p in sorted(sources)]))
    r=dict(complete=False,status='running',errors=[],fields_completed=0,case_kind_steps_completed=0,
           MRI_input_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,patient_neural_forwards=0,
           training_updates=0,validation_pixels_loaded=False,confirmation_patients_opened=False,
           lockedIXI_opened=False,training_ready=False,publication_claim_confirmed=False,goal_status='active',
           new_distinct_primary_maintexts_completed=0,new_patient_medical_effects=0,
           resolution_padding_identity_only_before_intensity=True,
           post_intensity_padding_identity_not_claimed=True,
           shared_numpy_seeded_normal_convention=True,
           production_gamma_statistics_float64=True,exactly_rounded_resolution_candidate=True,independent_collapsed_reference=True,
           previous_failed_session=90446,original_failed_fields_completed=14673,failed_prefix_inherited=False,
           independently_reimplemented_sampler_not_claimed=True,
           journal_path=journal.relative_to(ROOT).as_posix(),journal_columns=COLUMNS,
           case_index=[dict(patient=c['patient'],uid=c['uid']) for c,row in cases],
           cache_records=[],series_modes={},patient_modes={},cost_seconds={},max_errors={})
    counters=collections.defaultdict(collections.Counter)
    patient_counters=collections.defaultdict(collections.Counter)
    costs=collections.Counter();maxima=collections.Counter();current=None
    def guard():
        resource_guard()
        assert time.perf_counter()-started<WALL and torch.get_num_threads()==1
        assert not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
        if journal.exists():assert journal.stat().st_size<JOURNAL_LIMIT
    def save():
        r.update(elapsed_seconds=time.perf_counter()-started,cost_seconds=dict(costs),max_errors=dict(maxima),
                 series_modes={k:dict(v) for k,v in counters.items()},
                 patient_modes={k:dict(v) for k,v in patient_counters.items()})
        p=out/'receipt.json.tmp';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        p.replace(out/'receipt.json')
    save()
    try:
        with journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=6,mtime=0) as stream:
            for ci,(c,row) in enumerate(cases):
                guard();g=lattice(c);at=time.perf_counter()
                target=physical_label(read_reference_label(c),g);r['GT_arrays_loaded']+=1
                costs['GT_load_and_resample']+=time.perf_counter()-at
                target_sha=array_sha(target);assert target_sha==oldseries[c['uid']]['physical_label_sha256']
                indices=np.flatnonzero(schedule[:,1]==ci)
                for ki,kind in enumerate(KINDS):
                    guard();at=time.perf_counter();normalized,stats=source_image(c,row,kind)
                    cache=physical_mr(normalized,g);del normalized
                    load_seconds=time.perf_counter()-at;costs['MRI_load_and_resample']+=load_seconds
                    r['MRI_input_arrays_loaded']+=1
                    cache_sha=array_sha(cache)
                    assert cache_sha==refs[kind][c['uid']]['input_sha256']
                    assert target_sha==refs[kind][c['uid']]['label_sha256']
                    r['cache_records'].append(dict(patient=c['patient'],uid=c['uid'],kind=kind,
                         input_sha256=cache_sha,label_sha256=target_sha,cache_bytes=int(cache.nbytes),
                         cache_load_seconds=load_seconds))
                    for ix in indices:
                        guard();step=int(ix)+1;at=time.perf_counter()
                        x,y,geometry=sample_batch(cache,target,batch_rng(19998+step))
                        costs['sample_batch']+=time.perf_counter()-at
                        base=x.numpy();labels=y.numpy();mother_sha=array_sha(labels)
                        ip=intensity.primitives(step)
                        assert c['patient']==config['patient_ids'][int(schedule[ix,0])]
                        for pi in range(2):
                            source=indexed[(step,pi)];primitive=source['primitive'];geom=geometry[pi]
                            assert source['patient']==c['patient'] and source['uid']==c['uid']
                            assert source['geometry']==geom and source['mother_label_sha256']==mother_sha
                            assert source['target_label_sha256']==array_sha(labels[pi,0])
                            assert np.array_equal(base[pi,0],baseline_patch(cache,geom,PATCH))
                            domain=independent_domain(g,geom,PATCH);valid=int(domain.sum())
                            for mi,mode in enumerate(MODES):
                                guard();current=dict(step=step,patch=pi,case=ci,kind=kind,mode=mode)
                                at=time.perf_counter();image,support,meta=apply(cache,g,geom,primitive,mode,PATCH)
                                costs['resolution_production']+=time.perf_counter()-at
                                at=time.perf_counter();other,other_support,imeta=independent_apply(cache,g,geom,primitive,mode,PATCH)
                                costs['resolution_independent']+=time.perf_counter()-at
                                at=time.perf_counter()
                                actual=intensity.apply(image[None,None],[ip[pi]])[0,0]
                                shared=intensity.apply(other[None,None],[ip[pi]])[0,0]
                                costs['intensity_production_two_calls']+=time.perf_counter()-at
                                at=time.perf_counter()
                                isolated=apply_reference(image,ip[pi]);reference=apply_reference(other,ip[pi])
                                costs['intensity_independent_two_calls']+=time.perf_counter()-at
                                at=time.perf_counter()
                                errors=dict(pre_intensity_error=float(np.max(np.abs(image-other))),
                                    shared_post_intensity_error=float(np.max(np.abs(actual-shared))),
                                    isolated_intensity_error=float(np.max(np.abs(actual-isolated))),
                                    full_chain_error=float(np.max(np.abs(actual-reference))),
                                    support_error=float(np.max(np.abs(support-other_support))),
                                    coordinate_error=float(imeta['coordinate_max_error']))
                                binary=int(np.count_nonzero((support>=1-1e-9)!=(other_support>=1-1e-9)))
                                padding=int(np.count_nonzero(image[~domain].view(np.uint32)!=base[pi,0][~domain].view(np.uint32)))
                                padding+=int(np.count_nonzero(other[~domain].view(np.uint32)!=base[pi,0][~domain].view(np.uint32)))
                                changed=int(np.count_nonzero(image!=base[pi,0]))
                                current.update(errors,binary_disagreements=binary,
                                     pre_intensity_padding_disagreements=padding,
                                     intensity_primitives=ip[pi],geometry=geom,primitive=primitive)
                                for name,value in errors.items():
                                    assert value<=(3e-12 if name=='coordinate_error' else 3e-6),f'{name}={value} exceeds unchanged gate'
                                bits=int(np.count_nonzero(image.view(np.uint32)!=other.view(np.uint32)))
                                assert bits==0 and binary==0 and padding==0
                                assert np.array_equal(support>=1-1e-9,domain)
                                assert np.array_equal(other_support>=1-1e-9,domain)
                                assert array_sha(labels)==mother_sha
                                if not primitive['enabled']:assert np.array_equal(image,base[pi,0])
                                costs['comparisons_and_hashing']+=time.perf_counter()-at
                                record=[step,pi,ci,ki,mi,int(primitive['enabled'])]
                                record.extend(errors[k] for k in COLUMNS[6:12])
                                record.extend([binary,valid,changed,padding,bits,meta['exact_fallback_voxels'],imeta['direct_exact_fallback_voxels']])
                                at=time.perf_counter();stream.write((json.dumps(record,separators=(',',':'))+'\n').encode('utf-8'))
                                stream.flush(zlib.Z_SYNC_FLUSH);costs['journal_write_and_flush']+=time.perf_counter()-at
                                for key in [f'{ci}/{ki}/{mi}']:
                                    v=counters[key];v['fields']+=1;v['enabled']+=int(primitive['enabled'])
                                    v['effective_change']+=int(primitive['enabled'] and changed>0)
                                    v['valid_voxels']+=valid;v['target_voxels']+=1048576
                                pc=patient_counters[f'{c["patient"]}/{ki}/{mi}']
                                pc['fields']+=1;pc['enabled']+=int(primitive['enabled']);pc['effective_change']+=int(primitive['enabled'] and changed>0)
                                for name,value in errors.items():maxima[name]=max(maxima[name],value)
                                r['fields_completed']+=1
                                del image,support,other,other_support,actual,shared,isolated,reference
                                if r['fields_completed']%120==0:
                                    raw.flush();save();print(json.dumps(dict(fields_completed=r['fields_completed'],
                                        expected_fields=35904,max_errors=dict(maxima),elapsed_seconds=time.perf_counter()-started)),flush=True)
                        r['case_kind_steps_completed']+=1
                        del x,y,base,labels;gc.collect()
                    assert array_sha(cache)==cache_sha;del cache;gc.collect();save()
                assert array_sha(target)==target_sha;del target;gc.collect();save()
        assert r['fields_completed']==35904 and r['case_kind_steps_completed']==5984
        assert r['MRI_input_arrays_loaded']==38 and r['GT_arrays_loaded']==19
        assert len(patient_counters)==66 and all(v['fields']==544 and v['effective_change']>0 for v in patient_counters.values())
        assert len(counters)==114 and all(v['effective_change']>0 for v in counters.values())
        for ki in range(2):
            for mi in range(3):
                group=[v for k,v in counters.items() if k.endswith(f'/{ki}/{mi}')]
                assert sum(v['fields'] for v in group)==5984 and sum(v['enabled'] for v in group)==1785
                assert sum(v['valid_voxels'] for v in group)==6041370624
        for p in sources:assert sha(p)==next(b['sha256'] for b in read(out/'frozen_config.json')['source_bindings'] if b['path']==p.relative_to(ROOT).as_posix())
        r.update(complete=True,status='completed',all35904_full_target_MRI_and_intensity_fields_verified=True,
                 all5984_geometries_both_inputs_three_modes_replayed=True,all_mother_labels_preserved=True,
                 journal_sha256=sha(journal),journal_bytes=journal.stat().st_size,
                 frozen_config_sha256=sha(out/'frozen_config.json'),
                 source_bindings=[entry(p) for p in sorted(sources)])
    except Exception as exc:
        r['status']='failed';r['errors'].append(type(exc).__name__+': '+str(exc))
        r['traceback']=traceback.format_exc();r['failed_field']=current;traceback.print_exc()
    r['CUDA_initialized']=torch.cuda.is_initialized();save()
    print(json.dumps({k:r.get(k) for k in ['complete','status','errors','fields_completed',
        'case_kind_steps_completed','MRI_input_arrays_loaded','GT_arrays_loaded','max_errors','elapsed_seconds']}),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
