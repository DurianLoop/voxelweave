"""Report all four head fits, frozen gates and source verification; original failures retained."""
import json,os,sys
from pathlib import Path
from datetime import datetime,timezone
from mc_rc_observed_only_training_input import ROOT,read,sha
OUT=ROOT/'experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07'
FIG=ROOT/'figures/mc_rc_3d_frozen_feature_head_fit_2026_10_07'
REPORT=ROOT/'MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md'
def fmt(v):return 'undefined' if v is None else f'{v:.6f}' if isinstance(v,float) else str(v)
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not REPORT.exists();FIG.mkdir(exist_ok=False)
    path=OUT/'attempt01.json';proofpath=OUT/'module_full_fov_verification_attempt01.json';prod=read(path);proof=read(proofpath)
    assert prod['complete'] and proof['complete'] and not (prod['errors']+proof['errors']) and proof['result_sha256']==sha(path)
    original=read(ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json')
    lines=['# 固定骨干、主head拟合：全部结果','',
           '4分支各1024次CPU参数更新（bias-only 1参数/full-head 17参数），共4096次；原全网络1024更新另计。',
           '仅001开发系列，骨干及aux heads未更新、阈值0.5不变，四验证/八确认未开。所有分支仍失败原完整拟合gate。',
           '', '| 输入/分支 | 原foreground crop Dice | 主head soft Dice | 完整FOV Dice | recall | precision | absRVE | TP/FP/FN | 原gate |',
           '|---|---:|---:|---:|---:|---:|---:|---|---|']
    for a in prod['arms']:
        m=a['metrics']['full'];lines.append('| '+a['kind']+'/'+a['branch']+' | '+' | '.join(fmt(v) for v in [a['patch_metrics'][0]['dice'],a['final_main_head_numpy_loss']['soft_dice'],m['dice'],m['recall'],m['precision'],m['absRVE']])+f" | {m['tp']}/{m['fp']}/{m['fn']} | {a['training_fit_gate_passed']} |")
    lines+=['','17参数分支将同一foreground训练crop Dice提高到native0.943708/PCHIP0.907710，而完整FOV仅0.590714/0.372671。',
            '这表明原最后特征对该crop具有可利用的分离能力，不支持“当前架构无法学习”的断言；完整体积门槛仍失败，需要覆盖实际推断contexts的训练/骨干适配。',
            'bias-only降低背景概率同时明显牺牲recall；不能只看某个Dice改善选择阈值/偏置策略。输出层分支也改变了优化隔离及LR，不能单因果归结为偏置初始化或深监督冲突。',
            '', '## 全部域和分母','', '| 输入/分支/域 | Dice | recall | precision | absRVE | TP | FP | FN | TN | GT | pred |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for a in prod['arms']:
        for k,m in a['metrics'].items():lines.append('| '+a['kind']+'/'+a['branch']+'/'+k+' | '+' | '.join(fmt(m[v]) for v in ('dice','recall','precision','absRVE','tp','fp','fn','tn','gt_foreground','pred_foreground'))+' |')
    lines+=['','## 独立实现核验','']
    for a in proof['arms']:lines.append(f"- {a['kind']}/{a['branch']}：1024条历史、冻结参数及SHA核对；模块网络重放全部{a['full_native_voxels_replayed']}体素/16tiles，最大概率误差{a['probability_max_absolute_error']:.9g}，二值差异{a['prediction_disagreements']}，四域和原gate全部一致。")
    lines+=['','功能网络与模块网络的比较是实现核验，不是第二独立训练任务网络。',
            '下一项按新协议在全部16个推断tile特征上拟合同样17参数，检查覆盖的影响；不将重复tile/voxel当独立患者，不更改门槛。',
            '', '[运行结果](experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07/attempt01.json)、[模块网络核验](experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07/module_full_fov_verification_attempt01.json)、[新覆盖协议](MC_RC_3D_ALL_TILE_HEAD_FIT_PROTOCOL_2026-10-07.md)。']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    os.environ['MPLCONFIGDIR']=str(FIG/'mplconfig')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,4,figsize=(16,4.6),layout='constrained');colors=['#176c9c','#b46623'];labels=['Native','PCHIP']
    for a in prod['arms']:
        i=0 if a['kind']=='native_reference' else 1
        axes[0].plot([h['update'] for h in a['history']],[h['main_head_soft_dice'] for h in a['history']],
                     color=colors[i],linestyle='--' if a['branch']=='bias_only' else '-',label=labels[i]+' '+a['branch'])
    axes[0].set(xlabel='Head update',ylabel='Main-head batch soft Dice',ylim=(0,1.05),title='Fixed features; original batch')
    axes[0].legend(frameon=False,fontsize=8)
    for panel,key,title in [(1,'patch','Original foreground crop'),(2,'dice','Complete training FOV'),(3,'recall','Complete training FOV recall')]:
        for i,b in enumerate(original['arms']):
            members=[a for a in prod['arms'] if a['kind']==b['kind']]
            vals=[b['patch_metrics'][0]['dice']]+[a['patch_metrics'][0]['dice'] for a in members] if key=='patch' else [b['metrics']['full'][key]]+[a['metrics']['full'][key] for a in members]
            bars=axes[panel].bar(np.arange(3)+(i-.5)*.3,vals,width=.28,color=colors[i])
            for bar,v in zip(bars,vals):axes[panel].text(bar.get_x()+bar.get_width()/2,v+.018,f'{v:.3f}',ha='center',fontsize=8)
        axes[panel].axhline(.9,color='#444',linestyle='--',linewidth=1)
        axes[panel].set(ylim=(0,1.08),ylabel='Hard Dice' if key!='recall' else 'Recall',title=title)
        axes[panel].set_xticks(np.arange(3),['Original 512','Bias only','17 parameters'],rotation=35,ha='right')
    fig.suptitle('One development series; four frozen-feature head fits; 1024 updates each',fontsize=14)
    fig.supxlabel('All four original full fit gates failed. No held-out task qualification or reconstruction claim.',fontsize=10)
    files=[]
    for ext in ('png','svg'):
        p=FIG/('head_fit_results.'+ext);fig.savefig(p,dpi=170);files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    plt.close(fig)
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(Path(__file__)),
                result_sha256=sha(path),verification_sha256=sha(proofpath),report_sha256=sha(REPORT),figures=files,
                visual_review_completed=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    with (FIG/'provenance.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,report=REPORT.name,figures=files)))
if __name__=='__main__':main()
