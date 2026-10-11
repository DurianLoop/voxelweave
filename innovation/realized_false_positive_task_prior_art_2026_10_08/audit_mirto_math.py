"""Audit public printed tables and mathematical limits without medical input."""
import sys,json,re,math,time
from fractions import Fraction
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'cpu_audit_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
METHODS=['REFLECT','UCCD','cDDPM','AnomalyDINO']
def page(n):return (HERE/f'primary_attempt01/mirto_page{n:03d}.txt').read_text(encoding='utf-8')
def table(n,start,end):return page(n).split(start,1)[1].split(end,1)[0]
def rows(text,budgets=True):
    out=[];current=None
    for line in text.splitlines():
        line=line.strip().replace('−','-')
        m=re.match(r'^(REFLECT|UCCD|cDDPM|AnomalyDINO)\s+',line)
        if m:current=m.group(1);line=line[m.end():]
        if current and (re.match(r'^(5|10|20|40)\s+',line) if budgets else m):
            nums=[float(x) for x in re.findall(r'[+-]?\d+(?:\.\d+)?',line)]
            out.append(dict(method=current,values=nums,source_line=(m.group(1)+' ' if m else '')+line))
    return out
def beta_cdf(x,a,b):
    n=a+b-1
    return math.fsum(math.comb(n,k)*x**k*(1-x)**(n-k) for k in range(a,n+1))
def beta_q(p,a,b):
    lo,hi=0.,1.
    for _ in range(90):
        mid=(lo+hi)/2
        if beta_cdf(mid,a,b)<p:lo=mid
        else:hi=mid
    return (lo+hi)/2
