"""Exact printed-table arithmetic and AST facts; never import/execute author files."""
import ast
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE/'cpu_audit_attempt01'
sys.path.insert(0, str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client


def encode(value):
    return dict(exact=str(value), decimal=float(value))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    client.base.own_priority()
    client.resource_guard()
    OUT.mkdir(exist_ok=False)
    table = json.loads((HERE/'PAPER_TABLE_TRANSCRIPTION.json').read_text(encoding='utf-8'))
    rows = {r['method']: [None if v is None else Fraction(v) for v in r['values']] for r in table['table_III']}
    assert len(table['table_I_LPIPS']) == 5 and len(rows) == 10
    ours, asynchronous = rows['Ours'], rows['Ours_asyn']
    arithmetic = dict(
        asyn_reported_FLOPs_fraction_of_ensemble=encode(asynchronous[5]/ours[5]),
        asyn_reported_FLOPs_relative_difference=encode((ours[5]-asynchronous[5])/ours[5]),
        asyn_reported_parameters_relative_difference=encode((ours[4]-asynchronous[4])/ours[4]),
        asyn_is_most_expensive_single_expert_not_measured_total_patient_cost=True,
        asyn_quality_cells_missing=all(v is None for v in asynchronous[:4]),
        Ours_LPIPS_TableIII_converted=encode(ours[2]/100),
        full_b_g_LPIPS_TableI=encode(Fraction(table['table_I_LPIPS'][0]['LPIPS'])),
        unexplained_LPIPS_scope_or_value_difference=encode(Fraction(table['table_I_LPIPS'][0]['LPIPS'])-ours[2]/100),
        direct_3T_reference_LPIPS_units_match=(rows['3T_ref'][2]/100 == Fraction(table['table_I_LPIPS'][4]['LPIPS'])),
        TableIV_weights_sum=encode(sum(map(Fraction, table['table_IV_example_weights']))))
    # Literal Eq4 multiplies two separately normalized categorical factors.
    # Balanced scores/usage give exact weights 1/K^2, not 1/K.
    k = 3
    literal = [Fraction(1,k)*Fraction(1,k) for _ in range(k)]
    formula = dict(K=k, balanced_literal_Eq4_weights=[encode(v) for v in literal],
        balanced_literal_Eq4_sum=encode(sum(literal)),
        constant_equal_expert_latent_1_aggregate_literal_Eq9=encode(sum(literal)),
        TableIV_weights_sum=arithmetic['TableIV_weights_sum'],
        literal_equation_is_not_the_author_source_gating_function=True,
        author_source_gating='plain F.softmax of global averaged token features',
        author_source_MAD_temperature_floor='1e-8',
        source_zero_temperature_runtime_failure_not_claimed=True)
    source_facts = []
    for path in sorted((HERE/'sources_attempt01').glob('*.source.txt')):
        client.resource_guard()
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=path.name)
        classes = [dict(name=n.name, line=n.lineno,
            methods=[dict(name=m.name, line=m.lineno) for m in n.body if isinstance(m, ast.FunctionDef)])
            for n in tree.body if isinstance(n, ast.ClassDef)]
        lists = []
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            for n in ast.walk(cls):
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.List):
                    for target in n.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id=='self':
                            lists.append(dict(class_name=cls.name, attribute=target.attr, line=n.lineno,
                                expression=ast.unparse(n.value)))
        source_facts.append(dict(file=client.base.entry(path), classes=classes,
            self_attributes_assigned_plain_python_lists=lists,
            author_source_executed=False))
    expert_facts = next(r for r in source_facts if r['file']['path'].endswith('/experts.source.txt'))
    assert len(expert_facts['self_attributes_assigned_plain_python_lists']) == 16
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        printed_table_rows_audited=15, printed_weight_vectors_audited=1,
        arithmetic=arithmetic, printed_formula_diagnostic=formula, source_AST_facts=source_facts,
        static_source_interface_findings=[
            'train passes timesteps=[500,1000,2000] to MoEModel; model scalar schedule adds timesteps+1 and TimeEmbedding expects an integer embedding count',
            'train constructs VQ-VAE in_ch=1 but subsequently encodes a 3-channel 7T_input',
            'train VQ-VAE embed_dim=512 and MoE base_ch=128 disagree at expert fused-input channel contract',
            'model uses F.pad(acp[:-1], (0,0)), retaining T-1 rather than T prior cumulative alpha values',
            'experts store 16 layer sequences as plain Python lists rather than registered ModuleList/Sequential containers',
            'MoE forward evaluates all three experts unconditionally and weights their stacked outputs',
            'five visible source files provide no complete reverse sampler or asynchronous inference runner'
        ],
        observations_are_static_not_author_runtime_reproductions=True,
        author_implementation_files_fully_read=5, author_implementation_files_AST_parsed=5,
        author_code_executed=False, medical_arrays_loaded=0, model_checkpoint_arrays_loaded=0,
        neural_forwards=0, GPU_forwards=0, head_fits=0, new_action_labels=0,
        publication_claim_confirmed=False, goal_status='active',
        source_bindings=[client.base.entry(p) for p in [Path(__file__), HERE/'PROTOCOL.md',
            HERE/'PAPER_TABLE_TRANSCRIPTION.json', HERE/'sources_attempt01/receipt.json',
            HERE/'primary_attempt02/page_004.txt', HERE/'primary_attempt02/page_007.txt',
            HERE/'primary_attempt02/page_008.txt']],
        resource_snapshot=client.resource_guard())
    client.base.new(OUT/'receipt.json', result)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) < 6_000_000
    print(json.dumps(dict(complete=True, printed_table_rows_audited=15,
        arithmetic=arithmetic, formula=formula, plain_expert_layer_lists=16,
        source_files_AST_parsed=5, author_code_executed=False), ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
