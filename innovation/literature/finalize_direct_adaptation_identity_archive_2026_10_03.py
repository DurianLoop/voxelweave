"""Refresh navigation and static/global receipts after all scientific work in this batch."""
import json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
entry='''**本次接续已完成：** [三篇新原始正文/152定向锚点](literature/2026-10-03_task_adaptation_direct_fulltext_reading.md)明确直接分割/分辨率随机化/跨视图伪标签/级联已有先例。[固定12新患者25系列源资格](MC_RC_NEXT12_SOURCE_PREFLIGHT_RESULT_2026-10-03.md)完成1,475原头/25标签及独立重读，21合格、4阴性；无MR像素或模型效果。[本地身份与事前分配候选](MC_RC_LOCAL_IDENTITY_AND_ALLOCATION_RESULT_2026-10-03.md)检查503,812文件名/23,432文本+14大CSV，11开发/4验证/8确认保留但科学split未启用。[创新判断](INNOVATION_DECISION_AFTER_DIRECT_ADAPTATION_READING_2026-10-03.md)、[后续对照准备](TASK_ADAPTATION_NEXT_TRIAL_PREPARATION_2026-10-03.md)、[本轮记录](SESSION_UPDATE_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md)、[接续入口](SESSION_HANDOFF_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md)与[验收](SESSION_ARCHIVE_VERIFICATION_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03_attempt_02.json)保存来源、失败、准备。全部本批进程实际exit，本批新前向0/GPU0/科学确认0，goal active，尚无可发表且独立确认claim。下方各历史“live/当前”仅描述其记录时点。

'''
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for name in ('README.md','EXPERIMENT_QUEUE.md'):
        p=ROOT/name;text=p.read_text(encoding='utf-8')
        if '**本次接续已完成：** [三篇新原始正文/152定向锚点]' not in text:p.write_text(entry+text,encoding='utf-8')
    path=ROOT/'SESSION_ARCHIVE_VERIFICATION_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03_attempt_02.json';assert not path.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),scope='This batch static provenance/link integrity plus refreshed global evidence manifest; not scientific confirmation',complete=False,errors=[],checks=[],new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for script,extra in [('literature/verify_direct_adaptation_and_identity_stage_2026_10_03.py',['--write']),('literature/verify_direct_adaptation_and_identity_stage_2026_10_03.py',[]),('verify_archive.py',['--write']),('verify_archive.py',[])]:
        cmd=[sys.executable,'-X','utf8','-B',str(ROOT/script)]+extra
        result=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        row=dict(script=script,args=extra,command=cmd,exit_code=result.returncode,output=result.stdout.decode('utf-8',errors='replace'))
        r['checks'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        if result.returncode:r['errors'].append(script+' failed');break
    r['complete']=len(r['checks'])==4 and not r['errors'];r['finished_utc']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
