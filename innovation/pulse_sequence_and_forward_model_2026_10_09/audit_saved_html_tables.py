"""Independent streaming HTML cells + exact arithmetic on all published result rows."""
import sys,time,re,json
from pathlib import Path
from html.parser import HTMLParser
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard

class TableStream(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.article=False;self.tables=[];self.table=None;self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='article':self.article=True
        if not self.article:return
        if tag=='table':
            assert self.table is None
            self.table=dict(id=attrs.get('id'),rows=[])
        elif self.table is not None:
            if tag=='tr':assert self.row is None;self.row=[]
            elif tag in {'th','td'}:assert self.cell is None;self.cell=[]
            elif tag=='img' and self.cell is not None:self.cell.append(attrs.get('alt',''))
    def handle_endtag(self,tag):
        if tag=='article':self.article=False
        if self.table is None:return
        if tag in {'th','td'} and self.cell is not None:
            self.row.append(' '.join(' '.join(self.cell).split()));self.cell=None
        elif tag=='tr':
            assert self.cell is None;self.table['rows'].append(self.row);self.row=None
        elif tag=='table':
            assert self.row is None;self.tables.append(self.table);self.table=None
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)

def fraction(v):return dict(fraction=str(v),decimal=float(v))
def mean(v):return F(re.match(r'^\s*([0-9]+(?:\.[0-9]+)?)',v).group(1))
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    out=HERE/'table_audit_attempt01';out.mkdir(exist_ok=False)
    http=read(HERE/'primary_attempt01/HTTP_RECEIPT.json');tables={};sources=[]
    for key in ['psacnn','jointsr']:
        rec=next(v for v in http['records'] if v['key']==key);src=ROOT/rec['file']
        assert rec['complete'] and rec['HTTP_status']==200 and sha(src)==rec['sha256'] and src.stat().st_size==rec['bytes']
        parser=TableStream();parser.feed(src.read_text(encoding='utf-8'));tables[key]=parser.tables
        saved=HERE/('extraction_attempt02/'+key+'_tables.json');assert tables[key]==read(saved)
        sources.extend([src,saved])
    assert len(tables['psacnn'])==25 and len(tables['jointsr'])==14
    psdata=tables['psacnn'][21:];assert all(v['id'] is None for v in psdata) and len(psdata)==4
    ps=[]
    for number,table in enumerate(psdata,1):
        rows=table['rows'];names=rows[0][1:];regions=[]
        assert len(rows)==11 and names[-1]=='PSACNN'
        for row in rows[2:]:
            vals=[mean(v) for v in row[1:]];best=min(vals) if number<4 else max(vals)
            winners=[n for n,v in zip(names,vals) if v==best];p=vals[-1]
            regions.append(dict(region=row[0],methods={n:fraction(v) for n,v in zip(names,vals)},
                preferred_direction='lower' if number<4 else 'higher',best_methods=winners,
                PSACNN_strict_best=winners==['PSACNN'],PSACNN_tied_best='PSACNN' in winners and len(winners)>1))
        ps.append(dict(table=number,metric='repeated_acquisition_volume_coefficient_of_variation_percent' if number<4 else 'cross_contrast_automatic_segmentation_consistency_Dice',
            all9_regions=regions,strict_PSACNN_best=sum(v['PSACNN_strict_best'] for v in regions),
            tied_PSACNN_best=sum(v['PSACNN_tied_best'] for v in regions),manual_lesion_GT_accuracy=False))
    assert [v['strict_PSACNN_best'] for v in ps]==[5,5,6,6]
    assert [v['tied_PSACNN_best'] for v in ps]==[0,1,0,1]
    jsdata=tables['jointsr'][10:];assert len(jsdata)==4 and len(jsdata[0]['rows'])==2
    sr=[];volume=[];surface=[]
    for offset,spacing in zip([1,4,7],[3,5,7]):
        r=jsdata[1]['rows'];cubic,synth,sup=r[offset:offset+3]
        sr.append(dict(spacing_mm=spacing,printed_rows=[cubic,synth,sup],
            synth_minus_cubic_PSNR_dB=fraction(mean(synth[1])-mean(cubic[1])),synth_minus_cubic_SSIM=fraction(mean(synth[2])-mean(cubic[2])),
            synth_minus_supervised_PSNR_dB=fraction(mean(synth[1])-mean(sup[1])),synth_minus_supervised_SSIM=fraction(mean(synth[2])-mean(sup[2]))))
        r=jsdata[2]['rows'];cubic,synth,sup=r[offset+1:offset+4]
        assert cubic[0]==str(spacing)+' mm (cubic)' and 'SynthSR' in synth[0] and 'fully sup.' in sup[0]
        volume.append(dict(spacing_mm=spacing,printed_rows=[cubic,synth,sup],
            synth_minus_cubic_volume_error_percentage_points=fraction(mean(synth[1])-mean(cubic[1])),
            synth_minus_cubic_correlation=fraction(mean(synth[2])-mean(cubic[2])),
            synth_minus_cubic_Dice=fraction(mean(synth[3])-mean(cubic[3])),
            synth_minus_cubic_effect_size=fraction(mean(synth[4])-mean(cubic[4])),
            synth_minus_supervised_volume_error_percentage_points=fraction(mean(synth[1])-mean(sup[1]))))
    for col,spacing in zip([2,5,8],[3,5,7]):
        fields=[]
        for row in jsdata[3]['rows'][1:3]:
            cubic,synth,sup=[mean(row[j]) for j in [col,col+1,col+2]]
            fields.append(dict(metric=row[0],cubic_mm=fraction(cubic),synth_mm=fraction(synth),supervised_mm=fraction(sup),
                synth_minus_cubic_mm=fraction(synth-cubic),synth_minus_supervised_mm=fraction(synth-sup)))
        surface.append(dict(spacing_mm=spacing,errors=fields))
    blocks=read(HERE/'extraction_attempt02/jointsr_blocks.json');paragraph=blocks[121]['text']
    assert '2.7%' in paragraph and jsdata[2]['rows'][-1][1]=='2.8%'
    result=dict(complete=True,errors=[],all39_direct_HTML_tables_exact_cell_match=True,
        tables=dict(psacnn=dict(total_HTML_tables=25,formula_layouts=21,result_tables=4),jointsr=dict(total_HTML_tables=14,formula_layouts=10,hyperparameter_tables=1,result_tables=3)),
        psacnn_all_tables=ps,jointsr_all_SR_rows=sr,jointsr_all_hippocampus_rows=volume,jointsr_all_surface_errors=surface,
        jointsr_text121_vs_Table3_discrepancy=dict(context='7mm fully supervised hippocampal volume error',text='2.7%',table='2.8%',difference_percentage_points=fraction(F('2.8')-F('2.7')),source_not_repaired=True),
        significance_reconstructed_from_means=False,scanner_performance_or_manual_lesion_GT_inferred=False,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        elapsed_seconds=time.perf_counter()-started,resources=resource_guard(),source_bindings=[entry(p) for p in [Path(__file__),HERE/'TABLE_AUDIT_PROTOCOL.md',
            HERE/'primary_attempt01/HTTP_RECEIPT.json',HERE/'extraction_attempt02/jointsr_blocks.json',*sources]])
    dump(out/'receipt.json',result);assert time.perf_counter()-started<60 and (out/'receipt.json').stat().st_size<80000
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','psacnn_all_tables','jointsr_all_SR_rows','jointsr_all_hippocampus_rows','jointsr_all_surface_errors']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
