"""Public table checks and scalar counterexamples; no medical or neural computation."""
import sys,json,math,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'cpu_audit_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client

def norm(s):return ' '.join(s.replace('−','-').replace('×','x').replace('–','-').split())
def page(key,n):return norm((HERE/'primary_attempt01'/f'{key}_page{n:03d}.txt').read_text(encoding='utf-8'))
def close(x,y):assert abs(x-y)<1e-12,(x,y)
def ratio(a,b):return a/b

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();OUT.mkdir(exist_ok=False)
    src=HERE/'PUBLIC_TABLE_TRANSCRIPTION.json';t=json.loads(src.read_text(encoding='utf-8'));checks=[]
    for name,key,n in [('rd_table2','rd_vit',10),('rd_table4','rd_vit',14),('rd_tableC1','rd_vit',23),('hifi_tableV','hifi_mamba_v2',7),('hifi_tableIV','hifi_mamba_v2',6),('hifi_tableVII','hifi_mamba_v2',7)]:
        s=page(key,n)
        for i,r in enumerate(t[name]):
            if name=='rd_table2':patterns=[norm(r[0]),f'{r[1]:,}',f'{r[2]:.3f}',f'{r[3]:,}']
            elif name=='rd_table4':patterns=[r[0],f'{r[1]:.3f}',f'{r[2]:.3f}',f'{r[3]:+.1f} pp',f'{r[4]:.3f}',f'{r[5]:.3f}',f'{r[6]:-.1f} pp']
            elif name=='rd_tableC1':patterns=[r[0],f'{r[1]:.3f}']
            elif name=='hifi_tableV':patterns=[r[0],f'{r[1]:.2f}G',f'{r[2]:.2f}',f'{r[3]:.3f}',f'{r[4]:.3f}']
            elif name=='hifi_tableIV':patterns=[r[1],f'{r[2]:.2f}',f'{r[3]:.3f}',f'{r[4]:.3f}']
            else:patterns=[str(r[0]),r[1].replace('x','x'),f'{r[2]:.2f}',f'{r[3]:.3f}',f'{r[4]:.3f}']
            matched=norm(' '.join(patterns)) in s;checks.append(dict(table=name,row=i+1,physical_page=n,matched=matched))
    assert len(checks)==39 and all(c['matched'] for c in checks),[c for c in checks if not c['matched']]
    delta2=[100*(r[1]-r[2]) for r in t['rd_table4']];delta3=[100*(r[4]-r[5]) for r in t['rd_table4']]
    for r,d2,d3 in zip(t['rd_table4'],delta2,delta3):close(d2,r[3]);close(d3,r[6])
    rd=t['rd_table2'];hv=t['hifi_tableV'];mc=t['hifi_tableIV']
    numeric=dict(rd_moe_parameter_ratio=ratio(rd[2][1],rd[0][1]),rd_moe_dice_ratio=ratio(rd[2][2],rd[0][2]),
        rd_moe_train_time_ratio=ratio(rd[2][3],rd[0][3]),rd_ACT_train_time_ratio=ratio(rd[1][3],rd[4][3]),
        rd_C1_mean=math.fsum(r[1] for r in t['rd_tableC1'][:3])/3,
        rd_2D_advantage_pp=delta2,rd_3D_advantage_pp=delta3,rd_3D_gap_monotonically_narrowing=all(b<=a for a,b in zip([-d for d in delta3],[-d for d in delta3][1:])),
        hifi_P1_FLOPs_ratio_vs_V1=hv[5][1]/hv[3][1],hifi_P2_FLOPs_ratio_vs_V1=hv[6][1]/hv[4][1],
        hifi_P2_FLOPs_ratio_vs_LMO=hv[6][1]/hv[2][1],hifi_P1_FLOPs_ratio_vs_ReconFormer=hv[5][1]/hv[0][1],
        hifi_P1_FLOPs_ratio_vs_FpsFormer=hv[5][1]/hv[1][1],
        hifi_m4raw_P1_AF8_deltas_V2_minus_V1=dict(PSNR=mc[9][2]-mc[7][2],SSIM=mc[9][3]-mc[7][3],NMSE=mc[9][4]-mc[7][4]))
    close(numeric['rd_C1_mean'],t['rd_tableC1'][3][1])
    speed=[dict(attention_fraction=a,ideal_block_speedup=8/(8*a+1.4*(1-a)),dense_mask_block_speedup_before_overhead=1,
        empirical_runtime=False) for a in (0,.25,.5,.75,1)]
    def f(h):return .36*h+.8*math.tanh(h)
    roots=[]
    for start in (-.1,0,.1):
        h=start
        for _ in range(500):h=f(h)
        roots.append(dict(initial_h=start,final_h=h,fixed_point_residual=abs(h-f(h))))
    assert roots[0]['final_h']<-.1 and roots[1]['final_h']==0 and roots[2]['final_h']>.1
    assert max(r['fixed_point_residual'] for r in roots)<1e-12
    counter=dict(A=.36,f='.8*tanh(h)',f_bound=.8,f_Lipschitz_bound=.8,map_derivative_at_zero=1.16,roots=roots,
        actual_author_model_evaluated=False,unique_fixed_point_not_guaranteed_by_A_alone=True)
    p=[.2503,.2501,.2499,.2497];eps=1e-5
    assert abs(math.fsum(p)-1)<1e-12
    def routed(v):return [2,-1,5,7][max(range(4),key=lambda i:v[i])]
    finite=[]
    for i in range(4):
        lo=p.copy();hi=p.copy();lo[i]-=eps;hi[i]+=eps
        finite.append((routed(hi)-routed(lo))/(2*eps))
    assert finite==[0]*4
    route=dict(probabilities=p,N_tokens_assumed=1000,hard_utilization=[1000,0,0,0],
        probability_only_balance_loss=4*math.fsum(v*v for v in p),minimum_balance_loss=1,
        piecewise_constant_hard_selection_finite_differences=finite,author_source_not_inspected=True)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],rows_checked=39,
        all39_transcribed_rows_match_actual_extracted_text=True,row_checks=checks,public_table_arithmetic=numeric,
        hypothetical_ACT_cost_sensitivity=speed,scalar_recurrence_counterexample=counter,hard_router_formula_diagnostic=route,
        source_bindings=[client.base.entry(p) for p in (Path(__file__),src,HERE/'CPU_EXPLORATION_PLAN.md',HERE/'primary_attempt01/receipt.json',HERE/'visual_attempt01/receipt.json')],
        resource_snapshot=client.resource_guard(),medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,publication_claim_confirmed=False)
    client.base.new(OUT/'receipt.json',result)
    print(json.dumps({k:result[k] for k in ('complete','rows_checked','public_table_arithmetic','hypothetical_ACT_cost_sensitivity','scalar_recurrence_counterexample','hard_router_formula_diagnostic')},ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
