"""Unchanged per-stage caps, reserve unspent allowance only; own-process guard."""
import sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,read,entry,bind,dump
CAPS=((ROOT/'six_resolution_training_preparation_2026_10_09',7000000),
 (ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20000000),
 (ROOT/'gin_accepted_primary_followup_2026_10_09',6000000),(HERE,2000000))
def guard(started=None,wall=180):
 v=resource_guard();remaining=22800000;sizes={}
 for d,cap in CAPS:
  size=sum(p.stat().st_size for p in d.rglob('*') if p.is_file());assert size<cap,(d,size,cap)
  sizes[d.name]=size;remaining+=cap-size
 assert v['workspace_free_bytes']-remaining>=8000000000
 if started is not None:assert time.perf_counter()-started<wall
 v.update(remaining_all_stage_allowance_bytes=remaining,stage_sizes_bytes=sizes,
  guarded_workspace_free_bytes=v['workspace_free_bytes']-remaining)
 return v
