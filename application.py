# Import necessary modules from PyQt6 for GUI development.
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QFontDatabase, QImage
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect, 
                             QGridLayout, QCheckBox, QScrollArea, QLineEdit, QDialog, QMenu, QMessageBox)
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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
    
    def add_pomodoro_time_in_seconds(self, seconds):
        """Add time spent in pomodoro sessions in seconds"""
        self.stats['pomodoro_time_spent'] = self.stats.get('pomodoro_time_spent', 0) + seconds
        self.save_stats()
    
    def complete_pomodoro_session(self):
        """Mark a complete pomodoro session"""
        self.stats['total_pomodoro_sessions'] = self.stats.get('total_pomodoro_sessions', 0) + 1
        self.stats['focus_streak'] = self.stats.get('focus_streak', 0) + 1
        self.save_stats()
    
    def get_stats_summary(self):
        """Get formatted statistics summary"""
        focus_time_seconds = self.stats.get('pomodoro_time_spent', 0)
        focus_hours = focus_time_seconds // 3600
        focus_mins = (focus_time_seconds % 3600) // 60
        
        return {
            "Tasks Completed Today": str(self.stats.get('tasks_completed_today', 0)),
            "Focus Time Today": f"{focus_hours}h {focus_mins}m" if focus_hours > 0 else f"{focus_mins}m",
            "Total Tasks Completed": str(self.stats.get('total_tasks_completed', 0)),
            "Pomodoro Sessions": str(self.stats.get('total_pomodoro_sessions', 0)),
            "Current Focus Streak": str(self.stats.get('focus_streak', 0)),
            "Estimated Break Time": f"{self.stats.get('break_time', 0)}m"        }

