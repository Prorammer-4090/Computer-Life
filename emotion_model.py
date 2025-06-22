import cv2
from deepface import DeepFace

def emote(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = DeepFace.analyze(
        rgb_frame,
        actions=['emotion'],
        enforce_detection=False,
        detector_backend='opencv'
    )
    # DeepFace returns a list of dicts if more than one face or with some versions
    if isinstance(result, list):
        emotion = result[0]['dominant_emotion']
    else:
        emotion = result['dominant_emotion']
    return emotion


