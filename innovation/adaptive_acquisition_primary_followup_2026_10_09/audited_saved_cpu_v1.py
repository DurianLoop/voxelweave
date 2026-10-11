"""CPU copy saved-tensor hooks with exact content/shape/dtype/device round-trip audit."""
import gzip,json,time
from pathlib import Path
import torch
class _Saved:
 def __init__(self,cpu,device,index,owner):
  self.cpu=cpu;self.device=device;self.index=index;self.owner=owner;self.bytes=cpu.numel()*cpu.element_size();owner.live_bytes+=self.bytes;owner.peak_bytes=max(owner.peak_bytes,owner.live_bytes)
 def __del__(self):self.owner.live_bytes-=self.bytes
class CpuSavedTensorAudit:
 def __init__(self,hash_function,guard):self.hash_function=hash_function;self.guard=guard;self.records=[];self.live_bytes=0;self.peak_bytes=0;self.unpacks=0
 def pack(self,value):
  cpu=value.detach().to('cpu',copy=True);index=len(self.records);self.records.append(dict(id=index,shape=list(value.shape),dtype=str(value.dtype),device=str(value.device),logical_bytes=cpu.numel()*cpu.element_size(),sha256=self.hash_function(cpu.numpy()),unpack_events=[]))
  if len(self.records)%16==0:self.guard()
  return _Saved(cpu,value.device,index,self)
 def unpack(self,saved):
  q=self.records[saved.index];assert list(saved.cpu.shape)==q['shape'] and str(saved.cpu.dtype)==q['dtype'] and self.hash_function(saved.cpu.numpy())==q['sha256']
  restored=saved.cpu.to(saved.device,copy=True);roundtrip=restored.detach().to('cpu');assert torch.equal(saved.cpu,roundtrip) and self.hash_function(roundtrip.numpy())==q['sha256'] and restored.device==saved.device
  q['unpack_events'].append(dict(bitwise_equal=True,sha256=q['sha256'],shape_dtype_device_equal=True));self.unpacks+=1;del roundtrip
  if self.unpacks%16==0:self.guard()
  return restored
 def context(self):return torch.autograd.graph.saved_tensors_hooks(self.pack,self.unpack)
 def write(self,path):
  assert self.records and self.unpacks
  with Path(path).open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
   for q in self.records:f.write((json.dumps(q,separators=(',',':'))+'\n').encode('utf-8'))
  return dict(packed_tensors=len(self.records),unpack_events=self.unpacks,CPU_saved_peak_logical_bytes=self.peak_bytes,CPU_saved_final_logical_bytes=self.live_bytes,all_actual_unpacks_bitwise_verified=True)
