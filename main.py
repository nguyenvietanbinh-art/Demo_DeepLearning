import argparse
from src.video_processor import VideoProcessor


def parse_args():
    parser = argparse.ArgumentParser(description="SmartCounterAI Final Project")
    parser.add_argument("--source", default="data/videos/test.mp4", help="Video path hoặc camera index")
    parser.add_argument("--output", default="outputs/videos/result_raw.mp4")
    parser.add_argument("--web-output", default="outputs/videos/result_web.mp4")
    parser.add_argument("--csv", default="outputs/csv/statistics.csv")
    parser.add_argument("--model", default="models/best.pt")
    parser.add_argument("--line-mode", default="auto", choices=["none", "auto", "horizontal", "vertical"])
    parser.add_argument("--line-pos", default=0.5, type=float)
    parser.add_argument("--conf", default=0.15, type=float)
    parser.add_argument("--resize", action="store_true", help="Bật resize output thay vì giữ nguyên video gốc")
    parser.add_argument("--width", default=None, type=int)
    parser.add_argument("--height", default=None, type=int)
    parser.add_argument("--display", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    source = int(args.source) if str(args.source).isdigit() else args.source

    processor = VideoProcessor(
        model_path=args.model,
        conf_threshold=args.conf,
        line_mode=args.line_mode,
        line_pos=args.line_pos,
        keep_original_size=not args.resize,
        output_width=args.width,
        output_height=args.height,
    )

    result = processor.process(
        source=source,
        output_video_path=args.output,
        output_web_video_path=args.web_output,
        output_csv_path=args.csv,
        display=args.display,
        save_video=True,
    )

    print("=== SmartCounterAI Result ===")
    print("Summary:", result["summary"])
    print("Video:", result["output_web_video"])
    print("CSV:", result["output_csv"])


if __name__ == "__main__":
    main()
