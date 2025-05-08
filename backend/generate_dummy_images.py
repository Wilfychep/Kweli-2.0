import os
import numpy as np
from PIL import Image

# Configuration
image_size = (224, 224)
num_train = 10
num_val = 5
classes = ['real', 'fake']
base_dir = 'dataset'

# Function to create random image
def create_dummy_image(path):
    array = np.random.randint(0, 255, (image_size[1], image_size[0], 3), dtype=np.uint8)
    img = Image.fromarray(array)
    img.save(path)

# Generate dummy images
for split in ['train', 'val']:
    for label in classes:
        dir_path = os.path.join(base_dir, split, label)
        os.makedirs(dir_path, exist_ok=True)
        num_images = num_train if split == 'train' else num_val
        for i in range(num_images):
            image_path = os.path.join(dir_path, f'{label}_{i}.jpg')
            create_dummy_image(image_path)
            print(f"Created: {image_path}")

print("\n✅ Dummy image generation complete.")
