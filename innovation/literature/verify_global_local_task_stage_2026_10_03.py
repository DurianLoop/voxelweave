"""Complete batch sources, outcomes, denominators and artifact verification; no model execution."""
import ast,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/global_local_task_stage_manifest_2026-10-03.json'
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[];files=set()
    def check(value,message):
        if not value:errors.append(message)
    def include(path):
        p=Path(path);check(p.is_file(),'Missing '+str(p))
        if p.is_file():files.add(p)
    def bind(path,digest):
        include(path);check(Path(path).is_file() and sha(path)==digest,'SHA '+str(path))
    def completed(path):
        include(path);r=read(path);check(r['complete'] and not r['errors'],'Not completed '+str(path));return r
    trainfile=ROOT/'experiments/mc_rc_global_local_task_training_cpu/attempt_01.json'
    valfile=ROOT/'experiments/mc_rc_global_local_task_validation_cpu/attempt_01.json'
    train=completed(trainfile);val=completed(valfile)
    proof=completed(valfile.parent/'independent_metrics_and_checkpoint_attempt_01.json')
    check(train['updates_completed']==20000 and sum(train['training_sampling_counts'].values())==20000,'Fixed20k budget')
    check(train['model_parameters']==981602 and len(train['training_patient_ids'])==11 and len(train['training_series_uids'])==19,'Known model/training19 identity')
    check(len(val['evaluations'])==18 and {e['patient'] for e in val['evaluations']}=={'VS-MC-RC-020','VS-MC-RC-022','VS-MC-RC-024','VS-MC-RC-025'},'All4 validation patients/18 inputs')
    check(len({e['uid'] for e in val['evaluations']})==9 and {e['method'] for e in val['evaluations']}=={'raw_pchip','raw_linear'},'9series/two inputs')
    check(proof['checkpoint_replayed_planes']==54 and len(proof['evaluations'])==18 and proof['patient_first_aggregation_verified'],'54 replay planes/all18 independent metrics')
    check(proof['same_architecture_replay'] and not proof['second_independently_trained_model'],'Replay not second independently trained model')
    check(proof['capability_gate_passed']==val['capability_gate_passed']==all(val['capability_gate_checks'].values()),'Capability verdict')
    bind(valfile,proof['result_sha256'])
    bind(ROOT/'experiments/run_mc_rc_global_local_task_training_cpu.py',train['script_sha256'])
    bind(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py',train['support_sha256'])
    bind(ROOT/train['protocol_file'],train['protocol_sha256'])
    bind(ROOT/train['checkpoint_file'],train['checkpoint_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_global_local_task_validation_cpu.py',proof['script_sha256'])
    for row in train['source_bindings']+val['source_bindings']+val['code_bindings']:
        bind(ROOT/row['path'],row['sha256'])
    bind(ROOT/val['evaluation_protocol'],val['evaluation_protocol_sha256'])
    bind(ROOT/val['diagnostic_split_file'],val['diagnostic_split_sha256'])
    split=read(ROOT/val['diagnostic_split_file'])
    check(split['validation_neural_forwards_at_freeze']==0 and not split['final_scientific_split_activated'],'Frozen diagnostic split, confirmation closed')
    for e in val['evaluations']:bind(ROOT/e['prediction_file'],e['prediction_file_sha256'])
    for r in (train,val,proof):
        check(not r['gpu_initialized'] and not r['confirmation_patients_opened'] and not r['native_hidden_MR_pixels_decoded'],'CPU/confirmation/hidden-MR scope')
        check(r['scientific_confirmation_patients']==0 and not r['publication_claim_confirmed'],'No scientific confirmation')
    check(train['validation_neural_forwards_before_final_checkpoint']==0,'No pre-freeze validation')
    calls=sum(r[k] for r in (train,val,proof) for k in ('global_forward_calls','local_forward_calls'))
    report=read(valfile.parent/'report_provenance.json')
    bind(ROOT/report['report'],report['report_sha256'])
    bind(ROOT/'experiments/report_mc_rc_global_local_task_cpu.py',report['script_sha256'])
    check(report['training_updates']==20000 and report['total_model_branch_calls']==calls,'Report model counts')
    for r in report['source_bindings']:bind(ROOT/r['path'],r['sha256'])
    figurefolder=ROOT/'figures/mc_rc_global_local_task_cpu'
    figures=read(figurefolder/'provenance.json')
    bind(ROOT/'experiments/plot_mc_rc_global_local_task_cpu.py',figures['script_sha256'])
    for item in figures['outputs']+figures['source_bindings']:bind(ROOT/item['path'],item['sha256'])
    inputfile=ROOT/'experiments/mc_rc_validation_task_input_cpu/attempt_01.json'
    prod=completed(inputfile);ip=completed(inputfile.parent/'independent_all9_observed_inputs_and_label_axes_attempt_01.json')
    bind(inputfile,ip['result_sha256'])
    check(ip['observed_dicom_planes_verified']==145 and ip['sparse_inputs_verified']==36 and ip['labels_verified']==9,'Input proof145/36/9')
    check(not prod['non_observed_MR_pixels_decoded'] and not ip['non_observed_MR_pixels_decoded'],'Observed-only validation packages')
    for row in prod['series']:bind(ROOT/row['observed_package'],row['observed_package_sha256'])
    for record,key,file in ((prod,'script_sha256','audit_mc_rc_validation_task_input_cpu.py'),
                            (prod,'loader_sha256','mc_rc_task_roles_input_cpu.py'),
                            (ip,'script_sha256','verify_mc_rc_validation_task_input_cpu.py')):
        bind(ROOT/'experiments'/file,record[key])
    prepfile=ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json'
    vp=completed(prepfile);bind(prepfile,prod['preparation_sha256'])
    bind(ROOT/'experiments/prepare_mc_rc_validation_task_cases_cpu.py',vp['script_sha256'])
    geometry=completed(ROOT/'experiments/mc_rc_global_local_geometry_cpu/attempt_01.json')
    check(len(geometry['real_inputs'])==9 and sum(len(e['complete_planes_checked']) for e in geometry['real_inputs'])==27 and geometry['synthetic_physical_z_checks']==12,'9/27real and12 synthetic physical geometry')
    check(geometry['neural_forward_calls']==0 and not geometry['validation_task_effects_read'],'No geometry model effects')
    bind(ROOT/'experiments/audit_mc_rc_global_local_geometry_cpu.py',geometry['script_sha256'])
    bind(ROOT/'experiments/mc_rc_global_local_geometry_reference_cpu.py',geometry['reference_sha256'])
    diagnosis=completed(ROOT/'experiments/mc_rc_global_local_supervision_cpu/attempt_01.json')
    check(len(diagnosis['series'])==19 and diagnosis['samples_completed']==608 and diagnosis['neural_forward_calls']==0,'19/608 no-forward supervision diagnosis')
    check(not diagnosis['MRI_pixels_loaded'] and not diagnosis['checkpoint_loaded'] and not diagnosis['validation_or_confirmation_labels_loaded'],'Label-only development diagnosis')
    bind(ROOT/'experiments/diagnose_mc_rc_global_local_supervision_cpu.py',diagnosis['script_sha256'])
    bind(ROOT/'MC_RC_GLOBAL_LOCAL_SUPERVISION_DIAGNOSTIC_PLAN_2026-10-03.md',diagnosis['protocol_sha256'])
    metricfile=ROOT/'experiments/mc_rc_task_metrics_cpu_sources.json';m=read(metricfile)
    bind(ROOT/'experiments/mc_rc_task_metrics_cpu.py',m['output_sha256'])
    bind(ROOT/'experiments/prepare_mc_rc_task_metrics_cpu.py',m['generator_sha256'])
    for row in m['functions']:
        source=ROOT/row['source'];bind(source,row['source_sha256'])
        content=source.read_text(encoding='utf-8');node=next(n for n in ast.parse(content).body if isinstance(n,ast.FunctionDef) and n.name==row['function'])
        check(hashlib.sha256(ast.get_source_segment(content,node).encode()).hexdigest()==row['extracted_utf8_sha256'],'Extracted metric algorithm '+row['function'])
    texts=ROOT/'literature/source_cache/global_local_task_fulltexts_2026-10-03'
    reading=read(texts/'reading_provenance.json')
    check(reading['new_primary_bodies_read']==2 and reading['actual_new_body_text_blocks']==172 and len(reading['rereading']['actual_read_block_ids'])==19,'2new172/19old reading')
    bind(ROOT/reading['report'],reading['report_sha256'])
    bind(ROOT/'literature/register_global_local_task_reading_2026_10_03.py',reading['script_sha256'])
    bind(texts/'attempt_01.json',reading['acquisition_sha256'])
    for paper in reading['papers']:
        for prefix in ('raw','block','text'):bind(texts/paper[prefix+'_file'],paper[prefix+'_sha256'])
        blocks=read(texts/paper['block_file'])
        check(paper['actual_read_blocks']==[dict(index=i,**blocks[i]) for i in paper['actual_read_block_ids']],'Read primary anchors '+paper['key'])
        check(not paper['author_experiments_independently_reproduced'] and not paper['visual_figures_reviewed'],'Reading bounds '+paper['key'])
    old=reading['rereading'];bind(ROOT/old['source_file'],old['source_sha256'])
    check(old['actual_read_blocks']==[dict(index=i,**read(ROOT/old['source_file'])[i]) for i in old['actual_read_block_ids']],'Old reread anchors')
    lossfolder=ROOT/'literature/source_cache/task_loss_followup_fulltext_2026-10-03';loss=read(lossfolder/'reading_provenance.json')
    check(loss['new_primary_bodies_read']==1 and loss['actual_new_body_text_blocks']==162,'New loss reading162')
    bind(ROOT/loss['report'],loss['report_sha256']);bind(lossfolder/'attempt_01.json',loss['acquisition_sha256'])
    bind(ROOT/'literature/register_task_loss_followup_reading_2026_10_03.py',loss['script_sha256'])
    paper=loss['paper'];blocks=read(lossfolder/paper['block_file'])
    for prefix in ('raw','block','text'):bind(lossfolder/paper[prefix+'_file'],paper[prefix+'_sha256'])
    check(loss['actual_read_blocks']==[dict(index=i,**blocks[i]) for i in loss['actual_read_block_ids']],'Loss actual reading anchors')
    folders=['experiments/mc_rc_global_local_task_training_cpu','experiments/mc_rc_global_local_task_validation_cpu',
        'experiments/mc_rc_validation_task_case_preparation','experiments/mc_rc_validation_task_input_cpu',
        'experiments/mc_rc_global_local_geometry_cpu','experiments/mc_rc_global_local_supervision_cpu',
        'literature/source_cache/global_local_task_fulltexts_2026-10-03','literature/source_cache/global_local_task_search_2026-10-03',
        'literature/source_cache/task_loss_followup_fulltext_2026-10-03','literature/source_cache/task_loss_followup_search_2026-10-03',
        'figures/mc_rc_global_local_task_cpu']
    for folder in folders:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file():include(p)
    for p in (ROOT/'experiments').glob('*global_local*.py'):include(p)
    for p in (ROOT/'literature').glob('*global_local*'):
        if p.is_file() and p!=OUT:include(p)
    for p in (ROOT/'literature').glob('*task_loss_followup*'):
        if p.is_file():include(p)
    for pattern in ('*GLOBAL_LOCAL*.md','*VALIDATION_OBSERVED*.md'):
        for p in ROOT.glob(pattern):include(p)
    names=['README.md','EXPERIMENT_QUEUE.md','experiments/mc_rc_task_roles_input_cpu.py',
        'experiments/prepare_mc_rc_validation_task_cases_cpu.py','experiments/audit_mc_rc_validation_task_input_cpu.py',
        'experiments/prepare_validation_input_verifier_cpu.py','experiments/verify_mc_rc_validation_task_input_cpu.py',
        'experiments/mc_rc_task_metrics_cpu.py','experiments/mc_rc_task_metrics_cpu_sources.json','experiments/prepare_mc_rc_task_metrics_cpu.py',
        'experiments/global_local_fair_matrix_followup_preparation_2026-10-03.json']
    for name in names:include(ROOT/name)
    include(Path(__file__))
    for p in files:
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
        if p.suffix=='.md':
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if not target.startswith(('https://','http://','#','mailto:')):
                    check((p.parent/target.split('#',1)[0]).exists(),'Broken link '+str(p)+': '+target)
    manifest=dict(scope='3new primary bodies334blocks,19old reread; 20kCPU training,9/18validation and54same-model replay; observed-only proof and no-forward geometry/supervision; all failures/plans/public dialogue.',
        new_primary_bodies_read=3,new_primary_body_text_blocks=334,old_reread_blocks=19,
        training_updates=20000,total_model_branch_calls=calls,validation_patients=4,validation_series=9,
        validation_conditions=18,capability_gate_passed=val['capability_gate_passed'],
        scientific_confirmation_patients=0,publication_claim_confirmed=False,
        files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
    if '--write' in sys.argv:OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:check(OUT.exists() and read(OUT)==manifest,'Stage manifest differs')
    print(json.dumps(dict(files=len(files),errors=errors,new_primary_bodies_read=3,training_updates=20000,
        total_model_branch_calls=calls,capability_gate_passed=val['capability_gate_passed'],scientific_confirmation_patients=0),ensure_ascii=False))
    return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
