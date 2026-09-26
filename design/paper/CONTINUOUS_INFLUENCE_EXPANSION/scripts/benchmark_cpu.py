from adapters import *
import time,json,gc
def main():
    torch.set_num_threads(4)
    row=read(B/'case_registry.json')[0];ds=row['dataset'];z=row['influence_targets'][0]
    pool,lo,scale,mask=inputs(B/'inputs'/f'{ds}_{row["case"]}_z{z}.npz');cs=conditions(pool,z,REF,REF[0],patterns(),.01)
    results=[]
    for m,module,cls in [('resunet','ixi_diffusion.resunet','ResUNetResidualInterpolator'),('smamba_unet','ixi_smamba_unet_2p5d.train','SMambaUNet2p5DInterpolator')]:
        r=next(r for r in read(P/'model_registry.json') if r['dataset']==ds and r['model']==m)
        net=getattr(importlib.import_module(module),cls)(ROOT/r['checkpoint'],device='cpu')
        for j in range(3):
            t=time.perf_counter();q=normalized(net,m,cs,REF);elapsed=time.perf_counter()-t
            results.append(dict(model=m,device='cpu',threads=4,batch=4,repeat=j,seconds=elapsed,finite=bool(np.isfinite(q).all())))
            print(results[-1],flush=True)
        del net;gc.collect()
    write(P/'outputs/cpu_engineering_benchmark.json',results)
if __name__=='__main__':main()
