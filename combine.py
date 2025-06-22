import datetime
import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import csv
import json
import os
from scipy.spatial import distance as dist
import google.generativeai as genai
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QFontDatabase, QImage
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect, 
                             QGridLayout, QCheckBox, QScrollArea, QLineEdit, QDialog, QMenu, QMessageBox)
import sys

# Import the monitoring modules
from posture import check_posture_with_gemini
from eyedistancescreen import eye_dist
from sitting import sittingt
from emotion_model import emote

# Global variables
GEMINI_API_KEY = "AIzaSyCxImEs_JzNLqajbSLC91QsOoh6heTenBs"
client = genai.configure(api_key=GEMINI_API_KEY)

# MediaPipe setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# Eye tracking constants
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
blink_thresh = 0.21
succ_frame = 2

def calculate_EAR(eye):
    y1 = dist.euclidean(eye[1], eye[5])
    y2 = dist.euclidean(eye[2], eye[4])
    x1 = dist.euclidean(eye[0], eye[3])
    EAR = (y1 + y2) / (2.0 * x1)
    return EAR

class MonitoringThread(QThread):
    """Thread for running AI monitoring in background"""
    alert_signal = pyqtSignal(str, str)  # Signal for alerts (title, message)
    stats_update_signal = pyqtSignal(dict)  # Signal for stats updates
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        
        # Initialize CSV file
        self.csv_file = open("stats.csv", mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Timestamp", "blink_rate", "Posture", "Eye Distance", "Seated Time", "Emotion"])
        
        # Monitoring variables
        self.count_frame = 0
        self.blink_count = 0
        self.interval_start_time = time.time()
        self.interval_blink_count = 0
        self.blink_rate = 0
        self.count = 0
        
    def run(self):
        """Main monitoring loop"""
        self.running = True
        self.cap = cv2.VideoCapture(0)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            self.count += 1
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Blink detection
            results = face_mesh.process(rgb)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE_IDX]
                    right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE_IDX]
                    
                    left_EAR = calculate_EAR(left_eye)
                    right_EAR = calculate_EAR(right_eye)
                    avg_EAR = (left_EAR + right_EAR) / 2.0
                    
                    if avg_EAR < blink_thresh:
                        self.count_frame += 1
                    else:
                        if self.count_frame >= succ_frame:
                            self.blink_count += 1
                            self.interval_blink_count += 1
                        self.count_frame = 0
                
                # Calculate blink rate every 20 seconds
                elapsed = time.time() - self.interval_start_time
                if elapsed >= 20:
                    self.blink_rate = round((self.interval_blink_count / elapsed) * 60, 2)
                    self.interval_blink_count = 0
                    self.interval_start_time = time.time()
            
            # Periodic checks (every 50 seconds)
            if self.count % (int(fps * 50)) == 0:
                self.perform_checks(frame)
            
            # Update stats
            self.update_stats()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.03)
    
    def perform_checks(self, frame):
        """Perform all monitoring checks"""
        try:
            # Posture check
            posture = check_posture_with_gemini(frame)
            if "BAD" in posture:
                self.alert_signal.emit("Posture Alert", "Check your posture!")
            
            # Eye distance check
            eye_distance = eye_dist(frame)
            if eye_distance == True or eye_distance == "True":
                self.alert_signal.emit("Eye Distance Alert", "You are too close to the screen!")
            
            # Sitting time check
            sitting_time = round(sittingt(frame) / 60, 2)
            if sitting_time > 60:
                self.alert_signal.emit("Sitting Alert", "You've been sitting too long. Take a walk!")
            
            # Emotion check
            emotion = emote(frame)
            prompt = "Write one sentence to person about his positive emotion"
            response = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt, emotion])
            self.alert_signal.emit("Emotion Update", str(response))
            
        except Exception as e:
            print(f"Error in monitoring checks: {e}")
    
    def update_stats(self):
        """Update and emit current stats"""
        timestamp = datetime.datetime.now().isoformat()
        stats = {
            "blink_rate": self.blink_rate,
            "posture": "GOOD",  # Default value
            "eye_distance": 0,
            "sitting_time": 0,
            "emotion": "Neutral"
        }
        
        # Write to CSV
        self.csv_writer.writerow([timestamp, stats["blink_rate"], stats["posture"], 
                                 stats["eye_distance"], stats["sitting_time"], stats["emotion"]])
        
        # Emit stats update
        self.stats_update_signal.emit(stats)
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.csv_file:
            self.csv_file.close()

