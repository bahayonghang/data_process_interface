from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QCheckBox, QLabel, QSpinBox
)
from PyQt6.QtCore import Qt
import polars as pl
from .base import DataProcessor

class MovingAverage(DataProcessor):
    """Apply moving average to data."""
    
    def __init__(self):
        self.widget = None
        self.use_ma = False
        self.window_size = 5
    
    def process(self, data: pl.Series) -> pl.Series:
        """Apply moving average to the data."""
        if not self.use_ma:
            return data
            
        return data.rolling_mean(
            window_size=self.window_size,
            center=True
        ).fill_null(strategy='forward').fill_null(strategy='backward')
    
    def get_widget(self) -> QWidget:
        """Create and return the configuration widget."""
        if self.widget is None:
            self.widget = self._create_widget()
        return self.widget
    
    def _create_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.use_ma_cb = QCheckBox("启用移动平均")
        self.use_ma_cb.stateChanged.connect(self._on_state_changed)
        
        controls = QHBoxLayout()
        controls.addWidget(QLabel("窗口大小:"))
        
        self.window_spin = QSpinBox()
        self.window_spin.setRange(2, 1000)
        self.window_spin.setValue(5)
        controls.addWidget(self.window_spin)
        
        layout.addWidget(self.use_ma_cb)
        layout.addLayout(controls)
        widget.setLayout(layout)
        
        return widget
    
    def _on_state_changed(self, state: int) -> None:
        """Handle checkbox state change."""
        self.use_ma = state == Qt.CheckState.Checked.value
        self.window_spin.setEnabled(self.use_ma)
