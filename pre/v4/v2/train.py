import torch
import random
import numpy as np
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import os
import time
from tqdm import tqdm
import torchvision.models as models 
from pytorch_msssim import ssim

from v4.v2.models import GeneratorUNet, Discriminator
from dataset import get_dataloaders
from v4.v2.utils import plot_training_progress
from v4.v2.config import MODEL_CONFIG

def set_seed(seed=3407):
    # 1. 设置 Python 内置随机数生成器的种子
    random.seed(seed)
    
    # 2. 设置 Numpy 随机数生成器的种子
    np.random.seed(seed)
    
    # 3. 设置 PyTorch CPU 随机数生成器的种子
    torch.manual_seed(seed)
    
    # 4. 设置 PyTorch 当前 GPU 随机数生成器的种子
    torch.cuda.manual_seed(seed)
    
    # 5. 设置 PyTorch 所有可用 GPU 随机数生成器的种子（如果你使用多块 GPU）
    torch.cuda.manual_seed_all(seed)
    
    # 6. 针对 CuDNN 的设置（保证卷积等操作的强可复现性）
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# 调用函数
set_seed(3407)

# --- 感知损失类 (VGG Loss) ---
class VGGLoss(nn.Module):
    def __init__(self, device):
        super(VGGLoss, self).__init__()
        # 使用预训练的 VGG19 提取特征
        vgg = models.vgg19(pretrained=True).features
        self.vgg = nn.Sequential(*list(vgg.children())[:36]).to(device).eval()
        for param in self.vgg.parameters():
            param.requires_grad = False
        self.criterion = nn.L1Loss()
        self.register_buffer('mean', torch.Tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(device))
        self.register_buffer('std', torch.Tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(device))

    def forward(self, x, y):
        x = (x + 1) / 2
        y = (y + 1) / 2
        if x.shape[1] == 1: x = x.repeat(1, 3, 1, 1)
        if y.shape[1] == 1: y = y.repeat(1, 3, 1, 1)
        x = (x - self.mean) / self.std
        y = (y - self.mean) / self.std
        return self.criterion(self.vgg(x), self.vgg(y))

def smoothness_loss(flow):
    """计算流场平滑度 (Total Variation)"""
    dy = torch.abs(flow[:, :, 1:, :] - flow[:, :, :-1, :])
    dx = torch.abs(flow[:, :, :, 1:] - flow[:, :, :, :-1])
    return torch.mean(dx) + torch.mean(dy)

