"""Report all-tile coverage diagnostic only after feature and full-FOV verification completes."""
import json,os,sys
from pathlib import Path
from datetime import datetime,timezone
from mc_rc_observed_only_training_input import ROOT,read,sha
OUT=ROOT/'experiments/mc_rc_3d_all_tile_head_fit_2026_10_07'
FIG=ROOT/'figures/mc_rc_3d_all_tile_head_fit_2026_10_07'
REPORT=ROOT/'MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md'
def fmt(v):return 'undefined' if v is None else f'{v:.6f}' if isinstance(v,float) else str(v)
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not REPORT.exists();FIG.mkdir(exist_ok=False)
    path=OUT/'attempt01.json';proofpath=OUT/'module_features_and_full_fov_verification_attempt01.json'
    p,q=read(path),read(proofpath);assert p['complete'] and q['complete'] and not (p['errors']+q['errors']) and q['result_sha256']==sha(path)
    old=read(ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json')
    local=read(ROOT/'experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07/attempt01.json')
    lines=['# 全tile特征覆盖诊断：最后权重全部结果','',
           'native/PCHIP各1024次17参数CPU更新，共2048；固定原骨干，使用同一开发001的全部16个推断tile。',
           '原crop主head分支4096次及原全网络1024次更新分别保留，不合并成一次连续训练。全部原训练gate仍失败；没有验证/确认或新恢复方法确认。',
           '', '| 输入 | 原foreground crop Dice | 全tile训练soft Dice | 完整FOV Dice | recall | precision | absRVE | TP/FP/FN | 原gate |',
           '|---|---:|---:|---:|---:|---:|---:|---|---|']
    for a in p['arms']:
        m=a['metrics']['full'];values=[a['original_fixed_batch_patch_metrics'][0]['dice'],a['final_training_objective']['soft_dice'],m['dice'],m['recall'],m['precision'],m['absRVE']]
        lines.append('| '+a['kind']+' | '+' | '.join(fmt(v) for v in values)+f" | {m['tp']}/{m['fp']}/{m['fn']} | {a['training_fit_gate_passed']} |")
    lines+=['','每臂RAM特征矩阵1,073,741,824bytes；每更新16,777,216个重复tile体素，GT前景13,938，全部16tile保留。',
            '重复体素是训练分母，不是独立patient/series；本项没有删除背景/空tile。native/PCHIP分别训练约151.65/141.81秒，总墙钟约350.65秒。',
            '全tile覆盖后完整FOV Dice从局部head的0.590714/0.372671提高到0.678448/0.475659，但两臂仍未达到0.9，不能作为充分任务能力。',
            'PCHIP原训练crop的Dice还从局部head0.907710降为0.871483。全部context上的共同线性head仍有残余误差；需进一步骨干适配/优化/context控制。',
            '相较局部head，本项改变了训练空间/context覆盖与loss聚合域；不能称严格单因素采样因果实验。来自同一个已见开发series的比较不支持跨患者重建优劣结论。',
            '', '## 所有域与完整分母','', '| 输入/域 | Dice | recall | precision | absRVE | TP | FP | FN | TN | GT | pred |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for a in p['arms']:
        for k,m in a['metrics'].items():lines.append('| '+a['kind']+'/'+k+' | '+' | '.join(fmt(m[v]) for v in ('dice','recall','precision','absRVE','tp','fp','fn','tn','gt_foreground','pred_foreground'))+' |')
    lines+=['','## 独立实现核验','']
    for a in q['arms']:lines.append(f"- {a['kind']}：1024历史/LR、52项冻结骨干、1GiB特征和全部标签流SHA核对；16tile标签/预测/float64 NumPy loss一致，完整{a['full_native_voxels_replayed']}native体素重放，最大概率误差{a['probability_max_absolute_error']:.9g}，阈值预测差异{a['prediction_disagreements']}。")
    lines+=['','所有16tile的hard计数、empty/undefined及原crop计数见JSON。功能/模块网络比较仍只是实现核验，非第二独立训练网络。',
            '', '[全部结果](experiments/mc_rc_3d_all_tile_head_fit_2026_10_07/attempt01.json)、[特征/完整FOV核验](experiments/mc_rc_3d_all_tile_head_fit_2026_10_07/module_features_and_full_fov_verification_attempt01.json)、[冻结协议](MC_RC_3D_ALL_TILE_HEAD_FIT_PROTOCOL_2026-10-07.md)。']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    os.environ['MPLCONFIGDIR']=str(FIG/'mplconfig')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,4,figsize=(16,4.8),layout='constrained');colors=['#176c9c','#b46623'];names=['Native','PCHIP']
    for i,a in enumerate(p['arms']):axes[0].plot([h['update'] for h in a['history']],[h['soft_dice'] for h in a['history']],color=colors[i],label=names[i])
    axes[0].set(xlabel='Head update',ylabel='All-tile soft Dice (overlap counted)',ylim=(0,1.03),title='16 contexts; fixed backbone')
    axes[0].legend(frameon=False)
    for panel,key,title in [(1,'dice','Complete training FOV Dice'),(2,'recall','Complete training FOV recall'),(3,'absRVE','Complete training FOV absRVE')]:
        for i,a in enumerate(p['arms']):
            b=next(v for v in old['arms'] if v['kind']==a['kind']);c=next(v for v in local['arms'] if v['kind']==a['kind'] and v['branch']=='full_head')
            vals=[b['metrics']['full'][key],c['metrics']['full'][key],a['metrics']['full'][key]]
            bars=axes[panel].bar(np.arange(3)+(i-.5)*.3,vals,width=.28,color=colors[i])
            for bar,value in zip(bars,vals):axes[panel].text(bar.get_x()+bar.get_width()/2,value+.018,f'{value:.3f}',ha='center',fontsize=8)
        axes[panel].axhline(.25 if key=='absRVE' else .9,color='#444',linestyle='--',linewidth=1)
        if key!='absRVE':axes[panel].set_ylim(0,1.09)
        axes[panel].set_title(title);axes[panel].set_ylabel(key)
        axes[panel].set_xticks(np.arange(3),['Original 512','2-crop head','16-tile head'],rotation=35,ha='right')
    fig.suptitle('One development series; all-tile linear-head fit; 1024 updates per input',fontsize=14)
    fig.supxlabel('Both original full fit gates failed. Coverage and loss aggregation changed; no independent patient confirmation.',fontsize=9)
    files=[]
    for ext in ('png','svg'):
        dest=FIG/('all_tile_head_fit_results.'+ext);fig.savefig(dest,dpi=170);files.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest)))
    plt.close(fig)
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(Path(__file__)),
                result_sha256=sha(path),verification_sha256=sha(proofpath),report_sha256=sha(REPORT),figures=files,
                visual_review_completed=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    with (FIG/'provenance.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,report=REPORT.name,figures=files)))
if __name__=='__main__':main()
