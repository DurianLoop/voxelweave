"""Verify this batch's completed experiments, primary-reading anchors and artifacts."""
import ast,json,hashlib,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/development_loss_stage_manifest_2026-10-03.json'
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[];files=set()
    def check(value,message):
        if not value:errors.append(message)
    def include(path):
        path=Path(path);check(path.is_file(),'Missing '+str(path))
        if path.is_file():files.add(path)
    def bind(path,digest):
        include(path);check(Path(path).is_file() and sha(path)==digest,'SHA mismatch '+str(path))
    def complete(path):
        include(path);r=read(path);check(r['complete'] and not r['errors'],'Not complete '+str(path));return r
    diagnosis=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02'
    dp=diagnosis/'attempt_01.json';d=complete(dp);dq=complete(diagnosis/'independent_metrics_and_checkpoint_attempt_01.json')
    bind(dp,dq['result_sha256'])
    check(len(d['evaluations'])==len(dq['evaluations'])==19 and dq['checkpoint_replayed_planes']==57,'All19 metrics and57 planes')
    check(d['reused_complete_predictions']==3 and d['training_updates']==0,'Only3 complete predictions reused, no training')
    check(dq['same_architecture_replay'] and not dq['second_independently_trained_model'],'Replay is not independent trained task model')
    failed=read(ROOT/d['retained_failed_attempt']);include(ROOT/d['retained_failed_attempt'])
    check(not failed['complete'] and len(failed['evaluations'])==3 and failed['errors']==['AssertionError: '],'Original affine scoring failure retained')
    check('surface_metrics' in failed['traceback'],'Original failure cause retained')
    check(len(d['aggregate']['complete_miss_series'])==8 and sum(e['metrics']['full']['empty_prediction'] for e in d['evaluations'])==2,'TP0 versus empty counts')
    check(abs(d['aggregate']['patient_first_means']['full']['dice']-.12794708153623302)<1e-12,'Full11 developer aggregation')
    for item in d['source_bindings']+d['code_bindings']+dq['reused_algorithm_sources']:bind(ROOT/item['path'],item['sha256'])
    bind(ROOT/d['protocol_file'],d['protocol_sha256']);bind(ROOT/d['checkpoint_file'],d['checkpoint_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_frozen_global_local_development_cpu.py',dq['script_sha256'])
    bind(ROOT/'MC_RC_FROZEN_DEVELOPMENT_AFFINE_RESUME_PROTOCOL_2026-10-03.md',d['affine_metrics_resume_protocol_sha256'])
    for row in d['evaluations']:bind(ROOT/row['prediction_file'],row['prediction_file_sha256'])
    single=ROOT/'experiments/mc_rc_global_local_single_case_loss_cpu';sp=single/'attempt_01.json'
    s=complete(sp);sq=complete(single/'independent_metrics_draws_and_checkpoint_attempt_01.json');bind(sp,sq['result_sha256'])
    check(s['training_patient_ids']==['VS-MC-RC-012'] and s['training_series_uids']==[s['uid']],'Single known developer identity')
    check(len(s['arms'])==2 and all(a['updates_completed']==4000 and a['complete'] and a['model_parameters']==981602 for a in s['arms']),'Two fixed4000 budgets')
    check(s['matched_initialization_verified'] and s['all_4000_training_draws_matched'],'Initialization and draws')
    check(sq['training_draws_replayed']==4000 and sq['checkpoint_replayed_planes']==6,'All4000 draws and6 complete planes independently checked')
    check(sq['sampler_replay_shares_production_sampler'] and sq['same_architecture_replay'],'Sampler/architecture sharing disclosed')
    bind(ROOT/'experiments/run_mc_rc_global_local_single_case_loss_cpu.py',s['script_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_global_local_single_case_loss_cpu.py',sq['script_sha256'])
    bind(ROOT/s['protocol_file'],s['protocol_sha256'])
    for row in s['source_bindings']+s['code_bindings']+sq['code_bindings']:bind(ROOT/row['path'],row['sha256'])
    check(s['arms'][0]['draw_sha256']==s['arms'][1]['draw_sha256'] and len(s['arms'][0]['draw_sha256'])==4000,'Actual matched4000 list')
    for arm in s['arms']:
        bind(ROOT/arm['checkpoint_file'],arm['checkpoint_sha256']);e=arm['evaluation'];bind(ROOT/e['prediction_file'],e['prediction_file_sha256'])
        check(e['fit_gate_passed']==all(e['fit_gate_checks'].values()),'Fit gate '+arm['name'])
    for r in (d,dq,s,sq):
        check(not r['gpu_initialized'] and not r['confirmation_patients_opened'] and not r['native_hidden_MR_pixels_decoded'],'CPU/confirmation/hidden-MR guard')
        check(r['scientific_confirmation_patients']==0 and not r['publication_claim_confirmed'],'No publication confirmation')
    for folder,script in ((diagnosis,'report_mc_rc_frozen_development_diagnosis_cpu.py'),(single,'report_mc_rc_global_local_single_case_loss_cpu.py')):
        p=folder/'report_provenance.json';include(p);r=read(p);bind(ROOT/r['report'],r['report_sha256']);bind(ROOT/'experiments'/script,r['script_sha256'])
        for item in r['source_bindings']:bind(ROOT/item['path'],item['sha256'])
    supplement=single/'additional_author_provenance_bindings_before_completion.json';include(supplement)
    for row in read(supplement)['bindings']:bind(ROOT/row['path'],row['sha256'])
    minimal=ROOT/'experiments/mc_rc_global_local_fixed_plane_fit_cpu';mp=minimal/'attempt_01.json'
    m=complete(mp);mq=complete(minimal/'independent_metrics_and_plane_attempt_01.json');bind(mp,mq['result_sha256'])
    check(m['updates_completed']==1000 and m['training_patient_ids']==['VS-MC-RC-012'] and m['z']==38,'Fixed012 median plane/1000 budget')
    check(len(m['locations'])==16 and len(m['tile_exposure'])==16 and set(m['tile_exposure'].values())=={125},'All16 tiles exactly125 exposures')
    check(mq['checkpoint_replayed_planes']==1 and not mq['full_patient_evaluated'],'Minimal plane is not full patient')
    check(m['evaluation']['fit_gate_passed']==mq['fit_gate_passed_verified']==all(m['evaluation']['fit_gate_checks'].values()),'Minimal fit gate verified')
    for row in m['source_bindings']:bind(ROOT/row['path'],row['sha256'])
    bind(ROOT/'experiments/run_mc_rc_global_local_fixed_plane_fit_cpu.py',m['script_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_global_local_fixed_plane_fit_cpu.py',mq['script_sha256'])
    bind(ROOT/m['protocol_file'],m['protocol_sha256']);bind(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py',m['support_sha256'])
    bind(ROOT/m['checkpoint_file'],m['checkpoint_sha256']);bind(ROOT/m['evaluation']['prediction_file'],m['evaluation']['prediction_file_sha256'])
    mr=minimal/'report_provenance.json';include(mr);mr=read(mr)
    bind(ROOT/mr['report'],mr['report_sha256']);bind(ROOT/'experiments/report_mc_rc_global_local_fixed_plane_fit_cpu.py',mr['script_sha256'])
    for row in mr['source_bindings']:bind(ROOT/row['path'],row['sha256'])
    for r in (m,mq):check(not r['gpu_initialized'] and not r['native_hidden_MR_pixels_decoded'] and not r['confirmation_patients_opened'] and not r['publication_claim_confirmed'],'Minimal CPU/identity scope')
    texts=ROOT/'literature/source_cache/loss_sampling_bias_fulltexts_2026-10-03';reading=read(texts/'reading_provenance.json')
    check(reading['new_primary_bodies_read']==2 and reading['actual_new_body_text_blocks']==157,'Two new primary bodies157')
    bind(texts/'attempt_01.json',reading['acquisition_sha256']);bind(ROOT/reading['report'],reading['report_sha256'])
    bind(ROOT/'literature/register_loss_sampling_bias_and_author_reading_2026_10_03.py',reading['script_sha256'])
    for paper in reading['papers']:
        for prefix in ('raw','block','text'):bind(texts/paper[prefix+'_file'],paper[prefix+'_sha256'])
        blocks=read(texts/paper['block_file']);check(paper['actual_read_blocks']==[dict(index=i,**b) for i,b in enumerate(blocks)],'Actual primary anchors '+paper['key'])
        check(paper['actual_read_block_ids']==list(range(len(blocks))),'All body blocks '+paper['key'])
        check(not paper['visual_figures_reviewed'] and not paper['author_experiments_independently_reproduced'],'Reading limitations')
        if paper['key']=='lesion_loss_analysis':
            app=ET.parse(texts/paper['raw_file']).find('.//app')
            expected=[dict(xml_iteration_index=i,tag=e.tag,text=' '.join(''.join(e.itertext()).split())) for i,e in enumerate(app.iter()) if e.tag in ('p','disp-formula')]
            check(paper['back_appendix_a_actual_read_blocks']==expected,'Appendix A anchors')
    author=ROOT/'literature/source_cache/unified_focal_author_code_2026-10-03';ar=read(author/'reading_provenance.json')
    bind(author/'attempt_01.json',ar['acquisition_sha256']);bind(ROOT/ar['audit_report'],ar['audit_report_sha256'])
    check(ar['original_syntax_error']['type']=='IndentationError' and ar['original_syntax_error']['line']==262,'Original author syntax failure')
    check(not ar['author_package_executed'] and not ar['TensorFlow_imported'] and not ar['original_bytes_changed'],'Original author package not run/changed')
    for item in ar['sources']:
        p=author/item['file'];bind(p,item['sha256']);check(item['actual_read_utf8_text']==p.read_text(encoding='utf-8'),'Author reading text '+item['file'])
    port=complete(ROOT/'experiments/unified_focal_binary_cpu_port/attempt_01.json')
    guards=complete(ROOT/'experiments/unified_focal_binary_cpu_port/output_bias_and_input_guards_attempt_01.json')
    check(len(port['gradient_checks'])==24 and port['network_forward_calls']==0 and port['training_updates']==0,'24 finite differences, no neural experiment')
    bind(ROOT/'experiments/unified_focal_binary_cpu_port.py',port['port_sha256']);bind(author/'loss_functions.py',port['author_source_sha256'])
    bind(ROOT/'experiments/unified_focal_binary_cpu_port.py',guards['port_sha256'])
    figfolder=ROOT/'figures/mc_rc_frozen_development_diagnosis_cpu';figure=read(figfolder/'provenance.json')
    bind(ROOT/'experiments/plot_mc_rc_frozen_development_diagnosis_cpu.py',figure['script_sha256'])
    for item in figure['outputs']+figure['source_bindings']:bind(ROOT/item['path'],item['sha256'])
    folders=[diagnosis,ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu',single,minimal,
        ROOT/'experiments/unified_focal_binary_cpu_port',texts,author,
        ROOT/'literature/source_cache/loss_sampling_bias_search_2026-10-03',figfolder]
    folders.append(ROOT/'literature/source_cache/development_loss_entry_snapshot_2026-10-03')
    for folder in folders:
        for p in folder.rglob('*'):
            if p.is_file():include(p)
    for pattern in ('*DEVELOPMENT_AND_LOSS*.md','*FROZEN_GLOBAL_LOCAL_DEVELOPMENT*.md','*FROZEN_DEVELOPMENT_AFFINE*.md','*GLOBAL_LOCAL_SINGLE_CASE_LOSS*.md','*GLOBAL_LOCAL_FIXED_PLANE_FIT*.md','*LOSS_AND_COVERAGE*.md','UNIFIED_FOCAL_BINARY_CPU_PORT_PLAN*.md'):
        for p in ROOT.glob(pattern):include(p)
    names=['README.md','EXPERIMENT_QUEUE.md','experiments/frozen_development_affine_resume_generation.json',
        'experiments/mc_rc_full_affine_task_metrics_cpu.py','experiments/unified_focal_binary_cpu_port.py',
        'experiments/verify_unified_focal_binary_cpu_port.py','experiments/check_unified_focal_output_bias_cpu.py',
        'experiments/diagnose_mc_rc_frozen_global_local_development_cpu.py',
        'experiments/diagnose_mc_rc_frozen_global_local_development_attempt02_cpu.py',
        'experiments/verify_mc_rc_frozen_global_local_development_cpu.py',
        'experiments/run_mc_rc_global_local_single_case_loss_cpu.py','experiments/verify_mc_rc_global_local_single_case_loss_cpu.py',
        'experiments/report_mc_rc_global_local_single_case_loss_cpu.py','experiments/report_mc_rc_frozen_development_diagnosis_cpu.py',
        'experiments/plot_mc_rc_frozen_development_diagnosis_cpu.py',
        'experiments/run_mc_rc_global_local_fixed_plane_fit_cpu.py','experiments/verify_mc_rc_global_local_fixed_plane_fit_cpu.py',
        'experiments/report_mc_rc_global_local_fixed_plane_fit_cpu.py',
        'literature/2026-10-03_unified_focal_author_code_audit.md',
        'literature/2026-10-03_loss_sampling_bias_search_plan.md','literature/2026-10-03_loss_sampling_bias_selection.md',
        'literature/2026-10-03_loss_sampling_bias_fulltext_reading.md','literature/search_loss_sampling_bias_2026_10_03.py',
        'literature/fetch_loss_sampling_bias_fulltexts_2026_10_03.py','literature/register_loss_sampling_bias_and_author_reading_2026_10_03.py']
    for name in names:include(ROOT/name)
    include(Path(__file__))
    for p in files:
        if p.suffix=='.py' and p!=author/'loss_functions.py':ast.parse(p.read_text(encoding='utf-8'))
        if p.suffix=='.md' and not p.is_relative_to(ROOT/'literature/source_cache'):
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if not target.startswith(('https://','http://','#','mailto:')):check((p.parent/target.split('#',1)[0]).exists(),'Broken link '+str(p)+': '+target)
    manifest=dict(scope='Source/archive integrity and disclosed diagnostic evidence; not scientific confirmation',
        new_primary_bodies_read=2,new_body_text_blocks=157,developer_diagnosis_patients=11,developer_diagnosis_series=19,
        developer_checkpoint_replayed_planes=57,real_single_developer_training_updates=9000,
        synthetic_preflight_training_updates=20,single_developer_draws_replayed=4000,single_developer_planes_replayed=6,
        minimal_fixed_plane_training_updates=1000,minimal_plane_replayed=1,
        original_failed_diagnosis_total_forward_calls_known=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,
        files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
    if '--write' in sys.argv:OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:check(OUT.exists() and read(OUT)==manifest,'Stage manifest differs')
    print(json.dumps(dict(files=len(files),errors=errors,new_primary_bodies_read=2,training_updates=9000,publication_claim_confirmed=False),ensure_ascii=False))
    return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
