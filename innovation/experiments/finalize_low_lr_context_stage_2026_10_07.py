"""Write terminal records from observed tool exits; never infer exits from result.complete."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--timing-session',required=True,type=int)
    ap.add_argument('--metadata-session',type=int,default=None);ap.add_argument('--metadata-chunk',required=True);ap.add_argument('--timing-exit',required=True,type=int)
    ap.add_argument('--metadata-exit',required=True,type=int);a=ap.parse_args()
    assert a.timing_session==41977 and a.timing_exit==a.metadata_exit==0
    fitpath=ROOT/'experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/attempt01.json'
    qpath=ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json'
    tpath=ROOT/'experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07/attempt01.json'
    mpath=tpath.parent/'independent_metadata_and_time_aggregation_attempt01.json'
    fit,q,t,m=map(read,(fitpath,qpath,tpath,mpath))
    exits=read(ROOT/'SESSION_OBSERVED_EXITS_LOW_LR_CONTEXT_2026-10-07.json')
    qexits=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_CPU_RESOURCE_2026-10-07.json')
    assert all(v['complete'] and not v['errors'] for v in (fit,q,t,m))
    assert m['source_sha256']==sha(tpath)
    assert exits['training_result_sha256']==sha(fitpath) and qexits['qualification_result_sha256']==sha(qpath)
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,
        timing_observed_tool_session_id=a.timing_session,timing_observed_tool_exit=a.timing_exit,
        metadata_verifier_observed_tool_session_id=a.metadata_session,metadata_verifier_observed_tool_exit=a.metadata_exit,
        metadata_verifier_observed_tool_chunk_id=a.metadata_chunk,
        timing_result_sha256=sha(tpath),metadata_verifier_result_sha256=sha(mpath),
        metadata_verifier_did_not_replay_neural_pixels=True,GT_files_loaded=0,actual_training_updates=0,
        own_live_runs=[],publication_claim_confirmed=False)
    write(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_FOV_LOW_LR_2026-10-07.json',receipt)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,all_own_runs_terminal_from_observed_tool_exits=True,
        own_live_runs=[],training_observed_tool_session_id=exits['training_observed_tool_session_id'],
        training_observed_tool_exit=exits['training_observed_tool_exit'],
        independent_verifier_observed_tool_session_id=exits['independent_verifier_observed_tool_session_id'],
        independent_verifier_observed_tool_exit=exits['independent_verifier_observed_tool_exit'],
        resource_qualification_observed_tool_session_id=qexits['qualification_observed_tool_session_id'],
        resource_qualification_observed_tool_exit=qexits['qualification_observed_tool_exit'],
        resource_verifier_observed_tool_session_id=qexits['independent_verifier_observed_tool_session_id'],
        resource_verifier_observed_tool_exit=qexits['independent_verifier_observed_tool_exit'],
        fov_timing_observed_tool_session_id=a.timing_session,fov_timing_observed_tool_exit=a.timing_exit,
        fov_metadata_verifier_observed_tool_session_id=a.metadata_session,fov_metadata_verifier_observed_tool_exit=a.metadata_exit,
        fov_metadata_verifier_observed_tool_chunk_id=a.metadata_chunk,
        inherited_tool_exit_evidence='Existing observed-exit receipts from previous visible execution, not inferred from complete.',
        task_gain_audit_and_verifier_exit_evidence='User-provided continuation summary explicitly reports both actual exit 0; no invented session IDs.',
        expected_failed_entry_preserved=dict(AST_exit=1,entry_exit=1,MRI_loaded=False,
            evidence_file='experiments/mc_rc_3d_19series_fov_entry_failed_ast_2026_10_07.json',
            preserved_source_file='experiments/time_mc_rc_3d_19series_fov_cpu_2026_10_07.py.failed_ast_attempt01'),
        continuation_inspection_failures_preserved=[dict(tool_exit=1,action='PowerShell native argument -c quoting removed inner double quotes',
            effect='Metadata inspection only; Python syntax failure before reading any file; corrected using UTF-8 stdin.'),
            dict(action='rg Windows glob path rejected',effect='Read-only search; repeated with -g filters.')],
        new_cpu_backbone_updates=2048,resource_qualification_updates_discarded=66,formal19series_training_updates=0,
        new_gpu_updates=0,scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (fitpath,qpath,tpath,mpath,
            ROOT/'SESSION_OBSERVED_EXITS_LOW_LR_CONTEXT_2026-10-07.json',ROOT/'SESSION_OBSERVED_EXITS_19SERIES_CPU_RESOURCE_2026-10-07.json')])
    write(ROOT/'SESSION_EXECUTION_LEDGER_LOW_LR_CONTEXT_2026-10-07.json',ledger)
    plot=ROOT/'figures/mc_rc_3d_backbone_context_low_lr_2026_10_07/last_checkpoint_fit_comparison_v2.png'
    write(ROOT/'SESSION_LOW_LR_FIGURE_ACTUAL_VISUAL_REVIEW_2026-10-07.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        complete=True,actual_view_image_completed=True,path=plot.relative_to(ROOT).as_posix(),sha256=sha(plot),
        observations=['Current continuation directly viewed v2 PNG using view_image.',
        'Legend clears panels; gate line .90 and all eight values/labels visible; zero native .001 bars retained.',
        'Scientific plot is a one-patient/one-series fit diagnostic; does not compare common initial weights.'],
        prior_false_snapshot_preserved=True))
    raw=subprocess.run(['nvidia-smi','--query-gpu=timestamp,memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],
        capture_output=True,text=True,check=True,timeout=15).stdout.strip()
    fields=[x.strip() for x in raw.split(',')];assert len(fields)==4
    write(ROOT/'SESSION_GPU_OBSERVATION_LOW_LR_CLOSE_2026-10-07.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        raw_totals_observation=raw,free_bytes=int(fields[1])*1048576,total_bytes=int(fields[2])*1048576,utilization_percent=int(fields[3]),
        startup_floor_bytes=8_000_000_000,full_GPU_startup_eligible=int(fields[1])*1048576>=8_000_000_000,
        CUDA_initialized_by_observation=False,pids_requested=False,pids_modified=False))
    costs=[]
    for qa,ta in zip(q['arms'],t['arms']):
        assert qa['kind']==ta['kind'] and ta['total_tiles']==1139
        costs.append(dict(kind=qa['kind'],cache_seconds=qa['cache_elapsed_seconds'],
            median_update_seconds=qa['median_timed_seconds'],max_update_seconds=qa['max_timed_seconds'],
            all19_FOV_seconds=ta['all19_complete_inference_seconds'],all19_input_seconds=ta['all19_load_and_input_hash_seconds'],
            planned19998_updates_median_seconds=19998*qa['median_timed_seconds'],
            planned19998_updates_sample_max_seconds=19998*qa['max_timed_seconds']))
    budget=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,formal_training_started=False,
        calculations_only=True,measurements_from_single001_initial_weights=True,
        proposed_equal_patient_budget_per_arm=19998,complete_patient_rounds=1818,updates_per_patient=1818,arms=costs,
        two_arm_pure_update_median_hours=sum(c['planned19998_updates_median_seconds'] for c in costs)/3600,
        two_arm_pure_update_sample_max_hours=sum(c['planned19998_updates_sample_max_seconds'] for c in costs)/3600,
        two_arm_single_development_FOV_minutes=sum(c['all19_FOV_seconds'] for c in costs)/60,
        validation_complete_FOV_cost_not_measured=True,independent_replay_and_checkpoint_cost_not_in_estimates=True,
        estimates_are_not_guarantees=True,publication_claim_confirmed=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (qpath,tpath,mpath)])
    write(ROOT/'SESSION_LOW_LR_19SERIES_TRAINING_BUDGET_PREPARATION_2026-10-07.json',budget)
    rows=['| 输入 | 缓存 s | 更新 median/max s | 全19 FOV s | 构造+hash s | 1139 tiles |',
          '|---|---:|---:|---:|---:|---:|']
    for c in costs:rows.append(f"| {c['kind']} | {c['cache_seconds']:.2f} | {c['median_update_seconds']:.5f}/{c['max_update_seconds']:.5f} | {c['all19_FOV_seconds']:.2f} | {c['all19_input_seconds']:.2f} | 1139 |")
    report='''# 19开发series真实CPU资源与完整推断成本

真实训练资源资格和完整FOV无评分计时均已完成并实际exit0，独立batch重建和metadata聚合核验也实际exit0。19series/11患者没有删样本。两臂每臂33资源更新全部丢弃；当前正式训练更新0。原单001 low-LR最后模型只用于计时，不是19series充分适配的模型。

'''+ '\n'.join(rows)+f'''

每臂 image+float32 GT 缓存1,909,712,000 bytes。实际4 intra-op/1 interop、below-normal、无CUDA；原资源JSON的内嵌cpu_threads=1为遗留guard常量，顶层4为实际设置。完整FOV计时不读GT，不评分，不保存体积；输出概率SHA证明生产记录，独立核验只核tile覆盖/时间聚合/来源，不是独立神经像素重放。计时总墙钟{t['elapsed_seconds']:.2f}s。

按新准备的每臂19,998更新（1818完整患者轮，每患者1818步）计算，两臂纯更新中位数估算{budget['two_arm_pure_update_median_hours']:.2f}小时；按本次样本最大更新耗时估算{budget['two_arm_pure_update_sample_max_hours']:.2f}小时。后者也不是未来上界。两臂一次开发完整FOV另约{budget['two_arm_single_development_FOV_minutes']:.2f}分钟。还需加入输入构造、正式随机初始模型的实际速度、checkpoint/核验，以及未实测的四验证推断；不得把纸面20k情景当完工保证或充分能力。

下一科学实验需另立正式协议：共同随机初始化、完全相同患者/series/GT/增强流、同容量和更新数、同最后checkpoint规则。低LR单001两臂从不同初始模型出发，不能取代此控制。正式预算冻结后再启动，能力门槛不调低；只在两臂最终权重冻结后读开发/已见验证效果。八确认和locked IXI test继续关闭，科学确认0。

[资源资格](experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json) · [完整FOV计时](experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07/attempt01.json) · [metadata核验](experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07/independent_metadata_and_time_aggregation_attempt01.json) · [预算计算](SESSION_LOW_LR_19SERIES_TRAINING_BUDGET_PREPARATION_2026-10-07.json)。
'''
    with (ROOT/'MC_RC_3D_19SERIES_CPU_RESOURCE_AND_FOV_RESULT_2026-10-07.md').open('x',encoding='utf-8') as f:f.write(report)
    overview='''# 低学习率接续阶段结果

本阶段新增3篇原文、3篇重点摘要，完成两臂共2048次单001低LR全骨干更新、66次全部丢弃的多患者资源更新，以及两臂全19series各1139tile的完整FOV计时。科学确认患者0，可发表claim尚未确认，长期goal active。正式19series训练尚未启动。

native最后模型full Dice .967647、recall .976261、absRVE .017804；PCHIP .963253/.972305/.018793；两臂均过原单系列拟合gate。全部history、模型/预测SHA、三head functional/module、四域端点、生产和NumPy坐标及float64独立核验通过。旧native空预测未在低LR下复现；两臂不同初始权重，这不是公平SR效益或唯一病因证明。旧高LR失败保留。

HCC原文中AUC上升伴accuracy/sensitivity下降、主要DeLong差异不显著；Madras2018和Mozannar2020已经覆盖按两路径预期损失选择gate。因此单独gain head不支持方法首创。下一待检验问题是充分适配后是否仍有稳定、可预测且可独立确认的病灶修正余量；加入双路径成本头、已知defer、强PCHIP、直接任务、普通风险/误差和同预算随机等强对照。57,600配置合成gain目标检查及独立复算通过，仅为已知理论实现核验，无MRI效果。

资源资格两臂各33步、全19series覆盖、各患者3步、GT/增强一致、梯度有限；最终更新后权重丢弃。完整FOV计时无GT/任务评分，其独立核验只针对metadata/时间。正式多患者CPU预算现在可以依据完整实测准备，仍需共同随机初始化的正式入口及资格。GPU授权保持，最新物理GPU观测单独保存；不操作用户终端训练。

角色仍11开发/19series、4已见验证/9series、8保留确认/12series，当前四验证效果未在本阶段打开，八确认和locked IXI test关闭。没有改根环境或.gitignore。可见请求、公开进度、用户接续摘要、论文来源/版本/失败、脚本和结果均保存到innovation；未展示的历史原话不伪造。修复图v2已在本次直接view_image核看，原false快照/遮挡v1保留。

[拟合与独立结果](MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_RESULT_2026-10-07.md) · [资源成本](MC_RC_3D_19SERIES_CPU_RESOURCE_AND_FOV_RESULT_2026-10-07.md) · [创新判断](INNOVATION_DECISION_AFTER_DEFER_READING_2026-10-07.md) · [defer原文阅读](literature/2026-10-07_learning_to_defer_primary_collision_reading.md) · [HCC阅读](literature/2026-10-07_hcc_sr_task_primary_reading.md) · [gain目标审计](TASK_GAIN_TARGET_CPU_AUDIT_RESULT_2026-10-07.md) · [真实退出ledger](SESSION_EXECUTION_LEDGER_LOW_LR_CONTEXT_2026-10-07.json) · [可见对话](SESSION_VISIBLE_DIALOGUE_LOW_LR_CONTINUATION_2026-10-07.md)。
'''
    with (ROOT/'SESSION_RESULT_LOW_LR_CONTEXT_2026-10-07.md').open('x',encoding='utf-8') as f:f.write(overview)
    print(json.dumps(dict(complete=True,costs=costs,two_arm_median_hours=budget['two_arm_pure_update_median_hours']),ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
