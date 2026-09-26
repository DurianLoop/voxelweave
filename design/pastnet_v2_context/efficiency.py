import pastnet_v2.efficiency as benchmark
from .model import VARIANTS
from .run import load_model

if __name__=='__main__':
    benchmark.VARIANTS=VARIANTS;benchmark.load_model=load_model;benchmark.main()
