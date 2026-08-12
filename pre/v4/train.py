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

from models import GeneratorUNet, Discriminator
from dataset import get_dataloaders
from utils import plot_training_progress
from config import MODEL_CONFIG

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(3407)

class VGGLoss(nn.Module):
    def __init__(self, device):
        super(VGGLoss, self).__init__()
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
        loss = 0
        # 逐通道计算 VGG Loss 并平均 (因为这里的 3 通道是三张独立的切片)
        for i in range(x.shape[1]):
            xi = x[:, i:i+1, :, :].repeat(1, 3, 1, 1)
            yi = y[:, i:i+1, :, :].repeat(1, 3, 1, 1)
            xi = (xi - self.mean) / self.std
            yi = (yi - self.mean) / self.std
            loss += self.criterion(self.vgg(xi), self.vgg(yi))
        return loss / x.shape[1]

def smoothness_loss(flow):
    dy = torch.abs(flow[:, :, 1:, :] - flow[:, :, :-1, :])
    dx = torch.abs(flow[:, :, :, 1:] - flow[:, :, :, :-1])
    return torch.mean(dx) + torch.mean(dy)

def gradient_loss(pred, target):
    pred_dx = pred[:, :, :, 1:] - pred[:, :, :, :-1]
    target_dx = target[:, :, :, 1:] - target[:, :, :, :-1]
    pred_dy = pred[:, :, 1:, :] - pred[:, :, :-1, :]
    target_dy = target[:, :, 1:, :] - target[:, :, :-1, :]
    return torch.mean(torch.abs(pred_dx - target_dx)) + torch.mean(torch.abs(pred_dy - target_dy))

def foreground_weight_map(target):
    flat = target.flatten(start_dim=2)
    threshold = torch.quantile(flat, 0.75, dim=2, keepdim=True).unsqueeze(-1)
    foreground = (target >= threshold).float()
    brightness = 1.0 + target * 2.0
    return brightness * (1.0 + foreground * 2.0)

class Pix2PixTrainer:
    def __init__(self, data_folder, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.data_folder = data_folder
        
        # Generator: 6进 3出; Discriminator: 9进
        self.generator = GeneratorUNet(in_channels=6, out_channels=3).to(device)
        self.discriminator = Discriminator(in_channels=9).to(device)
        
        self.adversarial_criterion = nn.MSELoss().to(device)
        self.vgg_criterion = VGGLoss(device)
        
        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        self.g_losses = []
        self.d_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        
        os.makedirs('./checkpoints', exist_ok=True)
        os.makedirs('./training_plots', exist_ok=True)
        self.discriminator_output_shape = None

    def _get_d_shape(self, B, H, W):
        if self.discriminator_output_shape is None:
            dummy = torch.randn(B, 9, H, W).to(self.device)
            with torch.no_grad():
                out = self.discriminator.model(dummy)
            self.discriminator_output_shape = out.shape[2:]
        return self.discriminator_output_shape
    
    def train_epoch(self, dataloader, epoch, total_epochs):
        self.generator.train()
        self.discriminator.train()
        g_loss_accum, d_loss_accum = 0, 0
        
        decay_steps = total_epochs // 2
        if epoch < decay_steps:
            coarse_weight = 25.0 * (1.0 - epoch / decay_steps)
        else:
            coarse_weight = 0.0
            
        pbar = tqdm(dataloader, desc=f'Epoch {epoch}')
        for i, (input_slices, target_slices) in enumerate(pbar):
            B, _, H, W = input_slices.shape
            real_A = input_slices.to(self.device)   # [B, 6, H, W]
            real_B = target_slices.to(self.device)  # [B, 3, H, W]
            
            d_h, d_w = self._get_d_shape(B, H, W)
            valid = Variable(torch.Tensor(B, 1, d_h, d_w).fill_(0.9), requires_grad=False).to(self.device)
            fake = Variable(torch.Tensor(B, 1, d_h, d_w).fill_(0.1), requires_grad=False).to(self.device)
            
            # --- Train Generator ---
            self.g_optimizer.zero_grad()
            
            fake_B, flows, coarse_pred = self.generator(real_A)
            
            structure_weight = foreground_weight_map(real_B)
            pred_fake = self.discriminator(fake_B, real_A)
            loss_GAN = self.adversarial_criterion(pred_fake, valid) * 1.0
            
            l1_diff = torch.abs(fake_B - real_B)
            loss_L1 = torch.mean(l1_diff * structure_weight) * 10.0
            
            coarse_diff = torch.abs(coarse_pred - real_B)
            loss_Coarse = torch.mean(coarse_diff * structure_weight) * coarse_weight 
            
            loss_VGG = self.vgg_criterion(fake_B, real_B) * 0.0
            loss_SSIM = (1 - ssim(fake_B, real_B, data_range=2.0, size_average=True)) * 10.0
            loss_Gradient = gradient_loss(fake_B, real_B) * 2.0
            loss_Smooth = smoothness_loss(flows) * 0.05 
            
            g_loss = loss_GAN + loss_L1 + loss_Coarse + loss_VGG + loss_SSIM + loss_Gradient + loss_Smooth
            
            g_loss.backward()
            self.g_optimizer.step()
            
            # --- Train Discriminator ---
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
                    'Grad': f'{loss_Gradient.item():.2f}',
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
                grad = gradient_loss(fake_B, real_B)
                total_loss += (l1 + (1 - ssim_val) + 0.2 * grad).item()
        return total_loss / len(dataloader)
    
    def save_checkpoint(self, epoch):
        checkpoint = {
            'epoch': epoch,
            'generator_state_dict': self.generator.state_dict(),
            'discriminator_state_dict': self.discriminator.state_dict(),
            'g_losses': self.g_losses,
            'd_losses': self.d_losses,
            'best_val_loss': self.best_val_loss
        }
        filename = f'./checkpoints/pix2pix_epoch_{epoch}.pth'
        torch.save(checkpoint, filename)
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
    trainer.train(epochs=50, batch_size=4)
