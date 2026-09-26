import copy,hashlib,json
from pathlib import Path
import nibabel as nib
import numpy as np
from pastnet_v2.common import sha256,write_json
from .audit import ROOT,SOURCE

MANIFEST=ROOT/'manifests/fastmri_repaired.json'
def validation_hash(content):
    records=[r for r in content['records'] if r['split']=='val']
    return hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    if MANIFEST.exists():raise FileExistsError('Prepared dataset already exists; do not silently rebuild')
    source=json.loads(SOURCE.read_text(encoding='utf-8'));mapping=json.loads((ROOT/'results/repair_mapping.json').read_text())
    rec=next(r for r in source['records'] if r['case_id']==mapping['case_id']);old=nib.load(rec['path']).get_fdata(dtype=np.float32)
    assert sha256(rec['path'])==mapping['original_sha256']
    replacements=[];data_hashes={}
    for group in mapping['groups']:
        rows=group['slices'];indices=[x['old_index'] for x in rows];volume=old[:,:,indices].copy()
        orient=np.array(rows[0]['orientation']);normal=np.cross(orient[:3],orient[3:])
        ras=np.diag([-1.,-1.,1.]);axes=ras@np.stack([orient[3:],orient[:3],normal],axis=1)
        spacing=[*rows[0]['pixel_spacing'],group['spacing_z']];affine=np.eye(4)
        affine[:3,:3]=axes@np.diag(spacing);affine[:3,3]=ras@np.array(rows[0]['position'])
        new=copy.deepcopy(rec);new['case_id']=rec['case_id']+'_uid_'+group['uid_sha256'][:12]
        path=ROOT/'data'/(new['case_id']+'.nii.gz');path.parent.mkdir(exist_ok=True)
        if path.exists():raise FileExistsError(path)
        nib.save(nib.Nifti1Image(volume,affine),path)
        assert np.array_equal(nib.load(path).get_fdata(dtype=np.float32),volume)
        z=np.array([r['projected_z'] for r in rows]);new.update(path=str(path.resolve()),shape=list(volume.shape),
            geometry=dict(spacing=spacing,axes=axes.tolist(),z_mm=(z-z[0]).tolist(),spacing_known=1,orientation_known=1,
                source='DICOM_SeriesInstanceUID_separated_all_pixels_verified',nonuniformity=float(np.std(np.diff(z))/np.mean(np.diff(z)))))
        replacements.append(new);data_hashes[str(path.relative_to(ROOT))]=sha256(path)
    out=copy.deepcopy(source);out['records']=[r for r in out['records'] if r['case_id']!=rec['case_id']]+replacements
    assert validation_hash(source)==validation_hash(out)
    out['training_repair']=dict(original_manifest_sha256=sha256(SOURCE),case_id=rec['case_id'],replacement_cases=[r['case_id'] for r in replacements],
        validation_sha256=validation_hash(out),data_hashes=data_hashes,repair_mapping_sha256=sha256(ROOT/'results/repair_mapping.json'))
    write_json(MANIFEST,out);print('Prepared independent volumes and manifest; originals unchanged.')
if __name__=='__main__':main()
