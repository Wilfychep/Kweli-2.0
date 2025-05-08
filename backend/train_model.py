import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam

DATA_DIR = os.path.join(os.getcwd(), "data")
MODEL_PATH = os.path.join(os.getcwd(), "models", "model.h5")
BATCH_SIZE = 16
IMAGE_SIZE = (224, 224)
EPOCHS = 5  # increase for better accuracy

# Prepare data
datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)
train_gen = train_datagen.flow_from_directory(
    'dataset/train',
    target_size=(224, 224),
    batch_size=8,
    class_mode='binary',
    shuffle=True
)

val_datagen = ImageDataGenerator(rescale=1./255)

val_gen = val_datagen.flow_from_directory(
    'dataset/val',
    target_size=(224, 224),
    batch_size=8,
    class_mode='binary',
    shuffle=False
)

# Define a simple CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation="relu", input_shape=(*IMAGE_SIZE, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(64, activation="relu"),
    Dropout(0.5),
    Dense(1, activation="sigmoid")  # binary classification
])

model.compile(optimizer=Adam(learning_rate=0.0001), loss="binary_crossentropy", metrics=["accuracy"])

# Train model
model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS)

# Save model
model.save(MODEL_PATH)
print(f"✅ Model saved at: {MODEL_PATH}")
