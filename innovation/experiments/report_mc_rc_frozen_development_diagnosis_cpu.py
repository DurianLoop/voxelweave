"""Report completed, independently checked training-set performance without new inference."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def f(value):return 'undefined' if value is None else f'{value:.6f}'
def main():
    sys.stdout.reconfigure(encoding='utf-8');folder=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02'
    rp=folder/'attempt_01.json';qp=folder/'independent_metrics_and_checkpoint_attempt_01.json';r,q=read(rp),read(qp)
    assert r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and q['result_sha256']==sha(rp)
    assert len(r['evaluations'])==len(q['evaluations'])==19 and q['checkpoint_replayed_planes']==57
    means=r['aggregate']['patient_first_means'];miss=[e for e in r['evaluations'] if e['metrics']['full']['tp']==0]
    empty=[e for e in r['evaluations'] if e['metrics']['full']['pred_foreground']==0]
    lines=['# 冻结全视野模型的全部训练内完整诊断','',
        f'11开发患者/19系列、原训练匹配PCHIP/observed_shared、固定20k最后权重与.5，完整原生FOV/全部z。full Dice {f(means["full"]["dice"])}、missing Dice {f(means["missing"]["dice"])}、full recall {f(means["full"]["recall"])}、full absRVE {f(means["full"]["absolute_relative_volume_error"])}。19系列中{len(miss)}个TP=0，{len(empty)}个预测全空；TP=0不能一概称空预测。','',
        '全部19独立label轴/逐plane计数/完整affine cKDTree物理距离与57完整plane重放通过；非正交且surface非空者另作分块cdist全双向距离核验。软件证据不等于独立患者确认，重放仍共享architecture。','',
        '每患者先等权平均系列，再11患者等权；不丢弃TP=0、小病灶或undefined。full precision因一个患者含空预测而整体undefined，不能只平均剩余10人冒充11人结果；tail GT空，recall/RVE保留undefined。','',
        '| 患者 | 系列 | full Dice | missing Dice | recall | absRVE |','|---|---:|---:|---:|---:|---:|']
    for patient,item in r['aggregate']['patients'].items():
        m=item['metrics'];lines.append(f'| {patient} | {item["series"]} | {f(m["full"]["dice"])} | {f(m["missing"]["dice"])} | {f(m["full"]["recall"])} | {f(m["full"]["absolute_relative_volume_error"])} |')
    lines+=['','| 系列（患者/UID） | full Dice | TP | FP | FN | ASSD mm | HD95 mm |','|---|---:|---:|---:|---:|---:|---:|']
    for e in r['evaluations']:
        m=e['metrics']['full'];s=e['metrics']['full_surface'];lines.append(f'| {e["patient"]}/{e["uid"]} | {f(m["dice"])} | {m["tp"]} | {m["fp"]} | {m["fn"]} | {f(s["assd_mm"])} | {f(s["hd95_mm"])} |')
    known=sum(r[k]+q[k] for k in ('global_forward_calls','local_forward_calls'))
    lines+=['','原attempt失败保留：session70121实际exit1，第四系列旧surface orthogonality断言失败。新完整affine模块没有放宽容差/删病例/改预测。仅前三个完整且SHA绑定预测复制重评分，第四孤立输出保留但重新推断；新attempt02 session16876实际exit0，独立核验session50711实际exit0。',
        f'新attempt02生产global/local前向{r["global_forward_calls"]}/{r["local_forward_calls"]}，独立重放{q["global_forward_calls"]}/{q["local_forward_calls"]}，两次已完整登记分支调用合计{known}。原失败attempt未写最终forward计数，不虚报本轮全部调用总数。无新训练更新/GPU/隐藏MR/确认效果。',
        '', '训练内低、此前四验证人full Dice .127522也低；现有模型不适合作重建评价器。两队列分数相近并不证明没有过拟合，也不定位单一失败因果。下一步先做同架构单012可拟合性与同预算loss配方对照；即使拟合通过，仍需整个开发集/四验证人能力、native控制和公平重建矩阵。',
        '', '相关：[原协议](MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_CPU_PROTOCOL_2026-10-03.md)、[affine失败修复](MC_RC_FROZEN_DEVELOPMENT_AFFINE_RESUME_PROTOCOL_2026-10-03.md)、[生产记录](experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02/attempt_01.json)、[独立核验](experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02/independent_metrics_and_checkpoint_attempt_01.json)、[下一loss协议](MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_PROTOCOL_2026-10-03.md)。没有可发表且独立确认的新claim，goal active。']
    out=ROOT/'MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_CPU_RESULT_2026-10-03.md';assert not out.exists();out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    provenance=folder/'report_provenance.json';assert not provenance.exists()
    provenance.write_text(json.dumps(dict(script_sha256=sha(__file__),report=out.relative_to(ROOT).as_posix(),report_sha256=sha(out),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (rp,qp)],
        complete_miss_series=len(miss),empty_prediction_series=len(empty),known_attempt02_and_verifier_model_branch_calls=known,
        original_failed_attempt_total_calls_known=False,scientific_confirmation_patients=0,publication_claim_confirmed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report=str(out),complete_miss_series=len(miss),empty_prediction_series=len(empty),known_model_branch_calls=known)))
if __name__=='__main__':main()
