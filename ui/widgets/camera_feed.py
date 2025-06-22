"""
Camera Feed Widget
Widget for displaying camera feed with status icons.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame)

from ..core.config import ICON_PATHS


class CameraFeedWidget(QWidget):
    """Widget for displaying camera feed with overlay icons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Create the user interface elements."""
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Main camera feed display
        self.camera_feed = QLabel("📹 Camera Feed\n\nConnecting to camera...")
        self.camera_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_feed.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.camera_feed.setMinimumSize(500, 360)
        layout.addWidget(self.camera_feed, 0, 0)

        # Status icons overlay
        self._create_status_icons(layout)
    
    def _create_status_icons(self, parent_layout):
        """Create status icons overlay."""
        icons_container = QWidget()
        icons_layout = QVBoxLayout(icons_container)
        icons_layout.setContentsMargins(8, 8, 8, 8)
        icons_layout.setSpacing(6)

        # Create icon frames
        icon_configs = [
            (ICON_PATHS['posture'], "Posture: Good", "#4CAF50"),
            (ICON_PATHS['eye'], "Eye Distance: Optimal", "#2196F3"),
            (ICON_PATHS['emoji'], "Emotion: Focused", "#FF9800")
        ]
        
        for icon_path, tooltip, color in icon_configs:
            icon_frame = self._create_icon_frame(icon_path, tooltip, color)
            icons_layout.addWidget(icon_frame)

        icons_layout.addStretch()
        parent_layout.addWidget(icons_container, 0, 0, 
                               Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    
    def _create_icon_frame(self, icon_path, tooltip, color):
        """Create a single status icon frame."""
        icon_frame = QFrame()
        icon_frame.setStyleSheet(f'''
            QFrame {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid {color};
                border-radius: 6px;
                padding: 4px;
            }}
            QFrame:hover {{
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid {color};
            }}
        ''')
        
        icon_frame.setToolTip(tooltip)
        
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(2, 2, 2, 2)
        
        icon_label = QLabel()
        try:
            icon_label.setPixmap(QPixmap(icon_path).scaled(
                20, 20, Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation))
        except:
            # Fallback to emoji if image not found
            icon_label.setText("📊")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_layout.addWidget(icon_label)
        return icon_frame
    
    def _apply_styles(self):
        """Apply styling to the widget."""
        self.setStyleSheet('''
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 3px solid #404040;
                border-radius: 20px;
            }
        ''')
        
        self.camera_feed.setStyleSheet('''
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a1a, stop:0.5 #0a0a0a, stop:1 #1a1a1a);
            border: 2px solid #333;
            border-radius: 15px;
            color: #888888;
            padding: 20px;
        ''')
        
        # Style for icons container
        self.findChild(QWidget).setStyleSheet('''
            QWidget {
                background: rgba(0, 0, 0, 0.7);
                border-radius: 12px;
            }
        ''')
    
    def update_camera_feed(self, frame):
        """Update the camera feed with a new frame."""
        # This method would be implemented to display actual camera frames
        # For now, it's a placeholder
        pass
    
    def update_status_icon(self, icon_type, status, color):
        """Update a specific status icon."""
        # This method would be implemented to update individual icon states
        # For now, it's a placeholder
        pass
