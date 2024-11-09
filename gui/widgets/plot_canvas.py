from typing import Optional
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
import matplotlib.pyplot as plt

# 设置字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class PlotCanvas(QWidget):
    """Widget for displaying plots."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建图表
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # 添加工具栏
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # 创建子图
        self.ax1 = self.figure.add_subplot(211)
        self.ax2 = self.figure.add_subplot(212)
    
    def update_plot(self, 
                   original_data: np.ndarray, 
                   processed_data: np.ndarray,
                   title: str) -> None:
        """
        Update the plot with new data.
        
        Args:
            original_data: Original data array
            processed_data: Processed data array
            title: Plot title
        """
        # 清除现有图表
        self.ax1.clear()
        self.ax2.clear()
        
        # 绘制原始数据
        self.ax1.plot(original_data, 'b-', label='原始数据')
        self.ax1.set_title(f'原始数据 - {title}')
        self.ax1.grid(True)
        self.ax1.legend()
        
        # 绘制处理后数据
        self.ax2.plot(processed_data, 'r-', label='处理后数据')
        self.ax2.set_title('处理后数据')
        self.ax2.grid(True)
        self.ax2.legend()
        
        # 添加标签
        self.ax1.set_xlabel('数据点')
        self.ax2.set_xlabel('数据点')
        self.ax1.set_ylabel('值')
        self.ax2.set_ylabel('值')
        
        # 调整布局并刷新
        self.figure.tight_layout()
        self.canvas.draw()