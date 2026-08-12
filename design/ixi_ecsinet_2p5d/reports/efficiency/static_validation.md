# ECSI-Net Static Validation

Overall: `PASS`

- [x] `ast_parse`: parsed 8 Python files
- [x] `forward_4ch_shape`: (2, 1, 16, 16)
- [x] `forward_6ch_shape`: (2, 1, 16, 16)
- [x] `return_parts`: change, coarse, coarse_grad, correction, mask, recon, residual
- [x] `reconstruction_formula`: recon == coarse + mask * residual
- [x] `mask_range`: min=0.110214, max=0.115006
- [x] `finite_batch_loss`: loss=0.384244
- [x] `batch_loss_parts`: grad, l1, mask_mean, mask_prior_l1, residual_l1
- [x] `checkpoint_roundtrip`: shape=(16, 16)
- [x] `stride_mismatch_guard`: Checkpoint stride=4, requested stride=2
- [x] `profile_output_isolation`: {"smoke": "D:\\MRI\\design\\ixi_ecsinet_2p5d\\runs\\smoke", "mini": "D:\\MRI\\design\\ixi_ecsinet_2p5d\\runs\\mini", "full_test115_x2": "D:\\MRI\\design\\ixi_ecsinet_2p5d\\runs\\full_test115_x2", "full_test115_x6": "D:\\MRI\\design\\ixi_ecsinet_2p5d\\runs\\full_test115_x6"}
- [x] `profile_strides`: smoke=x4, full_test115_x2=x2, full_test115_x6=x6
