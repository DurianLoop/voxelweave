import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

def load_nifti(file_path):
    """加载NIfTI文件并返回数据和affine矩阵"""
    img = nib.load(file_path)
    data = img.get_fdata()
    affine = img.affine
    return data, affine

def save_nifti(data, affine, file_path):
    """保存数据为NIfTI文件"""
    img = nib.Nifti1Image(data, affine)
    nib.save(img, file_path)

def normalize_image(image):
    """标准化图像到[0,1]范围"""
    image = image.astype(np.float32)
    if image.max() == image.min():
        return np.zeros_like(image)
    normalized = (image - image.min()) / (image.max() - image.min() + 1e-8)
    return normalized

def create_slice_pairs(volume):
    """
    从3D体积创建切片对
    返回: [(slice0, slice2, slice1, current_idx, total_slices), ...]
    """
    pairs = []
    num_slices = volume.shape[2]
    
    # 至少需要3张切片
    if num_slices < 3:
        return []

    for i in range(1, num_slices - 1):
        input_slice1 = volume[:, :, i-1]  # 前一个切片
        input_slice2 = volume[:, :, i+1]  # 后一个切片
        target_slice = volume[:, :, i]    # 中间切片（目标）
        
        # 保存 (前, 后, 目标, 当前索引, 总切片数)
        pairs.append((input_slice1, input_slice2, target_slice, i, num_slices))
    
    return pairs

def plot_training_progress(generator, discriminator, g_losses, d_losses, save_path):
    """绘制训练进度"""
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(g_losses, label='Generator Loss')
    plt.plot(d_losses, label='Discriminator Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training Losses')
    
    plt.subplot(1, 2, 2)
    plt.plot(g_losses, label='Generator Loss', alpha=0.7)
    plt.plot(d_losses, label='Discriminator Loss', alpha=0.7)
    plt.yscale('log')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (log scale)')
    plt.legend()
    plt.title('Training Losses (Log Scale)')
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

class EarlyStopping:
    def __init__(self, patience=10, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        
    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0