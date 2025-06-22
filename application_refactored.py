"""
Emotion Detector Pro Application
Main application entry point with clean object-oriented architecture.
"""
import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


class EmotionDetectorApp:
    """Main application class."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
    
    def initialize(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        return self
    
    def run(self):
        """Run the application."""
        if not self.app or not self.main_window:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        self.main_window.show()
        return self.app.exec()


def main():
    """Application entry point."""
    app = EmotionDetectorApp()
    app.initialize()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
