"""Independent scalar/count/CSV proof using partition moments and manual correlations."""
import csv,hashlib,json,math,sys,traceback
from fractions import Fraction
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/full45_normalization_drift_cpu'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b,msg,rtol=1e-10,atol=1e-12):
    if not (a==b if a is None or b is None else math.isclose(a,b,rel_tol=rtol,abs_tol=atol)):raise ValueError(msg)
def ranks(x):
    order=sorted(range(len(x)),key=lambda i:x[i]);out=[None]*len(x);j=0
    while j<len(x):
        end=j+1
        while end<len(x) and x[order[end]]==x[order[j]]:end+=1
        for i in order[j:end]:out[i]=(j+1+end)/2
        j=end
    return out
def corr(x,y):
    mx=math.fsum(x)/len(x);my=math.fsum(y)/len(y);a=[v-mx for v in x];b=[v-my for v in y]
    return math.fsum(v*w for v,w in zip(a,b))/math.sqrt(math.fsum(v*v for v in a)*math.fsum(v*v for v in b))
def dice(x):
    den=2*x['tp']+x['fp']+x['fn'];return Fraction(2*x['tp'],den) if den else None
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=OUT/'independent_scalar_csv_and_correlations.json';assert not path.exists()
    r=read(OUT/'attempt_01.json');c=read(OUT/'run_contract.json')
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),
           complete=False,errors=[],patients_verified=0,domain_moment_cells_verified=0,same_image_affine_rms_verified=0,
           fraction_dice_deltas_verified=0,manual_correlations_verified=0,csv_rows_verified=0,new_neural_forwards=0,
           torch_imported=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,
           independence='Separate centered-moment RMS, manual Pearson and tied ranks, exact Fraction task deltas. Existing reconstruction replay and moment sums shared; no independent cohort/model.')
    try:
        assert r['complete'] and not r['errors'] and len(r['patients'])==45 and r['new_neural_forwards']==0
        assert sha(OUT/'run_contract.json')==r['run_contract_sha256']
        for e in c['files']:assert sha(ROOT.parent/e['path'])==e['sha256']
        rows=[]
        for e in r['patients']:
            assert sha(ROOT/e['file'])==e['sha256'];x=read(ROOT/e['file']);assert x['complete'] and not x['cuda_initialized']
            for s in x['source_bindings']:assert sha(ROOT/s['path'])==s['sha256']
            n=math.prod(x['shape']);indices=x['domain_indices'];assert sorted(z for zs in indices.values() for z in zs)==list(range(x['shape'][2]))
            for image,parts in x['domain_moments_float64'].items():
                assert sum(p['count'] for p in parts.values())==n
                full=x['full_moments_float64'][image]
                for domain,m in parts.items():
                    assert m['count']==x['shape'][0]*x['shape'][1]*len(indices[domain]);q['domain_moment_cells_verified']+=1
                    if m['count']:
                        close(m['mean'],m['sum']/m['count'],'Domain mean')
                        close(m['variance'],max(0.,m['sum_square']/m['count']-m['mean']**2),'Domain variance',atol=1e-8)
                close(full['mean'],math.fsum(p['sum'] for p in parts.values())/n,'Global mean',atol=1e-9)
                # Law of total variance; avoids subtracting two large full sums.
                variance=math.fsum(p['count']*(p['variance']+(p['mean']-full['mean'])**2) for p in parts.values() if p['count'])/n
                close(variance,full['variance'],'Total variance',atol=1e-8)
                st=x['statistics_ras_float32'][image]
                close(st['mean'],full['mean'],'Float32 mean unexpected drift',rtol=3e-6,atol=3e-5)
                close(st['std'],math.sqrt(variance),'Float32 std unexpected drift',rtol=3e-6,atol=3e-5)
            st=x['statistics_ras_float32'];mu,sd=st['raw']['mean'],st['raw']['std'];mp,sp=st['post']['mean'],st['post']['std']
            close(x['a_minus_one'],sd/sp-1,'a');close(x['b'],(mu-mp)/sp,'b');close(x['std_relative_change'],sp/sd-1,'std')
            for d in ('observed_anchors','unsupported_tail'):
                m=x['domain_moments_float64']['raw'][d];v=x['same_image_domains'][d]
                assert m==x['domain_moments_float64']['post'][d]
                if m['count']:
                    coefficient=1/sp-1/sd;offset=(m['mean']-mp)/sp-(m['mean']-mu)/sd
                    expected=math.sqrt(coefficient**2*m['variance']+offset**2)
                    close(v['rms_analytic_real'],expected,'Centered RMS',atol=1e-10)
                    close(v['rms_float32'],expected,'Float32 RMS',rtol=0,atol=2e-6)
                    assert v['max_affine_float32_roundoff']<4e-6
                else:assert v['rms_float32'] is None and v['rms_analytic_real'] is None
                q['same_image_affine_rms_verified']+=1
            raw=read(ROOT/'experiments/vs_seg_full_volume_cohort/patients'/x['patient']/'raw_pchip_attempt_01.json');post=read(ROOT/'experiments/vs_seg_post_resize_task_cpu'/(x['patient']+'.json'))
            assert raw['reconstructed_array_sha256']==x['raw_array_sha256'] and post['reconstructed_array_sha256']==x['post_array_sha256']
            for ref in c['references']:
                exact=dice(post['task_metrics'][ref]['full'])-dice(raw['task_metrics'][ref]['full'])
                close(float(exact),x['saved_full_dice'][ref]['post_minus_raw'],'Fraction Dice');q['fraction_dice_deltas_verified']+=1
            rows.append(x);q['patients_verified']+=1
        assert [x['patient'] for x in rows]==c['main_roster']
        for entry in r['associations']:
            a=[x[entry['feature']] for x in rows];b=[x['saved_full_dice'][entry['reference']]['post_minus_raw'] for x in rows]
            if entry['method']=='spearman':a,b=ranks(a),ranks(b)
            close(corr(a,b),entry['coefficient'],'Manual correlation');q['manual_correlations_verified']+=1
        for f,s in r['summary'].items():
            v=[x[f] for x in rows];close(math.fsum(v)/45,s['mean'],'Summary mean');close(min(v),s['minimum'],'Min');close(max(v),s['maximum'],'Max')
            assert s['pilot_values']=={x['patient']:x[f] for x in rows if x['patient'] in c['pilot_roster']}
        for ref,groups in r['cohort_dice'].items():
            for group,s in groups.items():
                selected=[x for x in rows if group=='full45' or (x['patient'] in c['pilot_roster'])==(group=='fixed_pilot3')]
                assert len(selected)==s['n'];close(math.fsum(x['saved_full_dice'][ref]['post_minus_raw'] for x in selected)/len(selected),s['mean'],'Cohort direction')
        p=ROOT/r['csv_file'];assert sha(p)==r['csv_sha256']
        with p.open(encoding='utf-8',newline='') as stream:csvrows=list(csv.DictReader(stream))
        assert len(csvrows)==45
        for x,y in zip(rows,csvrows):
            assert x['patient']==y['patient']
            for key in c['features']+['std_relative_change']:close(x[key],float(y[key]),'CSV feature')
            for ref in c['references']:close(x['saved_full_dice'][ref]['post_minus_raw'],float(y[ref+'_post_minus_raw_dice']),'CSV Dice')
            q['csv_rows_verified']+=1
        q['torch_imported']='torch' in sys.modules;assert not q['torch_imported'];q['complete']=True
    except Exception as exc:q['errors'].append(type(exc).__name__+': '+str(exc));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(q,ensure_ascii=False));return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
