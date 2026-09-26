from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parents[1];CV=P/'revised_manuscript'
def refine(d):
    t=(CV/'main.tex').read_text(encoding='utf-8')
    t=t.replace('shows all five core probes; complete MIRA report cards','shows all 13 bank entries; historical MIRA report cards')
    pieces=[]
    for _,r in d[(d.source=='new') & (d.stability=='FAIL')].iterrows():
        pieces.append(f'{r.model.replace("_","-")} on {"fastMRI" if r.dataset=="fastmri" else "IXI"} fails the frozen numerical gate (minimum {r.rank_stability_min:.3f})')
    for _,r in d[(d.source=='new') & (d.fixed_count_high<0)].iterrows():
        pieces.append(f'{r.model.replace("_","-")} on {"fastMRI" if r.dataset=="fastmri" else "IXI"} has a negative fixed-count association ({r.fixed_count:.3f}, simultaneous CI [{r.fixed_count_low:.3f},{r.fixed_count_high:.3f}])')
    boundary='The expanded audit also defines boundaries: '+ '; '.join(pieces)+'. Numerical PASS and beyond-count support do not imply a positive fixed-count association.' if pieces else ''
    marker=r'\subsection{Cross-architecture sharing beyond TTA}'
    if boundary:t=t.replace(marker,boundary+'\n\n'+marker)
    (CV/'main.tex').write_text(t,encoding='utf-8')
    f=CV/'continuous_influence_supp.tex';s=f.read_text(encoding='utf-8')
    if (P/'batch_repair_freeze.json').exists():
        note=r'''\paragraph{Batch execution correction.}
ACVTT/IXI and ResUNet/both cohorts initially failed the pre-response batch1-versus-batch4 equality check, although their single-sample adapters matched the native single-sample predictor exactly. Before any target evaluation for those three units, an engineering addendum fixed both nominal and perturbed predictions to single-sample execution. The original $10^{-5}$ native-output and $10^{-6}$ repeat tolerances were unchanged; all nine contexts were rechecked. The original failures are retained. Completed units keep their validated batch path, including the ACVTT/fastMRI numerical-stability failure. No scientific outcome determined this repair's scope; thresholds, cohorts and perturbations were unchanged.
'''
        s=s.replace(r'\subsection{Limits and provenance}',note+'\n'+r'\subsection{Limits and provenance}')
    # A supported BC field is not evidence for a positive FC field.
    if boundary:s=s.replace(r'\subsection{All secondary endpoints and amplitudes}',boundary+'\n\n'+r'\subsection{All secondary endpoints and amplitudes}')
    f.write_text(s,encoding='utf-8')
    f=CV/'continuous_influence_big_table.tex';s=f.read_text(encoding='utf-8').replace(r'\centering\scriptsize',r'\centering\footnotesize');f.write_text(s,encoding='utf-8')
    f=CV/'supplement.tex';s=f.read_text(encoding='utf-8')
    marker=r'\input{final_supp_1.tex}'
    note=r"""The earlier study protocols and counts in Sections 1--9 are retained as historical evidence. Section~\ref{sec:continuous-extension} reports the subsequent full-bank continuous-influence extension and its new simultaneous families; it supersedes earlier ``not run'' counts for that extension only.\par"""
    if note not in s:s=s.replace(marker,note+'\n'+marker)
    f.write_text(s,encoding='utf-8')
if __name__=='__main__':refine(pd.read_csv(P/'CONTINUOUS_INFLUENCE_BIG_TABLE.csv'))
