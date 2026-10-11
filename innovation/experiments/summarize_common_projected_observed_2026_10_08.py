"""Describe the fully observed control result, retaining the failed original precision gate."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT/'experiments/common_projected_observed_qualification_2026_10_08/attempt01.json'
FAIL = ROOT/'experiments/common_projected_observed_independent_2026_10_08/attempt01.json'
VERIFY = ROOT/'experiments/common_projected_observed_independent_precision_v2_2026_10_08/attempt01.json'
DEST = ROOT/'experiments/common_projected_observed_summary_2026_10_08.json'
REPORT = ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not DEST.exists() and not REPORT.exists()
    p, f, v = map(read, (PROD, FAIL, VERIFY))
    assert p['complete'] and v['complete'] and not p['errors'] and not v['errors']
    assert all(p['gate'].values()) and all(v['gate'].values())
    assert not f['complete'] and len(f['series']) == 3 and f['medical_observed_packages_loaded'] == 4
    assert len(p['series']) == len(v['series']) == 19
    assert {s['uid'] for s in p['series']} == {s['uid'] for s in v['series']}
    bindings = [entry(x) for x in (PROD, FAIL, VERIFY, Path(__file__),
        ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md',
        ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PRECISION_V2_PROTOCOL_2026-10-08.md')]
    for result in (p, f, v):
        for b in result.get('source_bindings', []):
            assert sha(ROOT/b['path']) == b['sha256'], b['path']
        assert all(result[k] == 0 for k in ('model_arrays_loaded', 'neural_forwards', 'GPU_forwards', 'training_updates'))
        assert not result['io_audit']['prohibited_access_attempts']
    counts = sum(d['medical_observed_packages_loaded'] for d in (p, f, v))
    assert counts == 42
    projection_max = max(s['source_projection_check']['max_abs_error'] for s in v['series'])
    hermite_max = max(s['full_Hermite_check']['max_abs_error'] for s in v['series'])
    ideal_failed_series = sum(not s['ideal_coordinate_diagnostic']['original_allclose_passed'] for s in v['series'])
    ideal_failed_samples = sum(s['ideal_coordinate_diagnostic']['original_failed_samples'] for s in v['series'])
    old_equal = sum(s['original_direct_float32_diagnostic']['whole_field_bitwise_equal'] for s in v['series'])
    old_max = max(s['original_direct_float32_diagnostic']['max_abs_difference'] for s in v['series'])
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[], source_bindings=bindings,
             unique_development_patients=11, unique_development_series=19, observed_package_load_events=counts,
             successful_production_loads=19, retained_failed_independent_loads=4, successful_v2_independent_loads=19,
             maximum_float32_coordinate_projection_error=projection_max, maximum_full_Hermite_error=hermite_max,
             ideal_coordinate_original_tolerance_failed_series=ideal_failed_series,
             ideal_coordinate_original_tolerance_failed_samples=ideal_failed_samples,
             original_direct_full_field_bitwise_equal_series=old_equal,
             original_direct_full_field_max_abs_difference=old_max,
             original_v1_independent_gate_passed=False, original_v1_failure_retained=True,
             v2_operator_precision_gate_passed=True, tolerance_widened=False,
             full_execution_hash_replay_is_shared_library=True, independent_math_checks_distinguished=True,
             source_projection_math_is_sampled=True, Hermite_math_is_full_native_array=True,
             input_control_ready=True, official_task_training_started=False, actual_MRI_task_benefit_measured=False,
             native_GT_validation_confirmation_pixels_read=False, locked_IXI_opened=False,
             neural_forwards=0, GPU_forwards=0, training_updates=0,
             goal_status='active', publication_claim_confirmed=False)
    with DEST.open('x', encoding='utf-8') as out:
        json.dump(r, out, ensure_ascii=False, indent=2)
        out.write('\n')
    lines = ['# 共同投影 observed 输入控制：19 系列结果', '',
        '新模块已在全部 19 个开发系列／11 个患者完成生产资格与精度明确的独立 v2 核验。它让 direct 和 dense-PCHIP 从同一份 float32 投影后锚点出发，用作后续输入因素对照；尚没有分割、动作收益或临床结果。', '',
        f'生产作业 {p["elapsed_seconds"]:.6f}s；原独立作业 {f["elapsed_seconds"]:.6f}s、真实失败；独立 v2 {v["elapsed_seconds"]:.6f}s。共加载 observed 包 42 次（19+4+19），唯一医学系列19。新模型数组、神经/GPU forward、训练更新0；计数不包含原训练，也不把 hash 字节读取当数组加载。', '',
        '## 已核输入合同', '',
        '- 原全部 observed 统计先归一化，再 bilinear 投影 r/c；两路取同一个只读锚点对象，分支后不重估统计。',
        '- 原 local PCHIP 内部四锚点、首尾 linear fallback、tail 复制；direct 缺层 native z=0。共同 z-only map 和 padding。',
        '- availability 由原二值 native mask 构造，两路共享；全部19与旧资格 SHA 逐位一致。强度增强不修改 mask，padding为0。',
        '- 中间 rcz affine 使用面内 pixel-center map；最终和 padded zrc affine 与原 grid 在1e-12容差下一致。', '',
        '## 保留的数值失败与修正范围', '',
        '原 v1 独立核验在第4个已加载包失败，只有3系列完成。原因检查依赖已安装 ATen header；另建 v2 protocol、source、preregistration、attempt，不覆盖原记录。v2 在同一预定样点重现原失败，用显式 float32 坐标后通过；atol/rtol仍各3e-5。', '',
        f'v2 面内四角样点最大误差 {projection_max:.12g}；完整 native z 的独立 NumPy Hermite/linear/tail 最大误差 {hermite_max:.12g}。同库全数组执行 SHA 重放通过。前者是抽样数值核验、后者覆盖全部中间 dense 体素；同库 hash 重放不能冒称独立数学证明。', '',
        f'按原 ideal float64 坐标的同一3e-5 abs/rel门槛，{ideal_failed_series}/19系列存在失败样点，总{ideal_failed_samples}个；这些差异和失败点保留在 v2 JSON。新 direct 与原一次 trilinear direct 完整体积逐位相同 {old_equal}/19，最大绝对差 {old_max:.12g}。未证明完整体积理想坐标误差界、float32可逆或严格信息等价。旧 direct absolute 任务失败没有因此被改写。', '',
        '| 患者 | UID末12位 | 后端投影最大样点误差 | 完整Hermite最大误差 | 原ideal门槛失败样点 | 新/旧direct最大差 |',
        '|---|---|---:|---:|---:|---:|']
    for s in v['series']:
        lines.append(f'| {s["patient"]} | {s["uid"][-12:]} | {s["source_projection_check"]["max_abs_error"]:.3g} | {s["full_Hermite_check"]["max_abs_error"]:.3g} | {s["ideal_coordinate_diagnostic"]["original_failed_samples"]} | {s["original_direct_float32_diagnostic"]["max_abs_difference"]:.3g} |')
    lines += ['', '## 证据与接续', '',
        '- [原输入合同](COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md)、[精度v2合同](COMMON_PROJECTED_OBSERVED_INPUT_PRECISION_V2_PROTOCOL_2026-10-08.md)。',
        '- [新模块](experiments/mc_rc_common_projected_observed_2026_10_08.py)、[19系列生产](experiments/common_projected_observed_qualification_2026_10_08/attempt01.json)、[原独立失败](experiments/common_projected_observed_independent_2026_10_08/attempt01.json)、[独立v2](experiments/common_projected_observed_independent_precision_v2_2026_10_08/attempt01.json)、[汇总](experiments/common_projected_observed_summary_2026_10_08.json)。',
        '', '待原两臂完整预算、真实最后退出、原56FOV/6gates/strict完成后，将此控制加入同初始化、同容量、同训练监督和完整实测成本的任务因素矩阵；不提前训练、不以中间loss选择动作。', '',
        '本控制变更投影和插值顺序，是输入解释对照，不称新恢复算法、原native锚点保持、理论风险证书或已发表claim。确认患者、已见验证及locked IXI仍关闭；goal active。']
    with REPORT.open('x', encoding='utf-8') as out:
        out.write('\n'.join(lines)+'\n')
    print(json.dumps({k:r[k] for k in ('complete','observed_package_load_events','maximum_float32_coordinate_projection_error',
                    'maximum_full_Hermite_error','ideal_coordinate_original_tolerance_failed_series',
                    'ideal_coordinate_original_tolerance_failed_samples','original_direct_full_field_bitwise_equal_series',
                    'original_direct_full_field_max_abs_difference')}, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