class CameraFeed:
    def __init__(self):
        self.cap = None
        self.is_running = False
        
    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_running = True
                return True
            else:
                print("Could not open camera")
                return False
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def get_frame(self):
        if self.cap and self.is_running:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
    
    def is_camera_available(self):
        return self.cap is not None and self.cap.isOpened()

class StatsManager:
    def __init__(self):
        self.stats_file = os.path.join(os.path.dirname(__file__), 'stats.json')
        self.stats = self.load_stats()
    
    def load_stats(self):
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as file:
                    stats = json.load(file)
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    if stats.get('last_updated') != today:
                        stats['tasks_completed_today'] = 0
                        stats['last_updated'] = today
                        self.save_stats(stats)
                    return stats
            else:
                return {
                    "tasks_completed_today": 0,
                    "pomodoro_time_spent": 0,
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "total_tasks_completed": 0,
                    "total_pomodoro_sessions": 0,
                    "focus_streak": 0,
                    "break_time": 0
                }
        except Exception as e:
            print(f"Error loading stats: {e}")
            return {"tasks_completed_today": 0, "pomodoro_time_spent": 0, "last_updated": datetime.datetime.now().strftime("%Y-%m-%d")}
    
    def save_stats(self, stats=None):
        try:
            if stats is None:
                stats = self.stats
            with open(self.stats_file, 'w', encoding='utf-8') as file:
                json.dump(stats, file, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def increment_tasks_completed(self):
        self.stats['tasks_completed_today'] += 1
        self.stats['total_tasks_completed'] = self.stats.get('total_tasks_completed', 0) + 1
        self.save_stats()
    
    def add_pomodoro_time(self, minutes):
        self.stats['pomodoro_time_spent'] += minutes
        self.save_stats()
    
    def complete_pomodoro_session(self):
        self.stats['total_pomodoro_sessions'] = self.stats.get('total_pomodoro_sessions', 0) + 1
        self.stats['focus_streak'] = self.stats.get('focus_streak', 0) + 1
        self.save_stats()
    
    def get_stats_summary(self):
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

class StatsOverlay(QWidget):
    def __init__(self, parent=None, stats_manager=None):
        super().__init__(parent)
        self.stats_manager = stats_manager or StatsManager()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        content_widget = QFrame(self)
        content_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(40, 40, 40, 0.98), stop:1 rgba(20, 20, 20, 0.98));
            color: white;
            border-radius: 20px;
            border: 2px solid rgba(100, 150, 255, 0.3);
        """)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        title = QLabel("Overall Statistics")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        stats_layout.setColumnStretch(0, 1)
        stats_layout.setColumnStretch(1, 2)

        stats = self.stats_manager.get_stats_summary()

        row = 0
        for name, value in stats.items():
            name_label = QLabel(name)
            name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet("""
                background: rgba(100, 150, 255, 0.15);
                border: 1px solid rgba(100, 150, 255, 0.3);
                border-radius: 8px;
                padding: 6px 10px;
                margin: 2px;
            """)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 11))
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            value_label.setStyleSheet("""
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 6px 10px;
                margin: 2px;
            """)
            
            stats_layout.addWidget(name_label, row, 0)
            stats_layout.addWidget(value_label, row, 1)
            row += 1

        layout.addLayout(stats_layout)
        
        close_button = QPushButton("Close")
        close_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        close_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 150, 255, 0.8), stop:1 rgba(80, 120, 200, 0.8));
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 170, 255, 0.9), stop:1 rgba(100, 140, 220, 0.9));
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(80, 120, 200, 0.9), stop:1 rgba(60, 100, 180, 0.9));
            }
        """)
        close_button.clicked.connect(self.hide_overlay)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def showEvent(self, event):
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def hide_overlay(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)

class PomodoroTimer(QFrame):
    def __init__(self, stats_manager=None):
        super().__init__()
        self.stats_manager = stats_manager or StatsManager()
        self.time_left = 25 * 60  # 25 minutes in seconds
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 60, 80, 0.9), stop:1 rgba(40, 40, 60, 0.9));
                border-radius: 15px;
                border: 2px solid rgba(100, 150, 255, 0.3);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("Pomodoro Timer")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #64A0FF;")
        layout.addWidget(self.time_label)
        
        button_layout = QHBoxLayout()
        
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 150, 255, 0.8), stop:1 rgba(80, 120, 200, 0.8));
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 170, 255, 0.9), stop:1 rgba(100, 140, 220, 0.9));
            }
        """)
        self.start_stop_button.clicked.connect(self.start_stop)
        button_layout.addWidget(self.start_stop_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 100, 100, 0.8), stop:1 rgba(200, 80, 80, 0.8));
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 120, 120, 0.9), stop:1 rgba(220, 100, 100, 0.9));
            }
        """)
        self.reset_button.clicked.connect(self.reset)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
    
    def update_time(self):
        if self.time_left > 0:
            self.time_left -= 1
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        else:
            self.timer.stop()
            self.is_running = False
            self.start_stop_button.setText("Start")
            self.stats_manager.complete_pomodoro_session()
            self.stats_manager.add_pomodoro_time(25)
            QMessageBox.information(self, "Pomodoro Complete", "Great job! Take a 5-minute break.")
    
    def start_stop(self):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.start_stop_button.setText("Start")
        else:
            self.timer.start(1000)
            self.is_running = True
            self.start_stop_button.setText("Stop")
    
    def reset(self):
        self.timer.stop()
        self.is_running = False
        self.time_left = 25 * 60
        self.time_label.setText("25:00")
        self.start_stop_button.setText("Start")

