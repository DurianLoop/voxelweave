"""Write all fixed-fit outcomes and a scientific figure after certified completion."""
import hashlib,json,os,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
FIT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'
FIG=ROOT/'figures/mc_rc_3d_cpu_fixed_fit_2026_10_07'
REPORT=ROOT/'MC_RC_3D_CPU_FIXED_FIT_RESULT_2026-10-07.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def value(x):return 'undefined' if x is None else f'{x:.6f}' if isinstance(x,float) else str(x)
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not REPORT.exists();FIG.mkdir(exist_ok=False)
    prod=json.loads((FIT/'attempt_01.json').read_text(encoding='utf-8'))
    proof=json.loads((FIT/'independent_both512_and_full_fov_2026_10_07.json').read_text(encoding='utf-8'))
    diagfile=ROOT/'experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07/attempt01.json'
    diag=json.loads(diagfile.read_text(encoding='utf-8'))
    assert prod['complete'] and proof['complete'] and diag['complete'] and not (prod['errors']+proof['errors']+diag['errors'])
    assert proof['result_sha256']==diag['fit_result_sha256']==sha(FIT/'attempt_01.json')
    lines=['# 两臂512更新CPU拟合：完整实际结果','',
           '两臂各512更新已完成，共1024更新；独立checkpoint/完整FOV重放与四变体patch诊断均已执行。',
           '只训练同一个开发系列001，不能作为19series充分训练、四验证能力或重建创新确认。GPU更新0，八确认未开，科学确认0。',
           '', '| 输入 | foreground训练patch Dice | 完整训练FOV Dice | recall | absRVE | TP | 拟合gate | 更新耗时(秒) |',
           '|---|---:|---:|---:|---:|---:|---|---:|']
    for arm in prod['arms']:
        m=arm['metrics']['full']
        lines.append('| '+' | '.join([arm['kind'],value(arm['patch_metrics'][0]['dice']),value(m['dice']),value(m['recall']),
                                     value(m['absRVE']),value(m['tp']),str(arm['training_fit_gate_passed']),value(arm['training_elapsed_seconds'])])+' |')
    lines+=['','## 所有域及空/undefined','',
            '| 输入/域 | Dice | recall | precision | absRVE | TP | FP | FN | TN | GT前景 | 预测前景 | GT空 | 预测空 |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|']
    for arm in prod['arms']:
        for name,m in arm['metrics'].items():
            keys=['dice','recall','precision','absRVE','tp','fp','fn','tn','gt_foreground','pred_foreground','empty_ground_truth','empty_prediction']
            lines.append('| '+arm['kind']+'/'+name+' | '+' | '.join(value(m[k]) for k in keys)+' |')
    lines+=['','## 预定的四个crop变体（不是四种完整体积效果）','',
            '| 输入/变体 | foreground crop主head hard-Dice | 主head batch soft-Dice | 主head前景平均概率 | 主head背景平均概率 | 三head加权loss |',
            '|---|---:|---:|---:|---:|---:|']
    for arm in diag['arms']:
        for d in arm['variants']:
            h=d['heads'][0]
            lines.append('| '+arm['kind']+'/'+d['variant']+' | '+' | '.join(value(v) for v in [h['hard_metrics'][0]['dice'],h['soft_dice'],
                         h['foreground_probability']['mean'],h['background_probability']['mean'],d['combined_loss']])+' |')
    lines+=['','完整逐head数量、概率及梯度核对见诊断JSON。4变体均报告，没有挑最优变体或改变阈值。',
            'logit梯度是当前输出上的局部描述，不是模型参数梯度冲突、优化因果证明或新的训练方法。',
            '', '## 独立实现核验','']
    for arm in proof['arms']:
        lines.append(f"- {arm['kind']}：512条更新/LR记录及checkpoint来源已核；{arm['full_native_voxels_replayed']}完整native voxel重放，概率最大绝对误差{arm['probability_max_absolute_error']:.9g}，阈值预测差异{arm['prediction_disagreements']}；{arm['total_tiles']}tiles、全部四域计数和拟合gate核对。")
    lines+=['','功能重放器是独立实现核验，不是第二独立训练任务网络。CPU结果不自动通过GPU显存/数值/速度资格。',
            '门槛失败保留，不减少分母、不改阈值/最后权重、不把弱任务能力改写成SR损害病灶。',
            '', '[训练记录](experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json)、[独立重放](experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/independent_both512_and_full_fov_2026_10_07.json)、[四变体诊断](experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07/attempt01.json)。']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    os.environ['MPLCONFIGDIR']=str(FIG/'mplconfig')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    colors=['#176c9c','#b46623'];labels=['Native reference','Raw PCHIP']
    fig,axes=plt.subplots(1,3,figsize=(12.5,4.2),layout='constrained')
    for i,a in enumerate(prod['arms']):
        axes[0].plot([h['update'] for h in a['every_update_history']],[h['loss'] for h in a['every_update_history']],
                     color=colors[i],label=labels[i],linewidth=1.5)
    axes[0].set_xlabel('Update');axes[0].set_ylabel('Deep-supervision BCE + Dice loss')
    axes[0].set_title('Fixed augmented batch; last checkpoint');axes[0].legend(frameon=False,fontsize=9)
    xpos=np.arange(4);names=['Training crop Dice','Full FOV Dice','Full FOV recall','Full FOV absRVE']
    gate=[.9,.9,.9,.25]
    for i,a in enumerate(prod['arms']):
        m=a['metrics']['full'];vals=[a['patch_metrics'][0]['dice'],m['dice'],m['recall'],m['absRVE']]
        for j,v in enumerate(vals):
            if v is None:axes[1].text(j+(i-.5)*.28,.02,'NA',ha='center',fontsize=8)
            else:axes[1].bar(j+(i-.5)*.28,v,width=.25,color=colors[i])
    for j,g in enumerate(gate):axes[1].plot([j-.34,j+.34],[g,g],color='#444444',linestyle='--',linewidth=1)
    axes[1].set_xticks(xpos,names,rotation=40,ha='right');axes[1].set_title('Complete training volume fit gates')
    axes[1].set_ylabel('Metric value (dashed: fixed gate)')
    for i,a in enumerate(diag['arms']):
        y=[d['heads'][0]['hard_metrics'][0]['dice'] for d in a['variants']]
        axes[2].plot(np.arange(4),[np.nan if v is None else v for v in y],marker='o',color=colors[i],label=labels[i])
    axes[2].set_xticks(np.arange(4),['Training aug.','Flips only','Intensity only','Identity'],rotation=40,ha='right')
    axes[2].set_ylim(-.03,1.03);axes[2].set_ylabel('Foreground crop hard-Dice');axes[2].set_title('Frozen four-variant crop diagnostics')
    fig.suptitle('One development series, two CPU fits, 512 updates each',fontsize=13)
    fig.supxlabel('Training diagnostics; no held-out task qualification or reconstruction claim',fontsize=9)
    files=[]
    for ext in ('png','svg'):
        p=FIG/('fixed_fit_results.'+ext);fig.savefig(p,dpi=180);files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    plt.close(fig)
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                script_sha256=sha(Path(__file__)),result_sha256=sha(FIT/'attempt_01.json'),
                replay_sha256=sha(FIT/'independent_both512_and_full_fov_2026_10_07.json'),diagnostic_sha256=sha(diagfile),
                report_sha256=sha(REPORT),figures=files,original_capability_gate_changed=False,
                scientific_confirmation_patients=0,publication_claim_confirmed=False,visual_review_completed=False)
    with (FIG/'provenance.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,report=REPORT.name,figures=[v['path'] for v in files])))
if __name__=='__main__':main()
