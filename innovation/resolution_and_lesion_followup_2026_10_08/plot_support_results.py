"""Standalone scientific figure of actual nonmedical support results and metadata audit."""
import sys,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
def main():
    resource_guard();started=time.perf_counter()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    q=read(HERE/'support_synthetic_attempt01/receipt.json');g=read(HERE/'development_geometry_attempt01/receipt.json')
    assert q['complete'] and g['complete'] and not q['errors'] and not g['errors']
    rows=[x for x in q['records'] if x['phantom']=='constant' and x['plan']['active']]
    dest=HERE/'support_results.png';assert not dest.exists()
    fig,axs=plt.subplots(1,3,figsize=(12,3.8),layout='constrained');colors=['#275d9f','#d8862a']
    positions=[0,1]
    axs[0].bar([p-.18 for p in positions],[x['crop_only_zero_padding_control']['mean'] for x in rows],.36,label='Crop only',color=colors[1])
    axs[0].bar([p+.18 for p in positions],[x['output_mean'] for x in rows],.36,label='Real context',color=colors[0])
    axs[0].set(xticks=positions,xticklabels=['Centered','Off center'],ylim=(0,1.15),ylabel='Mean intensity (constant input = 1)',title='Synthetic boundary loss');axs[0].legend(fontsize=8)
    axs[1].bar([p-.18 for p in positions],[x['source_voxels']/x['target_voxels'] for x in rows],.36,label='Source box',color=colors[0])
    axs[1].bar([p+.18 for p in positions],[x['intermediate_voxels']/x['target_voxels'] for x in rows],.36,label='Intermediate',color=colors[1])
    axs[1].set(xticks=positions,xticklabels=['Centered','Off center'],ylabel='Voxel count / target voxel count',title='Conservative context cost');axs[1].legend(fontsize=8)
    axs[2].bar(['Direct witness','No corner\nwitness'],[g['direct_corner_outside_real_FOV_witness_count'],76-g['direct_corner_outside_real_FOV_witness_count']],color=colors)
    axs[2].set(ylim=(0,76),ylabel='Patch plans (two paired inputs)',title='Source outside original FOV')
    for i,ax in enumerate(axs):
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
        if i==2:
            for p in ax.patches:ax.text(p.get_x()+p.get_width()/2,p.get_height()+1,str(int(p.get_height())),ha='center',fontsize=10)
    fig.suptitle('Support qualification only: no patient segmentation effects',fontsize=13)
    fig.savefig(dest,dpi=160);plt.close(fig)
    out=dict(complete=True,errors=[],figure=entry(dest),source_bindings=[entry(p) for p in [Path(__file__),HERE/'support_synthetic_attempt01/receipt.json',HERE/'development_geometry_attempt01/receipt.json']],elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'FIGURE_PROVENANCE.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':main()
