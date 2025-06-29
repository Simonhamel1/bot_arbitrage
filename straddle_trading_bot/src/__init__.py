# Package Bot de Trading Straddle
# Version 1.0 - Production Ready

__version__ = "1.0.0"
__author__ = "Straddle Trading Bot Team"
__description__ = "Bot de trading straddle professionnel avec hedging dynamique"

# Imports principaux
from .config import *
from .data_manager import DataManager
from .straddle_strategy import StraddleStrategy
from .visualization import TradingVisualization

__all__ = [
    'DataManager',
    'StraddleStrategy', 
    'TradingVisualization'
]
