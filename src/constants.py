CLASS_NAMES = {
    # Custom model: models/best.pt
    0: "Sitting",
    1: "Standing",
    2: "Person",
    3: "Tricycle",

    # COCO model: models/yolov8n.pt, remapped to avoid class-id conflict
    10: "Car",
    11: "Motorcycle",
    12: "Bus",
    13: "Truck",
}

CUSTOM_CLASS_IDS = [0, 1, 2, 3]
CLASS_IDS = list(CLASS_NAMES.keys())

COLORS = {
    "Sitting": (255, 255, 0),
    "Standing": (0, 255, 0),
    "Person": (255, 0, 0),
    "Tricycle": (0, 165, 255),
    "Car": (0, 255, 0),
    "Motorcycle": (255, 0, 255),
    "Bus": (255, 128, 0),
    "Truck": (0, 0, 255),
    "Object": (255, 255, 255),
}

CLASS_NAMES = {
    0: "Sitting",
    1: "Standing",
    2: "Person",
    3: "Tricycle",
    10: "Car",
    11: "Motorcycle",
    12: "Bus",
    13: "Truck",
}

DISPLAY_CLASSES = [
    "Sitting",
    "Standing",
    "Person",
    "Tricycle",
    "Car",
    "Motorcycle",
    "Bus",
    "Truck",
]
