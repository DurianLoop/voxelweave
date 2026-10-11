"""Explicit resource-only 30h supplement; original source-bound 25h entry stays immutable."""
import sys
import run_mc_rc_3d_19series_common_init_cpu_2026_10_07 as runner
from mc_rc_3d_19series_common_init_2026_10_07 import ROOT,OUT,read,sha,BUDGET
ADDENDUM=ROOT/'MC_RC_3D_19SERIES_COMMON_INIT_CPU_WALL_ADDENDUM_2026-10-07.md'

def main():
    before=read(OUT/'invocation01.json');proofpath=OUT/'independent_segment99_attempt01.json';proof=read(proofpath)
    exits=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_2026-10-07.json')
    vexit=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_VERIFIER_2026-10-07.json')
    assert before['complete'] and before['status']=='completed_segment' and not before['errors'] and before['stop_after']==99
    assert exits['training_observed_tool_exit']==0 and exits['training_result_sha256']==sha(OUT/'invocation01.json')
    assert proof['complete'] and not proof['errors'] and proof['all198_batches_verified'] and proof['paired_GT_and_augmentation_identical']
    assert proof['source_sha256']==sha(OUT/'invocation01.json')
    assert vexit['verifier_observed_tool_exit']==0 and vexit['verifier_result_sha256']==sha(proofpath)
    assert read(OUT/'frozen_config.json')['cumulative_train_wall_seconds_limit']==90000
    assert runner.MAX_SECONDS==90000 and runner.BUDGET==BUDGET==19998
    # The bound stays explicit in output records; original scientific config/source/checkpoints are not edited.
    runner.MAX_SECONDS=108000
    original_atomic=runner.atomic_json;original_new=runner.dump_new
    def decorate(path,value):
        if path.parent==OUT and path.name.startswith('invocation'):
            value.update(original_cumulative_wall_limit_seconds=90000,resource_supplement_wall_limit_seconds=108000,
                resource_supplement_file=ADDENDUM.relative_to(ROOT).as_posix(),resource_supplement_sha256=sha(ADDENDUM),
                actual_wrapper_file='experiments/run_mc_rc_3d_19series_common_init_cpu_wall_v2_2026_10_07.py',
                actual_wrapper_sha256=sha(__file__),scientific_update_budget_unchanged=True,
                original_25h_completion_not_claimed=True,segment99_independent_verifier_sha256=sha(proofpath))
        return value
    runner.atomic_json=lambda path,value:original_atomic(path,decorate(path,value))
    runner.dump_new=lambda path,value:original_new(path,decorate(path,value))
    return runner.main()
if __name__=='__main__':raise SystemExit(main())
