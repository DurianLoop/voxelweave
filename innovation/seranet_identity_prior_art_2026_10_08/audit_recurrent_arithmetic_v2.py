"""Public endpoint arithmetic and literal printed schedule, no medical data or models."""
import json,sys,re
from decimal import Decimal,getcontext
from pathlib import Path
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent
OUT=HERE/'recurrent_audit_attempt02'
D=Decimal

def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.base.own_priority();resources=prior.resource_guard()
    OUT.mkdir(exist_ok=False);getcontext().prec=40
    source=HERE/'primary_attempt02'
    sr1=[['joint_lce_l2','0.8048','0.8841','0.8518','0.8469','0.7995','0.8751','0.8092','0.8279'],
         ['all_steps_lce','0.8513','0.9082','0.8796','0.8797','0.8041','0.8733','0.8283','0.8352'],
         ['final_lce','0.8482','0.9102','0.8814','0.8799','0.8083','0.8762','0.8415','0.8423']]
    sr2=[['One-step','0.7677','0.8334','0.7900','0.7970','0.7600','0.8324','0.7911','0.7945'],
         ['LI-net','0.6849','0.7576','0.7558','0.7328','0.6686','0.7276','0.7282','0.7081'],
         ['Syn-net','0.7558','0.8256','0.7961','0.7925','0.7307','0.8095','0.7808','0.7737'],
         ['SegNetMRI','0.8210','0.8905','0.8575','0.8563','0.7817','0.8472','0.7728','0.8006'],
         ['SERANet-2','0.8344','0.8977','0.8669','0.8663','0.8053','0.8706','0.8373','0.8377'],
         ['SERANet-7','0.8548','0.9175','0.8905','0.8876','0.8122','0.8798','0.8457','0.8459']]
    checks=[]
    for tab,n,rows in [(1,6,sr1),(2,8,sr2)]:
        text=(source/f'seranet_candidate_page{n:03d}.txt').read_text(encoding='utf-8')
        for r in rows:
            assert ' '.join(r[1:]) in text,r[0]
            vals=list(map(D,r[1:]))
            for offset,noise in [(0,'10%'),(4,'20%')]:
                computed=sum(vals[offset:offset+3])/3
                delta=computed-vals[offset+3]
                ok=abs(delta)<=D('0.00005')
                checks.append(dict(table=tab,method=r[0],noise=noise,printed=str(vals[offset+3]),
                    computed=str(computed),difference=str(delta),within_half_unit_rounding=ok))
    inconsistencies=[r for r in checks if not r['within_half_unit_rounding']]
    # These are transcribed means, separately from the printed +/- dispersion.
    means={
        'neither':['0.494','0.636','0.462','28.78','0.957'],
        'ITFS':['0.499','0.682','0.467','27.20','0.943'],
        'DRLC':['0.510','0.686','0.472','28.84','0.957'],
        'both':['0.518','0.688','0.479','28.87','0.958']}
    text=(source/'teacher_forcing_page007.txt').read_text(encoding='utf-8')
    for name,values in means.items():
        line=next(line for line in text.splitlines() if line.strip().startswith(('X X ' if name=='both' else '')+values[0]+' ') or (values[0]+' ±' in line and values[1]+' ±' in line))
        nums=re.findall(r'\d+\.\d+',line)
        assert nums[::2]==values,(name,nums)
    rows={k:list(map(D,v)) for k,v in means.items()}
    cols=['Dice','Precision','Recall','PSNR_dB','SSIM']
    effects={name:{c:str(rows[name][i]-rows['neither'][i]) for i,c in enumerate(cols)} for name in ['ITFS','DRLC','both']}
    interaction={c:str(rows['both'][i]-rows['ITFS'][i]-rows['DRLC'][i]+rows['neither'][i]) for i,c in enumerate(cols)}
    schedule=[dict(t=t,alpha=str(max((-D(t)).exp()-D('.2'),D('.05'))),
        beta=str(1-max((-D(t)).exp()-D('.2'),D('.05')))) for t in [0,1,2,5,10,50]]
    source_differences=[
      dict(page=4,location='paragraph vs Eq.4',paragraph='Cross-Entropy',equation='1 - soft overlap ratio',implementation_unresolved=True),
      dict(page=5,location='paragraph vs Fig.2/Eq.5',paragraph='alpha increases, beta decreases',figure_and_equation='alpha decreases, beta increases',implementation_unresolved=True),
      dict(page=10,location='Brainweb paragraph vs Table4 p13',paragraph_WM='0.9285',table_WM='0.958',paragraph_GM='0.9354',table_GM='0.960',paragraph_SSIM='0.993',table_SSIM='0.997'),
      dict(page=13,location='in vivo paragraph vs Table5',paragraph_SSIM='0.983',table_SSIM='0.986'),
      dict(page=7,location='Table1 vs Table2 fixed0.5 baseline',table1_Dice_dispersion='0.494 +/-0.071',table2_Dice_dispersion='0.494 +/-0.083',different_run_possible_not_resolved=True),
      dict(page=7,location='Tables1,2 vs Table3 p10 final ATLAS SSIM',tables1_2='0.958',table3='0.959',different_run_possible_not_resolved=True)]
    q=dict(complete=True,errors=[],SERANet_table1_tissue_order=['CSF','GM','WM'],SERANet_table2_tissue_order=['CSF','WM','GM'],
        SERANet_printed_mean_checks=checks,SERANet_printed_means_rounding_consistent=not inconsistencies,SERANet_source_mean_inconsistencies=inconsistencies,
        teacher_table1_transcribed_means=means,teacher_table1_descriptive_gains=effects,teacher_table1_descriptive_interaction=interaction,
        teacher_table3_ours_minus_fullsample_UNet=dict(Dice=str(D('.518')-D('.512')),Precision=str(D('.688')-D('.632')),Recall=str(D('.479')-D('.511'))),
        literal_epoch_schedule=schedule,literal_alpha_floor_start_t=str(-D('.25').ln()),
        normalized_epoch_or_author_implementation_verified=False,source_differences=source_differences,
        source_bindings=[prior.base.entry(p) for p in [Path(__file__),HERE/'RECURRENT_ARITHMETIC_PLAN.md',
          HERE/'visual_attempt02/receipt.json',*[source/f'{key}_page{n:03d}.txt' for key,nums in [('seranet_candidate',[6,8]),('teacher_forcing',[4,5,7,10,13])] for n in nums]]],
        resource_snapshot=resources,statistical_inference_performed=False,clinical_effect_verified=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    prior.base.new(OUT/'receipt.json',q)
    print(json.dumps({k:q[k] for k in ['complete','SERANet_printed_means_rounding_consistent','SERANet_source_mean_inconsistencies','teacher_table1_descriptive_gains',
        'teacher_table1_descriptive_interaction','teacher_table3_ours_minus_fullsample_UNet','literal_epoch_schedule','literal_alpha_floor_start_t']},ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