class TasksWidget(QFrame):
    def __init__(self, stats_manager=None):
        super().__init__()
        self.stats_manager = stats_manager or StatsManager()
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.txt')
        self.tasks = []
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 60, 80, 0.9), stop:1 rgba(40, 40, 60, 0.9));
                border-radius: 15px;
                border: 2px solid rgba(100, 150, 255, 0.3);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("Tasks")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.tasks_widget)
        layout.addWidget(self.scroll_area)
        
        add_button = QPushButton("+ Add Task")
        add_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 150, 255, 0.8), stop:1 rgba(80, 120, 200, 0.8));
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 170, 255, 0.9), stop:1 rgba(100, 140, 220, 0.9));
            }
        """)
        add_button.clicked.connect(self.add_new_task)
        layout.addWidget(add_button)
    
    def load_tasks(self):
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            completed = line.startswith("[x] ")
                            text = line[4:] if completed else line
                            self.add_task_to_widget(text, completed)
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def save_tasks(self):
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as file:
                for task in self.tasks:
                    if task['completed']:
                        file.write(f"[x] {task['text']}\n")
                    else:
                        file.write(f"{task['text']}\n")
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task_to_widget(self, text, completed=False):
        task_frame = QFrame()
        task_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        task_layout = QHBoxLayout(task_frame)
        task_layout.setContentsMargins(10, 5, 10, 5)
        
        checkbox = QCheckBox()
        checkbox.setChecked(completed)
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background: rgba(100, 150, 255, 0.8);
                border: 2px solid rgba(100, 150, 255, 1);
                border-radius: 4px;
            }
        """)
        checkbox.stateChanged.connect(lambda state, t=text: self.on_task_checked(t, state))
        task_layout.addWidget(checkbox)
        
        task_label = QLabel(text)
        task_label.setFont(QFont("Segoe UI", 11))
        task_label.setStyleSheet("color: white;")
        if completed:
            task_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); text-decoration: line-through;")
        task_layout.addWidget(task_label)
        
        task_layout.addStretch()
        
        delete_button = QPushButton("×")
        delete_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        delete_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 100, 100, 0.8);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 2px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 120, 120, 0.9);
            }
        """)
        delete_button.clicked.connect(lambda: self.remove_task(text))
        task_layout.addWidget(delete_button)
        
        self.tasks_layout.addWidget(task_frame)
        self.tasks.append({'text': text, 'completed': completed, 'widget': task_frame})
    
    def add_task(self, text, completed=False):
        self.add_task_to_widget(text, completed)
        self.save_tasks()
    
    def add_new_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_text = dialog.get_task_text()
            if task_text:
                self.add_task(task_text)
    
    def on_task_checked(self, task_text, state):
        for task in self.tasks:
            if task['text'] == task_text:
                task['completed'] = (state == Qt.CheckState.Checked)
                if task['completed']:
                    self.stats_manager.increment_tasks_completed()
                break
        self.save_tasks()
    
    def remove_task(self, task_text):
        for i, task in enumerate(self.tasks):
            if task['text'] == task_text:
                task['widget'].deleteLater()
                self.tasks.pop(i)
                break
        self.save_tasks()

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_text = ""
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Add New Task")
        self.setFixedSize(400, 150)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 60, 80, 0.95), stop:1 rgba(40, 40, 60, 0.95));
                border-radius: 15px;
                border: 2px solid rgba(100, 150, 255, 0.3);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("Enter new task:")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        self.task_input = QLineEdit()
        self.task_input.setFont(QFont("Segoe UI", 12))
        self.task_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(100, 150, 255, 0.5);
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(100, 150, 255, 0.8);
            }
        """)
        self.task_input.returnPressed.connect(self.accept)
        layout.addWidget(self.task_input)
        
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Segoe UI", 12))
        cancel_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        add_button = QPushButton("Add")
        add_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 150, 255, 0.8), stop:1 rgba(80, 120, 200, 0.8));
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 170, 255, 0.9), stop:1 rgba(100, 140, 220, 0.9));
            }
        """)
        add_button.clicked.connect(self.accept)
        button_layout.addWidget(add_button)
        
        layout.addLayout(button_layout)
    
    def get_task_text(self):
        return self.task_input.text().strip()

class CombinedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stats_manager = StatsManager()
        self.camera_feed = CameraFeed()
        self.monitoring_thread = MonitoringThread()
        self.stats_overlay = None
        
        self.initUI()
        self.setup_monitoring()
    
    def initUI(self):
        self.setWindowTitle("Eye-AI - Combined Application")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 30, 50, 1), stop:1 rgba(20, 20, 40, 1));
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left panel - Camera and monitoring info
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)
        
        # Camera feed
        self.camera_label = QLabel("Camera Feed")
        self.camera_label.setFixedSize(400, 300)
        self.camera_label.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid rgba(100, 150, 255, 0.3);
                border-radius: 15px;
                color: white;
                font-size: 16px;
            }
        """)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.camera_label)
        
        # Monitoring status
        self.status_label = QLabel("AI Monitoring: Starting...")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #64A0FF; background: rgba(100, 150, 255, 0.1); padding: 10px; border-radius: 8px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.status_label)
        
        main_layout.addLayout(left_panel)
        
        # Right panel - Tools
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)
        
        # Pomodoro Timer
        self.pomodoro_timer = PomodoroTimer(self.stats_manager)
        right_panel.addWidget(self.pomodoro_timer)
        
        # Tasks Widget
        self.tasks_widget = TasksWidget(self.stats_manager)
        right_panel.addWidget(self.tasks_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.stats_button = QPushButton("📊 Statistics")
        self.stats_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.stats_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 150, 255, 0.8), stop:1 rgba(80, 120, 200, 0.8));
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 170, 255, 0.9), stop:1 rgba(100, 140, 220, 0.9));
            }
        """)
        self.stats_button.clicked.connect(self.show_stats_overlay)
        button_layout.addWidget(self.stats_button)
        
        self.stop_button = QPushButton("🛑 Stop Monitoring")
        self.stop_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.stop_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 100, 100, 0.8), stop:1 rgba(200, 80, 80, 0.8));
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 120, 120, 0.9), stop:1 rgba(220, 100, 100, 0.9));
            }
        """)
        self.stop_button.clicked.connect(self.stop_monitoring)
        button_layout.addWidget(self.stop_button)
        
        right_panel.addLayout(button_layout)
        main_layout.addLayout(right_panel)
        
        # Camera update timer
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera_feed)
        self.camera_timer.start(50)  # Update every 50ms
    
    def setup_monitoring(self):
        """Setup the monitoring thread and connect signals"""
        self.monitoring_thread.alert_signal.connect(self.show_alert)
        self.monitoring_thread.stats_update_signal.connect(self.update_monitoring_stats)
        self.monitoring_thread.start()
        self.status_label.setText("AI Monitoring: Active")
    
    def show_alert(self, title, message):
        """Show monitoring alerts"""
        QMessageBox.information(self, title, message)
    
    def update_monitoring_stats(self, stats):
        """Update monitoring statistics display"""
        # This can be used to update real-time stats in the UI
        pass
    
    def update_camera_feed(self):
        """Update the camera feed display"""
        if not self.camera_feed.is_running:
            if self.camera_feed.start_camera():
                self.status_label.setText("AI Monitoring: Active")
            else:
                self.status_label.setText("AI Monitoring: Camera Error")
                return
        
        frame = self.camera_feed.get_frame()
        if frame is not None:
            # Convert OpenCV frame to Qt format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Scale to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)
    
    def show_stats_overlay(self):
        """Show the statistics overlay"""
        if self.stats_overlay is None:
            self.stats_overlay = StatsOverlay(self, self.stats_manager)
        
        # Position overlay over the main window
        overlay_geometry = self.geometry()
        self.stats_overlay.setGeometry(overlay_geometry)
        self.stats_overlay.show()
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring_thread.stop_monitoring()
        self.camera_feed.stop_camera()
        self.status_label.setText("AI Monitoring: Stopped")
        self.stop_button.setText("✅ Monitoring Stopped")
        self.stop_button.setEnabled(False)
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.monitoring_thread.stop_monitoring()
        self.camera_feed.stop_camera()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    window = CombinedWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
