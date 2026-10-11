"""Bounded isolated replay from the committed checkpoint; never a full run."""
import argparse,datetime,json,shutil,sys,time,traceback
from pathlib import Path
import torch
from pastnet_v2.common import sha256,write_json
from pastnet_ixi_context import run as trainer
from i3net_amp_recovery.run import amp_recovery,ProbeFinished
from .run import ROOT,inspect,hashes,stream


def stats(x):
    if not isinstance(x,torch.Tensor):return str(type(x))
    y=x.detach();finite=torch.isfinite(y)
    return dict(shape=list(y.shape),dtype=str(y.dtype),finite=bool(finite.all()),
        nonfinite=int((~finite).sum()),minimum=float(y[finite].min()) if finite.any() else None,
        maximum=float(y[finite].max()) if finite.any() else None)


def worker(session,attempts):
    scratch=session/'scratch';calls=0;started=time.perf_counter();objective=trainer.objective
    def measured(model,batch,*args,**kwargs):
        nonlocal calls
        calls+=1
        try:
            loss,parts=objective(model,batch,*args,**kwargs)
        except Exception:
            write_json(session/'objective_exception.json',dict(calls=calls,batch={k:stats(v) for k,v in batch.items()},traceback=traceback.format_exc()))
            raise
        if not bool(torch.isfinite(loss)):
            write_json(session/'nonfinite_objective.json',dict(calls=calls,parts=parts,batch={k:stats(v) for k,v in batch.items()}))
        if calls%100==0:print(f'Isolated replay: {calls} microbatches, {time.perf_counter()-started:.1f}s',flush=True)
        return loss,parts
    trainer.objective=measured
    args=argparse.Namespace(variant='extended',seed=3407,out=scratch,smoke=False,resume=True,preflight=False,stop_after_epoch=0)
    result=dict(replay_attempts_limit=attempts,source='committed epoch4',full_started=False)
    try:
        with amp_recovery(session/'updates.jsonl',stop_after_attempts=attempts):trainer.train(args)
    except ProbeFinished:
        result.update(bounded_replay_completed=True,failure_reproduced=False,
            note='No failure within this replay; this does not establish the cause or rule out nondeterministic failures.')
    except Exception as exc:
        result.update(bounded_replay_completed=False,failure_reproduced=True,exception_type=type(exc).__name__,exception=str(exc),traceback=traceback.format_exc())
        # Preserve the exact failure state, confined to this disposable diagnostic copy.
        tb=sys.exc_info()[2]
        while tb:
            if tb.tb_frame.f_code is trainer.train.__code__:
                values=tb.tb_frame.f_locals
                saved={k:values[k].state_dict() for k in ('model','ema','optimizer','scaler') if k in values}
                saved.update(epoch=values.get('epoch'),step=values.get('step'),torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all())
                if 'data' in values:saved['batch']={k:v.detach().cpu() if isinstance(v,torch.Tensor) else v for k,v in values['data'].items()}
                torch.save(saved,session/'failure_state.pth')
            tb=tb.tb_next
        traceback.print_exc()
    finally:
        trainer.objective=objective
        result.update(objective_calls=calls,elapsed_seconds=time.perf_counter()-started,
            peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30)
        write_json(session/'replay_result.json',result)
    print(json.dumps(result,indent=2),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--attempts',type=int,default=192);p.add_argument('--worker-session',type=Path)
    a=p.parse_args();assert 190<=a.attempts<=195,'Bounded diagnostic only'
    if a.worker_session:
        session=a.worker_session.resolve();assert session.is_relative_to((ROOT/'diagnostics').resolve())
        worker(session,a.attempts);return
    source=trainer.ROOT/'runs/full_extended_seed3407';status=inspect(source,'extended',3407)
    assert status['epochs']==4 and not status['completed'],'Only the audited epoch4 failure may be replayed'
    original={n:sha256(source/n) for n in ['last.pth','best.pth','manifest.json']}
    session=ROOT/'diagnostics'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');scratch=session/'scratch';scratch.mkdir(parents=True)
    for n in original:shutil.copy2(source/n,scratch/n)
    provenance=dict(recovery_hashes=hashes(),frozen_training_hashes=trainer.hashes(),original_checkpoint_hashes=original,
        attempts_limit=a.attempts,policy='Exact frozen epoch5 replay in isolated checkpoint copy; only diagnostics added; no full run')
    write_json(session/'provenance.json',provenance)
    code=stream([sys.executable,'-B','-u','-m','pastnet_ixi_context_recovery.replay','--worker-session',str(session),'--attempts',str(a.attempts)],session/'stdout_stderr.txt')
    unchanged=all(sha256(source/n)==h for n,h in original.items())
    write_json(session/'original_preservation.json',dict(original_files_unchanged=unchanged,source_hashes_unchanged=trainer.hashes()==provenance['frozen_training_hashes'],exit_code=code))
    assert unchanged,'Original file unexpectedly changed'
    print(f'Diagnostic artifacts: {session}',flush=True)
    if code:raise SystemExit(code)


if __name__=='__main__':main()
