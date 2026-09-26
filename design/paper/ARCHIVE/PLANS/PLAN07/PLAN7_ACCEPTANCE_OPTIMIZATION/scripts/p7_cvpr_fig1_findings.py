"""Distinct CVPR Fig. 1: continuous influence mechanism and falsification gates."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

HERE=Path(__file__).resolve(); OUT=HERE.parents[2]/"CVPR"/"CVPR_UPGRADE"/"PAPER_FINAL"/"figures"
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"pdf.fonttype":42})
fig,ax=plt.subplots(figsize=(10.6,3.05)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")

def box(x,y,w,h,text,fc,ec="#23364d",lw=1.2,fs=9,weight="normal"):
    p=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.012,rounding_size=0.018",facecolor=fc,edgecolor=ec,linewidth=lw)
    ax.add_patch(p); ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,weight=weight,color="#17212b",linespacing=1.18); return p
def arrow(a,b,y,lab=""):
    ax.add_patch(FancyArrowPatch((a,y),(b,y),arrowstyle="-|>",mutation_scale=12,linewidth=1.25,color="#38536d"))
    if lab:ax.text((a+b)/2,y+.055,lab,ha="center",va="bottom",fontsize=8,color="#38536d")
def varrow(x,y1,y2,lab=""):
    ax.add_patch(FancyArrowPatch((x,y1),(x,y2),arrowstyle="-|>",mutation_scale=12,linewidth=1.25,color="#38536d"))
    if lab: ax.text(x+.012,(y1+y2)/2,lab,ha="left",va="center",fontsize=7.4,color="#38536d")

ax.text(.165,.94,"1  Count-matched contexts",ha="center",weight="bold",fontsize=11)
ax.text(.50,.94,"2  Measure shared neural influence",ha="center",weight="bold",fontsize=11)
ax.text(.835,.94,"3  What the evidence supports",ha="center",weight="bold",fontsize=11)

# panel 1
for x,label,c in [(.055,"-2","#7fb3d5"),(.145,"+2","#7fb3d5"),(.235,"+3","#f5b041")]:
    ax.add_patch(Circle((x,.68),.028,facecolor=c,edgecolor="#23364d",lw=1));ax.text(x,.68,label,ha="center",va="center",fontsize=7)
ax.text(.145,.57,"Reference: (-2,+2)\nComparator: (-2,+3)\nshared-anchor count = 1",ha="center",va="top",fontsize=8.5)
box(.035,.29,.11,.13,"same count\nweak reuse", "#eaf2f8")
box(.185,.29,.11,.13,"same count\nstrong reuse", "#fdebd0")
ax.text(.165,.17,"Count alone cannot encode\nhow much the estimator uses an anchor.",ha="center",fontsize=8.5,color="#34495e")

# panel 2
box(.36,.66,.12,.12,"shared physical\nanchor", "#eaf2f8",weight="bold",fs=8.3)
box(.52,.66,.12,.12,"same seeded\nperturbation", "#e8f8f5",fs=8.3)
arrow(.48,.52,.705)
box(.36,.36,.12,.12,"response in\ncontext a", "#f4ecf7",fs=8.3)
box(.52,.36,.12,.12,"response in\ncontext b", "#f4ecf7",fs=8.3)
varrow(.42,.655,.49,"finite difference"); varrow(.58,.655,.49,"finite difference")
box(.415,.13,.17,.12,"response cosine =\nshared influence I", "#d6eaf8",weight="bold")
ax.add_patch(FancyArrowPatch((.42,.355),(.49,.255),arrowstyle="-|>",mutation_scale=12,linewidth=1.25,color="#38536d"))
ax.add_patch(FancyArrowPatch((.58,.355),(.51,.255),arrowstyle="-|>",mutation_scale=12,linewidth=1.25,color="#38536d"))

# panel 3
box(.705,.67,.25,.13,"SUPPORTED LOCALLY\nI → aligned error → cancellation", "#d5f5e3",ec="#1e8449",weight="bold")
box(.705,.44,.25,.13,"BOUNDARY\nfixed-count NingXia is mixed/null", "#fcf3cf",ec="#b7950b",weight="bold")
box(.705,.18,.25,.17,"FAILED METHOD GATES\ncontext selection · jackknife\nresidualized disagreement", "#fadbd8",ec="#a93226",weight="bold")
ax.text(.83,.075,"Mechanism evidence ≠ a universally better score",ha="center",weight="bold",fontsize=9.5,color="#922b21")
fig.tight_layout(pad=.25)
fig.savefig(OUT/"p7_fig1_mechanism_findings.pdf",bbox_inches="tight")
fig.savefig(OUT/"p7_fig1_mechanism_findings.png",dpi=300,bbox_inches="tight")
print(OUT/"p7_fig1_mechanism_findings.pdf")
