from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import cv2
import torch
import numpy as np
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Load YOLOv5 models
model_plate = torch.hub.load('ultralytics/yolov5', 'custom',
    path='models/LP_detector_nano_61.pt', force_reload=True).to('cpu')
model_text = torch.hub.load('ultralytics/yolov5', 'custom',
    path='models/LP_ocr.pt', force_reload=True).to('cpu')

# Dummy red light detector (replace with your YOLO model or HSV method)
def is_red_light_on(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_pixels = cv2.countNonZero(mask1)
    return red_pixels > 500

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    name = os.path.basename(video_path).split('.')[0]
    output_path = os.path.join(RESULT_FOLDER, f'{name}_processed.avi')
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect red light
        red_light = is_red_light_on(frame)

        # Detect plates
        results_plate = model_plate(frame)
        boxes = results_plate.xyxy[0].numpy()

        for box in boxes:
            x1, y1, x2, y2, conf, cls = box
            if conf > 0.5:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cropped = frame[int(y1):int(y2), int(x1):int(x2)]

                # OCR
                results_text = model_text(cropped)
                texts = results_text.pandas().xyxy[0]['name'].to_list()
                plate_text = ' '.join(texts)

                if red_light and plate_text:
                    cv2.putText(frame, f'VI PHAM: {plate_text}', (int(x1), int(y1)-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        out.write(frame)

    cap.release()
    out.release()
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video = request.files['video']
        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)
        processed = process_video(video_path)
        return redirect(url_for('result', filename=os.path.basename(processed)))
    return render_template('index.html')

@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(RESULT_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
