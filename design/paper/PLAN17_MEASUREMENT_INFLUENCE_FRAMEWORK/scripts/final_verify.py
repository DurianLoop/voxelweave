"""Read-only source/protection checks; writes only this iteration's audit output."""
from common import *
import difflib

def main():
 checks=[]
 def record(name,ok,**detail):
  checks.append({'check':name,'passed':bool(ok),**detail})
  print(name, bool(ok), flush=True)
 def compare(records,base):
  return [r['path'] for r in records if not (base/r['path']).is_file() or sha(base/r['path'])!=r['sha256']]
 original=json.loads((P/'original_manifest.json').read_text(encoding='utf-8'))['files']
 bad=compare(original,P/'original_snapshot')
 record('all_original_snapshot_bytes_preserved',not bad,files=len(original),mismatches=bad)
 tmi=[r for r in original if r['path'].replace('\\','/').startswith('design/paper/TMI/')]
 bad=compare(tmi,ROOT);record('entire_original_TMI_tree_unchanged',not bad,files=len(tmi),mismatches=bad)
 root=[r for r in original if r['path']=='README.md']
 record('root_README_unchanged',not compare(root,ROOT))
 source=json.loads((OUT/'source_inventory.json').read_text(encoding='utf-8'))
 csvs=[r for r in source if r['path'].lower().endswith('.csv')]
 bad=compare(csvs,ROOT);record('all_historical_paper_CSV_bytes_unchanged',not bad,files=len(csvs),mismatches=bad)
 assets=[r for r in original if '/CVPR/' in r['path'].replace('\\','/') and any('/'+a+'/' in r['path'].replace('\\','/') for a in ['figures','tables','data'])]
 bad=compare(assets,ROOT);record('original_CVPR_figure_table_data_assets_unchanged',not bad,files=len(assets),mismatches=bad)
 baseline=json.loads((PAPER/'PLAN15_BASELINE_INTEGRATION/outputs/source_manifest.json').read_text(encoding='utf-8'))
 rows=[baseline['master']]+baseline['summary_files']
 bad=compare(rows,ROOT);record('experiment_master_and_native_summary_sources_unchanged',not bad,files=len(rows),mismatches=bad)
 inputs=json.loads((OUT/'neural_score_manifest.json').read_text(encoding='utf-8'))['inputs']
 bad=compare(inputs,ROOT);record('new_neural_experiment_inputs_unchanged',not bad,files=len(inputs),mismatches=bad)
 frozen=json.loads((OUT/'development_freeze.json').read_text(encoding='utf-8'))
 form=json.loads((OUT/'score_formula_freeze.json').read_text(encoding='utf-8'))
 record('new_score_protocol_hash_bindings',frozen['protocol_sha256']==form['protocol_sha256']==sha(P/'PROTOCOL.md'))
 score=pd.read_csv(OUT/'score_evaluation.csv');delta=pd.read_csv(OUT/'score_paired_deltas.csv');ds=delta.query("dataset=='ixi'")
 record('zero_positive_internal_eval_not_given_AP',score.query("dataset=='fastmri'").auprc.isna().all() and (score.query("dataset=='fastmri'").positives==0).all())
 record('all_12_transfer_guard_comparisons_cross_zero',len(ds)==12 and (ds.simultaneous_low<=0).all() and (ds.simultaneous_high>=0).all(),comparisons=len(ds))
 ns=pd.read_csv(OUT/'nonself_influence_summary.csv')
 record('six_nonself_alignment_advantages_simultaneously_positive',len(ns)==6 and (ns.simultaneous_low>0).all(),strata=len(ns))
 fw=json.loads((OUT/'framework_verification.json').read_text());pr=json.loads((OUT/'proposition_verification.json').read_text())
 record('framework_contract_and_proposition_checks',all(v for v in fw.values() if isinstance(v,bool)) and pr['all_mc_checks_pass'])
 build=json.loads((P/'build_logs/build_audit.json').read_text())
 record('two_PDFs_build_without_errors_or_overfull',len(build)==2 and all(r['success'] and not r['issues'] for r in build),documents=build)
 record('rendered_all_final_PDF_pages',len(list((P/'final_page_renders').glob('cvpr-*.png')))==8 and len(list((P/'final_page_renders').glob('supplement-*.png')))==20)
 current_changes=compare(original,ROOT)
 diffdir=P/'diffs';diffdir.mkdir(exist_ok=True)
 cv=Path('design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER')
 for name in ['main.tex','supplement.tex','p13_additional_analysis.tex','p14_additional_analysis.tex','p15_baseline_supplement.tex']:
  old=(P/'original_snapshot'/cv/name).read_text(encoding='utf-8').splitlines(True);new=(ROOT/cv/name).read_text(encoding='utf-8').splitlines(True)
  (diffdir/(name+'.diff')).write_text(''.join(difflib.unified_diff(old,new,fromfile='original/'+name,tofile='revised/'+name)),encoding='utf-8')
 report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_checks_passed':all(r['passed'] for r in checks),'checks':checks,'intentional_current_file_changes':current_changes,'scope':'Only recorded hashes can certify unchanged bytes; availability census is not a proof of an exhaustive historical chronology.'}
 save('final_verification.json',report)
 if not report['all_checks_passed']:raise SystemExit('Verification failed; inspect final_verification.json')

if __name__=='__main__':main()
