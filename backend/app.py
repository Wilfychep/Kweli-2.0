import os
import logging
import asyncio
import time
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from image_utils import preprocess_image, predict_image
from starknet_utils import init_starknet, store_result_sync, get_result_sync
import hashlib
import traceback

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limit

# Enhanced CORS configuration
CORS(app, resources={
    r"/upload": {
        "origins": ["http://localhost:*", "http://192.168.*", "exp://*"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    },
    r"/result/*": {
        "origins": "*",
        "methods": ["GET"]
    }
})

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global contract instance
my_contract = None

async def initialize_contract():
    """Initialize Starknet contract with retry logic"""
    global my_contract
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"🔧 Initializing Starknet contract (attempt {attempt + 1})...")
            my_contract = await init_starknet()
            if my_contract:
                logger.info("✅ Starknet contract ready")
                return
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Contract init failed: {str(e)}")
            if attempt == max_retries - 1:
                raise

def store_with_retry(felt_hash, prediction, max_retries=3):
    """Retry Starknet transactions with backoff"""
    for attempt in range(max_retries):
        try:
            tx_hash = store_result_sync(my_contract, felt_hash, prediction)
            if tx_hash:
                return tx_hash
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2 ** attempt)
    return None

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint for service health monitoring"""
    return jsonify({
        "status": "healthy",
        "contract_ready": bool(my_contract),
        "timestamp": datetime.utcnow().isoformat(),
        "storage_available": os.access(UPLOAD_FOLDER, os.W_OK)
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Secure file upload handler with full validation"""
    try:
        logger.info(f"Incoming upload from {request.remote_addr}")
        
        # Validate file
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Validate extension
        allowed_ext = {'jpg', 'jpeg', 'png'}
        ext = file.filename.split('.')[-1].lower()
        if '.' not in file.filename or ext not in allowed_ext:
            return jsonify({"error": f"Invalid file type. Allowed: {allowed_ext}"}), 400

        # Secure save
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        # Atomic write
        temp_path = f"{filepath}.tmp"
        file.save(temp_path)
        os.rename(temp_path, filepath)

        # Verify saved file
        if not os.path.exists(filepath):
            raise Exception("File save verification failed")

        # Process image
        preprocessed = preprocess_image(filepath)
        prediction = int(predict_image(preprocessed))  # 0=real, 1=fake
        label = "fake" if prediction == 1 else "real"
        logger.info(f"Prediction: {label}")

        # Generate hash
        with open(filepath, "rb") as f:
            file_data = f.read()
        image_hash = int.from_bytes(hashlib.sha256(file_data).digest()[:31], "big")
        logger.info(f"Image hash: 0x{image_hash:x}")

        # Store on Starknet
        tx_hash = store_with_retry(image_hash, prediction)
        if not tx_hash:
            raise Exception("Max retries reached for Starknet transaction")

        return jsonify({
            "status": "success",
            "result": label,
            "tx_hash": tx_hash,
            "image_hash": f"0x{image_hash:x}"
        })

    except Exception as e:
        logger.error(f"Upload failed: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/result/<image_hash>", methods=["GET"])
def get_result(image_hash):
    """Retrieve prediction from Starknet"""
    try:
        image_hash_int = int(image_hash, 16)
        result = get_result_sync(my_contract, image_hash_int)
        
        if result is None:
            return jsonify({"status": "not_found"}), 404
            
        return jsonify({
            "status": "success",
            "result": "fake" if result == 1 else "real"
        })

    except Exception as e:
        logger.error(f"Result lookup failed: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def run_server():
    """Start the application with proper shutdown handling"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(initialize_contract())
        app.run(host="0.0.0.0", port=5000, debug=False)  # debug=False for production
    except Exception as e:
        logger.critical(f"Fatal startup error: {str(e)}")
    finally:
        loop.close()

if __name__ == "__main__":
    run_server()