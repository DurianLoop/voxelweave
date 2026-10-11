"""Report minimal fixed-plane diagnostic; no patient-generalization inference."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');folder=ROOT/'experiments/mc_rc_global_local_fixed_plane_fit_cpu'
    rp=folder/'attempt_01.json';qp=folder/'independent_metrics_and_plane_attempt_01.json'
    r,q=[json.loads(p.read_text(encoding='utf-8')) for p in (rp,qp)]
    assert r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and q['result_sha256']==sha(rp)
    e=r['evaluation'];m=e['metrics'];passed=e['fit_gate_passed'];assert q['fit_gate_passed_verified']==passed
    lines=['# 单012固定切面、完整tile覆盖的最小拟合结果','',
        f'仅已见开发患者012、第{r["z"]}原生plane，按前景z唯一排序取中位数；随机初始化原981,602参数架构、固定1000updates、无augmentation、全部16tile循环，每tile曝光125次。最后checkpoint按原完整FOV推断/概率回原生/.5，不给推断GT定位。',
        '', '| 2D native plane端点 | 结果 |','|---|---:|',
        f'| Dice | {m["dice"]:.9f} |',f'| recall | {m["recall"]:.9f} |',f'| precision | {m["precision"]:.9f} |',
        f'| absolute relative area error | {m["absolute_relative_volume_error"]:.9f} |',
        f'| TP / FP / FN | {m["tp"]} / {m["fp"]} / {m["fn"]} |',f'| 预写fit gate | {passed} |',
        '', '预写gate为plane Dice/recall≥.95、绝对相对面积误差≤.05，逐项：'+json.dumps(e['fit_gate_checks'])+'。独立原生label轴、bincount与另套完整plane重放通过；面积ratio不是完整3D体积/缺层能力。',
        '', ('最小固定切面可拟合，说明此架构/几何/优化链条能在这张训练例上达到预写门槛。多切面单病例和多患者失败仍有效；改变了z曝光、augmentation与tile覆盖，不能据此定位一个失败因子。下一步可单独控制采样覆盖/augmentation、充分曝光和whole-FOV训练。' if passed else '这一固定预算下最小切面仍未达到预写门槛；不能用高召回或低patch loss宣称能力通过。下一步需另写优化/目标网格/容量控制，旧失败门槛和分数不改变。'),
        '', f'生产global/local调用{r["global_forward_calls"]}/{r["local_forward_calls"]}；独立完整plane重放{q["global_forward_calls"]}/{q["local_forward_calls"]}。GPUfalse、确认/验证/隐藏MR未开。单切面训练结果不作独立科学确认，goal active。',
        '', '[协议](MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_PROTOCOL_2026-10-03.md)、[原始生产](experiments/mc_rc_global_local_fixed_plane_fit_cpu/attempt_01.json)、[独立核验](experiments/mc_rc_global_local_fixed_plane_fit_cpu/independent_metrics_and_plane_attempt_01.json)。']
    out=ROOT/'MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_RESULT_2026-10-03.md';assert not out.exists();out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    pp=folder/'report_provenance.json';assert not pp.exists()
    pp.write_text(json.dumps(dict(script_sha256=sha(__file__),report=out.relative_to(ROOT).as_posix(),report_sha256=sha(out),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (rp,qp)],training_updates=1000,
        native_fixed_plane=r['z'],fit_gate_passed=passed,scientific_confirmation_patients=0,publication_claim_confirmed=False),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report=str(out),plane_fit_gate_passed=passed,plane_dice=m['dice'])))
if __name__=='__main__':main()
