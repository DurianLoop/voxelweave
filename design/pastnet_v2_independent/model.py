from pastnet_v2.model import PASTNetV2


class CorrespondenceOnly(PASTNetV2):
    """Same mature G086 backbone, only pre-fusion multiscale correspondence added."""
    def __init__(self):
        super().__init__('correspondence')
        # No weights or feature modulation from the unsuccessful geometry model.
        self.base.single.physical_adapter=None
        self.variant='correspondence_only'

    def forward_components(self,batch):
        # Isolate correspondence as a single variable. Positional priors here use
        # the same index/phase information already present in G086, not new mm.
        local=dict(batch)
        p=batch['physical'].clone()
        p[:,:,:14]=0
        p[:,:,15:17]=0
        local['physical']=p
        local['anchor_z']=batch['anchor_z'].new_tensor([-4.,0.,4.,8.])[None].expand(batch['cond'].shape[0],-1)
        return super().forward_components(local)
