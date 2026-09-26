"""Meaningful leakage / boundary / solver tests, independent of learned accuracy."""
import json
import copy
import tempfile
import unittest
from pathlib import Path
import nibabel as nib
import numpy as np
import torch
import pandas as pd
from unittest.mock import patch
from .data import IntervalDataset,build_sample
from .inference import interpolate_sparse
from .losses import smooth_cvar
from .losses import objective
from .model import PASTNetV2
from .report import paired_report


class Contracts(unittest.TestCase):
    def test_micro_batch_and_partial_checkpoint_gradients(self):
        torch.set_num_threads(2);torch.manual_seed(3407)
        geo=dict(spacing=[1,1,5],axes=np.eye(3).tolist(),z_mm=(np.arange(17)*5).tolist(),
                 spacing_known=1,orientation_known=1)
        rec=dict(case_id='a',patient_id='a',shape=[16,16,17],geometry=geo)
        v=np.random.default_rng(3407).random((16,16,17)).astype(np.float32)
        samples=[build_sample(v,rec,z,16,4) for z in (0,4,8)]
        batch={k:torch.stack([s[k] for s in samples]) for k in samples[0] if isinstance(samples[0][k],torch.Tensor)}
        full=PASTNetV2('control',base_channels=8,num_blocks=3,context_blocks=1,aggressive_channels=8).train()
        micro=copy.deepcopy(full);micro.base.single.checkpoint_blocks=1
        loss,_=objective(full,batch,1,80)
        loss.backward()
        for start,stop in ((0,2),(2,3)):
            piece={k:v[start:stop] for k,v in batch.items()}
            loss,_=objective(micro,piece,1,80)
            (loss*(stop-start)/3).backward()
        for (n,p),(mn,mp) in zip(full.named_parameters(),micro.named_parameters()):
            self.assertEqual(n,mn)
            if p.grad is not None:
                self.assertTrue(torch.allclose(p.grad,mp.grad,atol=2e-5,rtol=1e-3),n)

    def test_pairing_refuses_missing_patient(self):
        m=dict(seed=3407,data_sha256='same',init_sha256='same',variant='geometry')
        candidate=pd.DataFrame({'psnr':[25.,26.]},index=['a','b'])
        parent=pd.DataFrame({'psnr':[24.,25.]},index=['a','c'])
        with patch('pastnet_v2.report.load_run',side_effect=[(m,candidate),(m,parent)]):
            with self.assertRaisesRegex(ValueError,'Patient sets differ'):
                paired_report(['synthetic_candidate'],['synthetic_parent'],.08)

    def test_missing_target_extrema_do_not_change_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'volume.nii.gz'
            v=np.random.default_rng(42).random((16,16,17)).astype(np.float32)
            geo=dict(spacing=[1,1,5],axes=np.eye(3).tolist(),z_mm=(np.arange(17)*5).tolist(),
                     spacing_known=1,orientation_known=1)
            r=dict(case_id='a',patient_id='a',path=str(path),split='val',shape=list(v.shape),geometry=geo)
            manifest=root/'manifest.json';manifest.write_text(json.dumps(dict(records=[r])))
            nib.save(nib.Nifti1Image(v,np.eye(4)),path)
            first=IntervalDataset(manifest,'val',image_size=16)[0]
            v[:,:,1::4]=1e6
            nib.save(nib.Nifti1Image(v,np.eye(4)),path)
            second=IntervalDataset(manifest,'val',image_size=16)[0]
            for key in ('cond','anchors','valid','physical','anchor_z'):
                self.assertTrue(torch.equal(first[key],second[key]),key)
            self.assertFalse(torch.equal(first['target'],second['target']))
            with self.assertRaises(ValueError):
                IntervalDataset(manifest,'test')

    def test_only_actual_sparse_indices_and_anchor_clamp(self):
        torch.set_num_threads(2)
        v=np.stack([np.full((16,16),z,np.float32) for z in range(17)],axis=2)
        geo=dict(spacing=[1,1,5],axes=np.eye(3).tolist(),z_mm=(np.arange(17)*5).tolist(),
                 spacing_known=1,orientation_known=1)
        rec=dict(case_id='a',patient_id='a',shape=v.shape,geometry=geo)
        sample=build_sample(v,rec,0,16,6)
        self.assertEqual(sample['valid'].tolist(),[0,0,1,1,1,1])
        self.assertTrue(all(int(x)%4==0 for x in sample['anchors'][:,0,0,0]))
        model=PASTNetV2('correspondence',base_channels=8,num_blocks=1,context_blocks=1,aggressive_channels=8)
        result=interpolate_sparse(model,v[:,:,::4],geo,image_size=16,amp=False)
        self.assertTrue(np.array_equal(result[:,:,::4],v[:,:,::4]))
        self.assertEqual(result.shape,v.shape)
        self.assertTrue(np.isfinite(result).all())

    def test_smooth_cvar_envelope_gradient(self):
        x=torch.tensor([[[[.001,.002,.003,.020]]]],requires_grad=True)
        value=smooth_cvar(x,alpha=.75,temperature=.002)
        grad=torch.autograd.grad(value,x)[0]
        eps=1e-5
        for i in range(4):
            plus=x.detach().clone();minus=plus.clone()
            plus.reshape(-1)[i]+=eps;minus.reshape(-1)[i]-=eps
            fd=(smooth_cvar(plus,alpha=.75)-smooth_cvar(minus,alpha=.75))/(2*eps)
            self.assertAlmostEqual(float(fd),float(grad.reshape(-1)[i]),delta=.002)


if __name__=='__main__':
    unittest.main()
