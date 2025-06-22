# BlurNout 

**A Real-Time Health Monitoring Application for Computer Users**

BlurNout is an intelligent desktop application that monitors your health and productivity while you work on your computer. Using computer vision and AI, it tracks your posture, eye health, emotions, and work habits to provide real-time feedback and suggestions for maintaining better health during long computer sessions.

##  Features

###  **Real-Time Health Monitoring**
- **Blink Rate Detection**: Monitors your blinking frequency to prevent dry eyes
- **Eye Distance Tracking**: Ensures you maintain proper distance from your screen (40cm+)
- **Posture Analysis**: Uses Google Gemini AI to analyze and alert about poor posture
- **Sitting Time Tracking**: Reminds you to take breaks after extended sitting periods
- **Emotion Recognition**: Detects your emotional state and provides motivational feedback

###  **Productivity Tools**
- **Pomodoro Timer**: Built-in focus timer with session tracking
- **Task Management**: Create, complete, and track daily tasks
- **Statistics Dashboard**: Comprehensive analytics with charts and progress tracking
- **Focus Streak Monitoring**: Track your productivity streaks

### **Modern Interface**
- **Dark Theme UI**: Easy on the eyes for long usage sessions
- **Real-Time Camera Feed**: Live video feed with health indicator overlays
- **Animated Notifications**: Non-intrusive health alerts with 30-second throttling
- **Statistics Overlay**: Beautiful charts and progress visualizations

##  Dependencies

### **Core Dependencies**

#### **GUI Framework**
- **PyQt6** - Modern cross-platform GUI toolkit
  - `PyQt6.QtWidgets` - UI components
  - `PyQt6.QtCore` - Core functionality and animations
  - `PyQt6.QtGui` - Graphics and styling

#### **Computer Vision & AI**
- **OpenCV (`cv2`)** - Computer vision and camera handling
- **MediaPipe (`mediapipe`)** - Face mesh detection and pose estimation
- **Google Generative AI (`google.generativeai`)** - Gemini AI for posture analysis
- **DeepFace** - Emotion recognition and facial analysis
- **CVZone** - Computer vision utilities
  - `cvzone.FaceMeshModule` - Face mesh detection

#### **Data Processing & Analysis**
- **NumPy (`numpy`)** - Numerical computations
- **SciPy (`scipy`)** - Scientific computing
  - `scipy.spatial.distance` - Distance calculations for eye tracking
- **Matplotlib** - Data visualization and charts
  - `matplotlib.pyplot` - Plotting functionality
  - `matplotlib.dates` - Date formatting for charts
  - `matplotlib.backends.backend_qt5agg` - Qt integration

#### **Image Processing**
- **Pillow (`PIL`)** - Image processing and manipulation

#### **System & Utilities**
- **sys** - System-specific parameters (built-in)
- **os** - Operating system interface (built-in)
- **json** - JSON data handling (built-in)
- **time** - Time-related functions (built-in)
- **datetime** - Date and time manipulation (built-in)

## 📦 Installation

### **Prerequisites**
- Python 3.8 or higher
- Webcam/Camera access
- Windows/macOS/Linux

### **Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd BlurNout
```

### **Step 2: Install Dependencies**
```bash
pip install PyQt6
pip install opencv-python
pip install mediapipe
pip install google-generativeai
pip install deepface
pip install cvzone
pip install numpy
pip install scipy
pip install matplotlib
pip install Pillow
```

**Or install all at once:**
```bash
pip install PyQt6 opencv-python mediapipe google-generativeai deepface cvzone numpy scipy matplotlib Pillow
```

### **Step 3: API Configuration**
1. Get a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Replace the API key in `application.py` and `posture.py`:
```python
GEMINI_API_KEY = "your-api-key-here"
```

##  Usage

### **Running the Application**
```bash
python application.py
```

### **Main Interface**
- **Camera Feed**: Shows live video with health indicators
- **Pomodoro Timer**: Start/pause/reset your focus sessions
- **Task List**: Add and complete daily tasks
- **Menu Button**: Access statistics and application settings

### **Health Monitoring**
The application automatically monitors:
- **Blink Rate**: Alerts if below 6 blinks per minute
- **Eye Distance**: Warns if closer than 40cm to screen
- **Posture**: AI-powered posture analysis every 5 minutes
- **Sitting Time**: Break reminders after 1 hour of sitting
- **Emotions**: Motivational feedback based on detected emotions

### **Notification System**
- Smart 30-second throttling prevents notification spam
- Health alerts appear as styled popup messages
- Different notification types for various health metrics

##  Project Structure

```
BlurNout/
├── application.py          # Main application entry point
├── emotion_model.py        # Emotion detection using DeepFace
├── posture.py             # Posture analysis with Gemini AI
├── eyedistancescreen.py   # Eye distance calculation
├── sitting.py             # Sitting time and pose tracking
├── stats.json             # Statistics data storage
├── tasks.txt              # Task list storage
├── img/                   # UI icons and images
│   ├── posture.png
│   ├── eye.png
│   ├── emoji.png
│   └── ...
└── README.md              # This file
```

## 🎯 Key Features Explained

### **AI-Powered Posture Detection**
Uses Google's Gemini 2.0 Flash model to analyze camera feed and detect poor posture in real-time.

### **Comprehensive Eye Health**
- Tracks blink rate using MediaPipe face mesh detection
- Calculates eye-to-screen distance using facial landmarks
- Provides alerts for dry eye prevention

### **Smart Productivity Tracking**
- Pomodoro timer with session completion tracking
- Task management with automatic completion statistics
- Focus streak calculations and progress visualization

### **Emotion-Aware Feedback**
- Detects emotions using DeepFace neural networks
- Provides contextual motivational messages
- Tracks emotional patterns over time

## 🔧 Configuration

### **Notification Timing**
- Blink rate: Every 2 minutes minimum
- Eye distance: Immediate alerts
- Posture: 15-minute bad posture threshold
- Sitting time: 1-hour sitting threshold
- Emotions: 10-minute feedback intervals

### **Health Thresholds**
- Minimum blink rate: 6 blinks per minute
- Safe eye distance: 40cm or more
- Sitting time limit: 60 minutes
- Posture check interval: 5 minutes

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Support

If you encounter any issues or have questions:
1. Check the common issues section
2. Create an issue on GitHub
3. Ensure all dependencies are correctly installed
4. Verify camera permissions are granted

##  Acknowledgments

- **Google Gemini AI** for advanced posture analysis
- **MediaPipe** for robust face and pose detection
- **DeepFace** for emotion recognition capabilities
- **PyQt6** for the modern user interface framework

---

**Stay healthy while you code! 💻✨**
