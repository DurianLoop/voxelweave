# 已失败人工 v2：一次更新放大定位（预设）

旧 gin_cpu_reference_verification_attempt02/receipt.json、所有实现和阈值不改。新增 CPU 人工诊断，使用相同初值seed20261009、输入seed49、target501、GIN480000–480002、shape(2,1,16,16,16)，同production与FP64-norm reference、原AdamW lr1e-4/weight_decay1e-4/eps1e-8/betas(.9,.999)。每分支1次step0、3view、1backward，新增合计2人工CPU optimizer updates；不运行step1/MRI/GT/parent/GPU。

完整54参数与162state的原五类maxerror须逐值复现旧receipt。为每个参数保存最大更新差坐标、两个原始梯度/初值/更新值/一阶及二阶moments及hash，不只挑最坏层。用独立NumPy double首步AdamW数学式 p(1-lr*wd)-lr*g/(|g|+eps) 预测全部元素，误差阈值仍3e-6，记录实际最大值；公式检查仅验证更新放大，不认证两个模型通过既有参数gate。最坏坐标究竟同号/异号由数据决定，不预判。

CPU1/interop1/below-normal、no CUDA、wall180秒、receipt≤100KB；prep7MB/FOV20MB/accepted6MB/adaptive2MB/other22.8MB不变，freshfree扣所有未用cap≥8GB。独立audit只读新旧receipt、绑定和算术，不重跑模型。若复现/数学式检查失败就留下真实失败、停止。绝不改eps、钳制小梯度、降低gate或重称医学验证通过。
