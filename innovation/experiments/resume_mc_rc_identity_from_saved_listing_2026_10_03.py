"""Preserve first listing failure, then audit its usable listing with explicit gaps."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_local_identity_audit'
original=ROOT/'experiments/audit_mc_rc_local_identity_2026_10_03.py'
snapshot=OUT/'failed_listing_attempt_01_script.py.txt';assert not snapshot.exists();snapshot.write_bytes(original.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'failed_listing_attempt_01.json').write_text(json.dumps(dict(complete=False,errors=['rg enumeration returned an error for inaccessible temporary skill installer folder'],script_sha256=sha(snapshot),script_snapshot=snapshot.name,listing_file='rg_file_listing_attempt_01.txt',listing_sha256=sha(OUT/'rg_file_listing_attempt_01.txt'),stderr_file='rg_file_listing_stderr_attempt_01.txt',stderr_sha256=sha(OUT/'rg_file_listing_stderr_attempt_01.txt'),scientific_confirmation_patients=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=original.read_text(encoding='utf-8').replace('OUT.mkdir(exist_ok=False)','OUT.mkdir(exist_ok=True)')
start=s.index('    result=subprocess.run(');end=s.index("    listing=result.stdout.decode",start)
s=s[:start]+"    from types import SimpleNamespace\n    result=SimpleNamespace(stdout=(OUT/'rg_file_listing_attempt_01.txt').read_bytes())\n    assert len(result.stdout)<64_000_000\n"+s[end:]
s=s.replace("coverage_gaps=[],hits=[]", "coverage_gaps=[dict(path='temp/skill_install_tmp/codex/skill-install-ykexumxq',reason='Inaccessible during rg enumeration; first failure and stderr retained')],excluded_names_before_content_read=[],hits=[]")
s=s.replace("raise AssertionError('Excluded locked/test path reached: '+rel)", "r['excluded_names_before_content_read'].append(rel);continue")
s=s.replace("write(OUT/'attempt_01.json',r)","write(OUT/'attempt_02.json',r)")
s=s.replace("OUT/'focused15_review_queue.json'","OUT/'focused15_review_queue_attempt_02.json'")
p=ROOT/'experiments/audit_mc_rc_local_identity_attempt_02_2026_10_03.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print('First failure retained; second audit reads saved listing, makes no new enumeration.')
