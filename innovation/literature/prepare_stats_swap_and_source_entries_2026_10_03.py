"""Append current navigation while retaining exact prior entry bytes."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/stats_swap_and_source_entry_snapshot_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=False)
    prefix='''**最新完成（统计互换与新来源，2026-10-03）：** [3篇原始PDF阅读](literature/2026-10-03_masked_normalization_primary_reading.md)、[三人6次CPU统计互换](TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md)、[45人无前向输入审计](FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md)、[011/012/013来源预检](MC_RC_011_013_SOURCE_PREFLIGHT_RESULT_2026-10-03.md)。三人主ΔDice +.0014103，小且异质，原三人post−raw为正与全45为负，不能外推。45人post std平均−2.4882%、相同anchors归一化scale平均+2.5525%，单调关联不足，不部署风险排序。新3人5series/230头与5label完成，3薄层series通过、2厚层时点陰性保留；未读模型效果，角色pending，科学确认0。归一化/掩膜/等变直接先例均保留，anchor-only只作控制。GPU/用户训练/locked IXI test未操作，全部本批进程已实际exit，goal active，尚无可发表新claim。[创新判断](INNOVATION_DECISION_AFTER_STATS_SWAP_2026-10-03.md)、[下一步准备](STATS_SWAP_AND_SOURCE_NEXT_PREPARATION_2026-10-03.md)、[本批记录](SESSION_UPDATE_STATS_SWAP_AND_SOURCE_2026-10-03.md)、[可见对话](SESSION_VISIBLE_DIALOGUE_STATS_SWAP_AND_SOURCE_2026-10-03.md)、[最新接续](SESSION_HANDOFF_STATS_SWAP_AND_SOURCE_2026-10-03.md)及[验收记录](SESSION_ARCHIVE_VERIFICATION_STATS_SWAP_AND_SOURCE_2026-10-03.json)为当前入口。以下live/未完成措辞是历史时点，不代表当前后台任务。

'''
    rows=[]
    for name in ('README.md','EXPERIMENT_QUEUE.md'):
        p=ROOT/name;before=p.read_bytes();snapshot=OUT/(name+'.before.txt');snapshot.write_bytes(before)
        body=before.decode('utf-8');split=body.split('\n',1);after=split[0]+'\n\n'+prefix+(split[1].lstrip('\n') if len(split)>1 else '')
        p.write_text(after,encoding='utf-8');rows.append(dict(path=name,before_file=snapshot.name,before_sha256=sha(snapshot),after_sha256=sha(p)))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),entries=rows)
    (OUT/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__':main()
