"""
Application Configuration and Constants
"""

# Application Constants
APP_NAME = "Emotion Detector Pro"
DEFAULT_WINDOW_SIZE = (900, 600)
DEFAULT_WINDOW_POSITION = (300, 50)

# Timer Configuration
DEFAULT_POMODORO_TIME = 25 * 60  # 25 minutes in seconds

# File Paths
TASKS_FILE = 'tasks.txt'
STATS_FILE = 'stats.json'

# Icon Paths
ICON_PATHS = {
    'posture': 'img/posture.png',
    'eye': 'img/eye.png',
    'emoji': 'img/emoji.png'
}

# Colors
COLORS = {
    'success': '#4CAF50',
    'warning': '#FF9800', 
    'info': '#2196F3',
    'error': '#f44336',
    'primary': '#007acc'
}

# Styling
DARK_THEME = {
    'background_gradient': '''qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a1a, stop:0.5 #0f0f0f, stop:1 #1a1a1a)''',
    'widget_background': '''qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2a2a2a, stop:1 #1a1a1a)''',
    'text_color': '#ffffff',
    'border_color': '#404040'
}
