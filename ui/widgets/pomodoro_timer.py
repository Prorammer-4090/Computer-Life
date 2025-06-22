"""
Pomodoro Timer Widget
A timer widget for productivity tracking with play/pause and reset functionality.
"""
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from ..core.stats_manager import StatsManager
from ..core.config import DEFAULT_POMODORO_TIME


class PomodoroTimer(QFrame):
    """A Pomodoro timer widget with play/pause and reset functionality."""
    
    def __init__(self, stats_manager=None):
        super().__init__()
        self.stats_manager = stats_manager or StatsManager()
        self.time_left = DEFAULT_POMODORO_TIME
        self.original_time = DEFAULT_POMODORO_TIME
        self.was_running = False
        
        self._setup_timer()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_timer(self):
        """Initialize the QTimer for countdown functionality."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
    
    def _setup_ui(self):
        """Create the user interface elements."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Title label
        title_label = QLabel("Lock in timer")
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #888888; margin-bottom: 3px;")
        layout.addWidget(title_label)

        # Time display
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

        # Control buttons
        self._create_control_buttons(layout)
    
    def _create_control_buttons(self, parent_layout):
        """Create play/pause and reset buttons."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)
        
        # Play/Pause button
        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.clicked.connect(self.start_stop)
        
        # Reset button
        self.reset_button = QPushButton("⟳")
        self.reset_button.clicked.connect(self.reset)
        
        buttons_layout.addWidget(self.play_pause_button)
        buttons_layout.addWidget(self.reset_button)
        parent_layout.addLayout(buttons_layout)
    
    def _apply_styles(self):
        """Apply styling to the widget and its components."""
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
        
        button_style = '''
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {start_color}, stop:1 {end_color});
                border: none;
                border-radius: 16px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
                min-width: 30px;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {hover_start}, stop:1 {hover_end});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {pressed_start}, stop:1 {pressed_end});
            }}
        '''
        
        # Play/Pause button (green theme)
        self.play_pause_button.setStyleSheet(button_style.format(
            start_color='#4CAF50', end_color='#45a049',
            hover_start='#5CBF60', hover_end='#55b059',
            pressed_start='#3CAF40', pressed_end='#359039'
        ))
        
        # Reset button (orange theme)
        self.reset_button.setStyleSheet(button_style.format(
            start_color='#FF9800', end_color='#F57C00',
            hover_start='#FFA820', hover_end='#F68C00',
            pressed_start='#E68900', pressed_end='#D67C00'
        ))
    
    def update_time(self):
        """Update the timer display and handle completion."""
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.time_label.setText(f"{mins:02d}:{secs:02d}")
        
        if self.time_left == 0:
            self._handle_timer_completion()
    
    def _handle_timer_completion(self):
        """Handle what happens when the timer reaches zero."""
        self.timer.stop()
        self.play_pause_button.setText("▶")
        # Track completed pomodoro session
        self.stats_manager.complete_pomodoro_session()
        self.stats_manager.add_pomodoro_time(self.original_time // 60)

    def start_stop(self):
        """Toggle timer between running and stopped states."""
        if self.timer.isActive():
            self.timer.stop()
            self.play_pause_button.setText("▶")
            self.was_running = False
        else:
            self.timer.start(1000)  # 1 second intervals
            self.play_pause_button.setText("⏸")
            self.was_running = True

    def reset(self):
        """Reset the timer to its original time."""
        self.timer.stop()
        self.time_left = self.original_time
        self.time_label.setText("25:00")
        self.play_pause_button.setText("▶")
        self.was_running = False
