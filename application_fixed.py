# Import necessary modules from PyQt6 for GUI development.
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QFontDatabase
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect, QGridLayout, QCheckBox)
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
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(40, 40, 40, 0.98), stop:1 rgba(20, 20, 20, 0.98));
            color: white;
            border-radius: 20px;
            border: 2px solid rgba(100, 150, 255, 0.3);
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
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ee3333, stop:1 #bb2222);
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

class PomodoroTimer(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('''
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 2px solid #404040;
                padding: 10px;
                border-radius: 12px;
                max-width: 180px;
            }
        ''')
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Title label
        title_label = QLabel("Pomodoro Timer")
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #888888; margin-bottom: 3px;")
        layout.addWidget(title_label)

        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet('''
            color: #00ff88;
            background: rgba(0, 255, 136, 0.1);
            border-radius: 6px;
            padding: 6px;
            margin: 3px;
        ''')
        layout.addWidget(self.time_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)
        
        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border: none;
                border-radius: 16px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #55b059);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3CAF40, stop:1 #359039);
            }
        ''')
        
        self.reset_button = QPushButton("⟳")
        self.reset_button.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF9800, stop:1 #F57C00);
                border: none;
                border-radius: 16px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA820, stop:1 #F68C00);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E68900, stop:1 #D67C00);
            }
        ''')
        
        buttons_layout.addWidget(self.play_pause_button)
        buttons_layout.addWidget(self.reset_button)
        layout.addLayout(buttons_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.time_left = 25 * 60

    def update_time(self):
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.time_label.setText(f"{mins:02d}:{secs:02d}")
        if self.time_left == 0:
            self.timer.stop()
            self.play_pause_button.setText("▶")

    def start_stop(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play_pause_button.setText("▶")
        else:
            self.timer.start(1000)
            self.play_pause_button.setText("⏸")

    def reset(self):
        self.timer.stop()
        self.time_left = 25 * 60
        self.time_label.setText("25:00")
        self.play_pause_button.setText("▶")


class TasksWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('''
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 2px solid #404040;
                padding: 8px;
                border-radius: 12px;
                max-width: 180px;
            }
        ''')
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        title = QLabel("Today's Tasks")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet('''
            color: #ffffff;
            padding: 5px;
            background: rgba(100, 150, 255, 0.2);
            border-radius: 5px;
            border-left: 3px solid #6496ff;
        ''')
        layout.addWidget(title)

        tasks = [
            ("Project work", False),
            ("Code review", True),
            ("Meeting", False),
            ("Documentation", False)
        ]
        
        for task_text, completed in tasks:
            task_container = QFrame()
            task_container.setStyleSheet('''
                QFrame {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                    padding: 4px;
                    margin: 1px;
                    min-height: 25px;
                    max-height: 28px;
                }
                QFrame:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
            ''')
            
            task_layout = QHBoxLayout(task_container)
            task_layout.setContentsMargins(6, 4, 6, 4)
            task_layout.setSpacing(6)
            
            checkbox = QCheckBox()
            checkbox.setChecked(completed)
            checkbox.setStyleSheet('''
                QCheckBox::indicator {
                    width: 14px;
                    height: 14px;
                    border-radius: 7px;
                    border: 2px solid #6496ff;
                    background-color: transparent;
                }
                QCheckBox::indicator:checked {
                    background-color: #6496ff;
                    border: 2px solid #6496ff;
                }
            ''')
            
            task_label = QLabel(task_text)
            task_label.setFont(QFont("Segoe UI", 8))
            task_label.setStyleSheet(f'''
                color: {"#888888" if completed else "#ffffff"};
                text-decoration: {"line-through" if completed else "none"};
            ''')
            task_label.setWordWrap(False)
            
            task_layout.addWidget(checkbox)
            task_layout.addWidget(task_label, 1)
            
            layout.addWidget(task_container)

# Defines the main application window.
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        # Set the window title and initial geometry.
        self.setWindowTitle("Emotion Detector Pro")
        self.setGeometry(300, 50, 900, 600)
        # Set the global style for the main window.
        self.setStyleSheet('''
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #0f0f0f, stop:1 #1a1a1a);
                color: white;
            }
            QLabel {
                color: #ffffff;
            }
        ''')
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
        main_layout.setContentsMargins(15, 10, 15, 15)
        main_layout.setSpacing(15)

        # Create a top bar layout for the menu button.
        top_bar = QHBoxLayout()
        menu_button = QPushButton()
        # Set the icon for the menu button.
        menu_button.setIcon(QIcon(self.create_menu_icon()))
        menu_button.setIconSize(QSize(32, 32))
        # Style the menu button.
        menu_button.setStyleSheet('''
            QPushButton { 
                border: none; 
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover { 
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
        ''')
        menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Connect the button's clicked signal to toggle the stats overlay.
        menu_button.clicked.connect(self.toggle_stats_overlay)
        
        # Add title to top bar
        title_label = QLabel("Emotion Detector Pro")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet('''
            color: #ffffff;
        ''')
        
        top_bar.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        main_layout.addLayout(content_layout)

        # --- Camera Feed with Icons ---
        camera_container = QWidget()
        camera_container.setStyleSheet('''
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 3px solid #404040;
                border-radius: 20px;
            }
        ''')
        camera_container_layout = QGridLayout(camera_container)
        camera_container_layout.setContentsMargins(10, 10, 10, 10)

        self.camera_feed = QLabel("📹 Camera Feed\n\nConnecting to camera...")
        self.camera_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_feed.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.camera_feed.setMinimumSize(500, 360)
        self.camera_feed.setStyleSheet('''
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a1a, stop:0.5 #0a0a0a, stop:1 #1a1a1a);
            border: 2px solid #333;
            border-radius: 15px;
            color: #888888;
            padding: 20px;
        ''')
        camera_container_layout.addWidget(self.camera_feed, 0, 0)

        # Icons on top-left of camera feed with improved styling
        icons_container = QWidget()
        icons_container.setStyleSheet('''
            QWidget {
                background: rgba(0, 0, 0, 0.7);
                border-radius: 12px;
            }
        ''')
        icons_layout = QVBoxLayout(icons_container)
        icons_layout.setContentsMargins(15, 15, 15, 15)
        icons_layout.setSpacing(12)

        # Create icon containers with better styling
        for icon_path, tooltip, color in [
            ("img/posture.png", "Posture: Good", "#4CAF50"),
            ("img/eye.png", "Eye Distance: Optimal", "#2196F3"),
            ("img/emoji.png", "Emotion: Focused", "#FF9800")
        ]:
            icon_frame = QFrame()
            icon_frame.setStyleSheet(f'''
                QFrame {{
                    background: rgba(255, 255, 255, 0.1);
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 8px;
                }}
                QFrame:hover {{
                    background: rgba(255, 255, 255, 0.2);
                    border: 2px solid {color};
                }}
            ''')
            icon_frame.setToolTip(tooltip)
            
            icon_layout = QVBoxLayout(icon_frame)
            icon_layout.setContentsMargins(4, 4, 4, 4)
            
            icon_label = QLabel()
            try:
                icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except:
                icon_label.setText("📊")
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_layout.addWidget(icon_label)
            icons_layout.addWidget(icon_frame)

        icons_layout.addStretch()
        camera_container_layout.addWidget(icons_container, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        content_layout.addWidget(camera_container, stretch=3)

        # Side panel with better spacing
        side_panel_layout = QVBoxLayout()
        side_panel_layout.setSpacing(10)
        
        # Create a container for the side panel with max width
        side_panel_container = QWidget()
        side_panel_container.setLayout(side_panel_layout)
        side_panel_container.setMaximumWidth(200)
        
        content_layout.addWidget(side_panel_container, stretch=1)

        self.pomodoro_timer = PomodoroTimer()
        self.pomodoro_timer.play_pause_button.clicked.connect(self.pomodoro_timer.start_stop)
        self.pomodoro_timer.reset_button.clicked.connect(self.pomodoro_timer.reset)
        side_panel_layout.addWidget(self.pomodoro_timer)

        self.tasks_widget = TasksWidget()
        side_panel_layout.addWidget(self.tasks_widget)
        
        # Create an instance of the stats overlay and hide it initially.
        self.stats_overlay = StatsOverlay(self)
        self.stats_overlay.hide()
        
        # Add some spacing at the bottom
        side_panel_layout.addStretch()

    # Creates a menu icon programmatically using QPainter.
    def create_menu_icon(self):
        # Create a QPixmap to draw on.
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        # Create a QPainter to draw the icon.
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
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
