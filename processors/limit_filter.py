from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QCheckBox, QLabel, QDoubleSpinBox, QPushButton
)
from PyQt6.QtCore import Qt
import polars as pl
from .base import DataProcessor

class LimitFilter(DataProcessor):
    """Filter data based on upper and lower limits."""
    
    def __init__(self):
        self.widget = None
        self.use_filter = False
        self.lower_limit = -999999.0
        self.upper_limit = 999999.0
    
    def process(self, data: pl.Series) -> pl.Series:
        """Apply limit filtering to the data."""
        if not self.use_filter:
            return data
            
        return data.filter(
            (data >= self.lower_limit) & 
            (data <= self.upper_limit)
        )
    
    def get_widget(self) -> QWidget:
        """Create and return the configuration widget."""
        if self.widget is None:
            self.widget = self._create_widget()
        return self.widget
    
    def _create_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建控件
        self.use_limits_cb = QCheckBox("启用上下限")
        self.use_limits_cb.stateChanged.connect(self._on_state_changed)
        
        controls = QHBoxLayout()
        
        self.lower_spin = QDoubleSpinBox()
        self.lower_spin.setRange(-999999, 999999)
        
        self.upper_spin = QDoubleSpinBox()
        self.upper_spin.setRange(-999999, 999999)
        
        self.apply_button = QPushButton("应用上下限")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self._on_apply)  # 添加点击事件连接
        
        # 添加到布局
        controls.addWidget(QLabel("下限:"))
        controls.addWidget(self.lower_spin)
        controls.addWidget(QLabel("上限:"))
        controls.addWidget(self.upper_spin)
        controls.addWidget(self.apply_button)
        
        layout.addWidget(self.use_limits_cb)
        layout.addLayout(controls)
        widget.setLayout(layout)
        
        return widget
    
    def _on_state_changed(self, state: int) -> None:
        """Handle checkbox state change."""
        self.use_filter = state == Qt.CheckState.Checked.value
        self.apply_button.setEnabled(self.use_filter)
        if not self.use_filter:
            self._update_main_window()  # 取消勾选时更新图表
    
    def _on_apply(self) -> None:
        """Handle apply button click."""
        self.lower_limit = self.lower_spin.value()
        self.upper_limit = self.upper_spin.value()
        self._update_main_window()
    
    def _update_main_window(self) -> None:
        """Update the main window plot."""
        # 获取主窗口实例并更新图表
        main_window = self.widget.window()
        if main_window:
            main_window._update_plot()
    
    def update_limits(self, data: pl.Series) -> None:
        """Update limit values based on data."""
        self.use_limits_cb.setChecked(False)
        self.lower_spin.setValue(float(data.min()))
        self.upper_spin.setValue(float(data.max()))
        