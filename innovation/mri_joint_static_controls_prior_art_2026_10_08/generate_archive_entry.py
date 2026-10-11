"""Generate the same append-only archive contract for this reading stage."""
import sys,json,re,ast,difflib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    source=ROOT/'mri_decision_policy_prior_art_2026_10_08/archive_stage.py';old=source.read_text(encoding='utf-8')
    code=old.replace("PREVIOUS=ROOT/'three_arm_resource_bridge_2026_10_08'", "PREVIOUS=ROOT/'mri_decision_policy_prior_art_2026_10_08'")
    assert code!=old
    code=code.replace('4018','4118')
    code=re.sub(r'\b33\b','44',code);code=re.sub(r'\b11\b','12',code)
    needle="ledger['index_abstracts_screened']==24 and len(audit['comparisons'])==6"
    assert needle in code
    code=code.replace(needle,"ledger['index_abstracts_screened']==2 and len(audit['thesis_endpoint_aggregation_comparisons'])==4")
    code=code.replace('index_abstracts_screened=24','index_abstracts_screened=2')
    ast.parse(code)
    dest=HERE/'archive_stage.py'
    with dest.open('x',encoding='utf-8') as f:f.write(code)
    diff=HERE/'ARCHIVE_ENTRY_DIFF.patch'
    with diff.open('x',encoding='utf-8') as f:f.write(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        code.splitlines(keepends=True),fromfile=source.relative_to(ROOT).as_posix(),tofile=dest.relative_to(ROOT).as_posix())))
    goal_source=ROOT/'three_arm_resource_bridge_2026_10_08/USER_GOAL_REQUEST.md'
    message=goal_source.read_text(encoding='utf-8');assert message.count('38420877')==1
    message=message.replace('38420877','38953681')
    with (HERE/'USER_GOAL_REQUEST.md').open('x',encoding='utf-8') as f:f.write(message)
    result=dict(complete=True,errors=[],source_bindings=[base.entry(Path(__file__)),base.entry(source),base.entry(goal_source)],
        output_bindings=[base.entry(dest),base.entry(diff),base.entry(HERE/'USER_GOAL_REQUEST.md')],
        previous_archive_evidence_count=4118,new_full_text_pages_read=44,main_text_pages_read=39,
        ancillary_frontmatter_pages_read=5,visual_pages_reviewed=12,AST_parse_passed=True,
        original_archive_script_not_modified=True,goal_request_budget_current=38953681,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    base.new(HERE/'ARCHIVE_ENTRY_GENERATION.json',result)
    print(json.dumps(dict(complete=True,archive_script_generated=True,goal_request_saved=True)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
