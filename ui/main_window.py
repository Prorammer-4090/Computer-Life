"""
Main Application Window
The main window class that orchestrates all UI components.
"""
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMenu)

from .core.stats_manager import StatsManager
from .core.config import APP_NAME, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_POSITION, DARK_THEME
from .widgets.stats_overlay import StatsOverlay
from .widgets.pomodoro_timer import PomodoroTimer
from .widgets.tasks_widget import TasksWidget
from .widgets.camera_feed import CameraFeedWidget
from .utils.icon_utils import create_menu_icon
from .utils.style_utils import get_menu_style


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        # Initialize core components
        self.stats_manager = StatsManager()
        
        self._setup_window()
        self._create_ui()
        self._apply_styles()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(*DEFAULT_WINDOW_POSITION, *DEFAULT_WINDOW_SIZE)
        self.setFont(QFont("Segoe UI", 10))
    
    def _create_ui(self):
        """Create the main user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 15)
        main_layout.setSpacing(15)
        
        # Top bar
        self._create_top_bar(main_layout)
        
        # Content area
        self._create_content_area(main_layout)
        
        # Stats overlay (hidden initially)
        self.stats_overlay = StatsOverlay(self, self.stats_manager)
        self.stats_overlay.hide()
    
    def _create_top_bar(self, parent_layout):
        """Create the top navigation bar."""
        top_bar = QHBoxLayout()
        
        # Menu button
        self.menu_button = QPushButton()
        self.menu_button.setIcon(QIcon(create_menu_icon()))
        self.menu_button.setIconSize(QSize(32, 32))
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_button.clicked.connect(self.show_hamburger_menu)
        
        # Title
        title_label = QLabel(APP_NAME)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        
        # Layout
        top_bar.addWidget(self.menu_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        top_bar.addStretch()
        
        parent_layout.addLayout(top_bar)
    
    def _create_content_area(self, parent_layout):
        """Create the main content area."""
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Camera feed (main area)
        self.camera_feed = CameraFeedWidget()
        content_layout.addWidget(self.camera_feed, stretch=3)
        
        # Side panel
        self._create_side_panel(content_layout)
        
        parent_layout.addLayout(content_layout)
    
    def _create_side_panel(self, parent_layout):
        """Create the side panel with timer and tasks."""
        side_panel_layout = QVBoxLayout()
        side_panel_layout.setSpacing(10)
        
        # Container with max width
        side_panel_container = QWidget()
        side_panel_container.setLayout(side_panel_layout)
        side_panel_container.setMaximumWidth(200)
        
        # Pomodoro timer
        self.pomodoro_timer = PomodoroTimer(self.stats_manager)
        side_panel_layout.addWidget(self.pomodoro_timer)
        
        # Tasks widget
        self.tasks_widget = TasksWidget(self.stats_manager)
        side_panel_layout.addWidget(self.tasks_widget)
        
        # Stretch to push everything up
        side_panel_layout.addStretch()
        
        parent_layout.addWidget(side_panel_container, stretch=1)
    
    def _apply_styles(self):
        """Apply styling to the main window and components."""
        # Main window style
        self.setStyleSheet(f'''
            QMainWindow {{
                background: {DARK_THEME['background_gradient']};
                color: {DARK_THEME['text_color']};
            }}
            QLabel {{
                color: {DARK_THEME['text_color']};
            }}
        ''')
        
        # Menu button style
        self.menu_button.setStyleSheet('''
            QPushButton { 
                border: none; 
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover { 
                background: rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
        ''')
    
    def show_hamburger_menu(self):
        """Show the hamburger menu with options."""
        menu = QMenu(self)
        menu.setStyleSheet(get_menu_style())
        
        # Menu actions
        stats_action = menu.addAction("📊 View Statistics")
        stats_action.triggered.connect(self.show_stats_overlay)
        
        menu.addSeparator()
        
        minimize_action = menu.addAction("🗕 Minimize")
        minimize_action.triggered.connect(self.showMinimized)
        
        quit_action = menu.addAction("❌ Quit Application")
        quit_action.triggered.connect(self.close_application)
        
        # Show menu
        button_rect = self.menu_button.geometry()
        menu_pos = self.menu_button.mapToGlobal(button_rect.bottomLeft())
        menu.exec(menu_pos)
    
    def show_stats_overlay(self):
        """Show the statistics overlay."""
        central_widget = self.centralWidget()
        if central_widget:
            self.stats_overlay.setGeometry(central_widget.geometry())
        self.stats_overlay.show()
    
    def close_application(self):
        """Close the application."""
        self.close()
    
    def toggle_stats_overlay(self):
        """Toggle the statistics overlay visibility."""
        if self.stats_overlay.isVisible():
            self.stats_overlay.hide_overlay()
        else:
            self.show_stats_overlay()
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        if hasattr(self, 'stats_overlay') and self.stats_overlay.isVisible():
            central_widget = self.centralWidget()
            if central_widget:
                self.stats_overlay.setGeometry(central_widget.geometry())
        super().resizeEvent(event)
