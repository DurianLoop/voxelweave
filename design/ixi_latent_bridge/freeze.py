"""Three adaptation seeds, crossed paired statistics, then an explicit weight lock."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pastnet_v2.common import sha256,write_json
from .model import ROOT
from .run import hashes


def main():
    seeds=[3407,2027,9103];arrays={};identities={};baseline=None
    for seed in seeds:
        g=json.loads((ROOT/'results'/f'gate_seed{seed}.json').read_text())
        assert g['passed'] and g['code_hashes']==hashes(),f'Seed {seed} did not pass all prespecified guards'
        for variant in ['blind','latent']:
            run=ROOT/'runs'/f'full_{variant}_seed{seed}'
            m=json.loads((run/'manifest.json').read_text());c=json.loads((run/'completion.json').read_text())
            assert c['completed'] and not c['smoke'] and m['code_hashes']==hashes() and sha256(run/'best.pth')==c['best_sha256']
            f=pd.read_csv(run/'validation/per_patient.csv').set_index('patient_id').sort_index()
            if baseline is None:
                baseline=pd.read_csv(Path(m['frozen_baseline_dir'])/'per_patient.csv').set_index('patient_id').sort_index()
            assert f.index.equals(baseline.index)
            arrays.setdefault(variant,[]).append(f.to_numpy())
            identities[f'{variant}_seed{seed}']=dict(checkpoint=str(run/'best.pth'),sha256=c['best_sha256'],best_epoch=g['identities'][variant]['best_epoch'])
    rng=np.random.default_rng(73019);seed_draw=rng.integers(0,3,(10000,3));patient_draw=rng.integers(0,58,(10000,58))
    results={}
    for reference in ['blind','frozen_i3']:
        delta=np.stack(arrays['latent'])-(np.stack(arrays['blind']) if reference=='blind' else baseline.to_numpy()[None])
        records={}
        for k,key in enumerate(baseline.columns):
            values=delta[:,:,k]
            sampled=values[seed_draw[:,:,None],patient_draw[:,None,:]].mean((1,2))
            per_seed=values.mean(1)
            records[key]=dict(delta=float(values.mean()),per_seed_delta=per_seed.tolist(),seed_sd=float(per_seed.std(ddof=1)),
                ci95_crossed_seed_patient=np.quantile(sampled,[.025,.975]).tolist(),
                ci975_crossed_seed_patient=np.quantile(sampled,[.0125,.9875]).tolist())
        results[reference]=records
    assert results['blind']['psnr']['delta']>=.05 and results['frozen_i3']['psnr']['delta']>=.10
    assert all(r['psnr']['ci975_crossed_seed_patient'][0]>0 for r in results.values())
    write_json(ROOT/'results/three_seed_validation.json',dict(completed=True,seeds=seeds,paired=results,
        bootstrap='10000 crossed resamples of paired adaptation seeds and patients; only three fixed-prior adaptation seeds',
        identities=identities,code_hashes=hashes(),test_used=False,sota_claim=False))
    write_json(ROOT/'results/final_lock.json',dict(locked=True,seeds=seeds,identities=identities,
        representative_seed=3407,representative_choice='prespecified, no test-based selection',
        statistics_sha256=sha256(ROOT/'results/three_seed_validation.json'),code_hashes=hashes(),
        external_evaluation='Requires separate frozen IXI/NingXia matched evaluation; no test invoked by this lock',sota_claim=False))
    print('Three-seed validation lock complete. External test has not been opened.',flush=True)


if __name__=='__main__':main()
