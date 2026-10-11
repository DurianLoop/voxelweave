"""Post-hoc literal SeriesDescription coverage, not clinical sequence adjudication or causality."""
import hashlib,json,sys,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def family(s):
    d=s.lower()
    if 'fiesta' in d:return 'FIESTA literal'
    if 'spc' in d or 'space' in d:return 'SPC/SPACE literal'
    if 'ci3d' in d:return 'CI3D literal (not adjudicated CISS)'
    if 'drive' in d:return 'DRIVE literal'
    if 'tse' in d:return 'TSE literal'
    return 'unclassified literal'
def main():
    resource_guard();source=HERE/'ALLOWED_LABEL_TIMEPOINT_SOURCE_AUDIT_V2.json';q=json.loads(source.read_text());assert q['complete'] and len(q['series'])==28
    counts=collections.Counter((s['role'],family(s['description'])) for s in q['series'])
    rows=[]
    for (role,f),n in sorted(counts.items()):
        rr=[s for s in q['series'] if s['role']==role and family(s['description'])==f]
        rows.append(dict(role=role,literal_family=f,series=n,distinct_patients=len({s['patient'] for s in rr}),
            patients=sorted({s['patient'] for s in rr}),series_fraction=n/(19 if role=='development' else 9),
            exact_descriptions=dict(collections.Counter(s['description'] for s in rr))))
    assert counts[('development','FIESTA literal')]==12 and counts[('validation','FIESTA literal')]==1
    assert counts[('development','SPC/SPACE literal')]==3 and counts[('validation','SPC/SPACE literal')]==6
    out=dict(complete=True,errors=[],series=28,patient_counts=dict(development=11,validation=4),groups=rows,
        grouping_basis='Literal released SeriesDescription keywords; no pulse-sequence/name adjudication from raw MRI',
        sequence_physics_confirmed=False,development_validation_coverage_differs=True,all_cohort_CISS_claim_supported=False,
        acquisition_shift_causality_established=False,group_patients_not_mutually_exclusive=True,formal_primary_denominators_unchanged=True,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),source]],
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
    with (HERE/'ALLOWED_PROTOCOL_COVERAGE_DIAGNOSTIC.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(out,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
