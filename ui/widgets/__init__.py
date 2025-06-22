"""
UI Widgets module
Contains all the custom widgets used in the application.
"""

from .stats_overlay import StatsOverlay
from .pomodoro_timer import PomodoroTimer
from .tasks_widget import TasksWidget
from .task_dialog import AddTaskDialog
from .camera_feed import CameraFeedWidget

__all__ = [
    'StatsOverlay',
    'PomodoroTimer', 
    'TasksWidget',
    'AddTaskDialog',
    'CameraFeedWidget'
]
