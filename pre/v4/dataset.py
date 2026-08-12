import os
import glob
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from utils import load_nifti, normalize_image, create_slice_pairs
from skimage.transform import resize

class MRIDataset(Dataset):
    def __init__(self, data_folder, target_shape=(256, 256), transform=None):
        self.data_folder = data_folder
        self.target_shape = target_shape
        self.transform = transform
        self.slice_pairs = []
        
        nifti_files = glob.glob(os.path.join(data_folder, "*.nii.gz"))
        print(f"Found {len(nifti_files)} NIfTI files")
        
        for file_path in nifti_files:
            try:
                volume, affine = load_nifti(file_path)
                volume = normalize_image(volume)
                
                # 创建切片对 (默认 gap=4)
                pairs = create_slice_pairs(volume, gap=4)
                self.slice_pairs.extend(pairs)
                
                print(f"Loaded {file_path}: {volume.shape} -> {len(pairs)} slice pairs")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        print(f"Total slice pairs: {len(self.slice_pairs)}")
    
    def __len__(self):
        return len(self.slice_pairs)
    
    def __getitem__(self, idx):
        slice1, slice2, target, current_idx, total_slices, gap = self.slice_pairs[idx]
        
        # 调整大小
        slice1 = resize(slice1, self.target_shape, preserve_range=True, anti_aliasing=True)
        slice2 = resize(slice2, self.target_shape, preserve_range=True, anti_aliasing=True)
        
        # 针对 3 张 Target 进行调整
        target_resized = np.zeros((*self.target_shape, gap - 1), dtype=np.float32)
        for c in range(gap - 1):
            target_resized[:, :, c] = resize(target[:, :, c], self.target_shape, preserve_range=True, anti_aliasing=True)
        target = target_resized.transpose(2, 0, 1)  # [3, H, W]
        
        # --- 创建位置编码通道 ---
        # 1. 全局位置编码 (取两张输入切片的中间位置)
        z_pos = (current_idx + gap / 2.0) / (total_slices - 1) if total_slices > 1 else 0.5
        global_pos = np.full_like(slice1, z_pos, dtype=np.float32)
        
        # 2. 相对位置编码 (引入 t=0.25, 0.50, 0.75)
        rel_pos_1 = np.full_like(slice1, 0.25, dtype=np.float32)
        rel_pos_2 = np.full_like(slice1, 0.50, dtype=np.float32)
        rel_pos_3 = np.full_like(slice1, 0.75, dtype=np.float32)
        
        # 组合输入：[Prev, Next, Global_Pos, Rel_Pos_1, Rel_Pos_2, Rel_Pos_3] -> 6通道
        input_slices = np.stack([slice1, slice2, global_pos, rel_pos_1, rel_pos_2, rel_pos_3], axis=0) 
        
        input_slices = torch.FloatTensor(input_slices)
        target_slices = torch.FloatTensor(target) # target 已经是 [3, H, W]
        
        if self.transform:
            input_slices = self.transform(input_slices)
            target_slices = self.transform(target_slices)
        
        return input_slices, target_slices

def get_dataloaders(data_folder, batch_size=4, target_shape=(256, 256), validation_split=0.2):
    from torch.utils.data import random_split
    dataset = MRIDataset(data_folder, target_shape=target_shape)
    val_size = int(len(dataset) * validation_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    num_workers = int(os.environ.get("MRI_NUM_WORKERS", "0"))
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
    return train_loader, val_loader
