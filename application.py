# Import necessary modules from PyQt6 for GUI development.
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QFontDatabase, QImage
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect, 
                             QGridLayout, QCheckBox, QScrollArea, QLineEdit, QDialog, QMenu)
import sys
import os
import json
from datetime import datetime
import cv2
import mediapipe as mp
import numpy as np
import time
from scipy.spatial import distance as dist
import google.generativeai as genai
from posture import check_posture_with_gemini
from eyedistancescreen import eye_dist
from sitting import sittingt
from emotion_model import emote

# Global variables
GEMINI_API_KEY = "AIzaSyCxImEs_JzNLqajbSLC91QsOoh6heTenBs"
genai.configure(api_key=GEMINI_API_KEY)

# Statistics management class
class StatsManager:
    def __init__(self):
        self.stats_file = os.path.join(os.path.dirname(__file__), 'stats.json')
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Load statistics from JSON file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as file:
                    stats = json.load(file)
                    # Reset daily stats if it's a new day
                    today = datetime.now().strftime("%Y-%m-%d")
                    if stats.get('last_updated') != today:
                        stats['tasks_completed_today'] = 0
                        stats['last_updated'] = today
                        self.save_stats(stats)
                    return stats
            else:
                return {
                    "tasks_completed_today": 0,
                    "pomodoro_time_spent": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "total_tasks_completed": 0,
                    "total_pomodoro_sessions": 0,
                    "focus_streak": 0,
                    "break_time": 0
                }
        except Exception as e:
            print(f"Error loading stats: {e}")
            return {"tasks_completed_today": 0, "pomodoro_time_spent": 0, "last_updated": datetime.now().strftime("%Y-%m-%d")}
    
    def save_stats(self, stats=None):
        """Save statistics to JSON file"""
        try:
            if stats is None:
                stats = self.stats
            with open(self.stats_file, 'w', encoding='utf-8') as file:
                json.dump(stats, file, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def increment_tasks_completed(self):
        """Increment the number of tasks completed today"""
        self.stats['tasks_completed_today'] += 1
        self.stats['total_tasks_completed'] = self.stats.get('total_tasks_completed', 0) + 1
        self.save_stats()
    
    def add_pomodoro_time(self, minutes):
        """Add time spent in pomodoro sessions"""
        self.stats['pomodoro_time_spent'] += minutes
        self.save_stats()
    
    def complete_pomodoro_session(self):
        """Mark a complete pomodoro session"""
        self.stats['total_pomodoro_sessions'] = self.stats.get('total_pomodoro_sessions', 0) + 1
        self.stats['focus_streak'] = self.stats.get('focus_streak', 0) + 1
        self.save_stats()
    
    def get_stats_summary(self):
        """Get formatted statistics summary"""
        focus_time = self.stats.get('pomodoro_time_spent', 0)
        focus_hours = focus_time // 60
        focus_mins = focus_time % 60
        
        return {
            "Tasks Completed Today": str(self.stats.get('tasks_completed_today', 0)),
            "Focus Time Today": f"{focus_hours}h {focus_mins}m" if focus_hours > 0 else f"{focus_mins}m",
            "Total Tasks Completed": str(self.stats.get('total_tasks_completed', 0)),
            "Pomodoro Sessions": str(self.stats.get('total_pomodoro_sessions', 0)),
            "Current Focus Streak": str(self.stats.get('focus_streak', 0)),
            "Estimated Break Time": f"{self.stats.get('break_time', 0)}m"
        }
# Defines the overlay widget that displays statistics.
class StatsOverlay(QWidget):
    def __init__(self, parent=None, stats_manager=None):
        super().__init__(parent)
        self.stats_manager = stats_manager or StatsManager()
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
        layout.addWidget(title)        # Create a grid layout for the statistics.
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        stats_layout.setColumnStretch(1, 1)  # Make the value column stretchable.

        # Get real statistics from StatsManager
        stats = self.stats_manager.get_stats_summary()

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
                font-weight: bold;            }
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
        # Connect the button's clicked signal to the hide_overlay method.
        close_button.clicked.connect(self.hide_overlay)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the main layout for the StatsOverlay widget.
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

    # This event is called when the widget is shown.
    def showEvent(self, event):
        # Disconnect any existing connections to avoid conflicts
        try:
            self.animation.finished.disconnect()
        except:
            pass  # No connection to disconnect
            
        # Configure and start the fade-in animation.
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().showEvent(event)

    # This method is called to hide the overlay.
    def hide_overlay(self):
        # Disconnect any existing connections to avoid multiple connections
        try:
            self.animation.finished.disconnect()
        except:
            pass  # No connection to disconnect
        
        # Configure and start the fade-out animation.
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        # Connect the animation's finished signal to the widget's hide method.
        self.animation.finished.connect(self.hide)
        self.animation.start()

