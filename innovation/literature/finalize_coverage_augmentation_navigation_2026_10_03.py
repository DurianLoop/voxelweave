"""Prepend a UTF-8 current entry, preserving all historical navigation bytes in snapshots."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENTRY='''**最新接续（2026-10-03，覆盖×增强）：** [两篇原始正文累计205文字块](literature/2026-10-03_coverage_augmentation_followup_fulltext_reading.md)已读完；[单012四臂完整结果](MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_RESULT_2026-10-03.md)及16000draw/12完整plane独立核验全部结束。full Dice .865312/.965504/.747641/.914331，两个无增强臂过原fit gate，单训练患者/单seed，不作泛化claim。三新臂12000实际更新，GPU0/科学确认0。[19系列608draw/1216完整patch预检](experiments/mc_rc_no_augmentation_development_cpu_preflight/attempt_01.json)通过；新11开发固定20k无增强CPU训练 **session4831仍live**，[启动观测](literature/source_cache/no_augmentation_training_launch_observation_2026-10-03.json)时1200/20000，不重启也不称完成。[创新判断](INNOVATION_DECISION_AFTER_COVERAGE_AUGMENTATION_2026-10-03.md)、[后续准备](MC_RC_NO_AUGMENTATION_NEXT_TRIAL_PREPARATION_2026-10-03.md)、[阶段记录](SESSION_UPDATE_COVERAGE_AUGMENTATION_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_COVERAGE_AUGMENTATION_2026-10-03.md)、[接续入口](SESSION_HANDOFF_COVERAGE_AUGMENTATION_2026-10-03.md)保存全部本轮证据。尚无可发表且独立确认新claim，goal active；以下“当前/live”均指其历史记录时点。

'''


def main():
    for name in ('README.md','EXPERIMENT_QUEUE.md'):
        path=ROOT/name
        before=ROOT/'literature/source_cache/coverage_augmentation_entry_snapshot_2026-10-03'/(name+'.before')
        assert before.exists() and path.read_bytes()==before.read_bytes()
        path.write_bytes(ENTRY.encode('utf-8')+before.read_bytes())
    print('UTF-8 current navigation saved; original history preserved.')


if __name__=='__main__':
    main()
