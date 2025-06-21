# Import necessary modules from PyQt6 for GUI development.
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QFontDatabase
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect, QGridLayout)
import sys

# Defines the overlay widget that displays statistics.
class StatsOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set window flags to make the overlay frameless and stay on top of other windows.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # Make the background of the widget translucent to see the window behind it.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create an opacity effect to animate the fade-in and fade-out of the overlay.
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        # Create an animation for the opacity property.
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)  # Animation duration in milliseconds.
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Set the easing curve for a smooth animation.

        # Main widget for the content of the overlay.
        content_widget = QFrame(self)
        # Set the style for the content widget using CSS-like syntax.
        content_widget.setStyleSheet("""
            background-color: rgba(20, 20, 20, 0.95);
            color: white;
            border-radius: 15px;
        """)

        # Create a vertical layout for the content widget.
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Create and style the title label.
        title = QLabel("Overall Statistics")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Create a grid layout for the statistics.
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        stats_layout.setColumnStretch(1, 1)  # Make the value column stretchable.

        # A dictionary of placeholder statistics.
        stats = {
            "Stress Levels": "Low",
            "Posture Analysis": "Good",
            "Emotion Timeline": "Happy -> Calm -> Focused",
            "Focus Time": "45 min",
            "Break Time": "10 min"
        }

        # Loop through the stats dictionary and create labels for each item.
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

        layout.addLayout(stats_layout)
        layout.addStretch()  # Add stretch to push the close button to the bottom.

        # Create and style the close button.
        close_button = QPushButton("Close")
        close_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border: 1px solid #555;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Connect the button's clicked signal to the hide_overlay method.
        close_button.clicked.connect(self.hide_overlay)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the main layout for the StatsOverlay widget.
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

    # This event is called when the widget is shown.
    def showEvent(self, event):
        # Configure and start the fade-in animation.
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().showEvent(event)

    # This method is called to hide the overlay.
    def hide_overlay(self):
        # Configure and start the fade-out animation.
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        # Connect the animation's finished signal to the widget's hide method.
        self.animation.finished.connect(self.hide)
        self.animation.start()


# Defines the main application window.
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        # Set the window title and initial geometry.
        self.setWindowTitle("Emotion Detector")
        self.setGeometry(100, 100, 800, 700) # Increased height for better spacing
        # Set the global style for the main window.
        self.setStyleSheet("background-color: #121212; color: white;")
        self.setFont(QFont("Segoe UI", 10))
        # Initialize the user interface.
        self.initUI()

    # Sets up the user interface of the main window.
    def initUI(self):
        # Create a central widget to hold all other widgets.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Create the main vertical layout.
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 10, 20, 20)

        # Create a top bar layout for the menu button.
        top_bar = QHBoxLayout()
        menu_button = QPushButton()
        # Set the icon for the menu button.
        menu_button.setIcon(QIcon(self.create_menu_icon()))
        menu_button.setIconSize(QSize(32, 32))
        # Style the menu button.
        menu_button.setStyleSheet("""
            QPushButton { border: none; }
            QPushButton:hover { background-color: #333333; border-radius: 5px; }
        """)
        menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Connect the button's clicked signal to toggle the stats overlay.
        menu_button.clicked.connect(self.toggle_stats_overlay)
        top_bar.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch() # Push the button to the left.
        main_layout.addLayout(top_bar)

        # Create a placeholder for the camera feed.
        self.camera_feed = QLabel("Camera Feed")
        self.camera_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_feed.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.camera_feed.setMinimumSize(640, 480)
        self.camera_feed.setStyleSheet("background-color: black; border: 2px solid #222; border-radius: 15px;")
        main_layout.addWidget(self.camera_feed, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)

        # Create a horizontal layout for the information labels.
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)
        # Create and add the info labels to the layout.
        self.posture_label = self.create_info_label("Posture", "Good")
        self.distance_label = self.create_info_label("Eye Distance", "OK")
        self.emotion_label = self.create_info_label("Emotion", "Neutral")
        info_layout.addWidget(self.posture_label)
        info_layout.addWidget(self.distance_label)
        info_layout.addWidget(self.emotion_label)
        main_layout.addLayout(info_layout)

        # Create an instance of the stats overlay and hide it initially.
        self.stats_overlay = StatsOverlay(self)
        self.stats_overlay.hide()

    # Creates a styled information label widget.
    def create_info_label(self, title_text, value_text):
        # The main container for the info label.
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                padding: 15px;
                border-radius: 10px;
            }
        """)
        # Layout for the title and value labels.
        layout = QVBoxLayout(frame)
        layout.setSpacing(5)
        # The title part of the label (e.g., "Posture").
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #aaa; border: none; background: transparent;")
        # The value part of the label (e.g., "Good").
        value_label = QLabel(value_text)
        value_label.setFont(QFont("Segoe UI", 14))
        value_label.setStyleSheet("color: white; border: none; background: transparent;")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return frame

    # Creates a menu icon programmatically using QPainter.
    def create_menu_icon(self):
        # Create a QPixmap to draw on.
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent) # Make the pixmap background transparent.
        # Create a QPainter to draw the icon.
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # Enable anti-aliasing for smooth lines.
        pen = painter.pen()
        pen.setWidth(3)
        pen.setColor(QColor("white"))
        painter.setPen(pen)
        # Draw three horizontal lines to represent a menu icon.
        painter.drawLine(4, 8, 28, 8)
        painter.drawLine(4, 16, 28, 16)
        painter.drawLine(4, 24, 28, 24)
        painter.end()
        return pixmap

    # Shows or hides the statistics overlay.
    def toggle_stats_overlay(self):
        if self.stats_overlay.isVisible():
            self.stats_overlay.hide_overlay()
        else:
            # Set the geometry of the overlay to match the central widget's geometry.
            self.stats_overlay.setGeometry(self.centralWidget().geometry())
            self.stats_overlay.show()

    # This event is called when the main window is resized.
    def resizeEvent(self, event):
        # If the overlay is visible, resize it to match the new window size.
        if hasattr(self, 'stats_overlay') and self.stats_overlay.isVisible():
            self.stats_overlay.setGeometry(self.centralWidget().geometry())
        super().resizeEvent(event)

# Main function to run the application.
def window():
    # Create the QApplication instance.
    app = QApplication(sys.argv)
    # Create an instance of the main window.
    win = MyWindow()
    # Show the main window.
    win.show()
    # Start the application's event loop.
    sys.exit(app.exec())

# Entry point of the script.
window()