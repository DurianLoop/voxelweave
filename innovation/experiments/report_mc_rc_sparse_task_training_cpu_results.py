"""Render completed pilot and single-case counterexample with provenance, no rerun."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
from mc_rc_observed_only_training_input import ROOT,read,sha
def main():
    sys.stdout.reconfigure(encoding='utf-8');pp=ROOT/'experiments/mc_rc_sparse_task_training_cpu_pilot/attempt_01.json';p=read(pp);pq=read(pp.parent/'independent_metrics_and_checkpoint_attempt_01.json');fp=ROOT/'experiments/mc_rc_single_developer_fit_diagnostic_cpu/attempt_01.json';f=read(fp);fq=read(fp.parent/'independent_metrics_and_checkpoint_attempt_01.json');assert all(x['complete'] and not x['errors'] for x in (p,pq,f,fq));assert not p['capability_gate_passed'] and not f['fit_gate_passed']
    rows=[]
    for e in p['evaluations']+f['evaluations']:
        m=e['metrics'];s=m['full_surface'];role='单病例训练内' if e['development_role']=='single_case_training_fit_only' else ('多患者训练内' if e['patient'].endswith('012') else '开发内部留人')
        rows.append('| %s | %s | %s | %.6f | %.6f | %.6f | %.3f%% | %.3f | %.3f |'%(role,e['patient'],e['method'],m['full']['dice'],m['missing']['dice'],m['full']['recall'],m['full']['absolute_relative_volume_error']*100,s['assd_mm'],s['hd95_mm']))
    text='''# CPU任务训练：完整执行、能力失败与单病例可拟合性诊断

本轮首次从随机初始化训练当前MC-RC开发来源的任务网络。两次固定4000步训练及全部预测/复核均实际exit0，但预写科学能力门槛均未通过。不是训练出错被跳过，也不能把弱网络上的linear/PCHIP差异当重建优劣。

主pilot使用10开发患者18系列，013整人排除训练；012训练内与013留人检查各评raw PCHIP/raw linear，五层2.5D U-Net只有122,609参数。单病例诊断重新初始化相同架构/初权重，仅训练012唯一系列，仍4000步，最终只评012。两个模型都只使用observed MR生成稀疏输入，未加载作者权重，未解码隐藏MR、未打开4验证/8确认患者。阈值.5、最后checkpoint、全FOV规则tile固定；不按结果增加预算或换患者。

| 实验身份 | 患者 | 输入 | full Dice | supported missing Dice | full recall | full绝对体积误差 | ASSD mm | HD95 mm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
'''+ '\n'.join(rows)+'''

主pilot主输入两例均未过full Dice≥.70/missing≥.65/recall≥.70/绝对体积误差≤.50的预写门槛。012原生GT193,433体素，013仅567体素；大小差异不等于病理分类差异，官方MC-RC释义是Multi-Center Routine Clinical，发布二值VS标签，不是“resection cavity”的缩写。source资格此前已经通过，不能因效果坏换掉这两人。

主pilot患者均匀采样实际每人376–436updates（总4000），012仅376步；最后100步平均BCE+Dice loss .991259。训练后固定模型在012的50个前景patch（均有GT）micro Dice .030755；50个全FOV均匀patch中46个GT为空，micro Dice0。此为事后诊断，无optimizer或阈值选择，说明坏结果不只是规则tile遗漏覆盖；不证明某个架构因素或域偏移的因果解释。

单病例训练的最后100步平均loss .329622，full Dice .555150、missing .557284。其绝对体积误差只有1.3602%，但full recall .551374、ASSD18.299mm、HD9554.773mm，仍有84,148个FP和86,779个FN。**体积接近真值不能说明病灶位置/边界可靠**；这是一个训练内失败诊断例，不能外推临床或宣称新的规律。预写单病例fit门槛full/missing/recall≥.90未过，该配置没有充分可拟合性证据。

生产结果分别见 [多患者pilot](experiments/mc_rc_sparse_task_training_cpu_pilot/attempt_01.json)、[单病例诊断](experiments/mc_rc_single_developer_fit_diagnostic_cpu/attempt_01.json)，原始协议分别见 [pilot协议](MC_RC_SPARSE_TASK_TRAINING_CPU_PILOT_PLAN_2026-10-03.md)、[诊断协议](MC_RC_SINGLE_DEVELOPER_FIT_DIAGNOSTIC_PLAN_2026-10-03.md)。日志记录每100步loss/lr/预算，checkpoint保存训练身份、协议和初/终权重SHA；初权重SHA两次相同，训练身份已知。主训练实测137.651s、单病例138.720s，均CPU单线程、自身below-normal，GPU未初始化。

[主独立复核](experiments/mc_rc_sparse_task_training_cpu_pilot/independent_metrics_and_checkpoint_attempt_01.json)用逐slice编码bincount重算全部4条件的full/anchors/missing/tail指标，源NIfTI以独立transpose/flip重读；物理surface用显式6邻域+cKDTree，与生产EDT结果在.0001mm内一致。规则tile独立枚举/提取、最后checkpoint12个完整plane重放逐位一致；013训练18UID/10patient排除通过。[单病例复核](experiments/mc_rc_single_developer_fit_diagnostic_cpu/independent_metrics_and_checkpoint_attempt_01.json)相同独立计数/物理算法及3完整plane通过。复核模型仍引用生产architecture，单病例复核复用独立指标实现，不能称完全独立训练或第二评价器。

[开发全FOV叠图](figures/mc_rc_sparse_task_cpu_pilot/development_full_FOV_overlay.png)与[loss图](figures/mc_rc_sparse_task_cpu_pilot/training_loss.png)已生成并目视检查。叠图使用稀疏PCHIP；cyan是参考VS、red是预测，可见远离目标的散在预测。显示切面按GT最大面积事后选定，仅用于QC，未进入推断或指标ROI；不能把两张切面当所有病例临床影像审查。

本轮两次训练8000真实updates，另10步合成tensor预检；生产/复核总13,779次网络forward调用（batch调用，不是独立患者数），GPU0、科学确认0，publication claim未达到。原6×5矩阵、native能力、4验证能力及8冻结确认均未执行。本配置停止作为任务评价器；不据弱网络宣称SR有益、有害或适应后差距消失。下一步先验证更充分预算/更大物理上下文的任务基线，再启用公平矩阵；新容量/预算必须同时用于所有对照。
'''
    report=ROOT/'MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md';assert not report.exists();report.write_text(text,encoding='utf-8')
    files=[pp,pp.parent/'independent_metrics_and_checkpoint_attempt_01.json',fp,fp.parent/'independent_metrics_and_checkpoint_attempt_01.json'];r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in files],complete=True,new_training_updates=8000,new_neural_forward_calls=sum(x['neural_forward_calls'] for x in (p,pq,f,fq)),scientific_confirmation_patients=0,publication_claim_confirmed=False)
    assert r['new_neural_forward_calls']==13779;(pp.parent/'report_provenance.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':main()
