from ultralytics import YOLO
from .constants import CUSTOM_CLASS_IDS


# COCO class id -> project class id
# 2 car, 3 motorcycle, 5 bus, 7 truck
COCO_ID_MAP = {
    2: 10,  # Car
    3: 11,  # Motorcycle
    5: 12,  # Bus
    7: 13,  # Truck
}


def iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = max(0, box1[2] - box1[0]) * max(0, box1[3] - box1[1])
    area2 = max(0, box2[2] - box2[0]) * max(0, box2[3] - box2[1])

    union = area1 + area2 - inter
    return inter / union if union > 0 else 0


def prefer_car_over_truck(detections, iou_threshold=0.55):
    """Nếu Car và Truck chồng lên nhau, ưu tiên giữ Car và bỏ Truck."""
    result = []

    for det in detections:
        cls = int(det[5])

        if cls == 13:  # Truck
            overlapped_with_car = False

            for other in detections:
                if int(other[5]) == 10 and iou(det, other) > iou_threshold:
                    overlapped_with_car = True
                    break

            if overlapped_with_car:
                continue

        result.append(det)

    return result


def remove_duplicate_boxes(detections, iou_threshold=0.65):
    """Xóa box trùng cùng class, giữ box có confidence cao hơn."""
    detections = sorted(detections, key=lambda x: x[4], reverse=True)
    filtered = []

    for det in detections:
        duplicate = False

        for kept in filtered:
            same_class = int(det[5]) == int(kept[5])
            if same_class and iou(det, kept) > iou_threshold:
                duplicate = True
                break

        if not duplicate:
            filtered.append(det)

    return filtered


class ObjectDetector:
    """
    Dùng 2 model:
    - models/best.pt: Sitting, Standing, Person, Tricycle
    - models/yolov8n.pt: Car, Motorcycle, Bus, Truck
    """

    def __init__(self, model_path=None, conf_threshold=0.15, imgsz=960):
        self.custom_model = YOLO("models/best.pt")
        self.coco_model = YOLO("models/yolov8n.pt")
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz

    def detect(self, frame):
        detections = []

        custom_results = self.custom_model(
            frame,
            conf=self.conf_threshold,
            imgsz=self.imgsz,
            verbose=False,
        )[0]

        for box in custom_results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            if cls in CUSTOM_CLASS_IDS:
                detections.append([x1, y1, x2, y2, conf, cls])

        coco_results = self.coco_model(
            frame,
            conf=self.conf_threshold,
            imgsz=self.imgsz,
            verbose=False,
        )[0]

        for box in coco_results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            if cls in COCO_ID_MAP:
                new_cls = COCO_ID_MAP[cls]
                detections.append([x1, y1, x2, y2, conf, new_cls])

        detections = prefer_car_over_truck(detections)
        detections = remove_duplicate_boxes(detections)
        return detections
