"""Independent scalar norm objective in60-digit Decimal; no torch/module execution."""
from decimal import Decimal as D,localcontext
def decimal_norm_objective(actual,dy,index,direction,h,sign):
 with localcontext() as ctx:
  ctx.prec=60
  flat=[list(v.reshape(-1)) for v in actual]
  values=[[D.from_float(float(v)) for v in row] for row in flat]
  step=D.from_float(float(h))*sign
  values[index]=[v+step*D.from_float(float(d)) for v,d in zip(values[index],direction.reshape(-1))]
  x,w,b=values;batch,channels=actual[0].shape[:2];spatial=actual[0].size//(batch*channels);truth=[D.from_float(float(v)) for v in dy.reshape(-1)]
  total=D(0)
  for n in range(batch):
   for c in range(channels):
    lo=(n*channels+c)*spatial;segment=x[lo:lo+spatial];mean=sum(segment,D(0))/spatial
    centered=[v-mean for v in segment];scale=(sum((v*v for v in centered),D(0))/spatial+D('0.00001')).sqrt()
    total+=sum((truth[lo+i]*(v/scale*w[c]+b[c]) for i,v in enumerate(centered)),D(0))
  return +total
