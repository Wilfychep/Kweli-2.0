from tensorflow.keras.models import load_model
print("Attempting to load model...")
model = load_model("/home/suggest/kweli-frontend/backend/models/model.h5")
print("✅ Model loaded successfully!")