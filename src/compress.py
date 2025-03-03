import os
from pathlib import Path
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                            QPushButton, QFileDialog, QMessageBox, QLineEdit,
                            QComboBox)
from PyQt5.QtGui import QPixmap
import time

def compress_image(input_path, output_path, target_size_kb, min_quality=5, output_format='JPEG'):
    """
    使用二分法查找最佳压缩质量参数来压缩图片
    Args:
        input_path (str): 输入图片路径
        output_path (str): 输出图片路径
        target_size_kb (int): 目标文件大小（KB）
        min_quality (int): 最低图片质量
        output_format (str): 输出图片格式（JPEG, PNG, WEBP）
    """
    try:
        target_size = target_size_kb * 1024
        original_size = os.path.getsize(input_path)

        if original_size <= target_size:
            raise ValueError("原始文件已经小于目标大小，无需压缩")

        img = Image.open(input_path)
        if img.mode != 'RGB' and output_format == 'JPEG':
            img = img.convert('RGB')
        min_q = min_quality
        max_q = 95
        best_quality = None
        while min_q <= max_q:
            current_quality = (min_q + max_q) // 2
            try:
                # 这里不再保存中间结果
                img.save(output_path, quality=current_quality, format=output_format)
            except PermissionError:
                # 尝试解除文件占用
                for _ in range(3):
                    try:
                        img.save(output_path, quality=current_quality, format=output_format)
                        break
                    except:
                        time.sleep(0.5)
                else:
                    raise PermissionError(f"文件被占用，无法保存：{output_path}")

            current_size = os.path.getsize(output_path)

            if current_size <= target_size:
                best_quality = current_quality
                min_q = current_quality + 1
            else:
                max_q = current_quality - 1

        if best_quality is not None:
            try:
                # 只在找到最佳质量后保存最终结果
                img.save(output_path, quality=best_quality, format=output_format)
            except PermissionError:
                # 尝试解除文件占用
                for _ in range(3):
                    try:
                        img.save(output_path, quality=best_quality, format=output_format)
                        break
                    except:
                        time.sleep(0.5)
                else:
                    raise PermissionError(f"文件被占用，无法保存：{output_path}")
            final_size = os.path.getsize(output_path)
            print(f"压缩完成：")
            print(f"原始大小: {original_size/1024:.1f}KB")
            print(f"目标大小: {target_size/1024:.1f}KB")
            print(f"最终大小: {final_size/1024:.1f}KB")
            print(f"使用的质量参数: {best_quality}")

    except Exception as e:
        raise Exception(f"压缩过程中出错: {str(e)}")

def process_directory(input_dir, output_dir, target_size_kb, min_quality=5, output_format='JPEG'):
    """
    处理整个目录中的图片，并支持格式转换

    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
        target_size_kb (int): 目标文件大小（KB）
        min_quality (int): 最低图片质量
        output_format (str): 输出图片格式（JPEG, PNG, WEBP）
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    for img_path in input_path.rglob('*'):
        if img_path.suffix.lower() in image_extensions:
            relative_path = img_path.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix(f'.{output_format.lower()}')

            output_file.parent.mkdir(parents=True, exist_ok=True)

            print(f"\n处理文件: {relative_path}")
            try:
                compress_image(str(img_path), str(output_file), target_size_kb, min_quality, output_format)
            except Exception as e:
                print(f"处理 {relative_path} 时出错: {e}")

class ImageCompressorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图片压缩工具')
        self.setGeometry(100, 100, 500, 600)

        # 获取屏幕的宽度和高度
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        x = (screen_rect.width() - self.width()) // 2
        y = (screen_rect.height() - self.height()) // 2

        # 设置窗口位置为屏幕中心
        self.move(x, y)

        # 创建控件
        self.create_widgets()
        # 设置布局
        self.setup_layout()

    def create_widgets(self):
        # 输入路径
        self.input_label = QLabel('输入图片路径或目录:')
        self.input_entry = QLineEdit()
        self.input_button = QPushButton('浏览')
        self.input_button.clicked.connect(self.browse_input)
        # 输出路径
        self.output_label = QLabel('输出图片路径或目录:')
        self.output_entry = QLineEdit()
        self.output_button = QPushButton('浏览')
        self.output_button.clicked.connect(self.browse_output)
        # 目标大小
        self.size_label = QLabel('目标文件大小（KB）:')
        self.size_entry = QLineEdit()
        # 最低质量
        self.quality_label = QLabel('最低图片质量（1-100，默认5）:')
        self.quality_entry = QLineEdit()
        # 输出格式
        self.format_label = QLabel('输出图片格式:')
        self.format_var = QComboBox()
        self.format_var.addItems(['JPEG', 'PNG', 'WEBP'])
        # 开始压缩按钮
        self.compress_button = QPushButton('开始压缩')
        self.compress_button.clicked.connect(self.start_compression)

        # 图片预览
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(300, 300)
        self.preview_label.setScaledContents(True)

    def setup_layout(self):
        layout = QVBoxLayout()
        # 输入部分
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_entry)
        layout.addWidget(self.input_button)
        # 输出部分
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_entry)
        layout.addWidget(self.output_button)
        # 参数设置
        layout.addWidget(self.size_label)
        layout.addWidget(self.size_entry)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_entry)
        layout.addWidget(self.format_label)
        layout.addWidget(self.format_var)

        # 操作按钮
        layout.addWidget(self.compress_button)

        # 图片预览
        layout.addWidget(QLabel('图片预览:'))
        layout.addWidget(self.preview_label)

        self.setLayout(layout)

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择图片', '', '图片文件 (*.jpg *.jpeg *.png *.webp)')
        if path and os.path.exists(path) and os.access(path, os.R_OK):
            self.input_entry.setText(path)
            # 显示预览图片
            pixmap = QPixmap(path)
            self.preview_label.setPixmap(pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                aspectRatioMode=1
            ))

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if path:
            if not os.access(path, os.W_OK):
                QMessageBox.warning(self, '警告', '所选目录没有写入权限！')
                return
            self.output_entry.setText(path)

    def start_compression(self):
        input_path = self.input_entry.text()
        output_path = self.output_entry.text()
        target_size_kb = int(self.size_entry.text())
        min_quality = int(self.quality_entry.text() or "5")
        output_format = self.format_var.currentText()

        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"找不到输入文件或目录：{input_path}")

            # 新增路径处理逻辑
            if os.path.isfile(input_path):
                # 自动生成输出文件名
                if os.path.isdir(output_path):
                    input_filename = os.path.basename(input_path)
                    output_filename = os.path.splitext(input_filename)[0] + f'.{output_format.lower()}'
                    output_file = os.path.join(output_path, output_filename)
                else:
                    output_file = output_path
                
                # 检查输出目录权限
                output_dir = os.path.dirname(output_file)
                if not os.access(output_dir, os.W_OK):
                    raise PermissionError(f"无权限写入输出目录：{output_dir}")

                compress_image(input_path, output_file, target_size_kb, min_quality, output_format)
            else:
                # 检查输出目录权限
                if not os.access(output_path, os.W_OK):
                    raise PermissionError(f"无权限写入输出目录：{output_path}")
                
                process_directory(input_path, output_path, target_size_kb, min_quality, output_format)

            QMessageBox.information(self, '成功', '图片压缩完成！')
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

if __name__ == '__main__':
    app = QApplication([])
    window = ImageCompressorApp()
    window.show()
    app.exec_()