"""Archive the complete positive and negative source qualification with provenance."""
import csv,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_011_013_label_grid';HEAD=ROOT/'literature/source_cache/mc_rc_011_013_headers_2026-10-03'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    r=read(OUT/'attempt_01.json');h=read(HEAD/'attempt_01.json');q=read(OUT/'independent_all230_headers_and_5_labels_attempt_02.json');failed=read(OUT/'independent_all230_headers_and_5_labels.json')
    assert r['complete'] and h['complete'] and q['complete'] and not q['errors'] and q['label_result_sha256']==sha(OUT/'attempt_01.json') and q['header_result_sha256']==sha(HEAD/'attempt_01.json')
    assert not failed['complete'] and failed['errors'] and failed['script_sha256']==sha(OUT/'verifier_failed_attempt_01.py.txt')
    byuid={x['source']['SeriesInstanceUID']:x for x in h['series']};rows=[]
    for x in r['series']:
        y=byuid[x['series_uid']]['summary'];rows.append(dict(patient=x['patient'],study_uid=x['study_uid'],series_uid=x['series_uid'],description=x['description'],
            dicom_planes=y['planes'],native_spacing_mm=' / '.join(f'{v:.9f}' for v in y['native_spacing_rcz_mm']),nominal_thickness_mm=' / '.join(map(str,y['slice_thicknesses_mm'])),
            acquisition_types=' / '.join(y['mr_acquisition_types']),original_no_derived=y['original_no_derived'],header_qualified=x['header_qualified_candidate'],
            header_fail_reasons='; '.join(x['header_qualification_fail_reasons']),grid_corner_error_mm=x['grid']['max_corner_world_error_mm'],label_foreground_voxels=x['label_foreground_voxels'],
            source_preflight_passed=x['header_and_label_grid_preflight_passed'],patient_role='pending_patient_identity_and_split_no_model_effects_computed'))
    csvpath=OUT/'all5_source_qualification.csv'
    with csvpath.open('x',encoding='utf-8',newline='') as stream:w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# 固定011/012/013：5系列来源资格结果','',
           '按事前字典序规则固定3人全部5个候选series，230个DICOM对象。官方ZIP实际传输75,590,775字节，低于150,000,000上限；零重试。MR仅非像素头读取，未解码MR像素、未调用任务/SR模型或GPU。官方标签按块检查及独立逐层重读全部完成。','',
           '| 患者与描述 | 原生spacing rc/z（mm） | nominal thickness（mm） | 标签foreground体素 | 头+网格预检 |','| --- | --- | --- | ---: | --- |']
    for x in rows:lines.append(f"| {x['patient']} {x['description']} | {x['native_spacing_mm']} | {x['nominal_thickness_mm']} | {x['label_foreground_voxels']} | {'通过' if x['source_preflight_passed'] else '未通过：'+x['header_fail_reasons']} |")
    lines+=['', '3/5系列通过，分别来自011、012、013；013两个2D厚层时点未通过薄层3D合同，继续在完整分母报告，不改门槛或换患者。所有5标签binary、非空及来源网格检查都保存。3个通过系列仅是来源预检，不能叫3名科学确认患者。','',
            '独立复核实际重读全部230个DICOM非像素头和5个label，采用完整矩阵least-squares重算物理grid、inverse affine求整数轴变换和逐label平面计数；成功proof errors=[]。首次复核误加1e-4体素坐标容差，与事前0.05mm角点门槛不一致，011在约0.001126mm真实角点差下被误拒。保存首proof及原脚本，修正复核实现后另写attempt02；原下载和label结果没有改动或重跑。','',
            '[完整5series表](experiments/mc_rc_011_013_label_grid/all5_source_qualification.csv)、[标签资格记录](experiments/mc_rc_011_013_label_grid/attempt_01.json)、[全部头与传输来源](literature/source_cache/mc_rc_011_013_headers_2026-10-03/attempt_01.json)、[成功独立重读](experiments/mc_rc_011_013_label_grid/independent_all230_headers_and_5_labels_attempt_02.json)、[首失败proof](experiments/mc_rc_011_013_label_grid/independent_all230_headers_and_5_labels.json)。','',
            '身份与角色仍需完成：排除整个共享VS-SEG患者群（API有58共享PatientID，不只是overlap CSV的8条series）；已有8个开发患者全部时点归开发。源目录真实分母为71名候选/159series，减8人后63名/138series；继承摘要写成81候选不符合原记录，本轮使用71。此次新3人未读模型效果，尚未完成全项目身份交叉核验和训练/验证/确认split，保留pending角色。不能依据标签大小、模型能力或某时点的有利结果选确认病人。',
            '', '后续准备使用该预检结果审查任务训练来源；现官方checkpoint已在旧8开发人native能力失败，不能默认新来源任务能力。新训练需要相同容量、训练曝光/统计规则、完整未见患者角色以及独立任务端点。当前既未训练也未证明新方法收益。']
    report=ROOT/'MC_RC_011_013_SOURCE_PREFLIGHT_RESULT_2026-10-03.md';assert not report.exists();report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    prov=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),header_result_sha256=sha(HEAD/'attempt_01.json'),label_result_sha256=sha(OUT/'attempt_01.json'),successful_proof_sha256=sha(OUT/'independent_all230_headers_and_5_labels_attempt_02.json'),retained_failed_proof_sha256=sha(OUT/'independent_all230_headers_and_5_labels.json'),outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (report,csvpath)])
    (OUT/'report_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(series=5,passed_series=3,source_patients=3,scientific_confirmation_patients=0)))
if __name__=='__main__':main()
