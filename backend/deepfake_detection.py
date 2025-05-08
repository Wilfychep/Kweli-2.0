import os
import random
import numpy as np
import cv2
import hashlib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# Try loading model, fallback to mock
try:
    model = load_model('models/model.h5')
    use_mock = False
except Exception as e:
    print(f"⚠️ Model load failed, using mock predictions. Error: {e}")
    use_mock = True

TARGET_SIZE = (224, 224)

def hash_file(file_path):
    """Generate SHA-256 hash of file content"""
    with open(file_path, "rb") as f:
        file_data = f.read()
        return hashlib.sha256(file_data).hexdigest()

def preprocess_image(img_path, target_size=TARGET_SIZE):
    img = load_img(img_path, target_size=target_size)
    img_array = img_to_array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

def preprocess_video(video_path, target_size=TARGET_SIZE, max_frames=10):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0

    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        resized = cv2.resize(frame, target_size)
        normalized = resized.astype("float32") / 255.0
        frames.append(normalized)
        frame_count += 1

    cap.release()
    return np.array(frames) if frames else None

def detect_deepfake(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    file_hash = hash_file(file_path)

    if ext in ['.jpg', '.jpeg', '.png']:
        input_data = preprocess_image(file_path)
    elif ext in ['.mp4', '.mov', '.avi']:
        input_data = preprocess_video(file_path)
        if input_data is None:
            return "error", 0.0, file_hash
    else:
        return "unsupported file type", 0.0, file_hash

    # Use mock if model isn't available
    if use_mock:
        label = random.choice(["real", "fake"])
        confidence = round(random.uniform(0.65, 0.98), 2)
        return label, confidence, file_hash

    # Predict with actual model
    predictions = model.predict(input_data)
    print(f"Raw predictions: {predictions}")

    if predictions.ndim == 2 and predictions.shape[0] > 1:
        avg_conf = np.mean(predictions[:, 0])
        label = "fake" if avg_conf > 0.5 else "real"
        return label, float(avg_conf), file_hash
    else:
        conf = float(predictions[0][0])
        label = "fake" if conf > 0.5 else "real"
        return label, conf, file_hash
