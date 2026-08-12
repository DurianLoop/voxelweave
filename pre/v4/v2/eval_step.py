import os
import numpy as np
import nibabel as nib
import pandas as pd
from tqdm import tqdm
import cv2
from scipy import ndimage
from scipy.stats import pearsonr
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import normalized_mutual_information as nmi
import warnings
warnings.filterwarnings('ignore')

def calculate_similarity_metrics(original, generated, mask=None):
    """
    计算多种相似度指标

    参数:
    original: 原始图像数据
    generated: 生成图像数据
    mask: 可选掩码，只计算掩码区域

    返回:
    包含各种相似度指标的字典
    """
    # 确保数据类型一致
    original = original.astype(np.float32)
    generated = generated.astype(np.float32)

    # 创建掩码（如果未提供）
    if mask is None:
        # 使用简单的阈值掩码，排除背景
        mask = original > np.percentile(original, 5)

    # 只计算掩码区域
    orig_masked = original[mask]
    gen_masked = generated[mask]

    # 如果掩码区域太小，使用整个图像
    if len(orig_masked) < 100:
        orig_masked = original.flatten()
        gen_masked = generated.flatten()
        mask = np.ones_like(original, dtype=bool)

    metrics = {}

    # 1. 均方误差 (MSE) - 越低越好
    metrics['MSE'] = np.mean((orig_masked - gen_masked) ** 2)

    # 2. 峰值信噪比 (PSNR) - 越高越好
    if metrics['MSE'] == 0:
        metrics['PSNR'] = float('inf')
    else:
        max_pixel = np.max(orig_masked)
        metrics['PSNR'] = 20 * np.log10(max_pixel / np.sqrt(metrics['MSE']))

    # 3. 结构相似性指数 (SSIM) - 越高越好
    try:
        # 对于3D数据，我们计算每个切片的SSIM然后取平均
        if len(original.shape) == 3:
            ssim_values = []
            for z in range(original.shape[2]):
                slice_orig = original[..., z]
                slice_gen = generated[..., z]
                mask_slice = mask[..., z] if mask.ndim == 3 else mask

                if np.any(mask_slice):
                    # 提取掩码区域的边界框
                    where = np.argwhere(mask_slice)
                    y1, x1 = where.min(axis=0)
                    y2, x2 = where.max(axis=0) + 1

                    crop_orig = slice_orig[y1:y2, x1:x2]
                    crop_gen = slice_gen[y1:y2, x1:x2]

                    if crop_orig.size > 0 and crop_orig.shape == crop_gen.shape:
                        ssim_val = ssim(crop_orig, crop_gen, data_range=np.max(crop_orig)-np.min(crop_orig))
                        ssim_values.append(ssim_val)

            metrics['SSIM'] = np.mean(ssim_values) if ssim_values else 0
        else:
            metrics['SSIM'] = 0
    except:
        metrics['SSIM'] = 0

    # 4. 归一化互相关系数 (NCC) - 越高越好
    metrics['NCC'] = np.corrcoef(orig_masked, gen_masked)[0, 1] if len(orig_masked) > 1 else 0

    # 5. 归一化互信息 (NMI) - 越高越好
    try:
        # 使用直方图方法计算NMI
        hist_2d, _, _ = np.histogram2d(orig_masked, gen_masked, bins=50)
        metrics['NMI'] = nmi(original, generated, bins=50)
    except:
        metrics['NMI'] = 0

    # 6. 平均绝对误差 (MAE) - 越低越好
    metrics['MAE'] = np.mean(np.abs(orig_masked - gen_masked))

    # 7. 豪斯多夫距离 (近似) - 越低越好
    try:
        # 计算边缘距离作为豪斯多夫距离的近似
        edges_orig = np.array([ndimage.sobel(original[..., z]) for z in range(original.shape[2])]).flatten()
        edges_gen = np.array([ndimage.sobel(generated[..., z]) for z in range(generated.shape[2])]).flatten()

        if len(edges_orig) > 0 and len(edges_gen) > 0:
            # 使用百分位数避免异常值影响
            hd_forward = np.percentile(np.min(np.abs(edges_orig[:, None] - edges_gen), axis=1), 95)
            hd_backward = np.percentile(np.min(np.abs(edges_gen[:, None] - edges_orig), axis=1), 95)
            metrics['Hausdorff_Distance'] = max(hd_forward, hd_backward)
        else:
            metrics['Hausdorff_Distance'] = 0
    except:
        metrics['Hausdorff_Distance'] = 0

    # 8. 相关系数 (Pearson) - 越高越好
    try:
        corr, _ = pearsonr(orig_masked, gen_masked)
        metrics['Pearson_Correlation'] = corr
    except:
        metrics['Pearson_Correlation'] = 0

    return metrics

