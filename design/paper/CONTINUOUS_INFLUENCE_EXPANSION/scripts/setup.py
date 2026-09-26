from pathlib import Path
import sys,json,shutil,datetime
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';C=P.parent/'ARCHITECTURE_COVERAGE_CLOSURE';CV=P.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
sys.path.insert(0,str(B/'scripts'))
from common import sha,read,write
def main():
    assert not (P/'freeze.json').exists(),'Do not overwrite freeze'
    for d in ['outputs/responses','logs','original_snapshot','revised_manuscript','figures','build_logs']:(P/d).mkdir(parents=True,exist_ok=True)
    shutil.copytree(CV,P/'original_snapshot/manuscript',dirs_exist_ok=True)
    shutil.copytree(CV,P/'revised_manuscript',dirs_exist_ok=True)
    write(P/'model_registry.json',[r for r in read(C/'model_registry.json') if r['model'] in ['acvtt','resunet','smamba_unet','arssr']])
    files=list((B/'inputs').glob('*.npz'))+list((B/'targets').glob('*.npy'))
    files +=[B/'case_registry.json',B/'scripts/common.py',B/'scripts/acquired_probe.py',B/'scripts/audit_statistics.py',C/'model_registry.json',C/'FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.csv',C/'outputs/saint_acquired_observations.csv']
    files+=list((B/'outputs').glob('*acquired*.csv'))
    files += [ROOT/r['checkpoint'] for r in read(P/'model_registry.json')]
    for d in ['baseline/ixi_acvtt_2p5d','baseline/ixi_smamba_unet_2p5d','baseline/ixi_arssr']:
        files+=list((ROOT/d).glob('*.py'))
    files +=[ROOT/'pre/ixi_diffusion/resunet.py']
    files+=list((P/'original_snapshot/manuscript').rglob('*'))
    manifest=[]
    for f in sorted(set(files)):
        if f.is_file():manifest.append(dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f),bytes=f.stat().st_size))
    write(P/'SOURCE_MANIFEST.json',manifest)
    code={f.name:sha(f) for f in (P/'scripts').glob('*.py') if f.name in ['adapters.py','run.py']}
    write(P/'freeze.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),protocol_sha256=sha(P/'PROTOCOL.md'),source_manifest_sha256=sha(P/'SOURCE_MANIFEST.json'),registry_sha256=sha(P/'model_registry.json'),inference_code=code))
    print('FROZEN',len(manifest),'sources',len(read(P/'model_registry.json')),'checkpoints',flush=True)
if __name__=='__main__':main()
