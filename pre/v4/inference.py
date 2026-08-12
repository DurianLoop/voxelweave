import os
import glob
import torch
import numpy as np
import nibabel as nib
from skimage.transform import resize
from skimage.exposure import match_histograms
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from models import GeneratorUNet
from utils import load_nifti, save_nifti

def correct_z_flicker(volume, window_size=5):
    print("Applying Z-axis smoothing...")
    vol_float = volume.astype(np.float32)
    num_slices = vol_float.shape[2]
    
    z_means = [np.mean(vol_float[:,:,z][vol_float[:,:,z]>1e-6]) if np.any(vol_float[:,:,z]>1e-6) else 0 for z in range(num_slices)]
    z_means = np.array(z_means)
    
    if window_size % 2 == 0: window_size += 1
    window_size = min(window_size, num_slices if num_slices % 2 != 0 else num_slices - 1)
    if window_size < 3: window_size = 3
    
    smooth_means = savgol_filter(z_means, window_size, 2)
    corrected = np.zeros_like(vol_float)
    
    for z in range(num_slices):
        gain = smooth_means[z] / z_means[z] if z_means[z] > 1e-6 else 1.0
        gain = np.clip(gain, 0.5, 2.0)
        corrected[:,:,z] = vol_float[:,:,z] * gain
        
    return np.clip(corrected, vol_float.min(), vol_float.max())

def robust_histogram_matching(source, template):
    src_mask = source > source.mean() * 0.1
    tmpl_mask = template > template.mean() * 0.1
    if not np.any(src_mask) or not np.any(tmpl_mask): return source
    return match_histograms(source, template, channel_axis=None)

class MRIInterpolator:
    def __init__(self, model_path, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.generator = GeneratorUNet(in_channels=6, out_channels=3).to(device)
        self.load_model(model_path)
        self.generator.eval()
        self.input_size = (512, 512)
        self.global_min, self.global_max = 0.0, 1.0

    def load_model(self, path):
        ckpt = torch.load(path, map_location=self.device)
        self.generator.load_state_dict(ckpt['generator_state_dict'] if 'generator_state_dict' in ckpt else ckpt)
        print(f"Model loaded: {path}")

    def interpolate_supersample(self, volume):
        """Z轴倍增 (4x: 4mm生成1mm)"""
        org_shape = volume.shape
        num_slices = org_shape[2]
        new_slices = (num_slices - 1) * 4 + 1
        
        self.global_min, self.global_max = np.percentile(volume, 0), np.percentile(volume, 100)
        norm_vol = (np.clip(volume, self.global_min, self.global_max) - self.global_min) / (self.global_max - self.global_min + 1e-8)
        
        result = np.zeros((org_shape[0], org_shape[1], new_slices), dtype=np.float32)
        
        # 填入原始层
        for i in range(num_slices):
            result[:, :, i * 4] = volume[:, :, i]
            
        print("Inferencing intermediate slices...")
        with torch.no_grad():
            for i in range(num_slices - 1):
                s_prev = resize(norm_vol[:,:,i], self.input_size, preserve_range=True)
                s_next = resize(norm_vol[:,:,i+1], self.input_size, preserve_range=True)
                
                # 位置编码
                z_pos = (i + 0.5) / (num_slices - 1)
                pos_map = np.full(self.input_size, z_pos, dtype=np.float32)
                rel_1 = np.full(self.input_size, 0.25, dtype=np.float32)
                rel_2 = np.full(self.input_size, 0.50, dtype=np.float32)
                rel_3 = np.full(self.input_size, 0.75, dtype=np.float32)
                
                inp = torch.FloatTensor(np.stack([s_prev, s_next, pos_map, rel_1, rel_2, rel_3])).unsqueeze(0).to(self.device)
                
                # 网络一次输出三张切片
                gen, _, _ = self.generator(inp)
                gen = gen.squeeze().cpu().numpy() # [3, H, W]
                
                t_vals = [0.25, 0.50, 0.75]
                for t_idx, t_val in enumerate(t_vals):
                    interp = resize(gen[t_idx], org_shape[:2], preserve_range=True)
                    interp = interp * (self.global_max - self.global_min) + self.global_min
                    
                    # 直方图匹配到相邻层按距离权重的均值
                    ref = volume[:,:,i] * (1 - t_val) + volume[:,:,i+1] * t_val
                    interp = robust_histogram_matching(interp, ref)
                    
                    # 填入对应的层位置
                    result[:, :, i * 4 + 1 + t_idx] = np.maximum(interp, 0)
                
        return correct_z_flicker(result)

    def process_folder(self, input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        files = glob.glob(os.path.join(input_folder, "*.nii.gz"))
        for f in files:
            print(f"Processing {os.path.basename(f)}...")
            vol, aff = load_nifti(f)
            res_vol = self.interpolate_supersample(vol.astype(np.float32))
            save_nifti(res_vol.astype(vol.dtype), aff, os.path.join(output_folder, f"up_{os.path.basename(f)}"))

if __name__ == "__main__":
    interpolator = MRIInterpolator("./checkpoints/pix2pix_epoch_best.pth")
    interpolator.process_folder("./gan_inputs", "./gan_outputs")
