import os
import argparse
from PIL import Image
import sys
from pathlib import Path

def compress_image(input_path, output_path, target_size_kb, min_quality=5):
    """
    压缩图片到指定大小
    
    Args:
        input_path (str): 输入图片路径
        output_path (str): 输出图片路径
        target_size_kb (int): 目标文件大小（KB）
        min_quality (int): 最低图片质量，默认为5
    """
    # 目标大小转换为字节
    target_size = target_size_kb * 1024
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到输入文件: {input_path}")
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 打开原始图片
        img = Image.open(input_path)
        
        # 如果是PNG格式，转换为RGB模式
        if img.format == 'PNG':
            img = img.convert('RGB')
        
        # 获取原始文件大小
        original_size = os.path.getsize(input_path)
        
        # 如果原始文件已经小于目标大小，直接复制
        if original_size <= target_size:
            img.save(output_path, quality=95)
            print(f"原始文件已经小于目标大小，已直接保存")
            return
        
        # 二分查找最佳质量参数
        min_q = min_quality
        max_q = 95
        best_quality = None
        best_size = None
        
        while min_q <= max_q:
            current_quality = (min_q + max_q) // 2
            
            # 临时保存压缩后的图片
            img.save(output_path, 'JPEG', quality=current_quality)
            current_size = os.path.getsize(output_path)
            
            # 更新最佳结果
            if best_size is None or abs(current_size - target_size) < abs(best_size - target_size):
                best_quality = current_quality
                best_size = current_size
            
            # 如果当前大小接近目标大小（误差在5%以内），则完成
            if abs(current_size - target_size) / target_size < 0.05:
                break
            
            # 调整质量参数
            if current_size > target_size:
                max_q = current_quality - 1
            else:
                min_q = current_quality + 1
        
        # 使用最佳质量参数重新保存
        if best_quality is not None:
            img.save(output_path, 'JPEG', quality=best_quality)
            final_size = os.path.getsize(output_path)
            print(f"压缩完成：")
            print(f"原始大小: {original_size/1024:.1f}KB")
            print(f"目标大小: {target_size/1024:.1f}KB")
            print(f"最终大小: {final_size/1024:.1f}KB")
            print(f"使用的质量参数: {best_quality}")
            
    except Exception as e:
        raise Exception(f"压缩过程中出错: {str(e)}")

def process_directory(input_dir, output_dir, target_size_kb, min_quality=5):
    """
    处理整个目录中的图片
    
    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
        target_size_kb (int): 目标文件大小（KB）
        min_quality (int): 最低图片质量
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # 处理所有图片
    for img_path in input_path.rglob('*'):
        if img_path.suffix.lower() in image_extensions:
            # 计算相对路径，以保持目录结构
            relative_path = img_path.relative_to(input_path)
            output_file = output_path / relative_path
            
            # 确保输出文件的父目录存在
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n处理文件: {relative_path}")
            try:
                compress_image(str(img_path), str(output_file), target_size_kb, min_quality)
            except Exception as e:
                print(f"处理 {relative_path} 时出错: {e}")

def main():
    print("图片压缩工具")
    try:
        # 交互式获取输入并去除可能存在的引号
        input_path = input("输入图片路径或目录: ").strip().strip('"').strip("'")
        output_path = input("输出图片路径或目录: ").strip().strip('"').strip("'")
        target_size_kb = int(input("目标文件大小（KB）: "))
        
        try:
            min_quality = int(input("最低图片质量（1-100，默认5）: ") or "5")
            if not 1 <= min_quality <= 100:
                raise ValueError("质量值必须在1-100之间")
        except ValueError:
            print("使用默认质量值：5")
            min_quality = 5
        
        # 检查文件是否存在
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"找不到输入文件或目录：{input_path}")
            
        try:
            # 检查输入路径是文件还是目录
            if os.path.isfile(input_path):
                # 处理单个文件
                compress_image(input_path, output_path, target_size_kb, min_quality)
            else:
                # 处理整个目录
                process_directory(input_path, output_path, target_size_kb, min_quality)
                
        except Exception as e:
            print(f"错误：{str(e)}", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n程序已取消")
        sys.exit(0)

if __name__ == '__main__':
    main() 