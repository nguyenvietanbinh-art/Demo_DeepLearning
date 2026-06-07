import os
import time
import cv2

from .constants import CLASS_NAMES, COLORS, DISPLAY_CLASSES
from .counter import SmartLineCounter
from .detector import ObjectDetector
from .tracker_manager import TrackerManager
from .stats_writer import save_events_csv
from .video_utils import convert_to_web_mp4


class VideoProcessor:
    """
    Pipeline chính:
        Video/Camera
        -> YOLOv8
        -> ByteTrack
        -> Line Counting
        -> Output video + CSV

    Điểm quan trọng:
        keep_original_size=True giúp giữ nguyên tỉ lệ/kích thước video gốc,
        nhờ vậy bounding box rõ hơn và dễ quan sát khi demo đồ án.
    """

    def __init__(
        self,
        model_path="yolov8n.pt",
        conf_threshold=0.15,
        line_mode="auto",
        line_pos=0.5,
        keep_original_size=True,
        output_width=None,
        output_height=None,
        imgsz=960,
    ):
        self.detector = ObjectDetector(model_path=model_path, conf_threshold=conf_threshold, imgsz=imgsz)
        self.tracker = TrackerManager()

        self.keep_original_size = keep_original_size
        self.output_width = output_width
        self.output_height = output_height

        self.line_mode = line_mode
        self.line_pos = line_pos
        self.counter = None

    def _get_output_size(self, first_frame):
        height, width = first_frame.shape[:2]

        if self.keep_original_size:
            return width, height

        if self.output_width and self.output_height:
            return int(self.output_width), int(self.output_height)

        return width, height

    def _resize_if_needed(self, frame, output_size):
        width, height = output_size

        if frame.shape[1] == width and frame.shape[0] == height:
            return frame

        return cv2.resize(frame, (width, height))

    def _draw_lines(self, frame):
        height, width = frame.shape[:2]
        self.counter.update_video_size(width, height)

        if self.counter.line_mode == "none":
            return

        if self.counter.line_mode in ("horizontal", "auto"):
            cv2.line(frame, (0, self.counter.line_y), (width, self.counter.line_y), (0, 255, 0), 3)
            cv2.putText(
                frame,
                "H-Line",
                (20, max(25, self.counter.line_y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        if self.counter.line_mode in ("vertical", "auto"):
            cv2.line(frame, (self.counter.line_x, 0), (self.counter.line_x, height), (255, 0, 0), 3)
            cv2.putText(
                frame,
                "V-Line",
                (min(width - 130, self.counter.line_x + 10), 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2,
            )

    def _draw_summary(self, frame, fps):
        x, y = 20, 35

        cv2.putText(frame, f"FPS: {fps:.1f}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        y += 30
        cv2.putText(frame, f"Total: {self.counter.total_count}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        y += 30
        for name in DISPLAY_CLASSES:
            value = self.counter.class_counts.get(name, 0)
            cv2.putText(frame, f"{name}: {value}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2)
            y += 24

    def process(
        self,
        source,
        output_video_path,
        output_web_video_path,
        output_csv_path,
        display=False,
        save_video=True,
        max_frames=None,
    ):
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise RuntimeError(f"Không mở được nguồn video/camera: {source}")

        ret, first_frame = cap.read()
        if not ret:
            cap.release()
            raise RuntimeError("Không đọc được frame đầu tiên.")

        output_size = self._get_output_size(first_frame)
        width, height = output_size

        self.counter = SmartLineCounter(
            frame_width=width,
            frame_height=height,
            line_mode=self.line_mode,
            line_pos=self.line_pos,
        )

        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

        writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")

            if isinstance(source, int):
                output_fps = 10.0
            else:
                output_fps = cap.get(cv2.CAP_PROP_FPS)

                if not output_fps or output_fps <= 1 or output_fps > 60:
                    output_fps = 25.0

            writer = cv2.VideoWriter(
                output_video_path,
                fourcc,
                output_fps,
                output_size
            )

            if not writer.isOpened():
                cap.release()
                raise RuntimeError(f"Không tạo được VideoWriter: {output_video_path}")

        frame_index = 0
        start_time = time.time()
        previous_time = start_time

        current_frame = first_frame

        while True:
            frame_index += 1
            if max_frames and frame_index > max_frames:
                break

            frame = self._resize_if_needed(current_frame, output_size)

            now = time.time()
            fps = 1.0 / max(now - previous_time, 1e-6)
            previous_time = now
            timestamp = now - start_time

            detections = self.detector.detect(frame)
            tracks = self.tracker.update(detections, frame)

            self._draw_lines(frame)

            for track in tracks:
                if len(track) < 7:
                    continue

                x1, y1, x2, y2, track_id, score, cls = track[:7]
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                track_id = int(track_id)
                cls = int(cls)

                class_name = CLASS_NAMES.get(cls, "Object")
                color = COLORS.get(class_name, (255, 255, 255))

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                event = self.counter.update(track_id, cls, center_x, center_y, frame_index, timestamp)
                if event:
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    f"{class_name} ID:{track_id}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    color,
                    2,
                )

            self._draw_summary(frame, fps)

            if writer:
                writer.write(frame)

            if display:
                preview = frame
                if preview.shape[1] > 1280:
                    scale = 1280 / preview.shape[1]
                    preview = cv2.resize(preview, (1280, int(preview.shape[0] * scale)))

                cv2.imshow("SmartCounterAI", preview)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            ret, current_frame = cap.read()
            if not ret:
                break

        cap.release()

        if writer:
            writer.release()

        if display:
            cv2.destroyAllWindows()

        summary = self.counter.get_summary()
        save_events_csv(output_csv_path, self.counter.events, summary)

        web_video = output_video_path
        if save_video and output_web_video_path:
            try:
                web_video = convert_to_web_mp4(output_video_path, output_web_video_path)
            except Exception as error:
                print("Không convert được video web:", error)
                web_video = output_video_path

        return {
            "summary": summary,
            "output_video": output_video_path,
            "output_web_video": web_video,
            "output_csv": output_csv_path,
        }
