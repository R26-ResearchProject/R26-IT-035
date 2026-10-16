import cv2
import numpy as np

def validate_file(file):
    allowed_types = ["image/jpeg", "image/png"]

    if file.content_type not in allowed_types:
        return False, "Invalid file type"

    return True, None


def check_blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    if blur_score < 50:
        return False, "Image is too blurry"

    return True, None


def check_lighting(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)

    if brightness < 50:
        return False, "Image too dark"
    if brightness > 220:
        return False, "Image too bright"

    return True, None