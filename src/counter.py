from collections import defaultdict
from .constants import CLASS_NAMES


class SmartLineCounter:
    """
    Bộ đếm line thông minh.

    line_mode:
        horizontal: đếm khi object đi qua line ngang.
        vertical: đếm khi object đi qua line dọc.
        auto: tự chọn theo hướng chuyển động chính của object.

    line_pos:
        0 < line_pos < 1: hiểu là tỷ lệ theo width/height.
        line_pos >= 1: hiểu là pixel.
    """

    def __init__(self, frame_width, frame_height, line_mode="auto", line_pos=0.5):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.line_mode = line_mode
        self.line_pos = float(line_pos)

        self.line_x = self._resolve_pos(self.line_pos, self.frame_width)
        self.line_y = self._resolve_pos(self.line_pos, self.frame_height)

        self.previous_centers = {}
        self.counted_ids = set()

        self.total_count = 0
        self.class_counts = defaultdict(int)
        self.direction_counts = defaultdict(int)
        self.events = []

    def _resolve_pos(self, value, size):
        if 0 < value < 1:
            return int(value * size)
        return int(value)

    def update_video_size(self, width, height):
        self.frame_width = width
        self.frame_height = height
        self.line_x = self._resolve_pos(self.line_pos, width)
        self.line_y = self._resolve_pos(self.line_pos, height)

    def _cross_horizontal(self, prev_y, current_y):
        if prev_y <= self.line_y < current_y:
            return "down"
        if prev_y >= self.line_y > current_y:
            return "up"
        return None

    def _cross_vertical(self, prev_x, current_x):
        if prev_x <= self.line_x < current_x:
            return "right"
        if prev_x >= self.line_x > current_x:
            return "left"
        return None

    def update(self, track_id, cls, center_x, center_y, frame_index, timestamp):
        track_id = int(track_id)
        cls = int(cls)

        class_name = CLASS_NAMES.get(cls, "Object")
        previous = self.previous_centers.get(track_id)
        self.previous_centers[track_id] = (center_x, center_y)

        # None: chỉ nhận diện/tracking, không đếm qua line
        if self.line_mode == "none":
            return None

        if previous is None:
            return None

        if track_id in self.counted_ids:
            return None

        prev_x, prev_y = previous
        direction = None
        used_line = None

        if self.line_mode == "horizontal":
            direction = self._cross_horizontal(prev_y, center_y)
            used_line = "horizontal"

        elif self.line_mode == "vertical":
            direction = self._cross_vertical(prev_x, center_x)
            used_line = "vertical"

        else:
            dx = abs(center_x - prev_x)
            dy = abs(center_y - prev_y)

            if dx >= dy:
                direction = self._cross_vertical(prev_x, center_x)
                used_line = "vertical"
                if direction is None:
                    direction = self._cross_horizontal(prev_y, center_y)
                    used_line = "horizontal"
            else:
                direction = self._cross_horizontal(prev_y, center_y)
                used_line = "horizontal"
                if direction is None:
                    direction = self._cross_vertical(prev_x, center_x)
                    used_line = "vertical"

        if direction is None:
            return None

        self.counted_ids.add(track_id)
        self.total_count += 1
        self.class_counts[class_name] += 1
        self.direction_counts[direction] += 1

        event = {
            "frame": frame_index,
            "time_sec": round(timestamp, 3),
            "track_id": track_id,
            "class_name": class_name,
            "direction": direction,
            "line": used_line,
            "total_count": self.total_count,
            "class_count": self.class_counts[class_name],
        }

        self.events.append(event)
        return event

    def get_summary(self):
        return {
            "total": int(self.total_count),
            "by_class": dict(self.class_counts),
            "by_direction": dict(self.direction_counts),
            "line_mode": self.line_mode,
            "line_x": self.line_x,
            "line_y": self.line_y,
        }
