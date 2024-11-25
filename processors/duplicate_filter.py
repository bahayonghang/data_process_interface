from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QCheckBox, QLabel
)
from PyQt6.QtCore import Qt
import polars as pl
from .base import DataProcessor

class DuplicateFilter(DataProcessor):
    """Filter consecutive duplicate values."""
    
    def __init__(self):
        self.widget = None
        self.use_filter = False
    
    def process(self, data: pl.Series) -> pl.Series:
        """Apply duplicate filtering to the data."""
        if not self.use_filter:
            return data
            
        # 创建一个布尔掩码，标记与前一个值不同的位置
        mask = data != data.shift()
        # 第一个值应该保留
        mask = mask.fill_null(True)
        
        return data.filter(mask)
    
    def get_widget(self) -> QWidget:
        """Create and return the configuration widget."""
        if self.widget is None:
            self.widget = self._create_widget()
        return self.widget
    
    def _create_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建控件
        self.use_filter_cb = QCheckBox("启用连续重复值过滤")
        self.use_filter_cb.stateChanged.connect(self._on_state_changed)
        
        # 添加到布局
        layout.addWidget(self.use_filter_cb)
        widget.setLayout(layout)
        
        return widget
    
    def _on_state_changed(self, state: int) -> None:
        """Handle checkbox state change."""
        self.use_filter = state == Qt.CheckState.Checked.value
        self._update_main_window()  # 更新图表
        
    def _update_main_window(self) -> None:
        """Update the main window plot."""
        # 获取主窗口实例并更新图表
        main_window = self.widget.window()
        if main_window:
            main_window._update_plot()
