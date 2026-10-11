"""Synthetic temperature-placement audit, independent high-precision scalar replay."""
import json,hashlib,sys,time
from pathlib import Path
from decimal import Decimal,localcontext
from datetime import datetime,timezone
from mc_rc_reference_resources_2026_10_07 import resource_guard
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/calibration_position_cpu_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sig(x):return 1/(1+np.exp(-x))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);at=time.perf_counter()
    protocol=ROOT/'CALIBRATION_POSITION_CPU_PROTOCOL_2026-10-07.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        source_bindings=[dict(path=protocol.relative_to(ROOT).as_posix(),sha256=sha(protocol)),
            dict(path=Path(__file__).relative_to(ROOT).as_posix(),sha256=sha(__file__)),
            dict(path='experiments/mc_rc_reference_resources_2026_10_07.py',sha256=sha(ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py'))],
        MRI_arrays_loaded=0,model_forwards=0,training_updates=0,GPU_initialized=False,synthetic_only=True,
        publication_claim_confirmed=False,production_FOV_code_changed=False,temperature_fitted=False)
    try:
        r['resources_before']=resource_guard();z=np.asarray([2.,-10.]);w=np.asarray([.6,.4])
        p0=float(w@sig(z));post_logit=np.log(p0/(1-p0));rows=[];maxerr=0.
        with localcontext() as ctx:
            ctx.prec=80;dz=[Decimal(2),Decimal(-10)];dw=[Decimal('0.6'),Decimal('0.4')]
            def ds(x):return Decimal(1)/(Decimal(1)+(-x).exp())
            dp0=sum(a*ds(b) for a,b in zip(dw,dz));dl=(dp0/(1-dp0)).ln()
            for t in (.5,1.,2.,4.):
                tile=sig(z/t);a=float(w@tile);b=float(sig(post_logit/t));c=float(sig(float(w@z)/t))
                dt=Decimal(str(t));da=sum(x*ds(y/dt) for x,y in zip(dw,dz));db=ds(dl/dt);dc=ds(sum(x*y for x,y in zip(dw,dz))/dt)
                error=max(abs(float(q)-p) for q,p in zip((da,db,dc),(a,b,c)));maxerr=max(maxerr,error)
                assert error<=1e-12 and all((q>=Decimal('.5'))==(p>=.5) for q,p in zip((da,db,dc),(a,b,c)))
                assert np.array_equal(tile>=.5,sig(z)>=.5)
                rows.append(dict(temperature=t,tile_probabilities=tile.tolist(),tile_binary=(tile>=.5).tolist(),
                    calibrate_tiles_then_blend_probability=a,calibrate_tiles_then_blend_binary=a>=.5,
                    calibrate_final_probability=b,calibrate_final_binary=b>=.5,
                    blend_logits_probability=c,blend_logits_binary=c>=.5,independent_decimal_max_abs_error=error))
        base=next(x for x in rows if x['temperature']==1.);changed=next(x for x in rows if x['temperature']==2.)
        assert base['calibrate_tiles_then_blend_binary'] and not changed['calibrate_tiles_then_blend_binary']
        assert all(x['calibrate_final_binary']==(p0>=.5) for x in rows)
        assert not base['blend_logits_binary'] and base['calibrate_tiles_then_blend_binary']
        r.update(logits=z.tolist(),normalized_blending_weights=w.tolist(),baseline_probability=p0,rows=rows,
            independent_decimal_precision=80,independent_max_abs_error=maxerr,
            gates=dict(each_tile_argmax_unchanged=True,tile_calibration_can_change_blended_threshold=True,
                post_blend_calibration_preserves_final_threshold=True,logit_blend_is_different_pipeline=True,
                independent_decimal_replay=True),complete=True)
        r['resources_after']=resource_guard();assert time.perf_counter()-at<60
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}')
    r['elapsed_seconds']=time.perf_counter()-at
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','baseline_probability','independent_max_abs_error','gates','elapsed_seconds')}))
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
