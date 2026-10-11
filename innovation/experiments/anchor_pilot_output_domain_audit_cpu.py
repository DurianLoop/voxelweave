"""Audit all saved pilot comparisons in actual acquisition-index domains."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import csv,hashlib,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import nibabel as nib
from vs_seg_task_cpu_support import resource_gate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/anchor_pilot_output_domain_audit_cpu'
PILOT=ROOT/'experiments/anchor_bandwidth_task_cpu_pilot'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def overlap(p,r,m):
 a=p[m];b=r[m];tp=int(np.count_nonzero(a&b));fp=int(np.count_nonzero(a&~b));fn=int(np.count_nonzero(~a&b));den=2*tp+fp+fn
 return dict(tp=tp,fp=fp,fn=fn,dice=2*tp/den if den else None)
def main():
 sys.stdout.reconfigure(encoding='utf-8');gate=resource_gate();OUT.mkdir(exist_ok=False)
 r=read(PILOT/'attempt_01.json');proof=read(PILOT/'independent_inputs_and_all36_estimates.json');assert r['complete'] and proof['complete'] and not r['errors'] and not proof['errors'] and proof['result_sha256']==sha(PILOT/'attempt_01.json')
 conversion_path=ROOT/'experiments/vs_seg_full_volume_source_masks/attempt_02.json';conversion=read(conversion_path);cases={x['patient']:x for x in conversion['patients']};bindings={};xorrows=[];metricrows=[];patients=[]
 for patient in ('VS-SEG-202','VS-SEG-203','VS-SEG-204'):
  resource_gate();case=cases[patient];mp=ROOT/case['masks_file'];assert sha(mp)==case['masks_sha256'];bindings[case['masks_file']]=sha(mp)
  with np.load(mp) as masks:
   affine=masks['affine_ijk_ras'][:,[1,0,2,3]];refs={k:masks[v].astype(bool) for k,v in [('original_json','original_mask_rcz'),('rtstruct','rtstruct_mask_rcz')]}
  shape=refs['original_json'].shape;orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));inverse=nib.orientations.ornt_transform(nib.orientations.axcodes2ornt('RAS'),nib.orientations.io_orientation(affine));can_affine=affine@nib.orientations.inv_ornt_aff(orientation,shape)
  obs=list(range(0,shape[2],4));indices={'observed_anchors':obs,'supported_missing':[z for z in range(1,obs[-1]) if z%4],'unsupported_tail':list(range(obs[-1]+1,shape[2]))};domains={}
  for name,zs in indices.items():
   mask=np.zeros(shape,dtype=bool);mask[:,:,zs]=True;domains[name]=nib.orientations.apply_orientation(mask,orientation)
  assert np.all(sum(x.astype(np.uint8) for x in domains.values())==1)
  refs={k:nib.orientations.apply_orientation(v,orientation) for k,v in refs.items()};records={};predictions={}
  paths={'raw':ROOT/'experiments/vs_seg_full_volume_cohort/patients'/patient/'raw_pchip_attempt_01.json','post':ROOT/'experiments/vs_seg_post_resize_task_cpu'/f'{patient}.json'}
  paths.update({e['condition']:ROOT/e['file'] for e in r['patients'] if e['patient']==patient})
  metrics={}
  for condition,path in paths.items():
   x=read(path);assert x['complete'];pp=ROOT/x['prediction_file'];assert sha(pp)==x['prediction_sha256'];bindings[path.relative_to(ROOT).as_posix()]=sha(path);bindings[x['prediction_file']]=sha(pp)
   with np.load(pp) as saved:pred=saved['prediction_ras'].astype(bool);assert np.allclose(saved['affine'],can_affine,atol=1e-6,rtol=0)
   assert pred.shape==next(iter(refs.values())).shape;records[condition]=x;predictions[condition]=pred;metrics[condition]={}
   for ref,label in refs.items():
    metrics[condition][ref]={domain:overlap(pred,label,mask) for domain,mask in domains.items()}
    assert all(sum(m[k] for m in metrics[condition][ref].values())==x['task_metrics'][ref]['full'][k] for k in ('tp','fp','fn'))
  comparisons=list(dict.fromkeys(e['comparison'] for e in r['analysis']))
  for comparison in comparisons:
   left,right=comparison.split('-');changed=predictions[left]^predictions[right];native_changed=nib.orientations.apply_orientation(changed,inverse);assert native_changed.shape==shape
   total=0
   for domain,mask in domains.items():
    n=int(np.count_nonzero(changed&mask));perplane=sum(int(np.count_nonzero(native_changed[:,:,z])) for z in indices[domain]);assert n==perplane;total+=n
    xorrows.append(dict(patient=patient,comparison=comparison,domain=domain,domain_voxels=int(mask.sum()),changed_prediction_voxels=n,changed_fraction=n/int(mask.sum()) if mask.any() else None))
    for ref in refs:
     a=metrics[left][ref][domain];b=metrics[right][ref][domain]
     metricrows.append(dict(patient=patient,comparison=comparison,domain=domain,reference=ref,delta_tp=a['tp']-b['tp'],delta_fp=a['fp']-b['fp'],delta_fn=a['fn']-b['fn'],left_dice=a['dice'],right_dice=b['dice'],delta_dice=a['dice']-b['dice'] if a['dice'] is not None and b['dice'] is not None else None))
   assert total==int(np.count_nonzero(changed))
  patients.append(dict(patient=patient,full_confusion_partition_identity_verified=True,all18_xor_domain_counts_independently_replayed=True));print(json.dumps(dict(patient=patient,comparisons=6)),flush=True)
 outputs=[]
 for name,rows in [('all54_prediction_xor_domains.csv',xorrows),('all108_label_domain_task_differences.csv',metricrows)]:
  path=OUT/name
  with path.open('w',encoding='utf-8-sig',newline='') as stream:w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  outputs.append(path)
 selected=[x for x in xorrows if x['comparison']=='post_anchor_fixed-post' and x['domain']=='supported_missing']
 result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_PLAN_2026-10-03.md'),input_proof_sha256=sha(PILOT/'independent_inputs_and_all36_estimates.json'),conversion_manifest_sha256=sha(conversion_path),resource_gate=gate,complete=True,errors=[],patients=patients,prediction_pairs=18,xor_domain_counts_verified=54,label_domain_comparisons=108,source_bindings=[dict(path=k,sha256=v) for k,v in sorted(bindings.items())],selected_fixed_post_missing_output_changes=selected,posthoc=True,new_neural_forwards=0,torch_imported='torch' in sys.modules,scientific_confirmation_patients=0,publication_claim_confirmed=False)
 (OUT/'attempt_01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# 三人已保存预测：观测层、缺层和tail的实际响应','','这是完整pilot后的事后开发审计，没有新前向或MRI像素解码，torch未导入。18保存预测与三标签文件SHA核对；54个配对分区XOR计数以逆方向映射逐原生层复算，full混淆计数等于三个分区之和。两标签和原六比较全部保留。','','| 患者 | fixed post 缺层网络输入 | supported missing 预测变化体素 | 缺层域总量 |','| --- | --- | ---: | ---: |']
 for x in selected:lines.append(f"| {x['patient']} | 逐位相同（已有输入证明） | {x['changed_prediction_voxels']} | {x['domain_voxels']} |")
 lines += ['','完整体积Dice包含anchors，因此full差本身不足以定位缺层输出。上表直接核对实际missing预测，任何变化只能解释为当前完整任务推理链对仅anchors干预的响应；3D上下文、内部统计和滑窗等效应在这里未进一步拆开。未证明真实MRI解剖改变，也不支持已失败的带宽恢复主张。','','[54个XOR分区计数](experiments/anchor_pilot_output_domain_audit_cpu/all54_prediction_xor_domains.csv)、[108个两标签分区任务差](experiments/anchor_pilot_output_domain_audit_cpu/all108_label_domain_task_differences.csv)、[完整来源与身份记录](experiments/anchor_pilot_output_domain_audit_cpu/attempt_01.json)。supported missing与observed anchors指标不替代原full主结果；科学独立确认仍为0。']
 report=ROOT/'ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_RESULT_2026-10-03.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8');outputs.append(report)
 (OUT/'report_provenance.json').write_text(json.dumps(dict(script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),outputs=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in outputs]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(complete=True,errors=[],xor_domains=54,task_comparisons=108,selected=selected),ensure_ascii=False))
if __name__=='__main__':main()
