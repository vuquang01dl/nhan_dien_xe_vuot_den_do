from flask import Flask, request, jsonify
import os
from datetime import datetime
from services.process_video import process_violation_video

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + file.filename
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(video_path)

    # Xử lý video bằng AI
    result = process_violation_video(video_path)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
