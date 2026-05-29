import cv2
import numpy as np

# Import face detection module
from app.services.face_detection import detect_face_landmarks


# -------------------------
# HELPER FUNCTIONS
# -------------------------

def distance(p1, p2):

    return np.linalg.norm(
        np.array(p1) - np.array(p2)
    )


def compute_angle(a, b, c):

    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)

    cos_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) *
        np.linalg.norm(bc) +
        1e-6
    )

    return np.degrees(
        np.arccos(
            np.clip(cos_angle, -1.0, 1.0)
        )
    )


# -------------------------
# FEATURE EXTRACTION
# -------------------------

def extract_features(image):

    # Get facial landmarks
    points = detect_face_landmarks(image)

    # No face detected
    if points is None:
        return None

    try:

        # -------------------------
        # GEOMETRY FEATURES
        # -------------------------

        face_width = distance(
            points[234],
            points[454]
        )

        face_height = distance(
            points[10],
            points[152]
        )

        jaw_width = distance(
            points[58],
            points[288]
        )

        forehead_width = distance(
            points[103],
            points[332]
        )

        left_eye = distance(
            points[33],
            points[133]
        )

        right_eye = distance(
            points[362],
            points[263]
        )

        eye_size = (
            left_eye + right_eye
        ) / 2

        eye_spacing = distance(
            points[133],
            points[362]
        )

        nose_length = distance(
            points[168],
            points[1]
        )

        mouth_width = distance(
            points[61],
            points[291]
        )

        # -------------------------
        # RATIO FEATURES
        # -------------------------

        face_ratio = face_height / (
            face_width + 1e-6
        )

        jaw_ratio = jaw_width / (
            face_width + 1e-6
        )

        forehead_ratio = forehead_width / (
            face_width + 1e-6
        )

        eye_ratio = eye_size / (
            face_width + 1e-6
        )

        eye_spacing_ratio = eye_spacing / (
            face_width + 1e-6
        )

        nose_ratio = nose_length / (
            face_height + 1e-6
        )

        mouth_ratio = mouth_width / (
            face_width + 1e-6
        )

        # -------------------------
        # ANGLE FEATURES
        # -------------------------

        jaw_angle_left = compute_angle(
            points[234],
            points[58],
            points[152]
        )

        jaw_angle_right = compute_angle(
            points[454],
            points[288],
            points[152]
        )

        # -------------------------
        # TEXTURE FEATURES
        # -------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        laplacian_var = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        edges = cv2.Canny(
            gray,
            100,
            200
        )

        edge_density = (
            np.sum(edges > 0) /
            edges.size
        )

        # -------------------------
        # COLOR FEATURES
        # -------------------------

        lab = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2LAB
        )

        L, A, B = cv2.split(lab)

        mean_L = np.mean(L)
        mean_A = np.mean(A)
        mean_B = np.mean(B)

        BGR = cv2.split(image)

        redness = np.mean(
            BGR[2] - BGR[1]
        )

        color_std = np.std(L)

        # -------------------------
        # SYMMETRY FEATURE
        # -------------------------

        symmetry = abs(

            distance(
                points[234],
                points[152]
            )

            -

            distance(
                points[454],
                points[152]
            )
        )

        # -------------------------
        # ENGINEERED FEATURES
        # -------------------------

        roundness = 1 / (
            face_ratio + 1e-6
        )

        jaw_balance = abs(
            jaw_angle_left -
            jaw_angle_right
        )

        smoothness = 1 / (
            edge_density + 1e-6
        )

    except:
        return None

    # -------------------------
    # FINAL FEATURE VECTOR
    # -------------------------

    return [

        face_ratio,
        jaw_ratio,
        forehead_ratio,

        eye_ratio,
        eye_spacing_ratio,
        nose_ratio,

        mouth_ratio,

        jaw_angle_left,
        jaw_angle_right,

        laplacian_var,
        edge_density,

        mean_L,
        mean_A,
        mean_B,

        redness,
        color_std,
        symmetry,

        roundness,
        jaw_balance,
        smoothness
    ]