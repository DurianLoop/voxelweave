"""Independent native HTML-cell arithmetic; preserve discrepancies without guessing cause."""
import gzip,json,re,time
from html.parser import HTMLParser
from decimal import Decimal as D
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,entry,bind,dump
class Tables(HTMLParser):
 def __init__(self,wanted):
  super().__init__(convert_charrefs=True);self.wanted=wanted;self.active=False;self.rows=[];self.row=None;self.cell=None;self.skip=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='table' and a.get('id')==self.wanted:self.active=True
  if not self.active:return
  if tag=='tr':self.row=[]
  if tag in ('td','th'):self.cell=[]
  if tag=='annotation':self.skip+=1
 def handle_data(self,data):
  if self.active and self.cell is not None and not self.skip:self.cell.append(data)
 def handle_endtag(self,tag):
  if not self.active:return
  if tag=='annotation':self.skip-=1
  if tag in ('td','th') and self.cell is not None:
   self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
  if tag=='table':self.active=False
def table(folder,ident):
 p=folder/'primary.html.gz';t=Tables(ident);t.feed(gzip.decompress(p.read_bytes()).decode('utf-8'));assert t.rows
 return t.rows
def num(v):
 a=re.findall(r'[-+]?\d+(?:\.\d+)?',v.replace(',',''));assert len(a)==1,(v,a);return D(a[0])
start=time.perf_counter();before=guard(start);sw=HERE/'foundation_primary_html_attempt01/swin_pretraining';bs=HERE/'brainsegfounder_identity_html_attempt02'
ids=['S1.T1.2','S1.T3.2.1','S2.T4.2.1','S2.T5.2','S5.T7.2','S5.T8.2.1','S5.T9.2']
native={ident:table(bs,ident) for ident in ids};native['swin_A2.T1.3.1']=table(sw,'A2.T1.3.1')
means=[]
for ident in ('S2.T4.2.1','S2.T5.2','S5.T8.2.1','S5.T9.2'):
 rows=native[ident];samples=[r for r in rows if r and (r[0].startswith('Fold ') or r[0] in ('1','2','3','4','5'))];avg=next(r for r in rows if r[0]=='Average');assert len(samples)==5
 for col in range(1,len(avg)):
  values=[num(r[col]) for r in samples];computed=sum(values)/5;reported=num(avg[col]);precision=-reported.as_tuple().exponent
  # Bound includes rounding of each printed sample AND the printed mean.
  tolerance=D('0.5')*(D(10)**(-precision))+sum(D('0.5')*(D(10)**v.as_tuple().exponent) for v in values)/5
  means.append(dict(table=ident,column=col,values=[str(v) for v in values],mean_from_printed_values=str(computed),reported_mean=str(reported),reported_minus_computed=str(reported-computed),rounding_bound=str(tolerance),discrepancy_exceeds_printed_rounding=abs(reported-computed)>tolerance))
swrows=native['swin_A2.T1.3.1'][1:];assert len(swrows)==5
counts=[]
for row in swrows:
 assert len(row)==5,row
 train,val=[D(v) for v in row[4].split('/')];total=num(row[2]);assert total==train+val
 counts.append(dict(dataset=row[0],total=int(total),train=int(train),validation=int(val)))
sums={key:sum(v[key] for v in counts) for key in ('total','train','validation')}
assert sums==dict(total=5010,train=4761,validation=249)
swblocks=json.loads(gzip.decompress((sw/'blocks.json.gz').read_bytes()));bsblocks=json.loads(gzip.decompress((bs/'blocks.json.gz').read_bytes()))
swtext=[swblocks[i] for i in (51,58,73,90,97,128)];bstext=[bsblocks[i] for i in (53,54,56,58,80)]
assert '450K' in swblocks[58]['text'] and '45K' in swblocks[128]['text'] and 'from scratch' in swblocks[73]['text']
t4={r[0]:r for r in native['S2.T4.2.1'] if r};t8={r[0]:r for r in native['S5.T8.2.1'] if r}
cross=[dict(label='one_stage_small_Fold2',table4=t4['Fold 2'][2],table8=t8['Fold 2'][6]),dict(label='two_stage_small_Fold5',table4=t4['Fold 5'][1],table8=t8['Fold 5'][3])]
assert cross[0]['table4']=='0.9055' and cross[0]['table8']=='0.9186'
stage1_subject=num(next(r for r in native['S1.T3.2.1'] if 'Stage 1' in ' '.join(r))[3])
assert stage1_subject==43369
out=HERE/'foundation_table_arithmetic_attempt01';out.mkdir(exist_ok=False)
sources=[entry(Path(__file__)),entry(HERE/'resource_guard_v1.py')]+[entry(folder/n) for folder in (sw,bs) for n in ('primary.html.gz','blocks.json.gz','tables.json.gz')]
result=dict(complete=True,errors=[],source_bindings=sources,native_HTML_cells=native,fold_means=means,cross_table_differences=cross,
 Swin_pretraining_counts=counts,Swin_sum_from_native_cells=sums,Swin_reported_total=5050,Swin_reported_total_minus_table_sum=40,
 Swin_reported_iterations_main=450000,Swin_reported_iterations_appendix=45000,Swin_claimed_pretraining_GPU_days_approximately=6,
 BrainSegFounder_Table1_subjects=41400,BrainSegFounder_Table3_stage1_subjects=int(stage1_subject),BrainSegFounder_difference=1969,
 BrainSegFounder_ATLAS_Table1_and_Table3=655,BrainSegFounder_ATLAS_section_text=665,BrainSegFounder_ATLAS_difference=10,
 BrainSegFounder_ATLAS_stage2_table_LR='3e-3',BrainSegFounder_ATLAS_stage2_text_LR='5e-3',
 Swin_contract_text=swtext,BrainSegFounder_ATLAS_contract_text=bstext,
 source_discrepancy_cause_inferred=False,author_results_reproduced=False,statistical_significance_inferred=False,
 medical_effect_scored=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,CPU_optimizer_updates=0,GPU_calls=0,
 publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
for b in sources:bind(b)
dump(out/'receipt.json',result)
print(json.dumps(dict(complete=True,Swin_counts=sums,Swin_total_discrepancy=40,cross_table_differences=cross,fold_mean_discrepancies=[v for v in means if v['discrepancy_exceeds_printed_rounding']],BrainSegFounder_subject_difference=1969,BrainSegFounder_ATLAS_count_difference=10),ensure_ascii=False))
