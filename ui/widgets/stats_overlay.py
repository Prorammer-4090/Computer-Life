"""
Statistics Overlay Widget
Displays application statistics in an animated overlay.
"""
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, 
                             QFrame, QGraphicsOpacityEffect, QGridLayout)

from ..core.stats_manager import StatsManager


class StatsOverlay(QWidget):
    """Overlay widget that displays application statistics with animations."""
    
    def __init__(self, parent=None, stats_manager=None):
        super().__init__(parent)
        self.stats_manager = stats_manager or StatsManager()
        self._setup_window_properties()
        self._setup_animations()
        self._create_ui()
    
    def _setup_window_properties(self):
        """Configure window flags and attributes."""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def _setup_animations(self):
        """Setup opacity animations for show/hide effects."""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def _create_ui(self):
        """Create the user interface elements."""
        # Main content widget
        content_widget = QFrame(self)
        content_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(40, 40, 40, 0.98), stop:1 rgba(20, 20, 20, 0.98));
            color: white;
            border-radius: 20px;
            border: 2px solid rgba(100, 150, 255, 0.3);
        """)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Title
        title = QLabel("Overall Statistics")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Statistics grid
        self._create_stats_grid(layout)
        
        layout.addStretch()
        
        # Close button
        self._create_close_button(layout)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
    
    def _create_stats_grid(self, parent_layout):
        """Create and populate the statistics grid."""
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        stats_layout.setColumnStretch(1, 1)

        stats = self.stats_manager.get_stats_summary()

        row = 0
        for name, value in stats.items():
            name_label = QLabel(name)
            name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 14))
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            stats_layout.addWidget(name_label, row, 0)
            stats_layout.addWidget(value_label, row, 1)
            row += 1

        parent_layout.addLayout(stats_layout)
    
    def _create_close_button(self, parent_layout):
        """Create and style the close button."""
        close_button = QPushButton("✕ Close")
        close_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        close_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff4444, stop:1 #cc3333);
                border: none;
                padding: 15px 30px;
                border-radius: 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5555, stop:1 #dd4444);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ee3333, stop:1 #bb2222);
            }
        """)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.hide_overlay)
        parent_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def showEvent(self, event):
        """Handle show event with fade-in animation."""
        try:
            self.animation.finished.disconnect()
        except:
            pass
            
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().showEvent(event)

    def hide_overlay(self):
        """Hide the overlay with fade-out animation."""
        try:
            self.animation.finished.disconnect()
        except:
            pass
        
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()
