from pathlib import Path
import shutil,json,hashlib
from PIL import Image
P=Path(__file__).resolve().parents[1];PAPER=P.parent;CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER';TMI=PAPER/'TMI/TMI_ARCH_GENERALIZED'
GEN=Path('C:/Users/user/.codex/generated_images/01a0818d-2430-7383-ac1e-0d3327dd25bc')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def original(p):return (P/'original_snapshot'/p.relative_to(PAPER)).read_text(encoding='utf-8')
def write(p,t):p.write_text(t,encoding='utf-8')
def replace(t,a,b):
    assert a in t,a
    return t.replace(a,b)
(P/'generated').mkdir(exist_ok=True);rows=[]
items=[('exec-fe5c9c95-f9bd-475d-baee-4a9fd2031160.png','p16_cvpr_framework.png',CV),('exec-34d7674f-6e0c-4a66-a39a-c7b3ec6c5e01.png','p16_tmi_framework.png',TMI)]
for src,name,folder in items:
    dst=P/'generated'/name;shutil.copy2(GEN/src,dst);shutil.copy2(dst,folder/'figures'/name)
    im=Image.open(dst);rows.append({'source_path':str(GEN/src),'project_path':str(dst.relative_to(PAPER)),'paper_path':str((folder/'figures'/name).relative_to(PAPER)),'sha256':sha(dst),'pixels':list(im.size),'mode':im.mode,'pixel_content_edited_after_generation':False})
# Preserve generation iterations without referencing rejected graphs in a paper.
for src,name in [('exec-7f0f9b5e-40bc-47af-9a69-ad51d7d41dd6.png','tmi_initial_serial_pooling.png'),('exec-beba4d1b-ec70-45a4-b5e6-2534725cf9ca.png','tmi_parallel_missing_mask_edge.png')]:
    shutil.copy2(GEN/src,P/'generated'/name)
t=original(CV/'main.tex');t=replace(t,'{fig1_mechanism.pdf}','{p16_cvpr_framework.png}')
t=replace(t,'Proposed mechanism and reliability boundary. Reusing a physical measurement is not itself decisive; what matters is how similarly that measurement influences both local estimators. Aligned errors cancel in prediction differences. Large separation is one-sided evidence that at least one estimate is inaccurate, but small separation cannot certify correctness.',r'''Measurement-influence framework (schematic). The same target is reconstructed from two acquired contexts using a frozen estimator. Identical perturbations of a shared anchor produce local response differences $\Delta f_c=F_c(x+u)-F_c(x)$, whose cosine probes influence; the diagram denotes the input perturbation by $\delta$. Aligned target errors can cancel in output disagreement. Slice cards, model blocks, and error arrows illustrate the analysis, not patient examples, new layers, or measured results. Small disagreement cannot certify correctness.''')
# Compact the explanatory caption and declare the overview on page one so it
# appears before the detailed theory. Preserve all scientific body text.
start=t.index('\\caption{Measurement-influence framework')
end=t.index('\n\\label{fig:mechanism}',start)
t=t[:start]+r'''\caption{Measurement-influence framework (schematic). Shared-anchor perturbations (diagram: $\delta$; text: $\epsilon\xi$) probe frozen-estimator response alignment. Aligned target errors can cancel in disagreement, so agreement cannot certify correctness. Slice cards and model blocks are illustrations, not patient examples, measured results, or new layers.}'''+t[end:]
start=t.index('\\begin{figure*}[t]');end=t.index('\\end{figure*}',start)+len('\\end{figure*}')
block=t[start:end];t=t[:start]+t[end:]
t=t.replace('This formulation also explains',block+'\n\nThis formulation also explains',1)
# Remove repetition from the conclusion rather than reducing body or figure fonts.
start=t.index('Deterministic MRI interpolators can agree while jointly wrong',t.index('\\section{Conclusion}'))
end=t.index('\n\n\\clearpage',start)
t=t[:start]+'''Shared error can make deterministic MRI interpolators agree while jointly wrong. Across three cohorts and five neural architectures, same-target interventions support a local measurement-dependence mechanism, with cohort-dependent ranking and architecture-dependent influence stability. Retrospective benefit associations weaken after current-error adjustment or scale changes. Prospective acquisition and endpoint validation remain necessary.'''+t[end:]
write(CV/'main.tex',t)
t=original(TMI/'main.tex')
start=t.index('\\begin{figure}[t]',t.index('Our contributions'))
end=t.index('\\end{figure}',start)+len('\\end{figure}')
t=t[:start]+r'''\begin{figure*}[t]
\centering\includegraphics[width=.98\textwidth]{p16_tmi_framework.png}
\caption{Paired-reconstruction framework with acquired-support MRA scoring. General and bright masks independently pool disagreement; references and vessel labels enter retrospective evaluation only. This branch is distinct from historical GT-mask protocols. Images, masks, and model blocks are schematic illustrations, not patient data, measured results, or a new reconstruction backbone.}
\label{fig:concept}
\end{figure*}'''+t[end:]
t=replace(t,'Figure~\\ref{fig:concept} summarizes the hypothesis.', 'Figure~\\ref{fig:concept} summarizes the paired-reconstruction framework and the acquired-support MRA scoring branch.')
write(TMI/'main.tex',t)
write(P/'generation_manifest.json',json.dumps({'tool':'built-in image_gen.imagegen','requested_model':'image2.5','model_selection_available':False,'actual_backend_model_id':'not exposed by tool','assets':rows,'schematic_only':True},indent=2))
for name in ['build.py','render.py']:
    t=(PAPER/'PLAN15_BASELINE_INTEGRATION/scripts'/name).read_text(encoding='utf-8')
    if name=='build.py':t=t.replace('result=[]\nfor job in JOBS:', "JOBS=[job for job in JOBS if job[0] in {'cvpr','tmi'}]\nresult=[]\nfor job in JOBS:")
    else:
        t=t.replace("OUT=P13/'final_page_renders'", "OUT=P13/'final_page_renders_verified'")
        t=t.replace('for name,pdf in jobs.items():', "jobs={k:v for k,v in jobs.items() if k in {'cvpr','tmi'}}\nfor name,pdf in jobs.items():")
    write(P/'scripts'/name,t)
print(json.dumps(rows,indent=2))
