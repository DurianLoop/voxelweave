"""Capture startup/import failures before importing any research or torch code."""
import argparse,datetime,json,os,subprocess,sys,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def capture(command,folder):
    env=dict(os.environ,PYTHONUNBUFFERED='1',PYTHONIOENCODING='utf-8',
        PYTHONPATH=str(ROOT.parent)+';'+str(ROOT.parents[1]))
    code=1;child=None
    with (folder/'stdout_stderr.txt').open('w',encoding='utf-8') as log:
        try:
            child=subprocess.Popen(command,cwd=ROOT.parents[1],env=env,stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1)
            for line in child.stdout:
                log.write(line);log.flush();print(line,end='',flush=True)
            code=child.wait()
        except BaseException:
            message=traceback.format_exc();log.write(message);log.flush();print(message,file=sys.stderr,flush=True)
            if child is not None and child.poll() is None:child.terminate();child.wait()
            code=130 if isinstance(sys.exc_info()[1],KeyboardInterrupt) else 1
    (folder/'exit.json').write_text(json.dumps(dict(exit_code=code,command=command),indent=2),encoding='utf-8')
    return code


def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['pair','local','extended'],default='pair')
    p.add_argument('--seed',type=int,choices=[3407,2027,9103],default=3407)
    p.add_argument('--preflight',action='store_true');p.add_argument('--log-probe',action='store_true')
    a=p.parse_args()
    folder=ROOT/'startup_logs'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');folder.mkdir(parents=True)
    command=[sys.executable,'-B','-u','-m','pastnet_ixi_context_recovery.run','--variant',a.variant,'--seed',str(a.seed)]
    if a.preflight:command.append('--preflight')
    if a.log_probe:command.append('--log-probe')
    (folder/'request.json').write_text(json.dumps(dict(command=command,python=sys.executable,
        entrypoint='stdlib-only startup capture; frozen training recipe unchanged'),indent=2),encoding='utf-8')
    print(f'Startup log: {folder / "stdout_stderr.txt"}',flush=True)
    code=capture(command,folder)
    if code:print(f'Exit code {code}; full startup/traceback log: {folder / "stdout_stderr.txt"}',file=sys.stderr,flush=True)
    raise SystemExit(code)


if __name__=='__main__':main()
