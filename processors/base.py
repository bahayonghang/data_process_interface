from abc import ABC, abstractmethod
from typing import Any
import polars as pl

class DataProcessor(ABC):
    """Base class for all data processors."""
    
    @abstractmethod
    def process(self, data: pl.Series) -> pl.Series:
        """
        Process the input data series.
        
        Args:
            data: Input data series to process
            
        Returns:
            Processed data series
        """
        pass
    
    @abstractmethod
    def get_widget(self) -> Any:
        """
        Get the QWidget for processor configuration.
        
        Returns:
            QWidget for the processor
        """
        pass