# Defines the overlay widget that displays statistics with charts and modern UI
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
                stop:0 rgba(30, 30, 30, 0.95), stop:1 rgba(10, 10, 10, 0.95));
            color: white;
            border-radius: 20px;
            border: 2px solid rgba(100, 150, 255, 0.6);
        """)

        # Create the main layout for the content widget
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title with improved styling
        title_container = QFrame()
        title_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(100, 150, 255, 0.3), stop:1 rgba(50, 100, 200, 0.3));
            border-radius: 15px;
            padding: 15px;
        """)
        title_layout = QVBoxLayout(title_container)
        
        title = QLabel("📊 Analytics Dashboard")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 5px;")
        
        subtitle = QLabel("Complete overview of your productivity metrics")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #cccccc; margin-bottom: 10px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        main_layout.addWidget(title_container)

        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(100, 150, 255, 0.6);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(100, 150, 255, 0.8);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Scrollable content widget
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)

        # Create stats cards in a grid
        self.create_stats_cards(content_layout)
        
        # Create charts section
        self.create_charts_section(content_layout)

        # Set scroll area content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Close button with improved styling
        close_button = QPushButton("✕ Close Dashboard")
        close_button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        close_button.setFixedHeight(50)
        close_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff4444, stop:1 #cc2222);
                border: none;
                padding: 15px 30px;
                border-radius: 15px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5555, stop:1 #dd3333);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ee3333, stop:1 #aa1111);
            }
        """)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.hide_overlay)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the main layout for the StatsOverlay widget
        overlay_layout = QVBoxLayout(self)
        overlay_layout.addWidget(content_widget)
        self.setLayout(overlay_layout)
        
        # Add update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(5000)  # Update every 5 seconds

    def create_stats_cards(self, parent_layout):
        """Create modern stats cards with icons and values"""
        cards_container = QFrame()
        cards_layout = QGridLayout(cards_container)
        cards_layout.setSpacing(15)
        
        # Get real statistics from StatsManager
        stats = self.stats_manager.get_stats_summary()
        self.stats_labels = {}
        
        # Define card configurations with icons and colors
        card_configs = [
            ("Tasks Completed Today", "🎯", "#4CAF50", "tasks completed"),
            ("Focus Time Today", "⏰", "#2196F3", "focus time"),
            ("Total Tasks Completed", "📋", "#FF9800", "total tasks"),
            ("Pomodoro Sessions", "🍅", "#9C27B0", "sessions"),
            ("Current Focus Streak", "🔥", "#F44336", "streak"),
            ("Estimated Break Time", "☕", "#607D8B", "break time")
        ]
        
        for i, (stat_name, icon, color, description) in enumerate(card_configs):
            card = self.create_stat_card(
                stat_name, 
                str(stats.get(stat_name, "0")), 
                icon, 
                color, 
                description
            )
            row = i // 3
            col = i % 3
            cards_layout.addWidget(card, row, col)
            
        parent_layout.addWidget(cards_container)

    def create_stat_card(self, title, value, icon, color, description):
        """Create an individual stat card with modern design"""
        card = QFrame()
        card.setFixedSize(200, 120)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.1), stop:1 rgba(255, 255, 255, 0.05));
                border: 2px solid {color};
                border-radius: 15px;
                padding: 10px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.15), stop:1 rgba(255, 255, 255, 0.08));
                border: 2px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Icon and title row
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setStyleSheet(f"color: {color};")
        
        title_label = QLabel(title.replace(" ", "\n"))
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; line-height: 1.2;")
        title_label.setWordWrap(True)
        
        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; margin: 5px;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 8))
        desc_label.setStyleSheet("color: #888888;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(top_layout)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        # Store reference for updates
        self.stats_labels[title] = value_label
        
        return card

    def create_charts_section(self, parent_layout):
        """Create charts section with productivity visualizations"""
        charts_title = QLabel("📈 Productivity Analytics")
        charts_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        charts_title.setStyleSheet("color: #ffffff; margin: 20px 0 10px 0;")
        parent_layout.addWidget(charts_title)
        
        # Charts container
        charts_container = QFrame()
        charts_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setSpacing(20)
        
        # Create pie chart for task completion
        self.create_task_completion_chart(charts_layout)
        
        # Create progress bars for daily goals
        self.create_progress_section(charts_layout)
        
        parent_layout.addWidget(charts_container)

    def create_task_completion_chart(self, parent_layout):
        """Create a pie chart showing task completion"""
        chart_container = QFrame()
        chart_container.setFixedSize(300, 250)
        chart_container.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(chart_container)
        
        # Chart title
        title = QLabel("Task Completion")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create matplotlib figure
        fig = Figure(figsize=(4, 3), facecolor='none')
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background: transparent;")
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')
        
        # Data for pie chart
        tasks_today = self.stats_manager.stats.get('tasks_completed_today', 0)
        remaining = max(0, 8 - tasks_today)  # Assuming 8 tasks daily goal
        
        if tasks_today > 0 or remaining > 0:
            labels = ['Completed', 'Remaining']
            sizes = [tasks_today, remaining]
            colors = ['#4CAF50', '#666666']
            explode = (0.1, 0)  # explode completed slice
            
            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                  autopct='%1.0f', startangle=90, textprops={'color': 'white', 'fontsize': 10})
        else:
            ax.text(0.5, 0.5, 'No data yet', transform=ax.transAxes, 
                   ha='center', va='center', color='white', fontsize=12)
        
        ax.axis('equal')
        fig.tight_layout()
        
        layout.addWidget(canvas)
        parent_layout.addWidget(chart_container)

    def create_progress_section(self, parent_layout):
        """Create progress bars for daily goals"""
        progress_container = QFrame()
        progress_container.setFixedWidth(300)
        progress_container.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(progress_container)
        
        # Progress section title
        title = QLabel("Daily Goals Progress")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 15px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Progress bars data
        progress_data = [
            ("Tasks", self.stats_manager.stats.get('tasks_completed_today', 0), 8, "#4CAF50"),
            ("Focus Time", self.stats_manager.stats.get('pomodoro_time_spent', 0) // 60, 120, "#2196F3"),  # minutes
            ("Pomodoro Sessions", self.stats_manager.stats.get('total_pomodoro_sessions', 0), 4, "#9C27B0")
        ]
        
        for label, current, target, color in progress_data:
            self.create_progress_bar(layout, label, current, target, color)
        
        parent_layout.addWidget(progress_container)

    def create_progress_bar(self, parent_layout, label, current, target, color):
        """Create a single progress bar with label"""
        container = QFrame()
        container.setStyleSheet("margin: 5px 0;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(5)
        
        # Label with values
        label_text = QLabel(f"{label}: {current}/{target}")
        label_text.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label_text.setStyleSheet("color: #ffffff;")
        layout.addWidget(label_text)
        
        # Progress bar background
        progress_bg = QFrame()
        progress_bg.setFixedHeight(20)
        progress_bg.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
        """)
        
        # Progress bar fill
        progress_fill = QFrame(progress_bg)
        progress_value = min(100, (current / target * 100) if target > 0 else 0)
        fill_width = int(270 * progress_value / 100)  # 270 is approximate width
        progress_fill.setFixedSize(fill_width, 20)
        progress_fill.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {color}88);
                border-radius: 10px;
            }}
        """)
        
        # Percentage label
        percent_label = QLabel(f"{progress_value:.0f}%")
        percent_label.setFont(QFont("Segoe UI", 10))
        percent_label.setStyleSheet(f"color: {color}; margin-top: 2px;")
        percent_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(progress_bg)
        layout.addWidget(percent_label)
        parent_layout.addWidget(container)

    def update_stats(self):
        """Reloads stats from the file and updates all displays"""
        self.stats_manager.stats = self.stats_manager.load_stats()
        stats_summary = self.stats_manager.get_stats_summary()
        
        # Update stat cards
        for name, value in stats_summary.items():
            if name in self.stats_labels:
                self.stats_labels[name].setText(str(value))
        
        # Note: In a more complex implementation, you would also update charts here
        # For now, charts are updated when the overlay is shown

    def showEvent(self, event):
        """Called when the widget is shown"""
        # Disconnect any existing connections to avoid conflicts
        try:
            self.animation.finished.disconnect()
        except:
            pass  # No connection to disconnect
            
        # Configure and start the fade-in animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().showEvent(event)

    def hide_overlay(self):
        """Hide the overlay with fade-out animation"""
        # Disconnect any existing connections to avoid multiple connections
        try:
            self.animation.finished.disconnect()
        except:
            pass  # No connection to disconnect
        
        # Configure and start the fade-out animation
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        # Connect the animation's finished signal to the widget's hide method
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
        self.stats_manager.add_pomodoro_time_in_seconds(1)
        if self.time_left == 0:
            self.timer.stop()
            self.play_pause_button.setText("▶")
            # Track completed pomodoro session
            self.stats_manager.complete_pomodoro_session()

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
        self.setWindowTitle("BlurNout")
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
        title_label = QLabel("BlurNout")
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
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)        # Analysis variables
        self.count = 0
        self.LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
        self.blink_thresh = 0.21
        self.succ_frame = 2
        self.count_frame = 0
        self.interval_start_time = time.time()
        self.interval_blink_count = 0        # Notification tracking variables
        self.last_blink_notification = 0
        self.last_sitting_notification = 0
        self.last_eye_distance_notification = time.time()
        self.bad_posture_start_time = None
        self.last_posture_notification = 0
        self.last_emotion_notification = 0
        self.last_posture_check = 0  # For Gemini posture detection timing
        self.last_shown_messages = {}  # Track when each specific message was last shown
        self.current_blink_rate = 0
        self.current_sitting_time = 0
        self.current_eye_distance = 50  # Default safe distance
        self.current_posture = "Good"
        self.current_emotion = "Neutral"

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
                    
        # Always create current_frame for use in other functions
        current_frame = frame.copy()        
        elapsed = time.time() - self.interval_start_time
        if elapsed >= 4:
            eye_distance = eye_dist(current_frame)
            blink_rate = (self.interval_blink_count / elapsed) * 60
            self.current_blink_rate = blink_rate
            self.current_eye_distance = eye_distance
            self.icon_frames[1].setToolTip(f"Blink Rate: {blink_rate:.2f} BPM\nEye Distance: {eye_distance} cm")
            self.interval_blink_count = 0
            self.interval_start_time = time.time()
            
        # Check posture with Gemini every 5 minutes to avoid lag
        current_time = time.time()
        if current_time - self.last_posture_check >= 10:  # 10 seconds
            posture = check_posture_with_gemini(current_frame)
            self.current_posture = posture
            self.last_posture_check = current_time
              # Check sitting time every 30 frames (more frequent as it's not using AI)
        if self.count % 10 == 0:
            sitting_time = sittingt(current_frame)
            self.current_sitting_time = sitting_time
            sitting_time_minutes = sitting_time / 60  # Convert seconds to minutes
            self.icon_frames[0].setToolTip(f"Posture: {self.current_posture}\nSitting Time: {sitting_time_minutes:.1f} minutes")
            emotion = emote(current_frame)
            self.current_emotion = emotion
            self.icon_frames[2].setToolTip(f"Emotion: {emotion}")

        # Check for notifications
        self.check_notifications()

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
    def show_stats_overlay(self):
        # Update stats before showing
        self.stats_overlay.update_stats()
        # Position the overlay to cover the central widget area
        central_widget = self.centralWidget()
        if central_widget:
            self.stats_overlay.setGeometry(central_widget.geometry())
        # Show the overlay with fade-in animation
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
    def show_notification(self, title, message):
        """Show a notification popup using PyQt6 QMessageBox with 30-second throttling"""
        current_time = time.time()
        message_key = f"{title}:{message}"  # Create unique key for this specific message
        
        # Check if this exact message was shown within the last 30 seconds
        if message_key in self.last_shown_messages:
            time_since_last = current_time - self.last_shown_messages[message_key]
            if time_since_last < 5:  # 5 seconds throttling
                return  # Don't show the notification, it's too soon
        
        # Update the timestamp for this message
        self.last_shown_messages[message_key] = current_time
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
            }
            QMessageBox QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #005a9e;
            }
            QMessageBox QPushButton:pressed {
                background-color: #004080;
            }
        """)
        msg_box.exec()
    def check_notifications(self):
        """Check all health conditions and show notifications if needed"""
        current_time = time.time()
        
        # Check blink rate (every 2 minutes minimum)
        if (self.current_blink_rate is not None and self.current_blink_rate < 6 and 
            current_time - self.last_blink_notification > 120 and current_time > 30):  # 2 minutes
            self.show_notification(
                "Blink Rate Alert", 
                "Your blink rate is too low! Please close your eyes and blink more often to keep them moist."
            )
            self.last_blink_notification = current_time
        
        # Check sitting time (every 5 minutes minimum)
        if (self.current_sitting_time is not None and self.current_sitting_time > 3600 and  # 60 minutes in seconds
            current_time - self.last_sitting_notification > 300):  # 5 minutes
            self.show_notification(
                "Break Time Alert", 
                "You've been sitting for over an hour! Please take a break and move around for at least 2 minutes."
            )
            self.last_sitting_notification = current_time
        
        # Check eye distance (every 2 minutes minimum)
        if (self.current_eye_distance is not None and self.current_eye_distance < 40): 
            self.show_notification(
                "Eye Distance Alert", 
                "You're sitting too close to the screen! Please move back to at least 40cm distance to protect your eyes."
            )
            self.last_eye_distance_notification = current_time
        
        # Check posture (track bad posture duration)
        if (self.current_posture is not None and 
            ("bad" in self.current_posture.lower() or "poor" in self.current_posture.lower()) and current_time > 30):
            if self.bad_posture_start_time is None:
                self.bad_posture_start_time = current_time
            elif (current_time - self.bad_posture_start_time > 600 and  # 10 minutes
                  current_time - self.last_posture_notification > 600):  # Don't spam
                self.show_notification(
                    "Posture Alert", 
                    "You've had poor posture for 15 minutes! Please straighten your back and adjust your seating position."
                )
                self.last_posture_notification = current_time
        else:
            self.bad_posture_start_time = None  # Reset if posture is good
          # Check emotions (every 10 minutes minimum for positive/negative feedback)
        if (self.current_emotion is not None and 
            current_time - self.last_emotion_notification > 600 and current_time > 30):  # 10 minutes
            emotion_lower = self.current_emotion.lower()
            
            if "happy" in emotion_lower or "joy" in emotion_lower or "smile" in emotion_lower:
                self.show_notification(
                    "Great Work!", 
                    "You're looking happy and positive! Keep up the excellent work! 😊"
                )
                self.last_emotion_notification = current_time
            
            elif ("sad" in emotion_lower or "stress" in emotion_lower or 
                  "angry" in emotion_lower or "frustrated" in emotion_lower):
                self.show_notification(
                    "Stay Strong!", 
                    "Challenges are temporary, but your strength is permanent. Take a deep breath - this too shall pass! 💪"
                )
                self.last_emotion_notification = current_time

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
