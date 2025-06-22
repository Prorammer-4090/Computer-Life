"""
Icon Utilities
Helper functions for creating and managing icons.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QLabel


def create_menu_icon(size=32):
    """Create a hamburger menu icon programmatically."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    pen = painter.pen()
    pen.setWidth(3)
    pen.setColor(QColor("white"))
    painter.setPen(pen)
    
    # Draw three horizontal lines
    y_positions = [size // 4, size // 2, 3 * size // 4]
    margin = size // 8
    
    for y in y_positions:
        painter.drawLine(margin, y, size - margin, y)
    
    painter.end()
    return pixmap


def load_icon_with_fallback(icon_path, fallback_text="📊", size=(20, 20)):
    """Load an icon from path with fallback to text."""
    icon_label = QLabel()
    
    try:
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                size[0], size[1], 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(scaled_pixmap)
            return icon_label
    except Exception as e:
        print(f"Failed to load icon {icon_path}: {e}")
    
    # Fallback to text
    icon_label.setText(fallback_text)
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return icon_label


def get_status_color(status_type, value):
    """Get color based on status type and value."""
    color_map = {
        'posture': {
            'good': '#4CAF50',
            'bad': '#f44336',
            'unknown': '#888888'
        },
        'eye_distance': {
            'optimal': '#2196F3',
            'too_close': '#FF9800',
            'too_far': '#FF9800',
            'unknown': '#888888'
        },
        'emotion': {
            'focused': '#4CAF50',
            'distracted': '#FF9800',
            'tired': '#f44336',
            'unknown': '#888888'
        }
    }
    
    return color_map.get(status_type, {}).get(value, '#888888')
