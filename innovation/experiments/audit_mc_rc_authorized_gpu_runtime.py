"""No patient inputs: validate authorized GPU kernels before scored inference."""
from mc_rc_authorized_gpu_adapter import enable_authorized_gpu,synthetic_device_preflight,gpu_resource_gate
import json,sys,traceback
from datetime import datetime,timezone
from mc_rc_global_local_task_cpu_support import ROOT,sha


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    out=ROOT/'experiments/mc_rc_authorized_gpu_runtime_preflight';out.mkdir(exist_ok=False)
    path=out/'attempt_01.json';protocol=ROOT/'MC_RC_NO_AUGMENTATION_FULL_EVALUATION_GPU_PROTOCOL_2026-10-03.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        script_sha256=sha(__file__),protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),
        adapter_sha256=sha(ROOT/'experiments/mc_rc_authorized_gpu_adapter.py'),
        patient_inputs_read=0,label_inputs_read=0,training_updates=0,
        confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    try:
        r['runtime']=enable_authorized_gpu();r['synthetic_preflight']=synthetic_device_preflight()
        r['resources']=gpu_resource_gate();r['complete']=True
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False));return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
