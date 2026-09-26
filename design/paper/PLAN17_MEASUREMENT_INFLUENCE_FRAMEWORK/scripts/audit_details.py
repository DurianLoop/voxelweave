from pathlib import Path
import json,ast,hashlib,datetime
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];PAPER=P.parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
ledger=json.loads((P/'research_ledger.json').read_text(encoding='utf-8'));used=[]
for ds,path in [('fastmri','PLAN9_ARCH_GENERALIZATION/scripts/p9_disjoint_shared.py'),('ixi','PLAN11_CLAIM_STRENGTHENING/scripts/p11_ixi_five_arch_clean.py')]:
 f=PAPER/'ARCHIVE/PLANS'/path;tree=ast.parse(f.read_text(encoding='utf-8'))
 node=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MODEL_SPECS' for t in n.targets))
 specs=eval(compile(ast.Expression(node),str(f),'eval'),{'ROOT':ROOT})
 for model,spec in specs.items():
  q=spec['checkpoint'];used.append({'dataset':ds,'model':model,'checkpoint':q.relative_to(ROOT).as_posix(),'exists':q.exists(),'sha256':sha(q) if q.exists() else None,'stored_predictions':spec['stored'].relative_to(ROOT).as_posix(),'source_code':f.relative_to(ROOT).as_posix()})
folds=[]
for d in sorted((ROOT/'dataset/NingXiaData/processed_saint_cv').glob('fold_*/splits/nifti_seed3407')):
 sets={s:set((d/f'{s}_cases.txt').read_text().split()) for s in ['train','val','test']}
 folds.append({'fold':d.parents[1].name,'sets':{k:sorted(v) for k,v in sets.items()},'overlaps':{a+'_'+b:sorted(sets[a]&sets[b]) for a,b in [('train','val'),('train','test'),('val','test')]}})
ledger['primary_neural_checkpoint_bindings']=used;ledger['ningxia_patient_fold_audit']=folds
ledger['critical_findings'].append('New source correction: HAT/SwinIR and Plan9 neural influence use sum of shared response inner products divided by all-anchor response energies, NOT mean of individual response cosines. Main and supplementary must use the actual formula.')
ledger['audit_completed_before_new_experiments_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(P/'research_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'bound_checkpoints':len(used),'all_exist':all(r['exists'] for r in used),'ningxia_folds':folds},ensure_ascii=False))
