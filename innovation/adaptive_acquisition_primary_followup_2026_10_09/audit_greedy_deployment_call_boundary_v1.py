"""AST-only check of selected author call boundaries; never import author code."""
import ast,gzip,json,time
from pathlib import Path
from resource_guard_v1 import HERE,guard,entry,bind,dump
start=time.perf_counter();before=guard(start);p=HERE/'greedy_selected_sources_attempt01/src__policy_model__policy_model_utils.py.gz';text=gzip.decompress(p.read_bytes()).decode('utf-8');tree=ast.parse(text)
functions={v.name:v for v in tree.body if isinstance(v,(ast.FunctionDef,ast.AsyncFunctionDef))}
records=[]
for name,expected in [('get_new_zf',['masked_kspace_batch']),('compute_next_step_reconstruction',['recon_model','kspace','masked_kspace','mask','next_rows']),('get_policy_probs',['model','recons','mask']),('compute_scores',['args','recons','gt_mean','gt_std','unnorm_gt','data_range','comp_psnr'])]:
 f=functions[name];params=[v.arg for v in f.args.args];assert params==expected
 names={v.id for v in ast.walk(f) if isinstance(v,ast.Name)};calls=[ast.unparse(v) for v in ast.walk(f) if isinstance(v,ast.Call)]
 gtfields=sorted(names&{'gt','gt_mean','gt_std','unnorm_gt'})
 if name!='compute_scores':assert not gtfields
 else:assert {'gt_mean','gt_std','unnorm_gt'}.issubset(names)
 records.append(dict(function=name,params=params,start_line=f.lineno,end_line=f.end_lineno,GT_name_references=gtfields,calls=calls))
getprob=functions['get_policy_probs'];modelcalls=[v for v in ast.walk(getprob) if isinstance(v,ast.Call) and isinstance(v.func,ast.Name) and v.func.id=='model'];assert len(modelcalls)==1 and ast.unparse(modelcalls[0].args[0])=='recons'
nextstep=functions['compute_next_step_reconstruction'];recon=[v for v in ast.walk(nextstep) if isinstance(v,ast.Call) and isinstance(v.func,ast.Name) and v.func.id=='recon_model'];assert len(recon)==1 and ast.unparse(recon[0].args[0])=='zf'
out=HERE/'greedy_deployment_call_boundary_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],records=records,source_bindings=[entry(Path(__file__)),entry(p),entry(HERE/'greedy_policy_utils_fetch_attempt01/receipt.json')],
 author_commit='d4e4164c5e7d13e57391f8a932ffd81958995dcd',authenticated_publication_time_version=False,
 selected_policy_and_next_reconstruction_function_bodies_have_no_GT_names=True,
 acquisition_reads_chosen_column_from_full_kspace_simulator=True,full_kspace_is_project_deployment_input=False,
 GT_statistics_present_in_quality_scoring=True,quality_scoring_GT_statistics_prove_deployment_leak=False,
 callback_models_external_helpers_and_all_transitive_globals_audited=False,whole_author_pipeline_noninterference_proven=False,
 author_code_imported=False,author_code_executed=False,author_training_reproduced=False,publication_claim_confirmed=False,goal_status='active',
 resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
for b in r['source_bindings']:bind(b)
dump(out/'receipt.json',r);print(json.dumps({k:r[k] for k in ('complete','selected_policy_and_next_reconstruction_function_bodies_have_no_GT_names','GT_statistics_present_in_quality_scoring','quality_scoring_GT_statistics_prove_deployment_leak','whole_author_pipeline_noninterference_proven','author_code_executed')}))
