"""Actual terminal exits from this continuation, separate from live formal training."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    paired=ROOT/'experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07/attempt01.json'
    coord=ROOT/'experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07/attempt01.json'
    for p in (paired,coord):
        d=json.loads(p.read_text(encoding='utf-8'));assert d['complete'] and not d['errors']
    r=dict(paired_qualification_observed_tool_chunk='3e7ef8',paired_qualification_observed_tool_exit=0,
        paired_result_file=paired.relative_to(ROOT).as_posix(),paired_result_sha256=hashlib.sha256(paired.read_bytes()).hexdigest(),
        coordinate_diagnostic_observed_tool_chunk='f9749d',coordinate_diagnostic_observed_tool_exit=0,
        coordinate_result_file=coord.relative_to(ROOT).as_posix(),coordinate_result_sha256=hashlib.sha256(coord.read_bytes()).hexdigest(),
        actual_MRI_forwards=0,actual_MRI_training_updates=0,full_formal_training_observed_tool_exit=None,
        own_live_training_session=99542,publication_claim_confirmed=False,goal_status='active')
    with (ROOT/'SESSION_OBSERVED_EXITS_PAIRED_SAMPLING_FOV_2026-10-07.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,paired_exit=0,coordinate_exit=0)));return 0
if __name__=='__main__':raise SystemExit(main())
