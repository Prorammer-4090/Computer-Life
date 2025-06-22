"""
Statistics Management Module
Handles all statistics tracking and persistence for the application.
"""
import os
import json
from datetime import datetime


class StatsManager:
    """Manages application statistics and persistence."""
    
    def __init__(self, stats_file=None):
        """Initialize the StatsManager with optional custom stats file path."""
        if stats_file is None:
            stats_file = os.path.join(os.path.dirname(__file__), '..', '..', 'stats.json')
        self.stats_file = stats_file
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
                return self._create_default_stats()
        except Exception as e:
            print(f"Error loading stats: {e}")
            return self._create_default_stats()
    
    def _create_default_stats(self):
        """Create default statistics structure."""
        return {
            "tasks_completed_today": 0,
            "pomodoro_time_spent": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_tasks_completed": 0,
            "total_pomodoro_sessions": 0,
            "focus_streak": 0,
            "break_time": 0
        }
    
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
