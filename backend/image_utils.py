import cv2
import numpy as np
from tensorflow.keras.models import load_model
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODEL_PATH = "/home/suggest/kweli-frontend/backend/models/model.h5"
INPUT_SIZE = (224, 224)

class ImageProcessor:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        """Load ML model with validation"""
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file missing at {MODEL_PATH}")
        
        try:
            model = load_model(MODEL_PATH)
            logger.info("✅ Model loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            raise

    def preprocess(self, image_path):
        """Standardize image input"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Invalid image file")
                
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, INPUT_SIZE)
            img = img / 255.0  # Normalize
            return np.expand_dims(img, axis=0)
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise

    def predict(self, processed_img):
        """Run prediction with checks"""
        if not hasattr(self, 'model'):
            raise RuntimeError("Model not initialized")
            
        try:
            prediction = self.model.predict(processed_img)
            return float(prediction[0][0])  # Return probability
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

# Singleton instance
processor = ImageProcessor()

def preprocess_image(image_path):
    """Public interface for preprocessing"""
    return processor.preprocess(image_path)

def predict_image(processed_img):
    """Public interface for prediction"""
    return processor.predict(processed_img)
