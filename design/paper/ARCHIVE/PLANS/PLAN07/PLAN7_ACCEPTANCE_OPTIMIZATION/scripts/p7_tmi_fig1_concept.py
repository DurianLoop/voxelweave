"""Redesign TMI Fig. 1 for a clean 30-second mechanism read."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE=Path(__file__).resolve(); OUT=HERE.parents[2]/"TMI"/"TMI_MANUSCRIPT_SUBMISSION_FINAL"/"figures"
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"pdf.fonttype":42})
ORANGE="#d96f24"; BLUE="#2463a3"; GREY="#536273"; INK="#17212b"
fig,ax=plt.subplots(figsize=(7.05,2.28)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")

def box(x,y,w,h,text,fc,ec,weight="normal",fs=8.5):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.012,rounding_size=.018",facecolor=fc,edgecolor=ec,linewidth=1.25))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",color=INK,weight=weight,fontsize=fs,linespacing=1.15)
def arrow(x1,x2,y):
    ax.add_patch(FancyArrowPatch((x1,y),(x2,y),arrowstyle="-|>",mutation_scale=12,linewidth=1.25,color=GREY))

ax.text(.5,.955,r"Disagreement observes error differences:  $f_A-f_B=e_A-e_B$",ha="center",va="top",fontsize=10.5,weight="bold")
ax.text(.19,.82,"PHYSICAL EVIDENCE",ha="center",weight="bold",fontsize=8,color=GREY)
ax.text(.50,.82,"RECONSTRUCTION ERRORS",ha="center",weight="bold",fontsize=8,color=GREY)
ax.text(.80,.82,"OBSERVED DISAGREEMENT",ha="center",weight="bold",fontsize=8,color=GREY)

rows=[(.57,ORANGE,"SHARED","same anchors reused\nin contexts A and B","aligned errors\n$e_A\\approx e_B$","small $|f_A-f_B|$\nshared error hidden"),
      (.22,BLUE,"DISJOINT","different physical anchors\nin contexts A and B","context-sensitive errors\nremain different","larger $|f_A-f_B|$\nerror remains visible")]
for y,c,label,left,mid,right in rows:
    ax.text(.012,y,label,ha="left",va="center",weight="bold",color=c,fontsize=8.5)
    box(.10,y-.105,.22,.21,left,"#fff7f0" if c==ORANGE else "#eef5fb",c,fs=8)
    box(.39,y-.105,.22,.21,mid,"#fff7f0" if c==ORANGE else "#eef5fb",c,weight="bold",fs=8.5)
    box(.69,y-.105,.21,.21,right,"white",c,weight="bold",fs=8.2)
    arrow(.325,.385,y); arrow(.615,.685,y)

fig.tight_layout(pad=.2)
fig.savefig(OUT/"fig1_concept.pdf",bbox_inches="tight")
fig.savefig(OUT/"fig1_concept.png",dpi=300,bbox_inches="tight")
print(OUT/"fig1_concept.pdf")
