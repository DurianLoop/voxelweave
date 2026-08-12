import torch

# config.py - 配置文件

# 模型配置
MODEL_CONFIG = {
    'input_size': (512, 512),
    # 2 (前后切片) + 1 (全局位置编码) + 3 (相对位置编码 t=0.25, 0.5, 0.75) = 6 通道
    'in_channels': 6,  
    # 输出中间的 3 张切片
    'out_channels': 3
}

# 数据处理配置
DATA_CONFIG = {
    'max_size': 1024,
    'resize_method': 'adaptive',
}

# 训练配置
TRAIN_CONFIG = {
    'epochs': 50,         
    'batch_size': 8,        
    'lr_initial': 0.0002,
    'lr_decay_start': 100   
}

# 推理配置
INFERENCE_CONFIG = {
    'batch_size': 1,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}