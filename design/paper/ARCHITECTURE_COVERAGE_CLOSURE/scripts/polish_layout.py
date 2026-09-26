from pathlib import Path

P=Path(__file__).resolve().parents[1]
CV=P/'revised_manuscript'

def polish():
    f=CV/'main.tex';t=f.read_text(encoding='utf-8')
    t=t.replace(r'\input{mira_report_card_table.tex}', '')
    t=t.replace(r'Table~\ref{tab:mira-card} shows actual report cards with NA for measurements absent from each design.',
                r'Table~\ref{tab:neural} shows all five core probes; complete MIRA report cards in the supplement retain NA for fields absent from each design.')
    t=t.replace('Technical compatibility of a further five compatible interfaces is reported as available but not run;',
                'Five additional interfaces are available but their acquired-only probes were not run;')
    f.write_text(t,encoding='utf-8')
    for name in ['main.tex','final_acquired_table.tex','mira_report_card_table.tex','architecture_coverage_supp.tex']:
        f=CV/name;t=f.read_text(encoding='utf-8').replace('{tab:neural}','{tab:acquired-core}');f.write_text(t,encoding='utf-8')
    f=CV/'final_supp_4.tex';t=f.read_text(encoding='utf-8')
    t=t.replace('The acquired-only tables retain all four strata, and the fixed-context table retains every amplitude.',
                'The acquired-only table retains the original four strata and adds two SAINT strata; I3Net/CycleINR remain interface-ineligible. The original stability and fixed-context tables retain every original check and amplitude; the architecture-coverage section adds all SAINT checks.')
    f.write_text(t,encoding='utf-8')
    for name in ['architecture_coverage_table.tex','final_acquired_table.tex']:
        f=CV/name;t=f.read_text(encoding='utf-8').replace(r'\centering\scriptsize',r'\centering\footnotesize');f.write_text(t,encoding='utf-8')
    f=CV/'mira_report_card_table.tex';t=f.read_text(encoding='utf-8').replace(' & nan & ',' & NA & ')
    f.write_text(t,encoding='utf-8')
    f=CV/'architecture_coverage_supp.tex';t=f.read_text(encoding='utf-8')
    marker=r'\subsection{All-core acquired-only report card}'
    if r'\input{mira_report_card_table.tex}' not in t:
        t=t.replace(marker,marker+'\n'+r'\input{mira_report_card_table.tex}')
    marker='The full sampler random-draw order is preserved, including draws for unused output planes.'
    caveat=' Draw indices are phase-local: identical initial RNG states do not match the noise assigned to a given physical target across phases. This residual sampler-noise confound prevents interpreting the Res-SRDiff contrast as a pure measurement-identity effect.'
    if caveat not in t:t=t.replace(marker,marker+caveat)
    f.write_text(t,encoding='utf-8')

if __name__=='__main__':polish()
