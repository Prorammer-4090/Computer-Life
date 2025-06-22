
# import cv2
# import mediapipe as mp
# from scipy.spatial import distance as dist
# import time

# # EAR calculation for 6 eye points
# def calculate_EAR(eye):
#     y1 = dist.euclidean(eye[1], eye[5])
#     y2 = dist.euclidean(eye[2], eye[4])
#     x1 = dist.euclidean(eye[0], eye[3])
#     EAR = (y1 + y2) / (2.0 * x1)
#     return EAR

# # Indices for left and right eye landmarks (MediaPipe FaceMesh)
# LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
# RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

# blink_thresh = 0.21
# succ_frame = 2
# count_frame = 0
# blink_count = 0

# # For blink rate calculation
# interval = 20  # seconds
# interval_start_time = time.time()
# interval_blink_count = 0
# blink_rate = 0  # blinks per minute

# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
# mp_drawing = mp.solutions.drawing_utils

# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#     frame = cv2.flip(frame, 1)
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb)

#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:
#             h, w, _ = frame.shape
#             # Get eye coordinates
#             left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE_IDX]
#             right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE_IDX]

#             # Draw eyes
#             for pt in left_eye:
#                 cv2.circle(frame, pt, 2, (0,255,0), -1)
#             for pt in right_eye:
#                 cv2.circle(frame, pt, 2, (0,255,0), -1)

#             left_EAR = calculate_EAR(left_eye)
#             right_EAR = calculate_EAR(right_eye)
#             avg_EAR = (left_EAR + right_EAR) / 2.0

#             if avg_EAR < blink_thresh:
#                 count_frame += 1
#             else:
#                 if count_frame >= succ_frame:
#                     blink_count += 1
#                     interval_blink_count += 1
#                     cv2.putText(frame, 'Blink Detected', (30, 60),
#                                 cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 2)
#                 count_frame = 0

#     # Calculate blink rate every 20 seconds
#     elapsed = time.time() - interval_start_time
#     if elapsed >= interval:
#         blink_rate = (interval_blink_count / elapsed) * 60  # blinks per minute
#         interval_blink_count = 0
#         interval_start_time = time.time()

#     cv2.putText(frame, f'Blink Rate: {blink_rate:.2f} blinks/min', (30, 30),
#                 cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

#     cv2.imshow("Blink Detection", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()