from typing import Optional, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QComboBox, QLabel, QFileDialog
)
import polars as pl
from .widgets.data_loader import DataLoader
from .widgets.plot_canvas import PlotCanvas
from processors.base import DataProcessor
from processors.limit_filter import LimitFilter
from processors.moving_average import MovingAverage
from processors.duplicate_filter import DuplicateFilter

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据处理工具")
        self.resize(1200, 800)
        
        # 初始化成员变量
        self.df: Optional[pl.DataFrame] = None
        self.processors: List[DataProcessor] = []
        
        # 创建UI
        self._setup_ui()
        self._setup_processors()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 左侧控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        control_panel.setFixedWidth(450)
        
        # 数据加载部分
        self.data_loader = DataLoader()
        self.data_loader.data_loaded.connect(self._on_data_loaded)
        control_layout.addWidget(self.data_loader)
        
        # 列选择
        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel("选择列:"))
        self.column_selector = QComboBox()
        self.column_selector.currentIndexChanged.connect(self._on_column_changed)
        column_layout.addWidget(self.column_selector)
        control_layout.addLayout(column_layout)
        
        # 处理器配置区域
        self.processor_layout = QVBoxLayout()
        control_layout.addLayout(self.processor_layout)
        
        # 添加弹性空间
        control_layout.addStretch()
        
        # 绘图区域
        self.plot_canvas = PlotCanvas()
        
        # 添加到主布局
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.plot_canvas)
    
    def _setup_processors(self) -> None:
        """Initialize data processors."""
        # 添加处理器
        self.processors = [
            LimitFilter(),
            MovingAverage(),
            DuplicateFilter()
        ]
        
        # 添加处理器控件
        for processor in self.processors:
            self.processor_layout.addWidget(processor.get_widget())
    
    def _on_data_loaded(self, df: pl.DataFrame) -> None:
        """Handle data loading completion."""
        self.df = df
        
        # 更新列选择器
        self.column_selector.clear()
        self.column_selector.addItems(self.df.columns[1:])  # 跳过DateTime列
        
        # 更新图表
        self._update_plot()
    
    def _on_column_changed(self, index: int) -> None:
        """Handle column selection change."""
        if self.df is None:
            return
            
        # 更新处理器状态
        current_column = self.column_selector.currentText()
        if not current_column:  # 如果列名为空，跳过处理
            return
            
        current_data = self.df[current_column]
        
        # 更新上下限
        for processor in self.processors:
            if isinstance(processor, LimitFilter):
                processor.update_limits(current_data)
        
        # 更新图表
        self._update_plot()
    
    def _update_plot(self) -> None:
        """Update the plot with processed data."""
        if self.df is None or not self.column_selector.currentText():
            return
        
        # 获取当前列数据
        column = self.column_selector.currentText()
        data = self.df[column]
        
        # 依次应用所有处理器
        processed_data = data
        for processor in self.processors:
            processed_data = processor.process(processed_data)
        
        # 更新图表
        self.plot_canvas.update_plot(
            data.to_numpy(),
            processed_data.to_numpy(),
            column
        )
        