import os
import cv2
import numpy as np
import mediapipe as mp
from tqdm import tqdm

# -------------------------
# CONFIG
# -------------------------
DATASET_PATH = "data/raw/UTKFace"
MAX_SAMPLES = 8000

# -------------------------
# MediaPipe Setup
# -------------------------
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(static_image_mode=True)

# -------------------------
# Helper Functions
# -------------------------
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def compute_angle(a, b, c):
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

# -------------------------
# Feature Extraction
# -------------------------
def extract_features(image):

    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(img_rgb)

    if not results.multi_face_landmarks:
        return None

    landmarks = results.multi_face_landmarks[0].landmark
    points = [(lm.x, lm.y) for lm in landmarks]

    try:
        # Geometry
        face_width = distance(points[234], points[454])
        face_height = distance(points[10], points[152])

        jaw_width = distance(points[58], points[288])
        forehead_width = distance(points[103], points[332])

        left_eye = distance(points[33], points[133])
        right_eye = distance(points[362], points[263])
        eye_size = (left_eye + right_eye) / 2

        eye_spacing = distance(points[133], points[362])

        nose_length = distance(points[168], points[1])
        mouth_width = distance(points[61], points[291])

        # Ratios
        face_ratio = face_height / (face_width + 1e-6)
        jaw_ratio = jaw_width / (face_width + 1e-6)
        forehead_ratio = forehead_width / (face_width + 1e-6)
        eye_ratio = eye_size / (face_width + 1e-6)
        eye_spacing_ratio = eye_spacing / (face_width + 1e-6)
        nose_ratio = nose_length / (face_height + 1e-6)
        mouth_ratio = mouth_width / (face_width + 1e-6)

        # Angles
        jaw_angle_left = compute_angle(points[234], points[58], points[152])
        jaw_angle_right = compute_angle(points[454], points[288], points[152])

        # Texture
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size

        # Color
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)

        mean_L = np.mean(L)
        mean_A = np.mean(A)
        mean_B = np.mean(B)

        BGR = cv2.split(image)
        redness = np.mean(BGR[2] - BGR[1])

        color_std = np.std(L)

        # Symmetry
        symmetry = abs(
            distance(points[234], points[152]) -
            distance(points[454], points[152])
        )

    except:
        return None

    return [
        face_ratio, jaw_ratio, forehead_ratio,
        eye_ratio, eye_spacing_ratio, nose_ratio,
        mouth_ratio, jaw_angle_left, jaw_angle_right,
        laplacian_var, edge_density,
        mean_L, mean_A, mean_B,
        redness, color_std, symmetry
    ]

# -------------------------
# Main Script
# -------------------------
def main():

    features = []
    failed = 0

    print("Starting feature extraction...\n")

    files = os.listdir(DATASET_PATH)

    for file in tqdm(files):

        if len(features) >= MAX_SAMPLES:
            print("\nReached max samples:", MAX_SAMPLES)
            break

        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img_path = os.path.join(DATASET_PATH, file)
        img = cv2.imread(img_path)

        if img is None:
            failed += 1
            continue

        feat = extract_features(img)

        if feat is not None:
            features.append(feat)
        else:
            failed += 1

    # Convert to NumPy
    X = np.array(features, dtype=np.float32)

    # Save
    os.makedirs("data/processed", exist_ok=True)
    np.save("data/processed/X.npy", X)

    print("\nFeature extraction complete!")
    print("Dataset shape:", X.shape)
    print("Failed images:", failed)

if __name__ == "__main__":
    main()
    
    