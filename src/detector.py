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
    result = []

    for det in detections:
        cls = int(det[5])

        # 13 = Truck
        if cls == 13:
            overlapped_with_car = False 

            for other in detections:
                # 10 = Car
                if int(other[5]) == 10 and iou(det, other) > iou_threshold:
                    overlapped_with_car = True
                    break

            if overlapped_with_car:
                continue

        result.append(det)

    return result


def remove_sitting_standing_overlap(detections, iou_threshold=0.45):
    """
    Nếu Sitting và Standing chồng nhau thì giữ box confidence cao hơn.
    0 = Sitting
    1 = Standing
    """
    detections = sorted(detections, key=lambda x: x[4], reverse=True)
    result = []

    for det in detections:
        cls = int(det[5])

        if cls in [0, 1]:
            overlapped = False

            for kept in result:
                kept_cls = int(kept[5])

                if kept_cls in [0, 1] and iou(det, kept) > iou_threshold:
                    overlapped = True
                    break

            if overlapped:
                continue

        result.append(det)

    return result


def remove_duplicate_boxes(detections, iou_threshold=0.65):
    """
    Xóa box trùng cùng class, giữ box có confidence cao hơn.
    """
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
    - models/best.pt: Sitting, Standing, Tricycle
    - models/yolov8n.pt: Car, Motorcycle, Bus, Truck
    """

    def __init__(self, model_path=None, conf_threshold=0.25, imgsz=640):
        self.custom_model = YOLO("models/best.pt")
        self.coco_model = YOLO("models/yolov8n.pt")

        self.enable_coco = False

        # Custom thấp hơn để vẫn bắt được người xa/bị che
        self.custom_conf = 0.30

        # COCO cao hơn để giảm box rác Car/Truck
        self.coco_conf = 0.40

        self.imgsz = imgsz

    def detect(self, frame):
        detections = []

        # ===== CUSTOM MODEL =====
        custom_results = self.custom_model(
            frame,
            conf=self.custom_conf,
            imgsz=self.imgsz,
            augment=False,
            verbose=False,
        )[0]

        for box in custom_results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            w = x2 - x1
            h = y2 - y1

            if w < 20 or h < 20:
                continue

            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # CUSTOM_CLASS_IDS phải là [0, 1, 3]
            # 0 Sitting, 1 Standing, 3 Tricycle
            # Không có 2 Person
            if cls in CUSTOM_CLASS_IDS:

                # 0 = Sitting
                if cls == 0 and conf < 0.70:
                    continue

                # 1 = Standing
                if cls == 1 and conf < 0.35:
                    continue

                # 3 = Tricycle
                if cls == 3 and conf < 0.35:
                    continue

                detections.append([x1, y1, x2, y2, conf, cls])
        detections = remove_sitting_standing_overlap(detections)
        detections = remove_duplicate_boxes(detections)

        return detections
        # ===== COCO MODEL =====
        if self.enable_coco:

            coco_results = self.coco_model(
                frame,
                conf=self.coco_conf,
                imgsz=self.imgsz,
                verbose=False,
            )[0]

            for box in coco_results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                w = x2 - x1
                h = y2 - y1

                if w < 20 or h < 20:
                    continue

                conf = float(box.conf[0])
                cls = int(box.cls[0])

                if cls in COCO_ID_MAP:
                    new_cls = COCO_ID_MAP[cls]
                    detections.append([x1, y1, x2, y2, conf, new_cls])

        detections = prefer_car_over_truck(detections)
        detections = remove_sitting_standing_overlap(detections)
        detections = remove_duplicate_boxes(detections)

        return detections   