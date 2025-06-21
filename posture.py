import cv2
from PIL import Image
from google import genai

# Initialize the Gemini client
GEMINI_API_KEY = "AIzaSyCxImEs_JzNLqajbSLC91QsOoh6heTenBs"
client = genai.Client(api_key=GEMINI_API_KEY)

def check_posture_with_gemini(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)
    prompt = (
        "Is the person in this image standing or sitting with good posture (erect/tall) or bad posture (slouching)? "
        "Reply with only GOOD or BAD. GOOD means standing or sitting erect/tall. BAD means slouching."
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, pil_img]
        )
        answer = response.text.strip().upper()
        if "BAD" in answer:
            return "BAD"
        return "GOOD"
    except Exception as e:
        print("Error contacting Gemini API:", e)
        return "Err"
    

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#     frame = cv2.flip(frame, 1)
#     h, w, _ = frame.shape
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     posture = check_posture_with_gemini(frame)
     

#     if cv2.waitKey(10) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()