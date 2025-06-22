import cv2
import mediapipe as mp
import time
import numpy as np


mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

BREAK_DURATION = 120  # seconds (2 minutes)
sittingb = False
start_time = 0
current_session = 0
break_start_time = None
def sittingt(frame):
    global sittingb, start_time, current_session, break_start_time
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        # Person detected (any part of body)
        if not sittingb:
            # Person just returned
            if break_start_time is not None:
                break_length = time.time() - break_start_time
                if break_length >= BREAK_DURATION:
                    # Break long enough, reset stopwatch
                    start_time = time.time()
                    current_session = 0
                else:
                    # Break too short, continue stopwatch
                    # Don't adjust start_time, just continue from where we left off
                    pass
            else:
                # First time starting
                start_time = time.time()
                current_session = 0
            # person detected, start or resume stopwatch
            sittingb = True
            break_start_time = None
        # Calculate current session time
        current_session = time.time() - start_time
    else:
        # Person not detected (no body part visible)
        if sittingb:
            # person just left
            sittingb = False
            break_start_time = time.time()
        # Keep current_session as is when person is away

    return current_session





































# import cv2
# import time
# import mediapipe as mp

# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# # Load the default webcam
# cap = cv2.VideoCapture(0)

# BREAK_DURATION = 120  # seconds (2 minutes)

# sitting = False
# start_time = 0
# current_session = 0
# break_start_time = None

# print("Press 'q' to quit.")

# # while True:
# #     ret, frame = cap.read()
# #     if not ret:
# #         break

# #     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #     results = pose.process(rgb)

# #     if results.pose_landmarks:
# #         # Person detected (any part of body)
# #         if not sitting:
# #             # Only reset if break was long enough
# #             if break_start_time is not None:
# #                 break_length = time.time() - break_start_time
# #                 if break_length >= BREAK_DURATION:
# #                     print("Break was long enough. Stopwatch reset.")
# #                     start_time = time.time()
# #                 else:
# #                     print(f"Break too short ({break_length:.1f} sec). Stopwatch continues.")
# #                     # Adjust start_time so session continues
# #                     start_time = start_time + break_length
# #             else:
# #                 start_time = time.time()
# #             print("Person detected. Stopwatch started or resumed.")
# #             sitting = True
# #             break_start_time = None
# #         # Calculate current session time
# #         current_session = time.time() - start_time
# #     else:
# #         # Person not detected (no body part visible)
# #         if sitting:
# #             elapsed = time.time() - start_time
# #             print(f"Person left. Sitting time this session: {elapsed:.2f} seconds.")
# #             sitting = False
# #             break_start_time = time.time()
# #         current_session = time.time() - start_time if break_start_time is not None else 0

# #     # Show stopwatch time for the current session on the screen
# #     cv2.putText(frame, f"Sitting Time (this session): {current_session:.1f} sec", (10, 30),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

# #     cv2.imshow('Desk Monitor', frame)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()

