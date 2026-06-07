import os
import cv2
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename

from src.video_processor import VideoProcessor
from src.detector import ObjectDetector
from src.constants import CLASS_NAMES, COLORS


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "web", "static", "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "web", "static", "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "web", "templates"),
    static_folder=os.path.join(BASE_DIR, "web", "static"),
)
app.secret_key = "smartcounterai"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process-video", methods=["POST"])
def process_video():
    video = request.files.get("video")

    if not video or video.filename == "":
        flash("Vui lòng chọn video.")
        return redirect(url_for("index"))

    line_mode = request.form.get("line_mode", "auto")
    line_pos = float(request.form.get("line_pos", 0.5))
    conf = float(request.form.get("conf", 0.15))
    keep_original = request.form.get("keep_original", "on") == "on"

    filename = secure_filename(video.filename)
    input_path = os.path.join(UPLOAD_DIR, filename)
    video.save(input_path)

    name = os.path.splitext(filename)[0]
    raw_video = os.path.join(OUTPUT_DIR, f"result_{name}_raw.mp4")
    web_video = os.path.join(OUTPUT_DIR, f"result_{name}_web.mp4")
    output_csv = os.path.join(OUTPUT_DIR, f"statistics_{name}.csv")

    processor = VideoProcessor(
        conf_threshold=conf,
        line_mode=line_mode,
        line_pos=line_pos,
        keep_original_size=keep_original,
        imgsz=960,
    )

    result = processor.process(
        source=input_path,
        output_video_path=raw_video,
        output_web_video_path=web_video,
        output_csv_path=output_csv,
        display=False,
        save_video=True,
    )

    return render_template(
        "result.html",
        summary=result["summary"],
        video_file=os.path.basename(result["output_web_video"]),
        csv_file=os.path.basename(result["output_csv"]),
    )


@app.route("/process-camera", methods=["POST"])
def process_camera():
    camera_index = int(request.form.get("camera_index", 0))
    line_mode = request.form.get("line_mode", "none")
    line_pos = float(request.form.get("line_pos", 0.5))
    conf = float(request.form.get("conf", 0.15))

    raw_video = os.path.join(OUTPUT_DIR, "camera_result_raw.mp4")
    web_video = os.path.join(OUTPUT_DIR, "camera_result_web.mp4")
    output_csv = os.path.join(OUTPUT_DIR, "camera_statistics.csv")

    processor = VideoProcessor(
        conf_threshold=conf,
        line_mode=line_mode,
        line_pos=line_pos,
        keep_original_size=True,
        imgsz=960,
    )

    result = processor.process(
        source=camera_index,
        output_video_path=raw_video,
        output_web_video_path=web_video,
        output_csv_path=output_csv,
        display=True,
        save_video=True,
        max_frames=600,
    )

    return render_template(
        "result.html",
        summary=result["summary"],
        video_file=os.path.basename(result["output_web_video"]),
        csv_file=os.path.basename(result["output_csv"]),
    )


@app.route("/process-image", methods=["POST"])
def process_image():
    image = request.files.get("image")

    if not image or image.filename == "":
        flash("Vui lòng chọn ảnh.")
        return redirect(url_for("index"))

    filename = secure_filename(image.filename)
    input_path = os.path.join(UPLOAD_DIR, filename)
    image.save(input_path)

    frame = cv2.imread(input_path)
    if frame is None:
        flash("Không đọc được ảnh.")
        return redirect(url_for("index"))

    # Ảnh tĩnh ưu tiên nhận diện người nhỏ/bị che nên dùng conf thấp và imgsz cao hơn.
    detector = ObjectDetector(conf_threshold=0.12, imgsz=1280)
    detections = detector.detect(frame)

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        cls = int(cls)

        class_name = CLASS_NAMES.get(cls, "Object")
        color = COLORS.get(class_name, (255, 255, 255))

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"{class_name} {conf:.2f}",
            (x1, max(25, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    name = os.path.splitext(filename)[0]
    output_image = os.path.join(OUTPUT_DIR, f"result_{name}.jpg")
    cv2.imwrite(output_image, frame)

    return render_template(
        "result_image.html",
        image_file=os.path.basename(output_image),
    )


@app.route("/outputs/<path:filename>")
def outputs(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
