"""Move the shared threshold legend outside bars; retain the original v1 artifact."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'figures/mc_rc_3d_backbone_context_low_lr_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');source=DIR/'plot_data.json';d=json.loads(source.read_text(encoding='utf-8'));rows=d['rows']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4));labels=['native\nLR .001','PCHIP\nLR .001','native\nLR .0001','PCHIP\nLR .0001'];handle=None
    for ax,title,values in zip(axes,['Complete FOV Dice','Original foreground crop Dice'],
        [[r['full_metrics']['dice'] for r in rows],[r['original_augmented_crops'][0]['dice'] for r in rows]]):
        ax.bar(range(4),values,color=['#315d88','#cc8c2e','#315d88','#cc8c2e']);ax.set_xticks(range(4),labels);ax.set_ylim(0,1.10)
        handle=ax.axhline(.9,color='#ac3047',linestyle='--',linewidth=1,label='Original Dice threshold .90');ax.set_title(title,fontsize=11)
        for i,v in enumerate(values):ax.text(i,v+.025,f'{v:.4f}',ha='center',fontsize=9)
        ax.spines[['top','right']].set_visible(False);ax.set_ylabel('Dice')
    fig.suptitle('Development fit control: one patient / one series',fontsize=12,y=.98)
    fig.legend([handle],['Original Dice threshold .90'],loc='upper center',bbox_to_anchor=(.5,.92),fontsize=9,frameon=False)
    fig.subplots_adjust(top=.76,bottom=.20,wspace=.24,left=.07,right=.99)
    outputs=[]
    for suffix in ('png','svg'):
        p=DIR/f'last_checkpoint_fit_comparison_v2.{suffix}';assert not p.exists();fig.savefig(p,dpi=160)
        outputs.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    plt.close(fig)
    out=DIR/'plot_visual_repair_attempt02.json'
    with out.open('x',encoding='utf-8') as f:json.dump(dict(complete=True,script_sha256=sha(__file__),original_v1_preserved=True,
        source_bindings=[dict(path=source.relative_to(ROOT).as_posix(),sha256=sha(source))],outputs=outputs,actual_view_image_completed=False),f,indent=2);f.write('\n')
    print(json.dumps(outputs));return 0
if __name__=='__main__':raise SystemExit(main())