def evaluate_interpolation_quality(original_path, generated_path):
    """
    评估插值质量

    参数:
    original_path: 原始NIfTI文件路径
    generated_path: 生成NIfTI文件路径

    返回:
    包含整体相似度和生成切片相似度的字典
    """
    # 加载图像
    original_img = nib.load(original_path)
    generated_img = nib.load(generated_path)

    original_data = original_img.get_fdata()
    generated_data = generated_img.get_fdata()

    print(f"评估文件: {os.path.basename(original_path)}")
    print(f"原始数据形状: {original_data.shape}")
    print(f"生成数据形状: {generated_data.shape}")

    # 确保数据形状一致
    if original_data.shape != generated_data.shape:
        print("警告: 数据形状不匹配，尝试调整...")

        # 处理3D数据
        if len(original_data.shape) == 3 and len(generated_data.shape) == 3:
            # 检查x和y维度是否一致
            if original_data.shape[:2] == generated_data.shape[:2]:
                # x和y一致，z不一致
                if generated_data.shape[2] < original_data.shape[2]:
                    # 生成图像的z轴层数小于原始图像，只取原始图像的前z层
                    z_size = generated_data.shape[2]
                    original_data = original_data[:, :, :z_size]
                    print(f"截取原始图像z轴到前{z_size}层")
                else:
                    # 生成图像的z轴层数大于原始图像，调整生成图像
                    generated_data = cv2.resize(generated_data, original_data.shape[:2][::-1])
                    if generated_data.shape != original_data.shape:
                        # 如果调整后形状仍不一致，使用插值调整z轴
                        from scipy.ndimage import zoom
                        zoom_factors = [1, 1, original_data.shape[2] / generated_data.shape[2]]
                        generated_data = zoom(generated_data, zoom_factors)
                    print("调整生成图像形状以匹配原始图像")
            else:
                # x和y不一致，先调整x和y，再处理z轴
                generated_data = cv2.resize(generated_data, original_data.shape[:2][::-1])
                if generated_data.shape != original_data.shape and len(generated_data.shape) == 3:
                    if generated_data.shape[2] < original_data.shape[2]:
                        z_size = generated_data.shape[2]
                        original_data = original_data[:, :, :z_size]
                        print(f"调整x,y后截取原始图像z轴到前{z_size}层")
                    else:
                        from scipy.ndimage import zoom
                        zoom_factors = [1, 1, original_data.shape[2] / generated_data.shape[2]]
                        generated_data = zoom(generated_data, zoom_factors)
        else:
            # 对于非3D数据或维度不匹配的情况，使用原来的调整方法
            generated_data = cv2.resize(generated_data, original_data.shape[:2][::-1])
            if len(original_data.shape) == 3 and len(generated_data.shape) == 2:
                generated_data = np.expand_dims(generated_data, axis=-1)

    # 最终检查形状是否一致
    if original_data.shape != generated_data.shape:
        print(f"错误: 无法调整形状一致 - 原始: {original_data.shape}, 生成: {generated_data.shape}")
        return {}

    results = {}

    # 1. 计算整体相似度
    print("计算整体相似度...")
    overall_metrics = calculate_similarity_metrics(original_data, generated_data)

    for metric, value in overall_metrics.items():
        results[f'Overall_{metric}'] = value

    # 2. 计算生成切片的相似度（奇数索引：1, 3, 5, ...）
    print("计算生成切片相似度...")
    if len(original_data.shape) >= 3:
        z_dim = 2  # 假设z轴是第三个维度
        num_slices = original_data.shape[z_dim]

        # 获取生成切片的索引（奇数索引，从1开始）
        generated_slice_indices = list(range(1, num_slices-1, 2))

        if generated_slice_indices:
            # 提取生成切片
            if len(original_data.shape) == 3:
                original_generated_slices = original_data[..., generated_slice_indices]
                generated_generated_slices = generated_data[..., generated_slice_indices]
            else:  # 4D数据
                original_generated_slices = original_data[..., generated_slice_indices, :]
                generated_generated_slices = generated_data[..., generated_slice_indices, :]

            # 计算生成切片的相似度
            generated_metrics = calculate_similarity_metrics(
                original_generated_slices,
                generated_generated_slices
            )

            for metric, value in generated_metrics.items():
                results[f'Generated_Slices_{metric}'] = value

            # 额外计算生成切片与相邻切片的相似度对比
            if len(generated_slice_indices) >= 2:
                # 计算生成切片与相邻原始切片的相似度
                adjacent_similarities = []
                for slice_idx in generated_slice_indices:
                    if slice_idx > 0 and slice_idx < num_slices - 1:
                        # 生成切片与相邻切片的相似度
                        if len(original_data.shape) == 3:
                            prev_slice = original_data[..., slice_idx-1]
                            next_slice = original_data[..., slice_idx+1]
                            gen_slice = generated_data[..., slice_idx]

                            sim_prev = calculate_similarity_metrics(
                                prev_slice, gen_slice
                            )['SSIM']
                            sim_next = calculate_similarity_metrics(
                                next_slice, gen_slice
                            )['SSIM']

                            adjacent_similarities.append((sim_prev + sim_next) / 2)

                if adjacent_similarities:
                    results['Generated_Slices_Adjacent_SSIM_Mean'] = np.mean(adjacent_similarities)
                    results['Generated_Slices_Adjacent_SSIM_Std'] = np.std(adjacent_similarities)

    return results

