from pastnet_v2.model import PASTNetV2
VARIANTS={'repair':(False,False,False,False,4)}
def make_model(variant):
    if variant!='repair':raise ValueError(variant)
    m=PASTNetV2('control');m.variant=variant;return m
