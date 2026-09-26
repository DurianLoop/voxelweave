"""Scientific invariants and protected-source checks; no broad repository tests."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from topcow_experiment import interpolate,weights,fg
from stat_utils import corr,partial,gain,naurc
P14=Path(__file__).resolve().parents[1]; OUT=P14/'outputs'
checks=[]
for stage in ['PLAN13_EVIDENCE_UPGRADE','PLAN14_SCIENTIFIC_STRENGTHENING']:
    root=P14.parent/stage; m=json.loads((root/'original_manifest.json').read_text())
    assert all(hashlib.sha256((root/'original_snapshot'/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in m['files'])
    checks.append({'check':stage+'_snapshot','files':len(m['files']),'passed':True})

# Degree-three reproduction, reflection equivalence, and the acquired-only boundary.
z=np.arange(30,dtype=np.float32); v=(.001*z**3-.01*z**2+.2*z+1)[None,None,:]
for q in [7,9,11,13,15,17,19]:
    for phase in [0,2]:
        assert np.allclose(interpolate(v,q,4,phase,'cubic'),v[:,:,q],rtol=1e-5,atol=1e-5)
    for method in ['linear','cubic']:
        a=interpolate(v,q,4,0,method)
        modified=v.copy(); modified[:,:,1::2]+=5000
        assert np.array_equal(a,interpolate(modified,q,4,0,method))
        assert np.allclose(interpolate(v,q,4,0,method),interpolate(5*v,q,4,0,method)/5,rtol=1e-5)
checks.append({'check':'cubic_polynomial_reproduction_and_no_missing_slice_access','passed':True})

bank=pd.read_csv(OUT/'bank_mask_raw_reproduction.csv')
assert len(bank)==84 and bank.absolute_difference.max()<1e-10
assert bank.prediction_mask_differs_from_gt_voxels.gt(0).all()
checks.append({'check':'bank_masks_recomputed_from_raw_predictions','rows':len(bank),'max_error':float(bank.absolute_difference.max()),'passed':True})

# Independent residualization checks the partial Spearman algebra.
from scipy.stats import rankdata,pearsonr
ix=pd.read_csv(P14.parent/'PLAN13_EVIDENCE_UPGRADE/outputs/ixi_i3net_benefit_per_case.csv')
for normalized in [False,True]:
    scale=ix.acquired_range.to_numpy() if normalized else 1
    x=ix.anchor_cv.to_numpy()/scale; y=ix.benefit.to_numpy()/scale; z=ix.mae_x4.to_numpy()/scale
    X=np.column_stack([np.ones(len(ix)),rankdata(z)])
    a=rankdata(x)-X@np.linalg.lstsq(X,rankdata(x),rcond=None)[0]
    b=rankdata(y)-X@np.linalg.lstsq(X,rankdata(y),rcond=None)[0]
    assert abs(pearsonr(a,b).statistic-partial(x,y,z))<1e-12
checks.append({'check':'independent_OLS_partial_rank_units','passed':True})

if (OUT/'topcow_analysis_manifest.json').exists():
    p=pd.read_csv(OUT/'topcow_per_plane.csv',dtype={'case':str})
    b=pd.read_csv(OUT/'topcow_benefit_per_plane.csv',dtype={'case':str})
    c=pd.read_csv(OUT/'topcow_per_case.csv',dtype={'case':str})
    assert p.case.nunique()==125 and p.observable.between(0,1+1e-12).all()
    assert not p.duplicated(['case','z','pair','condition','mask']).any()
    assert p.groupby(['case','z']).size().eq(12).all()
    assert p.groupby(['case','pair','condition','mask']).residue.nunique().eq(2).all()
    assert not b.duplicated(['case','z','model']).any()
    expected=p.groupby(['case','pair','condition','mask','residue']).observable.mean().groupby(['case','pair','condition','mask']).mean()
    actual=c.set_index(['case','pair','condition','mask']).observable
    assert np.allclose(expected.sort_index(),actual.sort_index(),atol=1e-12)
    checks.append({'check':'topcow_complete_keys_energy_and_residue_balance','passed':True,'cases':125,'planes':len(p)//12})
    e=pd.read_csv(OUT/'topcow_effects.csv'); assert len(e)==6
    assert np.isfinite(e.select_dtypes(include='number')).all().all()
for prefix,n,planes in [('bright_anchor',125,10779),('cas_transfer',100,6412)]:
    p=pd.read_csv(OUT/(prefix+'_per_plane.csv'),dtype={'case':str})
    c=pd.read_csv(OUT/(prefix+'_per_case.csv'),dtype={'case':str})
    keys=['case','pair','condition']
    assert p.case.nunique()==n and len(p)==4*planes
    assert not p.duplicated(keys+['z']).any()
    assert p.groupby(['case','z']).size().eq(4).all()
    assert p.groupby(keys).residue.nunique().eq(2).all()
    expected=p.groupby(keys+['residue']).bright_disagreement.mean().groupby(keys).mean()
    assert np.allclose(expected.sort_index(),c.set_index(keys).bright_disagreement.sort_index(),atol=1e-12)
    r=pd.read_csv(OUT/(prefix+'_rankings.csv'));assert len(r)==8
    checks.append({'check':prefix+'_complete_keys_and_aggregation','passed':True,'cases':n,'planes':planes})

root=P14.parents[2]
for filename in ['topcow_run_manifest.json','cas_transfer_manifest.json']:
    m=json.loads((OUT/filename).read_text())
    assert all(hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in m['inputs'])
    checks.append({'check':filename+'_source_hashes_unchanged','passed':True,'files':len(m['inputs'])})

raw=(P14/'PROTOCOL.md').read_bytes();versions=P14/'protocol_versions'
# Preserve exact bytes, not normalized newlines, to match execution-time hashes.
e04=raw.split(b'## E05')[0]
expected=json.loads((OUT/'bright_anchor_manifest.json').read_text())['protocol_sha256']
matches=[x for x in [e04,e04.rstrip()+b'\n',e04.rstrip()+b'\n\n',e04.rstrip()+b'\r\n',e04.rstrip()+b'\r\n\r\n'] if hashlib.sha256(x).hexdigest()==expected]
assert matches,'Cannot reconstruct execution-time E04 protocol exactly'
(versions/'E04_amendment_before_bright_results.md').write_bytes(matches[0])
(versions/'E05_fixed_rule_before_CAS_results.md').write_bytes(raw)
hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in versions.glob('*.md')}
for filename,target in [('E01_E02_before_outcomes.md','9899c3956cfcf1ccd7638481b326098c2cc20679b544d5f2541c1d32921d71ed'),('E03_amendment_before_scale_results.md','7a1506b9551900fd602b62a465901ff5e1cae05f09c92cb4cba8ee452ac441da')]:
    path=versions/filename; normalized=path.read_bytes().replace(b'\r\n',b'\n')
    candidates=[normalized,normalized.replace(b'\n',b'\r\n')]
    candidates += [x.rstrip()+suffix for x in candidates.copy() for suffix in [b'',b'\n',b'\n\n',b'\r\n',b'\r\n\r\n']]
    matches=[x for x in candidates if hashlib.sha256(x).hexdigest()==target]
    assert matches,filename+' execution-time bytes unavailable'
    path.write_bytes(matches[0]);hashes.add(target)
for directory in ['case_records','cas_records']:
    for file in (P14/directory).glob('*.json'):
        assert json.loads(file.read_text())['protocol_sha256'] in hashes
for filename in ['bright_anchor_manifest.json','cas_transfer_manifest.json']:
    m=json.loads((OUT/filename).read_text());assert m['protocol_sha256'] in hashes
checks.append({'check':'execution_protocol_hashes_match_preserved_versions','passed':True,'versions':len(list(versions.glob('*.md')))})
(OUT/'verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
