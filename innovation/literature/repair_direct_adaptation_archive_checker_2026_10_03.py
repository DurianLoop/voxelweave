"""Retain first checker failure; correct stored search schema and use attempt02 receipt."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
original=ROOT/'literature/verify_direct_adaptation_and_identity_stage_2026_10_03.py'
snapshot=ROOT/'literature/verify_direct_adaptation_stage_failed_attempt_01.py.txt';assert not snapshot.exists();snapshot.write_bytes(original.read_bytes())
record=ROOT/'SESSION_ARCHIVE_VERIFICATION_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.json'
p=ROOT/'literature/direct_adaptation_archive_failure_provenance_2026-10-03.json';assert not p.exists()
p.write_text(json.dumps(dict(checker_snapshot=snapshot.relative_to(ROOT).as_posix(),checker_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),failed_receipt=record.relative_to(ROOT).as_posix(),failed_receipt_sha256=hashlib.sha256(record.read_bytes()).hexdigest(),reason="Checker used search['queries'] instead of actual search['responses']; research records unchanged"),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=original.read_text(encoding='utf-8');assert s.count("search['queries']")==1;s=s.replace("search['queries']","search['responses']")
s=s.replace("include(Path(__file__));include(ROOT/'literature/finalize_direct_adaptation_identity_archive_2026_10_03.py')", "include(Path(__file__));include(ROOT/'literature/finalize_direct_adaptation_identity_archive_2026_10_03.py');include(ROOT/'literature/repair_direct_adaptation_archive_checker_2026_10_03.py');include(ROOT/'literature/verify_direct_adaptation_stage_failed_attempt_01.py.txt');include(ROOT/'literature/direct_adaptation_archive_failure_provenance_2026-10-03.json');include(ROOT/'SESSION_ARCHIVE_VERIFICATION_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.json')")
original.write_text(s,encoding='utf-8')
old='SESSION_ARCHIVE_VERIFICATION_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.json';new='SESSION_ARCHIVE_VERIFICATION_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03_attempt_02.json'
for name in ('README.md','EXPERIMENT_QUEUE.md','SESSION_UPDATE_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md','SESSION_HANDOFF_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md'):
    q=ROOT/name;q.write_text(q.read_text(encoding='utf-8').replace('('+old+')','('+new+')'),encoding='utf-8')
q=ROOT/'literature/finalize_direct_adaptation_identity_archive_2026_10_03.py';q.write_text(q.read_text(encoding='utf-8').replace(old,new),encoding='utf-8')
q=ROOT/'SESSION_UPDATE_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md';s=q.read_text(encoding='utf-8');s += '\n归档检查首运行错误使用检索键queries，实际原JSON键为responses，KeyError终止。保留首验收JSON及当时检查器快照/SHA，修正检查器后使用attempt02另存验收，研究记录和门槛不变。\n';q.write_text(s,encoding='utf-8')
print('Retained first checker failure, corrected schema field, prepared attempt02 receipt.')
