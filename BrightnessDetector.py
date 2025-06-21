import cv2
import numpy as np

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Calculate average brightness
avg_brightness = np.mean(gray)

# Categorize brightness
if avg_brightness < 50:
    room = "Dark"
elif avg_brightness < 100:
    room = "Dim"
else:
    room = "Bright"

print(room)