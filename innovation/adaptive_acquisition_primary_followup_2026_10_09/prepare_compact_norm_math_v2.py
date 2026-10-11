import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'verify_compact_double_norm_cpu_v1.py').read_text(encoding='utf-8')
s=s.replace('compact_double_norm_cpu_attempt01','compact_double_norm_cpu_attempt02').replace('COMPACT_DOUBLE_NORM_PROTOCOL_V1.md','COMPACT_DOUBLE_NORM_PROTOCOL_V2.md')
s=s.replace('from compact_double_norm_v1 import CompactDoubleNormFunction','from compact_double_norm_v1 import CompactDoubleNormFunction\nfrom decimal_norm_finite_objective_v1 import decimal_norm_objective\nfrom decimal import Decimal as D,localcontext')
s=s.replace("HERE/'compact_double_norm_v1.py')", "HERE/'compact_double_norm_v1.py',HERE/'decimal_norm_finite_objective_v1.py',HERE/'COMPACT_DOUBLE_NORM_PROTOCOL_V1.md')")
old="      op,om=objective(plus),objective(minus);derivative=(op-om)/(2*h)\n      checks.append(dict(h=h,plus=op,minus=om,derivative=derivative,analytic_error=abs(derivative-analytical)))"
new="      op=decimal_norm_objective(actual,dy,index,direction,h,1);om=decimal_norm_objective(actual,dy,index,direction,h,-1)\n      with localcontext() as decimal_context:\n       decimal_context.prec=60;derivative=(op-om)/(2*D.from_float(h));error=abs(derivative-D.from_float(analytical))\n      checks.append(dict(h=h,plus_exact_decimal=str(op),minus_exact_decimal=str(om),derivative_exact_decimal=str(derivative),analytic_error_exact_decimal=str(error),derivative=float(derivative),analytic_error=float(error)))"
assert old in s;s=s.replace(old,new);ast.parse(s)
p=HERE/'verify_compact_double_norm_cpu_v2.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