# --- 主训练类 ---
class Pix2PixTrainer:
    def __init__(self, data_folder, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.data_folder = data_folder
        
        # 初始化模型
        self.generator = GeneratorUNet(in_channels=3, out_channels=1).to(device)
        self.discriminator = Discriminator(in_channels=4).to(device)
        
        # 损失函数
        self.adversarial_criterion = nn.MSELoss().to(device)
        self.vgg_criterion = VGGLoss(device)
        
        # 优化器
        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        # 训练记录
        self.g_losses = []
        self.d_losses = []
        self.val_losses = []
        
        # [新增] 记录最佳验证集Loss
        self.best_val_loss = float('inf')
        
        # 创建输出目录
        os.makedirs('./checkpoints', exist_ok=True)
        os.makedirs('./training_plots', exist_ok=True)
        
        self.discriminator_output_shape = None

    def _get_d_shape(self, B, H, W):
        """动态获取判别器输出尺寸"""
        if self.discriminator_output_shape is None:
            dummy = torch.randn(B, 4, H, W).to(self.device)
            with torch.no_grad():
                out = self.discriminator.model(dummy)
            self.discriminator_output_shape = out.shape[2:]
        return self.discriminator_output_shape
    
    def train_epoch(self, dataloader, epoch, total_epochs):
        self.generator.train()
        self.discriminator.train()
        g_loss_accum, d_loss_accum = 0, 0
        
        # 动态衰减策略
        decay_steps = total_epochs // 2
        if epoch < decay_steps:
            coarse_weight = 25.0 * (1.0 - epoch / decay_steps)
        else:
            coarse_weight = 0.0
            
        pbar = tqdm(dataloader, desc=f'Epoch {epoch}')
        for i, (input_slices, target_slices) in enumerate(pbar):
            B, _, H, W = input_slices.shape
            real_A = input_slices.to(self.device)
            real_B = target_slices.to(self.device)
            
            d_h, d_w = self._get_d_shape(B, H, W)
            
            # 标签平滑
            valid = Variable(torch.Tensor(B, 1, d_h, d_w).fill_(0.9), requires_grad=False).to(self.device)
            fake = Variable(torch.Tensor(B, 1, d_h, d_w).fill_(0.1), requires_grad=False).to(self.device)
            
            # ---------------------
            #  训练生成器 (Generator)
            # ---------------------
            self.g_optimizer.zero_grad()
            
            fake_B, flows, coarse_pred = self.generator(real_A)
            
            # [保留之前的修改] 亮度加权 L1 损失
            brightness_weight = 1.0 + (real_B * 9.0) 
            
            pred_fake = self.discriminator(fake_B, real_A)
            loss_GAN = self.adversarial_criterion(pred_fake, valid) * 1.0
            
            l1_diff = torch.abs(fake_B - real_B)
            loss_L1 = torch.mean(l1_diff * brightness_weight) * 10.0
            
            coarse_diff = torch.abs(coarse_pred - real_B)
            loss_Coarse = torch.mean(coarse_diff * brightness_weight) * coarse_weight 
            
            loss_VGG = self.vgg_criterion(fake_B, real_B) * 0.0
            loss_SSIM = (1 - ssim(fake_B, real_B, data_range=2.0, size_average=True)) * 10.0
            loss_Smooth = smoothness_loss(flows) * 0.05 
            
            g_loss = loss_GAN + loss_L1 + loss_Coarse + loss_VGG + loss_SSIM + loss_Smooth
            
            g_loss.backward()
            self.g_optimizer.step()
            
            # ---------------------
            #  训练判别器 (Discriminator)
            # ---------------------
            self.d_optimizer.zero_grad()
            
            pred_real = self.discriminator(real_B, real_A)
            loss_real = self.adversarial_criterion(pred_real, valid)
            
            pred_fake_d = self.discriminator(fake_B.detach(), real_A)
            loss_fake = self.adversarial_criterion(pred_fake_d, fake)
            
            d_loss = (loss_real + loss_fake) / 2
            d_loss.backward()
            self.d_optimizer.step()
            
            g_loss_accum += g_loss.item()
            d_loss_accum += d_loss.item()
            
            if i % 100 == 0:
                pbar.set_postfix({
                    'GAN': f'{loss_GAN.item():.2f}', 
                    'L1_W': f'{loss_L1.item():.2f}', 
                    'VGG': f'{loss_VGG.item():.2f}'
                })
        
        return g_loss_accum / len(dataloader), d_loss_accum / len(dataloader)
    
    def validate(self, dataloader):
        self.generator.eval()
        total_loss = 0
        with torch.no_grad():
            for input_slices, target_slices in dataloader:
                real_A = input_slices.to(self.device)
                real_B = target_slices.to(self.device)
                
                fake_B, _, _ = self.generator(real_A)
                
                l1 = nn.L1Loss()(fake_B, real_B) 
                ssim_val = ssim(fake_B, real_B, data_range=2.0, size_average=True)
                loss = l1 + (1 - ssim_val)
                total_loss += loss.item()
        
        return total_loss / len(dataloader)
    
    def save_checkpoint(self, epoch):
        """保存检查点"""
        checkpoint = {
            'epoch': epoch,
            'generator_state_dict': self.generator.state_dict(),
            'discriminator_state_dict': self.discriminator.state_dict(),
            'g_losses': self.g_losses,
            'd_losses': self.d_losses,
            'best_val_loss': self.best_val_loss # 保存最佳loss值以便恢复
        }
        # 如果 epoch 是字符串（如 'best', 'final'），直接拼接
        filename = f'./checkpoints/pix2pix_epoch_{epoch}.pth'
        torch.save(checkpoint, filename)
        # 仅在非 'best' 时打印保存路径，避免刷屏，或者都打印看你需求，这里为了区分 best 特意在 train 里打印
        if epoch != 'best':
            print(f"Checkpoint saved to {filename}")

    def train(self, epochs=200, batch_size=4, validation_split=0.2):
        print(f"Using device: {self.device}")
        
        train_loader, val_loader = get_dataloaders(
            self.data_folder, batch_size=batch_size, 
            target_shape=MODEL_CONFIG['input_size'], 
            validation_split=validation_split
        )
        
        print(f"Start training for {epochs} epochs...")
        
        for epoch in range(epochs):
            start_time = time.time()
            
            g_loss, d_loss = self.train_epoch(train_loader, epoch, epochs)
            val_loss = self.validate(val_loader)
            
            self.g_losses.append(g_loss)
            self.d_losses.append(d_loss)
            self.val_losses.append(val_loss)
            
            epoch_time = time.time() - start_time
            print(f'Epoch {epoch}/{epochs} ({epoch_time:.1f}s) - G: {g_loss:.4f}, D: {d_loss:.4f}, Val: {val_loss:.4f}')
            
            # [新增] 检查并保存最佳模型
            if val_loss < self.best_val_loss:
                prev_best = self.best_val_loss
                self.best_val_loss = val_loss
                self.save_checkpoint('best')
                print(f"🔥 New Best Model! Val Loss improved from {prev_best:.4f} to {val_loss:.4f}")
            
            if epoch % 5 == 0:
                self.save_checkpoint(epoch)
                plot_training_progress(
                    self.generator, self.discriminator, 
                    self.g_losses, self.d_losses, 
                    f'./training_plots/progress.png'
                )
        
        self.save_checkpoint('final')
        print("Training completed!")

if __name__ == "__main__":
    trainer = Pix2PixTrainer(data_folder='./gan_train')
    trainer.train(epochs=50, batch_size=6)