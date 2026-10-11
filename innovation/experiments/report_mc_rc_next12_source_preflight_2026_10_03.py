"""Export every fixed25 series and the extra physical-grid rejection."""
import csv,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_next12_label_grid';HEAD=ROOT/'literature/source_cache/mc_rc_next12_headers_2026-10-03'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');r=read(OUT/'attempt_01.json');h=read(HEAD/'attempt_01.json');q=read(OUT/'independent_all1475_headers_and_25_labels_attempt_01.json')
    assert r['complete'] and h['complete'] and q['complete'] and not r['errors'] and not h['errors'] and not q['errors']
    assert q['label_result_sha256']==sha(OUT/'attempt_01.json') and q['header_result_sha256']==sha(HEAD/'attempt_01.json')
    assert h['header_qualified_series']==22 and r['source_preflight_series_passed']==q['passed_series']==21
    byuid={x['source']['SeriesInstanceUID']:x for x in h['series']};rows=[]
    for x in r['series']:
        y=byuid[x['series_uid']]['summary'];reasons=list(x['header_qualification_fail_reasons'])
        if not x['grid']['same_native_grid']:reasons.append('label-native grid corner error exceeds fixed 0.05 mm')
        if not x['forms_consistent']:reasons.append('qform/sform discrepancy')
        rows.append(dict(patient=x['patient'],study_uid=x['study_uid'],series_uid=x['series_uid'],description=x['description'],
            dicom_planes=y['planes'],native_spacing_mm=' / '.join(f'{v:.9f}' for v in y['native_spacing_rcz_mm']),nominal_thickness_mm=' / '.join(map(str,y['slice_thicknesses_mm'])),
            acquisition_types=' / '.join(y['mr_acquisition_types']),header_qualified=x['header_qualified_candidate'],
            grid_corner_error_mm=x['grid']['max_corner_world_error_mm'],source_preflight_passed=x['header_and_label_grid_preflight_passed'],failure_reasons='; '.join(reasons),
            patient_role='await_predeclared_patient_allocation_and_model_training_identity; no task outcomes'))
    cp=OUT/'all25_source_qualification.csv';assert not cp.exists()
    with cp.open('x',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# 固定12患者、25系列：来源与标签网格结果','',
       '25/25官方MR ZIP下载实际exit 0，1,475原始对象，302,254,256传输字节，零自动重试。随后25标签语义/网格检查实际exit 0，独立重读全部1,475头/25标签也exit 0、errors=[]。全部12患者各至少有1个通过序列。','',
       '22/25系列通过非像素头资格，21/25通过头+标签网格：015一个DRIVE及031两个DRIVE头阴性；027的T2W_DRIVE_HR Tra头通过，但标签原生网格角点差0.054087070mm，超过原固定0.05mm，拒绝。该差异接近门槛仍不放宽，保留全部原名单与时点。','',
       '| 患者 | 序列描述 | 头资格 | 网格角点差mm | 最终源资格 |','| --- | --- | --- | ---: | --- |']
    for x in rows:lines.append(f"| {x['patient']} | {x['description']} | {x['header_qualified']} | {x['grid_corner_error_mm']:.9f} | {'通过' if x['source_preflight_passed'] else '未通过：'+x['failure_reasons']} |")
    lines+=['','[25完整CSV](experiments/mc_rc_next12_label_grid/all25_source_qualification.csv)、[标签生产记录](experiments/mc_rc_next12_label_grid/attempt_01.json)、[原始头与下载](literature/source_cache/mc_rc_next12_headers_2026-10-03/attempt_01.json)、[独立重读](experiments/mc_rc_next12_label_grid/independent_all1475_headers_and_25_labels_attempt_01.json)。','',
       '标签压缩成员累计6,313,485字节；按32MB分块读取，没有整批驻留。没有解码MR像素，没有导入torch，没有神经网络前向或GPU运行；没有对新患者计算方法效果。','',
       '连同上一批011/012/013，固定新增15患者、30系列，24系列源资格通过；患者角色和模型训练身份另审计。资格通过不等于任务能力、方法成功或未见患者科学确认。当前新claim仍0，旧8开发人及旧45队列不升级为确认。']
    rp=ROOT/'MC_RC_NEXT12_SOURCE_PREFLIGHT_RESULT_2026-10-03.md';assert not rp.exists();rp.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    prov=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),header_sha256=sha(HEAD/'attempt_01.json'),label_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_all1475_headers_and_25_labels_attempt_01.json'),outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (cp,rp)])
    (OUT/'report_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(series=25,header_passed=22,source_passed=21,source_patients=12,scientific_confirmation_patients=0)))
if __name__=='__main__':main()
