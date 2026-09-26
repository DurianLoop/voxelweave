from pastnet_v2.model import PASTNetV2
VARIANTS={'orientation':(False,False,False,False,4),'identity':(False,False,False,False,4)}
def make_model(variant):
    if variant not in VARIANTS:raise ValueError(variant)
    model=PASTNetV2('control');model.variant=variant;return model
