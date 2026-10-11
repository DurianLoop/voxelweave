"""Shared resource/IO audit only; contains no interpolation or input construction."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from mc_rc_reference_resources_2026_10_07 import resource_guard

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 20_000_000


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def entry(path):
    p = Path(path)
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def arrsha(a):
    import numpy as np
    a = np.ascontiguousarray(a)
    h = hashlib.sha256(json.dumps(dict(shape=list(a.shape), dtype=a.dtype.str), sort_keys=True).encode())
    h.update(memoryview(a).cast('B'))
    return h.hexdigest()


class StageAudit:
    def __init__(self, out, torch, allowed, started):
        self.out, self.torch, self.started = out.resolve(), torch, started
        self.allowed = {str((ROOT/p).resolve()).lower() for p in allowed}
        self.reads, self.denied, self.observed_opens = set(), [], []
        assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
        sys.addaudithook(self.audit)

    def audit(self, event, args):
        if event != 'open' or not args or not isinstance(args[0], (str, bytes)):
            return
        try:
            p = Path(args[0]).resolve()
        except (OSError, ValueError, TypeError):
            return
        mode = args[1] if len(args) > 1 else None
        reading = not isinstance(mode, str) or 'r' in mode or '+' in mode
        if isinstance(mode, str) and any(t in mode for t in ('w', 'a', 'x', '+')):
            if not p.is_relative_to(self.out):
                self.denied.append(str(p))
                raise PermissionError('Stage write outside its new attempt: '+str(p))
        if reading and p.is_relative_to(ROOT):
            rel = p.relative_to(ROOT).as_posix()
            prohibited = (p.name.endswith(('.zip', '.nii', '.nii.gz', '.pt', '.npy')) or
                          any(t in rel for t in ('mc_rc_validation_task', 'mc_rc_true_native_reference_attempt',
                                                'confirmation', 'locked_ixi')))
            if p.suffix == '.npz' and str(p).lower() not in self.allowed:
                prohibited = True
            if prohibited:
                self.denied.append(rel)
                raise PermissionError('Stage prohibited native/GT/other medical/model source: '+rel)
            self.reads.add(rel)
            # Hash byte IO and actual NumPy loads are separately counted by each caller.

    def guard(self):
        assert time.perf_counter()-self.started <= 1200, '1200s stage job budget exceeded'
        r = resource_guard()
        assert self.torch.get_num_threads() == self.torch.get_num_interop_threads() == 1
        assert not self.torch.cuda.is_initialized()
        saved = sum(p.stat().st_size for p in self.out.rglob('*') if p.is_file())
        assert saved <= LIMIT
        r.update(stage_saved_bytes=saved, stage_saved_limit=LIMIT, cuda_initialized=False,
                 interop_threads=1, new_stage_max_saved_bytes=LIMIT)
        return r

    def result(self):
        return dict(workspace_read_paths=sorted(self.reads), prohibited_access_attempts=self.denied,
                    NPZ_read_whitelist=sorted(self.allowed),
                    native_GT_validation_confirmation_pixels_read=False)
