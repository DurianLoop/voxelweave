"""Create bounded fixed25 variants without editing the completed fixed5 evidence."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def replace_once(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    return s.replace(a,b)

s=(ROOT/'experiments/audit_mc_rc_011_013_label_grid.py').read_text(encoding='utf-8')
s=s.replace('Five fixed official labels','Twenty-five fixed official labels').replace('mc_rc_011_013','mc_rc_next12')
s=s.replace('MC_RC_011_013_HEADER_AND_LABEL_PLAN_2026-10-03.md','MC_RC_NEXT12_IDENTITY_SOURCE_PLAN_2026-10-03.md')
s=replace_once(s,"expected={x['series_uid'] for x in selected['next_nonpixel_qualification_series']}","expected={x['SeriesInstanceUID'] for x in h['expected_sources']}")
s=s.replace('len(expected)==5 and len(h[\'series\'])==5',"len(expected)==25 and len(h['series'])==25")
s=s.replace('Fixed five official labels','Fixed twenty-five official labels')
s=s.replace('150_000_000','500_000_000').replace('2_000_000_000','10_000_000_000')
s=s.replace("complete=len(r['series'])==5","complete=len(r['series'])==25")
s=replace_once(s,"paths=[Path(__file__),PLAN,SELECTION", "paths=[Path(__file__),ROOT/'MC_RC_NEXT12_LABEL_GRID_ADDENDUM_2026-10-03.md',PLAN,SELECTION")
p=ROOT/'experiments/audit_mc_rc_next12_label_grid.py';assert not p.exists();p.write_text(s,encoding='utf-8')

s=(ROOT/'experiments/verify_mc_rc_011_013_header_label.py').read_text(encoding='utf-8')
s=s.replace('mc_rc_011_013','mc_rc_next12').replace('independent_all230_headers_and_5_labels_attempt_02.json','independent_all1475_headers_and_25_labels_attempt_01.json')
start=s.index("        for b in h['helper_bindings']")
end=s.index('        prior=read(',start)
s=s[:start]+"        for b in h['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']\n        expected={x['SeriesInstanceUID']:x for x in h['expected_sources']};assert len(expected)==25\n        assert set(expected)=={x['source']['SeriesInstanceUID'] for x in h['series']}=={x['series_uid'] for x in r['series']}\n"+s[end:]
s=s.replace("proof['raw_dicom_headers_verified']==230 and proof['labels_verified']==5 and proof['passed_series']==r['source_preflight_series_passed']==3","proof['raw_dicom_headers_verified']==1475 and proof['labels_verified']==25 and proof['passed_series']==r['source_preflight_series_passed']")
p=ROOT/'experiments/verify_mc_rc_next12_header_label.py';assert not p.exists();p.write_text(s,encoding='utf-8')

s=(ROOT/'literature/fetch_task_normalization_context_2026_10_03.py').read_text(encoding='utf-8')
s=s.replace('task_normalization_context_fulltexts_2026-10-03','task_adaptation_direct_fulltexts_2026-10-03').replace('2026-10-03_task_normalization_context_selection.md','2026-10-03_task_adaptation_direct_selection.md')
start=s.index('PAPERS=');end=s.index('\ndef sha',start)
s=s[:start]+"PAPERS=[('tumorsynth','PMC13036690','10.1148/rycan.250222'),\n ('multiplanar_fibroid','PMC13385847','10.1038/s41746-026-02780-6'),\n ('plaque_highresolution','PMC10244753','10.3389/fcvm.2023.1127653')]\n"+s[end:]
s=replace_once(s,"sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir", "sys.stdout.reconfigure(encoding='utf-8');sys.path.insert(0,str(ROOT.parent/'experiments'));from vs_seg_task_cpu_support import resource_gate;resource_gate();OUT.mkdir")
p=ROOT/'literature/fetch_task_adaptation_direct_2026_10_03.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print('Created three new scripts; completed fixed5 scripts unchanged.')
