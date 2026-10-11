"""Export every pilot endpoint and acquisition-domain count with report provenance."""
import csv,json,math
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_full_volume_runtime import ROOT,sha
OUT=ROOT/'experiments/task_stats_swap_cpu_pilot'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def csvwrite(path,rows):
    with path.open('x',encoding='utf-8',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    r=read(OUT/'attempt_01.json');q=read(OUT/'independent_inputs_domains_and_all30_estimates.json')
    assert r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and q['result_sha256']==sha(OUT/'attempt_01.json')
    endpoint_rows=[];patient_rows=[]
    for x in r['analysis']:
        endpoint_rows.append({k:x[k] for k in ('reference','domain','comparison','original_denominator','defined_n','mean')}|{'undefined_patients':','.join(x['undefined_patients'])})
        for p in x['patient_differences']:patient_rows.append({k:x[k] for k in ('reference','domain','comparison')}|p)
    assert len(endpoint_rows)==30 and len(patient_rows)==90
    paths=[]
    for name,rows in [('all30_endpoints.csv',endpoint_rows),('all90_patient_differences.csv',patient_rows)]:
        p=OUT/name;csvwrite(p,rows);paths.append(p)
    conditions={}
    for e in r['patients']:
        x=read(ROOT/e['file']);conditions.setdefault(x['patient'],{})[x['condition']]=x
        for name,v in x['diagonals'].items():conditions[x['patient']][name+'_'+name+'stats']=v
    counts=[];differences=[]
    for patient,cells in conditions.items():
        for name,x in cells.items():
            for ref,domains in x['domain_confusion'].items():
                for domain,m in domains.items():counts.append(dict(patient=patient,condition=name,reference=ref,domain=domain,**m))
        for ref in ('original_json','rtstruct'):
            for domain in ('observed_anchors','supported_missing','unsupported_tail'):
                for comp in [x['comparison'] for x in r['analysis'][:5]]:
                    dice={k:v['domain_confusion'][ref][domain]['dice'] for k,v in cells.items()}
                    if comp=='normalization_image_interaction':delta=(dice['post_poststats']-dice['post_rawstats'])-(dice['raw_poststats']-dice['raw_rawstats']) if all(v is not None for v in dice.values()) else None
                    else:left,right=comp.split('-');delta=dice[left]-dice[right] if dice[left] is not None and dice[right] is not None else None
                    differences.append(dict(patient=patient,reference=ref,domain=domain,comparison=comp,difference=delta,defined=delta is not None))
    assert len(counts)==72 and len(differences)==90
    for name,rows in [('all72_acquisition_domain_counts.csv',counts),('all90_acquisition_domain_differences.csv',differences)]:
        p=OUT/name;csvwrite(p,rows);paths.append(p)
    report=ROOT/'TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md'
    lines=['# 固定三人raw/post统计互换：CPU结果','',
           '全部6次交叉CPU前向已完成；两条原对角条件复用既有核验预测。最终独立复核通过6交叉输入重放、6对角输入SHA、72采集域confusion单元、30配对端点及6保存预测核验。没有GPU调用、新训练或科学独立确认。',
           '', '这三人是原固定技术预检名单202/203/204。其原post−raw JSON full均值为+.033359793753，与全45人的−.09175350相反；RT同样三人+.035143371676而全45为负。不能用三人结果解释全45损失、声称恢复或计算唯一归因百分比。','',
           '| 原JSON full比较 | 三人平均ΔDice |','| --- | ---: |']
    for x in r['analysis']:
        if x['reference']=='original_json' and x['domain']=='full':lines.append(f"| {x['comparison']} | {x['mean']:+.12f} |")
    lines+=['','主比较post_rawstats−post_poststats逐人JSON full：202 −.000768344059、203 +.002298443881、204 +.002700872208；RT平均+.001523343559。效应小且包含反例。固定图片换统计仍改变网络的整个输入，不能据ΔDice把它叫解剖恢复。','',
            '所有两标签×full/slab/去1mm带×5比较均保存，无筛选、bootstrap或显著性声明。full与slab在这三人可能相同，不得据此省略采集域。以下采集域由原始z索引建立后映射至RAS，区别于包含anchors的slab；unsupported tail保留undefined，不填0。','',
            '| 采集域，主比较post_rawstats−post_poststats | JSON三人均值（定义n） | RT三人均值（定义n） |','| --- | ---: | ---: |']
    for domain in ('observed_anchors','supported_missing','unsupported_tail'):
        vals={ref:[x['difference'] for x in differences if x['reference']==ref and x['domain']==domain and x['comparison']=='post_rawstats-post_poststats' and x['defined']] for ref in ('original_json','rtstruct')}
        def fmt(v):return f'{math.fsum(v)/len(v):+.12f} ({len(v)})' if v else 'undefined (0)'
        lines.append(f"| {domain} | {fmt(vals['original_json'])} | {fmt(vals['rtstruct'])} |")
    lines+=['','[全部30端点](experiments/task_stats_swap_cpu_pilot/all30_endpoints.csv)、[90逐人配对差](experiments/task_stats_swap_cpu_pilot/all90_patient_differences.csv)、[72采集域计数](experiments/task_stats_swap_cpu_pilot/all72_acquisition_domain_counts.csv)、[90采集域配对差](experiments/task_stats_swap_cpu_pilot/all90_acquisition_domain_differences.csv)、[输入与端点独立复核](experiments/task_stats_swap_cpu_pilot/independent_inputs_domains_and_all30_estimates.json)。','',
            '解析的difference-in-differences是预列交互项；两条统计/图像路径不同意味着不能提出自然唯一的归因比例。网络、患者与标签均来自已见开发条件，复核独立性限于NumPy输入重放与Fraction计数运算，不能替代新模型/患者科学确认。结合[三篇直接先例](literature/2026-10-03_masked_normalization_primary_reading.md)，anchor-only统计保留为控制，当前不作为独立创新或扩大原失败恢复干预的证据。']
    assert not report.exists();report.write_text('\n'.join(lines)+'\n',encoding='utf-8');paths.append(report)
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),independent_proof_sha256=sha(OUT/'independent_inputs_domains_and_all30_estimates.json'),outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths])
    (OUT/'report_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(endpoints=30,patient_differences=90,acquisition_counts=72,acquisition_differences=90,outputs=len(paths))))
if __name__=='__main__':main()
