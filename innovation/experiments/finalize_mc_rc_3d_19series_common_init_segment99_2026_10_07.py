"""Record verified formal short-segment timing and final-evaluation preparation; no new scoring."""
import argparse,hashlib,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,data):
    with p.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verifier-session',required=True,type=int)
    ap.add_argument('--verifier-chunk',required=True);ap.add_argument('--verifier-exit',required=True,type=int);args=ap.parse_args()
    assert args.verifier_session==96593 and args.verifier_exit==0
    sys.stdout.reconfigure(encoding='utf-8');p=OUT/'independent_segment99_attempt01.json';proof=read(p)
    q=read(OUT/'invocation01.json');ex=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_2026-10-07.json')
    assert q['complete'] and proof['complete'] and not q['errors'] and not proof['errors'] and proof['all198_batches_verified']
    assert ex['training_observed_tool_exit']==0 and ex['training_result_sha256']==sha(OUT/'invocation01.json')
    assert proof['source_sha256']==sha(OUT/'invocation01.json')
    for b in proof['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    new(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_VERIFIER_2026-10-07.json',dict(
        created_utc=datetime.now(timezone.utc).isoformat(),complete=True,verifier_observed_tool_session_id=args.verifier_session,
        verifier_observed_tool_chunk_id=args.verifier_chunk,verifier_observed_tool_exit=args.verifier_exit,
        verifier_result_sha256=sha(p),all198_batches_verified=True,actual_new_training_updates=0,
        full_FOV_not_replayed=True,own_live_runs_at_this_receipt=[],publication_claim_confirmed=False))
    arms=[dict(kind=a['kind'],updates=99,cache_seconds=a['cache_seconds'],median_update_seconds=a['new_update_median_seconds'],
        max_update_seconds=a['new_update_max_seconds'],last_loss=json.loads((ROOT/a['segment_history_file']).read_text(encoding='utf-8').splitlines()[-1])['loss'],
        initial_weights_sha256=a['initial_weights_sha256'],segment_checkpoint_file=a['segment_checkpoint_file'],
        segment_checkpoint_sha256=a['segment_checkpoint_sha256']) for a in q['arms']]
    forecast=sum(a['median_update_seconds']*19998 for a in arms)/3600
    remain=sum(a['median_update_seconds']*(19998-99) for a in arms)/3600
    cost=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,measurements_from_formal_first99=True,arms=arms,
        formal_completed_cpu_updates=198,formal_remaining_cpu_updates=39798,new_gpu_updates=0,
        full_two_arm_pure_update_median_forecast_hours=forecast,remaining_pure_update_median_forecast_hours=remain,
        original_resource_only_forecast_hours=19.00216070446535,formal_first_segment_actual_wall_seconds=q['elapsed_seconds'],
        original_cumulative_wall_limit_seconds=90000,supplement_cumulative_wall_limit_seconds=108000,
        forecasts_are_not_guarantees=True,slowdown_cause_not_identified=True,task_effects_scored=False,
        final_training_budget_completed=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=v.relative_to(ROOT).as_posix(),sha256=sha(v)) for v in (OUT/'invocation01.json',p,
            ROOT/'MC_RC_3D_19SERIES_COMMON_INIT_CPU_PROTOCOL_2026-10-07.md',ROOT/'MC_RC_3D_19SERIES_COMMON_INIT_CPU_WALL_ADDENDUM_2026-10-07.md')])
    new(ROOT/'SESSION_19SERIES_COMMON_INIT_SEGMENT99_COST_RESULT_2026-10-07.json',cost)
    lines=['| 输入 | 正式已完成 | cache s | 更新median/max s | 最后训练loss（非任务端点） |',
        '|---|---:|---:|---:|---:|']
    for a in arms:lines.append(f"| {a['kind']} | 99 | {a['cache_seconds']:.2f} | {a['median_update_seconds']:.5f}/{a['max_update_seconds']:.5f} | {a['last_loss']:.6f} |")
    doc='''# 共同初始化正式训练前99步结果

两臂共198次正式更新已完成，主训练和独立核验实际exit0；完整39,996预算尚未完成，MRI任务评分0，科学确认0。它们是正式训练前缀，保留AdamW moments和随机流继续；旧66资源更新仍全部丢弃、不混计。

'''+ '\n'.join(lines)+f'''

共同全新随机初始state SHA为`{arms[0]['initial_weights_sha256']}`。两臂各19series全覆盖、11患者各9步。全部198输入/GT/primitive由独立实现重建一致；不可变99checkpoint/history SHA、优化器每参数step99/有限moments、两臂GT/增强、全部三head module/functional概率和阈值、独立float64 BCE+Dice通过。未重新训练99步，梯度有限性来自主入口；只核最后batch，不是完整FOV神经重放或任务泛化。24次合成optimizer更新仅用于预检断点资格，不计198。

本次正式更新实测比此前33步资源资格慢，原因未知；原19.00h纯更新估值保留，修正全两臂纯更新median估值为{forecast:.2f}h，剩余约{remain:.2f}h。cache/保存/资源波动额外计；均不是未来保证。原25h完整执行不宣称成功；依据无任务评分的真实资源测量，另立资源补充将累计训练停止上限设30h，科学更新数19,998/臂、LR/初始化/数据/增强/能力gate不变，源码和原config不覆盖。

后续相同state/AdamW/流续至最后权重；两臂同时冻结后再读开发/已见验证任务效果。最终能力评价准备仍无可执行入口，现有metadata计算56完整预测packbits原始字节115,491,840（不含NPZ元数据）以支持后续独立全FOV核验。四已见验证门槛.70/.65/.70/.50、全部9series TP>0/四患者full和missing均正保留；八确认与locked IXI test关闭。

[正式freeze](MC_RC_3D_19SERIES_COMMON_INIT_CPU_PROTOCOL_2026-10-07.md) · [资源补充](MC_RC_3D_19SERIES_COMMON_INIT_CPU_WALL_ADDENDUM_2026-10-07.md) · [独立短段结果](experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/independent_segment99_attempt01.json) · [资源实测JSON](SESSION_19SERIES_COMMON_INIT_SEGMENT99_COST_RESULT_2026-10-07.json) · [后续全FOV准备](MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_PREPARATION_2026-10-07.md)。
'''
    with (ROOT/'MC_RC_3D_19SERIES_COMMON_INIT_SEGMENT99_RESULT_2026-10-07.md').open('x',encoding='utf-8') as f:f.write(doc)
    print(json.dumps(dict(complete=True,formal_cpu_updates=198,full_pure_update_hours=forecast,remaining_pure_update_hours=remain)))
    return 0
if __name__=='__main__':raise SystemExit(main())
