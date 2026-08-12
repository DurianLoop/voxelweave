import os
import glob
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from v4.v2.utils import load_nifti, normalize_image, create_slice_pairs
from skimage.transform import resize

class MRIDataset(Dataset):
    def __init__(self, data_folder, target_shape=(256, 256), transform=None):
        self.data_folder = data_folder
        self.target_shape = target_shape
        self.transform = transform
        self.slice_pairs = []
        
        # 查找所有NIfTI文件
        nifti_files = glob.glob(os.path.join(data_folder, "*.nii.gz"))
        print(f"Found {len(nifti_files)} NIfTI files")
        
        for file_path in nifti_files:
            try:
                volume, affine = load_nifti(file_path)
                volume = normalize_image(volume)
                
                # 创建切片对
                pairs = create_slice_pairs(volume)
                self.slice_pairs.extend(pairs)
                
                print(f"Loaded {file_path}: {volume.shape} -> {len(pairs)} slice pairs")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        print(f"Total slice pairs: {len(self.slice_pairs)}")
    
    def __len__(self):
        return len(self.slice_pairs)
    
    def __getitem__(self, idx):
        # 解包元组
        slice1, slice2, target, current_idx, total_slices = self.slice_pairs[idx]
        
        # 调整大小
        slice1 = resize(slice1, self.target_shape, preserve_range=True, anti_aliasing=True)
        slice2 = resize(slice2, self.target_shape, preserve_range=True, anti_aliasing=True)
        target = resize(target, self.target_shape, preserve_range=True, anti_aliasing=True)
        
        # --- 创建位置编码通道 ---
        # 计算相对位置 [0, 1]
        z_pos = current_idx / (total_slices - 1) if total_slices > 1 else 0.5
        # 创建一个全为 z_pos 的矩阵
        pos_channel = np.full_like(slice1, z_pos, dtype=np.float32)
        
        # 转换为PyTorch张量
        # 输入是3个通道: [Prev, Next, Position]
        input_slices = np.stack([slice1, slice2, pos_channel], axis=0)  # [3, H, W]
        target_slice = target[np.newaxis, ...]  # [1, H, W]
        
        input_slices = torch.FloatTensor(input_slices)
        target_slice = torch.FloatTensor(target_slice)
        
        if self.transform:
            input_slices = self.transform(input_slices)
            target_slice = self.transform(target_slice)
        
        return input_slices, target_slice

def get_dataloaders(data_folder, batch_size=4, target_shape=(256, 256), validation_split=0.2):
    """创建训练和验证数据加载器"""
    from torch.utils.data import random_split
    
    dataset = MRIDataset(data_folder, target_shape=target_shape)
    
    val_size = int(len(dataset) * validation_split)
    train_size = len(dataset) - val_size
    
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=24, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=24, pin_memory=True)
    
    return train_loader, val_loader