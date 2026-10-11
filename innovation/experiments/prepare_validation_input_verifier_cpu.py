"""Reuse frozen independent algorithms for new fixed9 source rereads, retain provenance."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'experiments/verify_mc_rc_development_training_input_cpu.py';dest=ROOT/'experiments/verify_mc_rc_validation_task_input_cpu.py';assert not dest.exists()
source_sha=hashlib.sha256(source.read_bytes()).hexdigest();text=source.read_text(encoding='utf-8')
changes={
    "OUT=ROOT/'experiments/mc_rc_development_training_input_cpu'":"OUT=ROOT/'experiments/mc_rc_validation_task_input_cpu'",
    "experiments/mc_rc_current_development_input_preparation/attempt_01.json":"experiments/mc_rc_validation_task_case_preparation/attempt_01.json",
    'independent_all19_observed_inputs_and_label_axes_attempt_01.json':'independent_all9_observed_inputs_and_label_axes_attempt_01.json',
    "experiments/mc_rc_observed_only_training_input.py":"experiments/mc_rc_task_roles_input_cpu.py",
    "len(r['series'])==19":"len(r['series'])==9",
    "q['sparse_inputs_verified']==76":"q['sparse_inputs_verified']==36",
    "q['labels_verified']==19":"q['labels_verified']==9"
}
for before,after in changes.items():assert before in text;text=text.replace(before,after)
needle="        byuid={x['uid']:x for x in r['series']}";assert needle in text
text=text.replace(needle,"        assert {c['patient'] for c in prep['cases']}=={'VS-MC-RC-020','VS-MC-RC-022','VS-MC-RC-024','VS-MC-RC-025'} and len(prep['cases'])==9\n"+needle)
text=text.replace("        assert q['sparse_inputs_verified']==36", "        q['independent_algorithms_reused_from_sha256']='"+source_sha+"'\n        assert q['sparse_inputs_verified']==36")
dest.write_text(text,encoding='utf-8');record=dict(created_utc=datetime.now(timezone.utc).isoformat(),base_file=source.relative_to(ROOT).as_posix(),base_sha256=source_sha,generated_file=dest.relative_to(ROOT).as_posix(),generated_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),changes=changes,scope='Independent algorithms reused from prior developer proof; new original validation source reread, no neural effects')
out=ROOT/'experiments/mc_rc_validation_task_case_preparation/verifier_generation.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,ensure_ascii=False))
