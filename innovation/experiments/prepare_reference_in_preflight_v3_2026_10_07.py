"""Permit the single approved observed NPZ while keeping patient ZIP/NIfTI readers blocked."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    old=ROOT/'preflight_mc_rc_3d_reference_in_v2_2026_10_07.py'
    new=ROOT/'preflight_mc_rc_3d_reference_in_v3_2026_10_07.py';assert not new.exists()
    s=old.read_text(encoding='utf-8')
    s=s.replace('import json,sys,time,traceback,zipfile','import json,sys,time,traceback,zipfile\nfrom pathlib import Path')
    s=s.replace("OUT=ROOT/'experiments/mc_rc_3d_reference_in_preflight_v2_2026_10_07'", "OUT=ROOT/'experiments/mc_rc_3d_reference_in_preflight_v3_2026_10_07'")
    s=s.replace('    save()\n    try:', '''    permitted_observed_npz=None
    original_zip_reader=zipfile.ZipFile
    def observed_npz_only(*args,**kwargs):
        source=args[0] if args else kwargs.get('file')
        resolved=Path(getattr(source,'name',source)).resolve()
        assert permitted_observed_npz is not None and resolved==permitted_observed_npz,'Only the approved observed NPZ may use ZIP reader'
        return original_zip_reader(*args,**kwargs)
    save()
    try:''')
    s=s.replace('zipfile.ZipFile=deny_patient_pixel_load','zipfile.ZipFile=observed_npz_only')
    s=s.replace("        observed=observed_package(case,row);", "        permitted_observed_npz=(ROOT/row['observed_package']).resolve()\n        assert sha(permitted_observed_npz)==row['observed_package_sha256']\n        r['observed_npz_reader_guard']='Exactly one resolved authenticated NPZ path; original MR ZIP and NIfTI readers forbidden'\n        observed=observed_package(case,row);")
    s=s.replace("        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]",
                "        sources += [ROOT/'MC_RC_3D_REFERENCE_IN_OBSERVED_NPZ_ADDENDUM_V3_2026-10-07.md',ROOT/'experiments/mc_rc_3d_reference_in_preflight_v2_2026_10_07/attempt01.json',ROOT/'experiments/prepare_reference_in_preflight_v3_2026_10_07.py']\n        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]")
    compile(s,str(new),'exec')
    with new.open('x',encoding='utf-8') as f:f.write(s)
    print(new.name)
if __name__=='__main__':main()
