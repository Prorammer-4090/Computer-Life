"""
UI Module for Emotion Detector Pro
Modern, object-oriented PyQt6 application with clean architecture.
"""

from .main_window import MainWindow
from .core import StatsManager
from .widgets import *
from .utils import *

__version__ = "2.0.0"
__author__ = "Your Name"

__all__ = ['MainWindow', 'StatsManager']
