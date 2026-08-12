import os
import glob
import torch
import numpy as np
import nibabel as nib
from skimage.transform import resize
from skimage.exposure import match_histograms
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from v4.v2.models import GeneratorUNet
from v4.v2.utils import load_nifti, save_nifti

# --- Post-Processing: Fix Flickering ---
def correct_z_flicker(volume, window_size=5):
    """Z轴亮度平滑，解决生成层忽明忽暗的问题"""
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
    """仅对前景区域进行直方图匹配"""
    src_mask = source > source.mean() * 0.1
    tmpl_mask = template > template.mean() * 0.1
    if not np.any(src_mask) or not np.any(tmpl_mask): return source
    return match_histograms(source, template, channel_axis=None)

# --- Inference ---
class MRIInterpolator:
    def __init__(self, model_path, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.generator = GeneratorUNet(in_channels=3, out_channels=1).to(device)
        self.load_model(model_path)
        self.generator.eval()
        self.input_size = (512, 512)
        self.global_min, self.global_max = 0.0, 1.0

    def load_model(self, path):
        ckpt = torch.load(path, map_location=self.device)
        self.generator.load_state_dict(ckpt['generator_state_dict'] if 'generator_state_dict' in ckpt else ckpt)
        print(f"Model loaded: {path}")

    def interpolate_supersample(self, volume):
        """Z轴倍增 (2x)"""
        org_shape = volume.shape
        num_slices = org_shape[2]
        new_slices = num_slices * 2 - 1
        
        # 全局归一化
        self.global_min, self.global_max = np.percentile(volume, 0), np.percentile(volume, 100)
        norm_vol = (np.clip(volume, self.global_min, self.global_max) - self.global_min) / (self.global_max - self.global_min + 1e-8)
        
        result = np.zeros((org_shape[0], org_shape[1], new_slices), dtype=np.float32)
        
        # 填入原始层
        for i in range(num_slices):
            result[:, :, i * 2] = volume[:, :, i]
            
        print("Inferencing intermediate slices...")
        with torch.no_grad():
            for i in range(0, new_slices - 1, 2):
                idx_prev, idx_next = i // 2, (i + 2) // 2
                
                s_prev = resize(norm_vol[:,:,idx_prev], self.input_size, preserve_range=True)
                s_next = resize(norm_vol[:,:,idx_next], self.input_size, preserve_range=True)
                
                # 位置编码
                z_pos = (idx_prev + idx_next) / 2.0 / (num_slices - 1)
                pos_map = np.full(self.input_size, z_pos, dtype=np.float32)
                
                inp = torch.FloatTensor(np.stack([s_prev, s_next, pos_map])).unsqueeze(0).to(self.device)
                
                # !! 获取生成结果 (忽略 flow 和 coarse) !!
                gen, _, _ = self.generator(inp)
                gen = gen.squeeze().cpu().numpy()
                
                # 后处理
                interp = resize(gen, org_shape[:2], preserve_range=True)
                interp = interp * (self.global_max - self.global_min) + self.global_min
                
                # 直方图匹配到相邻层均值
                ref = (volume[:,:,idx_prev] + volume[:,:,idx_next]) / 2.0
                interp = robust_histogram_matching(interp, ref)
                
                result[:, :, i + 1] = np.maximum(interp, 0)
                
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
