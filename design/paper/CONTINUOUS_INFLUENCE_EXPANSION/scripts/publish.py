from adapters import *
import pandas as pd,shutil,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
LABEL={'linear':'Linear','cubic':'Cubic','acvtt':'ACVTT','ressrdiff':'Res-SRDiff','arssr':'ArSSR','cycleinr':'CycleINR-style','resunet':'ResUNet','gan_2p5d':'Pix2Pix-GAN','swinir':'SwinIR','saint':'SAINT-style','i3net':'I3Net','hat':'HAT','smamba_unet':'SMamba-UNet'}
CV=P/'revised_manuscript';OLD=P/'original_snapshot/manuscript'
def write_tex(name,text):(CV/name).write_text(text,encoding='utf-8')
def ci(r,ep):
    if not pd.notna(r.get(ep)):return 'NA'
    return f'{r[ep]:.3f} [{r[ep+"_low"]:.3f}, {r[ep+"_high"]:.3f}]'
def state(r):
    if r.technical_status!='ELIGIBLE':return 'NA (interface)'
    if not pd.notna(r.rank_stability_min):return 'undefined / FAIL'
    label=r'\textbf{FAIL}' if r.stability=='FAIL' else str(r.stability)
    return f'{r.rank_stability_min:.3f} / {label}'
def figure(d):
    q=d[d.technical_status=='ELIGIBLE'].copy();q['sort']=q.model.map({m:i for i,m in enumerate(LABEL)});q=q.sort_values(['dataset','sort'])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(7.1,5.3),sharey=True)
    for j,ep in enumerate(['beyond_count','fixed_count']):
        ax=axs[j]
        for k,(_,r) in enumerate(q.iterrows()):
            y=len(q)-1-k;col='#236c98' if r.dataset=='fastmri' else '#b86516'
            if not pd.notna(r[ep]):continue
            ax.errorbar(r[ep],y,xerr=[[r[ep]-r[ep+'_low']],[r[ep+'_high']-r[ep]]],fmt='o' if r.stability=='PASS' else 'x',color=col,ms=4,capsize=2,lw=1)
        ax.axvline(0,color='.55',ls='--',lw=.7);ax.grid(axis='x',alpha=.18)
        ax.set_xlabel('Alignment advantage over count' if j==0 else 'Exactly-one-anchor partial correlation')
        ax.set_title('(a) Beyond count' if j==0 else '(b) Fixed count')
    axs[0].set_yticks(range(len(q)),[f'{r.dataset}/{LABEL[r.model]}' for _,r in q.iloc[::-1].iterrows()])
    fig.subplots_adjust(left=.25,right=.99,bottom=.12,top=.93,wspace=.16)
    fig.text(.26,.025,'Intervals: new eight-model family per cohort/endpoint. x: numerical stability FAIL.',fontsize=7)
    for ext in ['pdf','png']:fig.savefig(P/f'figures/continuous_influence_all_models.{ext}',dpi=200,bbox_inches='tight')
    plt.close(fig);shutil.copy2(P/'figures/continuous_influence_all_models.pdf',CV/'continuous_influence_all_models.pdf')
