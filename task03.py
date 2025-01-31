from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import os
import numpy as np
import cv2
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

OUTPUT_DIR = "captured_faces"
os.makedirs(OUTPUT_DIR, exist_ok=True)
   

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

# Ensure directories exist or handle errors
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
except OSError as e:
    print(f"Error creating directories: {e}")
    raise


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def optimize_image(image_path):
    image = Image.open(image_path)
    optimized_path = os.path.join(app.config["PROCESSED_FOLDER"], os.path.basename(image_path))
    image.save(optimized_path, "JPEG", optimize=True, quality=75)
    return optimized_path


def detect_duplicates(image_path, folder):
    query_image = cv2.imread(image_path)
    query_image = cv2.cvtColor(query_image, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(query_image, None)
    for filename in os.listdir(folder):
        if filename == os.path.basename(image_path):
            continue
        existing_image_path = os.path.join(folder, filename)
        existing_image = cv2.imread(existing_image_path)
        existing_image = cv2.cvtColor(existing_image, cv2.COLOR_BGR2GRAY)
        kp2, des2 = orb.detectAndCompute(existing_image, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        if len(matches) > 0 and len(matches) / min(len(kp1), len(kp2)) > 0.9:
            return True, filename
    return False, None


@app.route("/")
def home():
    return render_template("task03.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "profile_image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["profile_image"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Check for duplicates
        is_duplicate, duplicate_file = detect_duplicates(file_path, app.config["UPLOAD_FOLDER"])
        if is_duplicate:
            return jsonify({"message": "Duplicate image detected", "duplicate_file": duplicate_file}), 200

        # Optimize and return success
        optimize_image(file_path)
        return jsonify({"message": "File uploaded and optimized successfully", "filename": filename}), 201

    return jsonify({"error": f"File type not allowed: {file.filename}"}), 400


if __name__ == "__main__":
    app.run(debug=True)
