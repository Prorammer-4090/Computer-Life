import cv2
import mediapipe as mp
import numpy as np
import time
from scipy.spatial import distance as dist
import google.generativeai as genai
from PIL import Image

# Global variables
GEMINI_API_KEY = "AIzaSyCxImEs_JzNLqajbSLC91QsOoh6heTenBs"
client = genai.configure(api_key=GEMINI_API_KEY)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

from posture import check_posture_with_gemini
from eyedistancescreen import eye_dist
from sitting import sittingt
def calculate_EAR(eye):
    y1 = dist.euclidean(eye[1], eye[5])
    y2 = dist.euclidean(eye[2], eye[4])
    x1 = dist.euclidean(eye[0], eye[3])
    EAR = (y1 + y2) / (2.0 * x1)
    return EAR


# Indices for left and right eye landmarks (MediaPipe FaceMesh)
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

blink_thresh = 0.21
succ_frame = 2
count_frame = 0
blink_count = 0

# For blink rate calculation
interval_start_time = time.time()
interval_blink_count = 0
blink_rate = 0  # blinks per minute

# Global variables for sitting tracking
sitting = False
start_time = 0
break_start_time = None

cap = cv2.VideoCapture(0)

# Get framerate information
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Camera framerate: {fps} FPS")

count=0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    count+=1
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # FOR THE BLINKING PART
    results = face_mesh.process(rgb)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE_IDX]
            right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE_IDX]
            for pt in left_eye:
                cv2.circle(frame, pt, 2, (0,255,0), -1)
            for pt in right_eye:
                cv2.circle(frame, pt, 2, (0,255,0), -1)
            left_EAR = calculate_EAR(left_eye)
            right_EAR = calculate_EAR(right_eye)
            avg_EAR = (left_EAR + right_EAR) / 2.0
            if avg_EAR < blink_thresh:
                count_frame += 1
            else:
                if count_frame >= succ_frame:
                    blink_count += 1
                    interval_blink_count += 1
                count_frame = 0

        elapsed = time.time() - interval_start_time
        if elapsed >= 20:  #seconds
            blink_rate = (interval_blink_count / elapsed) * 60  # blinks per minute
            interval_blink_count = 0
            interval_start_time = time.time()

            print("Blink rate", blink_rate)

    # FOR THE POSTURE PART
    pose_results = pose.process(rgb)

    if count % 30 == 0:  
        posture = check_posture_with_gemini(frame)
        print(f"Posture: {posture}")

    if count % 120 == 0: 
        eye_distance = eye_dist(frame)
        print(f"Eye Distance: {eye_distance} cm")
    
    if count % 30 == 0:  # Show sitting every 50 frames
        sitting_time = sittingt(frame) 
        print(f"Sitting Time: {sitting_time} seconds")

    cv2.imshow('Eye-AI', frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()