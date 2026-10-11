"""Materialize an auditable V2 script; do not modify the failed original."""
import ast,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
FUNCTION='''def independently_physical_matrices(record,pivot_zrc,spacing_zrc):
    spacing=np.asarray(spacing_zrc,float)[::-1];pivot=np.asarray(pivot_zrc,float)[::-1]
    def rotate(v,axis,angle):
        c,s=np.cos(angle),np.sin(angle);x,y,z=v
        if axis==0:return np.array([x,c*y-s*z,s*y+c*z])
        if axis==1:return np.array([c*x+s*z,y,-s*x+c*z])
        return np.array([c*x-s*y,s*x+c*y,z])
    matrices=[]
    for reverse in [False,True]:
        columns=[]
        for basis in np.eye(3):
            v=basis*spacing
            if reverse:
                v*=record['scale'];axes=zip([0,1,2],record['degrees_xyz'])
            else:axes=zip([2,1,0],[-a for a in record['degrees_xyz'][::-1]])
            for axis,deg in axes:v=rotate(v,axis,np.deg2rad(deg))
            if not reverse:v/=record['scale']
            columns.append(v/spacing)
        a=np.column_stack(columns);matrices.append((a,pivot-a@pivot))
    return matrices

'''
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    src=HERE/'verify_full_geometry_support.py';dest=HERE/'verify_full_geometry_support_v2.py';assert not dest.exists()
    original=src.read_text(encoding='utf-8');tree=ast.parse(original)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='independently_physical_matrices')
    lines=original.splitlines(keepends=True);replaced=''.join(lines[:fn.lineno-1])+FUNCTION+''.join(lines[fn.end_lineno:])
    assert replaced.count("HERE/'full_support_attempt01'")==1
    replaced=replaced.replace("HERE/'full_support_attempt01'","HERE/'full_support_attempt02'")
    marker="[Path(__file__),HERE/'full_geometry_support.py',HERE/'PROTOCOL.md',src,"
    assert replaced.count(marker)==1
    replaced=replaced.replace(marker,"[Path(__file__),HERE/'verify_full_geometry_support.py',HERE/'prepare_full_support_v2.py',HERE/'FLOAT64_ORACLE_V2_PROTOCOL.md',HERE/'full_geometry_support.py',HERE/'PROTOCOL.md',src,")
    ast.parse(replaced)
    with dest.open('x',encoding='utf-8') as f:f.write(replaced)
    print(json.dumps(dict(complete=True,original_source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),new_source_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),source_changed_only_in_oracle_output_and_bindings=True)),flush=True)
if __name__=='__main__':main()
