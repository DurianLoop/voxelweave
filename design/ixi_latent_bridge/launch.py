"""Standard-library startup capture; never import torch before opening the log."""
import argparse,datetime,hashlib,json,os,subprocess,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent


def stream(command,log):
    env=dict(os.environ,PYTHONPATH=str(ROOT.parent)+';'+str(ROOT.parents[1]),PYTHONIOENCODING='utf-8',PYTHONUNBUFFERED='1')
    with log.open('w',encoding='utf-8') as f:
        child=None
        try:
            child=subprocess.Popen(command,cwd=ROOT.parents[1],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                text=True,encoding='utf-8',errors='replace',bufsize=1)
            for line in child.stdout:f.write(line);f.flush();print(line,end='',flush=True)
            return child.wait()
        except BaseException:
            message=traceback.format_exc();f.write(message);f.flush();print(message,file=sys.stderr,flush=True)
            if child is not None and child.poll() is None:child.terminate();child.wait()
            return 130 if isinstance(sys.exc_info()[1],KeyboardInterrupt) else 1


def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['pair','blind','latent'],default='pair')
    p.add_argument('--seed',type=int,choices=[3407,2027,9103],default=3407);p.add_argument('--preflight',action='store_true')
    p.add_argument('--smoke',action='store_true');p.add_argument('--log-probe',action='store_true');a=p.parse_args()
    session=ROOT/'logs'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');session.mkdir(parents=True)
    (session/'request.json').write_text(json.dumps(dict(arguments=vars(a),launcher_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2),encoding='utf-8')
    print(f'Complete startup/training logs: {session}',flush=True)
    if a.log_probe:
        code=stream([sys.executable,'-B','-u','-c',"import sys;print('stdout captured');print('中文日志');print('stderr captured',file=sys.stderr);raise RuntimeError('intentional startup capture probe')"],session/'probe.txt')
        text=(session/'probe.txt').read_text(encoding='utf-8')
        assert code!=0 and all(s in text for s in ['stdout captured','中文日志','stderr captured','Traceback','intentional startup capture probe'])
        (session/'probe.json').write_text(json.dumps(dict(passed=True,child_exit_code_preserved=code)),encoding='utf-8')
        print('Startup capture probe passed.');return
    prefix=[sys.executable,'-B','-u','-m','ixi_latent_bridge.run','--seed',str(a.seed)]
    if a.smoke:prefix+=['--smoke']
    commands=[]
    if not a.smoke:commands.append(('preflight',prefix+['--preflight']))
    if not a.preflight:
        commands.append(('frozen_i3_validation',prefix+['--baseline']))
        variants=['blind','latent'] if a.variant=='pair' else [a.variant]
        commands.extend((v,prefix+['--variant',v,'--resume']) for v in variants)
        if a.variant=='pair' and not a.smoke:commands.append(('paired_report',[sys.executable,'-B','-u','-m','ixi_latent_bridge.report','--seed',str(a.seed)]))
    for name,command in commands:
        code=stream(command,session/f'{name}_stdout_stderr.txt')
        (session/f'{name}_exit.json').write_text(json.dumps(dict(exit_code=code,command=command),indent=2),encoding='utf-8')
        if code:raise SystemExit(code)


if __name__=='__main__':main()
