"""Archive completed four-arm evidence and next-training preparation; never claim live completion."""
import ast, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/coverage_augmentation_stage_manifest_2026-10-03.json'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    sys.stdout.reconfigure(encoding='utf-8');files=set();errors=[]
    def check(value,message):
        if not value:errors.append(message)
    def include(path):
        path=Path(path);check(path.is_file(),'Missing '+str(path))
        if path.is_file():files.add(path)
    def bind(path,digest):
        include(path);check(Path(path).is_file() and sha(path)==digest,'SHA mismatch '+str(path))
    def complete(path):
        include(path);r=read(path);check(r['complete'] and not r['errors'],'Incomplete '+str(path));return r
    drawdir=ROOT/'experiments/mc_rc_coverage_augmentation_draw_cpu'
    d=complete(drawdir/'attempt_01.json');dv=complete(drawdir/'independent_all4000_geometry_and_inputs_attempt_01.json')
    bind(drawdir/'attempt_01.json',dv['result_sha256'])
    check(dv['all_arm_real_input_sha_checks']==dv['full_patch_geometry_checks']==16000,'All16000 original draw/reference checks')
    check(dv['legacy_original_sampler_matches']==4000 and dv['legacy_baseline_exact_reuse_verified'],'Authenticated legacy reuse')
    run=ROOT/'experiments/mc_rc_coverage_augmentation_factorial_cpu'
    r=complete(run/'attempt_01.json');q=complete(run/'independent_all_arms_metrics_draws_checkpoint_attempt_01.json')
    bind(run/'attempt_01.json',q['result_sha256'])
    check(r['new_training_updates_completed']==12000 and q['four_arm_training_draw_sha_checks']==16000 and q['checkpoint_replayed_planes']==12,'Actual12000 training/16000draw/12plane checks')
    check([a['name'] for a in r['arms']]==['legacy_aug','legacy_none','coverage_aug','coverage_none'],'All4 fixed arms')
    for record in (d,r):
        for b in record['source_bindings']:bind(ROOT/b['path'],b['sha256'])
        bind(ROOT/record['protocol_file'],record['protocol_sha256'])
    for b in r['code_bindings']+q['code_bindings']:bind(ROOT/b['path'],b['sha256'])
    for a in r['arms']:
        check(a['complete'] and a['updates_completed']==4000,'Completed '+a['name'])
        bind(ROOT/a['checkpoint_file'],a['checkpoint_sha256'])
        bind(ROOT/a['evaluation']['prediction_file'],a['evaluation']['prediction_file_sha256'])
    for record in (d,dv,r,q):
        check(not record['gpu_initialized'] and not record['native_hidden_MR_pixels_decoded'] and not record['confirmation_patients_opened'],'CPU/hidden/confirmation scope')
        check(not record['publication_claim_confirmed'] and record['scientific_confirmation_patients']==0,'No confirmed publication claim')
    analysis=read(run/'descriptive_factorial_analysis.json');include(run/'descriptive_factorial_analysis.json')
    for b in analysis['source_bindings']:bind(ROOT/b['path'],b['sha256'])
    la,ln,ca,cn=[a['evaluation']['metrics']['full']['dice'] for a in r['arms']]
    check(abs(analysis['contrasts']['full']['dice']['coverage_mean_difference']-((ca-la)+(cn-ln))/2)<1e-12,'Descriptive coverage difference')
    check(abs(analysis['contrasts']['full']['dice']['augmentation_mean_difference']-((la-ln)+(ca-cn))/2)<1e-12,'Descriptive augmentation difference')
    check(abs(analysis['contrasts']['full']['dice']['coverage_x_augmentation_difference_in_differences']-((ca-cn)-(la-ln)))<1e-12,'Descriptive difference in differences')
    pfdir=ROOT/'experiments/mc_rc_no_augmentation_development_cpu_preflight';pf=complete(pfdir/'attempt_01.json')
    check(len(pf['series'])==19 and pf['same_rng_final_state_matches']==pf['old_aug_input_sha_matches']==pf['new_none_reference_sha_matches']==608,'All19/608 sampler preflight')
    check(pf['full_patch_source_mapping_checks']==1216 and pf['network_forward_calls']==pf['training_updates']==0,'All1216 source mappings, no model calls')
    for b in pf['source_bindings']+pf['code_bindings']:bind(ROOT/b['path'],b['sha256'])
    bind(ROOT/pf['protocol_file'],pf['protocol_sha256'])
    textdir=ROOT/'literature/source_cache/coverage_augmentation_fulltexts_2026-10-03'
    reading=read(textdir/'reading_provenance.json');include(textdir/'reading_provenance.json')
    bind(textdir/'attempt_01.json',reading['acquisition_sha256']);bind(ROOT/reading['report'],reading['report_sha256'])
    bind(ROOT/'literature/register_coverage_augmentation_followup_reading_2026_10_03.py',reading['script_sha256'])
    check(reading['cumulative_new_primary_bodies_read']==2 and reading['cumulative_body_text_blocks']==205 and reading['remaining_body_text_blocks_completed_this_continuation']==102,'Cumulative205 versus continuation102 reading distinction')
    for paper in reading['papers']:
        for prefix in ('raw','block','text'):bind(textdir/paper[prefix+'_file'],paper[prefix+'_sha256'])
        blocks=read(textdir/paper['block_file'])
        check(paper['actual_read_blocks']==[dict(index=i,**b) for i,b in enumerate(blocks)],'Exact read block text '+paper['key'])
        check(paper['cumulative_actual_read_block_ids']==list(range(len(blocks))),'All cumulative blocks '+paper['key'])
        check(not paper['visual_figures_reviewed'] and not paper['author_experiments_independently_reproduced'],'Reading limitations explicit')
    figdir=ROOT/'figures/mc_rc_coverage_augmentation_factorial_cpu';fig=read(figdir/'provenance.json')
    for b in fig['source_bindings']+fig['outputs']:bind(ROOT/b['path'],b['sha256'])
    bind(ROOT/fig['report_file'],fig['report_sha256'])
    # These directories contain only completed immutable outputs; the new live
    # 20k training output is deliberately represented by a dated observation.
    for folder in (drawdir,run,pfdir,textdir,figdir,
                   *list((ROOT/'literature/source_cache').glob('*coverage_augmentation*'))):
        if folder.exists():
            for p in folder.rglob('*'):
                if p.is_file():include(p)
    for folder,pattern in ((ROOT,'*COVERAGE_AUGMENTATION*.md'),(ROOT,'*NO_AUGMENTATION*.md'),
                            (ROOT/'experiments','*coverage_augmentation*.py'),
                            (ROOT/'experiments','*no_augmentation*.py'),
                            (ROOT/'literature','*coverage_augmentation*.py'),
                            (ROOT/'literature','*coverage_augmentation*.md')):
        for p in folder.glob(pattern):include(p)
    for name in ('README.md','EXPERIMENT_QUEUE.md',
                 'experiments/no_augmentation_all_development_preparation_2026-10-03.json',
                 'literature/source_cache/no_augmentation_training_launch_observation_2026-10-03.json',
                 'literature/record_no_augmentation_training_observation_2026_10_03.py'):
        include(ROOT/name)
    for p in files:
        if p.suffix=='.py':
            try:ast.parse(p.read_text(encoding='utf-8'))
            except SyntaxError as error:errors.append('Syntax '+str(p)+': '+str(error))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),
        scope='Completed coverage/augmentation batch; next CPU training state is a dated observation, not final results.',
        files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)],
        completed_factorial_new_updates=12000,scientific_confirmation_patients=0,publication_claim_confirmed=False,
        next_training_complete_not_asserted=True,errors=errors)
    OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(files),errors=errors),ensure_ascii=False));return int(bool(errors))


if __name__=='__main__':
    raise SystemExit(main())
