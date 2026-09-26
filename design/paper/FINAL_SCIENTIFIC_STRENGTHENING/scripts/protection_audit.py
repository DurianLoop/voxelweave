from common import *
import argparse
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--after-install',action='store_true');args=ap.parse_args();guard();rows=[]
    for r in read(P/'original_manifest.json'):
        snap=P/'original_snapshot'/r['path'];rows.append(dict(group='original_snapshot',path=str(snap.relative_to(P)),passed=sha(snap)==r['sha256']))
        current=ROOT/r['path'];is_cv='/CVPR/CVPR_ARCH_GENERALIZED/PAPER/' in r['path']
        if not(args.after_install and is_cv):rows.append(dict(group='unchanged_original',path=r['path'],passed=sha(current)==r['sha256']))
    for r in read(P/'source_manifest.json'):
        rows.append(dict(group='frozen_scientific_source',path=r['path'],passed=sha(ROOT/r['path'])==r['sha256']))
    for r in read(P/'prepared_input_manifest.json'):
        rows.append(dict(group='frozen_prepared_input',path=r['path'],passed=sha(P/r['path'])==r['sha256']))
    df=pd.DataFrame(rows);name='protection_after_install' if args.after_install else 'protection_before_install';df.to_csv(OUT/(name+'.csv'),index=False)
    payload={'checks':len(df),'failures':int((~df.passed).sum()),'groups':df.groupby('group').size().to_dict(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(P/'FINAL_ITERATION_PROTOCOL.md'),'TMI_modified':False if df[(df.group=='unchanged_original')&df.path.str.contains('/TMI/')].passed.all() else 'CHECK_FAILURE'};write(OUT/(name+'.json'),payload);print(payload,flush=True)
    assert df.passed.all(),df[~df.passed].path.tolist()
if __name__=='__main__':main()
