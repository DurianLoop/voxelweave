"""Make a descriptive report only after complete, hash-bound 16-source replay."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_native_competence_cpu'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');result=read(OUT/'attempt_01.json');contract=read(OUT/'run_contract.json');proof=read(OUT/'independent_native_model_and_roi_replay.json');queue=read(ROOT/'experiments/mc_rc_native_competence_queue/attempt_01.json')
 if not queue['complete'] or not result['complete'] or result['errors'] or proof['errors'] or len(result['series'])!=16: raise ValueError('Full single-attempt queue/result/proof not successful')
 if proof['result_sha256']!=sha(OUT/'attempt_01.json') or proof['run_contract_sha256']!=sha(OUT/'run_contract.json') or result['run_contract_sha256']!=sha(OUT/'run_contract.json') or proof['verification_script_sha256']!=sha(ROOT/'experiments/verify_mc_rc_native_competence_cpu.py'): raise ValueError('Bound replay lineage differs')
 for f in contract['files']:
  if sha(ROOT/f['path'])!=f['sha256']: raise ValueError('Frozen input changed: '+f['path'])
 rows=result['series'];by={r['uid']:r for r in rows}
 if set(by)!={r['uid'] for r in contract['cases']} or set(by)!={r['uid'] for r in proof['series']} or proof['counts']['fresh_neural_replays']!=17: raise ValueError('All sources or replay coverage differs')
 if sum(r['native_planes_decoded'] for r in rows)!=proof['counts']['raw_native_arrays_decoded'] or sum(r['missing_targets'] for r in rows)!=proof['counts']['missing_targets']: raise ValueError('Decode/target count differs')
 patients=sorted({r['patient'] for r in rows});summary=dict(created_utc=datetime.now(timezone.utc).isoformat(),series=16,patients=8,missing_targets=sum(r['missing_targets'] for r in rows),native_planes=sum(r['native_planes_decoded'] for r in rows),conditions={},patient_equal_missing_dice_native_minus_sparse=result['patient_equal_missing_dice_native_minus_sparse'],scientific_independent_validation_patients=0,publication_claim_confirmed=False,proof_counts=proof['counts'],files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (OUT/'attempt_01.json',OUT/'run_contract.json',OUT/'independent_native_model_and_roi_replay.json',Path(__file__))])
 for name in ('native','sparse'):
  summary['conditions'][name]=dict(patient_equal_dice={},zero_true_positive_full_series=sum(r['task_competence'][name]['full']['true_positive_voxels']==0 for r in rows),empty_full_predictions=sum(r['task_competence'][name]['full']['predicted_voxels']==0 for r in rows),roi_gate_passed_series=sum(r['roi'][name+'_anchor_union_2mm']['gate_passed'] for r in rows),roi_metrics_range={})
  for region in ('full','observed','missing'):
   means=[sum(r['task_competence'][name][region]['dice'] for r in rows if r['patient']==p)/sum(r['patient']==p for r in rows) for p in patients];summary['conditions'][name]['patient_equal_dice'][region]=sum(means)/len(means)
  for metric in ('foreground_recall','boundary_recall','tile_foreground_recall','roi_fraction','tile_fraction'):
   values=[r['roi'][name+'_anchor_union_2mm']['metrics'][metric] for r in rows];summary['conditions'][name]['roi_metrics_range'][metric]=[min(values),max(values)]
 delta=summary['conditions']['native']['patient_equal_dice']['missing']-summary['conditions']['sparse']['patient_equal_dice']['missing']
 if abs(delta-result['patient_equal_missing_dice_native_minus_sparse'])>1e-12: raise ValueError('Descriptive patient endpoint differs')
 omitted=[r for r in rows if not r['in_old_frozen_15']]
 if len(omitted)!=1: raise ValueError('Omitted-source coverage differs')
 summary['omitted_source']=dict(patient=omitted[0]['patient'],uid=omitted[0]['uid'],missing_targets=omitted[0]['missing_targets'],ideal_anchor_union_2mm=omitted[0]['ideal_anchor_union_2mm']['metrics'],ideal_gate_passed=omitted[0]['ideal_anchor_union_2mm']['gate_passed'])
 lines=['# 16 系列完整 native 能力对照：全量独立重放结果','',f"固定 16 系列/8 开发患者、{summary['missing_targets']} 内部缺层全部完成，errors=[]。全体 {summary['native_planes']} 原 native MR planes 独立解码，16 次 native 与 1 次遗漏系列 sparse CPU 新前向全部逐位相同；原 label、坐标、physical disk 区域计数和患者汇总独立重算通过。实现重放不增加科学独立确认患者，当前仍为 0。",'',f"预写描述性主端点为患者内系列等权、再 8 患者等权的缺层 Dice(native)−Dice(sparse)：**{delta:+.9f}**。这是固定冻结模型及预处理在当前开发来源的能力对照，不是新 SR 方法优势、真实 slice-profile 因果或临床安全结论。",'','[事前合同](MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md)、[完整结果](experiments/mc_rc_native_competence_cpu/attempt_01.json)、[原输入哈希](experiments/mc_rc_native_competence_cpu/run_contract.json)、[独立模型/区域重放](experiments/mc_rc_native_competence_cpu/independent_native_model_and_roi_replay.json)、[描述性汇总](experiments/mc_rc_native_competence_cpu/descriptive_summary.json)。','','| 输入 | 全体积 Dice† | 观测层 Dice† | 内部缺层 Dice† | 全体积零 TP | 全空预测 | 主 ROI 过门槛 |','| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
 for name in ('native','sparse'):
  c=summary['conditions'][name];d=c['patient_equal_dice'];lines.append(f"| {name} | {d['full']:.9f} | {d['observed']:.9f} | {d['missing']:.9f} | {c['zero_true_positive_full_series']}/16 | {c['empty_full_predictions']}/16 | {c['roi_gate_passed_series']}/16 |")
 lines+=['','†均为患者内系列等权再患者等权；每系列 Dice 由指定区域完整体素 TP/预测/人工真值计数计算，不逐缺层等权。full 含 unsupported tail；missing 仅两真实 anchors 间的内部缺层。所有真值为官方 label，native 自动分割不是真值。','','| 患者 | 系列数 | native 缺层 Dice | sparse 缺层 Dice | native−sparse |','| --- | ---: | ---: | ---: | ---: |']
 for p in result['patients']: lines.append(f"| {p['patient']} | {p['series']} | {p['series_equal_missing_dice']['native']:.9f} | {p['series_equal_missing_dice']['sparse']:.9f} | {p['series_equal_missing_dice_native_minus_sparse']:+.9f} |")
 lines+=['','| 患者 / 系列末 8 位 | 描述 | native full / observed / missing Dice | sparse full / observed / missing Dice | native ROI 前景 / 边界覆盖 | sparse ROI 前景 / 边界覆盖 |','| --- | --- | --- | --- | --- | --- |']
 for r in rows:
  vals=[' / '.join(f"{r['task_competence'][name][reg]['dice']:.6f}" for reg in ('full','observed','missing')) for name in ('native','sparse')];roi=[' / '.join(f"{r['roi'][name+'_anchor_union_2mm']['metrics'][reg]:.6f}" for reg in ('foreground_recall','boundary_recall')) for name in ('native','sparse')];lines.append(f"| {r['patient']} / {r['uid'][-8:]}{'（补遗漏）' if not r['in_old_frozen_15'] else ''} | {r['description'].replace('|','/')} | {vals[0]} | {vals[1]} | {roi[0]} | {roi[1]} |")
 lines+=['','| ROI 指标范围（全 16 系列） | native | sparse |','| --- | --- | --- |']
 for m in ('foreground_recall','boundary_recall','tile_foreground_recall','roi_fraction','tile_fraction'):
  vals=['–'.join(f'{x:.9f}' for x in summary['conditions'][name]['roi_metrics_range'][m]) for name in ('native','sparse')];lines.append(f'| {m} | {vals[0]} | {vals[1]} |')
 o=summary['omitted_source'];lines+=['',f"遗漏 002 第二时点单独补了 {o['missing_targets']} 缺层及理想真实 anchor 区域：gate={o['ideal_gate_passed']}，foreground={o['ideal_anchor_union_2mm']['foreground_recall']:.9f}，boundary={o['ideal_anchor_union_2mm']['boundary_recall']:.9f}。它仍属于旧开发患者；历史 15 合同和结果保留，本报告使用来源更正后的完整 16 分母。",'','全量保留逐系列 native/sparse 失败及收益、完整 recall/precision 和每缺层 ROI 成本（见机器结果）。native 需要完整扫描，仅允许用于此指定参考对照，不能作为真实稀疏路线的输入。完整 native 仍出现定位失败时，稀疏失败无法全部归于抽层；相反方向的系列差异也不能单独识别协议、厚度、spacing 或域偏移的因果。','', '固定 checkpoint / raw-PCHIP / anchor-union+2 mm 的失败维持停止，不调整 crop、半径、阈值或 checkpoint 救回旧主结果。下一表征需要独立新合同、保持完整开发患者分母、同容量及面积预算对照，随后另找真正未用于设计的患者确认。当前没有可发表新方法 claim。','', '本报告只在全量独立 proof 生成之后写入；原 VS-SEG 队列的完成与本试验分开判断。GPU 未使用，用户训练未操作，locked IXI test 未读取。']
 with (OUT/'descriptive_summary.json').open('x',encoding='utf-8') as f: json.dump(summary,f,ensure_ascii=False,indent=2)
 with (ROOT/'MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md').open('x',encoding='utf-8') as f: f.write('\n'.join(lines)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
