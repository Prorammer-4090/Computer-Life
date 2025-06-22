"""
Tasks Widget
A widget for managing daily tasks with completion tracking.
"""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QWidget, QCheckBox, QDialog)

from ..core.stats_manager import StatsManager
from .task_dialog import AddTaskDialog


class TasksWidget(QFrame):
    """Widget for displaying and managing daily tasks."""
    
    def __init__(self, stats_manager=None):
        super().__init__()
        self.tasks = []
        self.stats_manager = stats_manager or StatsManager()
        self.tasks_file = os.path.join(os.path.dirname(__file__), '..', '..', 'tasks.txt')
        
        self._setup_ui()
        self._apply_styles()
        self.load_tasks()
    
    def _setup_ui(self):
        """Create the user interface elements."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Title
        self._create_title(main_layout)
        
        # Scroll area for tasks
        self._create_scroll_area(main_layout)
        
        # Add task button
        self._create_add_button(main_layout)
    
    def _create_title(self, parent_layout):
        """Create the title label."""
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
        parent_layout.addWidget(title)
    
    def _create_scroll_area(self, parent_layout):
        """Create the scrollable area for tasks."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(120)
        self.scroll_area.setMaximumHeight(140)
        
        # Widget to contain tasks
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(2, 2, 2, 2)
        self.tasks_layout.setSpacing(3)
        
        # Add stretch to push tasks to top
        self.tasks_layout.addStretch()
        
        self.scroll_area.setWidget(self.tasks_container)
        parent_layout.addWidget(self.scroll_area)
    
    def _create_add_button(self, parent_layout):
        """Create the add task button."""
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(28, 28)
        self.plus_button.clicked.connect(self.add_new_task)
        
        # Center the plus button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.plus_button)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply styling to the widget and its components."""
        self.setStyleSheet('''
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 2px solid #404040;
                border-radius: 12px;
                max-width: 220px;
            }
        ''')
        
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
    
    def load_tasks(self):
        """Load tasks from the text file."""
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
                self._create_default_tasks()
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def _create_default_tasks(self):
        """Create default tasks if file doesn't exist."""
        default_tasks = [
            ("Project work", False),
            ("Code review", False),
            ("Meeting", False)
        ]
        for text, completed in default_tasks:
            self.add_task_to_widget(text, completed)
        self.save_tasks()
    
    def save_tasks(self):
        """Save all tasks to the text file."""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as file:
                for text, checkbox, _ in self.tasks:
                    completed = checkbox.isChecked()
                    file.write(f"{text}|{completed}\n")
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task_to_widget(self, text, completed=False):
        """Add a task to the widget (internal method)."""
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
        
        # Connect checkbox state change to completion handler
        checkbox.stateChanged.connect(lambda state, task_text=text: self.on_task_checked(task_text, state))
        
        task_layout.addWidget(checkbox)
        
        # Insert before the stretch at the end
        insert_index = self.tasks_layout.count() - 1
        self.tasks_layout.insertWidget(insert_index, task_container)
        self.tasks.append((text, checkbox, task_container))
    
    def add_task(self, text, completed=False):
        """Add a new task and save to file."""
        self.add_task_to_widget(text, completed)
        self.save_tasks()
    
    def add_new_task(self):
        """Open dialog to add a new task."""
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_text = dialog.get_task_text()
            if task_text:
                self.add_task(task_text, False)
    
    def on_task_checked(self, task_text, state):
        """Handle task completion - remove from widget and save to file."""
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
        """Remove a task completely from both widget and file."""
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
