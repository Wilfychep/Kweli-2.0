import hashlib
import logging

logger = logging.getLogger(__name__)

def hash_image(filepath):
    """Return a SHA256 hash of the image file."""
    try:
        with open(filepath, "rb") as f:
            file_data = f.read()
        image_hash = hashlib.sha256(file_data).hexdigest()
        logger.info(f"🔐 Image hash: {image_hash}")
        return image_hash
    except Exception as e:
        logger.error(f"❌ Failed to hash image: {e}")
        raise