def main_evaluation():
    """
    主评估函数
    """
    # 目录设置
    original_dir = '/data/ZH/diffusers-main/data(10101)'
    generated_dir = 'gan_outputs'
    output_file = 'eval.xlsx'

    # 检查目录是否存在
    if not os.path.exists(original_dir):
        raise FileNotFoundError(f"原始数据目录不存在: {original_dir}")

    if not os.path.exists(generated_dir):
        raise FileNotFoundError(f"生成数据目录不存在: {generated_dir}")

    # 获取原始文件列表
    original_files = [f for f in os.listdir(original_dir) if f.endswith('.nii.gz')]

    if not original_files:
        print(f"在目录 {original_dir} 中未找到.nii.gz文件")
        return

    print(f"找到 {len(original_files)} 个原始NIfTI文件")

    # 存储所有结果
    all_results = []

    # 处理每个文件
    for original_file in tqdm(original_files, desc="评估文件"):
        original_path = os.path.join(original_dir, original_file)

        # 生成对应的生成文件名
        filename = os.path.splitext(os.path.splitext(original_file)[0])[0]
        generated_file = f"up_{filename}.nii.gz"
        generated_path = os.path.join(generated_dir, generated_file)

        if not os.path.exists(generated_path):
            print(f"警告: 生成文件不存在: {generated_file}")
            continue

        try:
            # 评估质量
            results = evaluate_interpolation_quality(original_path, generated_path)

            if results:  # 只有当结果不为空时才添加
                # 添加文件名信息
                results['Filename'] = original_file
                results['Generated_Filename'] = generated_file

                all_results.append(results)

                print(f"完成评估: {original_file}")
            else:
                print(f"跳过文件（形状无法匹配）: {original_file}")

        except Exception as e:
            print(f"评估文件 {original_file} 时出错: {e}")
            continue

    if not all_results:
        print("没有成功评估任何文件")
        return

    # 创建DataFrame
    df = pd.DataFrame(all_results)

    # 重新排列列，将文件名放在前面
    columns = ['Filename', 'Generated_Filename'] + [col for col in df.columns if col not in ['Filename', 'Generated_Filename']]
    df = df[columns]

    # 在DataFrame最后添加均值行
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    mean_row = {}

    # 处理非数值列
    for col in df.columns:
        if col in numeric_cols:
            mean_row[col] = df[col].mean()
        else:
            if col == 'Filename':
                mean_row[col] = '平均值'
            elif col == 'Generated_Filename':
                mean_row[col] = '平均值'
            else:
                mean_row[col] = ''

    # 创建均值行DataFrame并添加到原DataFrame
    mean_df = pd.DataFrame([mean_row])
    df_with_mean = pd.concat([df, mean_df], ignore_index=True)

    # 保存到Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 保存包含均值的完整数据
        df_with_mean.to_excel(writer, sheet_name='相似度评估', index=False)

        # 添加摘要统计
        summary_data = []

        for col in numeric_cols:
            summary_data.append({
                'Metric': col,
                'Mean': df[col].mean(),
                'Std': df[col].std(),
                'Min': df[col].min(),
                'Max': df[col].max(),
                'Median': df[col].median()
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='统计摘要', index=False)

    print(f"评估完成！结果已保存到: {output_file}")

    # 显示简要结果
    print("\n=== 评估结果摘要 ===")
    important_metrics = ['Overall_SSIM', 'Overall_PSNR', 'Overall_NMI',
                         'Generated_Slices_SSIM', 'Generated_Slices_PSNR', 'Generated_Slices_NMI']

    for metric in important_metrics:
        if metric in df.columns:
            mean_val = df[metric].mean()
            std_val = df[metric].std()
            print(f"{metric}: {mean_val:.4f} ± {std_val:.4f}")

    return df_with_mean

def create_detailed_report(df):
    """
    创建详细评估报告
    """
    # 移除平均值行（如果有）再进行详细报告计算
    df_original = df[df['Filename'] != '平均值'].copy() if '平均值' in df['Filename'].values else df.copy()

    # 创建更详细的报告
    report_data = []

    for _, row in df_original.iterrows():
        filename = row['Filename']

        # 整体质量评分（基于多个指标的综合）
        overall_score = 0
        overall_weights = {'SSIM': 0.4, 'PSNR': 0.3, 'NMI': 0.3}

        generated_score = 0
        generated_weights = {'SSIM': 0.4, 'PSNR': 0.3, 'NMI': 0.3}

        for metric, weight in overall_weights.items():
            col_name = f'Overall_{metric}'
            if col_name in row:
                # 归一化到0-1范围（假设更高的值更好）
                if metric in ['MSE', 'MAE', 'Hausdorff_Distance']:
                    # 这些指标越低越好，取倒数
                    normalized = 1 / (1 + row[col_name])
                else:
                    normalized = min(1.0, max(0.0, row[col_name]))

                overall_score += normalized * weight

        for metric, weight in generated_weights.items():
            col_name = f'Generated_Slices_{metric}'
            if col_name in row:
                if metric in ['MSE', 'MAE', 'Hausdorff_Distance']:
                    normalized = 1 / (1 + row[col_name])
                else:
                    normalized = min(1.0, max(0.0, row[col_name]))

                generated_score += normalized * weight

        report_data.append({
            'Filename': filename,
            'Overall_Quality_Score': overall_score,
            'Generated_Slices_Quality_Score': generated_score,
            'Quality_Ratio': generated_score / overall_score if overall_score > 0 else 0
        })

    report_df = pd.DataFrame(report_data)

    # 在详细报告中也添加均值行
    numeric_cols_report = report_df.select_dtypes(include=[np.number]).columns
    mean_row_report = {}

    for col in report_df.columns:
        if col in numeric_cols_report:
            mean_row_report[col] = report_df[col].mean()
        else:
            if col == 'Filename':
                mean_row_report[col] = '平均值'
            else:
                mean_row_report[col] = ''

    mean_df_report = pd.DataFrame([mean_row_report])
    report_df_with_mean = pd.concat([report_df, mean_df_report], ignore_index=True)

    # 保存详细报告
    with pd.ExcelWriter('eval_gan_detailed.xlsx', engine='openpyxl') as writer:
        report_df_with_mean.to_excel(writer, sheet_name='质量评分', index=False)

        # 添加排序版本（不包含均值行）
        sorted_df = report_df.sort_values('Overall_Quality_Score', ascending=False)
        sorted_df_with_mean = pd.concat([sorted_df, mean_df_report], ignore_index=True)
        sorted_df_with_mean.to_excel(writer, sheet_name='按质量排序', index=False)

    print("详细报告已保存到: eval_gan_detailed.xlsx")

    return report_df_with_mean

if __name__ == "__main__":
    # 安装所需库的提示
    try:
        import nibabel as nib
        import pandas as pd
        from scipy import ndimage
        from skimage.metrics import structural_similarity, normalized_mutual_information
    except ImportError as e:
        print("缺少必要的库，请安装：")
        print("pip install nibabel pandas opencv-python scikit-image scipy tqdm openpyxl")
        exit(1)

    # 运行主评估
    results_df = main_evaluation()

    if results_df is not None:
        # 创建详细报告
        create_detailed_report(results_df)

        print("\n评估完成！生成的文件：")
        print("1. eval_gan.xlsx - 主要评估结果（包含最后一行均值）")
        print("2. eval_gan_detailed.xlsx - 详细质量评分（包含最后一行均值）")
