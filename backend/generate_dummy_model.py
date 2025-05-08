import tensorflow as tf
from tensorflow.keras import layers, models

# Create a very simple CNN model
model = models.Sequential([
    layers.Input(shape=(224, 224, 3)),  # Expecting 224x224 RGB images
    layers.Conv2D(8, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(16, activation='relu'),
    layers.Dense(1, activation='sigmoid')  # Binary output: real or fake
])

# Compile the model
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Save it as model.h5
model.save('model.h5')

print("✅ Dummy model saved as model.h5")