class PomodoroTimer(QFrame):
    def __init__(self, stats_manager=None):
        super().__init__()
        self.stats_manager = stats_manager or StatsManager()
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
        title_label = QLabel("Lock in timer")
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
        self.original_time = 25 * 60
        self.was_running = False

    def update_time(self):
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.time_label.setText(f"{mins:02d}:{secs:02d}")
        if self.time_left == 0:
            self.timer.stop()
            self.play_pause_button.setText("▶")
            # Track completed pomodoro session
            self.stats_manager.complete_pomodoro_session()
            self.stats_manager.add_pomodoro_time(self.original_time // 60)

    def start_stop(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play_pause_button.setText("▶")
            self.was_running = False
        else:
            self.timer.start(1000)
            self.play_pause_button.setText("⏸")
            self.was_running = True

    def reset(self):
        self.timer.stop()
        self.time_left = self.original_time
        self.time_label.setText("25:00")
        self.play_pause_button.setText("▶")
        self.was_running = False


class TasksWidget(QFrame):
    def __init__(self, stats_manager=None):
        super().__init__()
        self.tasks = []
        self.stats_manager = stats_manager or StatsManager()
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.txt')
        
        self.setStyleSheet('''
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 2px solid #404040;
                border-radius: 12px;
                max-width: 220px;
            }
        ''')
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Title
        title = QLabel("Today's Tasks")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet('''
            color: #ffffff;
            padding: 6px;
            background: rgba(100, 150, 255, 0.2);
            border-radius: 6px;
            border-left: 3px solid #6496ff;
        ''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Scroll area for tasks
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(120)
        self.scroll_area.setMaximumHeight(140)
        self.scroll_area.setStyleSheet('''
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        ''')
        
        # Widget to contain tasks
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(2, 2, 2, 2)
        self.tasks_layout.setSpacing(3)
        
        # Load tasks from file
        self.load_tasks()
        
        # Add stretch to push tasks to top
        self.tasks_layout.addStretch()
        
        self.scroll_area.setWidget(self.tasks_container)
        main_layout.addWidget(self.scroll_area)
        
        # Plus button to add new tasks
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(28, 28)
        self.plus_button.clicked.connect(self.add_new_task)
        self.plus_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        ''')
        
        # Center the plus button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.plus_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
    
    def load_tasks(self):
        """Load tasks from the text file"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line and '|' in line:
                            text, completed_str = line.split('|', 1)
                            completed = completed_str.lower() == 'true'
                            # Only add incomplete tasks to the widget
                            if not completed:
                                self.add_task_to_widget(text, completed)
            else:
                # Create default tasks if file doesn't exist
                default_tasks = [
                    ("Project work", False),
                    ("Code review", False),
                    ("Meeting", False)
                ]
                for text, completed in default_tasks:
                    self.add_task_to_widget(text, completed)
                self.save_tasks()
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def save_tasks(self):
        """Save all tasks to the text file"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as file:
                for text, checkbox, _ in self.tasks:
                    completed = checkbox.isChecked()
                    file.write(f"{text}|{completed}\n")
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task_to_widget(self, text, completed=False):
        """Add a task to the widget (internal method)"""
        task_container = QFrame()
        task_container.setStyleSheet('''
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                padding: 4px;
                margin: 1px;
                min-height: 24px;
                max-height: 28px;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        ''')
        
        task_layout = QHBoxLayout(task_container)
        task_layout.setContentsMargins(4, 2, 4, 2)
        task_layout.setSpacing(6)
        
        checkbox = QCheckBox(text)
        checkbox.setChecked(completed)
        checkbox.setFont(QFont("Segoe UI", 9))
        checkbox.setStyleSheet(f'''
            QCheckBox {{
                color: {"#888888" if completed else "#ffffff"};
                text-decoration: {"line-through" if completed else "none"};
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 12px;
                height: 12px;
                border-radius: 6px;
                border: 2px solid #6496ff;
                background-color: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: #6496ff;
                border: 2px solid #6496ff;
            }}
        ''')
        
        # Connect checkbox state change to removal function
        checkbox.stateChanged.connect(lambda state, task_text=text: self.on_task_checked(task_text, state))
        
        task_layout.addWidget(checkbox)
        
        # Insert before the stretch at the end
        insert_index = self.tasks_layout.count() - 1
        self.tasks_layout.insertWidget(insert_index, task_container)
        self.tasks.append((text, checkbox, task_container))
    
    def add_task(self, text, completed=False):
        """Add a new task and save to file"""
        self.add_task_to_widget(text, completed)
        self.save_tasks()
    
    def add_new_task(self):
        """Open dialog to add a new task"""
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_text = dialog.get_task_text()
            if task_text:
                self.add_task(task_text, False)
    def on_task_checked(self, task_text, state):
        """Handle task completion - remove from widget and save to file"""
        if state == Qt.CheckState.Checked.value:  # Task is completed
            # Track completed task in statistics
            self.stats_manager.increment_tasks_completed()
            
            # Remove from widget
            for i, (text, checkbox, container) in enumerate(self.tasks):
                if text == task_text:
                    # Remove from layout
                    self.tasks_layout.removeWidget(container)
                    container.setParent(None)
                    container.deleteLater()
                    
                    # Remove from tasks list
                    del self.tasks[i]
                    break
            
            # Save updated tasks to file
            self.save_tasks()
    
    def remove_task(self, task_text):
        """Remove a task completely from both widget and file"""
        for i, (text, checkbox, container) in enumerate(self.tasks):
            if text == task_text:
                # Remove from layout
                self.tasks_layout.removeWidget(container)
                container.setParent(None)
                container.deleteLater()
                
                # Remove from tasks list
                del self.tasks[i]
                break
        
        # Save updated tasks to file
        self.save_tasks()

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        self.setFixedSize(300, 120)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)
        
        layout = QVBoxLayout()
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task description...")
        layout.addWidget(self.task_input)
        
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Focus on input field and connect Enter key
        self.task_input.setFocus()
        self.task_input.returnPressed.connect(self.accept)
    
    def get_task_text(self):
        return self.task_input.text().strip()

# Defines the main application window.
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        # Initialize stats manager first
        self.stats_manager = StatsManager()
        
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
        self.initCamera()

    # Sets up the user interface of the main window.
    def initUI(self):
        # Create a central widget to hold all other widgets.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create the main vertical layout.
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 15)
        main_layout.setSpacing(15)        # Create a top bar layout for the menu button.
        top_bar = QHBoxLayout()
        self.menu_button = QPushButton()
        # Set the icon for the menu button.
        self.menu_button.setIcon(QIcon(self.create_menu_icon()))
        self.menu_button.setIconSize(QSize(32, 32))
        # Style the menu button.
        self.menu_button.setStyleSheet('''
            QPushButton { 
                border: none; 
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
            }            QPushButton:hover { 
                background: rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
        ''')
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Connect the button's clicked signal to show the hamburger menu.
        self.menu_button.clicked.connect(self.show_hamburger_menu)
        
        # Add title to top bar
        title_label = QLabel("Emotion Detector Pro")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet('''
            color: #ffffff;
        ''')
        top_bar.addWidget(self.menu_button, alignment=Qt.AlignmentFlag.AlignLeft)
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
        icons_layout.setContentsMargins(8, 8, 8, 8)
        icons_layout.setSpacing(6)

        self.icon_frames = []
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
                icon_label.setPixmap(QPixmap(icon_path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except:
                icon_label.setText("📊")
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_layout.addWidget(icon_label)
            icons_layout.addWidget(icon_frame)
            self.icon_frames.append(icon_frame)

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
        self.pomodoro_timer = PomodoroTimer(self.stats_manager)
        self.pomodoro_timer.play_pause_button.clicked.connect(self.pomodoro_timer.start_stop)
        self.pomodoro_timer.reset_button.clicked.connect(self.pomodoro_timer.reset)
        side_panel_layout.addWidget(self.pomodoro_timer)

        self.tasks_widget = TasksWidget(self.stats_manager)
        side_panel_layout.addWidget(self.tasks_widget)
        
        # Create an instance of the stats overlay and hide it initially.
        self.stats_overlay = StatsOverlay(self, self.stats_manager)
        self.stats_overlay.hide()
        
        # Add some spacing at the bottom
        side_panel_layout.addStretch()

    def initCamera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.camera_feed.setText("Error: Could not open camera.")
            return

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_frame)
        self.camera_timer.start(30)  # ~33 FPS

        # Mediapipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

        # Analysis variables
        self.count = 0
        self.LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
        self.blink_thresh = 0.21
        self.succ_frame = 2
        self.count_frame = 0
        self.interval_start_time = time.time()
        self.interval_blink_count = 0

    def calculate_EAR(self, eye):
        y1 = dist.euclidean(eye[1], eye[5])
        y2 = dist.euclidean(eye[2], eye[4])
        x1 = dist.euclidean(eye[0], eye[3])
        EAR = (y1 + y2) / (2.0 * x1)
        return EAR

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        if frame is None:
            print("None")
        h, w, c = frame.shape
        
        self.count += 1
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in self.LEFT_EYE_IDX]
                right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in self.RIGHT_EYE_IDX]
                
                for pt in left_eye:
                    cv2.circle(frame, pt, 2, (0,255,0), -1)
                for pt in right_eye:
                    cv2.circle(frame, pt, 2, (0,255,0), -1)

                left_EAR = self.calculate_EAR(left_eye)
                right_EAR = self.calculate_EAR(right_eye)
                avg_EAR = (left_EAR + right_EAR) / 2.0

                if avg_EAR < self.blink_thresh:
                    self.count_frame += 1
                else:
                    if self.count_frame >= self.succ_frame:
                        self.interval_blink_count += 1
                    self.count_frame = 0
        
        elapsed = time.time() - self.interval_start_time
        if elapsed >= 20:
            blink_rate = (self.interval_blink_count / elapsed) * 60
            print(f"Blink Rate: {blink_rate:.2f} BPM")
            self.interval_blink_count = 0
            self.interval_start_time = time.time()
            
        current_frame = frame.copy()

        if self.count % 30 == 0:
            posture = check_posture_with_gemini(current_frame)
            self.icon_frames[0].setToolTip(f"Posture: {posture}")
            sitting_time = sittingt(current_frame)
            print(f"Sitting Time: {sitting_time} seconds")
            emotion = emote(current_frame)
            self.icon_frames[2].setToolTip(f"Emotion: {emotion}")

        if self.count % 120 == 0:
            eye_distance = eye_dist(current_frame)
            self.icon_frames[1].setToolTip(f"Eye Distance: {eye_distance} cm")

        display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_image = QImage(display_frame.data, w, h, c * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_feed.setPixmap(pixmap.scaled(self.camera_feed.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

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
        # Draw three horizontal lines to represent a menu icon.        painter.drawLine(4, 8, 28, 8)
        painter.drawLine(4, 16, 28, 16)
        painter.drawLine(4, 24, 28, 24)
        painter.end()
        return pixmap

    # Shows the hamburger menu with options
    def show_hamburger_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet('''
            QMenu {
                background-color: #2b2b2b;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 4px;
                color: white;
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #007acc;
            }
            QMenu::item:pressed {
                background-color: #005a9e;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 4px 8px;
            }
        ''')
        
        # Stats action
        stats_action = menu.addAction("📊 View Statistics")
        stats_action.triggered.connect(self.show_stats_overlay)
        
        # Add separator
        menu.addSeparator()
        
        # Close action (minimize to tray or hide)
        close_action = menu.addAction("🗕 Minimize")
        close_action.triggered.connect(self.showMinimized)
        
        # Quit action
        quit_action = menu.addAction("❌ Quit Application")
        quit_action.triggered.connect(self.close_application)
        
        # Show menu at button position
        button_rect = self.menu_button.geometry()
        menu_pos = self.menu_button.mapToGlobal(button_rect.bottomLeft())
        menu.exec(menu_pos)
    
    # Show the statistics overlay
    def show_stats_overlay(self):
        # Set the geometry of the overlay to match the central widget's geometry.
        central_widget = self.centralWidget()
        if central_widget:
            self.stats_overlay.setGeometry(central_widget.geometry())
        self.stats_overlay.show()
    
    # Close the application
    def close_application(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        self.close()

    # Shows or hides the statistics overlay.
    def toggle_stats_overlay(self):
        if self.stats_overlay.isVisible():
            self.stats_overlay.hide_overlay()
        else:
            self.show_stats_overlay()

    # This event is called when the main window is resized.
    def resizeEvent(self, event):
        # If the overlay is visible, resize it to match the new window size.
        if hasattr(self, 'stats_overlay') and self.stats_overlay.isVisible():
            central_widget = self.centralWidget()
            if central_widget:
                self.stats_overlay.setGeometry(central_widget.geometry())
        super().resizeEvent(event)

    def closeEvent(self, event):
        if hasattr(self, 'cap'):
            self.cap.release()
        super().closeEvent(event)

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
