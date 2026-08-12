from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class Warper(nn.Module):
    def forward(self, x: torch.Tensor, flow: torch.Tensor) -> torch.Tensor:
        batch, _channels, height, width = x.shape
        xx = torch.arange(0, width, device=x.device).view(1, -1).repeat(height, 1)
        yy = torch.arange(0, height, device=x.device).view(-1, 1).repeat(1, width)
        xx = xx.view(1, 1, height, width).repeat(batch, 1, 1, 1)
        yy = yy.view(1, 1, height, width).repeat(batch, 1, 1, 1)
        grid = torch.cat((xx, yy), 1).float()
        vgrid = grid + flow
        vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :] / max(width - 1, 1) - 1.0
        vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :] / max(height - 1, 1) - 1.0
        return F.grid_sample(
            x,
            vgrid.permute(0, 2, 3, 1),
            align_corners=True,
            mode="bilinear",
            padding_mode="border",
        )


class MotionEstimator(nn.Module):
    def __init__(self, in_channels: int = 2):
        super().__init__()

        def conv_block(in_c: int, out_c: int) -> nn.Sequential:
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, 3, 1, 1),
                nn.LeakyReLU(0.1, inplace=True),
                nn.Conv2d(out_c, out_c, 3, 1, 1),
                nn.LeakyReLU(0.1, inplace=True),
            )

        self.c1 = conv_block(in_channels, 32)
        self.c2 = conv_block(32, 64)
        self.c3 = conv_block(64, 128)
        self.d1 = nn.ConvTranspose2d(128, 64, 4, 2, 1)
        self.d2 = nn.ConvTranspose2d(128, 32, 4, 2, 1)
        self.final = nn.Conv2d(64, 4, 3, 1, 1)
        nn.init.constant_(self.final.weight, 0)
        nn.init.constant_(self.final.bias, 0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat1 = self.c1(x)
        feat2 = self.c2(F.avg_pool2d(feat1, 2))
        feat3 = self.c3(F.avg_pool2d(feat2, 2))
        up1 = self.d1(feat3)
        up1 = torch.cat([up1, feat2], dim=1)
        up2 = self.d2(up1)
        up2 = torch.cat([up2, feat1], dim=1)
        return self.final(up2)


class UNetDown(nn.Module):
    def __init__(self, in_size: int, out_size: int, normalize: bool = True, dropout: float = 0.0):
        super().__init__()
        layers: list[nn.Module] = [nn.Conv2d(in_size, out_size, 4, 2, 1, bias=False)]
        if normalize:
            layers.append(nn.BatchNorm2d(out_size))
        layers.append(nn.LeakyReLU(0.2))
        if dropout:
            layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)


class UNetUp(nn.Module):
    def __init__(self, in_size: int, out_size: int, dropout: float = 0.0):
        super().__init__()
        layers: list[nn.Module] = [
            nn.ConvTranspose2d(in_size, out_size, 4, 2, 1, bias=False),
            nn.BatchNorm2d(out_size),
            nn.ReLU(inplace=True),
        ]
        if dropout:
            layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, skip_input: torch.Tensor) -> torch.Tensor:
        x = self.model(x)
        return torch.cat((x, skip_input), 1)


class GeneratorUNet(nn.Module):
    def __init__(self, in_channels: int = 6, out_channels: int = 3):
        super().__init__()
        if out_channels < 1:
            raise ValueError(f"out_channels must be positive, got {out_channels}")
        expected_in_channels = out_channels + 3  # two anchors, global z, and one map per target slice
        if in_channels != expected_in_channels:
            raise ValueError(
                f"Expected in_channels={expected_in_channels} for out_channels={out_channels}, got {in_channels}"
            )
        self.out_channels = out_channels
        self.motion_estimator = MotionEstimator(in_channels=2)
        self.warper = Warper()
        # warped left/right stacks, two anchors, bidirectional flow, global z, and relative positions
        refine_in = 3 * out_channels + 7
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
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        if x.shape[1] != self.out_channels + 3:
            raise ValueError(
                f"Expected {self.out_channels + 3} condition channels, got {x.shape[1]}"
            )
        img_prev = x[:, 0:1, :, :]
        img_next = x[:, 1:2, :, :]
        pos_maps = x[:, 2:, :, :]
        flows = self.motion_estimator(torch.cat([img_prev, img_next], dim=1))
        flow_fwd = flows[:, 0:2, :, :]
        flow_bwd = flows[:, 2:4, :, :]
        ratios = [(index + 1) / float(self.out_channels + 1) for index in range(self.out_channels)]
        warped_prev = torch.cat(
            [self.warper(img_prev, flow_fwd * ratio) for ratio in ratios],
            dim=1,
        )
        warped_next = torch.cat(
            [self.warper(img_next, flow_bwd * (1.0 - ratio)) for ratio in ratios],
            dim=1,
        )
        coarse_pred = (warped_prev + warped_next) / 2.0
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
        return self.final_conv(u5), flows, coarse_pred


class Discriminator(nn.Module):
    def __init__(self, in_channels: int = 9):
        super().__init__()

        def block(in_filters: int, out_filters: int, normalization: bool = True) -> list[nn.Module]:
            layers: list[nn.Module] = [nn.Conv2d(in_filters, out_filters, 4, stride=2, padding=1)]
            if normalization:
                layers.append(nn.BatchNorm2d(out_filters))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *block(in_channels, 64, normalization=False),
            *block(64, 128),
            *block(128, 256),
            *block(256, 512),
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(512, 1, 4, padding=1, bias=False),
        )

    def forward(self, img_b: torch.Tensor, img_a: torch.Tensor) -> torch.Tensor:
        return self.model(torch.cat((img_a, img_b), 1))
