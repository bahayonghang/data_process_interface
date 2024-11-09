from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QFileDialog, QProgressDialog
)
from PyQt6.QtCore import pyqtSignal
import polars as pl

class DataLoader(QWidget):
    """Widget for loading data files."""
    
    # 信号定义
    data_loaded = pyqtSignal(object)  # 发送加载的DataFrame
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # 加载按钮
        self.load_button = QPushButton("加载数据")
        self.load_button.clicked.connect(self._load_data)
        layout.addWidget(self.load_button)
    
    def _load_data(self) -> None:
        """Handle data loading."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据文件",
            "",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if not file_path:
            return
            
        # 显示进度对话框
        progress = QProgressDialog("正在加载数据...", None, 0, 0, self)
        progress.setWindowTitle("请稍候")
        progress.setModal(True)
        progress.show()
        
        try:
            # 加载数据
            df = pl.read_csv(file_path)
            self.data_loaded.emit(df)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"加载数据时出错：\n{str(e)}")
        finally:
            progress.close()