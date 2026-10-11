"""AST-only source call audit and exhaustive tiny label algebra, no author execution or neural forward."""
import ast,hashlib,inspect,itertools,json,sys,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source(p):return p.read_text(encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard();out=HERE/'static_semantics_attempt01';out.mkdir(exist_ok=False)
    root=HERE/'author_root_sources_attempt01';names=['utils_py.source.txt','dataloading_py.source.txt','main_py.source.txt']
    trees={name:ast.parse(source(root/name),filename=name) for name in names}
    loader=next(n for n in trees['dataloading_py.source.txt'].body if isinstance(n,ast.ClassDef) and n.name=='RegDataLoaderV1')
    init=next(n for n in loader.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    arguments=init.args.args[1:];defaults=len(init.args.defaults);params=[]
    for i,a in enumerate(arguments):
        default=inspect.Parameter.empty if i<len(arguments)-defaults else None
        params.append(inspect.Parameter(a.arg,inspect.Parameter.POSITIONAL_OR_KEYWORD,default=default))
    signature=inspect.Signature(params)
    mtree=trees['main_py.source.txt'];calls=[]
    for call in ast.walk(mtree):
        if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name) or call.func.id!='RegDataLoaderV1':continue
        assert not any(isinstance(a,ast.Starred) for a in call.args) and all(k.arg is not None for k in call.keywords)
        try:
            signature.bind(*([None]*len(call.args)),**{k.arg:None for k in call.keywords});binding_error=None
        except TypeError as e:binding_error=str(e)
        calls.append(dict(lineno=call.lineno,positional_count=len(call.args),keyword_names=[k.arg for k in call.keywords],
            known_class_signature=str(signature),signature_binding_succeeds=binding_error is None,binding_error=binding_error,
            source_expression=ast.get_source_segment(source(root/'main_py.source.txt'),call)))
    assert len(calls)==2 and all(c['binding_error']=="missing a required argument: 'batch_size'" for c in calls)
    choices=next(n for n in mtree.body if isinstance(n,ast.If) and ast.unparse(n.test)=="__name__ == '__main__'")
    arch=next(n for n in choices.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='arch_chocies' for t in n.targets))
    listed=ast.literal_eval(arch.value);readme=source(root/'README_md.source.txt');requested=['qcresunet34','qcresunet50']
    assert all(s in readme and s not in listed for s in requested)
    # Enumerate independent region-membership errors; anatomical inclusion never assumed for XOR maps.
    region=lambda label:(label>0,label>=2,label==3)
    records=[]
    for truth,query in itertools.product(range(4),repeat=2):
        gt=region(truth);p=region(query);e=tuple(a!=b for a,b in zip(gt,p))
        reconstructed_label=3 if e[2] else 2 if e[1] and not e[2] else 1 if e[0] and not e[1] else 0
        projected=region(reconstructed_label);nested=(not e[2] or e[1]) and (not e[1] or e[0])
        records.append(dict(gt_label=truth,query_label=query,GT_regions_WT_TC_ET=gt,query_regions_WT_TC_ET=p,
            exact_error_regions_WT_TC_ET=e,error_maps_nested=nested,
            appendix_D_display_label=reconstructed_label,redecoded_display_regions=projected,
            anatomical_recomposition_equivalent=projected==e))
    violations=[r for r in records if not r['error_maps_nested']];assert len(violations)==6
    assert all(not r['anatomical_recomposition_equivalent'] for r in violations)
    assert all(r['anatomical_recomposition_equivalent'] for r in records if r['error_maps_nested'])
    binary=[]
    for truth,query in itertools.product([False,True],repeat=2):
        e=truth!=query;fp=e and query;fn=e and not query
        assert fp==(query and not truth) and fn==(truth and not query) and (query!=e)==truth
        binary.append(dict(GT=truth,query=query,error=e,derived_FP=fp,derived_FN=fn,exact_signed_direction_recovered=True))
    for name,tree in trees.items():compile(tree,name,'exec') # Compile is syntax-only; code object is never executed.
    assert time.perf_counter()-started<120 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    sources=[Path(__file__),HERE/'STATIC_AND_SEMANTIC_AUDIT_PROTOCOL.md',HERE/'extraction_attempt01/blocks.json',
        HERE/'author_web_attempt01/receipt_v2.json',HERE/'author_root_sources_attempt01/receipt.json',root/'README_md.source.txt']+[root/n for n in names]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],three_author_sources_AST_parse=True,
        author_commit='e9ddc2418c72cc1c20b69bd3074b7f96b8b5f408',author_sources_executed=False,
        constructor_call_checks=calls,README_arch_choices_not_in_selected_main_parser=requested,selected_main_parser_choices=listed,
        no_claim_entire_repository_examined=True,publication_runtime_failure_inferred=False,
        required_unresolved_import_in_root_snapshot='from losses import DC_and_BCE_loss, PearsonCorrLoss',
        selected_training_interface='CSV scalar subject quality and single binary label-mismatch SEM; NSD/multi-region complete pipeline not established from these files',
        anatomical_label_names={0:'background',1:'edema',2:'core',3:'enhancing'},all16_ordered_label_pairs=records,
        non_nested_error_region_pairs=len(violations),appendix_D_anatomical_recomposition_equivalence_not_guaranteed=True,
        scope_of_counterexample='Published visualization algebra only; does not invalidate its evaluated original per-channel SEM predictions.',
        all4_binary_pairs=binary,binary_FP_FN_direction_recoverable=True,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources])
    with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({k:r[k] for k in ['complete','constructor_call_checks','README_arch_choices_not_in_selected_main_parser','non_nested_error_region_pairs','binary_FP_FN_direction_recoverable','neural_forwards','elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
