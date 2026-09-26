from pathlib import Path
import json,datetime
P=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    for m in ['linear','acvtt','resunet','smamba_unet','arssr']:
        for ds,expected in [('fastmri',72),('ixi',345)]:
            completed=len(list((P/'outputs/responses').glob(f'{ds}_{m}_*.json')))
            f=P/f'outputs/validation_{ds}_{m}.json';v=json.loads(f.read_text())['status'] if f.exists() else 'NOT RUN'
            repaired=P/f'outputs/validation_batch1_{ds}_{m}.json'
            if repaired.exists():v=json.loads(repaired.read_text())['status']+' (batch1; batch4 record retained)'
            elif (P/'batch_repair_freeze.json').exists() and (ds,m) in [('ixi','acvtt'),('fastmri','resunet'),('ixi','resunet')]:v='BATCH4 FAIL; BATCH1 PENDING'
            analyzed=(P/f'outputs/summary_{ds}_{m}.json').exists()
            rows.append(dict(model=m,dataset=ds,completed_targets=completed,expected_targets=expected,interface_check=v,analysis_complete=analyzed))
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,all_response_targets_complete=sum(r['completed_targets'] for r in rows),planned_response_targets=2085)
    (P/'RUNNING_STATUS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=['# Continuous influence 扩展：执行状态','',f'更新时间 UTC：{result["utc"]}。新响应目标 {result["all_response_targets_complete"]}/2085。每个目标含全部九上下文、四幅度、双锚和四随机场。',
           '','| 模型 | 队列 | 已完成/计划目标 | 接口检查 | 统计完成 |','|---|---|---|---|---|']
    for r in rows:lines.append(f'| {r["model"]} | {r["dataset"]} | {r["completed_targets"]}/{r["expected_targets"]} | {r["interface_check"]} | {r["analysis_complete"]} |')
    lines +=['','所有模型/队列完成或明确技术失败后，才构建新的八模型同时区间与最终大表。正在计算中的模型不能写成 NA、失败或成功。',
              '','原始响应：outputs/responses；运行日志：logs/linear_run.log、logs/neural_run.log；分析日志：logs/analysis.log。',
              '','此文件仅记录实验执行进度；论文入口是否安装、PDF 是否重建及视觉检查是否完成，以 DELIVERY_STATUS.json 为准。']
    (P/'RUNNING_STATUS.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
