"""Update navigation and produce a local review package; never submits anything."""
from common import *
import zipfile

def write(p,t):p.write_text(t,encoding='utf-8')

write(PAPER/'README.md','''# MRI 层间插值双论文项目

当前 CVPR 科学版本为 **Plan 17（2026-09-11）**：共享测量影响框架、条件协方差命题、Algorithm 1、真实误差图和完整证据审计。TMI 保持 Plan 15 科学证据与 Plan 16 图稿版本。

| 文档 | 当前 PDF | 内容 |
|---|---|---|
| CVPR 正文 | [main.pdf](CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) | 8 页；技术内容止于第 7 页；4 张核心图、2 张主表 |
| CVPR 补充 | [supplement.pdf](CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf) | 20 页；审计、推导、失败评分、完整 baseline 和预算分析 |
| TMI 正文 | [main.pdf](TMI/TMI_ARCH_GENERALIZED/main.pdf) | 11 页；本轮未改动 |
| TMI baseline 补充 | [baseline_supplement.pdf](TMI/TMI_ARCH_GENERALIZED/baseline_supplement.pdf) | 5 页；本轮未改动 |

Plan 17 修正历史影响量公式描述、前瞻性措辞及排序估计对象，新增去自比较敏感性。唯一 acquired-only guard 未证实优越性；0 阳性内部评价与每配对仅 2 阳性的 IXI 结果完整保留，不声称真正未触及确认。没有新增训练或外部投稿。

## 当前入口

- [详细中文报告](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/FINAL_REPORT_ZH.md)
- [三位严格审稿人、自评和最高价值后续实验](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/HOSTILE_REVIEW_ZH.md)
- [证据审计](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/research_audit.md)、[研究台账](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/research_ledger.json)、[实验登记](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/experiment_registry.csv)
- [主张证据矩阵](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/claim_evidence_matrix.md)、[运行说明](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/RUN_COMMANDS_ZH.md)
- [保护和构建验证](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/outputs/final_verification.json)
- [本地审阅包](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/delivery/CVPR_PLAN17_REVIEW_PACKAGE.zip)

## 既有 baseline 和历史版本

13 模型、111 配置、555 指标值、3,735 行病例结果继续全部使用；CVPR 完整主表和 20 项预算分析现在位于补充材料，TMI 保持原位置。15 项预算 MAE 同时区间支持改善、5 项跨零；13 个重建 baseline 不等于 13 架构物理干预验证。原生全平面指标与共同支撑 QA 不混算。

- [Plan 15 完整 baseline 整合报告](PLAN15_BASELINE_INTEGRATION/FINAL_REPORT_ZH.md)、[逐方法使用情况](PLAN15_BASELINE_INTEGRATION/BASELINE_USE_MAP_ZH.md)
- [Plan 16 历史图稿报告](PLAN16_RESEARCH_DIAGRAMS/FINAL_REPORT_ZH.md)
- [Plan 14 报告](PLAN14_SCIENTIFIC_STRENGTHENING/FINAL_REPORT_ZH.md)、[Plan 13 报告](PLAN13_EVIDENCE_UPGRADE/FINAL_REPORT_ZH.md)
- [Plan 12 报告](ARCHIVE/PLANS/PLAN12_STRICT_REVIEW_ITERATION/STRICT_REVIEW_ITERATION_REPORT_ZH.md)

所有新产物保存在 paper 内。Plan 17 改稿前的 162 个文件由快照保护，根 README、原始数据和 TMI 未改动。A 类提交资料由用户处理；当前仍是研究候选稿，不能给出可校准的录用概率。
''')
write(PAPER/'CVPR/README.md','''# CVPR 当前论文

**Plan 17，2026-09-11。** [正文 8 页](CVPR_ARCH_GENERALIZED/PAPER/main.pdf)，技术内容止于第 7 页；[补充材料 20 页](CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf)。

本轮将论文重构为 Measurement-Influence Reliability Audit：Algorithm 1、条件协方差命题、真实共享/不共享误差图、五架构证据和完整审计。修正影响量描述并剔除主分析的自比较；旧结果仍在补充材料。新 guard 未证实优越性，没有被包装为成功方法。

13 模型、111 配置、全部五指标和 20 项训练预算对照完整保留在补充材料。当前定性图为真实推理结果；Plan 16 旧生成图与改稿前文件可在保护快照中找到。

[详细报告](../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/FINAL_REPORT_ZH.md) · [审稿风险](../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/HOSTILE_REVIEW_ZH.md) · [运行说明](../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/RUN_COMMANDS_ZH.md) · [证据台账](../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/research_ledger.json)
''')
CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
write(CV/'FINAL_BUILD_AUDIT.md','''# CVPR Plan 17 最终构建审计

2026-09-11：正文 8 页（技术内容止于第 7 页）、补充材料 20 页。正文完成 pdflatex → bibtex → pdflatex ×2；补充材料完成多遍 pdflatex。两文档无 LaTeX error、未定义引用或 overfull 警告。28 页均已渲染并检查，变更页面与关键图另作整页核对。

正文围绕共享测量影响框架，包含真实 MRI 定性图、Algorithm 1、条件命题、四张核心图和两张主表。13 模型全 baseline 与 20 项预算分析在补充材料完整保留。评分负结果和未触及确认集缺失均已披露。

[中文报告](../../../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/FINAL_REPORT_ZH.md) · [构建记录](../../../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/build_logs/build_audit.json) · [文件保护核验](../../../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/outputs/final_verification.json)

本轮 TMI 原有文件未改动；Plan 16 旧图稿及其审计由 Plan 17 原快照保护。
''')
print('Current navigation updated; call final_verify.py before packaging.',flush=True)

if __name__=='__main__':
 import subprocess,sys
 subprocess.run([sys.executable,'-B',str(P/'scripts/final_verify.py')],check=True)
 delivery=P/'delivery';delivery.mkdir(exist_ok=True)
 # Include source/PDF/evidence; exclude build products, snapshots and rendered pages.
 selected=[]
 for p in CV.rglob('*'):
  if p.is_file() and p.suffix.lower() in {'.tex','.bib','.cls','.sty','.bst','.pdf','.png','.jpg','.csv','.md','.bbl'}:selected.append(p)
 for p in P.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(P)
  if rel.parts[0] in {'original_snapshot','delivery','final_page_renders','build_logs'}:continue
  if p.suffix.lower() in {'.md','.tex','.py','.csv','.json','.npz','.pdf','.png','.diff','.txt'}:selected.append(p)
 for n in ['build_audit.json','cvpr_final.log','supplement_final.log']:selected.append(P/'build_logs'/n)
 records=[{'path':p.relative_to(PAPER).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(selected))]
 manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records,'scope':'Local review package, not an anonymous submission bundle. Includes provenance paths and illustrative derived arrays; no checkpoints or full MRI volumes.'}
 write(delivery/'artifact_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 archive=delivery/'CVPR_PLAN17_REVIEW_PACKAGE.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for r in records:z.write(PAPER/r['path'],r['path'])
  z.write(delivery/'artifact_manifest.json','artifact_manifest.json')
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for r in records:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
 write(delivery/'package_verification.json',json.dumps({'archive':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'files':len(records)+1,'all_member_hashes_verified':True},indent=2))
 print('Package verified:',archive,'files',len(records)+1,'bytes',archive.stat().st_size,flush=True)
