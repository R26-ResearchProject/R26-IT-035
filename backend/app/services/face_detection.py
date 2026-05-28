import cv2
import mediapipe as mp

# -------------------------
# INITIALIZE MEDIAPIPE
# -------------------------

mp_face = mp.solutions.face_mesh

face_mesh = mp_face.FaceMesh(
    static_image_mode=True
)

# -------------------------
# FACE DETECTION FUNCTION
# -------------------------

def detect_face_landmarks(image):

    # Convert BGR → RGB
    img_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # Process image using MediaPipe
    results = face_mesh.process(img_rgb)

    # No face detected
    if not results.multi_face_landmarks:
        return None

    # Extract first face landmarks
    landmarks = results.multi_face_landmarks[0].landmark

    # Convert landmarks into x,y points
    points = [
        (lm.x, lm.y)
        for lm in landmarks
    ]

    return points