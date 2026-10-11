"""Descriptive development report after all-source QDA/LDA replay."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_anchor_qda_cpu'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');r=read(OUT/'attempt_01.json');p=read(OUT/'independent_anchor_qda_replay.json');q=read(ROOT/'experiments/mc_rc_anchor_qda_queue/attempt_01.json');c=read(OUT/'run_contract.json')
 if not q['complete'] or not r['complete'] or r['errors'] or p['errors'] or p['counts']['series']!=16 or p['counts']['patients']!=8: raise ValueError('Complete all16/eightfold successful replay required')
 if p['result_sha256']!=sha(OUT/'attempt_01.json') or p['run_contract_sha256']!=sha(OUT/'run_contract.json') or p['verification_script_sha256']!=sha(ROOT/'experiments/verify_mc_rc_anchor_qda_cpu.py'): raise ValueError('Replay lineage differs')
 for f in c['files']:
  if sha(ROOT/f['path'])!=f['sha256']: raise ValueError('Frozen file mutated '+f['path'])
 rows=r['series'];methods=c['methods'];thresholds={'foreground_recall':(.99,'min'),'boundary_recall':(.99,'min'),'tile_foreground_recall':(.995,'min'),'roi_fraction':(.05,'max'),'tile_fraction':(.10,'max')};summary=dict(created_utc=datetime.now(timezone.utc).isoformat(),counts=p['counts'],methods={},primary='joint_QDA',scientific_independent_validation_patients=0,publication_claim_confirmed=False,files=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in (OUT/'attempt_01.json',OUT/'run_contract.json',OUT/'independent_anchor_qda_replay.json',Path(__file__))])
 lines=['# 真实观测层 QDA/LDA：全量开发诊断与复核结果','',f"全部16系列/8开发患者、{p['counts']['missing_targets']}缺层完成，四个模型、8个完整患者留出全部保存。原 MR只解码observed anchors；训练label也只读observed planes。独立逆映射/中心矩/完整患者剔除再拟合/Cholesky分类与physical-disk缺层计数复核errors=[]。共有{p['counts']['fresh_anchor_classifications']}个anchor-plane/model重新分类；特征提取及SciPy滤波实现明确复用。",'', '这是已用8人的开发泛化诊断；它不增加科学独立患者。QDA/LDA、多尺度局部外观和坐标先验不是新颖方法，没有生成缺层MRI或证明新SR收益。','', '[预写合同](MC_RC_ANCHOR_QDA_CPU_PLAN_2026-10-03.md)、[全量结果](experiments/mc_rc_anchor_qda_cpu/attempt_01.json)、[输入合同](experiments/mc_rc_anchor_qda_cpu/run_contract.json)、[独立重放](experiments/mc_rc_anchor_qda_cpu/independent_anchor_qda_replay.json)、[合成preflight](experiments/mc_rc_anchor_qda_preflight/attempt_01.json)、[汇总](experiments/mc_rc_anchor_qda_cpu/descriptive_summary.json)。','','| 模型 | 主区域过门槛 | 患者等权观测Dice | 前景覆盖范围 | 边界覆盖范围 | ROI面积范围 | tile面积范围 |','| --- | ---: | ---: | --- | --- | --- | --- |']
 for method in methods:
  d=r['summary'][method].copy();d['metric_ranges']={m:[min(x['methods'][method]['roi']['metrics'][m] for x in rows),max(x['methods'][method]['roi']['metrics'][m] for x in rows)] for m in thresholds};d['failed_by_endpoint']={m:sum(x['methods'][method]['roi']['metrics'][m]<value if direction=='min' else x['methods'][method]['roi']['metrics'][m]>value for x in rows) for m,(value,direction) in thresholds.items()};d['empty_observed_predictions']=sum(x['methods'][method]['observed_task']['predicted_voxels']==0 for x in rows);summary['methods'][method]=d;ranges=['–'.join(f'{v:.6f}' for v in d['metric_ranges'][m]) for m in ('foreground_recall','boundary_recall','roi_fraction','tile_fraction')];lines.append(f"| {method}{'（唯一主模型）' if method=='joint_QDA' else ''} | {d['roi_gate_passed']}/16 | {d['patient_equal_observed_dice']:.9f} | {' | '.join(ranges)} |")
 lines+=['','所有范围含失败系列；观察Dice按患者内系列等权再8患者等权，非逐plane均值。解释对照特征数不同，不称严格同容量，不按结果把某对照改成主模型。','','| 主模型端点 | 失败系列数 |','| --- | ---: |']
 for m,count in summary['methods']['joint_QDA']['failed_by_endpoint'].items(): lines.append(f'| {m} | {count}/16 |')
 lines+=['','| 患者 / 系列末8位 | 观测Dice | 前景覆盖 | 边界覆盖 | ROI面积 | tile面积 | 总门槛 |','| --- | ---: | ---: | ---: | ---: | ---: | --- |']
 for row in rows:
  d=row['methods']['joint_QDA'];m=d['roi']['metrics'];lines.append(f"| {row['patient']} / {row['uid'][-8:]} | {d['observed_task']['dice']:.6f} | {m['foreground_recall']:.6f} | {m['boundary_recall']:.6f} | {m['roi_fraction']:.6f} | {m['tile_fraction']:.6f} | {'通过' if d['roi']['gate_passed'] else '失败'} |")
 passed=summary['methods']['joint_QDA']['roi_gate_passed'];lines+=['',f'主joint_QDA为{passed}/16，未达到预写全16系列门槛。固定prior/shrinkage/threshold/2mm/特征配置保持失败，不按这批结果调参救回；不能由一个轻量Gaussian分类器失败推出所有学习表示不可能。' if passed<16 else '主joint_QDA达到开发几何门槛；它仍没有完整缺层SR收益、强动作风险对照或新患者确认，不是可发表方法结果。','', '留出患者全部系列在本fold训练membership中剔除；其观察label在其他fold是合法训练监督，但不进自己的参数、特征或决策。真实label只有在预测保存后用于缺层评分。所有model与class矩可从机器结果及fold文件复查。没有scikit-learn安装或环境变动，没有使用GPU或操作用户训练，locked IXI test未读。', '', '下一步先保留固定VS-SEG完整主队列的结果边界，再考虑新任务表示或来源：必须另冻训练/校准/确认患者，明确可观察输入和同容量动作对照，先验证可用信息能认出局部冲突，再验证完整缺层收益。稀疏人工标注及轮廓传播的直接先例见[三篇正文核读](literature/2026-10-03_anchor_representation_fulltext_reading.md)。']
 with (OUT/'descriptive_summary.json').open('x',encoding='utf-8') as f: json.dump(summary,f,ensure_ascii=False,indent=2)
 with (ROOT/'MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md').open('x',encoding='utf-8') as f: f.write('\n'.join(lines)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': raise SystemExit(main())
