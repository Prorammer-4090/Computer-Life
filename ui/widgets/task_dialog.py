"""
Task Dialog
Dialog for adding new tasks to the task list.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton)


class AddTaskDialog(QDialog):
    """Dialog for adding new tasks."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_dialog()
        self._create_ui()
        self._apply_styles()
        self._setup_connections()
    
    def _setup_dialog(self):
        """Configure dialog properties."""
        self.setWindowTitle("Add New Task")
        self.setFixedSize(300, 120)
    
    def _create_ui(self):
        """Create the user interface elements."""
        layout = QVBoxLayout()
        
        # Task input field
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task description...")
        layout.addWidget(self.task_input)
        
        # Buttons
        self._create_buttons(layout)
        
        self.setLayout(layout)
    
    def _create_buttons(self, parent_layout):
        """Create dialog buttons."""
        button_layout = QHBoxLayout()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        # Add button
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_button)
        
        parent_layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply styling to the dialog and its components."""
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
        
        # Special styling for cancel button
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
    
    def _setup_connections(self):
        """Setup signal connections."""
        # Focus on input field and connect Enter key
        self.task_input.setFocus()
        self.task_input.returnPressed.connect(self.accept)
    
    def get_task_text(self):
        """Get the entered task text."""
        return self.task_input.text().strip()
