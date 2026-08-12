import torch
import torch.nn as nn
import torch.nn.functional as F

# 1. 光流扭曲模块
class Warper(nn.Module):
    def __init__(self, device):
        super(Warper, self).__init__()
        self.device = device
    
    def forward(self, x, flow):
        B, C, H, W = x.shape
        xx = torch.arange(0, W).view(1, -1).repeat(H, 1)
        yy = torch.arange(0, H).view(-1, 1).repeat(1, W)
        xx = xx.view(1, 1, H, W).repeat(B, 1, 1, 1)
        yy = yy.view(1, 1, H, W).repeat(B, 1, 1, 1)
        
        grid = torch.cat((xx, yy), 1).float().to(self.device)
        vgrid = grid + flow
        vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :] / max(W - 1, 1) - 1.0
        vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :] / max(H - 1, 1) - 1.0
        vgrid = vgrid.permute(0, 2, 3, 1)
        output = F.grid_sample(x, vgrid, align_corners=True, mode='bilinear', padding_mode='border')
        return output

# 2. 运动估计网络
class MotionEstimator(nn.Module):
    def __init__(self, in_channels=2):
        super(MotionEstimator, self).__init__()
        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, 3, 1, 1),
                nn.LeakyReLU(0.1, inplace=True),
                nn.Conv2d(out_c, out_c, 3, 1, 1),
                nn.LeakyReLU(0.1, inplace=True)
            )
        self.c1 = conv_block(in_channels, 32)
        self.c2 = conv_block(32, 64)
        self.c3 = conv_block(64, 128)
        self.d1 = nn.ConvTranspose2d(128, 64, 4, 2, 1)
        self.d2 = nn.ConvTranspose2d(64 + 64, 32, 4, 2, 1)
        self.final = nn.Conv2d(32 + 32, 4, 3, 1, 1) 
        nn.init.constant_(self.final.weight, 0)
        nn.init.constant_(self.final.bias, 0)

    def forward(self, x):
        feat1 = self.c1(x)
        feat2 = self.c2(F.avg_pool2d(feat1, 2))
        feat3 = self.c3(F.avg_pool2d(feat2, 2))
        up1 = self.d1(feat3)
        up1 = torch.cat([up1, feat2], dim=1)
        up2 = self.d2(up1)
        up2 = torch.cat([up2, feat1], dim=1)
        out = self.final(up2)
        return out

# 3. 主生成器
class UNetDown(nn.Module):
    def __init__(self, in_size, out_size, normalize=True, dropout=0.0):
        super(UNetDown, self).__init__()
        layers = [nn.Conv2d(in_size, out_size, 4, 2, 1, bias=False)]
        if normalize: layers.append(nn.BatchNorm2d(out_size))
        layers.append(nn.LeakyReLU(0.2))
        if dropout: layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)
    def forward(self, x): return self.model(x)

class UNetUp(nn.Module):
    def __init__(self, in_size, out_size, dropout=0.0):
        super(UNetUp, self).__init__()
        layers = [
            nn.ConvTranspose2d(in_size, out_size, 4, 2, 1, bias=False),
            nn.BatchNorm2d(out_size),
            nn.ReLU(inplace=True)
        ]
        if dropout: layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)
    def forward(self, x, skip_input):
        x = self.model(x)
        x = torch.cat((x, skip_input), 1)
        return x

class GeneratorUNet(nn.Module):
    def __init__(self, in_channels=6, out_channels=3):
        super(GeneratorUNet, self).__init__()
        self.motion_estimator = MotionEstimator(in_channels=2)
        self.warper = None 
        
        # warped_prev(3) + warped_next(3) + img_prev(1) + img_next(1) + flows(4) + pos_maps(4) = 16 通道
        refine_in = 16
        
        self.down1 = UNetDown(refine_in, 64, normalize=False)
        self.down2 = UNetDown(64, 128)
        self.down3 = UNetDown(128, 256)
        self.down4 = UNetDown(256, 512, dropout=0.5)
        self.down5 = UNetDown(512, 512, dropout=0.5)
        
        self.up2 = UNetUp(512, 512, dropout=0.5)
        self.up3 = UNetUp(1024, 256)
        self.up4 = UNetUp(512, 128)
        self.up5 = UNetUp(256, 64)
        
        self.final_conv = nn.Sequential(
            nn.Upsample(scale_factor=2),
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(128, 64, 4, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, out_channels, 3, 1, 1),
            nn.Tanh()
        )

    def forward(self, x):
        # x: [B, 6, H, W]
        img_prev = x[:, 0:1, :, :]
        img_next = x[:, 1:2, :, :]
        pos_maps = x[:, 2:6, :, :] # global(1) + rel(3)
        
        if self.warper is None:
            self.warper = Warper(x.device)

        # 估计光流
        imgs_pair = torch.cat([img_prev, img_next], dim=1)
        flows = self.motion_estimator(imgs_pair) # [B, 4, H, W]
        flow_fwd = flows[:, 0:2, :, :] 
        flow_bwd = flows[:, 2:4, :, :]
        
        # 根据 t 缩放光流并生成三组 Coarse (Warping)
        # t = 0.25
        w_p_1 = self.warper(img_prev, flow_fwd * 0.25)
        w_n_1 = self.warper(img_next, flow_bwd * 0.75)
        # t = 0.50
        w_p_2 = self.warper(img_prev, flow_fwd * 0.50)
        w_n_2 = self.warper(img_next, flow_bwd * 0.50)
        # t = 0.75
        w_p_3 = self.warper(img_prev, flow_fwd * 0.75)
        w_n_3 = self.warper(img_next, flow_bwd * 0.25)
        
        warped_prev = torch.cat([w_p_1, w_p_2, w_p_3], dim=1) # [B, 3, H, W]
        warped_next = torch.cat([w_n_1, w_n_2, w_n_3], dim=1) # [B, 3, H, W]
        coarse_pred = (warped_prev + warped_next) / 2.0       # [B, 3, H, W]
        
        # Refinement (总计 16 通道)
        refine_input = torch.cat([warped_prev, warped_next, img_prev, img_next, flows, pos_maps], dim=1)
        
        d1 = self.down1(refine_input)
        d2 = self.down2(d1)
        d3 = self.down3(d2)
        d4 = self.down4(d3)
        d5 = self.down5(d4)
        
        u2 = self.up2(d5, d4)
        u3 = self.up3(u2, d3)
        u4 = self.up4(u3, d2)
        u5 = self.up5(u4, d1)
        
        final_img = self.final_conv(u5)
        
        return final_img, flows, coarse_pred

class Discriminator(nn.Module):
    # 输入为 Condition(6) + Fake/Real Image(3) = 9
    def __init__(self, in_channels=9):
        super(Discriminator, self).__init__()

        def discriminator_block(in_filters, out_filters, normalization=True):
            layers = [nn.Conv2d(in_filters, out_filters, 4, stride=2, padding=1)]
            if normalization: layers.append(nn.BatchNorm2d(out_filters))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *discriminator_block(in_channels, 64, normalization=False),
            *discriminator_block(64, 128),
            *discriminator_block(128, 256),
            *discriminator_block(256, 512),
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(512, 1, 4, padding=1, bias=False)
        )

    def forward(self, img_A, img_B):
        img_input = torch.cat((img_A, img_B), 1)
        return self.model(img_input)