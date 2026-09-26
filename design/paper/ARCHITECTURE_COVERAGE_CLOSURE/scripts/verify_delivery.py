from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=json.loads((P/'DELIVERY_MANIFEST.json').read_text())
    records=json.loads((P/'outputs/installed_files.json').read_text())
    for r in records:assert sha(ROOT/r['path'])==r['after_sha256'],r['path']
    zpath=P/'CVPR_ARCHITECTURE_COVERAGE_REVIEW_PACKAGE.zip'
    assert sha(zpath)==manifest['zip_sha256']
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        assert len(z.namelist())==manifest['zip_entries']
        assert not any(n.endswith('.npz') or 'manifest' in n.lower() for n in z.namelist())
        for s in ['main','supplement']:
            expected=(P/'revised_manuscript'/f'{s}.pdf').read_bytes()
            assert z.read(f'PAPER/{s}.pdf')==expected
            assert (P.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'/f'{s}.pdf').read_bytes()==expected
    # All small final reports/source files are checked again; large immutable arrays
    # were hashed during final manifest generation and their independent reproduction.
    n=0
    for r in manifest['files']:
        f=P/r['path'];assert f.exists() and f.stat().st_size==r['bytes'],f
        if f.suffix in {'.md','.tex','.py','.json','.csv','.pdf','.bib','.bst','.sty'}:
            assert sha(f)==r['sha256'],f;n+=1
    print(json.dumps(dict(status='PASS',installed_files=len(records),package_entries=manifest['zip_entries'],
                         manifest_files=len(manifest['files']),final_source_report_hashes_checked=n,
                         main_and_supplement_installed_and_packaged_identically=True)))
if __name__=='__main__':main()
