"""Fix the certificate path after adding provenance dependencies; retain both prior failures."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    old=ROOT/'audit_mc_rc_3d_label_roundtrip_v2_2026_10_07.py'
    new=ROOT/'audit_mc_rc_3d_label_roundtrip_v3_2026_10_07.py';assert not new.exists()
    s=old.read_text(encoding='utf-8').replace("OUT=ROOT/'experiments/mc_rc_3d_label_roundtrip_v2_2026_10_07'", "OUT=ROOT/'experiments/mc_rc_3d_label_roundtrip_v3_2026_10_07'")
    s=s.replace("certified=read(ROOT/sources[-1])", "certified=read(ROOT/'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json')")
    s=s.replace("        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sources]", "        sources += ['experiments/mc_rc_3d_label_roundtrip_v2_2026_10_07/attempt01.json','experiments/prepare_mc_rc_3d_label_roundtrip_v3_2026_10_07.py']\n        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sources]")
    compile(s,str(new),'exec')
    with new.open('x',encoding='utf-8') as f:f.write(s)
    print(new.name)
if __name__=='__main__':main()
