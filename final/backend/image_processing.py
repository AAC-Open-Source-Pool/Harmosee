import cv2
import numpy as np
import os
from inference_sdk import InferenceHTTPClient


def biggest_contour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 1000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest

def preprocess_image(image_path):
    """Preprocess image to detect largest 4-point contour and warp perspective."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at: {image_path}")
    
    img_original = img.copy()

    # Grayscale + Edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 20, 30, 30)
    edged = cv2.Canny(gray, 10, 20)

    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    biggest = biggest_contour(contours)

    if biggest.size != 0:
        # Reorder corner points
        points = biggest.reshape(4, 2)
        input_points = np.zeros((4, 2), dtype="float32")

        points_sum = points.sum(axis=1)
        input_points[0] = points[np.argmin(points_sum)]
        input_points[3] = points[np.argmax(points_sum)]

        points_diff = np.diff(points, axis=1)
        input_points[1] = points[np.argmin(points_diff)]
        input_points[2] = points[np.argmax(points_diff)]

        (top_left, top_right, bottom_right, bottom_left) = input_points
        bottom_width = np.linalg.norm(bottom_right - bottom_left)
        top_width = np.linalg.norm(top_right - top_left)
        right_height = np.linalg.norm(top_right - bottom_right)
        left_height = np.linalg.norm(top_left - bottom_left)

        max_width = max(int(bottom_width), int(top_width))
        max_height = int(max_width * 1.414)  # aspect ratio

        converted_points = np.float32([[0, 0], [max_width, 0],
                                       [0, max_height], [max_width, max_height]])

        matrix = cv2.getPerspectiveTransform(input_points, converted_points)
        img_output = cv2.warpPerspective(img_original, matrix, (max_width, max_height))

        print("✅ Perspective correction successful.")
        return img_output
    else:
        print("⚠ No suitable 4-point contour found. Returning original image.")
        return img_original

# import the inference-sdk

def run_model_inference(image_path):
    ROBOFLOW_API_KEY= os.getenv("ROBOFLOW_API_KEY")
    #if not ROBOFLOW_API_KEY:
    #    raise ValueError("ROBOFLOW_API_KEY environment variable not set.")
    # initialize the client
    CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY

)

    result = CLIENT.infer(image_path, model_id="sheet-music-player-pxhh2/1")
    predictions = result.get("predictions", [])
    return [pred["class"] for pred in predictions]

def extract_notes_from_image(image_path):
    processed = preprocess_image(image_path)
    temp_path = "processed_output.jpg"
    cv2.imwrite(temp_path, processed)
    return run_model_inference(temp_path)