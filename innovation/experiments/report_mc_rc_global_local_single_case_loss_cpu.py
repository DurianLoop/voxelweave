"""Summarize both independently checked loss arms; no selection or significance claims."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def f(value):return 'undefined' if value is None else f'{value:.6f}'
def main():
    sys.stdout.reconfigure(encoding='utf-8');folder=ROOT/'experiments/mc_rc_global_local_single_case_loss_cpu'
    rp=folder/'attempt_01.json';qp=folder/'independent_metrics_draws_and_checkpoint_attempt_01.json';r,q=read(rp),read(qp)
    assert r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and q['result_sha256']==sha(rp)
    assert q['training_draws_replayed']==4000 and q['checkpoint_replayed_planes']==6
    lines=['# 单012全视野、同预算loss配方诊断完整结果','',
        '两臂同981,602参数/初权重/4000updates/全部4000真实输入与augmentation draws；独立重生成每个draw摘要、核两套最后checkpoint、全部原生指标和6个完整plane重放通过。单开发患者训练内诊断，不是未见验证或loss泛化效果。',
        '', '| loss配方 | full Dice | missing Dice | recall | precision | absRVE | ASSD mm | HD95 mm | fit gate |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---|']
    for arm in r['arms']:
        e=arm['evaluation'];m=e['metrics'];s=m['full_surface'];full=m['full']
        lines.append('| '+arm['name']+' | '+' | '.join(f(v) for v in (full['dice'],m['missing']['dice'],full['recall'],full['precision'],full['absolute_relative_volume_error'],s['assd_mm'],s['hd95_mm']))+' | '+str(e['fit_gate_passed'])+' |')
    lines+=['','预写fit gate为full/missing Dice和full recall≥.90且absRVE≤.10；各臂门槛逐项如下：','']
    for arm in r['arms']:lines.append(arm['name']+': '+json.dumps(arm['evaluation']['fit_gate_checks'],ensure_ascii=False))
    lines+=['','| 配方/域 | TP | FP | FN | Dice | precision | recall | signed RVE | absRVE |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for arm in r['arms']:
        for domain in ('full','missing','anchors','tail'):
            m=arm['evaluation']['metrics'][domain]
            lines.append(f'| {arm["name"]}/{domain} | {m["tp"]} | {m["fp"]} | {m["fn"]} | '+' | '.join(f(m[k]) for k in ('dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error'))+' |')
    first,last=[a['evaluation']['metrics'] for a in r['arms']]
    delta={k:last['full'][k]-first['full'][k] for k in ('dice','recall','absolute_relative_volume_error')}
    passed=[a['name'] for a in r['arms'] if a['evaluation']['fit_gate_passed']]
    lines+=['', 'Unified配方−BCE+Dice（同一训练病例、单seed）full差值：'+json.dumps(delta,ensure_ascii=False)+'。这些是loss配方的整体差值：同时改变pixel项、区域项和per-image/class归约，不能归因于focal本身；loss数值尺度不同，不能用曲线高低比较优劣。',
        '', '通过fit gate的配方：'+(', '.join(passed) if passed else '无')+'。'+('通过只说明该患者能够训练内拟合；仍需全部开发与四验证患者能力、native控制和公平矩阵。' if passed else '固定4000步两配方均未证明完整可拟合性；不得事后加步或调门槛将本轮改写为通过。可另写固定slice/曝光与容量诊断协议。'),
        '', f'真实训练总updates8000；合成preflight另20updates、无真实MR。生产global/local调用{r["global_forward_calls"]}/{r["local_forward_calls"]}，独立重放{q["global_forward_calls"]}/{q["local_forward_calls"]}。CPU单线程、自身below-normal；GPU初始化false，验证/确认患者未加载，隐藏MR不解码。两套训练权重是同一架构/同一病例loss对照，不是第二独立泛化任务网络。',
        '', '[协议](MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_PROTOCOL_2026-10-03.md)、[两臂原始结果](experiments/mc_rc_global_local_single_case_loss_cpu/attempt_01.json)、[draw/指标/完整plane核验](experiments/mc_rc_global_local_single_case_loss_cpu/independent_metrics_draws_and_checkpoint_attempt_01.json)、[两篇新原始文献](literature/2026-10-03_loss_sampling_bias_fulltext_reading.md)。科学确认0，新发表claim未达到，goal active。']
    out=ROOT/'MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_RESULT_2026-10-03.md';assert not out.exists();out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    pp=folder/'report_provenance.json';assert not pp.exists()
    pp.write_text(json.dumps(dict(script_sha256=sha(__file__),report=out.relative_to(ROOT).as_posix(),report_sha256=sha(out),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (rp,qp)],
        training_updates=8000,synthetic_preflight_updates=20,checkpoint_replayed_planes=6,training_draws_replayed=4000,
        passed_fit_arms=passed,full_metric_difference=delta,scientific_confirmation_patients=0,publication_claim_confirmed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report=str(out),passed_fit_arms=passed,full_metric_difference=delta)))
if __name__=='__main__':main()
