"""Save actual completed evidence, reading provenance, and progress-only snapshot."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, obj):
    with Path(path).open('x',encoding='utf-8') as f:
        f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def markdown(path, lines):
    with Path(path).open('x',encoding='utf-8') as f:
        f.write('\n'.join(lines)+'\n')
def main():
    ledger = read(ROOT/'literature/source_cache/mc_rc_007_010_native_headers_2026-10-02/attempt_01.json')
    labels = read(ROOT/'experiments/mc_rc_007_010_native_label_gate/attempt_01.json')
    proof = read(ROOT/'experiments/mc_rc_007_010_native_label_gate/independent_raw_geometry_grid_verification.json')
    visibility = read(ROOT/'experiments/mc_rc_label_anchor_visibility/attempt_01.json')
    visibility_proof = read(ROOT/'experiments/mc_rc_label_anchor_visibility/independent_label_phase_verification.json')
    if proof['errors'] or visibility_proof['errors']:
        raise ValueError('Independent evidence verification not passed')
    lines = ['# 007/009/010七系列来源与标签联合资格结果','',
      '本批已完成固定7系列、527原DICOM头、全部7官方标签的检查及独立复核。6系列/3开发患者通过原生头与整数label-grid资格；007 MPR保留拒绝。没有新MR数组解码、模型推理、Dice或独立患者确认。', '',
      '[原合同](MC_RC_007_010_SOURCE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md)、[头索引](literature/source_cache/mc_rc_007_010_native_headers_2026-10-02/attempt_01.json)、[标签结果](experiments/mc_rc_007_010_native_label_gate/attempt_01.json)、[独立原头/标签复核](experiments/mc_rc_007_010_native_label_gate/independent_raw_geometry_grid_verification.json)。','',
      '| 患者/系列 | 标签前景体素 | grid角点误差mm | 联合资格 |','| --- | ---: | ---: | --- |']
    for row in labels['series']:
        lines.append('| %s / %s | %d | %.6f | %s |' %(row['patient'][-3:],row['description'],row['label_foreground_voxels'],row['grid']['max_corner_world_error_mm'],'通过' if row['header_and_label_grid_preflight_passed'] else '拒绝：MPR'))
    lines += ['', '七条实际MR ZIP传输共134,734,262 bytes，API FileSize的261,941,288 bytes不是实际传输。新标签提取ZIP payload 2,308,969 bytes，名义数组总615,471,104 bytes，全部先核预算再用≤32MB slab读取。各标签finite、binary及原生整数grid均通过；MPR拒绝来自原生采集证据，标签grid正确不会消除该拒绝。', '',
      '独立复核实际重新读全部527头，以全矩阵lstsq重建IPP affine、固定4-plane slab核7标签，反解signed整数grid/角点/extent、核官方CSV/完整artifact联结和ZIP成员hash。errors=[]。这是独立来源实现复核，不是新的科学确认队列。', '',
      '截至此阶段三批24系列中15合格、9拒绝/pending，001/002/004/005/006/007/009/010共8位开发患者全部合格时间点纳入[覆盖诊断](MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md)。不把多时点当独立人数，不能按覆盖/性能删系列；下一新MR读取和表征实验见[准备](MC_RC_NEW_VISIBLE_REPRESENTATION_PREPARATION_2026-10-03.md)。']
    markdown(ROOT/'MC_RC_007_010_NATIVE_LABEL_RESULT_2026-10-03.md',lines)
    lines = ['# 四倍抽层标签覆盖：完全隐藏成分不能解释主条件失败','',
      '事前固定全部15合格系列、8开发患者、phase0主条件，另全部4phase与6/26连接规则。主phase0在两种规则下均无完全避开观测层的缺层标签成分。四个phase下每个系列的最大标签成分都接触观测层。此前001/005门控失败不能据此归因于完全隐藏病灶。', '',
      '[合同](MC_RC_LABEL_ANCHOR_VISIBILITY_PLAN_2026-10-03.md)、[逐系列/成分结果](experiments/mc_rc_label_anchor_visibility/attempt_01.json)、[输入hash合同](experiments/mc_rc_label_anchor_visibility/run_contract.json)、[独立label/slab/坐标复核](experiments/mc_rc_label_anchor_visibility/independent_label_phase_verification.json)。','',
      '| 患者/系列 | 26连接成分 | 主相位观测前景占有效范围 | 主相位隐藏成分 |','| --- | ---: | ---: | ---: |']
    for row in visibility['series']:
        lines.append('| %s / %s | %d | %.2f%% | %d |' %(row['patient'][-3:],row['description'],row['topology']['26']['components'],100*row['phases'][0]['fraction_supported_on_anchors'],row['topology']['26']['phases'][0]['anchor_absent_components']))
    lines += ['', '预写相位敏感性：26连接在phase1/2/3各有1个隐藏成分，均来自010 FIESTA-C的同一个48体素成分（约2.967mm³），位于native z=32单plane，并触及column视野边界。不能未经标签语义检查把它称独立临床病灶或漏诊，也不能删除后另报成功。6连接在phase1/2/3各有2个，主要成分仍全部接触观测。主相位结论保持。','',
      '独立验证errors=[]，从全部原标签slab显式映射并检查787,030前景坐标、所有native plane counts、15×4×2的phase/成分计数、bbox及6对26分割细化关系。连通生成本身仍来自SciPy，未独立重写算法。全部标签来源属于开发，独立患者科学确认仍0。','',
      '观测前景比例只是体素几何比例，不是实际MRI病灶可视性或检测概率；采集厚度/profile不由spacing确定。该反证不否定其他疾病的薄层检出收益，也不保证边界可由稀疏输入恢复。下一步先测理想观测区域传播，再考虑稀疏MR导出的预测区域/边界特征，保留强对照与未见确认。']
    markdown(ROOT/'MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md',lines)
    acquisition = ROOT/'literature/source_cache/anchor_visibility_fulltexts_2026-10-03/attempt_01.json'
    records = []
    for row in read(acquisition)['papers']:
        path = acquisition.parent/row['text_file']
        records.append(dict(paper=row['title'],doi=row['expected_doi'],source_xml=(acquisition.parent/row['raw_file']).relative_to(ROOT).as_posix(),source_sha256=row['raw_sha256'],text_file=path.relative_to(ROOT).as_posix(),text_sha256=sha(path),actual_reading_completed=True,paragraphs_read=row['paragraphs'],paragraph_range_zero_based=[0,row['paragraphs']-1],supplementary_read=False,figures_visually_inspected=False))
    images = [ROOT/'literature/source_cache/constrained_oracle_reading_2026-10-02/SafeRestore_2026_page_5.png', ROOT/'literature/source_cache/constrained_oracle_reading_2026-10-02/2025_MoEDiff-SR_Mixture_of_Experts-Guided_Diffusion_Model_for_Region-Adaptive_MRI_SR_page_4.png']
    write(acquisition.parent/'reading_provenance.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),record_script_sha256=sha(__file__),acquisition_index_sha256=sha(acquisition),report='literature/2026-10-03_anchor_visibility_fulltext_reading.md',new_public_fulltexts_read=2,papers=records,existing_PDF_method_pages_rechecked=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in images],learning_or_network_replication=False))
    queue = ROOT/'experiments/vs_seg_full_volume_queue'
    status = read(ROOT/'experiments/vs_seg_full_volume_cohort/status.json')
    driver = read(queue/'attempt_01.json')
    write(ROOT/'literature/source_cache/mc_rc_anchor_queue_observation_2026-10-03.json',dict(observed_utc=datetime.now(timezone.utc).isoformat(),unified_exec_session=83910,poll_returned_live=True,poll_evidence='Actual write_stdin session83910 returned live before this read; snapshot is historical only',script_sha256=sha(__file__),contract_sha256=sha(ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'),active_stage=driver['active_stage'],driver_complete=driver['complete'],complete_main_patients=status['complete_main_patients'],fixed_main_denominator=status['fixed_main_denominator'],completed_conditions=status['completed_conditions'],main_complete=status['main_complete'],secondary_complete=status['secondary_complete'],dynamic_subcohort_statistics_computed=False,scientific_goal_complete=False,historical_inference_log_tail=(queue/'inference_attempt_01.log').read_text(encoding='utf-8',errors='replace').splitlines()[-3:]))
    print(json.dumps(dict(source_series=7,source_qualified=6,visibility_series=15,development_patients=8,new_fulltexts_read=2,source_errors=proof['errors'],visibility_errors=visibility_proof['errors'],queue_stage=driver['active_stage'],queue_main_complete=status['main_complete'],completed_conditions=status['completed_conditions'])))
if __name__=='__main__':
    main()