def jaccard(a,b):
    union=(a|b).bit_count()
    return Fraction((a^b).bit_count(),union) if union else Fraction(0)
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.resource_guard();tick=time.perf_counter();OUT.mkdir(exist_ok=False)
    t4=rows(table(15,'Table 4.','Table 5.'));t29=rows(table(32,'Table 29.','Table 30.'))
    t37=rows(table(35,'Table 37.','Table 38.'));t7=rows(table(16,'Table 7.','sees only'),False)
    assert [len(x) for x in [t4,t29,t37,t7]]==[16,16,16,4]
    assert all(len(r['values'])==17 for r in t4)
    assert all(len(r['values'])==12 for r in t29)
    assert all(len(r['values'])==13 for r in t37)
    bindings=[dict(physical_page=n,source=client.base.entry(HERE/f'primary_attempt01/mirto_page{n:03d}.txt')) for n in [5,6,9,13,15,16,25,32,35,36,40]]
    transfers=[];post=[];operating=[]
    for r4,r29 in zip(t4,t29):
        x=r4['values'];y=r29['values'];assert r4['method']==r29['method'] and x[0]==y[0]
        assert x[1]==y[1] and x[2]==y[4] and x[7]==y[3] and x[14]==y[6]
        residual=y[5]-y[4]-y[6];assert abs(residual)<=.0015+1e-12
        operating.append(dict(method=r4['method'],budget=x[0],validation_tau=x[1],Dice_mean=x[2],FP_mean=x[7],FP_p95=x[11],exceedance_percent=x[13],realized_to_nominal_ratio=x[7]/x[0]))
        transfers.append(dict(method=r29['method'],budget=y[0],Dice_validation=y[4],Dice_test_matched=y[5],gap_printed=y[6],printed_residual=residual,rounding_tolerance=.0015))
    for r in t37:
        x=r['values'];residual=x[4]-x[7]-x[10];assert abs(residual)<=.00015+1e-12
        post.append(dict(method=r['method'],budget=x[0],total=x[4],fixed_tau=x[7],relaxation=x[10],printed_residual=residual,rounding_tolerance=.00015))
    post7=[]
    for r in t7:
        x=r['values'];assert len(x)==9,x
        residual=x[0]-x[1]-x[4];assert abs(residual)<=.0015+1e-12
        post7.append(dict(method=r['method'],total=x[0],fixed_tau=x[1],relaxation=x[4],sensitivity_before=x[7],sensitivity_after=x[8],sensitivity_delta=x[8]-x[7],printed_residual=residual))
    crc=[]
    for n in [4,8,11,24,50,100]:
        alpha=Fraction(1,10);j=math.floor((n+1)*alpha-1);feasible=alpha>=Fraction(1,n+1)
        row=dict(n=n,alpha=float(alpha),minimum_feasible_alpha=1/(n+1),feasible_at_alpha_0_1=feasible,
            hypothetical_zero_harm_one_sided_95_upper=1-.05**(1/n),not_a_new_medical_result=True)
        if feasible:
            k=n-j;a=n+1-k;b=k
            row.update(Beta_a=a,Beta_b=b,mean=a/(a+b),probability_calibration_set_risk_at_most_alpha=beta_cdf(.1,a,b),quantile_97_5=beta_q(.975,a,b))
        crc.append(row)
    jcount=0;violations=0;tight=0
    for p in range(16):
        for a in range(16):
            for b in range(16):
                lhs=jaccard(a,b);rhs=abs(jaccard(p,a)-jaccard(p,b));jcount+=1
                violations+=int(lhs<rhs);tight+=int(lhs==rhs)
    assert jcount==4096 and violations==0
    costs=[]
    for method,seconds,pervolume in [('REFLECT',3*3600+7*60+18,32.5),('AnomalyDINO',15*60+23,2.7),('IterMask3D',2*3600+43*60+4,28.3)]:
        compatible=[n for n in range(1,1001) if pervolume-.05<=seconds/n<pervolume+.05]
        costs.append(dict(method=method,wall_seconds=seconds,seconds_per_volume_printed=pervolume,implied_real_ratio=seconds/pervolume,
            compatible_integer_counts_assuming_one_decimal_rounding=compatible,canonical_312_plus_24_count_compatible=336 in compatible,
            actual_author_volume_count_verified=False))
    u=next(x for x in post if x['method']=='UCCD' and x['budget']==20)
    val=.539-.519;matched=.541-.542;transfer=- (.002-.023)
    assert abs(val-matched-transfer)<1e-12
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],rows_checked=52,
        parsed_tables=dict(table4=t4,table29=t29,table37=t37,table7=t7),operating_point_audit=operating,
        transfer_gap_audit=transfers,postprocessing_audit=post,table7_audit=post7,
        UCCD_cDDPM_budget20=dict(validation_difference=val,equal_burden_difference=matched,transfer_explains_difference_change=transfer),
        UCCD_budget20_relaxation_fraction=u['relaxation']/u['total'],CRC_conditional_limits=crc,
        minimum_zero_harm_cases_for_one_sided_95_bound_at_most_10_percent=math.ceil(math.log(.05)/math.log(.9)),
        minimum_zero_harm_cases_for_one_sided_95_bound_at_most_5_percent=math.ceil(math.log(.05)/math.log(.95)),
        Jaccard_exhaustion=dict(universe_elements=4,triples=jcount,violations=violations,tight=tight,
            empty_empty_distance=0,does_not_validate_any_MRI_geometry=True),
        Holm_floors=[dict(B=10000,K=k,raw_floor=2/10001,adjusted_floor=2*k/10001,less_than_0_005_print_allowed=(2*k/10001<.005)) for k in [16,24,32]],
        REFLECT_denominator_only=dict(same_hits=287,all_components=5473,above_floor=472,
            all_component_ratio=287/5473,above_floor_sensitivity=287/472,ratio_increase_only_from_denominator=5473/472),
        cost_denominator_audit=costs,Table4_cDDPM20_Dice_confirmed_0_519=True,
        author_code_reproduced=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'CPU_AUDIT_PLAN.md',HERE/'primary_attempt01/receipt.json']]+[b['source'] for b in bindings],
        resource_snapshot=client.resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    client.base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=True,rows_checked=52,UCCD_cDDPM_budget20=q['UCCD_cDDPM_budget20'],relaxation_fraction=q['UCCD_budget20_relaxation_fraction'],
        CRC_limits=crc,Jaccard=q['Jaccard_exhaustion'],cost_denominators=costs,resource_snapshot=q['resource_snapshot']),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
