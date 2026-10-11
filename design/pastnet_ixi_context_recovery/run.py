"""Capture native Python output without changing the frozen training recipe."""
import argparse,datetime,json,os,subprocess,sys,traceback
from pathlib import Path
from pastnet_v2.common import sha256,write_json
from pastnet_ixi_context.run import ROOT as TRAIN_ROOT,hashes as training_hashes
from pastnet_ixi_context.model import INIT,INIT_SHA
from pastnet_ixi_context.data import MANIFEST

ROOT=Path(__file__).resolve().parent


def hashes():return {p.name:sha256(p) for p in sorted(p for glob in ('*.py','*.ps1','*.cmd') for p in ROOT.glob(glob))}


def runtime():
    import torch
    result=dict(python=sys.version,torch=torch.__version__,cuda_build=torch.version.cuda,cudnn=torch.backends.cudnn.version())
    try:
        probe=subprocess.run(['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader'],capture_output=True,text=True,timeout=10)
        result['gpu_driver_snapshot']=probe.stdout.strip();result['nvidia_smi_exit_code']=probe.returncode
    except Exception as exc:result['driver_snapshot_error']=str(exc)
    return result


def inspect(path,variant,seed):
    m=json.loads((path/'manifest.json').read_text())
    assert m['code_hashes']==training_hashes(),'Frozen source changed'
    assert m['data_sha256']==sha256(MANIFEST) and m['init_sha256']==sha256(INIT)==INIT_SHA
    assert m['variant']==variant and m['seed']==seed and not m['smoke']
    assert (path/'last.pth').exists(),'No committed epoch; inspect initialization separately'
    if (path/'completion.json').exists():
        c=json.loads((path/'completion.json').read_text())
        assert c['completed'] and not c['smoke'] and c['best_sha256']==sha256(path/'best.pth') and c['last_sha256']==sha256(path/'last.pth')
        return dict(completed=True,epochs=c['epochs'],best_psnr=c['best_psnr'],last_sha256=c['last_sha256'])
    import torch
    state=torch.load(path/'last.pth',map_location='cpu',weights_only=False)
    return dict(completed=False,epochs=state['epoch'],best_psnr=state['best'],last_sha256=sha256(path/'last.pth'),
        last_best_sha256=state['best_sha256'],best_payload_epoch=state['best_payload']['epoch'],partial_epoch_will_restart=True)


def stream(command,log):
    """Parent opens the log: child stdout, stderr and uncaught traceback share it."""
    env=dict(os.environ,PYTHONUNBUFFERED='1',PYTHONIOENCODING='utf-8',PYTHONPATH=str(TRAIN_ROOT.parent)+';'+str(TRAIN_ROOT.parents[1]))
    with log.open('w',encoding='utf-8') as f:
        child=subprocess.Popen(command,cwd=TRAIN_ROOT.parents[1],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
            text=True,encoding='utf-8',errors='replace',bufsize=1)
        try:
            for line in child.stdout:
                f.write(line);f.flush();print(line,end='',flush=True)
            return child.wait()
        except BaseException:
            traceback.print_exc(file=f);f.flush()
            if child.poll() is None:child.terminate();child.wait()
            raise


def main():
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,choices=[3407,2027,9103],default=3407)
    p.add_argument('--variant',choices=['pair','local','extended'],default='pair');p.add_argument('--preflight',action='store_true')
    p.add_argument('--log-probe',action='store_true');a=p.parse_args()
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');session=ROOT/'sessions'/stamp;session.mkdir(parents=True)
    if a.log_probe:
        code=stream([sys.executable,'-B','-c',"import sys;print('stdout captured',flush=True);print('中文日志捕获',flush=True);print('stderr captured',file=sys.stderr,flush=True);raise RuntimeError('intentional isolated log probe')"],session/'capture_probe.txt')
        content=(session/'capture_probe.txt').read_text(encoding='utf-8');assert code!=0 and all(x in content for x in ['stdout captured','中文日志捕获','stderr captured','Traceback','intentional isolated log probe'])
        write_json(session/'probe.json',dict(passed=True,exit_code_preserved=code,all_output_captured=True));print('Output capture probe passed.');return
    variants=['local','extended'] if a.variant=='pair' else [a.variant]
    status={v:inspect(TRAIN_ROOT/'runs'/f'full_{v}_seed{a.seed}',v,a.seed) for v in variants}
    write_json(session/'provenance.json',dict(recovery_hashes=hashes(),frozen_training_hashes=training_hashes(),seed=a.seed,
        status_before=status,runtime=runtime(),policy='output capture only; exact frozen trainer --resume; no numerical/model/loss/data/LR changes',preflight=a.preflight))
    print(json.dumps(status,indent=2),flush=True)
    if a.preflight:
        write_json(ROOT/'preflight.json',dict(passed=True,recovery_hashes=hashes(),status=status,frozen_training_hashes=training_hashes(),full_started=False));return
    for v in variants:
        if status[v]['completed']:print(f'{v}: completed {status[v]["epochs"]} epochs, verified and skipped.',flush=True);continue
        command=[sys.executable,'-B','-u','-m','pastnet_ixi_context.run','--variant',v,'--seed',str(a.seed),
            '--out',str(TRAIN_ROOT/'runs'/f'full_{v}_seed{a.seed}'),'--resume']
        code=stream(command,session/f'{v}_stdout_stderr.txt')
        write_json(session/f'{v}_exit.json',dict(exit_code=code,log=str(session/f'{v}_stdout_stderr.txt')))
        if code:raise SystemExit(code)
    if a.variant=='pair':
        code=stream([sys.executable,'-B','-u','-m','pastnet_ixi_context.report','--seed',str(a.seed)],session/'validation_report.txt')
        if code:raise SystemExit(code)


if __name__=='__main__':main()
