"""Fail-closed audit of Plan 4 publication-readiness claims."""
from pathlib import Path
import json
import pandas as pd
HERE=Path(__file__).resolve().parent;O=HERE/'plan4_outputs'
required=['CONSENSUS_ERROR_RESEARCH.md','HYPOTHESIS_PORTFOLIO.md','INNOVATION_SCORECARD.md','PLAN_4_REPORT.md','PLAN4_LITERATURE_AND_NOVELTY.md','PUBLICATION_READINESS_REPORT.md']
for f in required:assert (HERE/f).exists() and (HERE/f).stat().st_size>500,f
d=json.load(open(O/'overlap_zero_vs_max_summary.json'));base=[r for r in d['rows'] if 'target_model' not in r]
assert len(base)==2
for r in base:
 assert r['delta_plane_rho']>.15
 assert r['case_cluster_95ci'][0]>0
 assert r['max_endpoint_absdiff']==0
models=[r for r in d['rows'] if 'target_model' in r];assert len(models)==4
for r in models:
 assert r['delta_plane_rho']>0 and r['case_cluster_95ci'][0]>0
a=json.load(open(O/'analytical_disjoint_summary.json'));assert len(a['profiles'])==4
for r in a['profiles']:assert r['case_spearman']>.95
igc=json.load(open(O/'interleaved_x2_summary.json'));assert igc['requires_additional_acquisition'] is False and len(igc['rows'])==4
c=json.load(open(O/'curvature_spacing_summary.json'));assert 'bootstrap' in c
ad=json.load(open(O/'adaptive_acquisition_summary.json'));assert all(r['case_cluster_95ci'][0]>0 for r in ad['rows'])
for f in O.glob('*.csv'):
 x=pd.read_csv(f);assert len(x)>0,f
print({'status':'PASS','required_documents':len(required),'paired_cohorts':len(base),'neural_replications':len(models),'analytical_replications':len(a['profiles']),'audited_csv_files':len(list(O.glob('*.csv')))})
