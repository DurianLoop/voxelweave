import pastnet_v2.efficiency as benchmark
from .run import load_model


def main():
    benchmark.VARIANTS={'control':(False,False,False,False,4),'correspondence_only':(False,True,False,False,4)}
    benchmark.load_model=load_model
    benchmark.main()


if __name__=='__main__':
    main()
