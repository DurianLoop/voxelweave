"""Independent checks of numerical contracts and protected historical inputs."""
from pathlib import Path
import json, hashlib, re
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, rankdata, pearsonr

P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent; OUT=P13/'outputs'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
manifest=json.loads((P13/'original_manifest.json').read_text())
assert all(sha(P13/'original_snapshot'/r['path'])==r['sha256'] for r in manifest['files'])
checks.append({'check':'original_snapshot_sha256','passed':True,'files':len(manifest['files'])})
run=json.loads((OUT/'run_manifest.json').read_text())
assert all(sha(PAPER/r['path'])==r['sha256'] for r in run['inputs'])
checks.append({'check':'historical_analysis_inputs_unchanged','passed':True,'files':len(run['inputs'])})
old=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_same_model_benefit_per_case.csv')
new=pd.read_csv(OUT/'benefit_coupling.csv')
old_corr=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_same_model_benefit_correlations.csv')
joined=new.merge(old_corr,on=['dataset','model','score'],validate='one_to_one')
err=float(abs(joined.raw_rho-joined.spearman).max()); assert err<1e-12
for r in new.itertuples():
    g=old[old.dataset.eq(r.dataset)&old.model.eq(r.model)]
    x,y,z=[rankdata(g[k]) for k in [r.score,'benefit','mae_x4']]
    design=np.column_stack([np.ones(len(g)),z])
    rx=x-design@np.linalg.lstsq(design,x,rcond=None)[0]
    ry=y-design@np.linalg.lstsq(design,y,rcond=None)[0]
    independent=pearsonr(rx,ry).statistic
    assert abs(independent-r.partial_rho_given_x4)<1e-10
checks.append({'check':'all_74_score_associations_and_independent_partial_rank','passed':True,'rows':len(new),'max_raw_difference':err})
a=pd.read_csv(OUT/'architecture_sensitivity.csv')
p9=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs/p9_architecture_forest.csv')
p11=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_ixi_clean_model_summary_full.csv')
for ds,ref,column,w in [('fastmri',p9,'observable_gain','mean'),('ixi',p11,'median_observable_gain','median')]:
    q=a[a.dataset.eq(ds)&a.within_case.eq(w)&a.across_cases.eq(w)].merge(ref,on='model',validate='one_to_one')
    assert np.allclose(q.gain,q[column],atol=1e-12)
checks.append({'check':'ten_historical_observable_point_estimates_reproduced','passed':True})
identity=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_identity_swap_per_plane_full.csv')
balanced=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_identity_swap_balanced_per_case_full.csv')
assert len(identity)==2875 and len(balanced)==575
assert not identity.duplicated(['case','model','target_z']).any()
assert np.allclose(balanced.observable_gain_balanced,(balanced.observable_gain_residue1+balanced.observable_gain_residue3)/2)
checks.append({'check':'identity_swap_rows_and_balancing','passed':True,'planes':len(identity),'model_cases':len(balanced)})
ix=pd.read_csv(OUT/'ixi_i3net_benefit_per_case.csv'); pl=pd.read_csv(OUT/'ixi_i3net_benefit_per_plane.csv')
assert len(ix)==115 and len(pl)==7334 and not pl.duplicated(['case','z']).any()
assert pl.z.mod(2).eq(1).all()
for k in ['mae_x2','mae_x4']:
    expected=pl.groupby('case')[k].mean().sort_index()
    assert np.allclose(expected,ix.set_index('case')[k].sort_index(),atol=1e-12)
checks.append({'check':'ixi_common_support_aggregation','passed':True,'planes':len(pl)})

roots=[PAPER/'ARCHIVE/PLANS'/x for x in ['PLAN9_ARCH_GENERALIZATION','PLAN10_ACCEPTANCE_ITERATION','PLAN11_CLAIM_STRENGTHENING','PLAN12_STRICT_REVIEW_ITERATION']]
inventory=[]
for root in roots:
    for p in sorted(root.rglob('*.csv')):
        r={'path':p.relative_to(PAPER).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,
           'technical_only':bool(re.search('smoke|pilot|failure_probe|debug',p.name,re.I))}
        try:
            frame=pd.read_csv(p); r.update(rows=len(frame),columns=len(frame.columns),column_names=';'.join(frame.columns),read_status='OK')
        except Exception as exc: r.update(read_status=type(exc).__name__+': '+str(exc))
        inventory.append(r)
pd.DataFrame(inventory).to_csv(OUT/'historical_csv_inventory.csv',index=False)
checks.append({'check':'historical_csv_full_parse_inventory','passed':all(r['read_status']=='OK' for r in inventory),'files':len(inventory)})
for d in [PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER',PAPER/'TMI/TMI_ARCH_GENERALIZED']:
    for p in d.glob('*.tex'):
        raw=p.read_bytes(); assert not b'\times' in raw # catches literal TAB + imes
        assert not any(v in raw for v in [b'\x08',b'\x0c',b'\x0b'])
        assert b'\rho' not in raw # catches literal CR + ho
    tex=(d/'main.tex').read_text(encoding='utf-8')
    cite=set(x.strip() for group in re.findall(r'\\cite\{([^}]+)\}',tex) for x in group.split(','))
    keys=set(re.findall(r'@\w+\{([^,]+)',(d/'references.bib').read_text(encoding='utf-8')))
    assert not cite-keys
checks.append({'check':'latex_escape_and_bibliography_keys','passed':True})
(OUT/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))
