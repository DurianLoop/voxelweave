import os
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import torch

# 保持随机种子设定，确保环境一致性
torch.manual_seed(3407)
np.random.seed(3407)

# 路径配置
pred_path = 'gan_outputs/up_091.nii.gz'
gt_path = '/data/ZH/diffusers-main/data(10101)/091.nii.gz'
output_dir = './vis'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

print("正在加载 NIfTI 数据...")
# 加载体数据
pred_data = nib.load(pred_path).get_fdata()
gt_data = nib.load(gt_path).get_fdata()

# 获取 Z 轴的维度大小
z_len_pred = pred_data.shape[2]
z_len_gt = gt_data.shape[2]

# 取两个体数据 Z 轴长度的最小值，作为安全遍历的边界
min_z_len = min(z_len_pred, z_len_gt)
print(f"推理数据 Z 轴长度: {z_len_pred}, GT 数据 Z 轴长度: {z_len_gt}")

# 生成有效范围内的所有奇数切片索引：1, 3, 5, 7, 9...
target_slices = range(1, min_z_len, 2)

for z_idx in target_slices:
    # 提取 Z 轴对应的切片数据
    pred_slice = pred_data[:, :, z_idx]
    gt_slice = gt_data[:, :, z_idx]
    
    # 计算绝对误差
    error_map = np.abs(pred_slice - gt_slice)
    
    # 开始绘图
    plt.figure(figsize=(8, 6))
    
    # 使用 vmin=0 和 vmax=1000 固定色带映射范围
    im = plt.imshow(error_map, cmap='jet', origin='lower', vmin=0, vmax=500) 
    
    # 添加颜色条，extend='max' 表示超过 1000 的值用最高端的颜色（红色）表示
    cbar = plt.colorbar(im, extend='max')
    cbar.set_label('Absolute Error', rotation=270, labelpad=15)
    
    plt.title(f'Error Heatmap - Z-Slice {z_idx:03d}')
    plt.axis('off')
    
    # 保存图像
    save_path = os.path.join(output_dir, f'error_heatmap_slice_{z_idx:03d}.png')
    plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor='white')
    plt.close() # 关闭图表以释放内存
    
print(f"全部绘制完成！共生成 {len(target_slices)} 张误差热力图，保存在 {output_dir} 目录中。")
