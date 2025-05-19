import os
import sys
import cv2
import torch
from datetime import datetime
from ultralytics import YOLO
from utils.ocr_sort import sort_ocr_boxes

# Thêm đường dẫn đến YOLOv5 local
YOLOV5_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'yolov5'))
if YOLOV5_PATH not in sys.path:
    sys.path.insert(0, YOLOV5_PATH)

# Import các thành phần cần thiết từ YOLOv5
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import non_max_suppression
from yolov5.utils.torch_utils import select_device


# Load các mô hình
device = select_device('cpu')

model_vehicle = YOLO("models/loaixe.pt")  # YOLOv8 dùng ultralytics
model_plate = DetectMultiBackend("models/LP_detector_nano_61.pt", device=device)
model_text = DetectMultiBackend("models/LP_ocr.pt", device=device)

def run_yolo5_detection(model, image):
    """Chuyển ảnh sang dạng tensor và chạy model YOLOv5 local"""
    img = cv2.resize(image, (640, 640))
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR -> RGB, HWC -> CHW
    img = torch.from_numpy(img).float().to(device) / 255.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    with torch.no_grad():
        pred = model(img)
        pred = non_max_suppression(pred, conf_thres=0.3, iou_thres=0.5)
    return pred

def process_violation_video(video_path):
    cap = cv2.VideoCapture(video_path)
    STOP_LINE_Y = 250
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 5 != 0:
            continue

        # Giả định luôn có đèn đỏ để kiểm tra vượt
        red_light = True

        # Phát hiện phương tiện bằng YOLOv8
        results_vehicle = model_vehicle(frame)
        for box in results_vehicle[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cls_id = int(box.cls[0])
            vehicle_type = model_vehicle.names[cls_id]
            center_y = (y1 + y2) // 2

            if red_light and center_y > STOP_LINE_Y:
                vehicle_crop = frame[y1:y2, x1:x2]

                # Phát hiện biển số
                pred_plate = run_yolo5_detection(model_plate, vehicle_crop)
                for det in pred_plate[0]:
                    px1, py1, px2, py2, conf, cls = map(int, det[:6])
                    plate_crop = vehicle_crop[py1:py2, px1:px2]

                    # Nhận diện ký tự
                    pred_text = run_yolo5_detection(model_text, plate_crop)
                    plate_number = sort_ocr_boxes(pred_text, model_text)

                    # Trả kết quả
                    cap.release()
                    return {
                        "vehicle_type": vehicle_type,
                        "plate_number": plate_number,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "violation": "Vượt đèn đỏ"
                    }

    cap.release()
    return {
        "vehicle_type": "Không rõ",
        "plate_number": "Không rõ",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "violation": "Không phát hiện"
    }
