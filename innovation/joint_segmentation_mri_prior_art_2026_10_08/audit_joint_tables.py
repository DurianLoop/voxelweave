"""Decimal arithmetic on visually checked author tables; no medical or neural imports."""
import json,sys,time
from decimal import Decimal as D
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'table_audit_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def delta(a,b):return [str(D(x)-D(y)) for x,y in zip(a,b)]
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard();tick=time.perf_counter()
    p=HERE/'PAPER_TABLE_TRANSCRIPTION.json';q=json.loads(p.read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=False);s=q['segnetmri'];c=q['calibrationless'];rows=[]
    for rate,t in c['table3'].items():
        proposed=t['Proposed'];cascade=t['Cascade']
        frozen=c['table2_dice'][rate]['IDSLR+SEG']
        dc=delta(proposed[1:],cascade[1:]);df=delta(proposed[1:],frozen)
        rows.append(dict(rate=rate,tissue_order=c['tissue_order'],
           proposed_minus_frozen_Dice=df,proposed_minus_joint_cascade_Dice=dc,
           joint_cascade_comparison_positive=sum(D(v)>0 for v in dc),
           joint_cascade_comparison_negative=sum(D(v)<0 for v in dc),
           proposed_minus_joint_cascade_SNR_dB=str(D(proposed[0])-D(cascade[0])),
           proposed_few_minus_full=delta(t['Proposed_few_shot'],proposed),
           shared_few_minus_cascade_few=delta(t['Proposed_few_shot'],t['Cascade_few_shot'])))
    assert sum(row['joint_cascade_comparison_positive'] for row in rows)==4
    assert sum(row['joint_cascade_comparison_negative'] for row in rows)==2
    st=s['table1_dice_percent'];ss=dict(tissue_order=s['tissue_order'],
       proposed_minus_frozen_percentage_points=delta(st['SegNetMRI5'],st['MRN5+MSN']),
       proposed_minus_reconstruction_only_adapted_percentage_points=delta(st['SegNetMRI5'],st['Liu2017']),
       proposed_minus_FS_reference_percentage_points=delta(st['SegNetMRI5'],st['FS+MSN']),
       PSNR_minus_MRN5=str(D(s['table2']['SegNetMRI5']['PSNR'])-D(s['table2']['MRN5']['PSNR'])),
       PSNR_minus_Liu2017=str(D(s['table2']['SegNetMRI5']['PSNR'])-D(s['table2']['Liu2017']['PSNR'])),
       printed_test_slice_count=48,printed_reconstruction_MRI_count=37,counts_not_reconciled=True)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
       source_bindings=[base.entry(v) for v in (Path(__file__),p,HERE/'PROTOCOL.md',
       HERE/'primary_attempt01/receipt.json',HERE/'primary_attempt01/segnetmri.pdf',
       HERE/'primary_attempt01/calibrationless.pdf',
       HERE/'visual_attempt01/segnetmri_page005.png',HERE/'visual_attempt01/segnetmri_page006.png',
       HERE/'visual_attempt01/calibrationless_page008.png')],calibrationless=rows,segnetmri=ss,
       few_shot_label_fraction=str(D(4)/D(40)),used_CCP_subset_subjects=40+7+15,
       few_shot_is_not_10percent_total_MRI_or_reconstruction_supervision=True,
       no_patient_paired_values=True,no_statistical_significance_calculated=True,
       no_Dice_SNR_composite_score=True,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
       actual_new_MRI_task_benefit_measured=False,publication_claim_confirmed=False,elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',result);print(json.dumps(result,ensure_ascii=False),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())

