"""Preserve syntax-failed v1; parenthesize the negation and verify AST before launch."""
import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'independent_round51_audit_v1.py').read_text(encoding='utf-8')
assert s.count("==not complete")==1
s=s.replace('==not complete','==(not complete)').replace('independent_round51_audit_attempt01','independent_round51_audit_attempt02')
ast.parse(s);p=HERE/'independent_round51_audit_v2.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(p)