def main():
    assert read(P/'outputs/analysis_complete.json')['status']=='PASS'
    if (P/'batch_repair_freeze.json').exists():
        assert (P/'outputs/batch_repair_complete.json').exists() and read(P/'outputs/batch_repair_complete.json')['status']=='PASS','Batch correction still running; do not publish a stale partial table'
    d=pd.read_csv(P/'CONTINUOUS_INFLUENCE_BIG_TABLE.csv');assert len(d)==26
    n=int((d.technical_status=='ELIGIBLE').sum());passed=int((d.stability=='PASS').sum());support=int((d.claim_status=='SUPPORTED').sum())
    nmodels=int(d[d.technical_status=='ELIGIBLE'].model.nunique());new=d[(d.source=='new')&(d.technical_status=='ELIGIBLE')];new_supported=int((new.claim_status=='SUPPORTED').sum())
    lines=['# 13 模型 continuous-influence 大表','',f'实际测试 {nmodels} 个模型、{n} 个模型/队列；其中 {passed} 个模型/队列通过数值稳定性，{support} 个同时满足稳定性与 beyond-count 区间为正。其余模型仍逐行保留。',
           '','本表使用新的每队列/每端点八模型同时置信区间。旧三模型点估计保持不变，原推断家族区间保存在 CSV 的 legacy 列及上一轮交付；两种区间不混称同一家族。',
           '','| 模型 | 队列 | 技术资格 | 稳定性 .005 / .02 / −.01 | 门槛 / 判定 | beyond count [同时95%CI] | fixed count [同时95%CI] | beyond-count 支持判定 |','|---|---|---|---|---|---|---|---|']
    for _,r in d.iterrows():
        st=' / '.join(f'{r[k]:.6f}' if pd.notna(r.get(k)) else 'NA' for k in ['stability_half','stability_double','stability_negative'])
        lines.append(f'| {LABEL[r.model]} | {r.dataset} | {r.technical_status} | {st} | '+(f'{r.threshold:.2f} / {r.stability}' if pd.notna(r.get('threshold')) else 'NA')+f' | {ci(r,"beyond_count")} | {ci(r,"fixed_count")} | {r.claim_status} |')
    lines+=['','Linear 是物理双锚插值控制，不是新增神经架构。ArSSR 的线性稠密初始化只作为内部特征，不计作额外采集锚。结构兼容、稳定性和 beyond-count 支持是不同结论。',
            '','## 接口不合格原因']
    for m,g in d[d.technical_status!='ELIGIBLE'].groupby('model'):lines.append(f'- {LABEL[m]}：{g.reason.iloc[0]}。')
    lines+=['','旧 SAINT 的目标知情空结果、I3Net/CycleINR 历史稳定性失败和所有旧负结果保留。本轮没有新增协方差验证，Claim D 仍仅覆盖 HAT/SwinIR/SAINT 的原 IXI 试验。']
    (P/'CONTINUOUS_INFLUENCE_BIG_TABLE.md').write_text('\n'.join(lines),encoding='utf-8')
    rows=[]
    for m in LABEL:
        parts=[LABEL[m]]
        for ds in ['fastmri','ixi']:
            r=d[(d.model==m)&(d.dataset==ds)].iloc[0]
            parts.extend([ci(r,'beyond_count'),ci(r,'fixed_count'),state(r)])
        rows.append(' & '.join(parts)+r'\\')
    tex=r'''\begin{table*}[t]\centering\scriptsize
\caption{Continuous-influence audit of the full 13-model bank. BC: $|\rho_I|-|\rho_{count}|$ for error alignment; FC: exactly-one-anchor partial correlation adjusting span, asymmetry and examination. Intervals use a NEW simultaneous family of eight scheduled models per cohort/endpoint, retaining numerical failures. Min./status is the minimum of three frozen amplitude/sign rank checks; gates are .85 for HAT/SwinIR and .90 otherwise. Interface NA is not a measured null. Linear is an analytical control. All individual checks, legacy intervals and secondary signs are in the supplement/CSV.}
\label{tab:continuous-big}\setlength{\tabcolsep}{3pt}
\begin{tabular}{lrrlrrl}\toprule
& \multicolumn{3}{c}{fastMRI: 24 examinations} & \multicolumn{3}{c}{IXI: 115 examinations}\\
Model & BC [sim. CI] & FC [sim. CI] & Min./status & BC [sim. CI] & FC [sim. CI] & Min./status\\\midrule
'''+ '\n'.join(rows)+r'\bottomrule\end{tabular}\end{table*}'
    write_tex('continuous_influence_big_table.tex',tex)
    supp=[r'\section{Full-Bank Continuous-Influence Extension}',r'\label{sec:continuous-extension}',
          'This separately frozen retrospective extension tests Linear, ACVTT, ResUNet, SMamba-UNet and the validated variable-depth ArSSR interface. The earlier closure and historical inference families remain intact. The new eight-model family includes original HAT/SwinIR/SAINT observations without re-inference, retains numerically failed models and uses identical examination bootstrap draws within each cohort. It does not correct for the entire research history.',
          'Acquired inputs, all 417 depth-selected targets per model, masks, Q1/Q99 scale, context grid, four Rademacher seeds, amplitudes, clipping and fixed-count covariates remain unchanged. All new models use the existing .90 gate; HAT/SwinIR retain .85. Response arrays are hash-bound before target access. ArSSR densifies only its two observed anchors using the native deterministic initializer at the actual physical spacing; intermediate planes are not acquired evidence. Its target-only query is checked against the full native normalized-input routine at all nine contexts before outcome evaluation.',
          r'\input{continuous_influence_big_table.tex}',
          f'Of {n} measured model/cohort strata, {passed} pass numerical stability and {support} also have positive simultaneous beyond-count intervals. The five newly scheduled implementations contribute {len(new)} measured strata and {new_supported} such supported strata. Technical incompatibility, numerical failure and a null association are separately reported.',
          r'\begin{figure*}[t]\centering\includegraphics[width=.98\textwidth]{continuous_influence_all_models.pdf}',
          r'\caption{Every estimable continuous-influence model/cohort, under the new simultaneous comparison families. Crosses retain numerical failures. This figure is not filtered by favorable results.}\end{figure*}']
    for ds in ['fastmri','ixi']:
        supp += [r'\begin{table*}[t]\centering\scriptsize',f'\\caption{{{ds}: all three rank-stability checks; every model retained. Legacy null/fail results belong to their original information contracts.}}',r'\begin{tabular}{lrrrrll}\toprule Model & $+.005$ & $+.02$ & $-.01$ & Gate & Stability & Beyond-count claim\\\midrule']
        for _,r in d[d.dataset==ds].iterrows():
            parts=[LABEL[r.model]]+[f'{r[k]:.6f}' if pd.notna(r.get(k)) else 'NA' for k in ['stability_half','stability_double','stability_negative']]+[f'{r.threshold:.2f}' if pd.notna(r.get('threshold')) else 'NA',str(r.stability) if pd.notna(r.stability) else 'NA',r.claim_status.replace('_',' ')]
            supp.append(' & '.join(parts)+r'\\')
        supp.append(r'\bottomrule\end{tabular}\end{table*}')
    supp += [r'\subsection{All secondary endpoints and amplitudes}',
             'All values below are descriptive; no secondary endpoint replaces alignment or changes claim eligibility. BC is absolute-correlation advantage over count; FC is exactly-one-anchor partial rank correlation. Undefined values remain NA.']
    secondary=pd.read_csv(P/'ALL_SECONDARY_SIGNS.csv')
    for ds in ['fastmri','ixi']:
        for ep in ['alignment','observable','disagreement','paired_error','reference_error','companion_error']:
            supp +=[r'\begin{table*}[t]\centering\scriptsize',f'\\caption{{{ds}, {ep.replace("_"," ")}: complete descriptive BC/FC by amplitude.}}',r'\begin{tabular}{lrrrr}\toprule Model & $+.01$ (primary) & $+.005$ & $+.02$ & $-.01$\\\midrule']
            for m in LABEL:
                q=secondary[(secondary.dataset==ds)&(secondary.model==m)&(secondary.endpoint==ep)]
                if q.empty:continue
                parts=[LABEL[m]]
                for eps in [.01,.005,.02,-.01]:
                    r=q[np.isclose(q.epsilon,eps)].iloc[0];parts.append(f'{r.beyond_count:.4f}/{r.fixed_count:.4f}' if pd.notna(r.beyond_count) and pd.notna(r.fixed_count) else 'NA')
                supp.append(' & '.join(parts)+r'\\')
            supp.append(r'\bottomrule\end{tabular}\end{table*}')
    supp +=[r'\subsection{Limits and provenance}',
             'Linear is not a neural replication. Adapted implementations and the ArSSR/CycleINR code lineage limit independence of architectural counts. Fixed-count associations can retain geometry and clipping effects. The cohort is reused retrospectively; simultaneous intervals quantify sampling variation within these fixed analyses, not historical selection. No new covariance or calibrated reliability claim follows automatically. All earlier negative findings and NEEDS HUMAN CONFIRMATION data/ethics items remain valid.',
             r'\paragraph{Reproduction.} The protocol, frozen hashes, raw responses, independent physical-anchor embedding checks, all 26 bank rows, bootstrap replicates and execution logs are retained in \path{CONTINUOUS_INFLUENCE_EXPANSION/}. Earlier masks, predictions and protocols remain read-only.']
    write_tex('continuous_influence_supp.tex','\n\n'.join(supp))
    t=(OLD/'main.tex').read_text(encoding='utf-8')
    t=t.replace(r'\input{final_acquired_table.tex}',r'\input{continuous_influence_big_table.tex}')
    t=t.replace(r'Table~\ref{tab:acquired-core}',r'Table~\ref{tab:continuous-big}')
    t=t.replace('Every two-model simultaneous interval is positive','Every original two-model simultaneous interval is positive')
    t=t.replace('Influence formed with acquired-only masks and scales.','Earlier three-model experiments with acquired-only masks and scales; their original inference families are retained here. The new full-bank comparison is in Table~\\ref{tab:continuous-big}.')
    t=t.replace('Five additional interfaces are available but their acquired-only probes were not run; it is not counted as acquired-only validation.',f'The new comparison evaluates {nmodels} compatible implementations under one declared response protocol; interface-ineligible models remain in Table~\\ref{{tab:continuous-big}}.')
    t=t.replace('Acquired-only neural influence now covers three compatible models on two brain cohorts, including a non-transformer.',f'The full-bank acquired-only comparison covers {nmodels} compatible implementations, including a linear control, on two brain cohorts.')
    t=t.replace('The acquired-only mechanism evidence is scoped to HAT, SwinIR and SAINT-style on the two brain cohorts.',f'Continuous-influence claims are limited to the numerically eligible, supported model/cohort strata in Table~\\ref{{tab:continuous-big}}; {support} of {n} measured strata satisfy both requirements under the new comparison family.')
    old_abstract='Acquired-only HAT, SwinIR and SAINT-style probes pass their frozen numerical gates and support influence beyond anchor count on both cohorts; fixed-context perturbations support the conditional local covariance trend.'
    t=t.replace(old_abstract,f'An acquired-only audit evaluates {nmodels} compatible implementations: {passed} of {n} model/cohort strata pass frozen numerical gates, and {support} also support influence beyond anchor count under simultaneous model-family intervals. Earlier fixed-context perturbations support a conditional local covariance trend.')
    marker=r'\subsection{Cross-architecture sharing beyond TTA}'
    addition=f'''\\paragraph{{Expanded continuous-influence comparison.}}
The new retrospective extension tests Linear, ACVTT, ResUNet, SMamba-UNet and the validated ArSSR pair interface using the same targets, inputs and response settings. Table~\\ref{{tab:continuous-big}} retains all 13 bank entries. Across {n} measured model/cohort strata, {passed} pass the frozen numerical gates and {support} also have positive beyond-count intervals; {new_supported} supported strata come from the new implementations. The NEW simultaneous family covers eight scheduled models separately per cohort/endpoint, retaining failures regardless of sign. Original three-model point estimates are unchanged; their legacy intervals remain separately labeled. Linear is an analytical control, not a neural architecture.

'''
    t=t.replace(marker,addition+marker)
    write_tex('main.tex',t)
    # Keep the previous coverage table as a historical table only in the previous
    # closure section; current main coverage must reflect the new measured statuses.
    cov=(OLD/'architecture_coverage_table.tex').read_text(encoding='utf-8')
    cov=cov.replace('Subscript $a$: technically available pair interface, influence not run.','Subscript $a$: interface audit only; see the current full-bank table for evaluated continuous influence.')
    for m in ['linear','acvtt','resunet','smamba_unet','arssr']:
        q=d[d.model==m];st_ok=(q.stability=='PASS').all();sup_ok=(q.claim_status=='SUPPORTED').all()
        symbol=r'$\checkmark$' if sup_ok else (r'$\circ$' if st_ok else r'$\times$')
        def update(line):
            tail=line.split(r'\\',1)[1] if r'\\' in line else ''
            cells=line.split('&');cells[4]=' '+symbol+' ';cells[5]=' '+(r'$\checkmark$' if st_ok else r'$\times$')+' ';cells[-1]=' Phase; influence in large table '+r'\\';return '&'.join(cells)+tail
        cov='\n'.join(update(line) if line.startswith(LABEL[m]+' &') else line for line in cov.splitlines())
    cov=cov.replace('SAINT\'s new acquired-only result is supported while its historical beyond-count result is $\\circ$ (supplement).','Current cohort-specific effects and numerical gates are in Table~\\ref{tab:continuous-big}; historical SAINT null evidence remains in the supplement. Covariance coverage is unchanged.')
    write_tex('architecture_coverage_table.tex',cov)
    s=(OLD/'supplement.tex').read_text(encoding='utf-8').replace(r'\end{document}',r'\clearpage\input{continuous_influence_supp.tex}'+'\n'+r'\end{document}')
    write_tex('supplement.tex',s);figure(d)
    from refine_manuscript import refine
    refine(d)
    report=f'''# Continuous influence 扩展实验报告

在保留上一轮文件的独立目录内，新增测试五个已有实现；全表列出 13 模型、两个队列的 26 条记录。实际完成 {nmodels} 模型、{n} 个模型/队列；数值 PASS {passed} 个，按新八模型家族区间同时满足稳定性与 beyond-count 支持 {support} 个。新增实现中满足两项要求 {new_supported}/{len(new)} 个模型/队列。

[完整大表](CONTINUOUS_INFLUENCE_BIG_TABLE.md) 和同名 CSV 包含所有失败、NA 和 legacy 区间。[修订主文](revised_manuscript/main.pdf) 与 [补充材料](revised_manuscript/supplement.pdf) 需结合 build_logs 的成功记录判断是否已完成重建；实际入口交付状态以 DELIVERY_STATUS.json 为准，未完成视觉检查不得声称投稿就绪。

主文使用新的八模型同时家族大表，补充材料列出全部三次稳定性检查、全幅度全端点和森林图。原三模型点估计没有变化；新旧多重比较区间分别保留。没有重训、增加数据集、改公式、选更有利阈值或删去负结果。

证据范围：Claims A/B 的原五核心相位矩阵不变；Claim C 的新增支持必须按模型/队列和稳定性界限读取；本轮没有新增协方差试验，Claim D 不扩大。Linear 是解析对照，ArSSR 为本地适配实现，不应将八个名称写成八次结构独立的神经验证。

限制：同一批检查被回顾性复用；置信区间不覆盖整个研究过程中的选择。数值 PASS 不等于通用 Jacobian 精确性，不保证校准可靠性、排名改进或临床效用。旧 SAINT 空结果、I3Net/CycleINR 历史 FAIL、126.4% 最坏近似误差和 guard 负结果均保留。真实数据/伦理/授权仍 NEEDS HUMAN CONFIRMATION。

工程记录：原始响应和其输入哈希在目标读取前记录；全部新响应以独立物理锚嵌入公式重算，bootstrap 与显式病例复制对照。详见 outputs/summary_*.json、SOURCE_MANIFEST.json、freeze.json、logs/ 和 PROTOCOL.md。
'''
    (P/'FINAL_REPORT_ZH.md').write_text(report,encoding='utf-8')
    write(P/'outputs/manuscript_generated.json',dict(status='PASS',measured_models=nmodels,measured_strata=n,numerical_pass=passed,supported=support,new_supported=new_supported))
    print('LARGE TABLE AND MANUSCRIPTS GENERATED',nmodels,n,passed,support,flush=True)
if __name__=='__main__':main()
