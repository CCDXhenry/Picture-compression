import os
from pathlib import Path
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFileDialog, QMessageBox, 
                            QLineEdit, QComboBox, QGridLayout, QScrollArea)
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QMimeData
import time

class DragDropWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(100, 100)
        self.add_button.setStyleSheet("""
            QPushButton {
                font-size: 48px;
                border: 3px dashed #aaa;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #888;
            }
        """)
        self.add_button.clicked.connect(self.parent().browse_images)
        self.layout.addWidget(self.add_button, 0, Qt.AlignCenter)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls if url.isLocalFile()]
        valid_files = [f for f in files if Path(f).suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]
        if valid_files:
            self.parent().add_thumbnails(valid_files)
        event.acceptProposedAction()

class ImageCompressorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图片压缩工具')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 参数设置行
        params_layout = QHBoxLayout()
        self.size_entry = QLineEdit(placeholderText="目标大小（KB）")
        self.quality_entry = QLineEdit(placeholderText="最低质量（1-100）")
        self.format_var = QComboBox()
        self.format_var.addItems(['JPEG', 'PNG', 'WEBP'])
        
        params_layout.addWidget(QLabel("目标大小:"))
        params_layout.addWidget(self.size_entry)
        params_layout.addWidget(QLabel("最低质量:"))
        params_layout.addWidget(self.quality_entry)
        params_layout.addWidget(QLabel("输出格式:"))
        params_layout.addWidget(self.format_var)

        # 图片区域
        self.scroll_area = QScrollArea()
        self.scroll_content = DragDropWidget(self)
        self.thumbnails_layout = QGridLayout()
        self.scroll_content.layout.addLayout(self.thumbnails_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_content)

        # 压缩按钮
        self.compress_button = QPushButton("开始压缩")
        self.compress_button.setStyleSheet("font-size: 16px; padding: 12px 24px;")
        self.compress_button.clicked.connect(self.start_compression)

        # 组装界面
        main_layout.addLayout(params_layout)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.compress_button)

        self.setLayout(main_layout)
        self.center_window()

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)

    def browse_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", 
            "图片文件 (*.jpg *.jpeg *.png *.webp)"
        )
        if files:
            self.add_thumbnails(files)

    def add_thumbnails(self, files):
        row = col = 0
        max_col = 4  # 每行显示4个缩略图

        for path in files:
            if path in self.image_paths:
                continue

            # 添加缩略图
            thumbnail = QLabel()
            thumbnail.setFixedSize(100, 100)
            pixmap = QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumbnail.setPixmap(pixmap)
            thumbnail.setStyleSheet("""
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 2px;
            """)

            # 添加删除按钮
            close_btn = QPushButton("×")
            close_btn.setFixedSize(20, 20)
            close_btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    color: white;
                    background-color: #ff4444;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
            """)
            close_btn.clicked.connect(lambda _, p=path: self.remove_image(p))

            # 容器布局
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addWidget(thumbnail)
            container_layout.addWidget(close_btn, 0, Qt.AlignCenter)
            container_layout.setContentsMargins(0, 0, 0, 0)

            self.thumbnails_layout.addWidget(container, row, col)
            self.image_paths.append(path)

            col += 1
            if col >= max_col:
                col = 0
                row += 1

    def remove_image(self, path):
        self.image_paths.remove(path)
        # 重新加载所有缩略图
        self.clear_thumbnails()
        self.add_thumbnails(self.image_paths)

    def clear_thumbnails(self):
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def start_compression(self):
        # 创建压缩图片文件夹
        output_dir = Path("compressed_images")
        output_dir.mkdir(parents=True, exist_ok=True)

        for input_path in self.image_paths:
            input_filename = os.path.basename(input_path)
            output_file = output_dir / f"compressed_{input_filename}"

            target_size_kb = int(self.size_entry.text())
            min_quality = int(self.quality_entry.text() or "5")
            output_format = self.format_var.currentText()

            try:
                compress_image(input_path, str(output_file), target_size_kb, min_quality, output_format)
                # 检查压缩后的文件大小
                final_size_kb = os.path.getsize(output_file) / 1024
                if final_size_kb < target_size_kb:
                    print(f"警告: {input_filename} 压缩后大小 {final_size_kb:.1f}KB 小于目标大小 {target_size_kb}KB")
            except Exception as e:
                QMessageBox.critical(self, '错误', str(e))

        QMessageBox.information(self, '成功', '所有图片压缩完成！')

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

if __name__ == '__main__':
    app = QApplication([])
    window = ImageCompressorApp()
    window.show()
    app.exec_()
