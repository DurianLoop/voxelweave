"""Build the authoritative Plan-5 MRI interpolation manifest.

The manifest records files; it never copies MRI data.  Future Plan-5 scripts
must select cases through this table instead of filesystem ordering.
"""
from __future__ import annotations
import sys
from dataclasses import replace
from pathlib import Path
import nibabel as nib
import pandas as pd

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1]
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]
from rasinet.optimization_protocol import profile_sources,case_names,prediction_path,gt_path

def archived(s,ds,factor):
 return replace(s,root=ROOT/'baseline'/f'{s.root.name}_root_results_202607') if ds=='ningxia' and factor in (2,6) else s

def main():
 rows=[]
 for ds in ('fastmri','ningxia','ixi'):
  folds=[f'fold_{i:02d}' for i in range(8)] if ds=='ningxia' else [None]
  for factor in ((4,) if ds=='ixi' else (2,4,6)):
   specs={m:archived(profile_sources(ds,factor)[m],ds,factor) for m in ('i3net','hat','swinir')}
   for fold in folds:
    for model,src in specs.items():
     ref=specs['i3net']
     for case in case_names(src,fold):
      pp=prediction_path(src,fold,case);gp=gt_path(ref,fold,case)
      if not pp.exists() or not gp.exists():continue
      img=nib.load(str(gp));shape=img.shape;spacing=img.header.get_zooms()
      rows.append({'dataset':ds,'case_id':case,'split':'test' if ds=='fastmri' else 'OOF_'+str(fold),
       'patient_cluster':case.split('_')[0] if ds=='ningxia' else case,'modality':'MRI','contrast':'T2','factor':factor,
       'architecture':model,'source_file':str(pp.resolve()),'ground_truth_file':str(gp.resolve()),
       'physical_spacing_mm':float(spacing[2]),'volume_depth':int(shape[2]),
       'matched_planes':int(sum(z%factor!=0 for z in range(shape[2]))),'context_type':'standard_factor_grid',
       'overlap_type':'pair_dependent','evaluation_eligibility':True})
 x=pd.DataFrame(rows).sort_values(['dataset','case_id','factor','architecture'])
 x.to_csv(UP/'DATA_MANIFEST.csv',index=False)
 print({'rows':len(x),'datasets':x.dataset.nunique(),'cases':x.case_id.nunique(),'patient_clusters':x.patient_cluster.nunique(),'all_files_exist':bool(x.source_file.map(lambda p:Path(p).exists()).all() and x.ground_truth_file.map(lambda p:Path(p).exists()).all())})
if __name__=='__main__':main()
