"""Independently partition integer confusion counts and check all CSV values."""
import csv,hashlib,json,math,sys
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/anchor_pilot_boundary_decomposition_cpu'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');result=read(OUT/'attempt_01.json');records={};partitions={}
 for e in result['source_bindings']:
  path=ROOT/e['path'];assert sha(path)==e['sha256'];x=read(path);condition={'raw_pchip':'raw','post_resize_pchip':'post'}.get(x['condition'],x['condition']);records.setdefault(x['patient'],{})[condition]=x
  for ref,domains in x['task_metrics'].items():
   a=domains['full'];b=domains['exclude_reference_boundary_1mm']
   for domain in ('full','outside_1mm_band','excluded_1mm_band'):
    counts={k:(a[k] if domain=='full' else b[k] if domain=='outside_1mm_band' else a[k]-b[k]) for k in ('tp','fp','fn')};assert min(counts.values())>=0
    denom=2*counts['tp']+counts['fp']+counts['fn'];partitions[(x['patient'],condition,ref,domain)]=(counts,Fraction(2*counts['tp'],denom) if denom else None)
 def rows(name):
  with (OUT/name).open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))
 def close(a,b):assert math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12)
 condition_rows=rows('all108_condition_partitions.csv');paired=rows('all108_paired_partition_differences.csv');summaries=rows('all36_partition_summaries.csv')
 assert len(condition_rows)==len(partitions)==108 and len(paired)==108 and len(summaries)==36
 assert len({(x['patient'],x['comparison'],x['reference'],x['domain']) for x in paired})==108
 for x in condition_rows:
  c,d=partitions[(x['patient'],x['condition'],x['reference'],x['domain'])]
  assert all(int(x[k])==c[k] for k in c);close(x['dice'],d)
 grouped={}
 for x in paired:
  left,right=x['comparison'].split('-');a,ad=partitions[(x['patient'],left,x['reference'],x['domain'])];b,bd=partitions[(x['patient'],right,x['reference'],x['domain'])]
  assert all(int(x['delta_'+k])==a[k]-b[k] for k in a);close(x['delta_dice'],ad-bd)
  grouped.setdefault((x['comparison'],x['reference'],x['domain']),[]).append((ad-bd,{k:a[k]-b[k] for k in a}))
 for x in summaries:
  group=grouped[(x['comparison'],x['reference'],x['domain'])];assert len(group)==3;close(x['mean_delta_dice'],sum(d for d,c in group)/3)
  for k in ('tp','fp','fn'):close(x['mean_delta_'+k],Fraction(sum(c[k] for d,c in group),3))
 report=dict(complete=True,errors=[],script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),
  condition_partitions_verified=108,paired_rows_verified=108,summaries_verified=36,
  original_plan_count_expression_incorrect=True,correct_count='6 comparisons x 2 labels x 3 partitions x 3 patients = 108',
  independent_implementation='Integer subtraction, exact Fraction Dice and independent CSV readers; shared saved records, no independent labels/cohort.',
  new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
 path=OUT/'independent_partition_and_csv_verification.json';assert not path.exists();path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
